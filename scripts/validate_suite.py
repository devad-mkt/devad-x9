from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


# Package validation is read-only, including runtime-parity imports.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "devad-x9",
    "x9-loop-style",
    "x9-loop-code",
    "devad-x9-loop",
    "devad-x9-manager",
    "codex-x9-backup",
    "codex-token-budget",
    "devad-memory",
    "x9-project-docs",
    "dokploy",
    "devad-docs",
    "tldr",
    "smooth-coding",
    "sdlc",
    "xplan",
    "devad-adoptions",
)
CAP_NAMES = {"STATUS.md", "HANDOFFS.md"}
HOST_RUNTIME_ROOTS = (".agents",)
LOCAL_TEMP_ROOTS = (".temp",)
LOOP_FILES = {
    "ROLE_REGISTRY.json",
    "PASS_CAPSULE.json",
    "WORKTREE_INDEX.json",
    "TASK_GRAPH.json",
    "RESOURCE_CLAIMS.json",
    "EVENT_CURSOR.json",
    "DISPATCH_LEDGER.jsonl",
    "DECISION_GATES.json",
}
LOOP_LITE_FILES = {
    ".gitignore",
    "APPROVED_JOBS.json",
    "MIGRATION_CLASSIFICATION.json",
    "README.md",
    "SNAPSHOT.json",
    "contracts",
    "snapshots",
}
OWNER_PACKET_FILES = {".gitignore", "README.md"}
LOOP_LITE_CONTRACT_CAPS = {
    "ACTION.json": 4 * 1024,
    "CALL_RECEIPT.json": 16 * 1024,
    "FEATURE_PACKET.json": 32 * 1024,
    "OWNER_PACKET.json": 4 * 1024,
    "PROGRAM_PACKET.json": 16 * 1024,
    "RESULT.json": 4 * 1024,
    "STOP_CONTRACT.json": 4 * 1024,
    "TASK.json": 4 * 1024,
    "WORKER_CHECKPOINT.json": 16 * 1024,
    "WORK_ORDER.json": 16 * 1024,
}
LOOP_LITE_CONTRACTS = set(LOOP_LITE_CONTRACT_CAPS)
V7_CANONICAL_JSON = {
    "APPROVED_JOBS.json": "x9-loop-approved-jobs-v1",
    "MIGRATION_CLASSIFICATION.json": "x9-loop-migration-classification-v1",
    "ACTION.json": "x9-loop-action-v2",
    "CALL_RECEIPT.json": "x9-loop-call-receipt-v1",
    "FEATURE_PACKET.json": "x9-loop-feature-v1",
    "PROGRAM_PACKET.json": "x9-loop-program-v1",
    "RESULT.json": "x9-loop-result-v2",
    "STOP_CONTRACT.json": "x9-loop-stop-contract-v1",
    "TASK.json": "x9-loop-lite-task-v1",
    "WORKER_CHECKPOINT.json": "x9-loop-worker-checkpoint-v1",
    "WORK_ORDER.json": "x9-loop-work-order-v1",
}
LOOP_LITE_TABLES = {
    "actors", "worktrees", "tasks", "claims", "resources", "dispatches",
    "deliveries", "events", "gates", "outbox", "metrics", "programs",
    "work_orders", "worktree_classifications", "call_reservations",
    "inbox",
}
LOOP_LITE_IGNORES = {"loop.db", "loop.db-shm", "loop.db-wal", "runtime/", "*.corrupt-*", "*.failed-*", "*.rebuild-*"}
LOOP_LITE_CONTROLLER = "skills/devad-x9-loop/scripts/loopctl.py"
LOOP_LITE_SNAPSHOT_SCHEMA = "x9-loop-lite-snapshot-v3"
ALLOWED_STATUS = {"RETAINED", "MOVED", "ADAPTED", "NEW", "RETIRED"}
PROJECT_STATE_ROOTS = (".devad/manager", ".devad/workers")


def _is_project_state_path(relative: str) -> bool:
    return any(
        relative == root or relative.startswith(root + "/")
        for root in PROJECT_STATE_ROOTS
    )


def _is_host_runtime_path(relative: str) -> bool:
    return any(
        relative == root or relative.startswith(root + "/")
        for root in HOST_RUNTIME_ROOTS
    )

