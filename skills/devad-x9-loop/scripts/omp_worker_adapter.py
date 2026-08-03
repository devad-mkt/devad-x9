"""Provider-offline OMP/Pi external-sidecar adapter.

The adapter is deliberately transport-shaped rather than provider-shaped.  It
validates one immutable session envelope, composes an argument array, and
accepts only an injected fake/process runner.  S0 never starts a real OMP or
Pi process, never writes session state, and always reports ``provider_calls``
as zero.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import threading
from typing import Any, Mapping, MutableMapping, Protocol


REQUEST_SCHEMA = "x9-omp-worker-request-v1"
RECEIPT_SCHEMA = "x9-omp-worker-receipt-v1"
PROVIDER_CALLS = 0

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_TOKEN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_SESSION_ID = re.compile(r"^[^\x00-\x1f\x7f-][^\x00-\x1f\x7f]{0,511}$")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_SECRET_ASSIGNMENT = re.compile(
    r"(?P<label>\b(?:api[_-]?key|token|password|secret|authorization|cookie)\b)"
    r"(?P<separator>\s*[:=]\s*)(?P<value>[^\s,;]+)",
    re.IGNORECASE,
)
_BEARER = re.compile(r"(?P<label>\bBearer\s+)(?P<value>[^\s,;]+)", re.IGNORECASE)


class AdapterError(RuntimeError):
    """Typed, secret-safe deterministic adapter failure."""

    def __init__(self, code: str, message: str | None = None, **details: Any):
        self.code = code
        self.details = details
        super().__init__(message or code)


class ProcessRunner(Protocol):
    """Small fakeable process boundary used by provider-offline tests."""

    def run(
        self,
        argv: list[str],
        *,
        cwd: str,
        env_overrides: Mapping[str, str | None],
        input_text: str,
        timeout_seconds: int,
        cancel_event: object,
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class DriverProfile:
    name: str
    resume_flag: str
    session_flag: str
    continue_flag: str | None
    enabled: bool = True
    disabled_code: str | None = None


DRIVER_PROFILES: dict[str, DriverProfile] = {
    "omp": DriverProfile(
        name="omp",
        resume_flag="--resume",
        session_flag="--session",
        continue_flag="--continue",
    ),
    "pi": DriverProfile(
        name="pi",
        resume_flag="--session",
        session_flag="--session",
        continue_flag=None,
    ),
    "opencode": DriverProfile(
        name="opencode",
        resume_flag="--session",
        session_flag="--session",
        continue_flag=None,
        enabled=False,
        disabled_code="PROFILE_DISABLED",
    ),
    "command-code": DriverProfile(
        name="command-code",
        resume_flag="",
        session_flag="",
        continue_flag=None,
        enabled=False,
        disabled_code="RESUME_UNSUPPORTED",
    ),
}


def _reject_floats(value: Any, seen: set[int] | None = None) -> None:
    if isinstance(value, float):
        raise AdapterError("NON_CANONICAL_FLOAT")
    if isinstance(value, Mapping):
        seen = set() if seen is None else seen
        marker = id(value)
        if marker in seen:
            raise AdapterError("NON_CANONICAL_CYCLE")
        seen.add(marker)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise AdapterError("NON_CANONICAL_KEY")
                _reject_floats(item, seen)
        finally:
            seen.remove(marker)
    elif isinstance(value, (list, tuple)):
        seen = set() if seen is None else seen
        marker = id(value)
        if marker in seen:
            raise AdapterError("NON_CANONICAL_CYCLE")
        seen.add(marker)
        try:
            for item in value:
                _reject_floats(item, seen)
        finally:
            seen.remove(marker)


def canonical_json_bytes(value: Any) -> bytes:
    _reject_floats(value)
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            + b"\n"
        )
    except (TypeError, ValueError) as exc:
        raise AdapterError("NON_CANONICAL_JSON") from exc


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def redact_stream(value: str, *, max_chars: int = 4096) -> str:
    """Redact common credential assignments before any stream is retained."""

    if not isinstance(value, str):
        raise AdapterError("STREAM_INVALID")
    redacted = _SECRET_ASSIGNMENT.sub(
        lambda match: f"{match.group('label')}{match.group('separator')}[REDACTED]",
        value,
    )
    redacted = _BEARER.sub(lambda match: f"{match.group('label')}[REDACTED]", redacted)
    if len(redacted) > max_chars:
        return redacted[:max_chars] + "...[TRUNCATED]"
    return redacted


def _validate_hash(value: Any, code: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value.lower()) is None:
        raise AdapterError(code)
    return value.lower()


def _validate_git_sha(value: Any, code: str) -> str:
    if not isinstance(value, str) or _GIT_SHA.fullmatch(value.lower()) is None:
        raise AdapterError(code)
    return value.lower()


def _validate_token(value: Any, field: str) -> str:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
        raise AdapterError("IDENTITY_INVALID", field=field)
    return value


def _validate_session_id(value: Any, field: str = "session_id") -> str:
    if not isinstance(value, str) or _SESSION_ID.fullmatch(value) is None:
        raise AdapterError("SESSION_ID_INVALID", field=field)
    return value


def _is_reparse(path: Path) -> bool:
    try:
        stat = path.lstat()
    except OSError:
        return False
    return path.is_symlink() or bool(getattr(stat, "st_file_attributes", 0) & 0x400)


def _assert_plain_tree(path: Path, code: str) -> None:
    current = path
    while True:
        if current.exists() and _is_reparse(current):
            raise AdapterError(code)
        if current == current.parent:
            break
        current = current.parent


def _path_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise AdapterError("PATH_INVALID", field=field)
    if any(part in {"", ".", ".."} for part in re.split(r"[\\/]", value) if part):
        raise AdapterError("PATH_INVALID", field=field)
    if not Path(value).is_absolute():
        raise AdapterError("PATH_INVALID", field=field)
    return value


def _resolve_path(value: Any, field: str, *, code: str = "PATH_INVALID") -> Path:
    raw = _path_text(value, field)
    path = Path(os.path.abspath(os.path.normpath(raw)))
    try:
        _assert_plain_tree(path, code)
    except AdapterError:
        raise
    except OSError as exc:
        raise AdapterError(code) from exc
    return path


def _ensure_within(path: Path, root: Path, code: str) -> Path:
    try:
        candidate = path.resolve(strict=False)
        boundary = root.resolve(strict=False)
        if os.path.normcase(os.path.commonpath((str(candidate), str(boundary)))) != os.path.normcase(str(boundary)):
            raise AdapterError(code)
    except AdapterError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise AdapterError(code) from exc
    return candidate


def _require_file(path: Path, code: str) -> None:
    if not path.is_file() or _is_reparse(path):
        raise AdapterError(code)


def _require_directory(path: Path, code: str) -> None:
    if not path.is_dir() or _is_reparse(path):
        raise AdapterError(code)


def hash_path(path_value: str | Path) -> str:
    """Hash one file or a deterministic file-tree manifest without copying it."""

    path = _resolve_path(str(path_value), "path")
    if path.is_file():
        try:
            return sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise AdapterError("PATH_READ_FAILED") from exc
    if not path.is_dir():
        raise AdapterError("PATH_NOT_FOUND")
    rows: list[str] = []
    try:
        for child in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
            _assert_plain_tree(child, "SCOPE_VIOLATION")
            if not child.is_file():
                continue
            relative = child.relative_to(path).as_posix()
            rows.append(f"{sha256_bytes(child.read_bytes())}  {relative}")
    except (OSError, ValueError) as exc:
        raise AdapterError("PATH_READ_FAILED") from exc
    return sha256_bytes(("\n".join(rows) + "\n").encode("utf-8"))


def hash_session(path_value: str | Path) -> str:
    return hash_path(path_value)


def session_manifest_hash(path_value: str | Path) -> str:
    return hash_path(path_value)


def _policy_value(request: Mapping[str, Any], policy: Mapping[str, Any], name: str, default: Any = None) -> Any:
    return policy[name] if name in policy else request.get(name, default)


def _profile(name: Any, mode: str) -> DriverProfile:
    if not isinstance(name, str) or not name:
        raise AdapterError("PROFILE_INVALID")
    normalized = name.lower()
    profile = DRIVER_PROFILES.get(normalized)
    if profile is None:
        raise AdapterError("PROFILE_UNSUPPORTED")
    if not profile.enabled:
        raise AdapterError(profile.disabled_code or "PROFILE_DISABLED")
    if normalized == "command-code" and mode != "NEW":
        raise AdapterError("RESUME_UNSUPPORTED")
    return profile


def _normalize_identity(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AdapterError("WORKTREE_IDENTITY_MISSING", field=field)
    required = ("worktree_id", "worktree_path", "base_sha", "head_state")
    if any(item not in value for item in required):
        raise AdapterError("WORKTREE_IDENTITY_MISSING", field=field)
    path = _resolve_path(value["worktree_path"], f"{field}.worktree_path", code="WORKTREE_MISMATCH")
    _require_directory(path, "WORKTREE_MISMATCH")
    base_sha = _validate_git_sha(value["base_sha"], "WORKTREE_MISMATCH")
    head_sha = _validate_git_sha(value.get("head_sha", base_sha), "WORKTREE_MISMATCH")
    head_state = value["head_state"]
    if head_state != "CLEAN":
        raise AdapterError("WORKTREE_DIRTY")
    result = {
        "worktree_id": _validate_token(value["worktree_id"], f"{field}.worktree_id"),
        "worktree_path": path,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "head_state": head_state,
        "branch": value.get("branch"),
        "git_dir": None,
        "common_dir": None,
    }
    if result["branch"] is not None and not isinstance(result["branch"], str):
        raise AdapterError("WORKTREE_MISMATCH")
    for name in ("git_dir", "common_dir"):
        if value.get(name) is not None:
            git_path = _resolve_path(value[name], f"{field}.{name}", code="WORKTREE_MISMATCH")
            result[name] = git_path
    return result


def _check_same_path(left: Path | None, right: Path | None) -> bool:
    if left is None or right is None:
        return left is right
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _normalize_request(request: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(request, Mapping):
        raise AdapterError("REQUEST_INVALID")
    policy_value = request.get("session_policy", {})
    if not isinstance(policy_value, Mapping):
        raise AdapterError("SESSION_POLICY_INVALID")
    policy = dict(policy_value)
    mode = _policy_value(request, policy, "mode")
    if mode not in {"NEW", "RESUME_EXACT", "CONTINUE_EXACT", "FORK_FROM_EXACT"}:
        raise AdapterError("SESSION_MODE_INVALID")
    profile_name = request.get("profile", request.get("omp_profile_kind", "omp"))
    profile = _profile(profile_name, mode)

    if request.get("schema", REQUEST_SCHEMA) != REQUEST_SCHEMA:
        raise AdapterError("REQUEST_SCHEMA_INVALID")
    provider_budget = request.get("provider_call_budget", 0)
    if isinstance(provider_budget, bool) or not isinstance(provider_budget, int) or provider_budget != 0:
        raise AdapterError("PROVIDER_CALL_BUDGET_NONZERO")
    if request.get("provider_calls", 0) != 0:
        raise AdapterError("PROVIDER_CALLS_FORBIDDEN")

    session_dir = _resolve_path(request.get("session_dir"), "session_dir", code="SCOPE_VIOLATION")
    _require_directory(session_dir, "SESSION_NOT_FOUND")
    executable = _resolve_path(request.get("executable_path"), "executable_path", code="EXECUTABLE_DRIFT")
    _require_file(executable, "EXECUTABLE_NOT_FOUND")
    executable_sha256 = _validate_hash(request.get("executable_sha256"), "EXECUTABLE_HASH_INVALID")
    if hash_path(executable) != executable_sha256:
        raise AdapterError("EXECUTABLE_DRIFT")
    omp_profile = request.get("omp_profile", request.get("profile_name"))
    if not isinstance(omp_profile, str) or not omp_profile or _CONTROL_RE.search(omp_profile):
        raise AdapterError("PROFILE_NAME_INVALID")
    version = request.get("omp_version", request.get("version"))
    if not isinstance(version, str) or not version or _CONTROL_RE.search(version):
        raise AdapterError("VERSION_INVALID")

    bound_worktree = _normalize_identity(request.get("worktree"), "worktree")
    observed_value = request.get("current_worktree", request.get("observed_worktree"))
    observed_worktree = _normalize_identity(observed_value, "current_worktree")
    for name in ("worktree_id", "base_sha", "head_sha", "branch"):
        if bound_worktree[name] != observed_worktree[name]:
            raise AdapterError("WORKTREE_MISMATCH", field=name)
    for name in ("worktree_path", "git_dir", "common_dir"):
        if not _check_same_path(bound_worktree[name], observed_worktree[name]):
            raise AdapterError("WORKTREE_MISMATCH", field=name)
    if observed_worktree["head_sha"] != observed_worktree["base_sha"]:
        raise AdapterError("WORKTREE_MISMATCH", field="head_sha")

    settings_path_value = request.get("settings_path")
    settings_sha256 = request.get("settings_sha256")
    settings_path: Path | None = None
    if settings_path_value is not None or settings_sha256 is not None:
        if settings_path_value is None or settings_sha256 is None:
            raise AdapterError("SETTINGS_DRIFT")
        settings_path = _resolve_path(settings_path_value, "settings_path", code="SCOPE_VIOLATION")
        _ensure_within(settings_path, session_dir, "SCOPE_VIOLATION")
        _require_file(settings_path, "SETTINGS_DRIFT")
        settings_sha256 = _validate_hash(settings_sha256, "SETTINGS_HASH_INVALID")
        if hash_path(settings_path) != settings_sha256:
            raise AdapterError("SETTINGS_DRIFT")

    discovery_home_value = request.get("discovery_home")
    omp_agent_dir_value = request.get("omp_agent_dir")
    if (discovery_home_value is None) != (omp_agent_dir_value is None):
        raise AdapterError("DISCOVERY_ISOLATION_INVALID")
    discovery_home: Path | None = None
    omp_agent_dir: Path | None = None
    if discovery_home_value is not None:
        if profile.name != "omp":
            raise AdapterError("DISCOVERY_ISOLATION_INVALID")
        discovery_home = _resolve_path(
            discovery_home_value,
            "discovery_home",
            code="SCOPE_VIOLATION",
        )
        _ensure_within(discovery_home, session_dir, "SCOPE_VIOLATION")
        _require_directory(discovery_home, "DISCOVERY_HOME_NOT_FOUND")
        omp_agent_dir = _resolve_path(
            omp_agent_dir_value,
            "omp_agent_dir",
            code="DISCOVERY_ISOLATION_INVALID",
        )
        _require_directory(omp_agent_dir, "OMP_AGENT_DIR_NOT_FOUND")

    prompt = request.get("prompt", "")
    if not isinstance(prompt, str) or _CONTROL_RE.search(prompt.replace("\n", "").replace("\r", "")):
        raise AdapterError("PROMPT_INVALID")
    prompt_sha256 = request.get("prompt_sha256")
    if prompt_sha256 is not None:
        prompt_sha256 = _validate_hash(prompt_sha256, "PROMPT_HASH_INVALID")
        if sha256_bytes(prompt.encode("utf-8")) != prompt_sha256:
            raise AdapterError("PROMPT_DRIFT")
    else:
        prompt_sha256 = sha256_bytes(prompt.encode("utf-8"))
    context_capsule_sha256 = request.get("context_capsule_sha256")
    if context_capsule_sha256 is not None:
        context_capsule_sha256 = _validate_hash(context_capsule_sha256, "CONTEXT_HASH_INVALID")

    session_path_value = _policy_value(request, policy, "session_path")
    session_id_value = _policy_value(request, policy, "session_id")
    session_sha256 = _policy_value(request, policy, "session_sha256")
    session_path: Path | None = None
    session_id: str | None = None
    if session_id_value is not None:
        session_id = _validate_session_id(session_id_value)
    if session_path_value is not None:
        session_path = _resolve_path(session_path_value, "session_path", code="SCOPE_VIOLATION")
        _ensure_within(session_path, session_dir, "SCOPE_VIOLATION")
        _require_file(session_path, "SESSION_NOT_FOUND")
        session_sha256 = _validate_hash(session_sha256, "SESSION_HASH_INVALID")
        if hash_session(session_path) != session_sha256:
            raise AdapterError("SESSION_INCOMPATIBLE")
    elif session_sha256 is not None:
        raise AdapterError("SESSION_POLICY_INVALID")
    if mode != "NEW":
        if profile.name == "omp" and session_path is None:
            raise AdapterError("SESSION_INCOMPATIBLE")
        if profile.name == "pi" and session_id is None:
            raise AdapterError("SESSION_ID_INVALID")
        if session_path is None and session_id is None:
            raise AdapterError("SESSION_INCOMPATIBLE")
    elif any(policy.get(name) is not None for name in ("session_id", "session_path", "session_sha256")):
        raise AdapterError("SESSION_POLICY_INVALID")

    parent_id_value = _policy_value(request, policy, "parent_session_id")
    parent_path_value = _policy_value(request, policy, "parent_session_path")
    parent_sha256 = _policy_value(request, policy, "parent_session_sha256")
    parent_path: Path | None = None
    parent_id: str | None = None
    if parent_id_value is not None:
        parent_id = _validate_session_id(parent_id_value, "parent_session_id")
    if parent_path_value is not None:
        parent_path = _resolve_path(parent_path_value, "parent_session_path", code="SCOPE_VIOLATION")
        _ensure_within(parent_path, session_dir, "SCOPE_VIOLATION")
        _require_file(parent_path, "SESSION_NOT_FOUND")
        parent_sha256 = _validate_hash(parent_sha256, "PARENT_SESSION_HASH_INVALID")
        if hash_session(parent_path) != parent_sha256:
            raise AdapterError("SESSION_INCOMPATIBLE")
    elif parent_sha256 is not None:
        raise AdapterError("SESSION_POLICY_INVALID")
    if mode == "FORK_FROM_EXACT":
        if profile.name == "pi":
            if parent_id is None:
                raise AdapterError("SESSION_ID_INVALID", field="parent_session_id")
            if parent_path is None or parent_sha256 is None:
                raise AdapterError("SESSION_INCOMPATIBLE")
        if parent_path is None:
            parent_path = session_path
            parent_sha256 = session_sha256
        if parent_path is None or parent_sha256 is None:
            raise AdapterError("SESSION_INCOMPATIBLE")
        if parent_id is None:
            parent_id = session_id
    elif any(item is not None for item in (parent_id, parent_path, parent_sha256)):
        raise AdapterError("SESSION_POLICY_INVALID")

    model_policy = _policy_value(request, policy, "model_policy", "KEEP")
    if model_policy not in {"KEEP", "CHANGE_EXACT"}:
        raise AdapterError("MODEL_POLICY_INVALID")
    recorded_model = _policy_value(request, policy, "recorded_model", _policy_value(request, policy, "model"))
    requested_model = _policy_value(request, policy, "requested_model")
    requested_thinking = _policy_value(request, policy, "requested_thinking")
    if recorded_model is not None and (not isinstance(recorded_model, str) or not recorded_model or _CONTROL_RE.search(recorded_model)):
        raise AdapterError("MODEL_POLICY_INVALID")
    if requested_model is not None and (not isinstance(requested_model, str) or not requested_model or _CONTROL_RE.search(requested_model)):
        raise AdapterError("MODEL_POLICY_INVALID")
    if requested_thinking is not None and (not isinstance(requested_thinking, str) or not requested_thinking or _CONTROL_RE.search(requested_thinking)):
        raise AdapterError("THINKING_INVALID")
    if model_policy == "KEEP":
        if requested_model is not None and requested_model != recorded_model:
            raise AdapterError("MODEL_POLICY_INVALID")
        if requested_thinking is not None:
            raise AdapterError("MODEL_POLICY_INVALID")
    elif requested_model is None:
        raise AdapterError("MODEL_POLICY_INVALID")
    if mode == "FORK_FROM_EXACT" and model_policy == "KEEP" and requested_model is not None:
        raise AdapterError("MODEL_POLICY_INVALID")

    timeout_seconds = request.get("timeout_seconds", 60)
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise AdapterError("TIMEOUT_INVALID")
    run_id = request.get("run_id")
    if run_id is not None:
        _validate_token(run_id, "run_id")
    denied_effects = request.get("denied_effects", [])
    allowed_tools = request.get("allowed_tools", [])
    for name, value in (("denied_effects", denied_effects), ("allowed_tools", allowed_tools)):
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            raise AdapterError("EFFECT_POLICY_INVALID", field=name)
        for index, item in enumerate(value):
            try:
                _validate_token(item, f"{name}[{index}]")
            except AdapterError as exc:
                raise AdapterError(
                    "EFFECT_POLICY_INVALID",
                    field=f"{name}[{index}]",
                ) from exc
    return {
        "profile": profile.name,
        "driver": profile,
        "mode": mode,
        "session_dir": session_dir,
        "session_id": session_id,
        "session_path": session_path,
        "session_sha256": session_sha256,
        "parent_session_id": parent_id,
        "parent_session_path": parent_path,
        "parent_session_sha256": parent_sha256,
        "model_policy": model_policy,
        "recorded_model": recorded_model,
        "requested_model": requested_model,
        "requested_thinking": requested_thinking,
        "omp_profile": omp_profile,
        "executable": executable,
        "executable_sha256": executable_sha256,
        "omp_version": version,
        "work_order_id": _validate_token(request.get("work_order_id"), "work_order_id"),
        "dispatch_id": _validate_token(request.get("dispatch_id"), "dispatch_id"),
        "target_actor_id": _validate_token(request.get("target_actor_id"), "target_actor_id"),
        "project_profile_id": _validate_token(request.get("project_profile_id"), "project_profile_id"),
        "worktree": bound_worktree,
        "settings_path": settings_path,
        "settings_sha256": settings_sha256,
        "discovery_home": discovery_home,
        "omp_agent_dir": omp_agent_dir,
        "prompt": prompt,
        "prompt_sha256": prompt_sha256,
        "context_capsule_sha256": context_capsule_sha256,
        "allowed_tools": tuple(allowed_tools),
        "denied_effects": tuple(denied_effects),
        "provider_call_budget": provider_budget,
        "timeout_seconds": timeout_seconds,
        "run_id": run_id,
    }


def normalize_request(request: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a safe, non-secret normalized envelope."""

    normalized = _normalize_request(request)
    safe = copy.deepcopy(normalized)
    safe.pop("prompt", None)
    safe.pop("driver", None)
    for key, value in list(safe.items()):
        if isinstance(value, Path):
            safe[key] = str(value)
        elif isinstance(value, dict):
            safe[key] = {
                item_key: str(item_value) if isinstance(item_value, Path) else item_value
                for item_key, item_value in value.items()
            }
    safe["allowed_tools"] = list(safe["allowed_tools"])
    safe["denied_effects"] = list(safe["denied_effects"])
    return safe


