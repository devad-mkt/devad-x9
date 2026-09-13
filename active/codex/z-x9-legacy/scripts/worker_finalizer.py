#!/usr/bin/env python3
"""Seal one existing canonical WORKER result as a Controller ingress event.

The finalizer does not decide success, evaluate gates, update Controller state,
select work, contact providers, or retry.  It verifies byte identity and writes
one immutable event locator suitable for ``loopctl ingest-worker-result --file``
when written in a registered Worker worktree outbox.  Controller-runtime inbox
copies remain the input for ``loopctl run-once --file``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import sys
import unicodedata
import uuid
from typing import Any


_SHA256 = re.compile(r"[0-9a-f]{64}")
_TOKEN = re.compile(r"[A-Za-z0-9._:-]{1,128}")
RESULT_CAP_BYTES = 4 * 1024
EVENT_CAP_BYTES = 4 * 1024
RESULT_READY_CAP_BYTES = 4 * 1024
PRE_STOP_CAP_BYTES = 64 * 1024


class FinalizerError(RuntimeError):
    """Stable, secret-safe finalization failure code."""


def _load_v7_contract():
    """Load the sibling contract without changing process import paths."""
    path = Path(__file__).with_name("v7_contract.py")
    spec = importlib.util.spec_from_file_location(
        "x9_loop_v7_contract_for_worker_finalizer", path
    )
    if spec is None or spec.loader is None:
        raise FinalizerError("EVENT_CONTRACT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as exc:
        raise FinalizerError("EVENT_CONTRACT_UNAVAILABLE") from exc
    return module


def _load_style_autonomy_gate():
    """Reuse the installed Style classifier as the Loop Code stop gate."""
    path = (
        Path(__file__).resolve().parents[2]
        / "x9-loop-style"
        / "scripts"
        / "style_autonomy_gate.py"
    )
    spec = importlib.util.spec_from_file_location(
        "x9_style_autonomy_gate_for_worker_finalizer", path
    )
    if spec is None or spec.loader is None:
        raise FinalizerError("PRE_STOP_GATE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as exc:
        raise FinalizerError("PRE_STOP_GATE_UNAVAILABLE") from exc
    return module


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite number")


def _canonical_json_bytes(payload: Any) -> bytes:
    def reject(value: Any) -> None:
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("non-finite number")
            raise ValueError("floating number")
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("non-string key")
                reject(item)
        elif isinstance(value, list):
            for item in value:
                reject(item)

    reject(payload)
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


def _decode_canonical(raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            parse_float=lambda _value: (_ for _ in ()).throw(
                ValueError("floating number")
            ),
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise FinalizerError("RESULT_NOT_CANONICAL") from exc
    if not isinstance(payload, dict):
        raise FinalizerError("RESULT_NOT_CANONICAL")
    try:
        expected = _canonical_json_bytes(payload)
    except (TypeError, ValueError) as exc:
        raise FinalizerError("RESULT_NOT_CANONICAL") from exc
    if raw != expected:
        raise FinalizerError("RESULT_NOT_CANONICAL")
    return payload


def _is_reparse(path: Path) -> bool:
    try:
        stat = path.lstat()
    except OSError:
        return False
    attributes = getattr(stat, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & 0x400)


def _assert_plain_parents(path: Path, code: str) -> None:
    current = path.parent
    while True:
        if current.exists() and _is_reparse(current):
            raise FinalizerError(code)
        if current == current.parent:
            return
        current = current.parent


def _canonical_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise FinalizerError("RESULT_PATH_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value or normalized.startswith("/"):
        raise FinalizerError("RESULT_PATH_INVALID")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise FinalizerError("RESULT_PATH_INVALID")
    canonical = str(PurePosixPath(*parts))
    if canonical != normalized or re.match(r"^[A-Za-z]:", canonical):
        raise FinalizerError("RESULT_PATH_INVALID")
    return canonical


def _resolve_result(repo: Path, relative: str) -> Path:
    canonical = _canonical_repo_path(relative)
    try:
        root = repo.resolve(strict=True)
        if not root.is_dir() or _is_reparse(root):
            raise FinalizerError("REPOSITORY_PATH_INVALID")
        candidate = root.joinpath(*PurePosixPath(canonical).parts)
        _assert_plain_parents(candidate, "RESULT_PATH_INVALID")
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise FinalizerError("RESULT_PATH_INVALID")
        if _is_reparse(candidate) or not resolved.is_file():
            raise FinalizerError("RESULT_PATH_INVALID")
        return resolved
    except FinalizerError:
        raise
    except (OSError, RuntimeError) as exc:
        raise FinalizerError("RESULT_PATH_INVALID") from exc


def _validate_result_identity(result: dict[str, Any]) -> None:
    required = {
        "dispatch_id",
        "event_id",
        "packet_sha256",
        "role",
        "schema",
        "task_id",
        "work_order_id",
        "work_order_sha256",
        "worker_id",
    }
    if not required.issubset(result):
        raise FinalizerError("RESULT_IDENTITY_INVALID")
    if result["schema"] != "x9-loop-result-v2" or result["role"] != "WORKER":
        raise FinalizerError("RESULT_IDENTITY_INVALID")
    for field in ("dispatch_id", "event_id", "task_id", "work_order_id", "worker_id"):
        value = result[field]
        if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
            raise FinalizerError("RESULT_IDENTITY_INVALID")
    for field in ("packet_sha256", "work_order_sha256"):
        value = result[field]
        if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
            raise FinalizerError("RESULT_IDENTITY_INVALID")
    if result["packet_sha256"] != result["work_order_sha256"]:
        raise FinalizerError("RESULT_IDENTITY_INVALID")


def _validate_pre_stop_admission(
    result: dict[str, Any], pre_stop_case: str | Path | None
) -> None:
    outcome = result.get("outcome")
    if outcome in {"SUCCESS", "SUCCESS_CANDIDATE"}:
        if pre_stop_case is not None:
            raise FinalizerError("PRE_STOP_NOT_APPLICABLE")
        return
    if pre_stop_case is None:
        raise FinalizerError("PRE_STOP_ADMISSION_REQUIRED")
    path = Path(pre_stop_case)
    try:
        if (
            not path.is_file()
            or _is_reparse(path)
            or path.stat().st_size > PRE_STOP_CAP_BYTES
        ):
            raise FinalizerError("PRE_STOP_ADMISSION_INVALID")
        raw = path.read_bytes()
        case = json.loads(raw.decode("utf-8"))
    except FinalizerError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FinalizerError("PRE_STOP_ADMISSION_INVALID") from exc
    try:
        if _canonical_json_bytes(case) != raw:
            raise FinalizerError("PRE_STOP_ADMISSION_INVALID")
    except (TypeError, ValueError) as exc:
        raise FinalizerError("PRE_STOP_ADMISSION_INVALID") from exc
    gate = _load_style_autonomy_gate()
    decision = gate._classify_schema_case(case)
    if case.get("schema") == gate.WAIT_SCHEMA:
        if (
            decision.get("state") != "DEPENDENCY_WAIT"
            or case.get("expected_packet_sha256", "").casefold()
            != result["packet_sha256"].casefold()
            or outcome not in {
                "HARD_EXTERNAL", "STOP_EXHAUSTED", "CACHE_DRIFT_UNRESOLVED"
            }
        ):
            raise FinalizerError("PRE_STOP_CONTINUE_LOCAL")
        return
    if case.get("schema") != gate.SCHEMA:
        raise FinalizerError("PRE_STOP_ADMISSION_INVALID")
    if (
        decision.get("classification") not in {"THINKER_ALLOWED", "OWNER_REQUIRED"}
        or not decision.get("outbound_question_allowed")
        or (
            outcome == "VERIFIED_FAILURE"
            and case.get("distinct_failed_approaches")
            != result.get("failed_verified_approaches")
        )
    ):
        raise FinalizerError("PRE_STOP_CONTINUE_LOCAL")


def _result_ready_expiry() -> str:
    return (
        datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def build_result_ready_signal(
    result: dict[str, Any],
    *,
    result_path: str,
    result_sha256: str,
    project_profile_id: str,
    return_to_task_id: str,
    expires_at: str | None = None,
) -> dict[str, Any]:
    """Build a signal-only callback without copying the durable result."""
    _validate_result_identity(result)
    contract = _load_v7_contract()
    identity = {
        "dispatch_id": result["dispatch_id"],
        "event_id": result["event_id"],
        "packet_sha256": result["packet_sha256"],
        "result_path": result_path,
        "result_sha256": result_sha256,
        "task_id": result["task_id"],
        "work_order_id": result["work_order_id"],
        "work_order_sha256": result["work_order_sha256"],
        "worker_id": result["worker_id"],
    }
    callback_id = "rr-" + hashlib.sha256(
        contract.canonical_json_bytes(
            {
                "expected_result_identity": identity,
                "return_to_task_id": return_to_task_id,
            }
        )
    ).hexdigest()[:32]
    signal = contract.build_result_ready(
        callback_id=callback_id,
        expected_result_identity=identity,
        expires_at=expires_at or _result_ready_expiry(),
        project_profile_id=project_profile_id,
        return_to_task_id=return_to_task_id,
    )
    raw = contract.canonical_json_bytes(signal)
    if len(raw) > RESULT_READY_CAP_BYTES:
        raise FinalizerError("RESULT_READY_TOO_LARGE")
    try:
        validated = contract.validate_result_ready(
            raw,
            hashlib.sha256(raw).hexdigest(),
            project_profile_id,
            expected_identity=identity,
            expected_requester=return_to_task_id,
        )
    except contract.ContractError as exc:
        raise FinalizerError("RESULT_READY_CONTRACT_INVALID") from exc
    if validated != signal:
        raise FinalizerError("RESULT_READY_CONTRACT_INVALID")
    return signal


def write_result_ready_signal(
    result: dict[str, Any],
    *,
    result_path: str,
    result_sha256: str,
    output: str | Path,
    project_profile_id: str,
    return_to_task_id: str,
    expires_at: str | None = None,
) -> dict[str, Any]:
    signal = build_result_ready_signal(
        result,
        result_path=result_path,
        result_sha256=result_sha256,
        project_profile_id=project_profile_id,
        return_to_task_id=return_to_task_id,
        expires_at=expires_at,
    )
    output_path = Path(output)
    contract = _load_v7_contract()
    if output_path.exists():
        if _is_reparse(output_path) or not output_path.is_file():
            raise FinalizerError("RESULT_READY_CONFLICT")
        try:
            existing_raw = output_path.read_bytes()
            existing = contract.validate_result_ready(
                existing_raw,
                hashlib.sha256(existing_raw).hexdigest(),
                project_profile_id,
                expected_identity=signal["expected_result_identity"],
                expected_requester=return_to_task_id,
            )
        except (OSError, contract.ContractError) as exc:
            raise FinalizerError("RESULT_READY_CONFLICT") from exc
        return {
            "callback_id": existing["callback_id"],
            "event_id": existing["expected_result_identity"]["event_id"],
            "signal_sha256": hashlib.sha256(existing_raw).hexdigest(),
            "status": "ALREADY_RESULT_READY",
        }
    raw = _canonical_json_bytes(signal)
    wrote = _write_once(output_path, raw)
    return {
        "callback_id": signal["callback_id"],
        "event_id": signal["expected_result_identity"]["event_id"],
        "signal_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "RESULT_READY" if wrote else "ALREADY_RESULT_READY",
    }


def _write_once(path: Path, raw: bytes) -> bool:
    _assert_plain_parents(path, "EVENT_OUTPUT_PATH_INVALID")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _assert_plain_parents(path, "EVENT_OUTPUT_PATH_INVALID")
        if path.exists():
            if _is_reparse(path) or not path.is_file():
                raise FinalizerError("EVENT_OUTPUT_PATH_INVALID")
            if path.stat().st_size > EVENT_CAP_BYTES or path.stat().st_size != len(raw):
                raise FinalizerError("EVENT_RECEIPT_CONFLICT")
            if path.read_bytes() == raw:
                return False
            raise FinalizerError("EVENT_RECEIPT_CONFLICT")
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                if _is_reparse(path) or not path.is_file():
                    raise FinalizerError("EVENT_OUTPUT_PATH_INVALID")
                if path.stat().st_size > EVENT_CAP_BYTES or path.stat().st_size != len(raw):
                    raise FinalizerError("EVENT_RECEIPT_CONFLICT")
                if path.read_bytes() == raw:
                    return False
                raise FinalizerError("EVENT_RECEIPT_CONFLICT")
        finally:
            if temporary.exists():
                temporary.unlink()
        return True
    except FinalizerError:
        raise
    except OSError as exc:
        raise FinalizerError("EVENT_OUTPUT_WRITE_FAILED") from exc


def finalize_result(
    repo: str | Path,
    result_path: str,
    event_output: str | Path,
    *,
    project_profile_id: str,
    result_ready_output: str | Path | None = None,
    return_to_task_id: str | None = None,
    result_ready_expires_at: str | None = None,
    pre_stop_case: str | Path | None = None,
) -> dict[str, Any]:
    """Emit one immutable, hash-bound WORKER_RESULT event locator."""
    if (result_ready_output is None) != (return_to_task_id is None):
        raise FinalizerError("RESULT_READY_TARGET_INCOMPLETE")
    canonical_path = _canonical_repo_path(result_path)
    absolute = _resolve_result(Path(repo), canonical_path)
    if absolute.stat().st_size > RESULT_CAP_BYTES:
        raise FinalizerError("RESULT_TOO_LARGE")
    try:
        raw = absolute.read_bytes()
    except OSError as exc:
        raise FinalizerError("RESULT_READ_FAILED") from exc
    result = _decode_canonical(raw)
    _validate_result_identity(result)
    _validate_pre_stop_admission(result, pre_stop_case)
    contract = _load_v7_contract()
    expected = {
        field: result[field]
        for field in (
            "dispatch_id",
            "event_id",
            "packet_sha256",
            "task_id",
            "work_order_id",
            "work_order_sha256",
            "worker_id",
        )
    }
    try:
        validated_result, _disposition = contract.validate_worker_result(
            result, expected
        )
    except (contract.ContractError, TypeError, ValueError) as exc:
        raise FinalizerError("RESULT_CONTRACT_INVALID") from exc
    if validated_result != result:
        raise FinalizerError("RESULT_CONTRACT_INVALID")
    result_sha256 = hashlib.sha256(raw).hexdigest()
    event = {
        "event_id": result["event_id"],
        "event_type": "WORKER_RESULT",
        "payload_ref": {
            "path": canonical_path,
            "sha256": result_sha256,
        },
        "project_profile_id": project_profile_id,
        "schema": "x9-loop-inbox-event-v1",
        "source_actor_id": result["worker_id"],
        "source_role": "WORKER",
    }
    event_raw = _canonical_json_bytes(event)
    if len(event_raw) > EVENT_CAP_BYTES:
        raise FinalizerError("EVENT_CONTRACT_INVALID")
    event_sha256 = hashlib.sha256(event_raw).hexdigest()
    try:
        validated = contract.validate_inbox_event(
            event_raw, event_sha256, project_profile_id
        )
    except (contract.ContractError, TypeError, ValueError) as exc:
        raise FinalizerError("EVENT_CONTRACT_INVALID") from exc
    if validated != event:
        raise FinalizerError("EVENT_CONTRACT_INVALID")
    wrote = _write_once(Path(event_output), event_raw)
    response = {
        "event_sha256": event_sha256,
        "result_sha256": result_sha256,
        "status": "FINALIZED" if wrote else "ALREADY_FINALIZED",
    }
    if result_ready_output is not None and return_to_task_id is not None:
        response["result_ready"] = write_result_ready_signal(
            result,
            result_path=canonical_path,
            result_sha256=result_sha256,
            output=result_ready_output,
            project_profile_id=project_profile_id,
            return_to_task_id=return_to_task_id,
            expires_at=result_ready_expires_at,
        )
    return response


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--result-path", required=True)
    parser.add_argument("--event-output", required=True)
    parser.add_argument("--project-profile-id", required=True)
    parser.add_argument("--result-ready-output")
    parser.add_argument("--return-to-task-id")
    parser.add_argument("--result-ready-expires-at")
    parser.add_argument("--pre-stop-case")
    args = parser.parse_args(argv)
    try:
        result = finalize_result(
            args.repo,
            args.result_path,
            args.event_output,
            project_profile_id=args.project_profile_id,
            result_ready_output=args.result_ready_output,
            return_to_task_id=args.return_to_task_id,
            result_ready_expires_at=args.result_ready_expires_at,
            pre_stop_case=args.pre_stop_case,
        )
    except (FinalizerError, OSError, TypeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, FinalizerError) else "FINALIZER_FAILED"
        sys.stdout.buffer.write(
            _canonical_json_bytes({"error": code, "status": "ERROR"})
        )
        return 2
    sys.stdout.buffer.write(_canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