def _is_local_temp_path(relative: str) -> bool:
    return any(
        relative == root or relative.startswith(root + "/")
        for root in LOCAL_TEMP_ROOTS
    )


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _is_link_or_reparse(path: Path) -> bool:
    item = os.lstat(path)
    return stat.S_ISLNK(item.st_mode) or bool(
        getattr(item, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _assert_manifest_path_safe(root: Path, path: Path) -> Path:
    root_absolute = Path(os.path.abspath(root))
    path_absolute = Path(os.path.abspath(path))
    try:
        relative = path_absolute.relative_to(root_absolute)
    except ValueError as exc:
        raise ValueError(f"manifest path escapes package root: {path}") from exc
    current = root_absolute
    if _is_link_or_reparse(current):
        raise ValueError(f"manifest package root is a link or reparse point: {root}")
    for part in relative.parts:
        current = current / part
        if _is_link_or_reparse(current):
            raise ValueError(f"manifest path is a link or reparse point: {path}")
    resolved_root = root_absolute.resolve(strict=True)
    resolved_path = path_absolute.resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"resolved manifest path escapes package root: {path}") from exc
    return resolved_path


def _manifest_path(root: Path, relative: str) -> Path:
    if not relative or "\\" in relative:
        raise ValueError(f"non-canonical manifest path: {relative}")
    posix = PurePosixPath(relative)
    windows = PureWindowsPath(relative)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or posix.as_posix() != relative
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise ValueError(f"unsafe manifest path: {relative}")
    return _assert_manifest_path_safe(root, root.joinpath(*posix.parts))


def _eligible_manifest_paths(root: Path) -> set[str]:
    eligible: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if (
            relative == "SOURCE_MANIFEST.sha256"
            or relative == ".git"
            or relative.startswith(".git/")
            or "__pycache__" in path.parts
            or path.suffix == ".pyc"
            or _is_project_state_path(relative)
            or _is_host_runtime_path(relative)
            or _is_local_temp_path(relative)
        ):
            continue
        safe_path = _assert_manifest_path_safe(root, path)
        if not safe_path.is_file():
            continue
        eligible.add(relative)
    return eligible


def validate_manifest(errors: list[str]) -> None:
    manifest = ROOT / "SOURCE_MANIFEST.sha256"
    if not manifest.is_file():
        errors.append("missing SOURCE_MANIFEST.sha256")
        return
    try:
        manifest = _assert_manifest_path_safe(ROOT, manifest)
    except (OSError, ValueError) as exc:
        errors.append(f"unsafe SOURCE_MANIFEST.sha256: {exc}")
        return
    listed: set[str] = set()
    for line in manifest.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append("invalid source manifest line")
            continue
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            errors.append(f"invalid source manifest digest: {relative}")
            continue
        if relative in listed:
            errors.append(f"duplicate source manifest entry: {relative}")
            continue
        listed.add(relative)
        if relative == ".git" or relative.startswith(".git/"):
            errors.append(f"manifest includes Git metadata: {relative}")
            continue
        try:
            path = _manifest_path(ROOT, relative)
        except (OSError, ValueError) as exc:
            errors.append(f"unsafe or missing source manifest file: {relative}: {exc}")
            continue
        if not path.is_file():
            errors.append(f"manifest entry is not a file: {relative}")
            continue
        data = path.read_bytes()
        if (
            not relative.startswith(".devad/")
            and b"\r\n" in data
            and b"\0" not in data
        ):
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                pass
            else:
                errors.append(f"manifest includes CRLF UTF-8 text: {relative}")
                continue
        if hashlib.sha256(data).hexdigest() != digest:
            errors.append(f"manifest mismatch: {relative}")
    try:
        expected = _eligible_manifest_paths(ROOT)
    except (OSError, ValueError) as exc:
        errors.append(f"unsafe package path during manifest enumeration: {exc}")
        return
    for relative in sorted(expected - listed):
        errors.append(f"source file is unlisted: {relative}")
    for relative in sorted(listed - expected):
        errors.append(f"manifest entry is not an eligible source file: {relative}")


def validate_skills(errors: list[str]) -> None:
    actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    if actual != set(SKILLS):
        errors.append(f"skill set mismatch: {sorted(actual)}")
    for name in SKILLS:
        path = ROOT / "skills" / name / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing skill: {name}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        if not text.startswith("---\n") or f"name: {name}" not in text:
            errors.append(f"invalid skill frontmatter: {name}")
        cap = 350 if name == "smooth-coding" else 300
        if len(text.splitlines()) > cap:
            errors.append(f"skill entrypoint over {cap} lines: {name}")
    manager_shim = ROOT / "skills" / "devad-x9-manager" / "SKILL.md"
    if manager_shim.is_file():
        text = manager_shim.read_text(encoding="utf-8-sig")
        if "x9-loop-style" not in text or len(text.splitlines()) > 40:
            errors.append("manager compatibility shim is not a small style redirect")
    loop_compat = ROOT / "skills" / "devad-x9-loop" / "SKILL.md"
    if loop_compat.is_file():
        redirect = "\n".join(loop_compat.read_text(encoding="utf-8-sig").splitlines()[:24])
        if "$x9-loop-style" not in redirect or "Archived V7 contract" not in redirect:
            errors.append("V7 compatibility skill lacks the required top-level style redirect")


def validate_registry(errors: list[str]) -> None:
    try:
        legacy = json.loads((ROOT / "legacy.inventory.json").read_text(encoding="utf-8-sig"))
        registry = json.loads((ROOT / "features.registry.json").read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"registry load failed: {exc}")
        return
    old_ids = {item["id"] for item in legacy.get("items", [])}
    features = registry.get("features", [])
    covered = [item.get("legacy_id") for item in features if item.get("legacy_id")]
    if len(covered) != len(set(covered)):
        errors.append("duplicate legacy feature classifications")
    missing = sorted(old_ids - set(covered))
    if missing:
        errors.append(f"unclassified legacy features: {len(missing)}")
    for feature in features:
        for field in ("id", "owner", "source", "status", "purpose", "required_test"):
            if not feature.get(field):
                errors.append(f"feature missing {field}: {feature.get('id')}")
        status = feature.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"invalid feature status: {feature.get('id')}:{status}")
        if status in {"MOVED", "ADAPTED", "RETIRED"}:
            if not feature.get("replacement") or not feature.get("reason"):
                errors.append(f"feature missing replacement/reason: {feature.get('id')}")