def _build_command(normalized: Mapping[str, Any]) -> list[str]:
    profile: DriverProfile = normalized["driver"]
    mode = normalized["mode"]
    if profile.name == "omp":
        command = [
            str(normalized["executable"]),
            "--profile",
            normalized["omp_profile"],
            "--session-dir",
            str(normalized["session_dir"]),
            "--cwd",
            str(normalized["worktree"]["worktree_path"]),
        ]
    else:
        command = [str(normalized["executable"]), "--session-dir", str(normalized["session_dir"])]
    if normalized["allowed_tools"]:
        command.extend(["--tools", ",".join(normalized["allowed_tools"])])
    else:
        command.append("--no-tools")
    if mode == "FORK_FROM_EXACT":
        if profile.name == "omp":
            command.extend([profile.resume_flag, str(normalized["parent_session_path"])])
        else:
            command.extend([profile.resume_flag, normalized["parent_session_id"]])
    elif mode == "RESUME_EXACT":
        if profile.name == "omp":
            command.extend([profile.resume_flag, str(normalized["session_path"])])
        else:
            command.extend([profile.resume_flag, normalized["session_id"]])
    elif mode == "CONTINUE_EXACT":
        if profile.continue_flag is None:
            command.extend([profile.session_flag, normalized["session_id"]])
        else:
            command.append(profile.continue_flag)
    if normalized["model_policy"] == "CHANGE_EXACT":
        command.extend(["--model", normalized["requested_model"]])
        if normalized["requested_thinking"] is not None:
            command.extend(["--thinking", normalized["requested_thinking"]])
    return command


def build_command(request: Mapping[str, Any]) -> list[str]:
    """Compose one argv array; never build a shell command string."""

    return _build_command(_normalize_request(request))


def compose_command(request: Mapping[str, Any]) -> list[str]:
    return build_command(request)


def build_launch_args(request: Mapping[str, Any]) -> list[str]:
    return build_command(request)


def _bound_identity(normalized: Mapping[str, Any], command: list[str]) -> dict[str, Any]:
    worktree = normalized["worktree"]
    return {
        "schema": RECEIPT_SCHEMA,
        "profile": normalized["profile"],
        "mode": normalized["mode"],
        "session_dir": str(normalized["session_dir"]),
        "session_id": normalized["session_id"],
        "session_path": str(normalized["session_path"]) if normalized["session_path"] else None,
        "session_sha256": normalized["session_sha256"],
        "parent_session_id": normalized["parent_session_id"],
        "parent_session_path": str(normalized["parent_session_path"]) if normalized["parent_session_path"] else None,
        "parent_session_sha256": normalized["parent_session_sha256"],
        "model_policy": normalized["model_policy"],
        "recorded_model": normalized["recorded_model"],
        "requested_model": normalized["requested_model"],
        "requested_thinking": normalized["requested_thinking"],
        "command_sha256": sha256_bytes(canonical_json_bytes(command)),
        "cwd": str(worktree["worktree_path"]),
        "worktree_id": worktree["worktree_id"],
        "worktree_path": str(worktree["worktree_path"]),
        "base_sha": worktree["base_sha"],
        "head_sha": worktree["head_sha"],
        "branch": worktree["branch"],
        "git_dir": str(worktree["git_dir"]) if worktree["git_dir"] else None,
        "common_dir": str(worktree["common_dir"]) if worktree["common_dir"] else None,
        "settings_path": str(normalized["settings_path"]) if normalized["settings_path"] else None,
        "settings_sha256": normalized["settings_sha256"],
        "discovery_home": (
            str(normalized["discovery_home"]) if normalized["discovery_home"] else None
        ),
        "omp_agent_dir": (
            str(normalized["omp_agent_dir"]) if normalized["omp_agent_dir"] else None
        ),
        "prompt_sha256": normalized["prompt_sha256"],
        "context_capsule_sha256": normalized["context_capsule_sha256"],
        "work_order_id": normalized["work_order_id"],
        "dispatch_id": normalized["dispatch_id"],
        "target_actor_id": normalized["target_actor_id"],
        "project_profile_id": normalized["project_profile_id"],
        "omp_profile": normalized["omp_profile"],
        "omp_version": normalized["omp_version"],
        "executable_path": str(normalized["executable"]),
        "executable_sha256": normalized["executable_sha256"],
        "allowed_tools": list(normalized["allowed_tools"]),
        "denied_effects": list(normalized["denied_effects"]),
        "provider_call_budget": normalized["provider_call_budget"],
        "timeout_seconds": normalized["timeout_seconds"],
        "run_id": normalized["run_id"],
    }