def validate_template(errors: list[str]) -> None:
    template = ROOT / "templates" / "x9-project" / ".devad"
    router = template / "ROUTER.md"
    if not router.is_file() or "Read this file first" not in router.read_text(encoding="utf-8-sig"):
        errors.append("missing manifest-first project router")
    loop = template / "manager" / "loop"
    actual_loop = {path.name for path in loop.iterdir() if path.is_file()} if loop.is_dir() else set()
    if actual_loop != LOOP_FILES:
        errors.append(f"loop template mismatch: {sorted(actual_loop)}")
    capsule = loop / "PASS_CAPSULE.json"
    if capsule.is_file() and capsule.stat().st_size >= 8192:
        errors.append("template PASS_CAPSULE is not below 8 KB")

    for path in template.rglob("*"):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            errors.append(f"generated cache included: {path.relative_to(ROOT)}")
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        if path.name in CAP_NAMES:
            text = path.read_text(encoding="utf-8-sig")
            if len(text.splitlines()) > 120 or len(path.read_bytes()) > 12_000:
                errors.append(f"active file over compact cap: {path.relative_to(ROOT)}")

    link_re = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for path in template.rglob("*.md"):
        for target in link_re.findall(path.read_text(encoding="utf-8-sig")):
            if target.startswith(("http://", "https://", "#", "/")) or "<" in target or ">" in target:
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                errors.append(f"broken template link: {path.relative_to(ROOT)} -> {target}")