def _idempotency_key(normalized: Mapping[str, Any], command: list[str]) -> str:
    identity = _bound_identity(normalized, command)
    return sha256_bytes(canonical_json_bytes(identity))


def idempotency_key(request: Mapping[str, Any]) -> str:
    normalized = _normalize_request(request)
    return _idempotency_key(normalized, _build_command(normalized))


def _cancelled(cancel_event: object | None) -> bool:
    if cancel_event is None:
        return False
    if isinstance(cancel_event, bool):
        return cancel_event
    checker = getattr(cancel_event, "is_set", None)
    return bool(checker()) if callable(checker) else False


def _process_result(value: Any) -> tuple[int, str, str, bool, bool]:
    if not isinstance(value, Mapping):
        raise AdapterError("PROCESS_RESULT_INVALID")
    returncode = value.get("returncode", 0)
    if isinstance(returncode, bool) or not isinstance(returncode, int):
        raise AdapterError("PROCESS_RESULT_INVALID")
    stdout = value.get("stdout", "")
    stderr = value.get("stderr", "")
    if not isinstance(stdout, str) or not isinstance(stderr, str):
        raise AdapterError("PROCESS_RESULT_INVALID")
    provider_calls = value.get("provider_calls", 0)
    if provider_calls != PROVIDER_CALLS:
        raise AdapterError("PROVIDER_CALLS_FORBIDDEN")
    return (
        returncode,
        redact_stream(stdout),
        redact_stream(stderr),
        bool(value.get("timed_out", False)),
        bool(value.get("cancelled", False)),
    )


def _run_process(
    runner: ProcessRunner,
    command: list[str],
    normalized: Mapping[str, Any],
    cancel_event: object | None,
) -> tuple[int, str, str]:
    if _cancelled(cancel_event):
        raise AdapterError("CANCELLED")
    try:
        env_overrides: dict[str, str | None] = {}
        if normalized["profile"] == "omp" and normalized["discovery_home"] is not None:
            env_overrides = {
                "USERPROFILE": str(normalized["discovery_home"]),
                "HOME": str(normalized["discovery_home"]),
                "PI_CODING_AGENT_DIR": str(normalized["omp_agent_dir"]),
                "OMP_PROFILE": None,
                "PI_PROFILE": None,
            }
        result = runner.run(
            command,
            cwd=str(normalized["worktree"]["worktree_path"]),
            env_overrides=env_overrides,
            input_text=normalized["prompt"],
            timeout_seconds=normalized["timeout_seconds"],
            cancel_event=cancel_event,
        )
    except TimeoutError as exc:
        raise AdapterError("TIMEOUT") from exc
    except AdapterError:
        raise
    except (KeyboardInterrupt, InterruptedError) as exc:
        raise AdapterError("CANCELLED") from exc
    except Exception as exc:  # pragma: no cover - defensive fake boundary
        if _cancelled(cancel_event):
            raise AdapterError("CANCELLED") from exc
        raise AdapterError("PROCESS_FAILED", error=type(exc).__name__) from exc
    returncode, stdout, stderr, timed_out, cancelled = _process_result(result)
    if timed_out:
        raise AdapterError("TIMEOUT")
    if cancelled or _cancelled(cancel_event):
        raise AdapterError("CANCELLED")
    if returncode != 0:
        raise AdapterError("PROCESS_FAILED", returncode=returncode, stderr=stderr)
    return returncode, stdout, stderr