def validate_loop_lite(errors: list[str]) -> None:
    loop_lite = ROOT / "templates" / "x9-project" / ".devad" / "manager" / "loop-lite"
    if not loop_lite.is_dir():
        errors.append("missing loop-lite template")
        return
    missing = sorted(name for name in LOOP_LITE_FILES if not (loop_lite / name).exists())
    if missing:
        if "SNAPSHOT.json" in missing:
            errors.append("missing loop-lite recovery snapshot")
        errors.extend(f"missing loop-lite artifact: {name}" for name in missing if name != "SNAPSHOT.json")
        return
    controller = ROOT / LOOP_LITE_CONTROLLER
    if not controller.is_file():
        errors.append("missing loop-lite controller")
    owner_store = loop_lite.parent / "owner-packets"
    owner_files = (
        {path.name for path in owner_store.iterdir() if path.is_file()}
        if owner_store.is_dir()
        else set()
    )
    if owner_files != OWNER_PACKET_FILES:
        errors.append(f"owner-packet template mismatch: {sorted(owner_files)}")
    else:
        owner_ignores = set(
            (owner_store / ".gitignore")
            .read_text(encoding="utf-8-sig")
            .splitlines()
        )
        if not {"*", "!.gitignore", "!README.md"}.issubset(owner_ignores):
            errors.append("owner-packet local-only ignore is incomplete")
        owner_readme = (owner_store / "README.md").read_text(
            encoding="utf-8-sig"
        )
        if "local sensitive state" not in owner_readme:
            errors.append("owner-packet privacy policy is missing")
    ignored = set((loop_lite / ".gitignore").read_text(encoding="utf-8-sig").splitlines())
    missing_ignores = sorted(LOOP_LITE_IGNORES - ignored)
    if missing_ignores:
        errors.append(f"loop-lite gitignore incomplete: {missing_ignores}")
    snapshot = loop_lite / "SNAPSHOT.json"
    if snapshot.stat().st_size >= 8192:
        errors.append("loop-lite recovery snapshot is not below 8 KB")
    try:
        snapshot_raw = snapshot.read_bytes()
        payload = json.loads(snapshot_raw)
    except json.JSONDecodeError:
        errors.append("invalid loop-lite V3 snapshot JSON")
        return
    try:
        loopctl_path = ROOT / LOOP_LITE_CONTROLLER
        module_name = "_x9_validate_suite_loopctl"
        spec = importlib.util.spec_from_file_location(module_name, loopctl_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("loop-lite controller import unavailable")
        loopctl = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = loopctl
        spec.loader.exec_module(loopctl)
        loopctl.Controller(ROOT / "templates" / "x9-project")._decode_snapshot(snapshot_raw)
    except Exception as exc:
        errors.append(f"loop-lite {LOOP_LITE_SNAPSHOT_SCHEMA} runtime validation failed: {exc}")
    contracts = loop_lite / "contracts"
    actual_contracts = {path.name for path in contracts.glob("*.json")}
    if actual_contracts != LOOP_LITE_CONTRACTS:
        errors.append(f"loop-lite contract mismatch: {sorted(actual_contracts)}")
    for path in contracts.glob("*.json"):
        maximum = LOOP_LITE_CONTRACT_CAPS.get(path.name, 0)
        if not maximum or path.stat().st_size > maximum:
            errors.append(f"loop-lite contract over compact cap: {path.relative_to(ROOT)}")

    root_contracts = {"APPROVED_JOBS.json", "MIGRATION_CLASSIFICATION.json"}
    for name, schema in V7_CANONICAL_JSON.items():
        path = (loop_lite if name in root_contracts else contracts) / name
        try:
            raw = path.read_bytes()
            contract_payload = json.loads(raw)
        except (FileNotFoundError, json.JSONDecodeError):
            errors.append(f"invalid V7 canonical JSON: {path.relative_to(ROOT)}")
            continue
        if (
            _contains_float(contract_payload)
            or raw != _canonical_json_bytes(contract_payload)
            or contract_payload.get("schema") != schema
        ):
            errors.append(f"non-canonical V7 contract: {path.relative_to(ROOT)}")

    try:
        approved_jobs = json.loads((loop_lite / "APPROVED_JOBS.json").read_bytes())
    except (FileNotFoundError, json.JSONDecodeError):
        approved_jobs = {}
    if approved_jobs.get("jobs") != []:
        errors.append("V7 approved job manifest must default to empty")
    try:
        action_payload = json.loads((contracts / "ACTION.json").read_text(encoding="utf-8-sig"))
        task_payload = json.loads((contracts / "TASK.json").read_text(encoding="utf-8-sig"))
        owner_payload = json.loads((contracts / "OWNER_PACKET.json").read_text(encoding="utf-8-sig"))
        result_payload = json.loads((contracts / "RESULT.json").read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError):
        return
    expected_action_fields = {
        "action",
        "action_id",
        "attempt",
        "dispatch_id",
        "must_record_transport",
        "schema",
        "target_actor_id",
        "target_role",
        "project_profile_id",
        "task_id",
        "work_order_path",
        "work_order_id",
        "work_order_sha256",
    }
    if (
        set(action_payload) != expected_action_fields
        or action_payload.get("schema") != "x9-loop-action-v2"
        or action_payload.get("action") != "SEND_WORK_ORDER"
        or action_payload.get("target_role") != "WORKER"
        or action_payload.get("must_record_transport") is not True
        or action_payload.get("work_order_path")
        != ".devad/manager/loop-lite/runtime/work-orders/<work_order_id>/WORK_ORDER.json"
        or "packet" in action_payload
    ):
        errors.append("loop-lite action contract is not minimal V7 Work Order transport")
    if task_payload.get("kind") != "task" or not {"owner_packet_path", "owner_packet_sha256"}.issubset(task_payload) or task_payload.get("owner_packet_path") != ".devad/manager/owner-packets/<packet_sha256>.json":
        errors.append("loop-lite task contract missing content-addressed owner packet")
    attachments = owner_payload.get("attachments")
    if owner_payload.get("schema") != "x9-owner-packet-v1" or "packet_sha256" in owner_payload or not isinstance(attachments, list) or not attachments or attachments[0].get("path") != ".devad/manager/owner-packets/artifacts/<attachment_sha256>.txt":
        errors.append("loop-lite owner packet contract is not controller-compatible")
    proof = result_payload.get("proof")
    expected_proof_paths = {
        "security": ".devad/workers/<worker_id>/proof/<event_id>/security.json",
        "tests": ".devad/workers/<worker_id>/proof/<event_id>/tests.json",
    }
    proof_is_structured = isinstance(proof, list) and bool(proof) and all(
        isinstance(item, dict) and {"kind", "path", "sha256"}.issubset(item)
        for item in proof
    ) and {item["kind"] for item in proof} == {"security", "tests"} and {item["kind"]: item["path"] for item in proof} == expected_proof_paths
    change_map = result_payload.get("change_map")
    change_map_valid = (
        isinstance(change_map, dict)
        and set(change_map)
        == {"changed_surface", "proof_refs", "reason", "remaining_risk", "rollback"}
        and isinstance(change_map.get("changed_surface"), list)
        and isinstance(change_map.get("proof_refs"), list)
        and all(
            isinstance(change_map.get(field), str) and change_map[field]
            for field in ("reason", "remaining_risk", "rollback")
        )
    )
    if (
        result_payload.get("schema") != "x9-loop-result-v2"
        or result_payload.get("outcome") != "SUCCESS"
        or not isinstance(result_payload.get("work_order_id"), str)
        or not isinstance(result_payload.get("work_order_sha256"), str)
        or not proof_is_structured
        or not change_map_valid
        or change_map["changed_surface"] != result_payload.get("changed_files")
        or change_map["proof_refs"] != [item["path"] for item in result_payload["proof"]]
        or not isinstance(result_payload.get("c1"), str)
        or not isinstance(result_payload.get("c2"), str)
    ):
        errors.append("loop-lite result contract missing V7 Work Order, change map, or C1/C2 proof")


def validate_metadata(errors: list[str]) -> None:
    try:
        kit = json.loads((ROOT / "kit.manifest.json").read_text(encoding="utf-8-sig"))
        index = json.loads((ROOT / "skills.index.json").read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"package metadata load failed: {exc}")
        return
    if (
        kit.get("version") != "7.3-lite"
        or kit.get("runtime_truth_root") != ".devad/manager/loop-lite"
        or kit.get("name") != "X9 Loop Style (stable) + Code Trial"
        or kit.get("manager_skill") != "x9-loop-style"
        or kit.get("experimental_engine_skill") != "x9-loop-code"
        or kit.get("default_mode") != "STYLE_ONLY"
    ):
        errors.append("kit manifest does not name the Style default and Code trial boundary")
    if (
        kit.get("schema") != "devad-x9-loop-codex-kit-v7.3-lite"
        or index.get("schema") != "devad-x9-loop-kit-v7.3-lite"
        or index.get("date") != "2026-07-30"
        or kit.get("packaged_skills") != len(SKILLS)
    ):
        errors.append("package metadata schema/date is not V7.3 Lite")


def validate_no_generated_cache(errors: list[str]) -> None:
    listed = set()
    manifest = ROOT / "SOURCE_MANIFEST.sha256"
    if manifest.is_file():
        for line in manifest.read_text(encoding="utf-8-sig").splitlines():
            if "  " in line:
                listed.add(line.split("  ", 1)[1])
    for root_name in ("skills", "scripts", "templates"):
        for path in (ROOT / root_name).rglob("*"):
            relative = path.relative_to(ROOT).as_posix()
            if (
                ("__pycache__" in path.parts or path.suffix == ".pyc")
                and relative in listed
            ):
                errors.append(f"generated cache included: {path.relative_to(ROOT)}")
            if path.is_file() and "loop-lite" in path.parts and (path.name in {"loop.db", "loop.db-shm", "loop.db-wal"} or "runtime" in path.parts):
                errors.append(f"generated loop-lite runtime included: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    validate_manifest(errors)
    validate_skills(errors)
    validate_registry(errors)
    validate_template(errors)
    validate_loop_lite(errors)
    validate_metadata(errors)
    validate_no_generated_cache(errors)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print("PASS: X9 Loop V7 skills, registry, manifest, compact template, JSON, and links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