def _session_before(normalized: Mapping[str, Any]) -> tuple[str | None, str | None]:
    session_path = normalized["session_path"]
    parent_path = normalized["parent_session_path"]
    session_hash = hash_session(session_path) if session_path is not None else None
    parent_hash = hash_session(parent_path) if parent_path is not None else None
    if session_hash is not None and session_hash != normalized["session_sha256"]:
        raise AdapterError("SESSION_INCOMPATIBLE")
    if parent_hash is not None and parent_hash != normalized["parent_session_sha256"]:
        raise AdapterError("SESSION_INCOMPATIBLE")
    return session_hash, parent_hash


def _receipt(normalized: Mapping[str, Any], command: list[str], key: str, stdout: str, stderr: str) -> dict[str, Any]:
    return {
        **_bound_identity(normalized, command),
        "status": "PASS",
        "provider_calls": PROVIDER_CALLS,
        "idempotency_key": key,
        "stdout": stdout,
        "stderr": stderr,
    }


def _validate_replay_receipt(
    existing: Mapping[str, Any],
    normalized: Mapping[str, Any],
    command: list[str],
    key: str,
) -> None:
    if existing.get("idempotency_key") != key or existing.get("schema") != RECEIPT_SCHEMA:
        raise AdapterError("IDEMPOTENCY_CONFLICT")
    for field, expected in _bound_identity(normalized, command).items():
        if existing.get(field) != expected:
            raise AdapterError("IDEMPOTENCY_CONFLICT", field=field)


def execute(
    request: Mapping[str, Any],
    runner: ProcessRunner | None = None,
    *,
    receipt_store: MutableMapping[str, Mapping[str, Any]] | None = None,
    cancel_event: object | None = None,
) -> dict[str, Any]:
    """Run one fake/process boundary without provider or session side effects."""

    normalized = _normalize_request(request)
    command = _build_command(normalized)
    key = _idempotency_key(normalized, command)
    if receipt_store is not None and key in receipt_store:
        existing = dict(receipt_store[key])
        _validate_replay_receipt(existing, normalized, command, key)
        existing["status"] = "IDEMPOTENT_REPLAY"
        existing["provider_calls"] = PROVIDER_CALLS
        return existing
    if runner is None:
        raise AdapterError("PROVIDER_CALLS_FORBIDDEN")
    before_session, before_parent = _session_before(normalized)
    _, stdout, stderr = _run_process(runner, command, normalized, cancel_event)
    after_session, after_parent = _session_before(normalized)
    if before_session != after_session or before_parent != after_parent:
        raise AdapterError("SESSION_MUTATED")
    receipt = _receipt(normalized, command, key, stdout, stderr)
    if receipt_store is not None:
        receipt_store[key] = copy.deepcopy(receipt)
    return receipt


def run_offline(
    request: Mapping[str, Any],
    runner: ProcessRunner | None = None,
    *,
    receipt_store: MutableMapping[str, Mapping[str, Any]] | None = None,
    cancel_event: object | None = None,
) -> dict[str, Any]:
    return execute(request, runner, receipt_store=receipt_store, cancel_event=cancel_event)


def verify_update_compatibility(
    session_path: str,
    expected_session_sha256: str,
    *,
    compatible: bool,
) -> dict[str, Any]:
    """Check an update in an isolated/fake profile without rewriting old bytes."""

    path = _resolve_path(session_path, "session_path", code="SESSION_VERSION_INCOMPATIBLE")
    _require_file(path, "SESSION_VERSION_INCOMPATIBLE")
    expected = _validate_hash(expected_session_sha256, "SESSION_VERSION_INCOMPATIBLE")
    actual = hash_session(path)
    if actual != expected or not compatible:
        raise AdapterError("SESSION_VERSION_INCOMPATIBLE")
    return {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "provider_calls": PROVIDER_CALLS,
        "session_sha256": actual,
    }


def validate_session_request(request: Mapping[str, Any]) -> dict[str, Any]:
    return normalize_request(request)


__all__ = [
    "AdapterError",
    "DRIVER_PROFILES",
    "ProcessRunner",
    "REQUEST_SCHEMA",
    "RECEIPT_SCHEMA",
    "build_command",
    "build_launch_args",
    "canonical_json_bytes",
    "compose_command",
    "execute",
    "hash_path",
    "hash_session",
    "idempotency_key",
    "normalize_request",
    "redact_stream",
    "run_offline",
    "session_manifest_hash",
    "sha256_bytes",
    "validate_session_request",
    "verify_update_compatibility",
]
