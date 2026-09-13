#!/usr/bin/env python3
"""Deterministic, local controller for the bounded X9 Loop Lite v6 state."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import importlib.util
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import threading
import tomllib
import uuid
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Callable, Mapping


class LoopError(RuntimeError):
    pass


class SnapshotExportError(LoopError):
    pass


class StateNotDurableError(LoopError):
    pass


class IdentityError(LoopError):
    pass


class ClaimConflictError(LoopError):
    pass


class ResourceConflictError(LoopError):
    pass


class TaskNotReadyError(LoopError):
    pass


class DeliveryError(LoopError):
    pass


class StaleCompletionError(LoopError):
    pass


class ScopeBreachError(LoopError):
    pass


class GitStateError(LoopError):
    pass


class _InboxAlreadyConsumed(RuntimeError):
    pass


def _load_v7_contract():
    path = Path(__file__).with_name("v7_contract.py").resolve()
    name = "_x9_loop_v7_contract_" + hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    module = sys.modules.get(name)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_snapshot_capacity():
    path = Path(__file__).with_name("snapshot_capacity.py").resolve()
    name = "_x9_loop_snapshot_capacity_" + hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    module = sys.modules.get(name)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_program_import():
    path = Path(__file__).with_name("program_import.py").resolve()
    name = "_x9_loop_program_import_" + hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    module = sys.modules.get(name)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_project_brain():
    path = Path(__file__).with_name("project_brain.py").resolve()
    name = "_x9_loop_project_brain_" + hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    module = sys.modules.get(name)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
SCHEMA_V1 = "x9-loop-lite-snapshot-v1"
SCHEMA_V2 = "x9-loop-lite-snapshot-v2"
SCHEMA = "x9-loop-lite-snapshot-v3"
TERMINAL_TASK_ORDER_STATUS_PAIRS = {
    ("COMPLETE", "COMPLETE"),
    ("SUPERSEDED", "SUPERSEDED"),
}
DB_USER_VERSION = 3
V7_FENCE_FUNCTION = "x9_v7_write_allowed"
V7_FENCE_TRIGGER_SQL = {
    "x9_v7_write_fence_insert": """
CREATE TRIGGER x9_v7_write_fence_insert
BEFORE INSERT ON meta
WHEN NEW.key = 'generation' AND x9_v7_write_allowed() != 1
BEGIN
  SELECT RAISE(ABORT, 'X9_V7_WRITE_FENCED');
END
""".strip(),
    "x9_v7_write_fence_update": """
CREATE TRIGGER x9_v7_write_fence_update
BEFORE UPDATE OF value ON meta
WHEN NEW.key = 'generation' AND x9_v7_write_allowed() != 1
BEGIN
  SELECT RAISE(ABORT, 'X9_V7_WRITE_FENCED');
END
""".strip(),
}
V1_SNAPSHOT_TABLES = (
    "actors", "worktrees", "tasks", "claims", "resources", "dispatches",
    "deliveries", "events", "gates", "outbox", "metrics",
)
V2_SNAPSHOT_TABLES = (
    *V1_SNAPSHOT_TABLES,
    "programs", "work_orders", "worktree_classifications",
    "call_reservations",
)
SNAPSHOT_TABLES = (*V2_SNAPSHOT_TABLES, "inbox")


SNAPSHOT_COLUMNS = {
    "actors": ("actor_id", "role", "title", "model"),
    "worktrees": ("worktree_id", "path", "repository_id"),
    "tasks": ("task_id", "worker_id", "worktree_id", "base_sha", "owner_packet_path", "owner_packet_sha256", "dependencies", "finish_line", "status"),
    "claims": ("task_id", "path", "kind"), "resources": ("task_id", "resource"),
    "dispatches": ("dispatch_id", "task_id", "sender_id", "target_id", "packet_sha256", "packet", "supersedes", "status", "created_at"),
    "deliveries": ("id", "dispatch_id", "phase", "method", "result", "created_at"),
    "events": ("event_id", "task_id", "dispatch_id", "event_sha256", "created_at"),
    "gates": ("task_id", "name", "status", "note"), "outbox": ("dispatch_id", "payload"), "metrics": ("key", "value"),
    "programs": ("program_id", "packet_path", "packet_sha256", "source_git_sha", "source_root_sha256", "status", "imported_at"),
    "work_orders": ("work_order_id", "task_id", "worker_id", "packet_path", "packet_sha256", "program_id", "status", "created_at"),
    "worktree_classifications": ("worktree_id", "classification", "owner_decision_sha256"),
    "call_reservations": ("call_id", "work_order_id", "sequence", "action_class", "attempt", "prompt_prefix_sha256", "tool_schema_sha256", "status", "created_at"),
    "inbox": ("event_id", "task_id", "dispatch_id", "event_sha256", "payload", "status", "created_at"),
}
V2_SNAPSHOT_COLUMNS = {
    table: SNAPSHOT_COLUMNS[table]
    for table in V2_SNAPSHOT_TABLES
}
COMPLETED_TASK_ID_CAP = 16
GIT_TIMEOUT_SECONDS = 10
def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def coding_limit(successful_dispatches: int, metrics: dict[str, Any]) -> int:
    failure_keys = (
        "lost_work", "duplicate_delivery", "stale_completion", "scope_breach",
        "parser_failure", "orphan_lock", "false_pass", "context_compaction",
    )
    if any(int(metrics.get(key, 0) or 0) for key in failure_keys):
        return 1
    if successful_dispatches >= 10:
        return 3
    if successful_dispatches >= 3:
        return 2
    return 1


class Controller:
    def __init__(self, repo: Path | str, now_fn: Callable[[], str] | None = None):
        self.repo = Path(repo).resolve()
        self.root = self.repo / ".devad" / "manager" / "loop-lite"
        self.db_path = self.root / "loop.db"
        self.snapshot_path = self.root / "SNAPSHOT.json"
        self.action_path = self.root / "runtime" / "ACTION.json"
        self.approved_jobs_path = self.root / "APPROVED_JOBS.json"
        self.migration_state_path = self.root / "MIGRATION_STATE.json"
        self.project_profile_path = self.root / "PROJECT_PROFILE.json"
        self._mutation_lock = threading.RLock()
        self.now_fn = now_fn or (lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"))

    @property
    def loop_contract(self):
        return _load_v7_contract()

    def _ensure_project_profile(
        self, connection: sqlite3.Connection | None = None
    ) -> str:
        contract = _load_v7_contract()
        stored_id: str | None = None
        if connection is not None:
            row = connection.execute(
                "SELECT value FROM meta WHERE key='project_profile_id'"
            ).fetchone()
            if row:
                stored_id = row[0]
        self._safe_state_path(
            self.project_profile_path, create_parents=True
        )
        document: dict[str, Any] | None = None
        if self.project_profile_path.is_file():
            try:
                raw = self.project_profile_path.read_bytes()
                parsed = json.loads(raw)
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
            ) as exc:
                raise IdentityError("PROJECT_PROFILE_INVALID") from exc
            if (
                not isinstance(parsed, dict)
                or set(parsed) != {"project_profile_id", "schema"}
                or parsed.get("schema") != "x9-loop-project-profile-v1"
                or contract.canonical_json_bytes(parsed) != raw
            ):
                raise IdentityError("PROJECT_PROFILE_INVALID")
            document = parsed
        profile_id = (
            document["project_profile_id"]
            if document is not None
            else stored_id
            if stored_id is not None
            else "profile-" + uuid.uuid4().hex
        )
        if (
            not isinstance(profile_id, str)
            or re.fullmatch(r"[A-Za-z0-9._:-]{16,128}", profile_id)
            is None
            or (stored_id is not None and stored_id != profile_id)
        ):
            raise IdentityError("PROJECT_PROFILE_INVALID")
        expected = {
            "project_profile_id": profile_id,
            "schema": "x9-loop-project-profile-v1",
        }
        expected_raw = contract.canonical_json_bytes(expected)
        if document is None:
            self._atomic_state_write(
                self.project_profile_path, expected_raw
            )
        elif self.project_profile_path.read_bytes() != expected_raw:
            raise IdentityError("PROJECT_PROFILE_INVALID")
        if connection is not None:
            connection.execute(
                "INSERT INTO meta(key,value) VALUES"
                "('project_profile_id',?) ON CONFLICT(key) DO UPDATE "
                "SET value=excluded.value",
                (profile_id,),
            )
        return profile_id

    def _validate_project_context(
        self,
        feature: Mapping[str, Any],
        *,
        phase: str,
        connection: sqlite3.Connection | None = None,
    ) -> dict[str, Any]:
        if not feature.get("context_capsule_ref"):
            return {"status": "LEGACY_CONTEXT", "phase": phase}
        brain = _load_project_brain()
        try:
            profile_id = self._ensure_project_profile(connection)
            return brain.validate_feature_packet_context(
                self.repo,
                feature,
                profile_id=profile_id,
                phase=phase,
                allow_legacy=False,
            )
        except brain.ProjectBrainError as exc:
            raise IdentityError(exc.code) from exc

    @staticmethod
    def _resolve_under(root: Path, path: Path) -> Path:
        resolved_root = root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
        return resolved_path

    @staticmethod
    def _is_reparse(path: Path) -> bool:
        metadata = path.lstat()
        attributes = int(getattr(metadata, "st_file_attributes", 0) or 0)
        reparse_flag = int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
        return stat.S_ISLNK(metadata.st_mode) or bool(attributes & reparse_flag)

    def _safe_state_path(
        self, path: Path, *, create_parents: bool = False, directory: bool = False
    ) -> Path:
        candidate = Path(os.path.abspath(path))
        try:
            relative = candidate.relative_to(self.repo)
        except ValueError as exc:
            raise LoopError("STATE_PATH_UNSAFE") from exc
        parent_parts = relative.parts if directory else relative.parts[:-1]
        current = self.repo
        for part in parent_parts:
            current = current / part
            if os.path.lexists(current):
                if self._is_reparse(current) or not current.is_dir():
                    raise LoopError("STATE_PATH_UNSAFE")
            elif create_parents:
                try:
                    current.mkdir()
                except FileExistsError:
                    pass
                if not os.path.lexists(current) or self._is_reparse(current) or not current.is_dir():
                    raise LoopError("STATE_PATH_UNSAFE")
            else:
                break
            try:
                current.resolve(strict=True).relative_to(self.repo)
            except (OSError, ValueError, RuntimeError) as exc:
                raise LoopError("STATE_PATH_UNSAFE") from exc
        if os.path.lexists(candidate):
            if self._is_reparse(candidate):
                raise LoopError("STATE_PATH_UNSAFE")
            try:
                candidate.resolve(strict=True).relative_to(self.repo)
            except (OSError, ValueError, RuntimeError) as exc:
                raise LoopError("STATE_PATH_UNSAFE") from exc
        return candidate

    def _atomic_state_write(self, path: Path, data: bytes) -> None:
        target = self._safe_state_path(path, create_parents=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        self._safe_state_path(
            target.parent, create_parents=True, directory=True
        )
        target = self._safe_state_path(target, create_parents=True)
        temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        self._safe_state_path(temporary, create_parents=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= int(getattr(os, "O_NOFOLLOW", 0) or 0)
        descriptor = os.open(temporary, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            self._safe_state_path(temporary)
            os.replace(temporary, target)
            self._safe_state_path(target)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if os.path.lexists(temporary):
                try:
                    temporary.unlink()
                except OSError:
                    pass

    def _write_state_once(
        self, path: Path, data: bytes, packet_name: str
    ) -> bool:
        contract = self.loop_contract
        contract.validate_packet_cap(packet_name, data)
        target = self._safe_state_path(path, create_parents=True)
        if os.path.lexists(target):
            if self._is_reparse(target) or not target.is_file():
                raise StateNotDurableError("RESULT_READY_PATH_INVALID")
            if target.stat().st_size > contract.PACKET_CAPS[packet_name]:
                raise StateNotDurableError("RESULT_READY_PACKET_TOO_LARGE")
            if target.read_bytes() == data:
                return False
            raise IdentityError("RESULT_READY_FILE_CONFLICT")
        temporary = target.with_name(
            f".{target.name}.{uuid.uuid4().hex}.tmp"
        )
        descriptor = -1
        try:
            self._safe_state_path(temporary, create_parents=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            flags |= int(getattr(os, "O_NOFOLLOW", 0) or 0)
            descriptor = os.open(temporary, flags, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                if self._is_reparse(target) or not target.is_file():
                    raise StateNotDurableError("RESULT_READY_PATH_INVALID")
                if target.read_bytes() == data:
                    return False
                raise IdentityError("RESULT_READY_FILE_CONFLICT")
            return True
        except (IdentityError, StateNotDurableError):
            raise
        except OSError as exc:
            raise StateNotDurableError("RESULT_READY_WRITE_FAILED") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if os.path.lexists(temporary):
                try:
                    temporary.unlink()
                except OSError:
                    pass

    @staticmethod
    def _result_ready_id(value: str) -> str:
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value) is None:
            raise IdentityError("RESULT_READY_EVENT_ID_INVALID")
        return value

    def result_ready_path(self, event_id: str) -> Path:
        return (
            self.root / "runtime" / "result-ready"
            / self._result_ready_id(event_id) / "RESULT_READY.json"
        )

    def _result_ready_state_path(self, event_id: str) -> Path:
        return self.result_ready_path(event_id).with_name("STATE.json")

    def _loop_incident_path(self, event_id: str) -> Path:
        return self.result_ready_path(event_id).with_name("LOOP_INCIDENT.json")

    def _read_profile_id(self) -> str:
        try:
            raw = self.project_profile_path.read_bytes()
            value = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IdentityError("PROJECT_PROFILE_INVALID") from exc
        expected = {
            "project_profile_id": value.get("project_profile_id")
            if isinstance(value, dict)
            else None,
            "schema": "x9-loop-project-profile-v1",
        }
        if (
            not isinstance(value, dict)
            or set(value) != set(expected)
            or value != expected
            or self.loop_contract.canonical_json_bytes(value) != raw
        ):
            raise IdentityError("PROJECT_PROFILE_INVALID")
        return value["project_profile_id"]

    def _result_ready_row(
        self,
        event_id: str,
        identity: Mapping[str, Any] | None = None,
    ) -> sqlite3.Row:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT e.event_id,e.task_id,e.dispatch_id,e.event_sha256,"
                "d.sender_id,d.target_id,d.packet_sha256,d.status AS dispatch_status,"
                "t.worker_id,t.worktree_id,t.status AS task_status,"
                "w.path AS worktree_path,wo.work_order_id,"
                "wo.packet_sha256 AS work_order_sha256,"
                "wo.status AS work_order_status "
                "FROM events e JOIN dispatches d ON d.dispatch_id=e.dispatch_id "
                "JOIN tasks t ON t.task_id=e.task_id "
                "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "JOIN work_orders wo ON wo.task_id=t.task_id "
                "WHERE e.event_id=?",
                (event_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise IdentityError("RESULT_READY_EVENT_UNKNOWN")
        expected = {
            "dispatch_id": row["dispatch_id"],
            "event_id": row["event_id"],
            "packet_sha256": row["packet_sha256"],
            "result_path": (
                f".devad/workers/{row['worker_id']}/receipts/"
                f"{row['event_id']}.json"
            ),
            "result_sha256": row["event_sha256"],
            "task_id": row["task_id"],
            "work_order_id": row["work_order_id"],
            "work_order_sha256": row["work_order_sha256"],
            "worker_id": row["worker_id"],
        }
        if identity is not None and dict(identity) != expected:
            raise IdentityError("RESULT_READY_IDENTITY_MISMATCH")
        if (
            row["dispatch_status"] != "COMPLETE"
            or row["dispatch_id"] != expected["dispatch_id"]
            or row["task_id"] != expected["task_id"]
            or row["packet_sha256"] != row["work_order_sha256"]
        ):
            raise IdentityError("RESULT_READY_STATE_INVALID")
        return row

    def _result_ready_identity_from_row(
        self, row: sqlite3.Row
    ) -> dict[str, str]:
        return {
            "dispatch_id": row["dispatch_id"],
            "event_id": row["event_id"],
            "packet_sha256": row["packet_sha256"],
            "result_path": (
                f".devad/workers/{row['worker_id']}/receipts/"
                f"{row['event_id']}.json"
            ),
            "result_sha256": row["event_sha256"],
            "task_id": row["task_id"],
            "work_order_id": row["work_order_id"],
            "work_order_sha256": row["work_order_sha256"],
            "worker_id": row["worker_id"],
        }

    def _read_result_ready_result(
        self, row: sqlite3.Row, identity: Mapping[str, Any]
    ) -> dict[str, Any]:
        root = Path(row["worktree_path"])
        try:
            result_path = self._resolve_under(
                root,
                root / Path(*PurePosixPath(identity["result_path"]).parts),
            )
            raw = result_path.read_bytes()
            if len(raw) > self.loop_contract.PACKET_CAPS["RESULT.json"]:
                raise IdentityError("RESULT_READY_RESULT_TOO_LARGE")
            document = json.loads(raw)
        except IdentityError:
            raise
        except (
            OSError,
            UnicodeDecodeError,
            ValueError,
            RuntimeError,
        ) as exc:
            raise IdentityError("RESULT_READY_RESULT_INVALID") from exc
        if (
            not isinstance(document, dict)
            or self.loop_contract.canonical_json_bytes(document) != raw
            or hashlib.sha256(raw).hexdigest() != identity["result_sha256"]
        ):
            raise IdentityError("RESULT_READY_RESULT_HASH_MISMATCH")
        expected = {
            field: identity[field]
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
            validated, _disposition = self.loop_contract.validate_worker_result(
                document, expected
            )
        except self.loop_contract.ContractError as exc:
            raise IdentityError("RESULT_READY_RESULT_INVALID") from exc
        if validated != document:
            raise IdentityError("RESULT_READY_RESULT_INVALID")
        return document

    def _result_ready_callback_id(
        self, identity: Mapping[str, Any], requester_id: str
    ) -> str:
        seed = {
            "expected_result_identity": dict(identity),
            "return_to_task_id": requester_id,
        }
        return "rr-" + hashlib.sha256(
            self.loop_contract.canonical_json_bytes(seed)
        ).hexdigest()[:32]

    def _result_ready_expiry(self) -> str:
        value = self.now_fn()
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return (
                parsed + timedelta(hours=1)
            ).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        except (TypeError, ValueError):
            return value

    def _result_ready_state(
        self, event_id: str
    ) -> tuple[dict[str, Any], bytes] | None:
        path = self._result_ready_state_path(event_id)
        try:
            path = self._safe_state_path(path)
        except LoopError as exc:
            raise StateNotDurableError("RESULT_READY_STATE_INVALID") from exc
        if not path.exists():
            return None
        if self._is_reparse(path) or not path.is_file():
            raise StateNotDurableError("RESULT_READY_STATE_INVALID")
        try:
            raw = self._read_capped_packet(path, "RESULT_READY.json")
            value = json.loads(raw)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            self.loop_contract.ContractError,
        ) as exc:
            raise StateNotDurableError("RESULT_READY_STATE_INVALID") from exc
        required = {
            "callback_id",
            "circuit",
            "event_id",
            "expected_result_identity",
            "expires_at",
            "repair_attempts",
            "schema",
            "signal_sha256",
        }
        if (
            not isinstance(value, dict)
            or set(value) != required
            or value["schema"] != "x9-loop-result-ready-state-v1"
            or value["event_id"] != event_id
            or value["circuit"] not in {"CLOSED", "OPEN"}
            or value["repair_attempts"] not in {0, 1}
            or not isinstance(value["expires_at"], str)
            or self.loop_contract.canonical_json_bytes(value) != raw
        ):
            raise StateNotDurableError("RESULT_READY_STATE_INVALID")
        try:
            self.loop_contract._validate_result_ready_identity(
                value["expected_result_identity"]
            )
        except self.loop_contract.ContractError as exc:
            raise StateNotDurableError("RESULT_READY_STATE_INVALID") from exc
        if (
            not isinstance(value["callback_id"], str)
            or not isinstance(value["signal_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", value["signal_sha256"])
        ):
            raise StateNotDurableError("RESULT_READY_STATE_INVALID")
        return value, raw

    def _emit_result_ready_for_identity(
        self,
        identity: Mapping[str, Any],
        *,
        return_to_task_id: str,
        project_profile_id: str | None = None,
    ) -> dict[str, Any]:
        contract = self.loop_contract
        try:
            signal_path = self._safe_state_path(
                self.result_ready_path(identity["event_id"])
            )
        except LoopError as exc:
            raise IdentityError("RESULT_READY_PATH_INVALID") from exc
        if os.path.lexists(signal_path) and self._is_reparse(signal_path):
            raise IdentityError("RESULT_READY_PATH_INVALID")
        existing_state = self._result_ready_state(identity["event_id"])
        profile_id = project_profile_id or self._read_profile_id()
        if signal_path.is_file():
            try:
                signal_raw = self._read_capped_packet(
                    signal_path, "RESULT_READY.json"
                )
                signal_sha256 = hashlib.sha256(signal_raw).hexdigest()
                signal = contract.validate_result_ready(
                    signal_raw,
                    signal_sha256,
                    profile_id,
                    expected_identity=identity,
                    expected_requester=return_to_task_id,
                )
            except (OSError, LoopError, contract.ContractError) as exc:
                raise IdentityError("RESULT_READY_FILE_CONFLICT") from exc
            callback_id = signal["callback_id"]
            wrote_signal = False
        else:
            callback_id = self._result_ready_callback_id(
                identity, return_to_task_id
            )
            expires_at = (
                existing_state[0]["expires_at"]
                if existing_state is not None
                else self._result_ready_expiry()
            )
            signal = contract.build_result_ready(
                callback_id=callback_id,
                expected_result_identity=identity,
                expires_at=expires_at,
                project_profile_id=profile_id,
                return_to_task_id=return_to_task_id,
            )
            signal_raw = contract.canonical_json_bytes(signal)
            signal_sha256 = hashlib.sha256(signal_raw).hexdigest()
            contract.validate_result_ready(
                signal_raw,
                signal_sha256,
                profile_id,
                expected_identity=identity,
                expected_requester=return_to_task_id,
            )
            wrote_signal = self._write_state_once(
                signal_path, signal_raw, "RESULT_READY.json"
            )
        state = {
            "callback_id": callback_id,
            "circuit": "CLOSED",
            "event_id": identity["event_id"],
            "expected_result_identity": dict(identity),
            "expires_at": signal["expires_at"],
            "repair_attempts": 0,
            "schema": "x9-loop-result-ready-state-v1",
            "signal_sha256": signal_sha256,
        }
        if existing_state is None:
            self._write_state_once(
                self._result_ready_state_path(identity["event_id"]),
                contract.canonical_json_bytes(state),
                "RESULT_READY.json",
            )
        elif (
            existing_state[0]["expected_result_identity"] != identity
            or existing_state[0]["callback_id"] != callback_id
            or existing_state[0]["expires_at"] != signal["expires_at"]
            or existing_state[0]["signal_sha256"] != signal_sha256
        ):
            raise IdentityError("RESULT_READY_STATE_CONFLICT")
        return {
            "callback_id": callback_id,
            "event_id": identity["event_id"],
            "path": signal_path.relative_to(self.repo).as_posix(),
            "signal_sha256": signal_sha256,
            "status": "RESULT_READY",
            "written": wrote_signal,
        }

    def _result_ready_input(
        self, signal_file: str | Path
    ) -> tuple[Path, str]:
        candidate = Path(signal_file)
        if not candidate.is_absolute():
            candidate = self.repo / candidate
        candidate = Path(os.path.abspath(candidate))
        event_id = self._result_ready_id(candidate.parent.name)
        expected = Path(os.path.abspath(self.result_ready_path(event_id)))
        if os.path.normcase(str(candidate)) != os.path.normcase(str(expected)):
            raise IdentityError("RESULT_READY_PATH_INVALID")
        return self._safe_state_path(candidate), event_id

    def _read_result_ready_signal(
        self,
        signal_path: Path,
        *,
        requester_id: str,
        expected_identity: Mapping[str, Any] | None = None,
    ) -> tuple[dict[str, Any], bytes]:
        if not signal_path.is_file() or self._is_reparse(signal_path):
            raise IdentityError("RESULT_READY_MISSING")
        try:
            raw = self._read_capped_packet(signal_path, "RESULT_READY.json")
        except (OSError, LoopError, self.loop_contract.ContractError) as exc:
            raise IdentityError("RESULT_READY_INVALID") from exc
        signal_sha256 = hashlib.sha256(raw).hexdigest()
        try:
            signal = self.loop_contract.validate_result_ready(
                raw,
                signal_sha256,
                self._read_profile_id(),
                expected_identity=expected_identity,
                expected_requester=requester_id,
            )
        except self.loop_contract.ContractError as exc:
            raise IdentityError(str(exc)) from exc
        return signal, raw

    def emit_result_ready(self, event_id: str) -> dict[str, Any]:
        """Publish one signal-only callback for an already-consumed result."""
        row = self._result_ready_row(event_id)
        identity = self._result_ready_identity_from_row(row)
        self._read_result_ready_result(row, identity)
        return self._emit_result_ready_for_identity(
            identity,
            return_to_task_id=row["sender_id"],
        )

    def consume_result_ready(
        self,
        signal_file: str | Path,
        *,
        requester_id: str,
    ) -> dict[str, Any]:
        """Re-read the durable result named by one RESULT_READY signal."""
        signal_path, event_id = self._result_ready_input(signal_file)
        signal, signal_raw = self._read_result_ready_signal(
            signal_path, requester_id=requester_id
        )
        identity = signal["expected_result_identity"]
        row = self._result_ready_row(event_id, identity)
        if row["sender_id"] != requester_id:
            raise IdentityError("RESULT_READY_REQUESTER_MISMATCH")
        state = self._result_ready_state(event_id)
        if state is not None:
            state_value, _state_raw = state
            if (
                state_value["expected_result_identity"] != identity
                or state_value["callback_id"] != signal["callback_id"]
                or state_value["signal_sha256"]
                != hashlib.sha256(signal_raw).hexdigest()
            ):
                raise IdentityError("RESULT_READY_STATE_CONFLICT")
            if state_value["circuit"] == "OPEN":
                raise IdentityError("RESULT_READY_CIRCUIT_OPEN")
        result = self._read_result_ready_result(row, identity)
        return {
            "callback_id": signal["callback_id"],
            "event_id": event_id,
            "result_sha256": identity["result_sha256"],
            "status": "RESULT_READY_ACKNOWLEDGED",
            "worker_id": result["worker_id"],
        }

    def _write_result_ready_incident(
        self,
        row: sqlite3.Row,
        identity: Mapping[str, Any],
        *,
        requester_id: str,
        expected_signal_sha256: str,
        state_raw: bytes | None,
    ) -> dict[str, Any]:
        connection = self._connect()
        try:
            claims = [
                dict(item)
                for item in connection.execute(
                    "SELECT path,kind FROM claims WHERE task_id=? "
                    "ORDER BY path,kind",
                    (row["task_id"],),
                )
            ]
        finally:
            connection.close()
        claims_sha256 = _sha(claims)
        state_sha256 = hashlib.sha256(state_raw or b"").hexdigest()
        incident = {
            "actual_transition": "RESULT_READY_REDELIVERY_FAILED",
            "circuit": "OPEN",
            "claims_sha256": claims_sha256,
            "dispatch_id": identity["dispatch_id"],
            "event_id": identity["event_id"],
            "evidence_hashes": {
                "expected_signal_sha256": expected_signal_sha256,
                "result_sha256": identity["result_sha256"],
                "state_sha256": state_sha256,
            },
            "expected_result_identity": dict(identity),
            "expected_transition": "RESULT_READY",
            "host_enforcement": "MODEL_PROFILE_NOT_TOOL_ENFORCED",
            "incident_id": "incident-" + expected_signal_sha256[:32],
            "proposed_regression": (
                "duplicate callback and second redelivery remain idempotent"
            ),
            "repair_outcome": "ONE_REDELIVERY_EXHAUSTED",
            "reproducer": (
                "initial RESULT_READY was unavailable after one bounded repair"
            ),
            "return_to_task_id": requester_id,
            "schema": "x9-loop-incident-v1",
            "task_id": identity["task_id"],
            "worker_id": identity["worker_id"],
            "work_order_id": identity["work_order_id"],
            "worktree_id": row["worktree_id"],
            "worktree_path": row["worktree_path"],
        }
        raw = self.loop_contract.canonical_json_bytes(incident)
        try:
            self.loop_contract.validate_loop_incident(
                raw,
                hashlib.sha256(raw).hexdigest(),
                expected_identity=identity,
            )
        except self.loop_contract.ContractError as exc:
            raise StateNotDurableError("LOOP_INCIDENT_INVALID") from exc
        path = self._loop_incident_path(identity["event_id"])
        wrote = self._write_state_once(path, raw, "LOOP_INCIDENT.json")
        return {
            "incident_path": path.relative_to(self.repo).as_posix(),
            "incident_sha256": hashlib.sha256(raw).hexdigest(),
            "written": wrote,
        }

    def reconcile_result_ready(
        self,
        signal_file: str | Path,
        *,
        requester_id: str,
        expected_result_identity: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform at most one deterministic callback redelivery."""
        signal_path, event_id = self._result_ready_input(signal_file)
        row = self._result_ready_row(event_id)
        identity = self._result_ready_identity_from_row(row)
        if (
            row["sender_id"] != requester_id
            or expected_result_identity is not None
            and dict(expected_result_identity) != identity
        ):
            raise IdentityError("RESULT_READY_IDENTITY_MISMATCH")
        self._read_result_ready_result(row, identity)
        existing_state = self._result_ready_state(event_id)
        signal_exists = signal_path.is_file()
        if signal_exists:
            signal, signal_raw = self._read_result_ready_signal(
                signal_path,
                requester_id=requester_id,
                expected_identity=identity,
            )
            if existing_state is not None:
                state_value, _state_raw = existing_state
                if (
                    state_value["expected_result_identity"] != identity
                    or state_value["callback_id"] != signal["callback_id"]
                    or state_value["signal_sha256"]
                    != hashlib.sha256(signal_raw).hexdigest()
                ):
                    raise IdentityError("RESULT_READY_STATE_CONFLICT")
                if state_value["circuit"] == "OPEN":
                    return {
                        "callback_id": signal["callback_id"],
                        "event_id": event_id,
                        "status": "CIRCUIT_OPEN",
                    }
            return {
                "callback_id": signal["callback_id"],
                "event_id": event_id,
                "status": "ALREADY_DELIVERED",
            }

        contract = self.loop_contract
        state_value = existing_state[0] if existing_state is not None else None
        callback_id = self._result_ready_callback_id(identity, requester_id)
        expires_at = (
            state_value["expires_at"]
            if state_value is not None
            else self._result_ready_expiry()
        )
        signal = contract.build_result_ready(
            callback_id=callback_id,
            expected_result_identity=identity,
            expires_at=expires_at,
            project_profile_id=self._read_profile_id(),
            return_to_task_id=requester_id,
        )
        signal_raw = contract.canonical_json_bytes(signal)
        signal_sha256 = hashlib.sha256(signal_raw).hexdigest()
        if state_value is not None:
            if (
                state_value["callback_id"] != callback_id
                or state_value["expected_result_identity"] != identity
                or state_value["signal_sha256"] != signal_sha256
            ):
                raise IdentityError("RESULT_READY_STATE_CONFLICT")
            if state_value["circuit"] == "OPEN":
                try:
                    incident = self._safe_state_path(
                        self._loop_incident_path(event_id)
                    )
                except LoopError as exc:
                    raise IdentityError("LOOP_INCIDENT_PATH_INVALID") from exc
                if os.path.lexists(incident) and self._is_reparse(incident):
                    raise IdentityError("LOOP_INCIDENT_PATH_INVALID")
                if not incident.is_file():
                    details = self._write_result_ready_incident(
                        row,
                        identity,
                        requester_id=requester_id,
                        expected_signal_sha256=signal_sha256,
                        state_raw=existing_state[1],
                    )
                else:
                    try:
                        incident_raw = self._read_capped_packet(
                            incident, "LOOP_INCIDENT.json"
                        )
                        self.loop_contract.validate_loop_incident(
                            incident_raw,
                            hashlib.sha256(incident_raw).hexdigest(),
                            expected_identity=identity,
                        )
                    except (
                        OSError,
                        UnicodeDecodeError,
                        ValueError,
                        LoopError,
                        self.loop_contract.ContractError,
                    ) as exc:
                        raise IdentityError("LOOP_INCIDENT_INVALID") from exc
                    details = {
                        "incident_path": incident.relative_to(self.repo).as_posix(),
                        "incident_sha256": hashlib.sha256(
                            incident_raw
                        ).hexdigest(),
                    }
                return {
                    "callback_id": callback_id,
                    "event_id": event_id,
                    "status": "CIRCUIT_OPEN",
                    **details,
                }
        attempts = state_value["repair_attempts"] if state_value else 0
        if attempts == 0:
            self._write_state_once(
                signal_path, signal_raw, "RESULT_READY.json"
            )
            repaired_state = {
                "callback_id": callback_id,
                "circuit": "CLOSED",
                "event_id": event_id,
                "expected_result_identity": identity,
                "expires_at": expires_at,
                "repair_attempts": 1,
                "schema": "x9-loop-result-ready-state-v1",
                "signal_sha256": signal_sha256,
            }
            if state_value is None:
                self._write_state_once(
                    self._result_ready_state_path(event_id),
                    contract.canonical_json_bytes(repaired_state),
                    "RESULT_READY.json",
                )
            else:
                self._atomic_state_write(
                    self._result_ready_state_path(event_id),
                    contract.canonical_json_bytes(repaired_state),
                )
            return {
                "callback_id": callback_id,
                "event_id": event_id,
                "signal_sha256": signal_sha256,
                "status": "REDELIVERED",
            }

        details = self._write_result_ready_incident(
            row,
            identity,
            requester_id=requester_id,
            expected_signal_sha256=signal_sha256,
            state_raw=existing_state[1] if existing_state is not None else None,
        )
        opened_state = {
            "callback_id": callback_id,
            "circuit": "OPEN",
            "event_id": event_id,
            "expected_result_identity": identity,
            "expires_at": expires_at,
            "repair_attempts": 1,
            "schema": "x9-loop-result-ready-state-v1",
            "signal_sha256": signal_sha256,
        }
        if state_value is None:
            self._write_state_once(
                self._result_ready_state_path(event_id),
                contract.canonical_json_bytes(opened_state),
                "RESULT_READY.json",
            )
        else:
            self._atomic_state_write(
                self._result_ready_state_path(event_id),
                contract.canonical_json_bytes(opened_state),
            )
        return {
            "callback_id": callback_id,
            "event_id": event_id,
            "status": "CIRCUIT_OPEN",
            **details,
        }

    read_result_ready = consume_result_ready
    repair_result_ready = reconcile_result_ready
    redeliver_result_ready = reconcile_result_ready

    @staticmethod
    def _enable_v7_connection(
        connection: sqlite3.Connection,
        write_allowed: Callable[[], int] | None = None,
    ) -> None:
        callback = write_allowed if write_allowed is not None else (lambda: 1)
        connection.create_function(
            V7_FENCE_FUNCTION,
            0,
            callback,
            deterministic=write_allowed is None,
        )

    def _connect(self) -> sqlite3.Connection:
        self._safe_state_path(self.db_path, create_parents=True)
        connection = sqlite3.connect(self.db_path, isolation_level=None)
        self._enable_v7_connection(
            connection,
            lambda: 0 if self.migration_state_path.exists() else 1,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    @staticmethod
    def _schema_semantics(
        connection: sqlite3.Connection, tables: set[str]
    ) -> dict[str, Any]:
        semantics: dict[str, Any] = {}
        for table in sorted(tables):
            columns = tuple(
                (
                    row["name"],
                    str(row["type"]).upper(),
                    int(row["notnull"]),
                    row["dflt_value"],
                    int(row["pk"]),
                )
                for row in connection.execute(
                    f"PRAGMA table_info({table})"
                )
            )
            foreign_keys = tuple(
                sorted(
                    (
                        row["table"],
                        row["from"],
                        row["to"],
                        row["on_update"],
                        row["on_delete"],
                        row["match"],
                    )
                    for row in connection.execute(
                        f"PRAGMA foreign_key_list({table})"
                    )
                )
            )
            indexes = []
            for index in connection.execute(
                f"PRAGMA index_list({table})"
            ):
                index_columns = tuple(
                    row["name"]
                    for row in connection.execute(
                        f"PRAGMA index_info({index['name']})"
                    )
                )
                indexes.append(
                    (
                        int(index["unique"]),
                        index["origin"],
                        int(index["partial"]),
                        index_columns,
                    )
                )
            semantics[table] = (
                columns,
                foreign_keys,
                tuple(sorted(indexes)),
            )
        return semantics

    @classmethod
    def _trusted_schema_semantics(
        cls, *, version: int
    ) -> dict[str, Any]:
        reference = sqlite3.connect(":memory:")
        reference.row_factory = sqlite3.Row
        cls._enable_v7_connection(reference)
        try:
            cls._schema_v1(reference)
            if version >= 2:
                cls._upgrade_schema_v2(reference)
            if version >= 3:
                cls._upgrade_schema_v3(reference)
            tables = {
                row[0]
                for row in reference.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            return cls._schema_semantics(reference, tables)
        finally:
            reference.close()
    @classmethod
    def _validate_v1_schema_shape(
        cls,
        connection: sqlite3.Connection,
        *,
        allow_fence: bool = False,
    ) -> None:
        objects = [
            dict(row)
            for row in connection.execute(
                "SELECT type,name,tbl_name,sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_autoindex_%' "
                "ORDER BY type,name"
            )
        ]
        expected_tables = {*V1_SNAPSHOT_TABLES, "meta", "sqlite_sequence"}
        tables = {
            row["name"] for row in objects if row["type"] == "table"
        }
        other = [row for row in objects if row["type"] != "table"]
        if tables != expected_tables:
            raise StateNotDurableError("V6_DATABASE_INVALID")
        if allow_fence:
            trigger_sql = {
                row["name"]: " ".join(str(row["sql"]).split())
                for row in other
                if row["type"] == "trigger" and row["tbl_name"] == "meta"
            }
            expected_trigger_sql = {
                name: " ".join(sql.split())
                for name, sql in V7_FENCE_TRIGGER_SQL.items()
            }
            if (
                len(other) != len(expected_trigger_sql)
                or trigger_sql != expected_trigger_sql
            ):
                raise StateNotDurableError("V6_DATABASE_INVALID")
        elif other:
            raise StateNotDurableError("V6_DATABASE_INVALID")
        for table in V1_SNAPSHOT_TABLES:
            columns = tuple(
                row["name"]
                for row in connection.execute(
                    f"PRAGMA table_info({table})"
                )
            )
            if columns != SNAPSHOT_COLUMNS[table]:
                raise StateNotDurableError("V6_DATABASE_INVALID")
        if (
            cls._schema_semantics(connection, expected_tables)
            != cls._trusted_schema_semantics(version=1)
        ):
            raise StateNotDurableError("V6_DATABASE_INVALID")

    @classmethod
    def _validate_v2_schema_shape(
        cls, connection: sqlite3.Connection
    ) -> None:
        objects = [
            dict(row)
            for row in connection.execute(
                "SELECT type,name,tbl_name,sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_autoindex_%' "
                "ORDER BY type,name"
            )
        ]
        extra_tables = {
            "programs",
            "work_orders",
            "worktree_classifications",
            "call_receipts",
            "call_reservations",
        }
        expected_tables = {
            *V1_SNAPSHOT_TABLES,
            "meta",
            "sqlite_sequence",
            *extra_tables,
        }
        tables = {
            row["name"] for row in objects if row["type"] == "table"
        }
        trigger_sql = {
            row["name"]: " ".join(str(row["sql"]).split())
            for row in objects
            if row["type"] == "trigger" and row["tbl_name"] == "meta"
        }
        expected_trigger_sql = {
            name: " ".join(sql.split())
            for name, sql in V7_FENCE_TRIGGER_SQL.items()
        }
        other = [row for row in objects if row["type"] != "table"]
        if (
            tables != expected_tables
            or len(other) != len(expected_trigger_sql)
            or trigger_sql != expected_trigger_sql
            or connection.execute("PRAGMA user_version").fetchone()[0] != 2
        ):
            raise StateNotDurableError("V2_DATABASE_INVALID")
        expected_columns = {
            "meta": ("key", "value"),
            **{
                table: SNAPSHOT_COLUMNS[table]
                for table in V1_SNAPSHOT_TABLES
            },
            "programs": SNAPSHOT_COLUMNS["programs"],
            "work_orders": SNAPSHOT_COLUMNS["work_orders"],
            "worktree_classifications": SNAPSHOT_COLUMNS[
                "worktree_classifications"
            ],
            "call_reservations": SNAPSHOT_COLUMNS[
                "call_reservations"
            ],
            "call_receipts": (
                "call_id",
                "work_order_id",
                "sequence",
                "receipt_sha256",
                "receipt",
                "created_at",
            ),
        }
        for table, expected in expected_columns.items():
            columns = tuple(
                row["name"]
                for row in connection.execute(
                    f"PRAGMA table_info({table})"
                )
            )
            if columns != expected:
                raise StateNotDurableError("V2_DATABASE_INVALID")
        if (
            cls._schema_semantics(connection, expected_tables)
            != cls._trusted_schema_semantics(version=2)
        ):
            raise StateNotDurableError("V2_DATABASE_INVALID")

    @classmethod
    def _validate_v3_schema_shape(
        cls, connection: sqlite3.Connection
    ) -> None:
        objects = [
            dict(row)
            for row in connection.execute(
                "SELECT type,name,tbl_name,sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_autoindex_%' "
                "ORDER BY type,name"
            )
        ]
        expected_tables = {
            *SNAPSHOT_TABLES,
            "call_receipts",
            "meta",
            "sqlite_sequence",
        }
        tables = {
            row["name"] for row in objects if row["type"] == "table"
        }
        trigger_sql = {
            row["name"]: " ".join(str(row["sql"]).split())
            for row in objects
            if row["type"] == "trigger" and row["tbl_name"] == "meta"
        }
        expected_trigger_sql = {
            name: " ".join(sql.split())
            for name, sql in V7_FENCE_TRIGGER_SQL.items()
        }
        other = [row for row in objects if row["type"] != "table"]
        if (
            tables != expected_tables
            or len(other) != len(expected_trigger_sql)
            or trigger_sql != expected_trigger_sql
            or connection.execute("PRAGMA user_version").fetchone()[0]
            != DB_USER_VERSION
        ):
            raise StateNotDurableError("V3_DATABASE_INVALID")
        expected_columns = {
            "meta": ("key", "value"),
            **{
                table: SNAPSHOT_COLUMNS[table]
                for table in SNAPSHOT_TABLES
            },
            "call_receipts": (
                "call_id",
                "work_order_id",
                "sequence",
                "receipt_sha256",
                "receipt",
                "created_at",
            ),
        }
        for table, expected in expected_columns.items():
            columns = tuple(
                row["name"]
                for row in connection.execute(
                    f"PRAGMA table_info({table})"
                )
            )
            if columns != expected:
                raise StateNotDurableError("V3_DATABASE_INVALID")
        if (
            cls._schema_semantics(connection, expected_tables)
            != cls._trusted_schema_semantics(version=3)
        ):
            raise StateNotDurableError("V3_DATABASE_INVALID")

    @staticmethod
    def _schema_v1(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS actors (
              actor_id TEXT PRIMARY KEY, role TEXT NOT NULL, title TEXT NOT NULL, model TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS worktrees (
              worktree_id TEXT PRIMARY KEY, path TEXT NOT NULL, repository_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
              task_id TEXT PRIMARY KEY, worker_id TEXT NOT NULL REFERENCES actors(actor_id),
              worktree_id TEXT NOT NULL REFERENCES worktrees(worktree_id), base_sha TEXT NOT NULL, owner_packet_path TEXT NOT NULL, owner_packet_sha256 TEXT NOT NULL,
               dependencies TEXT NOT NULL, finish_line TEXT NOT NULL, status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS claims (
              task_id TEXT NOT NULL REFERENCES tasks(task_id), path TEXT NOT NULL, kind TEXT NOT NULL,
              PRIMARY KEY(task_id, path)
            );
            CREATE TABLE IF NOT EXISTS resources (
              task_id TEXT NOT NULL REFERENCES tasks(task_id), resource TEXT NOT NULL,
              PRIMARY KEY(task_id, resource)
            );
            CREATE TABLE IF NOT EXISTS dispatches (
              dispatch_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id),
              sender_id TEXT NOT NULL REFERENCES actors(actor_id), target_id TEXT NOT NULL REFERENCES actors(actor_id),
              packet_sha256 TEXT NOT NULL, packet TEXT NOT NULL, supersedes TEXT, status TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS deliveries (
              id INTEGER PRIMARY KEY AUTOINCREMENT, dispatch_id TEXT NOT NULL REFERENCES dispatches(dispatch_id),
              phase TEXT NOT NULL, method TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
              event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id),
              dispatch_id TEXT NOT NULL REFERENCES dispatches(dispatch_id), event_sha256 TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS gates (
              task_id TEXT NOT NULL REFERENCES tasks(task_id), name TEXT NOT NULL, status TEXT NOT NULL,
              note TEXT NOT NULL, PRIMARY KEY(task_id, name)
            );
            CREATE TABLE IF NOT EXISTS outbox (
              dispatch_id TEXT PRIMARY KEY REFERENCES dispatches(dispatch_id), payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS metrics (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """
        )
        connection.execute("INSERT OR IGNORE INTO meta(key, value) VALUES('generation', '0')")

    @staticmethod
    def _upgrade_schema_v2(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS programs (
              program_id TEXT PRIMARY KEY, packet_path TEXT NOT NULL, packet_sha256 TEXT NOT NULL,
              source_git_sha TEXT NOT NULL, source_root_sha256 TEXT NOT NULL, status TEXT NOT NULL,
              imported_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS work_orders (
              work_order_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id),
              worker_id TEXT NOT NULL REFERENCES actors(actor_id), packet_path TEXT NOT NULL,
              packet_sha256 TEXT NOT NULL, program_id TEXT NOT NULL REFERENCES programs(program_id),
              status TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS worktree_classifications (
              worktree_id TEXT PRIMARY KEY REFERENCES worktrees(worktree_id), classification TEXT NOT NULL,
              owner_decision_sha256 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS call_receipts (
              call_id TEXT PRIMARY KEY, work_order_id TEXT NOT NULL REFERENCES work_orders(work_order_id),
              sequence INTEGER NOT NULL, receipt_sha256 TEXT NOT NULL,
              receipt TEXT NOT NULL, created_at TEXT NOT NULL,
              UNIQUE(work_order_id, sequence)
            );
            CREATE TABLE IF NOT EXISTS call_reservations (
              call_id TEXT PRIMARY KEY, work_order_id TEXT NOT NULL REFERENCES work_orders(work_order_id),
              sequence INTEGER NOT NULL, action_class TEXT NOT NULL,
              attempt INTEGER NOT NULL,
              prompt_prefix_sha256 TEXT NOT NULL, tool_schema_sha256 TEXT NOT NULL,
              status TEXT NOT NULL, created_at TEXT NOT NULL,
              UNIQUE(work_order_id, sequence)
            );
            CREATE TRIGGER IF NOT EXISTS x9_v7_write_fence_insert
            BEFORE INSERT ON meta
            WHEN NEW.key = 'generation' AND x9_v7_write_allowed() != 1
            BEGIN
              SELECT RAISE(ABORT, 'X9_V7_WRITE_FENCED');
            END;
            CREATE TRIGGER IF NOT EXISTS x9_v7_write_fence_update
            BEFORE UPDATE OF value ON meta
            WHEN NEW.key = 'generation' AND x9_v7_write_allowed() != 1
            BEGIN
              SELECT RAISE(ABORT, 'X9_V7_WRITE_FENCED');
            END;
            """
        )
        connection.execute("PRAGMA user_version=2")
        connection.execute(
            "INSERT INTO meta(key,value) VALUES('schema_version','2') "
            "ON CONFLICT(key) DO UPDATE SET value='2'"
        )

    @staticmethod
    def _upgrade_schema_v3(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS inbox (
              event_id TEXT PRIMARY KEY,
              task_id TEXT NOT NULL,
              dispatch_id TEXT NOT NULL,
              event_sha256 TEXT NOT NULL,
              payload TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        connection.execute(f"PRAGMA user_version={DB_USER_VERSION}")
        connection.execute(
            "INSERT INTO meta(key,value) VALUES('schema_version','3') "
            "ON CONFLICT(key) DO UPDATE SET value='3'"
        )

    @classmethod
    def _schema(cls, connection: sqlite3.Connection) -> None:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if "meta" in tables and "programs" not in tables:
            raise StateNotDurableError("V2_MIGRATION_REQUIRED")
        if "programs" in tables and "inbox" not in tables:
            raise StateNotDurableError("V3_MIGRATION_REQUIRED")
        if "inbox" in tables:
            cls._validate_v3_schema_shape(connection)
            return
        cls._schema_v1(connection)
        cls._upgrade_schema_v2(connection)
        cls._upgrade_schema_v3(connection)
        cls._validate_v3_schema_shape(connection)

    def _generation(self, connection: sqlite3.Connection) -> int:
        return int(connection.execute("SELECT value FROM meta WHERE key='generation'").fetchone()[0])

    @staticmethod
    def _metric_json_list(connection: sqlite3.Connection, key: str) -> list[str]:
        row = connection.execute("SELECT value FROM metrics WHERE key=?", (key,)).fetchone()
        if not row:
            return []
        try:
            value = json.loads(row[0])
        except (TypeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("METRIC_STATE_INVALID") from exc
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise StateNotDurableError("METRIC_STATE_INVALID")
        return value

    def _completed_task_ids(self, connection: sqlite3.Connection) -> list[str]:
        return self._metric_json_list(connection, "completed_task_ids")

    def _remember_completed_task(self, connection: sqlite3.Connection, task_id: str) -> None:
        values = [task_id, *(item for item in self._completed_task_ids(connection) if item != task_id)]
        connection.execute(
            "INSERT INTO metrics(key,value) VALUES('completed_task_ids',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (_json(values[:COMPLETED_TASK_ID_CAP]),),
        )

    def _mutate(self, operation: Callable[[sqlite3.Connection], Any]) -> Any:
        with self._mutation_lock:
            return self._mutate_locked(operation)

    def _mutate_locked(
        self, operation: Callable[[sqlite3.Connection], Any]
    ) -> Any:
        if self.migration_state_path.exists():
            raise StateNotDurableError("MIGRATION_IN_PROGRESS")
        connection = self._connect()
        bundle: dict[str, Any] | None = None
        try:
            self._schema(connection)
            self._ensure_project_profile(connection)
            current_raw = (
                self.snapshot_path.read_bytes()
                if self.snapshot_path.is_file()
                else None
            )
            if current_raw is not None and not self._snapshot_matches_connection(
                connection, current_raw
            ):
                raise StateNotDurableError("SNAPSHOT_STALE")
            connection.execute("BEGIN IMMEDIATE")
            result = operation(connection)
            generation = self._generation(connection) + 1
            connection.execute(
                "UPDATE meta SET value=? WHERE key='generation'",
                (str(generation),),
            )
            bundle = self._snapshot_bundle(
                connection,
                current_snapshot_raw=current_raw,
                generation=generation,
            )
            self._validate_bundle_targets(bundle)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        try:
            if bundle is None:
                raise SnapshotExportError("SNAPSHOT_EXPORT_FAILED")
            self._write_snapshot_bundle(bundle)
        except Exception as exc:
            try:
                self._safe_state_path(self.action_path)
                if self.action_path.is_file():
                    self.action_path.unlink()
            except (LoopError, OSError) as invalidation_error:
                raise SnapshotExportError(
                    "SNAPSHOT_EXPORT_FAILED:ACTION_INVALIDATION_FAILED"
                ) from invalidation_error
            if isinstance(exc, SnapshotExportError):
                raise
            raise SnapshotExportError("SNAPSHOT_EXPORT_FAILED") from exc
        return result
    def _rows(self, connection: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
        return [dict(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY 1")]

    def _call_receipt_archive(
        self, pending: tuple[str, bytes] | None = None
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        archive_root = self.root / "runtime" / "call-receipts"
        self._safe_state_path(archive_root, directory=True)
        entries: list[dict[str, str]] = []
        call_ids: set[str] = set()
        sequences: dict[str, set[int]] = {}
        if archive_root.is_dir():
            for order_dir in sorted(
                archive_root.iterdir(), key=lambda item: item.name
            ):
                self._safe_state_path(order_dir, directory=True)
                if (
                    not order_dir.is_dir()
                    or re.fullmatch(
                        r"[A-Za-z0-9._:-]{1,128}", order_dir.name
                    )
                    is None
                ):
                    raise StateNotDurableError("CALL_ARCHIVE_INVALID")
                order_sequences = sequences.setdefault(
                    order_dir.name, set()
                )
                for path in sorted(
                    order_dir.iterdir(), key=lambda item: item.name
                ):
                    self._safe_state_path(path)
                    if not path.is_file() or path.suffix != ".json":
                        raise StateNotDurableError(
                            "CALL_ARCHIVE_INVALID"
                        )
                    try:
                        raw = path.read_bytes()
                        receipt = contract.validate_call_receipt(
                            json.loads(raw)
                        )
                    except (
                        OSError,
                        UnicodeDecodeError,
                        json.JSONDecodeError,
                        contract.ContractError,
                    ) as exc:
                        raise StateNotDurableError(
                            "CALL_ARCHIVE_INVALID"
                        ) from exc
                    digest = hashlib.sha256(raw).hexdigest()
                    relative = path.relative_to(self.repo).as_posix()
                    if (
                        contract.canonical_json_bytes(receipt) != raw
                        or path.stem != digest
                        or receipt["call_id"] in call_ids
                        or receipt["sequence"] in order_sequences
                    ):
                        raise StateNotDurableError(
                            "CALL_ARCHIVE_INVALID"
                        )
                    call_ids.add(receipt["call_id"])
                    order_sequences.add(receipt["sequence"])
                    entries.append(
                        {"path": relative, "sha256": digest}
                    )
        if pending is not None:
            relative, raw = pending
            try:
                path = self.repo / Path(*PurePosixPath(relative).parts)
                receipt = contract.validate_call_receipt(json.loads(raw))
            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
                contract.ContractError,
            ) as exc:
                raise StateNotDurableError("CALL_ARCHIVE_INVALID") from exc
            digest = hashlib.sha256(raw).hexdigest()
            parts = PurePosixPath(relative).parts
            if (
                len(parts) != 7
                or parts[:5]
                != (".devad", "manager", "loop-lite", "runtime", "call-receipts")
                or parts[5] not in sequences
                or parts[6] != digest + ".json"
                or contract.canonical_json_bytes(receipt) != raw
                or receipt["call_id"] in call_ids
                or receipt["sequence"] in sequences[parts[5]]
                or os.path.lexists(path)
            ):
                raise StateNotDurableError("CALL_ARCHIVE_INVALID")
            call_ids.add(receipt["call_id"])
            sequences[parts[5]].add(receipt["sequence"])
            entries.append({"path": relative, "sha256": digest})
        for order_sequences in sequences.values():
            if sorted(order_sequences) != list(
                range(1, len(order_sequences) + 1)
            ):
                raise StateNotDurableError("CALL_ARCHIVE_INVALID")
        entries.sort(key=lambda item: item["path"])
        return {
            "count": len(entries),
            "root_sha256": hashlib.sha256(
                contract.canonical_json_bytes(entries)
            ).hexdigest(),
        }
    def _snapshot_reference_path(
        self, relative: str, *, create_parents: bool = False
    ) -> Path:
        if not isinstance(relative, str) or "\\" in relative:
            raise SnapshotExportError("SNAPSHOT_SHARD_PATH_INVALID")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != relative:
            raise SnapshotExportError("SNAPSHOT_SHARD_PATH_INVALID")
        if not (
            re.fullmatch(
                r"\.devad/manager/loop-lite/snapshots/generations/[0-9]+/shards/[0-9a-f]{64}\.json",
                relative,
            )
            or re.fullmatch(
                r"\.devad/manager/loop-lite/snapshots/roots/[0-9a-f]{64}\.json",
                relative,
            )
        ):
            raise SnapshotExportError("SNAPSHOT_SHARD_PATH_INVALID")
        return self._safe_state_path(
            self.repo / Path(*pure.parts), create_parents=create_parents
        )

    def _read_snapshot_reference(self, relative: str) -> bytes:
        path = self._snapshot_reference_path(relative)
        if not path.is_file():
            raise SnapshotExportError("SNAPSHOT_SHARD_EXTRA_OR_MISSING")
        return path.read_bytes()

    def _list_generation_shards(self, generation: int) -> set[str]:
        if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
            raise SnapshotExportError("SNAPSHOT_INVALID")
        relative = (
            ".devad/manager/loop-lite/snapshots/generations/"
            f"{generation}/shards"
        )
        root = self.repo / Path(*PurePosixPath(relative).parts)
        self._safe_state_path(root, directory=True)
        if not root.exists():
            return set()
        if not root.is_dir() or self._is_reparse(root):
            raise SnapshotExportError("SNAPSHOT_SHARD_PATH_INVALID")
        paths: set[str] = set()
        for item in root.rglob("*"):
            self._safe_state_path(item, directory=item.is_dir())
            if item.is_dir():
                if self._is_reparse(item):
                    raise SnapshotExportError("SNAPSHOT_SHARD_PATH_INVALID")
                continue
            if not item.is_file():
                raise SnapshotExportError("SNAPSHOT_SHARD_PATH_INVALID")
            paths.add(item.relative_to(self.repo).as_posix())
        return paths

    def _snapshot_tables(
        self,
        connection: sqlite3.Connection,
        table_names: tuple[str, ...] = SNAPSHOT_TABLES,
    ) -> dict[str, list[dict[str, Any]]]:
        tables = {table: self._rows(connection, table) for table in table_names}
        tables["dispatches"] = [
            dict(row)
            for row in connection.execute("SELECT * FROM dispatches ORDER BY rowid")
        ]
        return tables

    def _snapshot_dispatch_attempts(
        self, connection: sqlite3.Connection
    ) -> dict[str, int]:
        attempts: dict[str, int] = {}
        for row in connection.execute(
            "SELECT o.dispatch_id,o.payload FROM outbox o "
            "JOIN dispatches d ON d.dispatch_id=o.dispatch_id "
            "JOIN tasks t ON t.task_id=d.task_id "
            "WHERE d.status='PREPARED' AND t.status NOT IN ('COMPLETE','SUPERSEDED') "
            "ORDER BY o.dispatch_id"
        ):
            try:
                attempts[row["dispatch_id"]] = int(
                    json.loads(row["payload"]).get("attempt", 1)
                )
            except (TypeError, ValueError, json.JSONDecodeError):
                attempts[row["dispatch_id"]] = 1
        return attempts

    def _snapshot_bundle(
        self,
        connection: sqlite3.Connection,
        *,
        current_snapshot_raw: bytes | None = None,
        generation: int | None = None,
        call_receipt_archive: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        capacity = _load_snapshot_capacity()
        if current_snapshot_raw is None and self.snapshot_path.is_file():
            self._safe_state_path(self.snapshot_path)
            current_snapshot_raw = self.snapshot_path.read_bytes()
        try:
            return capacity.build_bundle(
                generation=(
                    self._generation(connection)
                    if generation is None
                    else generation
                ),
                columns=SNAPSHOT_COLUMNS,
                tables=self._snapshot_tables(connection),
                recovery_worktrees=[
                    dict(row)
                    for row in connection.execute(
                        "SELECT worktree_id,path FROM worktrees ORDER BY worktree_id"
                    )
                ],
                completed_task_ids=self._completed_task_ids(connection),
                dispatch_attempts=self._snapshot_dispatch_attempts(connection),
                call_receipt_archive=(
                    self._call_receipt_archive()
                    if call_receipt_archive is None
                    else call_receipt_archive
                ),
                current_snapshot_raw=current_snapshot_raw,
            )
        except capacity.SnapshotCapacityError as exc:
            raise SnapshotExportError(str(exc)) from exc

    def _decode_v2_snapshot(
        self, snapshot: Mapping[str, Any], raw: bytes
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        expected = {
            "call_receipt_archive",
            "completed_task_ids",
            "dispatch_attempts",
            "generation",
            "recovery_worktrees",
            "schema",
            "tables",
        }
        if (
            len(raw) > 8192
            or set(snapshot) != expected
            or snapshot.get("schema") != SCHEMA_V2
            or isinstance(snapshot.get("generation"), bool)
            or not isinstance(snapshot.get("generation"), int)
            or contract.canonical_json_bytes(dict(snapshot)) != raw
        ):
            raise SnapshotExportError("SNAPSHOT_INVALID")
        completed = snapshot["completed_task_ids"]
        attempts = snapshot["dispatch_attempts"]
        archive = snapshot["call_receipt_archive"]
        recovery = snapshot["recovery_worktrees"]
        tables = snapshot["tables"]
        if (
            not isinstance(completed, list)
            or len(completed) > COMPLETED_TASK_ID_CAP
            or len(set(completed)) != len(completed)
            or not all(isinstance(item, str) and item for item in completed)
            or not isinstance(attempts, dict)
            or not all(
                isinstance(key, str)
                and isinstance(value, int)
                and not isinstance(value, bool)
                and value >= 1
                for key, value in attempts.items()
            )
            or not isinstance(archive, dict)
            or set(archive) != {"count", "root_sha256"}
            or isinstance(archive.get("count"), bool)
            or not isinstance(archive.get("count"), int)
            or archive["count"] < 0
            or re.fullmatch(r"[0-9a-f]{64}", str(archive.get("root_sha256")))
            is None
            or not isinstance(recovery, list)
            or any(
                not isinstance(row, dict)
                or set(row) != {"worktree_id", "path"}
                or not all(isinstance(row[key], str) and row[key] for key in row)
                for row in recovery
            )
            or len({row["worktree_id"] for row in recovery}) != len(recovery)
            or not isinstance(tables, dict)
            or set(tables) != set(V2_SNAPSHOT_TABLES)
        ):
            raise SnapshotExportError("SNAPSHOT_INVALID")
        for table, rows in tables.items():
            if not isinstance(rows, list):
                raise SnapshotExportError("SNAPSHOT_TABLE_INVALID")
            columns = set(V2_SNAPSHOT_COLUMNS[table])
            if any(not isinstance(row, dict) or set(row) != columns for row in rows):
                raise SnapshotExportError("SNAPSHOT_COLUMN_UNKNOWN")
        upgraded_tables = {table: list(rows) for table, rows in tables.items()}
        upgraded_tables["inbox"] = []
        return {
            "call_receipt_archive": archive,
            "completed_task_ids": completed,
            "dispatch_attempts": attempts,
            "generation": snapshot["generation"],
            "recovery_worktrees": recovery,
            "tables": upgraded_tables,
        }

    def _decode_snapshot(self, raw: bytes) -> dict[str, Any]:
        try:
            snapshot = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SnapshotExportError("SNAPSHOT_INVALID") from exc
        schema = snapshot.get("schema") if isinstance(snapshot, dict) else None
        if schema == SCHEMA_V2:
            return self._decode_v2_snapshot(snapshot, raw)
        if schema != SCHEMA:
            raise SnapshotExportError("SNAPSHOT_INVALID")
        capacity = _load_snapshot_capacity()
        try:
            old_table_schema = capacity.table_schema_sha256(
                V2_SNAPSHOT_COLUMNS
            )
            columns = (
                V2_SNAPSHOT_COLUMNS
                if snapshot.get("table_schema_sha256") == old_table_schema
                else SNAPSHOT_COLUMNS
            )
            state = capacity.decode_v3(
                snapshot=snapshot,
                snapshot_raw=raw,
                columns=columns,
                read_reference=self._read_snapshot_reference,
                list_generation_shards=self._list_generation_shards,
            )
            if columns is V2_SNAPSHOT_COLUMNS:
                state["tables"] = {
                    **state["tables"],
                    "inbox": [],
                }
            return state
        except capacity.SnapshotCapacityError as exc:
            raise SnapshotExportError(str(exc)) from exc

    def _snapshot_matches_connection(
        self, connection: sqlite3.Connection, raw: bytes | None = None
    ) -> bool:
        try:
            if raw is None:
                self._safe_state_path(self.snapshot_path)
                raw = self.snapshot_path.read_bytes()
            state = self._decode_snapshot(raw)
            user_version = connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0]
            if user_version == 2:
                tables = {
                    table: state["tables"][table]
                    for table in V2_SNAPSHOT_TABLES
                }
                return (
                    state["generation"] == self._generation(connection)
                    and state["call_receipt_archive"]
                    == self._call_receipt_archive()
                    and tables
                    == self._snapshot_tables(connection, V2_SNAPSHOT_TABLES)
                    and state["completed_task_ids"]
                    == self._completed_task_ids(connection)
                    and state["dispatch_attempts"]
                    == self._snapshot_dispatch_attempts(connection)
                    and state["recovery_worktrees"]
                    == [
                        dict(row)
                        for row in connection.execute(
                            "SELECT worktree_id,path FROM worktrees ORDER BY worktree_id"
                        )
                    ]
                )
            if (
                state["generation"] != self._generation(connection)
                or state["call_receipt_archive"] != self._call_receipt_archive()
            ):
                return False
            schema = json.loads(raw).get("schema")
            if schema == SCHEMA_V2:
                expected = _load_v7_contract().canonical_json_bytes(
                    self._snapshot_v2_data(connection)
                )
            else:
                expected = self._snapshot_bundle(
                    connection, current_snapshot_raw=raw
                )["root_raw"]
            return expected == raw
        except (
            LoopError,
            OSError,
            UnicodeDecodeError,
            ValueError,
            json.JSONDecodeError,
        ):
            return False

    def _write_immutable_snapshot_reference(
        self, relative: str, data: bytes
    ) -> None:
        target = self._snapshot_reference_path(relative, create_parents=True)
        if os.path.lexists(target):
            self._safe_state_path(target)
            if not target.is_file() or target.read_bytes() != data:
                raise SnapshotExportError("SNAPSHOT_IMMUTABLE_REF_MISMATCH")
            return
        staging = self.root / "snapshots" / "staging"
        self._safe_state_path(
            staging, create_parents=True, directory=True
        )
        temporary = staging / f"{uuid.uuid4().hex}.tmp"
        self._safe_state_path(temporary, create_parents=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= int(getattr(os, "O_NOFOLLOW", 0) or 0)
        descriptor = os.open(temporary, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, target, follow_symlinks=False)
            except FileExistsError:
                self._safe_state_path(target)
                if not target.is_file() or target.read_bytes() != data:
                    raise SnapshotExportError(
                        "SNAPSHOT_IMMUTABLE_REF_MISMATCH"
                    )
            self._safe_state_path(target)
            if target.read_bytes() != data:
                raise SnapshotExportError("SNAPSHOT_IMMUTABLE_REF_MISMATCH")
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if os.path.lexists(temporary):
                temporary.unlink()

    def _validate_bundle_targets(self, bundle: Mapping[str, Any]) -> None:
        expected_paths = {
            item["reference"]["path"] for item in bundle["shards"]
        }
        generation = bundle["root"]["generation"]
        existing_paths = self._list_generation_shards(generation)
        if not existing_paths.issubset(expected_paths):
            raise SnapshotExportError("SNAPSHOT_SHARD_EXTRA_OR_MISSING")
        entries = [
            (item["reference"]["path"], item["raw"])
            for item in bundle["shards"]
        ]
        if bundle["previous_archive"] is not None:
            entries.append(bundle["previous_archive"])
        for relative, data in entries:
            target = self._snapshot_reference_path(relative)
            if os.path.lexists(target):
                self._safe_state_path(target)
                if not target.is_file() or target.read_bytes() != data:
                    raise SnapshotExportError(
                        "SNAPSHOT_IMMUTABLE_REF_MISMATCH"
                    )

    def _write_snapshot_bundle(
        self, bundle: Mapping[str, Any], *, write_root: bool = True
    ) -> None:
        self._validate_bundle_targets(bundle)
        for item in bundle["shards"]:
            self._write_immutable_snapshot_reference(
                item["reference"]["path"], item["raw"]
            )
        if bundle["previous_archive"] is not None:
            self._write_immutable_snapshot_reference(*bundle["previous_archive"])
        if self._list_generation_shards(bundle["root"]["generation"]) != {
            item["reference"]["path"] for item in bundle["shards"]
        }:
            raise SnapshotExportError("SNAPSHOT_SHARD_EXTRA_OR_MISSING")
        if write_root:
            self._atomic_state_write(self.snapshot_path, bundle["root_raw"])
    def _snapshot_v2_data(self, connection: sqlite3.Connection | None = None) -> dict[str, Any]:
        owns_connection = connection is None
        connection = connection or self._connect()
        try:
            if owns_connection:
                self._schema(connection)
            active_tasks = [dict(row) for row in connection.execute("SELECT * FROM tasks WHERE status NOT IN ('COMPLETE','SUPERSEDED') ORDER BY task_id")]
            active_ids = [row["task_id"] for row in active_tasks]
            active_dispatches = [
                dict(row)
                for row in connection.execute(
                    "SELECT d.* FROM dispatches d JOIN tasks t ON t.task_id=d.task_id "
                    "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') AND (d.status IN ('PREPARED','DISPATCHED') "
                    "OR (t.status='THINX_REVIEW_REQUIRED' AND d.rowid=("
                    "SELECT MAX(d2.rowid) FROM dispatches d2 WHERE d2.task_id=d.task_id))) "
                    "ORDER BY d.dispatch_id"
                )
            ]
            actor_ids = {row["worker_id"] for row in active_tasks}
            actor_ids.update(row[0] for row in connection.execute("SELECT actor_id FROM actors WHERE role IN ('LINX','THINX')"))
            actor_ids.update(row["sender_id"] for row in active_dispatches)
            actor_ids.update(row["target_id"] for row in active_dispatches)
            worktree_ids = {row["worktree_id"] for row in active_tasks}
            def selected(table: str, column: str, values: set[str]) -> list[dict[str, Any]]:
                if not values:
                    return []
                placeholders = ",".join("?" for _ in values)
                return [dict(row) for row in connection.execute(f"SELECT * FROM {table} WHERE {column} IN ({placeholders}) ORDER BY 1", tuple(sorted(values)))]
            active_dispatch_ids = {row["dispatch_id"] for row in active_dispatches}
            prepared_ids = {row["dispatch_id"] for row in active_dispatches if row["status"] == "PREPARED"}
            dispatch_attempts = {}
            for row in selected("outbox", "dispatch_id", prepared_ids):
                try:
                    dispatch_attempts[row["dispatch_id"]] = int(json.loads(row["payload"]).get("attempt", 1))
                except (TypeError, ValueError, json.JSONDecodeError):
                    dispatch_attempts[row["dispatch_id"]] = 1
            referenced_complete: list[str] = []
            for task in active_tasks:
                for dependency in json.loads(task["dependencies"]):
                    row = connection.execute("SELECT status FROM tasks WHERE task_id=?", (dependency,)).fetchone()
                    if row and row[0] == "COMPLETE" and dependency not in referenced_complete:
                        referenced_complete.append(dependency)
            if len(referenced_complete) > COMPLETED_TASK_ID_CAP:
                raise SnapshotExportError("COMPLETED_DEPENDENCY_CAP")
            recent_complete = [row[0] for row in connection.execute("SELECT task_id FROM tasks WHERE status='COMPLETE' ORDER BY rowid DESC LIMIT ?", (COMPLETED_TASK_ID_CAP,))]
            completed_task_ids: list[str] = []
            for item in [*referenced_complete, *recent_complete, *self._completed_task_ids(connection)]:
                if item not in completed_task_ids:
                    completed_task_ids.append(item)
            completed_task_ids = completed_task_ids[:COMPLETED_TASK_ID_CAP]
            recovery_worktrees = [dict(row) for row in connection.execute("SELECT worktree_id,path FROM worktrees ORDER BY worktree_id")]
            classifications = [dict(row) for row in connection.execute("SELECT * FROM worktree_classifications ORDER BY worktree_id")]
            worktree_ids.update(row["worktree_id"] for row in classifications)
            programs = [dict(row) for row in connection.execute("SELECT * FROM programs WHERE status='ACTIVE' ORDER BY program_id")]
            work_orders = [
                dict(row) for row in connection.execute(
                    "SELECT * FROM work_orders WHERE status NOT IN ('COMPLETE','EXPIRED','SUPERSEDED') ORDER BY work_order_id"
                )
            ]
            active_order_ids = {row["work_order_id"] for row in work_orders}
            active_metric_keys = {f"blocked:{task_id}" for task_id in active_ids}
            active_metric_keys.update(f"task-contract:{task_id}" for task_id in active_ids)
            for work_order_id in active_order_ids:
                active_metric_keys.update(
                    f"{prefix}:{work_order_id}"
                    for prefix in (
                        "call-count", "call-latest", "call-root",
                        "call-tokens", "call-unknown",
                    )
                )
            empty_receipt_root = _sha([])
            def is_recoverable_default_metric(row: sqlite3.Row) -> bool:
                key, value = row["key"], row["value"]
                return (
                    (key.startswith("historical-receipts:") and value == "{}")
                    or (key.startswith("receipt-count:") and value == "0")
                    or (
                        key.startswith("receipt-root:")
                        and value == empty_receipt_root
                    )
                )
            metrics = [
                dict(row) for row in connection.execute("SELECT * FROM metrics WHERE key != 'completed_task_ids' ORDER BY key")
                if (
                    not row["key"].startswith(("blocked:", "task-contract:", "call-"))
                    or row["key"] in active_metric_keys
                )
                and not is_recoverable_default_metric(row)
            ]
            call_reservations = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM call_reservations WHERE status='RESERVED' "
                    "ORDER BY call_id"
                )
                if row["work_order_id"] in active_order_ids
            ]
            return {
                "schema": SCHEMA_V2, "generation": self._generation(connection), "recovery_worktrees": recovery_worktrees,
                "dispatch_attempts": dispatch_attempts,
                "completed_task_ids": completed_task_ids,
                "call_receipt_archive": self._call_receipt_archive(),
                "tables": {
                    "actors": selected("actors", "actor_id", actor_ids), "worktrees": selected("worktrees", "worktree_id", worktree_ids),
                    "tasks": active_tasks, "claims": selected("claims", "task_id", set(active_ids)),
                    "resources": selected("resources", "task_id", set(active_ids)), "dispatches": active_dispatches,
                    "deliveries": selected("deliveries", "dispatch_id", active_dispatch_ids), "events": [],
                    "gates": selected("gates", "task_id", set(active_ids)),
                    "outbox": [], "metrics": metrics,
                    "programs": programs, "work_orders": work_orders,
                    "worktree_classifications": classifications,
                    "call_reservations": call_reservations,
                },
            }
        finally:
            if owns_connection:
                connection.close()
    def _snapshot_data(
        self, connection: sqlite3.Connection | None = None
    ) -> dict[str, Any]:
        owns_connection = connection is None
        connection = connection or self._connect()
        try:
            if owns_connection:
                self._schema(connection)
            return self._snapshot_bundle(connection)["root"]
        finally:
            if owns_connection:
                connection.close()
    def _snapshot_v1_data(self, connection: sqlite3.Connection) -> dict[str, Any]:
        active_tasks = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM tasks WHERE status NOT IN ('COMPLETE','SUPERSEDED') ORDER BY task_id"
            )
        ]
        active_ids = [row["task_id"] for row in active_tasks]
        active_dispatches = [
            dict(row)
            for row in connection.execute(
                "SELECT d.* FROM dispatches d JOIN tasks t ON t.task_id=d.task_id "
                "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') AND (d.status IN ('PREPARED','DISPATCHED') "
                "OR (t.status='THINX_REVIEW_REQUIRED' AND d.rowid=("
                "SELECT MAX(d2.rowid) FROM dispatches d2 WHERE d2.task_id=d.task_id))) "
                "ORDER BY d.dispatch_id"
            )
        ]
        actor_ids = {row["worker_id"] for row in active_tasks}
        actor_ids.update(
            row[0]
            for row in connection.execute(
                "SELECT actor_id FROM actors WHERE role IN ('LINX','THINX')"
            )
        )
        actor_ids.update(row["sender_id"] for row in active_dispatches)
        actor_ids.update(row["target_id"] for row in active_dispatches)
        worktree_ids = {row["worktree_id"] for row in active_tasks}

        def selected(table: str, column: str, values: set[str]) -> list[dict[str, Any]]:
            if not values:
                return []
            placeholders = ",".join("?" for _ in values)
            return [
                dict(row)
                for row in connection.execute(
                    f"SELECT * FROM {table} WHERE {column} IN ({placeholders}) ORDER BY 1",
                    tuple(sorted(values)),
                )
            ]

        active_dispatch_ids = {row["dispatch_id"] for row in active_dispatches}
        prepared_ids = {
            row["dispatch_id"] for row in active_dispatches if row["status"] == "PREPARED"
        }
        dispatch_attempts = {}
        for row in selected("outbox", "dispatch_id", prepared_ids):
            try:
                dispatch_attempts[row["dispatch_id"]] = int(
                    json.loads(row["payload"]).get("attempt", 1)
                )
            except (TypeError, ValueError, json.JSONDecodeError):
                dispatch_attempts[row["dispatch_id"]] = 1
        referenced_complete: list[str] = []
        for task in active_tasks:
            for dependency in json.loads(task["dependencies"]):
                row = connection.execute(
                    "SELECT status FROM tasks WHERE task_id=?", (dependency,)
                ).fetchone()
                if row and row[0] == "COMPLETE" and dependency not in referenced_complete:
                    referenced_complete.append(dependency)
        if len(referenced_complete) > COMPLETED_TASK_ID_CAP:
            raise StateNotDurableError("V6_SNAPSHOT_INVALID")
        recent_complete = [
            row[0]
            for row in connection.execute(
                "SELECT task_id FROM tasks WHERE status='COMPLETE' "
                "ORDER BY rowid DESC LIMIT ?",
                (COMPLETED_TASK_ID_CAP,),
            )
        ]
        completed_task_ids: list[str] = []
        for item in [
            *referenced_complete,
            *recent_complete,
            *self._completed_task_ids(connection),
        ]:
            if item not in completed_task_ids:
                completed_task_ids.append(item)
        completed_task_ids = completed_task_ids[:COMPLETED_TASK_ID_CAP]
        recovery_worktrees = [
            dict(row)
            for row in connection.execute(
                "SELECT worktree_id,path FROM worktrees ORDER BY worktree_id"
            )
        ]
        active_metric_keys = {f"blocked:{task_id}" for task_id in active_ids}
        metrics = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM metrics WHERE key != 'completed_task_ids' ORDER BY key"
            )
            if not row["key"].startswith("blocked:")
            or row["key"] in active_metric_keys
        ]
        return {
            "schema": SCHEMA_V1,
            "generation": self._generation(connection),
            "recovery_worktrees": recovery_worktrees,
            "dispatch_attempts": dispatch_attempts,
            "completed_task_ids": completed_task_ids,
            "tables": {
                "actors": selected("actors", "actor_id", actor_ids),
                "worktrees": selected("worktrees", "worktree_id", worktree_ids),
                "tasks": active_tasks,
                "claims": selected("claims", "task_id", set(active_ids)),
                "resources": selected("resources", "task_id", set(active_ids)),
                "dispatches": active_dispatches,
                "deliveries": selected(
                    "deliveries", "dispatch_id", active_dispatch_ids
                ),
                "events": [],
                "gates": selected("gates", "task_id", set(active_ids)),
                "outbox": [],
                "metrics": metrics,
            },
        }

    @staticmethod
    def _is_v6_status_only_handover_receipt(
        receipt: Mapping[str, Any], parts: tuple[str, ...], stem: str
    ) -> bool:
        if receipt.get("schema") != "x9-v6-status-only-handover-receipt-v1":
            return False
        worker = receipt.get("worker")
        if isinstance(worker, Mapping):
            actor = worker.get("thread_actor_id")
            role = worker.get("real_role")
        else:
            actor = receipt.get("worker_thread_actor_id")
            role = receipt.get("real_role")
        return (
            len(parts) == 5
            and parts[0:2] == (".devad", "workers")
            and parts[3] == "receipts"
            and parts[2] == actor
            and stem == receipt.get("status_request_id")
            and receipt.get("mode") == "STATUS_ONLY_HANDOVER"
            and role == "WORKER"
        )

    @staticmethod
    def _historical_receipt_metric_key(worktree_path: str | Path) -> str:
        canonical = (
            str(Path(worktree_path).resolve())
            .replace("\\", "/")
            .casefold()
        )
        scope = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
        return f"historical-receipts:{scope}"

    def _observed_historical_receipt_entries(
        self, worktree_root: Path
    ) -> dict[str, str]:
        try:
            resolved_root = worktree_root.resolve(strict=True)
            receipts = resolved_root / ".devad" / "workers"
            entries: dict[str, str] = {}
            for candidate in (
                receipts.glob("*/receipts/*.json")
                if receipts.is_dir()
                else ()
            ):
                resolved = self._resolve_under(resolved_root, candidate)
                relative = self._normal_path(
                    resolved.relative_to(resolved_root).as_posix()
                )
                data = resolved.read_bytes()
                receipt = json.loads(data.decode("utf-8"))
                if receipt.get("schema") != "x9-v6-status-only-handover-receipt-v1":
                    continue
                if not self._is_v6_status_only_handover_receipt(
                    receipt, PurePosixPath(relative).parts, resolved.stem
                ):
                    raise ValueError("historical receipt shape")
                entries[relative] = hashlib.sha256(data).hexdigest()
            return entries
        except (
            OSError,
            UnicodeDecodeError,
            ValueError,
            RuntimeError,
            json.JSONDecodeError,
            ScopeBreachError,
            AttributeError,
        ) as exc:
            raise StateNotDurableError("RECEIPT_SET_MISMATCH") from exc

    def _capture_historical_receipts(
        self, connection: sqlite3.Connection, worktree_root: Path
    ) -> None:
        if not worktree_root.is_dir():
            return
        entries = self._observed_historical_receipt_entries(worktree_root)
        key = self._historical_receipt_metric_key(worktree_root)
        value = _json(entries)
        existing = connection.execute(
            "SELECT value FROM metrics WHERE key=?", (key,)
        ).fetchone()
        if existing and existing[0] != value:
            raise StateNotDurableError("RECEIPT_SET_MISMATCH")
        connection.execute(
            "INSERT OR IGNORE INTO metrics(key,value) VALUES(?,?)",
            (key, value),
        )

    def _historical_receipt_paths(
        self,
        worktree_root: Path,
        connection: sqlite3.Connection | None = None,
    ) -> set[str]:
        owns_connection = connection is None
        connection = connection or self._connect()
        try:
            key = self._historical_receipt_metric_key(worktree_root)
            row = connection.execute(
                "SELECT value FROM metrics WHERE key=?", (key,)
            ).fetchone()
            raw = row[0] if row else "{}"
            approved = json.loads(raw)
            if (
                not isinstance(approved, dict)
                or _json(approved) != raw
                or any(
                    not isinstance(path, str)
                    or self._normal_path(path) != path
                    or not isinstance(digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                    for path, digest in approved.items()
                )
            ):
                raise StateNotDurableError("RECEIPT_SET_MISMATCH")
            observed = self._observed_historical_receipt_entries(worktree_root)
            if observed != approved:
                raise StateNotDurableError("RECEIPT_SET_MISMATCH")
            return set(approved)
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
            ScopeBreachError,
        ) as exc:
            raise StateNotDurableError("RECEIPT_SET_MISMATCH") from exc
        finally:
            if owns_connection:
                connection.close()

    def _recovery_evidence(self, worktrees: list[dict[str, str]], strict: bool) -> dict[str, Any]:
        evidence: dict[str, Any] = {"worktrees": 0, "receipts": 0, "git_paths": 0, "receipt_sha256": "", "issues": []}
        receipt_hashes: list[str] = []
        for row in worktrees:
            root = Path(row["path"])
            if not root.is_dir():
                if strict:
                    raise SnapshotExportError("RECOVERY_WORKTREE_MISSING")
                evidence["issues"].append(f"WORKTREE_MISSING:{row['worktree_id']}")
                continue
            evidence["worktrees"] += 1
            receipts = root / ".devad" / "workers"
            if receipts.is_dir():
                for receipt_path in receipts.glob("*/receipts/*.json"):
                    try:
                        resolved_receipt = self._resolve_under(root, receipt_path)
                        data = resolved_receipt.read_bytes()
                        receipt = json.loads(data.decode("utf-8"))
                        relative = self._normal_path(resolved_receipt.relative_to(root.resolve()).as_posix())
                        parts = PurePosixPath(relative).parts
                        if self._is_v6_status_only_handover_receipt(receipt, parts, resolved_receipt.stem):
                            continue
                        if (len(parts) != 5 or parts[0:2] != (".devad", "workers")
                                or parts[3] != "receipts" or resolved_receipt.stem != receipt.get("event_id")
                                or receipt.get("schema") not in {"x9-loop-lite-result-v1", "x9-loop-lite-thinx-decision-v1", "x9-loop-result-v2", "x9-loop-thinx-decision-v2"}):
                            raise ValueError("receipt shape")
                        receipt_hashes.append(hashlib.sha256(data).hexdigest())
                        evidence["receipts"] += 1
                    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, ScopeBreachError, AttributeError):
                        if strict:
                            raise SnapshotExportError("RECOVERY_RECEIPT_INVALID")
                        evidence["issues"].append(f"RECEIPT_INVALID:{receipt_path}")
            try:
                for arguments in (["diff", "--cached", "--name-only"], ["diff", "--name-only"], ["ls-files", "--others", "--exclude-standard"]):
                    evidence["git_paths"] += len(self._git_paths(arguments, root))
            except GitStateError:
                if strict:
                    raise SnapshotExportError("RECOVERY_GIT_STATE_UNKNOWN")
                evidence["issues"].append(f"GIT_STATE_UNKNOWN:{row['worktree_id']}")
        evidence["receipt_sha256"] = _sha(sorted(receipt_hashes))
        return evidence
    def _write_snapshot(self) -> None:
        connection = self._connect()
        bundle: dict[str, Any] | None = None
        try:
            self._schema(connection)
            current_raw = (
                self.snapshot_path.read_bytes()
                if self.snapshot_path.is_file()
                else None
            )
            if current_raw is not None:
                try:
                    current_schema = json.loads(current_raw).get("schema")
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise StateNotDurableError("SNAPSHOT_STALE") from exc
                if not self._snapshot_matches_connection(connection, current_raw):
                    raise StateNotDurableError("SNAPSHOT_STALE")
            else:
                current_schema = None
            if current_schema == SCHEMA_V2:
                connection.execute("BEGIN IMMEDIATE")
                generation = self._generation(connection) + 1
                connection.execute(
                    "UPDATE meta SET value=? WHERE key='generation'",
                    (str(generation),),
                )
                bundle = self._snapshot_bundle(
                    connection,
                    current_snapshot_raw=current_raw,
                    generation=generation,
                )
                self._validate_bundle_targets(bundle)
                connection.commit()
            else:
                bundle = self._snapshot_bundle(
                    connection, current_snapshot_raw=current_raw
                )
                self._validate_bundle_targets(bundle)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        if bundle is None:
            raise SnapshotExportError("SNAPSHOT_EXPORT_FAILED")
        self._write_snapshot_bundle(bundle)
    def _controller_snapshot_evidence(
        self, worktree_root: Path, connection: sqlite3.Connection | None = None
    ) -> set[str]:
        try:
            if worktree_root.resolve(strict=True) != self.repo:
                return set()
        except (OSError, RuntimeError):
            return set()
        self._safe_state_path(self.snapshot_path)
        if not self.snapshot_path.is_file():
            return set()
        owns_connection = connection is None
        connection = connection or self._connect()
        try:
            if owns_connection:
                self._schema(connection)
            if not self._snapshot_matches_connection(connection):
                return set()
        finally:
            if owns_connection:
                connection.close()
        return {
            self._normal_path(self.snapshot_path.relative_to(self.repo).as_posix())
        }
    def _controller_snapshot_tamper(self, worktree_root: Path) -> set[str]:
        try:
            same_repo = worktree_root.resolve(strict=True) == self.repo
        except (OSError, RuntimeError):
            return set()
        if not same_repo or not os.path.lexists(self.snapshot_path):
            return set()
        relative = self._normal_path(self.snapshot_path.relative_to(self.repo).as_posix())
        return set() if self._controller_snapshot_evidence(worktree_root) else {relative}

    def _assert_durable(self) -> None:
        self._safe_state_path(self.snapshot_path)
        if not self.snapshot_path.is_file():
            raise StateNotDurableError("SNAPSHOT_STALE")
        connection = self._connect()
        try:
            self._schema(connection)
            if not self._snapshot_matches_connection(connection):
                raise StateNotDurableError("SNAPSHOT_STALE")
        finally:
            connection.close()
    def _ensure_approved_jobs(self) -> None:
        contract = _load_v7_contract()
        empty = {
            "jobs": [],
            "monitor_mode": "DISABLED",
            "schema": "x9-loop-approved-jobs-v1",
        }
        if not self.approved_jobs_path.exists():
            self._atomic_state_write(
                self.approved_jobs_path, contract.canonical_json_bytes(empty)
            )
            return
        try:
            raw = self.approved_jobs_path.read_bytes()
            value = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("APPROVED_JOBS_INVALID") from exc
        if (
            not isinstance(value, dict)
            or set(value) not in (
                {"jobs", "schema"},
                {"jobs", "monitor_mode", "schema"},
                {"jobs", "monitor_mode", "project_profile_id", "schema"},
            )
            or contract.canonical_json_bytes(value) != raw
        ):
            raise StateNotDurableError("APPROVED_JOBS_NONCANONICAL")
        try:
            providers = {
                row["provider"]: "AVAILABLE"
                for row in value["jobs"]
                if isinstance(row, Mapping) and isinstance(row.get("provider"), str)
            }
            contract.compare_scheduled_jobs(
                value,
                [],
                providers,
                project_profile_id=value.get("project_profile_id"),
            )
        except (KeyError, TypeError, contract.ContractError) as exc:
            raise StateNotDurableError("APPROVED_JOBS_INVALID") from exc

    def init(self, import_v5: bool = False) -> dict[str, Any]:
        self.recover_interrupted_migration()
        self._safe_state_path(self.root, create_parents=True, directory=True)
        self._safe_state_path(self.action_path, create_parents=True)
        self._ensure_approved_jobs()
        connection = self._connect()
        try:
            self._schema(connection)
            self._ensure_project_profile(connection)
        finally:
            connection.close()
        imported = {"actors": 0, "worktrees": 0, "tasks": 0, "claims": 0, "gates": 0}
        skipped = 0
        if import_v5:
            legacy = self.repo / ".devad" / "manager" / "loop"
            def load(name: str) -> dict[str, Any]:
                try:
                    value = json.loads((legacy / name).read_text(encoding="utf-8"))
                    return value if isinstance(value, dict) else {}
                except (OSError, json.JSONDecodeError):
                    return {}
            registry = load("ROLE_REGISTRY.json").get("tasks", {})
            worktrees = load("WORKTREE_INDEX.json").get("worktrees", {})
            graph = load("TASK_GRAPH.json").get("tasks", {})
            claims = load("RESOURCE_CLAIMS.json").get("tasks", {})
            gates = load("DECISION_GATES.json").get("tasks", {})
            def migrate(connection: sqlite3.Connection) -> dict[str, Any]:
                nonlocal skipped
                for actor_id, row in registry.items() if isinstance(registry, dict) else ():
                    role = row.get("role") if isinstance(row, dict) else None
                    if not isinstance(role, str) or role.upper() not in {"LINX", "THINX", "WORKER", "READER", "CHUNK", "SIDE"}:
                        skipped += 1
                        continue
                    cursor = connection.execute("INSERT OR IGNORE INTO actors(actor_id,role,title,model) VALUES(?,?,?,?)", (actor_id, role.upper(), str(row.get("title", "")), str(row.get("model", "Unknown"))))
                    imported["actors"] += cursor.rowcount
                for worktree_id, row in worktrees.items() if isinstance(worktrees, dict) else ():
                    if not isinstance(row, dict) or not row.get("path") or not row.get("repository_id"):
                        skipped += 1
                        continue
                    normalized_worktree = str(Path(row["path"]).resolve())
                    cursor = connection.execute("INSERT OR IGNORE INTO worktrees(worktree_id,path,repository_id) VALUES(?,?,?)", (worktree_id, normalized_worktree, str(row["repository_id"])))
                    imported["worktrees"] += cursor.rowcount
                    count_key, root_key = self._receipt_metric_keys(normalized_worktree)
                    connection.execute("INSERT OR IGNORE INTO metrics(key,value) VALUES(?,'0')", (count_key,))
                    connection.execute("INSERT OR IGNORE INTO metrics(key,value) VALUES(?,?)", (root_key, _sha([])))
                for task_id, row in graph.items() if isinstance(graph, dict) else ():
                    if not isinstance(row, dict):
                        skipped += 1
                        continue
                    worker_id, worktree_id, base_sha = row.get("worker_id"), row.get("worktree_id"), row.get("base_sha")
                    actor = connection.execute("SELECT role FROM actors WHERE actor_id=?", (worker_id,)).fetchone()
                    worktree = connection.execute("SELECT 1 FROM worktrees WHERE worktree_id=?", (worktree_id,)).fetchone()
                    if not isinstance(base_sha, str) or not actor or actor[0] != "WORKER" or not worktree:
                        skipped += 1
                        continue
                    cursor = connection.execute("INSERT OR IGNORE INTO tasks(task_id,worker_id,worktree_id,base_sha,owner_packet_path,owner_packet_sha256,dependencies,finish_line,status) VALUES(?,?,?,?,?,?,?,?,?)", (task_id, worker_id, worktree_id, base_sha, "", "", _json(row.get("dependencies", [])), str(row.get("finish_line", "")), "REGISTERED"))
                    if not cursor.rowcount:
                        continue
                    imported["tasks"] += 1
                    connection.execute("INSERT OR REPLACE INTO gates(task_id,name,status,note) VALUES(?,?,?,?)", (task_id, "OWNER_PACKET_MISSING", "BLOCKED", "legacy task requires owner packet"))
                    claim_row = claims.get(task_id, {}) if isinstance(claims, dict) else {}
                    for item in claim_row.get("claims", []) if isinstance(claim_row, dict) else []:
                        try:
                            connection.execute("INSERT INTO claims(task_id,path,kind) VALUES(?,?,?)", (task_id, self._normal_path(item["path"]), str(item.get("kind", "file")).casefold()))
                            imported["claims"] += 1
                        except (KeyError, ScopeBreachError):
                            skipped += 1
                    for resource in claim_row.get("resources", []) if isinstance(claim_row, dict) else []:
                        connection.execute("INSERT OR IGNORE INTO resources(task_id,resource) VALUES(?,?)", (task_id, str(resource).casefold()))
                    gate_row = gates.get(task_id, {}) if isinstance(gates, dict) else {}
                    for name, gate in gate_row.get("gates", {}).items() if isinstance(gate_row, dict) else []:
                        if isinstance(gate, dict) and isinstance(gate.get("status"), str):
                            connection.execute("INSERT OR REPLACE INTO gates(task_id,name,status,note) VALUES(?,?,?,?)", (task_id, name, gate["status"].upper(), str(gate.get("note", ""))))
                            imported["gates"] += 1
                return imported
            self._mutate(migrate)
        else:
            self._write_snapshot()
        self._write_action(self._current_action())
        self._write_views()
        return {"status": "PASS", "imported": imported, "skipped": skipped}

    @staticmethod
    def _digest_file(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _read_capped_packet(path: Path, packet_name: str) -> bytes:
        contract = _load_v7_contract()
        maximum = contract.PACKET_CAPS.get(packet_name)
        if maximum is None:
            raise contract.ContractError(f"PACKET_CAP_UNKNOWN:{packet_name}")
        if path.stat().st_size > maximum:
            raise contract.ContractError(
                f"PACKET_CAP_EXCEEDED:{packet_name}"
            )
        raw = path.read_bytes()
        contract.validate_packet_cap(packet_name, raw)
        return raw

    def _v6_recovery_paths(self) -> list[tuple[str, Path]]:
        return [
            ("loop.db", self.db_path),
            ("loop.db-wal", Path(str(self.db_path) + "-wal")),
            ("loop.db-shm", Path(str(self.db_path) + "-shm")),
            ("SNAPSHOT.json", self.snapshot_path),
        ]

    def _v7_recovery_paths(self) -> list[tuple[str, Path]]:
        return [
            ("loop.db", self.db_path),
            ("loop.db-wal", Path(str(self.db_path) + "-wal")),
            ("loop.db-shm", Path(str(self.db_path) + "-shm")),
            ("SNAPSHOT.json", self.snapshot_path),
            ("ACTION.json", self.action_path),
            ("APPROVED_JOBS.json", self.approved_jobs_path),
            ("PROJECT_PROFILE.json", self.project_profile_path),
        ]

    def _v7_snapshot_reference_manifest(
        self, snapshot_raw: bytes
    ) -> list[dict[str, Any]]:
        try:
            snapshot = json.loads(snapshot_raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("V7_SNAPSHOT_INVALID") from exc
        capacity = _load_snapshot_capacity()
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("schema") != SCHEMA
            or snapshot.get("table_schema_sha256")
            != capacity.table_schema_sha256(V2_SNAPSHOT_COLUMNS)
        ):
            raise StateNotDurableError("V7_SNAPSHOT_INVALID")
        try:
            self._decode_snapshot(snapshot_raw)
        except (LoopError, OSError, ValueError) as exc:
            raise StateNotDurableError("V7_SNAPSHOT_INVALID") from exc
        references: list[dict[str, Any]] = []
        raw_references = [
            *snapshot.get("terminal_shards", []),
            *snapshot.get("active_shards", []),
        ]
        previous = snapshot.get("previous_generation")
        if previous is not None:
            raw_references.append(previous)
        seen: set[str] = set()
        for reference in raw_references:
            if not isinstance(reference, dict):
                raise StateNotDurableError("V7_SNAPSHOT_INVALID")
            relative = reference.get("path")
            digest = reference.get("sha256")
            size = reference.get("byte_size")
            if (
                not isinstance(relative, str)
                or relative in seen
                or not isinstance(digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                or isinstance(size, bool)
                or not isinstance(size, int)
                or size <= 0
            ):
                raise StateNotDurableError("V7_SNAPSHOT_INVALID")
            try:
                source = self._snapshot_reference_path(relative)
            except LoopError as exc:
                raise StateNotDurableError("V7_SNAPSHOT_INVALID") from exc
            if (
                not source.is_file()
                or source.stat().st_size != size
                or self._digest_file(source) != digest
            ):
                raise StateNotDurableError("V7_SNAPSHOT_INVALID")
            seen.add(relative)
            references.append(
                {"path": relative, "sha256": digest, "size": size}
            )
        return sorted(references, key=lambda row: row["path"])

    def _v7_database_matches_snapshot(
        self, connection: sqlite3.Connection, snapshot_raw: bytes
    ) -> bool:
        try:
            state = self._decode_snapshot(snapshot_raw)
            capacity = _load_snapshot_capacity()
            bundle = capacity.build_bundle(
                generation=self._generation(connection),
                columns=V2_SNAPSHOT_COLUMNS,
                tables=self._snapshot_tables(
                    connection, V2_SNAPSHOT_TABLES
                ),
                recovery_worktrees=[
                    dict(row)
                    for row in connection.execute(
                        "SELECT worktree_id,path FROM worktrees "
                        "ORDER BY worktree_id"
                    )
                ],
                completed_task_ids=self._completed_task_ids(connection),
                dispatch_attempts=self._snapshot_dispatch_attempts(
                    connection
                ),
                call_receipt_archive=state["call_receipt_archive"],
                current_snapshot_raw=snapshot_raw,
            )
            return bundle["root_raw"] == snapshot_raw
        except (
            LoopError,
            OSError,
            sqlite3.Error,
            ValueError,
            capacity.SnapshotCapacityError,
        ):
            return False

    def _write_recovery_manifest(
        self,
        recovery_dir: Path,
        recovery_id: str,
        source_snapshot_sha256: str,
        generation: int,
        files: list[dict[str, Any]],
    ) -> None:
        contract = _load_v7_contract()
        manifest = {
            "files": files,
            "generation": generation,
            "recovery_id": recovery_id,
            "schema": "x9-loop-v6-recovery-v1",
            "source_snapshot_sha256": source_snapshot_sha256,
        }
        self._atomic_state_write(recovery_dir / "RECOVERY.json", contract.canonical_json_bytes(manifest))

    def _write_migration_state(
        self,
        *,
        operation: str,
        phase: str,
        recovery_id: str,
        source_snapshot_sha256: str,
    ) -> None:
        if operation not in {"MIGRATE", "ROLLBACK", "MIGRATE_V3"} or phase not in {
            "PREPARED", "V6_HELD", "V7_INSTALLED", "V7_HELD",
            "V6_INSTALLED", "V3_INSTALLED", "ABORTED", "COMMITTED",
            "RECOVERED", "ROLLED_BACK",
        }:
            raise StateNotDurableError("MIGRATION_STATE_INVALID")
        state = {
            "operation": operation,
            "phase": phase,
            "recovery_id": recovery_id,
            "schema": "x9-loop-migration-state-v1",
            "source_snapshot_sha256": source_snapshot_sha256,
        }
        self._atomic_state_write(
            self.migration_state_path,
            _load_v7_contract().canonical_json_bytes(state),
        )

    def _read_migration_state(self) -> dict[str, str] | None:
        self._safe_state_path(self.migration_state_path)
        if not self.migration_state_path.exists():
            return None
        contract = _load_v7_contract()
        try:
            raw = self.migration_state_path.read_bytes()
            state = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("MIGRATION_STATE_INVALID") from exc
        if (
            not isinstance(state, dict)
            or set(state) != {
                "operation", "phase", "recovery_id", "schema",
                "source_snapshot_sha256",
            }
            or contract.canonical_json_bytes(state) != raw
            or state["schema"] != "x9-loop-migration-state-v1"
            or state["operation"] not in {
                "MIGRATE", "ROLLBACK", "MIGRATE_V3"
            }
            or state["phase"] not in {
                "PREPARED", "V6_HELD", "V7_INSTALLED", "V7_HELD",
                "V6_INSTALLED", "V3_INSTALLED", "ABORTED", "COMMITTED",
                "RECOVERED", "ROLLED_BACK",
            }
            or not re.fullmatch(
                (
                    r"v7-[0-9a-f]{16}-g[0-9]+-[0-9a-f]{8}"
                    if state["operation"] == "MIGRATE_V3"
                    else r"v6-[0-9a-f]{16}-g[0-9]+-[0-9a-f]{8}"
                ),
                str(state["recovery_id"]),
            )
            or not re.fullmatch(
                r"[0-9a-f]{64}", str(state["source_snapshot_sha256"])
            )
        ):
            raise StateNotDurableError("MIGRATION_STATE_INVALID")
        return state

    def _archive_migration_state(self, phase: str) -> None:
        state = self._read_migration_state()
        if state is None:
            return
        self._write_migration_state(
            operation=state["operation"],
            phase=phase,
            recovery_id=state["recovery_id"],
            source_snapshot_sha256=state["source_snapshot_sha256"],
        )
        recovery_dir = self.root / "recovery" / state["recovery_id"]
        self._safe_state_path(recovery_dir, create_parents=True, directory=True)
        destination = recovery_dir / (
            f"MIGRATION_STATE.{phase.casefold()}.{uuid.uuid4().hex}.json"
        )
        self._safe_state_path(destination, create_parents=True)
        os.replace(self.migration_state_path, destination)

    def _install_v6_write_fence(self, expected_snapshot: bytes) -> None:
        connection = sqlite3.connect(self.db_path, isolation_level=None)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("BEGIN EXCLUSIVE")
            self._validate_v1_schema_shape(connection)
            if (
                self.snapshot_path.read_bytes() != expected_snapshot
                or _json(self._snapshot_v1_data(connection)).encode("utf-8")
                != expected_snapshot
                or connection.execute("PRAGMA integrity_check").fetchone()[0]
                != "ok"
                or connection.execute("PRAGMA foreign_key_check").fetchall()
            ):
                raise StateNotDurableError("V6_SOURCE_DRIFT")
            for sql in V7_FENCE_TRIGGER_SQL.values():
                connection.execute(sql)
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _validate_held_v6_set(
        self, recovery_dir: Path, expected_snapshot: bytes
    ) -> None:
        db_path = recovery_dir / "active-loop.db"
        snapshot_path = recovery_dir / "active-SNAPSHOT.json"
        try:
            snapshot = snapshot_path.read_bytes()
            connection = sqlite3.connect(
                f"file:{db_path.as_posix()}?mode=ro", uri=True
            )
            connection.row_factory = sqlite3.Row
            try:
                self._validate_v1_schema_shape(
                    connection, allow_fence=True
                )
                projected = _json(
                    self._snapshot_v1_data(connection)
                ).encode("utf-8")
                integrity = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]
                foreign_keys = connection.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
            finally:
                connection.close()
        except (
            OSError,
            sqlite3.Error,
            TypeError,
            ValueError,
            LoopError,
        ) as exc:
            raise StateNotDurableError("V6_SOURCE_DRIFT") from exc
        if (
            snapshot != expected_snapshot
            or projected != expected_snapshot
            or integrity != "ok"
            or foreign_keys
        ):
            raise StateNotDurableError("V6_SOURCE_DRIFT")

    def recover_interrupted_migration(self) -> dict[str, Any]:
        state = self._read_migration_state()
        if state is None:
            return {"status": "NONE"}
        if state["phase"] in {
            "ABORTED", "COMMITTED", "RECOVERED", "ROLLED_BACK"
        }:
            self._archive_migration_state(state["phase"])
            return {"status": state["phase"], "recovery_id": state["recovery_id"]}
        if state["operation"] == "MIGRATE_V3":
            result = self.rollback_to_v7(state["recovery_id"])
            self._archive_migration_state("RECOVERED")
            return {
                "status": "RECOVERED",
                "operation": state["operation"],
                "recovery_id": state["recovery_id"],
                "rollback": result,
            }
        recovery_dir = self.root / "recovery" / state["recovery_id"]
        held_paths = list(recovery_dir.glob("active-*"))
        if (
            state["operation"] == "MIGRATE"
            and state["phase"] == "PREPARED"
            and not held_paths
            and self.db_path.is_file()
            and self.snapshot_path.is_file()
        ):
            active_snapshot = self.snapshot_path.read_bytes()
            connection = sqlite3.connect(
                f"file:{self.db_path.as_posix()}?mode=ro", uri=True
            )
            connection.row_factory = sqlite3.Row
            try:
                try:
                    self._validate_v1_schema_shape(connection)
                    unfenced = True
                except StateNotDurableError:
                    unfenced = False
                projected = _json(
                    self._snapshot_v1_data(connection)
                ).encode("utf-8")
                integrity = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]
                foreign_keys = connection.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
            except (
                sqlite3.Error,
                TypeError,
                ValueError,
                LoopError,
            ) as exc:
                raise StateNotDurableError(
                    "MIGRATION_RECOVERY_AMBIGUOUS"
                ) from exc
            finally:
                connection.close()
            if (
                unfenced
                and projected == active_snapshot
                and integrity == "ok"
                and not foreign_keys
            ):
                self._archive_migration_state("ABORTED")
                return {
                    "status": "PRESERVED_ACTIVE_V6",
                    "operation": state["operation"],
                    "recovery_id": state["recovery_id"],
                }
            try:
                connection = sqlite3.connect(
                    f"file:{self.db_path.as_posix()}?mode=ro", uri=True
                )
                connection.row_factory = sqlite3.Row
                try:
                    self._validate_v1_schema_shape(
                        connection, allow_fence=True
                    )
                    fenced_projection = _json(
                        self._snapshot_v1_data(connection)
                    ).encode("utf-8")
                finally:
                    connection.close()
            except (
                sqlite3.Error,
                TypeError,
                ValueError,
                LoopError,
            ):
                raise StateNotDurableError(
                    "MIGRATION_RECOVERY_AMBIGUOUS"
                )
            if fenced_projection != active_snapshot:
                raise StateNotDurableError(
                    "MIGRATION_RECOVERY_AMBIGUOUS"
                )
        result = self.rollback_to_v6(state["recovery_id"], _journal=False)
        self._archive_migration_state("RECOVERED")
        return {
            "status": "RECOVERED",
            "operation": state["operation"],
            "recovery_id": state["recovery_id"],
            "rollback": result,
        }

    def migrate_v1_to_v2(self, historical_missing: dict[str, str] | None = None) -> dict[str, Any]:
        self.recover_interrupted_migration()
        historical_missing = dict(historical_missing or {})
        self._safe_state_path(self.root, create_parents=True, directory=True)
        self._safe_state_path(self.db_path)
        self._safe_state_path(self.snapshot_path)
        if not self.db_path.is_file() or not self.snapshot_path.is_file():
            raise StateNotDurableError("V6_RECOVERY_SET_INCOMPLETE")
        source_snapshot = self.snapshot_path.read_bytes()
        try:
            snapshot = json.loads(source_snapshot.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("V6_SNAPSHOT_INVALID") from exc
        if snapshot.get("schema") != SCHEMA_V1 or not isinstance(snapshot.get("generation"), int):
            raise StateNotDurableError("V6_SNAPSHOT_INVALID")
        approved_jobs_existed = self.approved_jobs_path.exists()
        approved_jobs_original = (
            self.approved_jobs_path.read_bytes()
            if approved_jobs_existed
            else None
        )
        if approved_jobs_existed:
            self._ensure_approved_jobs()
        self._safe_state_path(self.action_path, create_parents=True)
        action_existed = self.action_path.exists()
        action_original = self.action_path.read_bytes() if action_existed else None
        source_snapshot_sha256 = hashlib.sha256(source_snapshot).hexdigest()
        recovery_id = f"v6-{source_snapshot_sha256[:16]}-g{snapshot['generation']}-{uuid.uuid4().hex[:8]}"
        recovery_dir = self.root / "recovery" / recovery_id
        self._safe_state_path(recovery_dir, create_parents=True, directory=True)
        recovery_files: list[dict[str, Any]] = []
        for name, source in self._v6_recovery_paths():
            self._safe_state_path(source)
            if not source.exists():
                continue
            target = recovery_dir / name
            self._safe_state_path(target, create_parents=True)
            shutil.copyfile(source, target)
            digest = self._digest_file(target)
            if digest != self._digest_file(source):
                raise StateNotDurableError("V6_RECOVERY_COPY_MISMATCH")
            recovery_files.append({"name": name, "sha256": digest, "size": target.stat().st_size})
        if {row["name"] for row in recovery_files} != {
            name for name, path in self._v6_recovery_paths() if path.exists()
        }:
            raise StateNotDurableError("V6_RECOVERY_SET_INCOMPLETE")

        source_db = recovery_dir / "loop.db"
        source = sqlite3.connect(f"file:{source_db.as_posix()}?mode=ro", uri=True)
        source.row_factory = sqlite3.Row
        classifications: list[tuple[str, str, str]] = []
        try:
            self._validate_v1_schema_shape(source)
            generation_row = source.execute("SELECT value FROM meta WHERE key='generation'").fetchone()
            generation = int(generation_row[0]) if generation_row else -1
            if generation != snapshot["generation"]:
                raise StateNotDurableError("V6_GENERATION_MISMATCH")
            try:
                expected_v1_snapshot = _json(self._snapshot_v1_data(source)).encode("utf-8")
            except (LoopError, sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise StateNotDurableError("V6_SNAPSHOT_INVALID") from exc
            if expected_v1_snapshot != source_snapshot:
                raise StateNotDurableError("V6_SNAPSHOT_INVALID")
            for worktree in source.execute("SELECT worktree_id,path FROM worktrees ORDER BY worktree_id"):
                if Path(worktree["path"]).is_dir():
                    continue
                worktree_id = worktree["worktree_id"]
                active_tasks = source.execute(
                    "SELECT COUNT(*) FROM tasks WHERE worktree_id=? AND status NOT IN ('COMPLETE','SUPERSEDED')",
                    (worktree_id,),
                ).fetchone()[0]
                active_dispatches = source.execute(
                    "SELECT COUNT(*) FROM dispatches d JOIN tasks t ON t.task_id=d.task_id "
                    "WHERE t.worktree_id=? AND d.status IN ('PREPARED','DISPATCHED')",
                    (worktree_id,),
                ).fetchone()[0]
                active_claims = source.execute(
                    "SELECT COUNT(*) FROM claims c JOIN tasks t ON t.task_id=c.task_id "
                    "WHERE t.worktree_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
                    (worktree_id,),
                ).fetchone()[0]
                active_resources = source.execute(
                    "SELECT COUNT(*) FROM resources r JOIN tasks t ON t.task_id=r.task_id "
                    "WHERE t.worktree_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
                    (worktree_id,),
                ).fetchone()[0]
                if any((active_tasks, active_dispatches, active_claims, active_resources)):
                    raise StateNotDurableError(f"ACTIVE_WORKTREE_MISSING:{worktree_id}")
                decision = historical_missing.get(worktree_id)
                if worktree_id != "core-legacy" or not isinstance(decision, str) or not re.fullmatch(r"[0-9a-f]{64}", decision):
                    raise StateNotDurableError(f"WORKTREE_MISSING:{worktree_id}")
                classifications.append((worktree_id, "HISTORICAL_MISSING", decision))
        finally:
            source.close()

        next_db = Path(str(self.db_path) + ".next")
        next_snapshot = Path(str(self.snapshot_path) + ".next")
        next_paths = (
            next_db, next_snapshot, Path(str(next_db) + "-wal"),
            Path(str(next_db) + "-shm"),
        )
        stale_next = []
        for path in next_paths:
            self._safe_state_path(path, create_parents=True)
            if os.path.lexists(path):
                stale_next.append(path)
        if stale_next:
            quarantine = (
                self.root / "recovery" / f"orphaned-next-{uuid.uuid4().hex}"
            )
            self._safe_state_path(
                quarantine, create_parents=True, directory=True
            )
            for path in stale_next:
                os.replace(path, quarantine / path.name)
        source = sqlite3.connect(f"file:{source_db.as_posix()}?mode=ro", uri=True)
        target = sqlite3.connect(next_db)
        try:
            source.backup(target)
        finally:
            source.close()
            target.close()
        target = sqlite3.connect(next_db, isolation_level=None)
        self._enable_v7_connection(target)
        target.row_factory = sqlite3.Row
        target.execute("PRAGMA foreign_keys=ON")
        try:
            target.execute("BEGIN IMMEDIATE")
            self._upgrade_schema_v2(target)
            self._upgrade_schema_v3(target)
            for worktree in target.execute(
                "SELECT path FROM worktrees ORDER BY worktree_id"
            ):
                self._capture_historical_receipts(
                    target, Path(worktree["path"])
                )
            target.executemany(
                "INSERT INTO worktree_classifications(worktree_id,classification,owner_decision_sha256) VALUES(?,?,?)",
                classifications,
            )
            migration_generation = snapshot["generation"] + 1
            target.execute("UPDATE meta SET value=? WHERE key='generation'", (str(migration_generation),))
            target.execute(
                "INSERT INTO meta(key,value) VALUES('v6_source_snapshot_sha256',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (source_snapshot_sha256,),
            )
            target.execute(
                "INSERT INTO meta(key,value) VALUES('migration_generation',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(migration_generation),),
            )
            if target.execute("PRAGMA foreign_key_check").fetchall():
                raise StateNotDurableError("V2_FOREIGN_KEY_INVALID")
            if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise StateNotDurableError("V2_INTEGRITY_INVALID")
            snapshot_bundle = self._snapshot_bundle(
                target,
                current_snapshot_raw=source_snapshot,
                generation=migration_generation,
            )
            self._validate_bundle_targets(snapshot_bundle)
            snapshot_bytes = snapshot_bundle["root_raw"]
            target.commit()
            checkpoint = target.execute(
                "PRAGMA wal_checkpoint(TRUNCATE)"
            ).fetchone()
            if not checkpoint or checkpoint[0] != 0 or checkpoint[1] != checkpoint[2]:
                raise StateNotDurableError("V2_WAL_CHECKPOINT_FAILED")
        except Exception:
            target.rollback()
            target.close()
            raise
        target.close()
        self._atomic_state_write(next_snapshot, snapshot_bytes)
        self._write_snapshot_bundle(snapshot_bundle, write_root=False)
        check = sqlite3.connect(f"file:{next_db.as_posix()}?mode=ro", uri=True)
        check.row_factory = sqlite3.Row
        try:
            self._validate_v3_schema_shape(check)
            if check.execute("PRAGMA user_version").fetchone()[0] != DB_USER_VERSION:
                raise StateNotDurableError("V2_VERSION_INVALID")
            if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise StateNotDurableError("V2_INTEGRITY_INVALID")
        finally:
            check.close()
        next_sidecars = [path for path in next_paths[2:] if path.exists()]
        if any(
            path.name.endswith("-wal") and path.stat().st_size != 0
            for path in next_sidecars
        ):
            raise StateNotDurableError("V2_WAL_CHECKPOINT_FAILED")
        if next_sidecars:
            quarantine = recovery_dir / f"next-sidecars-{uuid.uuid4().hex}"
            self._safe_state_path(
                quarantine, create_parents=True, directory=True
            )
            for path in next_sidecars:
                self._safe_state_path(path)
                os.replace(path, quarantine / path.name)
        if any(path.exists() for path in next_paths[2:]):
            raise StateNotDurableError("V2_NEXT_SIDECAR_RESIDUE")
        self._write_recovery_manifest(
            recovery_dir,
            recovery_id,
            source_snapshot_sha256,
            snapshot["generation"],
            recovery_files,
        )

        expected_source = {
            row["name"]: (row["sha256"], row["size"])
            for row in recovery_files
        }
        current_source = {
            name: (self._digest_file(path), path.stat().st_size)
            for name, path in self._v6_recovery_paths()
            if path.exists()
        }
        if current_source != expected_source:
            raise StateNotDurableError("V6_SOURCE_DRIFT")

        moved: list[tuple[Path, Path]] = []
        installed: list[Path] = []
        fence_installed = False
        try:
            self._write_migration_state(
                operation="MIGRATE",
                phase="PREPARED",
                recovery_id=recovery_id,
                source_snapshot_sha256=source_snapshot_sha256,
            )
            self._install_v6_write_fence(source_snapshot)
            fence_installed = True
            for name, original in self._v6_recovery_paths():
                if original.exists():
                    held = recovery_dir / f"active-{name}"
                    os.replace(original, held)
                    moved.append((original, held))
            self._validate_held_v6_set(recovery_dir, source_snapshot)
            self._write_migration_state(
                operation="MIGRATE",
                phase="V6_HELD",
                recovery_id=recovery_id,
                source_snapshot_sha256=source_snapshot_sha256,
            )
            os.replace(next_db, self.db_path)
            installed.append(self.db_path)
            os.replace(next_snapshot, self.snapshot_path)
            installed.append(self.snapshot_path)
            self._write_migration_state(
                operation="MIGRATE",
                phase="V7_INSTALLED",
                recovery_id=recovery_id,
                source_snapshot_sha256=source_snapshot_sha256,
            )
            self._ensure_approved_jobs()
            self._write_action(self._current_action())
            if not self._is_durable_read_only():
                raise StateNotDurableError("V2_POST_INSTALL_INVALID")
            self._validate_held_v6_set(recovery_dir, source_snapshot)
            self._archive_migration_state("COMMITTED")
        except BaseException as exc:
            if not fence_installed and not moved and not installed:
                if self.migration_state_path.exists():
                    self._archive_migration_state("ABORTED")
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                if isinstance(exc, StateNotDurableError):
                    raise
                raise StateNotDurableError(
                    "V2_ATOMIC_REPLACE_FAILED"
                ) from exc
            try:
                self.rollback_to_v6(recovery_id, _journal=False)
                if action_existed and action_original is not None:
                    self._atomic_state_write(
                        self.action_path, action_original
                    )
                elif self.action_path.exists():
                    os.replace(
                        self.action_path,
                        recovery_dir
                        / f"failed-ACTION-{uuid.uuid4().hex}.json",
                    )
                if (
                    approved_jobs_existed
                    and approved_jobs_original is not None
                ):
                    self._atomic_state_write(
                        self.approved_jobs_path,
                        approved_jobs_original,
                    )
                elif self.approved_jobs_path.exists():
                    os.replace(
                        self.approved_jobs_path,
                        recovery_dir
                        / f"failed-APPROVED_JOBS-{uuid.uuid4().hex}.json",
                    )
            except BaseException as restore_exc:
                raise StateNotDurableError("V2_RESTORE_FAILED") from restore_exc
            self._archive_migration_state("ABORTED")
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise StateNotDurableError(
                "V2_ATOMIC_REPLACE_FAILED"
            ) from exc
        return {
            "status": "PASS",
            "recovery_id": recovery_id,
            "source_snapshot_sha256": source_snapshot_sha256,
            "migration_generation": migration_generation,
        }

    def migrate_v2_to_v3(self) -> dict[str, Any]:
        self.recover_interrupted_migration()
        self._safe_state_path(self.root, create_parents=True, directory=True)
        required = {"loop.db", "SNAPSHOT.json", "ACTION.json"}
        active_paths = self._v7_recovery_paths()
        present = {
            name for name, path in active_paths if path.is_file()
        }
        if not required.issubset(present):
            raise StateNotDurableError("V7_RECOVERY_SET_INCOMPLETE")
        source_snapshot = self.snapshot_path.read_bytes()
        references = self._v7_snapshot_reference_manifest(source_snapshot)
        source_snapshot_sha256 = hashlib.sha256(source_snapshot).hexdigest()
        contract = _load_v7_contract()
        try:
            action_raw = self.action_path.read_bytes()
            action = json.loads(action_raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("V7_ACTION_INVALID") from exc
        if (
            len(action_raw) > 4096
            or contract.canonical_json_bytes(action) != action_raw
            or contract.canonical_json_bytes(self._current_action())
            != action_raw
        ):
            raise StateNotDurableError("V7_ACTION_INVALID")
        if self.approved_jobs_path.exists():
            self._ensure_approved_jobs()
        if self.project_profile_path.is_file():
            try:
                profile_raw = self.project_profile_path.read_bytes()
                profile = json.loads(profile_raw)
            except (
                OSError, UnicodeDecodeError, json.JSONDecodeError
            ) as exc:
                raise StateNotDurableError("PROJECT_PROFILE_INVALID") from exc
            if (
                not isinstance(profile, dict)
                or set(profile) != {"project_profile_id", "schema"}
                or profile.get("schema")
                != "x9-loop-project-profile-v1"
                or contract.canonical_json_bytes(profile) != profile_raw
            ):
                raise StateNotDurableError("PROJECT_PROFILE_INVALID")
        else:
            profile = {
                "project_profile_id": "profile-" + uuid.uuid4().hex,
                "schema": "x9-loop-project-profile-v1",
            }
            profile_raw = contract.canonical_json_bytes(profile)
        profile_id = profile["project_profile_id"]
        if (
            not isinstance(profile_id, str)
            or re.fullmatch(r"[A-Za-z0-9._:-]{16,128}", profile_id) is None
        ):
            raise StateNotDurableError("PROJECT_PROFILE_INVALID")

        source = sqlite3.connect(
            f"file:{self.db_path.as_posix()}?mode=ro", uri=True
        )
        source.row_factory = sqlite3.Row
        try:
            self._validate_v2_schema_shape(source)
            if (
                source.execute("PRAGMA integrity_check").fetchone()[0]
                != "ok"
                or source.execute("PRAGMA foreign_key_check").fetchall()
                or self._decode_snapshot(source_snapshot)[
                    "call_receipt_archive"
                ]
                != self._call_receipt_archive()
                or not self._v7_database_matches_snapshot(
                    source, source_snapshot
                )
            ):
                raise StateNotDurableError("V7_SOURCE_INVALID")
            generation = self._generation(source)
        finally:
            source.close()

        recovery_id = (
            f"v7-{source_snapshot_sha256[:16]}-g{generation}-"
            f"{uuid.uuid4().hex[:8]}"
        )
        recovery_dir = self.root / "recovery" / recovery_id
        self._safe_state_path(
            recovery_dir, create_parents=True, directory=True
        )
        files: list[dict[str, Any]] = []
        for name, source_path in active_paths:
            self._safe_state_path(source_path)
            if not source_path.is_file():
                continue
            target = recovery_dir / name
            self._safe_state_path(target, create_parents=True)
            shutil.copyfile(source_path, target)
            digest = self._digest_file(target)
            if digest != self._digest_file(source_path):
                raise StateNotDurableError("V7_RECOVERY_COPY_MISMATCH")
            files.append(
                {
                    "name": name,
                    "sha256": digest,
                    "size": target.stat().st_size,
                }
            )
        if {row["name"] for row in files} != present:
            raise StateNotDurableError("V7_RECOVERY_SET_INCOMPLETE")
        expected = {
            row["name"]: (row["sha256"], row["size"])
            for row in files
        }
        current = {
            name: (self._digest_file(path), path.stat().st_size)
            for name, path in active_paths
            if path.is_file()
        }
        if current != expected:
            raise StateNotDurableError("V7_SOURCE_DRIFT")

        source_stage = recovery_dir / "source-stage"
        self._safe_state_path(
            source_stage, create_parents=True, directory=True
        )
        for name in ("loop.db", "loop.db-wal", "loop.db-shm"):
            if name in expected:
                shutil.copyfile(recovery_dir / name, source_stage / name)
        staged_source = sqlite3.connect(
            f"file:{(source_stage / 'loop.db').as_posix()}?mode=ro",
            uri=True,
        )
        staged_source.row_factory = sqlite3.Row
        try:
            self._validate_v2_schema_shape(staged_source)
            if (
                staged_source.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]
                != "ok"
                or staged_source.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
                or not self._v7_database_matches_snapshot(
                    staged_source, source_snapshot
                )
            ):
                raise StateNotDurableError("V7_SOURCE_INVALID")
            next_db = Path(str(self.db_path) + ".next")
            next_snapshot = Path(str(self.snapshot_path) + ".next")
            next_profile = Path(str(self.project_profile_path) + ".next")
            next_action = Path(str(self.action_path) + ".next")
            next_sidecar_paths = (
                Path(str(next_db) + "-wal"),
                Path(str(next_db) + "-shm"),
            )
            next_paths = (
                next_db, next_snapshot, *next_sidecar_paths,
                next_profile, next_action,
            )
            if any(os.path.lexists(path) for path in next_paths):
                raise StateNotDurableError("V3_NEXT_RESIDUE")
            target = sqlite3.connect(next_db)
            try:
                staged_source.backup(target)
            finally:
                target.close()
        finally:
            staged_source.close()

        target = sqlite3.connect(next_db, isolation_level=None)
        self._enable_v7_connection(target)
        target.row_factory = sqlite3.Row
        target.execute("PRAGMA foreign_keys=ON")
        try:
            target.execute("BEGIN IMMEDIATE")
            self._validate_v2_schema_shape(target)
            self._upgrade_schema_v3(target)
            migration_generation = generation + 1
            target.execute(
                "UPDATE meta SET value=? WHERE key='generation'",
                (str(migration_generation),),
            )
            target.execute(
                "INSERT INTO meta(key,value) VALUES"
                "('v7_source_snapshot_sha256',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (source_snapshot_sha256,),
            )
            target.execute(
                "INSERT INTO meta(key,value) VALUES"
                "('v7_source_database_sha256',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (expected["loop.db"][0],),
            )
            target.execute(
                "INSERT INTO meta(key,value) VALUES"
                "('migration_generation',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(migration_generation),),
            )
            target.execute(
                "INSERT INTO meta(key,value) VALUES"
                "('project_profile_id',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (profile_id,),
            )
            baseline_action_fields = {
                "action", "action_id", "attempt", "dispatch_id",
                "must_record_transport", "schema", "target_actor_id",
                "target_role", "task_id", "work_order_path",
                "work_order_sha256",
            }
            bound_action_fields = {
                *baseline_action_fields,
                "project_profile_id", "work_order_id",
            }
            for row in target.execute(
                "SELECT o.dispatch_id,o.payload,d.task_id,d.target_id,"
                "w.work_order_id,w.packet_path,w.packet_sha256 "
                "FROM outbox o JOIN dispatches d "
                "ON d.dispatch_id=o.dispatch_id JOIN work_orders w "
                "ON w.task_id=d.task_id WHERE d.status='PREPARED'"
            ).fetchall():
                try:
                    prepared_action = json.loads(row["payload"])
                except (TypeError, json.JSONDecodeError) as exc:
                    raise StateNotDurableError("V7_ACTION_INVALID") from exc
                if (
                    not isinstance(prepared_action, dict)
                    or set(prepared_action)
                    not in {frozenset(baseline_action_fields), frozenset(bound_action_fields)}
                    or prepared_action.get("schema") != "x9-loop-action-v2"
                    or prepared_action.get("action") != "SEND_WORK_ORDER"
                    or prepared_action.get("dispatch_id") != row["dispatch_id"]
                    or prepared_action.get("task_id") != row["task_id"]
                    or prepared_action.get("target_actor_id") != row["target_id"]
                    or prepared_action.get("work_order_path") != row["packet_path"]
                    or prepared_action.get("work_order_sha256")
                    != row["packet_sha256"]
                    or (
                        "work_order_id" in prepared_action
                        and prepared_action["work_order_id"]
                        != row["work_order_id"]
                    )
                    or (
                        "project_profile_id" in prepared_action
                        and prepared_action["project_profile_id"] != profile_id
                    )
                ):
                    raise StateNotDurableError("V7_ACTION_INVALID")
                prepared_action["work_order_id"] = row["work_order_id"]
                prepared_action["project_profile_id"] = profile_id
                prepared_raw = contract.canonical_json_bytes(prepared_action)
                if len(prepared_raw) > 4096:
                    raise StateNotDurableError("V3_ACTION_INVALID")
                target.execute(
                    "UPDATE outbox SET payload=? WHERE dispatch_id=?",
                    (
                        prepared_raw.decode("utf-8").rstrip(chr(10)),
                        row["dispatch_id"],
                    ),
                )
            current_action_row = target.execute(
                "SELECT o.payload FROM outbox o JOIN dispatches d "
                "ON d.dispatch_id=o.dispatch_id WHERE d.status='PREPARED' "
                "ORDER BY d.created_at,d.dispatch_id LIMIT 1"
            ).fetchone()
            if current_action_row:
                migrated_action = json.loads(current_action_row["payload"])
            else:
                waiting = target.execute(
                    "SELECT 1 FROM dispatches d JOIN tasks t "
                    "ON t.task_id=d.task_id WHERE t.status NOT IN "
                    "('COMPLETE','SUPERSEDED') AND d.status='DISPATCHED' LIMIT 1"
                ).fetchone()
                migrated_action = self._status_action(
                    "WAIT" if waiting else "NOOP",
                    "delivery-acknowledged" if waiting else "no-outbox",
                )
            self._validate_v3_schema_shape(target)
            if (
                target.execute("PRAGMA integrity_check").fetchone()[0]
                != "ok"
                or target.execute("PRAGMA foreign_key_check").fetchall()
            ):
                raise StateNotDurableError("V3_DATABASE_INVALID")
            bundle = self._snapshot_bundle(
                target,
                current_snapshot_raw=source_snapshot,
                generation=migration_generation,
            )
            self._validate_bundle_targets(bundle)
            target.commit()
            checkpoint = target.execute(
                "PRAGMA wal_checkpoint(TRUNCATE)"
            ).fetchone()
            if (
                not checkpoint
                or checkpoint[0] != 0
                or checkpoint[1] != checkpoint[2]
            ):
                raise StateNotDurableError("V3_WAL_CHECKPOINT_FAILED")
        except BaseException:
            target.rollback()
            target.close()
            raise
        target.close()
        self._atomic_state_write(next_snapshot, bundle["root_raw"])
        migrated_action_raw = contract.canonical_json_bytes(migrated_action)
        if len(migrated_action_raw) > 4096:
            raise StateNotDurableError("V3_ACTION_INVALID")
        self._atomic_state_write(next_profile, profile_raw)
        self._atomic_state_write(next_action, migrated_action_raw)
        self._write_snapshot_bundle(bundle, write_root=False)
        check = sqlite3.connect(
            f"file:{next_db.as_posix()}?mode=ro", uri=True
        )
        check.row_factory = sqlite3.Row
        try:
            self._validate_v3_schema_shape(check)
            if (
                check.execute("PRAGMA integrity_check").fetchone()[0]
                != "ok"
                or check.execute("PRAGMA foreign_key_check").fetchall()
                or not self._snapshot_matches_connection(
                    check, bundle["root_raw"]
                )
            ):
                raise StateNotDurableError("V3_NEXT_INVALID")
        finally:
            check.close()
        sidecars = [path for path in next_sidecar_paths if path.exists()]
        if any(
            path.name.endswith("-wal") and path.stat().st_size
            for path in sidecars
        ):
            raise StateNotDurableError("V3_WAL_CHECKPOINT_FAILED")
        if sidecars:
            quarantine = recovery_dir / "next-sidecars"
            self._safe_state_path(
                quarantine, create_parents=True, directory=True
            )
            for path in sidecars:
                os.replace(path, quarantine / path.name)

        manifest = {
            "files": files,
            "generation": generation,
            "recovery_id": recovery_id,
            "schema": "x9-loop-v7-recovery-v1",
            "snapshot_references": references,
            "source_database_sha256": expected["loop.db"][0],
            "source_snapshot_sha256": source_snapshot_sha256,
        }
        self._atomic_state_write(
            recovery_dir / "RECOVERY.json",
            contract.canonical_json_bytes(manifest),
        )
        self._write_migration_state(
            operation="MIGRATE_V3",
            phase="PREPARED",
            recovery_id=recovery_id,
            source_snapshot_sha256=source_snapshot_sha256,
        )
        current = {
            name: (self._digest_file(path), path.stat().st_size)
            for name, path in active_paths
            if path.is_file()
        }
        if current != expected:
            self._archive_migration_state("ABORTED")
            raise StateNotDurableError("V7_SOURCE_DRIFT")

        hold_dir = recovery_dir / "install-hold"
        failed_dir = recovery_dir / "failed-install"
        self._safe_state_path(
            hold_dir, create_parents=True, directory=True
        )
        self._safe_state_path(
            failed_dir, create_parents=True, directory=True
        )
        replace_names = {
            "loop.db", "loop.db-wal", "loop.db-shm", "SNAPSHOT.json",
            "ACTION.json", "PROJECT_PROFILE.json",
        }
        held: list[tuple[Path, Path]] = []
        installed: list[Path] = []
        try:
            for name, path in active_paths:
                if name in replace_names and path.exists():
                    destination = hold_dir / name
                    os.replace(path, destination)
                    held.append((path, destination))
            self._write_migration_state(
                operation="MIGRATE_V3",
                phase="V7_HELD",
                recovery_id=recovery_id,
                source_snapshot_sha256=source_snapshot_sha256,
            )
            os.replace(next_db, self.db_path)
            installed.append(self.db_path)
            os.replace(next_snapshot, self.snapshot_path)
            installed.append(self.snapshot_path)
            os.replace(next_profile, self.project_profile_path)
            installed.append(self.project_profile_path)
            os.replace(next_action, self.action_path)
            installed.append(self.action_path)
            if not self._is_durable_read_only():
                raise StateNotDurableError("V3_POST_INSTALL_INVALID")
            if (
                self.action_path.read_bytes()
                != contract.canonical_json_bytes(self._current_action())
            ):
                raise StateNotDurableError("V3_ACTION_INVALID")
            self._write_migration_state(
                operation="MIGRATE_V3",
                phase="V3_INSTALLED",
                recovery_id=recovery_id,
                source_snapshot_sha256=source_snapshot_sha256,
            )
        except BaseException as exc:
            for path in reversed(installed):
                if path.exists():
                    os.replace(path, failed_dir / path.name)
            for active, held_path in reversed(held):
                if held_path.exists():
                    os.replace(held_path, active)
            for path in next_paths:
                if path.exists():
                    os.replace(path, failed_dir / path.name)
            if self.migration_state_path.exists():
                self._archive_migration_state("ABORTED")
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            if isinstance(exc, StateNotDurableError):
                raise
            raise StateNotDurableError("V3_ATOMIC_REPLACE_FAILED") from exc
        if any(path.exists() for path in next_paths):
            raise StateNotDurableError("V3_NEXT_RESIDUE")
        self._archive_migration_state("COMMITTED")
        return {
            "status": "PASS",
            "recovery_id": recovery_id,
            "source_snapshot_sha256": source_snapshot_sha256,
            "migration_generation": migration_generation,
        }

    def rollback_to_v7(self, recovery_id: str) -> dict[str, Any]:
        if not re.fullmatch(
            r"v7-[0-9a-f]{16}-g[0-9]+-[0-9a-f]{8}", recovery_id
        ):
            raise StateNotDurableError("RECOVERY_ID_INVALID")
        recovery_dir = self.root / "recovery" / recovery_id
        manifest_path = recovery_dir / "RECOVERY.json"
        self._safe_state_path(manifest_path)
        contract = _load_v7_contract()
        try:
            manifest_raw = manifest_path.read_bytes()
            manifest = json.loads(manifest_raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID") from exc
        expected_keys = {
            "files", "generation", "recovery_id", "schema",
            "snapshot_references", "source_database_sha256",
            "source_snapshot_sha256",
        }
        if (
            not isinstance(manifest, dict)
            or set(manifest) != expected_keys
            or contract.canonical_json_bytes(manifest) != manifest_raw
            or manifest["schema"] != "x9-loop-v7-recovery-v1"
            or manifest["recovery_id"] != recovery_id
            or isinstance(manifest["generation"], bool)
            or not isinstance(manifest["generation"], int)
            or not isinstance(manifest["files"], list)
            or not isinstance(manifest["snapshot_references"], list)
            or re.fullmatch(
                r"[0-9a-f]{64}", str(manifest["source_database_sha256"])
            )
            is None
            or re.fullmatch(
                r"[0-9a-f]{64}", str(manifest["source_snapshot_sha256"])
            )
            is None
        ):
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
        allowed = {name for name, _ in self._v7_recovery_paths()}
        expected: dict[str, dict[str, Any]] = {}
        for row in manifest["files"]:
            if (
                not isinstance(row, dict)
                or set(row) != {"name", "sha256", "size"}
                or row["name"] not in allowed
                or row["name"] in expected
                or re.fullmatch(r"[0-9a-f]{64}", str(row["sha256"]))
                is None
                or isinstance(row["size"], bool)
                or not isinstance(row["size"], int)
                or row["size"] < 0
            ):
                raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
            expected[row["name"]] = row
        if not {"loop.db", "SNAPSHOT.json", "ACTION.json"}.issubset(
            expected
        ):
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
        present = {
            name for name in allowed if (recovery_dir / name).is_file()
        }
        if set(expected) != present:
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
        for name, row in expected.items():
            source = recovery_dir / name
            if (
                source.stat().st_size != row["size"]
                or self._digest_file(source) != row["sha256"]
            ):
                raise StateNotDurableError("RECOVERY_HASH_MISMATCH")
        snapshot_raw = (recovery_dir / "SNAPSHOT.json").read_bytes()
        if (
            hashlib.sha256(snapshot_raw).hexdigest()
            != manifest["source_snapshot_sha256"]
            or expected["loop.db"]["sha256"]
            != manifest["source_database_sha256"]
            or self._v7_snapshot_reference_manifest(snapshot_raw)
            != manifest["snapshot_references"]
        ):
            raise StateNotDurableError("RECOVERY_HASH_MISMATCH")

        stage_dir = recovery_dir / f"rollback-stage-{uuid.uuid4().hex}"
        self._safe_state_path(
            stage_dir, create_parents=True, directory=True
        )
        for name in expected:
            shutil.copyfile(recovery_dir / name, stage_dir / name)
        source = sqlite3.connect(
            f"file:{(stage_dir / 'loop.db').as_posix()}?mode=ro", uri=True
        )
        source.row_factory = sqlite3.Row
        try:
            self._validate_v2_schema_shape(source)
            if (
                source.execute("PRAGMA integrity_check").fetchone()[0]
                != "ok"
                or source.execute("PRAGMA foreign_key_check").fetchall()
                or self._generation(source) != manifest["generation"]
                or not self._v7_database_matches_snapshot(
                    source, snapshot_raw
                )
            ):
                raise StateNotDurableError("RECOVERY_STATE_INVALID")
        finally:
            source.close()
        try:
            action_raw = (stage_dir / "ACTION.json").read_bytes()
            action = json.loads(action_raw)
            if (
                len(action_raw) > 4096
                or contract.canonical_json_bytes(action) != action_raw
            ):
                raise StateNotDurableError("RECOVERY_STATE_INVALID")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("RECOVERY_STATE_INVALID") from exc

        failed_dir = recovery_dir / f"v73-failed-{uuid.uuid4().hex}"
        self._safe_state_path(
            failed_dir, create_parents=True, directory=True
        )
        self._write_migration_state(
            operation="MIGRATE_V3",
            phase="PREPARED",
            recovery_id=recovery_id,
            source_snapshot_sha256=manifest["source_snapshot_sha256"],
        )
        next_paths = (
            Path(str(self.db_path) + ".next"),
            Path(str(self.snapshot_path) + ".next"),
            Path(str(self.db_path) + ".next-wal"),
            Path(str(self.db_path) + ".next-shm"),
        )
        held: list[tuple[Path, Path]] = []
        installed: list[tuple[str, Path]] = []
        try:
            for name, active in self._v7_recovery_paths():
                if active.exists():
                    destination = failed_dir / name
                    os.replace(active, destination)
                    held.append((active, destination))
            for path in next_paths:
                if path.exists():
                    destination = failed_dir / path.name
                    os.replace(path, destination)
                    held.append((path, destination))
            for name, active in self._v7_recovery_paths():
                if name not in expected:
                    continue
                os.replace(stage_dir / name, active)
                installed.append((name, active))
            restored = sqlite3.connect(
                f"file:{self.db_path.as_posix()}?mode=ro", uri=True
            )
            restored.row_factory = sqlite3.Row
            try:
                self._validate_v2_schema_shape(restored)
                valid = (
                    restored.execute(
                        "PRAGMA integrity_check"
                    ).fetchone()[0]
                    == "ok"
                    and not restored.execute(
                        "PRAGMA foreign_key_check"
                    ).fetchall()
                    and self._v7_database_matches_snapshot(
                        restored, self.snapshot_path.read_bytes()
                    )
                )
            finally:
                restored.close()
            if not valid:
                raise StateNotDurableError("RECOVERY_RESTORE_MISMATCH")
            for name, active in installed:
                row = expected[name]
                if (
                    active.stat().st_size != row["size"]
                    or self._digest_file(active) != row["sha256"]
                ):
                    raise StateNotDurableError("RECOVERY_RESTORE_MISMATCH")
        except BaseException as exc:
            for name, active in reversed(installed):
                if active.exists():
                    os.replace(active, failed_dir / f"partial-{name}")
            for active, stored in reversed(held):
                if stored.exists():
                    os.replace(stored, active)
            if self.migration_state_path.exists():
                self._archive_migration_state("ABORTED")
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            if isinstance(exc, StateNotDurableError):
                raise
            raise StateNotDurableError("RECOVERY_RESTORE_FAILED") from exc
        if any(path.exists() for path in next_paths):
            raise StateNotDurableError("V3_NEXT_RESIDUE")
        self._archive_migration_state("ROLLED_BACK")
        return {
            "status": "PASS",
            "recovery_id": recovery_id,
            "restored_files": sorted(expected),
            "v73_evidence_path": str(
                failed_dir.relative_to(self.repo)
            ).replace("\\", "/"),
        }

    def rollback_to_v6(self, recovery_id: str, _journal: bool = True) -> dict[str, Any]:
        if not re.fullmatch(r"v6-[0-9a-f]{16}-g[0-9]+-[0-9a-f]{8}", recovery_id):
            raise StateNotDurableError("RECOVERY_ID_INVALID")
        recovery_dir = self.root / "recovery" / recovery_id
        manifest_path = recovery_dir / "RECOVERY.json"
        self._safe_state_path(manifest_path)
        contract = _load_v7_contract()
        try:
            manifest_raw = manifest_path.read_bytes()
            manifest = json.loads(manifest_raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID") from exc
        if (
            not isinstance(manifest, dict)
            or set(manifest) != {
                "files", "generation", "recovery_id", "schema",
                "source_snapshot_sha256",
            }
            or contract.canonical_json_bytes(manifest) != manifest_raw
            or manifest["schema"] != "x9-loop-v6-recovery-v1"
            or manifest["recovery_id"] != recovery_id
            or not isinstance(manifest["generation"], int)
            or not re.fullmatch(
                r"[0-9a-f]{64}", str(manifest["source_snapshot_sha256"])
            )
            or not isinstance(manifest["files"], list)
        ):
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
        allowed_names = {name for name, _ in self._v6_recovery_paths()}
        expected: dict[str, dict[str, Any]] = {}
        for row in manifest["files"]:
            if (
                not isinstance(row, dict)
                or set(row) != {"name", "sha256", "size"}
                or row["name"] not in allowed_names
                or row["name"] in expected
                or not re.fullmatch(r"[0-9a-f]{64}", str(row["sha256"]))
                or isinstance(row["size"], bool)
                or not isinstance(row["size"], int)
                or row["size"] < 0
            ):
                raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
            expected[row["name"]] = row
        present = {
            name for name in allowed_names if (recovery_dir / name).is_file()
        }
        if (
            not {"loop.db", "SNAPSHOT.json"}.issubset(expected)
            or set(expected) != present
        ):
            raise StateNotDurableError("RECOVERY_MANIFEST_INVALID")
        for name, row in expected.items():
            source = recovery_dir / name
            self._safe_state_path(source)
            if (
                source.stat().st_size != row["size"]
                or self._digest_file(source) != row["sha256"]
            ):
                raise StateNotDurableError("RECOVERY_HASH_MISMATCH")
        snapshot_source = recovery_dir / "SNAPSHOT.json"
        if (
            self._digest_file(snapshot_source)
            != manifest["source_snapshot_sha256"]
        ):
            raise StateNotDurableError("RECOVERY_HASH_MISMATCH")

        def validate_v1_set(directory: Path) -> None:
            snapshot_path = directory / "SNAPSHOT.json"
            db_path = directory / "loop.db"
            try:
                snapshot_bytes = snapshot_path.read_bytes()
                snapshot = json.loads(snapshot_bytes)
                connection = sqlite3.connect(
                    f"file:{db_path.as_posix()}?mode=ro", uri=True
                )
                connection.row_factory = sqlite3.Row
                try:
                    self._validate_v1_schema_shape(connection)
                    generation_row = connection.execute(
                        "SELECT value FROM meta WHERE key='generation'"
                    ).fetchone()
                    generation = int(generation_row[0]) if generation_row else -1
                    expected_snapshot = _json(
                        self._snapshot_v1_data(connection)
                    ).encode("utf-8")
                    integrity = connection.execute(
                        "PRAGMA integrity_check"
                    ).fetchone()[0]
                    foreign_keys = connection.execute(
                        "PRAGMA foreign_key_check"
                    ).fetchall()
                    user_version = connection.execute(
                        "PRAGMA user_version"
                    ).fetchone()[0]
                finally:
                    connection.close()
            except (
                OSError, sqlite3.Error, UnicodeDecodeError, json.JSONDecodeError,
                TypeError, ValueError, LoopError,
            ) as exc:
                raise StateNotDurableError("RECOVERY_STATE_INVALID") from exc
            if (
                user_version >= 2
                or integrity != "ok"
                or foreign_keys
                or snapshot.get("schema") != SCHEMA_V1
                or snapshot.get("generation") != generation
                or generation != manifest["generation"]
                or expected_snapshot != snapshot_bytes
            ):
                raise StateNotDurableError("RECOVERY_STATE_INVALID")

        validate_v1_set(recovery_dir)
        stage_dir = recovery_dir / f"rollback-next-{uuid.uuid4().hex}"
        self._safe_state_path(stage_dir, create_parents=True, directory=True)
        try:
            for name in sorted(expected):
                self._atomic_state_write(
                    stage_dir / name, (recovery_dir / name).read_bytes()
                )
            validate_v1_set(stage_dir)
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            if isinstance(exc, StateNotDurableError):
                raise
            raise StateNotDurableError("RECOVERY_STAGE_FAILED") from exc

        if _journal:
            self._write_migration_state(
                operation="ROLLBACK",
                phase="PREPARED",
                recovery_id=recovery_id,
                source_snapshot_sha256=manifest["source_snapshot_sha256"],
            )
        failed_dir = recovery_dir / f"v7-failed-{uuid.uuid4().hex}"
        self._safe_state_path(failed_dir, create_parents=True, directory=True)
        active_paths = [
            *self._v6_recovery_paths(),
            ("ACTION.json", self.action_path),
            ("APPROVED_JOBS.json", self.approved_jobs_path),
            ("snapshots", self.root / "snapshots"),
            ("loop.db.next", Path(str(self.db_path) + ".next")),
            ("loop.db.next-wal", Path(str(self.db_path) + ".next-wal")),
            ("loop.db.next-shm", Path(str(self.db_path) + ".next-shm")),
            (
                "SNAPSHOT.json.next", Path(str(self.snapshot_path) + ".next")
            ),
        ]
        held: list[tuple[str, Path, Path]] = []
        installed: list[tuple[str, Path]] = []
        try:
            for name, active in active_paths:
                self._safe_state_path(active)
                if active.exists():
                    destination = failed_dir / name
                    os.replace(active, destination)
                    held.append((name, active, destination))
            if _journal:
                self._write_migration_state(
                    operation="ROLLBACK",
                    phase="V7_HELD",
                    recovery_id=recovery_id,
                    source_snapshot_sha256=manifest["source_snapshot_sha256"],
                )
            for name, active in self._v6_recovery_paths():
                if name not in expected:
                    continue
                os.replace(stage_dir / name, active)
                installed.append((name, active))
            validate_v1_set(self.root)
            self._write_action(self._current_action())
            installed.append(("ACTION.json", self.action_path))
            if _journal:
                self._write_migration_state(
                    operation="ROLLBACK",
                    phase="V6_INSTALLED",
                    recovery_id=recovery_id,
                    source_snapshot_sha256=manifest["source_snapshot_sha256"],
                )
            for name, active in installed:
                if name in expected and (
                    active.stat().st_size != expected[name]["size"]
                    or self._digest_file(active) != expected[name]["sha256"]
                ):
                    raise StateNotDurableError("RECOVERY_RESTORE_MISMATCH")
        except BaseException as exc:
            restore_errors = []
            for name, active in reversed(installed):
                try:
                    if active.exists():
                        os.replace(active, failed_dir / f"partial-v6-{name}")
                except OSError as restore_exc:
                    restore_errors.append(type(restore_exc).__name__)
            for name, active, stored in reversed(held):
                try:
                    if stored.exists() and not active.exists():
                        os.replace(stored, active)
                except OSError as restore_exc:
                    restore_errors.append(type(restore_exc).__name__)
            if restore_errors:
                raise StateNotDurableError("RECOVERY_ROLLBACK_FAILED") from exc
            if _journal:
                self._archive_migration_state("ABORTED")
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            if isinstance(exc, StateNotDurableError):
                raise
            raise StateNotDurableError("RECOVERY_RESTORE_FAILED") from exc
        if _journal:
            self._archive_migration_state("COMMITTED")
        return {
            "status": "PASS",
            "recovery_id": recovery_id,
            "restored_files": sorted(expected),
            "v7_evidence_path": str(failed_dir.relative_to(self.repo)).replace("\\", "/"),
        }
    def _normal_path(self, value: str) -> str:
        if not isinstance(value, str):
            raise ScopeBreachError("INVALID_PATH")
        raw = value.strip().replace("\\", "/")
        if (not raw or raw in {".", ".."} or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw)
                or any(character in raw for character in "*?[]{}")):
            raise ScopeBreachError(f"INVALID_PATH:{value}")
        path = PurePosixPath(raw)
        if any(part in {"", ".", ".."} for part in path.parts):
            raise ScopeBreachError(f"INVALID_PATH:{value}")
        canonical = str(path)
        if canonical in {"", "."}:
            raise ScopeBreachError(f"INVALID_PATH:{value}")
        return canonical.casefold()

    @staticmethod
    def _claim_kind(value: Any) -> str:
        kind = str(value).casefold()
        if kind not in {"file", "dir"}:
            raise ScopeBreachError(f"INVALID_CLAIM_KIND:{value}")
        return kind
    @staticmethod
    def _overlap(path_a: str, kind_a: str, path_b: str, kind_b: str) -> bool:
        folded_a = path_a.casefold()
        folded_b = path_b.casefold()
        if folded_a == folded_b:
            return True
        return (kind_a == "dir" and folded_b.startswith(folded_a + "/")) or (
            kind_b == "dir" and folded_a.startswith(folded_b + "/")
        )

    @staticmethod
    def _receipt_metric_keys(worktree_path: str | Path) -> tuple[str, str]:
        canonical = str(Path(worktree_path).resolve()).replace("\\", "/").casefold()
        scope = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
        return f"receipt-count:{scope}", f"receipt-root:{scope}"

    def _receipt_state(self, connection: sqlite3.Connection, worktree_path: str | Path) -> tuple[int, str]:
        count_key, root_key = self._receipt_metric_keys(worktree_path)
        count_row = connection.execute("SELECT value FROM metrics WHERE key=?", (count_key,)).fetchone()
        root_row = connection.execute("SELECT value FROM metrics WHERE key=?", (root_key,)).fetchone()
        if not count_row and not root_row:
            return 0, _sha([])
        try:
            count = int(count_row[0]) if count_row else -1
            root = str(root_row[0]) if root_row else ""
        except (TypeError, ValueError) as exc:
            raise StateNotDurableError("RECEIPT_SET_INVALID") from exc
        if count < 0 or not re.fullmatch(r"[0-9a-f]{64}", root):
            raise StateNotDurableError("RECEIPT_SET_INVALID")
        return count, root

    def _set_receipt_state(
        self, connection: sqlite3.Connection, worktree_id: str, hashes: list[str]
    ) -> None:
        worktree = connection.execute(
            "SELECT path FROM worktrees WHERE worktree_id=?", (worktree_id,)
        ).fetchone()
        if not worktree:
            raise StateNotDurableError("RECEIPT_WORKTREE_UNKNOWN")
        count_key, root_key = self._receipt_metric_keys(worktree["path"])
        values = sorted(hashes)
        connection.execute(
            "INSERT INTO metrics(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (count_key, str(len(values))),
        )
        connection.execute(
            "INSERT INTO metrics(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (root_key, _sha(values)),
        )

    def _registered_rejected_receipt_paths(
        self,
        worktree_root: Path,
        connection: sqlite3.Connection | None = None,
    ) -> set[str]:
        owns_connection = connection is None
        connection = connection or self._connect()
        try:
            resolved_root = worktree_root.resolve(strict=True)
            contract = _load_v7_contract()
            if not connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' "
                "AND name='inbox'"
            ).fetchone():
                return set()
            paths: dict[str, str] = {}
            for row in connection.execute(
                "SELECT i.event_sha256,i.payload,w.path AS worktree_path "
                "FROM inbox i JOIN tasks t ON t.task_id=i.task_id "
                "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "WHERE i.status LIKE 'REJECTED:%' "
                "OR i.status LIKE 'REPAIR_ACKNOWLEDGED:%'"
            ):
                try:
                    if Path(row["worktree_path"]).resolve(strict=True) != resolved_root:
                        continue
                    envelope_raw = row["payload"].encode("utf-8")
                    envelope = json.loads(envelope_raw)
                    validated = contract.validate_inbox_event(
                        envelope_raw,
                        row["event_sha256"],
                        envelope["project_profile_id"],
                    )
                    relative = self._normal_path(
                        validated["payload_ref"]["path"]
                    )
                    digest = validated["payload_ref"]["sha256"]
                    receipt_path = self._resolve_under(
                        resolved_root,
                        resolved_root
                        / Path(*PurePosixPath(relative).parts),
                    )
                    actual = hashlib.sha256(
                        receipt_path.read_bytes()
                    ).hexdigest()
                except (
                    OSError, RuntimeError, KeyError, TypeError, ValueError,
                    json.JSONDecodeError, contract.ContractError,
                ) as exc:
                    raise StateNotDurableError(
                        "REJECTED_RECEIPT_REGISTRY_INVALID"
                    ) from exc
                if actual != digest:
                    raise StateNotDurableError(
                        "REJECTED_RECEIPT_TAMPERED"
                    )
                if relative in paths and paths[relative] != digest:
                    raise StateNotDurableError(
                        "REJECTED_RECEIPT_REGISTRY_INVALID"
                    )
                paths[relative] = digest
            return set(paths)
        finally:
            if owns_connection:
                connection.close()

    def _validated_receipt_entries(
        self, worktree_root: Path, connection: sqlite3.Connection | None = None,
        exclude_paths: set[str] | None = None,
    ) -> dict[str, str]:
        owns_connection = connection is None
        connection = connection or self._connect()
        try:
            resolved_root = worktree_root.resolve(strict=True)
            registered = False
            for row in connection.execute("SELECT worktree_id,path FROM worktrees"):
                try:
                    if Path(row["path"]).resolve(strict=True) == resolved_root:
                        registered = True
                        break
                except (OSError, RuntimeError):
                    continue
            if not registered:
                raise StateNotDurableError("RECEIPT_WORKTREE_UNKNOWN")
            expected_count, expected_root = self._receipt_state(connection, resolved_root)
            excluded = {self._normal_path(path) for path in (exclude_paths or set())}
            rejected: dict[str, str] = {}
            contract = _load_v7_contract()
            inbox_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' "
                "AND name='inbox'"
            ).fetchone()
            rejected_rows = connection.execute(
                "SELECT i.event_sha256,i.payload,w.path AS worktree_path "
                "FROM inbox i JOIN tasks t ON t.task_id=i.task_id "
                "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "WHERE i.status LIKE 'REJECTED:%' "
                "OR i.status LIKE 'REPAIR_ACKNOWLEDGED:%'"
            ) if inbox_exists else ()
            for row in rejected_rows:
                try:
                    if Path(row["worktree_path"]).resolve(strict=True) != resolved_root:
                        continue
                    envelope_raw = row["payload"].encode("utf-8")
                    envelope = json.loads(envelope_raw)
                    validated = contract.validate_inbox_event(
                        envelope_raw,
                        row["event_sha256"],
                        envelope["project_profile_id"],
                    )
                    relative = self._normal_path(
                        validated["payload_ref"]["path"]
                    )
                    digest = validated["payload_ref"]["sha256"]
                except (
                    OSError, RuntimeError, KeyError, TypeError, ValueError,
                    json.JSONDecodeError, contract.ContractError,
                ) as exc:
                    raise StateNotDurableError(
                        "REJECTED_RECEIPT_REGISTRY_INVALID"
                    ) from exc
                if relative in rejected and rejected[relative] != digest:
                    raise StateNotDurableError(
                        "REJECTED_RECEIPT_REGISTRY_INVALID"
                    )
                rejected[relative] = digest
            entries: dict[str, str] = {}
            seen_rejected: set[str] = set()
            receipts = resolved_root / ".devad" / "workers"
            for candidate in receipts.glob("*/receipts/*.json") if receipts.is_dir() else ():
                try:
                    resolved = self._resolve_under(resolved_root, candidate)
                    relative = self._normal_path(resolved.relative_to(resolved_root).as_posix())
                    if relative in excluded:
                        continue
                    data = resolved.read_bytes()
                    if relative in rejected:
                        if hashlib.sha256(data).hexdigest() != rejected[relative]:
                            raise StateNotDurableError(
                                "REJECTED_RECEIPT_TAMPERED"
                            )
                        seen_rejected.add(relative)
                        continue
                    receipt = json.loads(data.decode("utf-8"))
                    parts = PurePosixPath(relative).parts
                    if self._is_v6_status_only_handover_receipt(receipt, parts, resolved.stem):
                        continue
                    actor = receipt.get("worker_id") or receipt.get("actor_id")
                    if (len(parts) != 5 or parts[0:2] != (".devad", "workers")
                            or parts[3] != "receipts" or parts[2] != actor
                            or resolved.stem != receipt.get("event_id")
                            or receipt.get("schema") not in {"x9-loop-lite-result-v1", "x9-loop-lite-thinx-decision-v1", "x9-loop-result-v2", "x9-loop-thinx-decision-v2"}):
                        raise ValueError("receipt shape")
                    entries[relative] = hashlib.sha256(data).hexdigest()
                except (OSError, ValueError, RuntimeError, json.JSONDecodeError, ScopeBreachError, AttributeError) as exc:
                    raise StateNotDurableError("RECEIPT_SET_MISMATCH") from exc
            if seen_rejected != set(rejected):
                raise StateNotDurableError("REJECTED_RECEIPT_MISSING")
            hashes = sorted(entries.values())
            if len(hashes) != expected_count or _sha(hashes) != expected_root:
                raise StateNotDurableError("RECEIPT_SET_MISMATCH")
            return entries
        finally:
            if owns_connection:
                connection.close()

    def _validated_receipt_proof_paths(
        self,
        worktree_root: Path,
        receipt_entries: Mapping[str, str],
    ) -> set[str]:
        contract = _load_v7_contract()
        root = worktree_root.resolve(strict=True)
        accepted: set[str] = set()
        for receipt_relative, receipt_sha256 in receipt_entries.items():
            try:
                receipt_path = self._resolve_under(
                    root,
                    root / Path(*PurePosixPath(receipt_relative).parts),
                )
                receipt_raw = receipt_path.read_bytes()
                receipt = json.loads(receipt_raw)
            except (
                OSError, RuntimeError, ValueError, json.JSONDecodeError,
            ) as exc:
                raise StateNotDurableError("RECEIPT_SET_MISMATCH") from exc
            if hashlib.sha256(receipt_raw).hexdigest() != receipt_sha256:
                raise StateNotDurableError("RECEIPT_SET_MISMATCH")
            if receipt.get("schema") != "x9-loop-result-v2":
                continue
            expected = {
                "dispatch_id": receipt.get("dispatch_id"),
                "event_id": receipt.get("event_id"),
                "packet_sha256": receipt.get("packet_sha256"),
                "task_id": receipt.get("task_id"),
                "work_order_id": receipt.get("work_order_id"),
                "work_order_sha256": receipt.get("work_order_sha256"),
                "worker_id": receipt.get("worker_id"),
            }
            try:
                verified_order, _compatibility = self._verify_work_order(
                    receipt["work_order_id"],
                    allow_terminal_historical_contract=True,
                )
                validated, _ = contract.validate_worker_result(
                    receipt,
                    expected,
                    require_proof_bound_approaches=(
                        "autonomy_contract" in verified_order
                    ),
                )
            except (IdentityError, contract.ContractError) as exc:
                raise StateNotDurableError("RECEIPT_SET_MISMATCH") from exc
            for item in validated.get("proof", []):
                try:
                    relative = self._normal_path(item["path"])
                    expected_path = self._normal_path(
                        f".devad/workers/{validated['worker_id']}/proof/"
                        f"{validated['event_id']}/{item['kind']}.json"
                    )
                    proof_path = self._resolve_under(
                        root,
                        root / Path(*PurePosixPath(relative).parts),
                    )
                    proof_raw = proof_path.read_bytes()
                    proof = json.loads(proof_raw)
                except (
                    OSError, RuntimeError, KeyError, TypeError, ValueError,
                    json.JSONDecodeError,
                ) as exc:
                    raise StateNotDurableError("RESULT_PROOF_INVALID") from exc
                expected_proof = {
                    "dispatch_id": validated["dispatch_id"],
                    "event_id": validated["event_id"],
                    "kind": item["kind"],
                    "schema": "x9-loop-proof-v2",
                    "status": "PASS",
                    "task_id": validated["task_id"],
                    "work_order_id": validated["work_order_id"],
                    "worker_id": validated["worker_id"],
                }
                if (
                    relative != expected_path
                    or relative in accepted
                    or hashlib.sha256(proof_raw).hexdigest()
                    != item["sha256"]
                    or proof != expected_proof
                    or contract.canonical_json_bytes(proof) != proof_raw
                ):
                    raise StateNotDurableError("RESULT_PROOF_INVALID")
                accepted.add(relative)
            for approach in validated.get("approach_receipts", []):
                try:
                    relative = self._normal_path(approach["evidence_path"])
                    expected_path = self._normal_path(
                        f".devad/workers/{validated['worker_id']}/proof/"
                        f"{validated['event_id']}/approaches/"
                        f"{approach['approach_id']}.json"
                    )
                    proof_path = self._resolve_under(
                        root, root / Path(*PurePosixPath(relative).parts)
                    )
                    proof_raw = proof_path.read_bytes()
                    proof = json.loads(proof_raw)
                except (
                    OSError, RuntimeError, KeyError, TypeError, ValueError,
                    json.JSONDecodeError,
                ) as exc:
                    raise StateNotDurableError(
                        "APPROACH_EVIDENCE_INVALID"
                    ) from exc
                expected_proof = {
                    "action_class": approach["action_class"],
                    "approach_id": approach["approach_id"],
                    "event_id": validated["event_id"],
                    "failure_code": approach["failure_code"],
                    "hypothesis": approach["hypothesis"],
                    "next_route": approach["next_route"],
                    "progress": approach["progress"],
                    "route": approach["route"],
                    "schema": "x9-loop-approach-proof-v1",
                    "source_hashes": approach["source_hashes"],
                    "task_id": validated["task_id"],
                    "work_order_id": validated["work_order_id"],
                    "worker_id": validated["worker_id"],
                }
                if (
                    relative != expected_path
                    or relative in accepted
                    or hashlib.sha256(proof_raw).hexdigest()
                    != approach["evidence_sha256"]
                    or proof != expected_proof
                    or contract.canonical_json_bytes(proof) != proof_raw
                ):
                    raise StateNotDurableError("APPROACH_EVIDENCE_INVALID")
                for source_relative, source_sha256 in (
                    approach["source_hashes"].items()
                ):
                    try:
                        source = self._resolve_under(
                            root,
                            root / Path(*PurePosixPath(source_relative).parts),
                        )
                        source_raw = source.read_bytes()
                    except (OSError, RuntimeError) as exc:
                        raise StateNotDurableError(
                            "APPROACH_EVIDENCE_INVALID"
                        ) from exc
                    if hashlib.sha256(source_raw).hexdigest() != source_sha256:
                        raise StateNotDurableError("APPROACH_EVIDENCE_INVALID")
                accepted.add(relative)
        return accepted

    def _validate_consumed_worker_outbox(
        self,
        worktree_root: Path,
        *,
        inbox_event: Mapping[str, Any],
        task_id: str,
        worker_id: str,
        worktree_id: str,
        worktree_path: str,
        base_sha: str,
        work_order_id: str,
        work_order_sha256: str,
        dispatch_id: str,
        packet_sha256: str,
        result_sha256: str,
        receipt_entries: Mapping[str, str] | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> str | None:
        contract = _load_v7_contract()
        try:
            root = worktree_root.resolve(strict=True)
            declared_root = Path(worktree_path).resolve(strict=True)
            if (
                root != declared_root
                or not root.is_dir()
                or self._is_reparse(root)
            ):
                raise ValueError("worktree path")
            owns_connection = connection is None
            bound_connection = connection or self._connect()
            try:
                bound = bound_connection.execute(
                    "SELECT path FROM worktrees WHERE worktree_id=?",
                    (worktree_id,),
                ).fetchone()
                if (
                    bound is None
                    or Path(bound["path"]).resolve(strict=True) != root
                ):
                    raise ValueError("worktree identity")
            finally:
                if owns_connection:
                    bound_connection.close()
            if set(inbox_event) != {
                "dispatch_id",
                "event_id",
                "event_sha256",
                "payload",
                "status",
            }:
                raise ValueError("inbox fields")
            event_id = inbox_event["event_id"]
            if (
                inbox_event["dispatch_id"] != dispatch_id
                or inbox_event["status"] != "CONSUMED"
                or not isinstance(event_id, str)
                or not event_id
            ):
                raise ValueError("inbox identity")
            event_sha256 = self._require_sha256(
                inbox_event["event_sha256"], "INBOX_EVENT_INVALID"
            )
            if not isinstance(inbox_event["payload"], str):
                raise ValueError("inbox payload")
            inbox_raw = inbox_event["payload"].encode("utf-8")
            if hashlib.sha256(inbox_raw).hexdigest() != event_sha256:
                raise ValueError("inbox hash")
            validated_inbox = contract.validate_inbox_event(
                inbox_raw,
                event_sha256,
                self._ensure_project_profile(),
            )
            receipt_relative = self._normal_path(
                f".devad/workers/{worker_id}/receipts/{event_id}.json"
            )
            expected_inbox = {
                "event_id": event_id,
                "event_type": "WORKER_RESULT",
                "payload_ref": {
                    "path": receipt_relative,
                    "sha256": result_sha256,
                },
                "project_profile_id": self._ensure_project_profile(),
                "schema": "x9-loop-inbox-event-v1",
                "source_actor_id": worker_id,
                "source_role": "WORKER",
            }
            if validated_inbox != expected_inbox:
                raise ValueError("inbox envelope")
            expected_outbox = self._normal_path(
                f".devad/workers/{worker_id}/outbox/"
                f"{event_id}/INBOX_EVENT.json"
            )
            outbox_lexical = root / Path(
                *PurePosixPath(expected_outbox).parts
            )
            if not os.path.lexists(outbox_lexical):
                return None
            current = root
            parts = PurePosixPath(expected_outbox).parts
            for index, part in enumerate(parts):
                current = current / part
                if (
                    not os.path.lexists(current)
                    or self._is_reparse(current)
                    or (index < len(parts) - 1 and not current.is_dir())
                ):
                    raise ValueError("outbox path")
            outbox_path = self._resolve_under(root, outbox_lexical)
            if not outbox_path.is_file() or self._is_reparse(outbox_path):
                raise ValueError("outbox file")
            outbox_raw = self._read_capped_packet(
                outbox_path, "INBOX_EVENT.json"
            )
            if outbox_raw != inbox_raw:
                raise ValueError("outbox bytes")
            receipt_path = self._resolve_under(
                root,
                root / Path(*PurePosixPath(receipt_relative).parts),
            )
            receipt_raw = self._read_capped_packet(
                receipt_path, "RESULT.json"
            )
            receipt = json.loads(receipt_raw)
            if (
                hashlib.sha256(receipt_raw).hexdigest() != result_sha256
                or contract.canonical_json_bytes(receipt) != receipt_raw
                or (
                    receipt_entries is not None
                    and receipt_entries.get(receipt_relative)
                    != result_sha256
                )
            ):
                raise ValueError("receipt identity")
            expected_result = {
                "dispatch_id": dispatch_id,
                "event_id": event_id,
                "packet_sha256": packet_sha256,
                "task_id": task_id,
                "work_order_id": work_order_id,
                "work_order_sha256": work_order_sha256,
                "worker_id": worker_id,
            }
            validated_result, _ = contract.validate_worker_result(
                receipt, expected_result
            )
            if validated_result != receipt:
                raise ValueError("receipt contract")
        except StaleCompletionError:
            raise
        except (
            IdentityError,
            contract.ContractError,
            LoopError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise StaleCompletionError("INBOX_EVENT_INVALID") from exc
        state = self._git_state(base_sha, root)
        staged = set(self._scope_paths(state["staged"]))
        unstaged = set(self._scope_paths(state["unstaged"]))
        untracked = set(self._scope_paths(state["untracked"]))
        committed = set(self._scope_paths(state["committed"]))
        tracked = set(
            self._git_paths(["ls-files", "--", expected_outbox], root)
        )
        if (
            expected_outbox not in untracked
            or expected_outbox in staged
            or expected_outbox in unstaged
            or expected_outbox in committed
            or expected_outbox in tracked
            or self._read_capped_packet(
                outbox_path, "INBOX_EVENT.json"
            )
            != outbox_raw
        ):
            raise StaleCompletionError("RESULT_GIT_INVALID")
        return expected_outbox

    def _validate_consumed_result_ready(
        self,
        worktree_root: Path,
        *,
        event_id: str,
        task_id: str,
        worker_id: str,
        work_order_id: str,
        work_order_sha256: str,
        dispatch_id: str,
        packet_sha256: str,
        result_sha256: str,
        requester_id: str | None = None,
        dispatch_sender_id: str | None = None,
    ) -> str | None:
        """Admit one identity-bound Worker RESULT_READY as system evidence."""
        contract = _load_v7_contract()
        root = worktree_root.resolve(strict=True)
        result_path = self._normal_path(
            f".devad/workers/{worker_id}/receipts/{event_id}.json"
        )
        relative = self._normal_path(
            f".devad/workers/{worker_id}/outbox/{event_id}/RESULT_READY.json"
        )
        lexical = root / Path(*PurePosixPath(relative).parts)
        if not os.path.lexists(lexical):
            return None
        try:
            expected_identity = {
                "dispatch_id": dispatch_id,
                "event_id": event_id,
                "packet_sha256": packet_sha256,
                "result_path": result_path,
                "result_sha256": result_sha256,
                "task_id": task_id,
                "work_order_id": work_order_id,
                "work_order_sha256": work_order_sha256,
                "worker_id": worker_id,
            }
            if requester_id is None:
                requester_id = self._result_ready_row(
                    event_id, expected_identity
                )["sender_id"]
            if (
                dispatch_sender_id is not None
                and requester_id != dispatch_sender_id
            ):
                raise ValueError("result-ready requester")
            current = root
            parts = PurePosixPath(relative).parts
            for index, part in enumerate(parts):
                current = current / part
                if (
                    not os.path.lexists(current)
                    or self._is_reparse(current)
                    or (index < len(parts) - 1 and not current.is_dir())
                ):
                    raise ValueError("result-ready path")
            path = self._resolve_under(root, lexical)
            if not path.is_file() or self._is_reparse(path):
                raise ValueError("result-ready file")
            raw = self._read_capped_packet(path, "RESULT_READY.json")
            signal = contract.validate_result_ready(
                raw,
                hashlib.sha256(raw).hexdigest(),
                expected_identity=expected_identity,
                expected_profile_id=self._ensure_project_profile(),
                expected_requester=requester_id,
            )
            if signal["callback_id"] != self._result_ready_callback_id(
                expected_identity, requester_id
            ):
                raise ValueError("result-ready callback")
        except (
            IdentityError,
            contract.ContractError,
            LoopError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise StaleCompletionError("RESULT_GIT_INVALID") from exc
        state = self._git_state("HEAD", root)
        staged = set(self._scope_paths(state["staged"]))
        unstaged = set(self._scope_paths(state["unstaged"]))
        untracked = set(self._scope_paths(state["untracked"]))
        committed = set(self._scope_paths(state["committed"]))
        tracked = set(self._git_paths(["ls-files", "--", relative], root))
        if (
            relative not in untracked
            or relative in staged
            or relative in unstaged
            or relative in committed
            or relative in tracked
            or self._read_capped_packet(path, "RESULT_READY.json") != raw
        ):
            raise StaleCompletionError("RESULT_GIT_INVALID")
        return relative

    def _validated_consumed_worker_outbox_paths(
        self,
        worktree_root: Path,
        connection: sqlite3.Connection,
        receipt_entries: Mapping[str, str],
    ) -> set[str]:
        root = worktree_root.resolve(strict=True)
        accepted: set[str] = set()
        if not connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' "
            "AND name='inbox'"
        ).fetchone():
            return accepted
        rows = connection.execute(
            "SELECT i.dispatch_id,i.event_id,i.event_sha256,i.payload,"
            "i.status,t.task_id,t.worker_id,t.worktree_id,t.base_sha,"
            "t.status AS task_status,w.path AS worktree_path,"
            "wo.work_order_id,wo.packet_sha256 AS work_order_sha256,"
            "wo.status AS order_status,d.sender_id,d.target_id,d.packet_sha256,"
            "d.status AS dispatch_status,e.event_sha256 AS result_sha256 "
            "FROM inbox i JOIN tasks t ON t.task_id=i.task_id "
            "JOIN worktrees w ON w.worktree_id=t.worktree_id "
            "JOIN work_orders wo ON wo.task_id=t.task_id "
            "JOIN dispatches d ON d.dispatch_id=i.dispatch_id "
            "AND d.task_id=t.task_id JOIN events e ON e.event_id=i.event_id "
            "AND e.task_id=t.task_id AND e.dispatch_id=d.dispatch_id "
            "WHERE i.status='CONSUMED' "
            "AND t.status IN ('COMPLETE','SUPERSEDED') "
            "AND wo.status=t.status AND d.status='COMPLETE'"
        )
        for row in rows:
            try:
                if Path(row["worktree_path"]).resolve(strict=True) != root:
                    continue
            except (OSError, RuntimeError) as exc:
                raise StateNotDurableError(
                    "CONSUMED_WORKER_OUTBOX_INVALID"
                ) from exc
            if row["target_id"] != row["worker_id"]:
                raise StateNotDurableError(
                    "CONSUMED_WORKER_OUTBOX_INVALID"
                )
            relative = self._validate_consumed_worker_outbox(
                root,
                inbox_event={
                    "dispatch_id": row["dispatch_id"],
                    "event_id": row["event_id"],
                    "event_sha256": row["event_sha256"],
                    "payload": row["payload"],
                    "status": row["status"],
                },
                task_id=row["task_id"],
                worker_id=row["worker_id"],
                worktree_id=row["worktree_id"],
                worktree_path=row["worktree_path"],
                base_sha=row["base_sha"],
                work_order_id=row["work_order_id"],
                work_order_sha256=row["work_order_sha256"],
                dispatch_id=row["dispatch_id"],
                packet_sha256=row["packet_sha256"],
                result_sha256=row["result_sha256"],
                receipt_entries=receipt_entries,
                connection=connection,
            )
            if relative is None:
                pass
            elif relative in accepted:
                raise StateNotDurableError("CONSUMED_WORKER_OUTBOX_INVALID")
            else:
                accepted.add(relative)
            result_ready = self._validate_consumed_result_ready(
                root,
                event_id=row["event_id"],
                task_id=row["task_id"],
                worker_id=row["worker_id"],
                work_order_id=row["work_order_id"],
                work_order_sha256=row["work_order_sha256"],
                dispatch_id=row["dispatch_id"],
                packet_sha256=row["packet_sha256"],
                result_sha256=row["result_sha256"],
                requester_id=row["sender_id"],
                dispatch_sender_id=row["sender_id"],
            )
            if result_ready is None:
                continue
            if result_ready in accepted:
                raise StateNotDurableError("CONSUMED_WORKER_OUTBOX_INVALID")
            accepted.add(result_ready)
        return accepted

    def register_actor(self, actor_id: str, role: str, title: str, model: str) -> dict[str, Any]:
        allowed_roles = ("LINX", "THINX", "THINKER", "WORKER", "READER", "CHUNK", "SIDE")
        reserved_stems = (
            {"con", "prn", "aux", "nul"}
            | {f"com{index}" for index in range(1, 10)}
            | {f"lpt{index}" for index in range(1, 10)}
        )
        if (
            not isinstance(actor_id, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", actor_id) is None
            or actor_id.endswith(".")
            or actor_id.split(".", 1)[0] in reserved_stems
        ):
            raise IdentityError("ACTOR_ID_INVALID")
        if not isinstance(role, str):
            raise IdentityError("ACTOR_ROLE_INVALID")
        role = role.upper()
        if role not in allowed_roles:
            raise IdentityError("ACTOR_ROLE_INVALID")
        for value, code in (
            (title, "ACTOR_TITLE_INVALID"),
            (model, "ACTOR_MODEL_INVALID"),
        ):
            if not isinstance(value, str) or not 1 <= len(value) <= 128 or re.search(r"[\x00-\x1f\x7f-\x9f]", value) is not None:
                raise IdentityError(code)
        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            collision = connection.execute(
                "SELECT actor_id FROM actors WHERE actor_id = ? COLLATE NOCASE LIMIT 1",
                (actor_id,),
            ).fetchone()
            if collision is not None and collision[0] != actor_id:
                raise IdentityError("ACTOR_ID_COLLISION")
            old = connection.execute("SELECT role FROM actors WHERE actor_id=?", (actor_id,)).fetchone()
            if old and old[0] != role:
                raise IdentityError("ROLE_IMMUTABLE")
            connection.execute(
                "INSERT OR IGNORE INTO actors(actor_id,role,title,model) VALUES(?,?,?,?)",
                (actor_id, role, title, model),
            )
            warnings = []
            for known in allowed_roles:
                if known != role and re.search(rf"(?<![A-Za-z0-9]){re.escape(known)}(?![A-Za-z0-9])", title, re.IGNORECASE):
                    warnings.append(f"TITLE_ROLE_MISMATCH:{actor_id}:{role}:{title}")
                    break
            return {"status": "REGISTERED", "warnings": warnings}
        return self._mutate(operation)

    def register_worktree(self, worktree_id: str, path: Path | str, repository_id: str) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", worktree_id):
            raise IdentityError("WORKTREE_ID_INVALID")
        normalized = str(Path(path).resolve())
        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            old = connection.execute("SELECT path,repository_id FROM worktrees WHERE worktree_id=?", (worktree_id,)).fetchone()
            if old and (str(Path(old["path"]).resolve()) != normalized or old["repository_id"] != repository_id):
                raise IdentityError("WORKTREE_IMMUTABLE")
            connection.execute(
                "INSERT OR IGNORE INTO worktrees(worktree_id,path,repository_id) VALUES(?,?,?)",
                (worktree_id, normalized, repository_id),
            )
            if old:
                self._historical_receipt_paths(Path(normalized), connection)
            else:
                self._capture_historical_receipts(connection, Path(normalized))
            count_key, root_key = self._receipt_metric_keys(normalized)
            connection.execute("INSERT OR IGNORE INTO metrics(key,value) VALUES(?,'0')", (count_key,))
            connection.execute("INSERT OR IGNORE INTO metrics(key,value) VALUES(?,?)", (root_key, _sha([])))
            return {"status": "REGISTERED", "worktree_id": worktree_id}
        return self._mutate(operation)

    @staticmethod
    def _require_sha256(value: Any, code: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise IdentityError(code)
        return value

    @staticmethod
    def _require_git_sha(value: Any, code: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
            raise IdentityError(code)
        return value

    @staticmethod
    def _validate_feature_dag(
        feature_ids: list[str], dependencies_by_id: Mapping[str, list[str]]
    ) -> None:
        feature_set = set(feature_ids)
        if set(dependencies_by_id) != feature_set:
            raise IdentityError("PROGRAM_FEATURE_DAG_INVALID")
        for feature_id, dependencies in dependencies_by_id.items():
            if (
                not isinstance(dependencies, list)
                or any(
                    not isinstance(dependency, str)
                    or dependency in {".", ".."}
                    or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", dependency)
                    for dependency in dependencies
                )
                or len(dependencies) != len(set(dependencies))
                or feature_id in dependencies
                or not set(dependencies).issubset(feature_set)
            ):
                raise IdentityError("PROGRAM_FEATURE_DAG_INVALID")
        resolved: set[str] = set()
        remaining = {
            feature_id: set(dependencies_by_id[feature_id])
            for feature_id in feature_ids
        }
        while remaining:
            ready = sorted(
                feature_id
                for feature_id, dependencies in remaining.items()
                if dependencies.issubset(resolved)
            )
            if not ready:
                raise IdentityError("PROGRAM_FEATURE_DAG_INVALID")
            for feature_id in ready:
                remaining.pop(feature_id)
                resolved.add(feature_id)

    def import_program(
        self,
        program: dict[str, Any],
        *,
        source_git_sha: str,
        source_root: Path | str,
        source_root_sha256: str,
        metadata_by_path: Mapping[str, Mapping[str, Any]] | None = None,
        required_source_classes: tuple[str, ...] | list[str] = (),
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        importer = _load_program_import()
        if not isinstance(program, dict) or program.get("schema") != "x9-loop-program-v1":
            raise IdentityError("PROGRAM_SCHEMA_INVALID")
        program_payload = dict(program)
        feature_packets = program_payload.pop("feature_packets", None)
        reserved = {
            "coverage_shard_refs",
            "coverage_summary_ref",
            "feature_index",
            "inventory_ref",
            "source_git_sha",
            "source_root_path",
            "source_root_sha256",
            "writer",
        }
        if reserved.intersection(program_payload):
            raise IdentityError("PROGRAM_FIELDS_RESERVED")
        program_id = program_payload.get("program_id")
        if (
            not isinstance(program_id, str)
            or program_id in {".", ".."}
            or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", program_id)
        ):
            raise IdentityError("PROGRAM_ID_INVALID")
        feature_ids = program_payload.get("features")
        if (
            not isinstance(feature_ids, list)
            or not feature_ids
            or any(
                not isinstance(item, str)
                or item in {".", ".."}
                or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", item)
                for item in feature_ids
            )
            or len(feature_ids) != len(set(feature_ids))
            or len(feature_ids) != len({item.casefold() for item in feature_ids})
        ):
            raise IdentityError("PROGRAM_FEATURES_INVALID")
        if (
            not isinstance(feature_packets, list)
            or len(feature_packets) != len(feature_ids)
            or any(not isinstance(feature, dict) for feature in feature_packets)
        ):
            raise IdentityError("PROGRAM_FEATURE_PACKETS_INVALID")
        normalized_features: dict[str, dict[str, Any]] = {}
        feature_raw_by_id: dict[str, bytes] = {}
        dependencies_by_id: dict[str, list[str]] = {}
        for supplied in feature_packets:
            feature = dict(supplied)
            try:
                contract.validate_context_complete(feature)
                self._validate_project_context(feature, phase="pre-plan")
                raw_feature = contract.canonical_json_bytes(feature)
                contract.validate_packet_cap("FEATURE_PACKET.json", raw_feature)
            except contract.ContractError as exc:
                raise IdentityError(exc.code) from exc
            feature_id = feature.get("feature_id")
            if (
                not isinstance(feature_id, str)
                or feature_id not in feature_ids
                or feature_id in normalized_features
            ):
                raise IdentityError("PROGRAM_FEATURE_PACKETS_INVALID")
            dependencies = feature.get("dependencies")
            if not isinstance(dependencies, list):
                raise IdentityError("PROGRAM_FEATURE_DAG_INVALID")
            normalized_features[feature_id] = feature
            feature_raw_by_id[feature_id] = raw_feature
            dependencies_by_id[feature_id] = list(dependencies)
        if set(normalized_features) != set(feature_ids):
            raise IdentityError("PROGRAM_FEATURE_PACKETS_INVALID")
        self._validate_feature_dag(feature_ids, dependencies_by_id)
        self._require_git_sha(source_git_sha, "PROGRAM_GIT_SHA_INVALID")
        self._require_sha256(source_root_sha256, "PROGRAM_ROOT_SHA_INVALID")
        source_candidate = Path(source_root)
        if not source_candidate.is_absolute():
            source_candidate = self.repo / source_candidate
        try:
            if self._is_reparse(source_candidate):
                raise ValueError("reparse source root")
            source_path = self._resolve_under(self.repo, source_candidate)
            if not source_path.is_dir():
                raise ValueError("source root is not a directory")
            source_root_path = contract.canonical_repo_path(
                source_path.relative_to(self.repo).as_posix()
            )
        except (OSError, ValueError, RuntimeError, contract.ContractError) as exc:
            raise IdentityError("PROGRAM_SOURCE_ROOT_INVALID") from exc
        try:
            artifacts = importer.build_import_artifacts(
                source_path,
                metadata_by_path=metadata_by_path,
                required_source_classes=required_source_classes,
            )
        except importer.ProgramImportError as exc:
            raise IdentityError("PROGRAM_IMPORT_INVALID") from exc
        actual_root = artifacts["inventory_root_sha256"]
        if actual_root != source_root_sha256:
            raise IdentityError("PROGRAM_ROOT_HASH_MISMATCH")
        try:
            importer.verify_inventory(
                source_path,
                artifacts["rows"],
                expected_root_sha256=actual_root,
            )
        except importer.ProgramImportError as exc:
            raise IdentityError("PROGRAM_SOURCE_ROOT_DRIFT") from exc
        covered_features = {
            feature_id
            for row in artifacts["rows"]
            for feature_id in row["feature_ids"]
        }
        coverage = json.loads(artifacts["coverage_summary"])
        if (
            covered_features != set(feature_ids)
            or coverage.get("inventory_root_sha256") != actual_root
            or coverage.get("conflicts")
            or coverage.get("missing_required_source_classes")
        ):
            raise IdentityError("PROGRAM_FEATURE_COVERAGE_INVALID")
        program_root = contract.canonical_repo_path(
            f".devad/manager/loop-lite/programs/{program_id}"
        )
        inventory_relative = contract.canonical_repo_path(
            f"{program_root}/IMPORT_INVENTORY.jsonl"
        )
        coverage_relative = contract.canonical_repo_path(
            f"{program_root}/IMPORT_COVERAGE_SUMMARY.json"
        )
        shard_refs = [
            {
                "index": index,
                "path": contract.canonical_repo_path(
                    f"{program_root}/coverage/{index:05d}.jsonl"
                ),
                "sha256": contract.sha256_bytes(shard),
            }
            for index, shard in enumerate(artifacts["shards"])
        ]
        feature_index: list[dict[str, Any]] = []
        feature_writes: list[tuple[Path, bytes]] = []
        for feature_id in sorted(feature_ids):
            raw_feature = feature_raw_by_id[feature_id]
            feature_relative = contract.canonical_repo_path(
                f"{program_root}/features/{feature_id}/FEATURE_PACKET.json"
            )
            feature_index.append(
                {
                    "dependencies": sorted(dependencies_by_id[feature_id]),
                    "feature_id": feature_id,
                    "feature_packet_path": feature_relative,
                    "feature_packet_sha256": contract.sha256_bytes(raw_feature),
                    "state": "READY" if not dependencies_by_id[feature_id] else "BLOCKED",
                }
            )
            feature_writes.append(
                (
                    self.repo / Path(*PurePosixPath(feature_relative).parts),
                    raw_feature,
                )
            )
        packet = dict(program_payload)
        packet["features"] = sorted(feature_ids)
        packet["feature_index"] = feature_index
        packet["source_git_sha"] = source_git_sha
        packet["source_root_path"] = source_root_path
        packet["source_root_sha256"] = actual_root
        packet["inventory_ref"] = {
            "path": inventory_relative,
            "sha256": contract.sha256_bytes(artifacts["inventory_jsonl"]),
        }
        packet["coverage_summary_ref"] = {
            "path": coverage_relative,
            "sha256": contract.sha256_bytes(artifacts["coverage_summary"]),
        }
        packet["coverage_shard_refs"] = shard_refs
        packet["writer"] = "Controller"
        raw = contract.canonical_json_bytes(packet)
        contract.validate_packet_cap("PROGRAM_PACKET.json", raw)
        packet_sha256 = contract.sha256_bytes(raw)
        relative = contract.canonical_repo_path(
            f"{program_root}/PROGRAM_PACKET.json"
        )
        path = self.repo / Path(*PurePosixPath(relative).parts)
        artifact_writes = [
            (
                self.repo / Path(*PurePosixPath(inventory_relative).parts),
                artifacts["inventory_jsonl"],
            ),
            (
                self.repo / Path(*PurePosixPath(coverage_relative).parts),
                artifacts["coverage_summary"],
            ),
            *[
                (
                    self.repo / Path(*PurePosixPath(ref["path"]).parts),
                    shard,
                )
                for ref, shard in zip(shard_refs, artifacts["shards"])
            ],
            *feature_writes,
            (path, raw),
        ]
        if any(target.exists() and target.read_bytes() != data for target, data in artifact_writes):
            raise IdentityError("PROGRAM_ID_DRIFT")

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            old = connection.execute(
                "SELECT packet_sha256 FROM programs WHERE program_id=?", (program_id,)
            ).fetchone()
            if old and old["packet_sha256"] != packet_sha256:
                raise IdentityError("PROGRAM_ID_DRIFT")
            for target, data in artifact_writes:
                self._atomic_state_write(target, data)
            connection.execute(
                "INSERT INTO programs(program_id,packet_path,packet_sha256,source_git_sha,source_root_sha256,status,imported_at) "
                "VALUES(?,?,?,?,?,'ACTIVE',?) ON CONFLICT(program_id) DO NOTHING",
                (program_id, relative, packet_sha256, source_git_sha, actual_root, self.now_fn()),
            )
            return {
                "status": "IMPORTED",
                "program_id": program_id,
                "packet_path": relative,
                "packet_sha256": packet_sha256,
                "source_root_sha256": actual_root,
            }

        return self._mutate(operation)

    def _verify_program_import(
        self, packet: Mapping[str, Any]
    ) -> list[dict[str, Any]]:
        contract = _load_v7_contract()
        importer = _load_program_import()

        def read_ref(ref: Any, fields: set[str]) -> tuple[str, bytes]:
            if not isinstance(ref, Mapping) or set(ref) != fields:
                raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID")
            relative = contract.canonical_repo_path(ref["path"])
            self._require_sha256(ref["sha256"], "PROGRAM_IMPORT_ARTIFACT_INVALID")
            path = self._resolve_under(
                self.repo, self.repo / Path(*PurePosixPath(relative).parts)
            )
            raw_ref = path.read_bytes()
            if contract.sha256_bytes(raw_ref) != ref["sha256"]:
                raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID")
            return relative, raw_ref

        try:
            _, inventory_raw = read_ref(
                packet.get("inventory_ref"), {"path", "sha256"}
            )
            _, coverage_raw = read_ref(
                packet.get("coverage_summary_ref"), {"path", "sha256"}
            )
            shard_refs = packet.get("coverage_shard_refs")
            if not isinstance(shard_refs, list) or not shard_refs:
                raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID")
            shards: list[bytes] = []
            for expected_index, ref in enumerate(shard_refs):
                if (
                    not isinstance(ref, Mapping)
                    or set(ref) != {"index", "path", "sha256"}
                    or ref["index"] != expected_index
                ):
                    raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID")
                _, shard = read_ref(ref, {"index", "path", "sha256"})
                shards.append(shard)
            rows = [
                json.loads(line)
                for line in inventory_raw.decode("utf-8").splitlines()
            ]
            normalized_rows = importer.validate_inventory_rows(rows)
            if (
                not inventory_raw
                or importer.inventory_jsonl_bytes(normalized_rows) != inventory_raw
                or b"".join(shards) != inventory_raw
            ):
                raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID")
            coverage = json.loads(coverage_raw)
            if (
                importer.canonical_json_bytes(coverage) != coverage_raw
                or importer.build_coverage_summary(normalized_rows, shards) != coverage_raw
                or coverage.get("inventory_root_sha256")
                != packet.get("source_root_sha256")
            ):
                raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID")
            feature_ids = packet.get("features")
            if (
                not isinstance(feature_ids, list)
                or not feature_ids
                or any(
                    not isinstance(feature_id, str)
                    or feature_id in {".", ".."}
                    or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", feature_id)
                    for feature_id in feature_ids
                )
                or feature_ids != sorted(feature_ids)
                or len(feature_ids) != len(set(feature_ids))
                or len(feature_ids) != len({item.casefold() for item in feature_ids})
            ):
                raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
            covered_features = {
                feature_id
                for row in normalized_rows
                for feature_id in row["feature_ids"]
            }
            if covered_features != set(feature_ids):
                raise IdentityError("PROGRAM_FEATURE_COVERAGE_INVALID")
            feature_index = packet.get("feature_index")
            if not isinstance(feature_index, list) or len(feature_index) != len(feature_ids):
                raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
            program_id = packet.get("program_id")
            if (
                not isinstance(program_id, str)
                or program_id in {".", ".."}
                or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", program_id)
            ):
                raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
            assignments: list[dict[str, Any]] = []
            dependencies_by_id: dict[str, list[str]] = {}
            seen_feature_ids: set[str] = set()
            for entry in feature_index:
                if not isinstance(entry, Mapping) or set(entry) != {
                    "dependencies",
                    "feature_id",
                    "feature_packet_path",
                    "feature_packet_sha256",
                    "state",
                }:
                    raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
                feature_id = entry["feature_id"]
                if feature_id not in feature_ids or feature_id in seen_feature_ids:
                    raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
                seen_feature_ids.add(feature_id)
                dependencies = entry["dependencies"]
                if (
                    not isinstance(dependencies, list)
                    or dependencies != sorted(dependencies)
                    or len(dependencies) != len(set(dependencies))
                ):
                    raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
                expected_state = "READY" if not dependencies else "BLOCKED"
                if entry["state"] != expected_state:
                    raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
                feature_relative = contract.canonical_repo_path(
                    entry["feature_packet_path"]
                )
                expected_relative = (
                    f".devad/manager/loop-lite/programs/{program_id}/features/"
                    f"{feature_id}/FEATURE_PACKET.json"
                )
                if feature_relative != expected_relative:
                    raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
                feature_sha256 = self._require_sha256(
                    entry["feature_packet_sha256"],
                    "PROGRAM_FEATURE_INDEX_INVALID",
                )
                feature_path = self._resolve_under(
                    self.repo,
                    self.repo / Path(*PurePosixPath(feature_relative).parts),
                )
                feature_raw = feature_path.read_bytes()
                if contract.sha256_bytes(feature_raw) != feature_sha256:
                    raise IdentityError("FEATURE_PACKET_DRIFT")
                feature = json.loads(feature_raw.decode("utf-8"))
                if (
                    not isinstance(feature, dict)
                    or contract.canonical_json_bytes(feature) != feature_raw
                ):
                    raise IdentityError("FEATURE_PACKET_DRIFT")
                contract.validate_packet_cap("FEATURE_PACKET.json", feature_raw)
                contract.validate_context_complete(feature)
                self._validate_project_context(feature, phase="pre-plan")
                if (
                    feature.get("feature_id") != feature_id
                    or sorted(feature.get("dependencies", [])) != dependencies
                ):
                    raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
                assignment = dict(feature)
                assignment["path"] = feature_relative
                assignment["sha256"] = feature_sha256
                assignments.append(assignment)
                dependencies_by_id[feature_id] = list(dependencies)
            if seen_feature_ids != set(feature_ids):
                raise IdentityError("PROGRAM_FEATURE_INDEX_INVALID")
            self._validate_feature_dag(feature_ids, dependencies_by_id)
            source_relative = contract.canonical_repo_path(
                packet.get("source_root_path")
            )
            source_candidate = self.repo / Path(
                *PurePosixPath(source_relative).parts
            )
            if self._is_reparse(source_candidate):
                raise IdentityError("PROGRAM_SOURCE_ROOT_DRIFT")
            source_path = self._resolve_under(self.repo, source_candidate)
            if not source_path.is_dir():
                raise IdentityError("PROGRAM_SOURCE_ROOT_DRIFT")
        except IdentityError:
            raise
        except (
            OSError, UnicodeDecodeError, ValueError, RuntimeError,
            json.JSONDecodeError, contract.ContractError,
            importer.ProgramImportError,
        ) as exc:
            raise IdentityError("PROGRAM_IMPORT_ARTIFACT_INVALID") from exc
        try:
            importer.verify_inventory(
                source_path,
                normalized_rows,
                expected_root_sha256=packet["source_root_sha256"],
            )
        except importer.ProgramImportError as exc:
            raise IdentityError("PROGRAM_SOURCE_ROOT_DRIFT") from exc
        return sorted(assignments, key=lambda feature: feature["feature_id"])

    def _v7_action(
        self,
        dispatch_id: str,
        task_id: str,
        worker_id: str,
        work_order_id: str,
        work_order_path: str,
        work_order_sha256: str,
    ) -> dict[str, Any]:
        return {
            "action": "SEND_WORK_ORDER",
            "action_id": "act-" + str(uuid.uuid4()),
            "attempt": 1,
            "dispatch_id": dispatch_id,
            "must_record_transport": True,
            "project_profile_id": self._ensure_project_profile(),
            "schema": "x9-loop-action-v2",
            "target_actor_id": worker_id,
            "target_role": "WORKER",
            "task_id": task_id,
            "work_order_id": work_order_id,
            "work_order_path": work_order_path,
            "work_order_sha256": work_order_sha256,
        }

    def _verify_candidate_handoff(
        self,
        candidate_handoff: Mapping[str, Any],
        connection: sqlite3.Connection,
    ) -> tuple[Path, set[str]]:
        contract = _load_v7_contract()
        try:
            handoff = contract.validate_candidate_handoff(candidate_handoff)
        except contract.ContractError as exc:
            raise IdentityError(exc.code) from exc
        source = connection.execute(
            "SELECT t.status AS task_status,t.worker_id,t.worktree_id,"
            "t.base_sha,w.path AS worktree_path,wo.status AS order_status "
            "FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id "
            "JOIN work_orders wo ON wo.task_id=t.task_id "
            "AND wo.work_order_id=? WHERE t.task_id=?",
            (
                handoff["source_work_order_id"],
                handoff["source_task_id"],
            ),
        ).fetchone()
        event = connection.execute(
            "SELECT event_sha256,dispatch_id FROM events "
            "WHERE event_id=? AND task_id=?",
            (handoff["source_event_id"], handoff["source_task_id"]),
        ).fetchone()
        dispatch = (
            connection.execute(
                "SELECT status FROM dispatches WHERE dispatch_id=?",
                (event["dispatch_id"],),
            ).fetchone()
            if event is not None
            else None
        )
        if (
            source is None
            or source["task_status"] != "COMPLETE"
            or source["order_status"] != "COMPLETE"
            or source["worker_id"] != handoff["source_worker_id"]
            or source["worktree_id"] != handoff["source_worktree_id"]
            or source["base_sha"] != handoff["source_base_sha"]
            or event is None
            or event["event_sha256"] != handoff["source_result_sha256"]
            or dispatch is None
            or dispatch["status"] != "COMPLETE"
        ):
            raise StaleCompletionError("CANDIDATE_HANDOFF_IDENTITY_MISMATCH")
        try:
            source_root = Path(source["worktree_path"]).resolve(strict=True)
            declared_root = Path(
                handoff["source_worktree_path"]
            ).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise IdentityError("CANDIDATE_HANDOFF_WORKTREE_INVALID") from exc
        if (
            source_root != declared_root
            or not source_root.is_dir()
            or self._is_reparse(source_root)
        ):
            raise IdentityError("CANDIDATE_HANDOFF_WORKTREE_INVALID")
        expected_receipt = self._normal_path(
            f".devad/workers/{source['worker_id']}/receipts/"
            f"{handoff['source_event_id']}.json"
        )
        receipt_entries = self._validated_receipt_entries(
            source_root, connection
        )
        if receipt_entries.get(expected_receipt) != handoff["source_result_sha256"]:
            raise StaleCompletionError("CANDIDATE_HANDOFF_RECEIPT_MISMATCH")
        candidate_paths = {
            self._normal_path(item["path"])
            for item in handoff["files"]
        }
        try:
            receipt_path = self._resolve_under(
                source_root,
                source_root / Path(*PurePosixPath(expected_receipt).parts),
            )
            receipt_raw = receipt_path.read_bytes()
            source_receipt = json.loads(receipt_raw)
            receipt_changed = {
                self._normal_path(path)
                for path in source_receipt["changed_files"]
            }
        except (
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise StaleCompletionError(
                "CANDIDATE_HANDOFF_RECEIPT_MISMATCH"
            ) from exc
        if (
            hashlib.sha256(receipt_raw).hexdigest()
            != handoff["source_result_sha256"]
            or source_receipt.get("outcome") != "SUCCESS_CANDIDATE"
            or source_receipt.get("event_id") != handoff["source_event_id"]
            or source_receipt.get("task_id") != handoff["source_task_id"]
            or source_receipt.get("worker_id") != handoff["source_worker_id"]
            or source_receipt.get("work_order_id")
            != handoff["source_work_order_id"]
            or receipt_changed != candidate_paths
        ):
            raise StaleCompletionError("CANDIDATE_HANDOFF_RECEIPT_MISMATCH")
        head = self._run_git(["rev-parse", "HEAD"], source_root)
        if head.returncode or head.stdout.strip() != handoff["source_base_sha"]:
            raise StaleCompletionError("CANDIDATE_HANDOFF_GIT_DRIFT")
        for item in handoff["files"]:
            relative = self._normal_path(item["path"])
            lexical = source_root / Path(*PurePosixPath(relative).parts)
            if item["state"] == "PRESENT":
                try:
                    candidate = self._resolve_under(source_root, lexical)
                except (OSError, RuntimeError, ValueError) as exc:
                    raise StaleCompletionError("CANDIDATE_HANDOFF_FILE_DRIFT") from exc
                if (
                    self._is_reparse(candidate)
                    or not candidate.is_file()
                    or self._digest_file(candidate) != item["sha256"]
                ):
                    raise StaleCompletionError("CANDIDATE_HANDOFF_FILE_DRIFT")
            else:
                try:
                    self._resolve_under(source_root, lexical.parent)
                except (OSError, RuntimeError, ValueError) as exc:
                    raise StaleCompletionError("CANDIDATE_HANDOFF_FILE_DRIFT") from exc
                if os.path.lexists(lexical):
                    raise StaleCompletionError("CANDIDATE_HANDOFF_FILE_DRIFT")
        evidence = self._historical_receipt_paths(source_root, connection)
        evidence.update(receipt_entries)
        evidence.update(
            self._validated_receipt_proof_paths(source_root, receipt_entries)
        )
        evidence.update(
            self._registered_rejected_receipt_paths(source_root, connection)
        )
        evidence.update(
            self._validated_consumed_worker_outbox_paths(
                source_root, connection, receipt_entries
            )
        )
        source_state = self._git_state(handoff["source_base_sha"], source_root)
        source_dirty = {
            path
            for name in ("staged", "unstaged", "untracked", "committed")
            for path in self._scope_paths(source_state[name])
            if path not in evidence
        }
        if source_dirty != candidate_paths:
            raise TaskNotReadyError("WORKTREE_NOT_CLEAN")
        return source_root, candidate_paths

    def _verify_v7_worktree_preflight(
        self,
        worktree_path: str | Path,
        base_sha: str,
        connection: sqlite3.Connection,
        candidate_handoff: Mapping[str, Any] | None = None,
    ) -> None:
        source_root: Path | None = None
        candidate_paths: set[str] = set()
        if candidate_handoff is not None:
            source_root, candidate_paths = self._verify_candidate_handoff(
                candidate_handoff, connection
            )
        try:
            root = Path(worktree_path).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise IdentityError("WORKTREE_IDENTITY_INVALID") from exc
        if not root.is_dir() or self._is_reparse(root):
            raise IdentityError("WORKTREE_IDENTITY_INVALID")
        top = self._run_git(["rev-parse", "--show-toplevel"], root)
        if top.returncode:
            raise IdentityError("WORKTREE_IDENTITY_INVALID")
        try:
            git_root = Path(top.stdout.strip()).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise IdentityError("WORKTREE_IDENTITY_INVALID") from exc
        if git_root != root:
            raise IdentityError("WORKTREE_IDENTITY_INVALID")
        head = self._run_git(["rev-parse", "HEAD"], root)
        if head.returncode or head.stdout.strip() != base_sha:
            raise IdentityError("WORKTREE_BASE_SHA_MISMATCH")
        state = self._git_state(base_sha, root)
        evidence = self._historical_receipt_paths(root, connection)
        receipt_entries = self._validated_receipt_entries(root, connection)
        evidence.update(receipt_entries)
        evidence.update(
            self._validated_receipt_proof_paths(root, receipt_entries)
        )
        evidence.update(
            self._validated_consumed_worker_outbox_paths(
                root, connection, receipt_entries
            )
        )
        if source_root is not None and root == source_root:
            evidence.update(candidate_paths)
        dirty = {
            path
            for name in ("staged", "unstaged", "untracked", "committed")
            for path in self._scope_paths(state[name])
            if path not in evidence
        }
        if dirty:
            raise TaskNotReadyError("WORKTREE_NOT_CLEAN")

    def _admit_active_order_capacity(
        self, connection: sqlite3.Connection, baseline_root_size: int
    ) -> None:
        capacity = _load_snapshot_capacity()
        active_count = connection.execute(
            "SELECT COUNT(*) FROM work_orders wo "
            "JOIN tasks t ON t.task_id=wo.task_id "
            "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') "
            "AND wo.status NOT IN ('COMPLETE','EXPIRED','SUPERSEDED')"
        ).fetchone()[0]
        if active_count > capacity.ACTIVE_ORDER_CAP:
            raise TaskNotReadyError("ACTIVE_ORDER_CAPACITY")
        bundle = self._snapshot_bundle(
            connection,
            generation=self._generation(connection) + 1,
        )
        candidate_size = len(bundle["root_raw"])
        delta = candidate_size - baseline_root_size
        reserve = (
            capacity.ACTIVE_ORDER_CAP - active_count
        ) * capacity.ACTIVE_ORDER_RESERVATION_BYTES
        if (
            delta > capacity.ACTIVE_ORDER_RESERVATION_BYTES
            or candidate_size + reserve > capacity.ROOT_CAP_BYTES
        ):
            raise TaskNotReadyError("ACTIVE_ORDER_CAPACITY")
    def create_work_order(
        self,
        *,
        program_id: str,
        stop: dict[str, Any],
        linx_id: str,
        action_class: str,
        _connection: sqlite3.Connection | None = None,
        _candidate_handoff: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if _connection is None:
            self._assert_durable()
        contract = _load_v7_contract()
        owns_connection = _connection is None
        connection = self._connect() if owns_connection else _connection
        assert connection is not None
        try:
            program = connection.execute(
                "SELECT * FROM programs WHERE program_id=? AND status='ACTIVE'", (program_id,)
            ).fetchone()
            linx = connection.execute("SELECT role FROM actors WHERE actor_id=?", (linx_id,)).fetchone()
        finally:
            if owns_connection:
                connection.close()
        if not program:
            raise IdentityError("PROGRAM_UNKNOWN")
        if not linx or linx["role"] != "LINX":
            raise IdentityError("SENDER_IDENTITY_INVALID")
        program_path = self.repo / Path(*PurePosixPath(program["packet_path"]).parts)
        try:
            program_raw = program_path.read_bytes()
            parsed_program = json.loads(program_raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IdentityError("PROGRAM_PACKET_INVALID") from exc
        if (
            contract.sha256_bytes(program_raw) != program["packet_sha256"]
            or contract.canonical_json_bytes(parsed_program) != program_raw
        ):
            raise IdentityError("PROGRAM_PACKET_DRIFT")
        feature_assignments = self._verify_program_import(parsed_program)
        for feature in feature_assignments:
            self._validate_project_context(feature, phase="pre-work-order")
        work_order_id = "wo-" + str(uuid.uuid4())
        task_id = "task-" + work_order_id[3:]
        work_order_path = f".devad/manager/loop-lite/runtime/work-orders/{work_order_id}/WORK_ORDER.json"
        order_path = self.repo / Path(*PurePosixPath(work_order_path).parts)

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            baseline_root_size = len(
                self._snapshot_bundle(
                    connection,
                    generation=self._generation(connection) + 1,
                )["root_raw"]
            )
            authoritative_ids = {
                feature["feature_id"] for feature in feature_assignments
            }
            assigned: set[str] = set()
            completed: set[str] = set()
            prior_orders = connection.execute(
                "SELECT wo.work_order_id,wo.packet_path,wo.packet_sha256,wo.status AS work_order_status,t.status "
                "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                "WHERE wo.program_id=? AND wo.status!='SUPERSEDED' "
                "ORDER BY wo.created_at,wo.work_order_id",
                (program_id,),
            )
            for row in prior_orders:
                prior_path = self.repo / Path(
                    *PurePosixPath(row["packet_path"]).parts
                )
                try:
                    prior_raw = prior_path.read_bytes()
                    prior_order = json.loads(prior_raw.decode("utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise IdentityError("PROGRAM_FEATURE_ASSIGNMENT_INVALID") from exc
                if (
                    contract.sha256_bytes(prior_raw) != row["packet_sha256"]
                    or contract.canonical_json_bytes(prior_order) != prior_raw
                    or prior_order.get("program_packet_path") != program["packet_path"]
                    or prior_order.get("program_packet_sha256") != program["packet_sha256"]
                ):
                    raise IdentityError("PROGRAM_FEATURE_ASSIGNMENT_INVALID")
                refs = prior_order.get("feature_packet_refs")
                if not isinstance(refs, list) or not refs:
                    raise IdentityError("PROGRAM_FEATURE_ASSIGNMENT_INVALID")
                for ref in refs:
                    feature_id = ref.get("feature_id") if isinstance(ref, Mapping) else None
                    if feature_id not in authoritative_ids or feature_id in assigned:
                        raise IdentityError("PROGRAM_FEATURE_ASSIGNMENT_INVALID")
                    assigned.add(feature_id)
                    if row["status"] == "COMPLETE":
                        completed.add(feature_id)
                if (
                    row["status"] not in {"COMPLETE", "SUPERSEDED"}
                    and row["work_order_status"] not in {"COMPLETE", "EXPIRED", "SUPERSEDED"}
                    and prior_order.get("action_class") == action_class
                    and isinstance(prior_order.get("autonomy_contract"), Mapping)
                ):
                    selected_features = [
                        feature for feature in feature_assignments
                        if feature["feature_id"] in {
                            ref["feature_id"] for ref in refs
                        }
                    ]
                    try:
                        candidate_mission = contract.mission_identity(
                            action_class=action_class,
                            features=selected_features,
                            program_packet_ref={
                                "path": program["packet_path"],
                                "sha256": program["packet_sha256"],
                            },
                            stop=stop,
                        )
                    except contract.ContractError as exc:
                        raise IdentityError(exc.code) from exc
                    if (
                        prior_order["autonomy_contract"].get("mission_sha256")
                        == candidate_mission
                    ):
                        dispatch = connection.execute(
                            "SELECT dispatch_id FROM dispatches WHERE task_id=? "
                            "ORDER BY rowid DESC LIMIT 1",
                            (prior_order["task_id"],),
                        ).fetchone()
                        return {
                            "status": "ACTIVE_WORK_ORDER_REUSED",
                            "dispatch_id": dispatch["dispatch_id"] if dispatch else None,
                            "task_id": prior_order["task_id"],
                            "work_order_id": row["work_order_id"],
                            "work_order_path": row["packet_path"],
                            "work_order_sha256": row["packet_sha256"],
                        }

            capacity = _load_snapshot_capacity()
            active_order_count = connection.execute(
                "SELECT COUNT(*) FROM work_orders wo "
                "JOIN tasks t ON t.task_id=wo.task_id "
                "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') "
                "AND wo.status NOT IN ('COMPLETE','EXPIRED','SUPERSEDED')"
            ).fetchone()[0]
            if active_order_count >= capacity.ACTIVE_ORDER_CAP:
                raise TaskNotReadyError("ACTIVE_ORDER_CAPACITY")
            unassigned = [
                feature
                for feature in feature_assignments
                if feature["feature_id"] not in assigned
            ]
            ready = [
                feature
                for feature in unassigned
                if set(feature["dependencies"]).issubset(completed)
            ]
            if not ready:
                if not unassigned:
                    raise TaskNotReadyError("PROGRAM_COMPLETE")
                raise TaskNotReadyError("DEPENDENCY_NOT_COMPLETE")

            def build_order(
                selected: list[dict[str, Any]],
            ) -> tuple[dict[str, Any], bytes, str]:
                try:
                    return contract.build_work_order(
                        action_class=action_class,
                        created_at=self.now_fn(),
                        features=selected,
                        program_packet_ref={
                            "path": program["packet_path"],
                            "sha256": program["packet_sha256"],
                        },
                        source_git_sha=program["source_git_sha"],
                        source_root_sha256=program["source_root_sha256"],
                        stop=stop,
                        task_id=task_id,
                        work_order_id=work_order_id,
                        candidate_handoff=_candidate_handoff,
                    )
                except contract.ContractError as exc:
                    raise IdentityError(exc.code) from exc

            selected = [ready[0]]
            order, raw, work_order_sha256 = build_order(selected)
            if ready[0].get("atomic_compatible") is True:
                for candidate in ready[1:]:
                    try:
                        pair_order, pair_raw, pair_sha256 = contract.build_work_order(
                            action_class=action_class,
                            created_at=order["created_at"],
                            features=[ready[0], candidate],
                            program_packet_ref={
                                "path": program["packet_path"],
                                "sha256": program["packet_sha256"],
                            },
                            source_git_sha=program["source_git_sha"],
                            source_root_sha256=program["source_root_sha256"],
                            stop=stop,
                            task_id=task_id,
                            work_order_id=work_order_id,
                            candidate_handoff=_candidate_handoff,
                        )
                    except contract.ContractError as exc:
                        if exc.code == "TWO_FEATURE_NOT_ATOMIC":
                            continue
                        raise IdentityError(exc.code) from exc
                    selected = [ready[0], candidate]
                    order, raw, work_order_sha256 = (
                        pair_order,
                        pair_raw,
                        pair_sha256,
                    )
                    break

            first = selected[0]
            worker_id = first["worker_id"]
            worker = connection.execute("SELECT role FROM actors WHERE actor_id=?", (worker_id,)).fetchone()
            worktree = connection.execute(
                "SELECT path FROM worktrees WHERE worktree_id=?", (first["worktree_id"],)
            ).fetchone()
            if not worker or worker["role"] != "WORKER":
                raise IdentityError("WORKER_IDENTITY_INVALID")
            if not worktree or str(Path(worktree["path"]).resolve()) != str(Path(first["worktree_path"]).resolve()):
                raise IdentityError("WORKTREE_IDENTITY_INVALID")
            claims = [
                (
                    contract.canonical_repo_path(row["path"]),
                    self._claim_kind(row.get("kind", "file")),
                )
                for row in order["claims"]
            ]
            candidate = order.get("candidate_handoff")
            if candidate is not None:
                if candidate["source_worker_id"] != worker_id:
                    raise IdentityError("CANDIDATE_HANDOFF_WORKER_MISMATCH")
                for item in candidate["files"]:
                    if not any(
                        self._overlap(item["path"], "file", path, kind)
                        for path, kind in claims
                    ):
                        raise ScopeBreachError(
                            f"CANDIDATE_HANDOFF_CLAIM_MISMATCH:{item['path']}"
                        )
            self._verify_v7_worktree_preflight(
                worktree["path"], first["base_sha"], connection, candidate
            )
            active = connection.execute(
                "SELECT 1 FROM dispatches d JOIN tasks t ON t.task_id=d.task_id "
                "WHERE t.worker_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED') AND d.status IN ('PREPARED','DISPATCHED') LIMIT 1",
                (worker_id,),
            ).fetchone()
            if active:
                raise TaskNotReadyError("WORKER_ACTIVE_DISPATCH")
            resources = contract.canonical_resource_keys(order["resources"])
            for existing in connection.execute(
                "SELECT c.task_id,c.path,c.kind FROM claims c JOIN tasks t ON t.task_id=c.task_id WHERE t.status NOT IN ('COMPLETE','SUPERSEDED')"
            ):
                for path, kind in claims:
                    if self._overlap(path, kind, existing["path"], existing["kind"]):
                        raise ClaimConflictError(f"CLAIM_CONFLICT:{path}:{existing['task_id']}")
            for resource in resources:
                old = connection.execute(
                    "SELECT r.task_id FROM resources r JOIN tasks t ON t.task_id=r.task_id "
                    "WHERE r.resource=? AND t.status NOT IN ('COMPLETE','SUPERSEDED') LIMIT 1",
                    (resource,),
                ).fetchone()
                if old:
                    raise ResourceConflictError(f"RESOURCE_CONFLICT:{resource}:{old[0]}")
            finish_line = first["finish_line"]
            finish_line_text = (
                finish_line
                if isinstance(finish_line, str)
                else _json(list(finish_line))
            )
            connection.execute(
                "INSERT INTO tasks(task_id,worker_id,worktree_id,base_sha,owner_packet_path,owner_packet_sha256,dependencies,finish_line,status) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (task_id, worker_id, first["worktree_id"], first["base_sha"], work_order_path, work_order_sha256, _json(sorted(first["dependencies"])), finish_line_text, "REGISTERED"),
            )
            connection.executemany("INSERT INTO claims(task_id,path,kind) VALUES(?,?,?)", [(task_id, path, kind) for path, kind in claims])
            connection.executemany("INSERT INTO resources(task_id,resource) VALUES(?,?)", [(task_id, item) for item in resources])
            connection.execute(
                "INSERT INTO work_orders VALUES(?,?,?,?,?,?,?,?)",
                (work_order_id, task_id, worker_id, work_order_path, work_order_sha256, program_id, "CREATED", self.now_fn()),
            )
            dispatch_id = "dsp-" + str(uuid.uuid4())
            packet = {
                "schema": "x9-loop-work-order-dispatch-v1",
                "task_id": task_id,
                "work_order_path": work_order_path,
                "work_order_sha256": work_order_sha256,
            }
            action = self._v7_action(
                dispatch_id,
                task_id,
                worker_id,
                work_order_id,
                work_order_path,
                work_order_sha256,
            )
            action_raw = contract.canonical_json_bytes(action)
            contract.validate_packet_cap("ACTION.json", action_raw)
            connection.execute(
                "INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)",
                (dispatch_id, task_id, linx_id, worker_id, work_order_sha256, _json(packet), None, "PREPARED", self.now_fn()),
            )
            connection.execute("INSERT INTO outbox(dispatch_id,payload) VALUES(?,?)", (dispatch_id, action_raw.decode("utf-8").rstrip("\n")))
            self._admit_active_order_capacity(connection, baseline_root_size)
            self._atomic_state_write(order_path, raw)
            return {
                "status": "CREATED",
                "dispatch_id": dispatch_id,
                "task_id": task_id,
                "work_order_id": work_order_id,
                "work_order_path": work_order_path,
                "work_order_sha256": work_order_sha256,
                "_action_raw": action_raw,
            }

        if _connection is not None:
            return operation(_connection)
        result = self._mutate(operation)
        if result["status"] == "ACTIVE_WORK_ORDER_REUSED":
            self._publish_current_action()
            return result
        result.pop("_action_raw")
        self._publish_current_action()
        return result

    def _verify_work_order(
        self,
        work_order_id: str,
        *,
        allow_terminal_historical_contract: bool = False,
    ) -> tuple[dict[str, Any], str | None]:
        contract = _load_v7_contract()
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT wo.*,t.base_sha,t.worker_id AS task_worker_id,t.worktree_id,t.status AS task_status,w.path AS worktree_path,p.packet_path AS program_packet_path,"
                "p.packet_sha256 AS program_packet_sha256,p.source_git_sha,p.source_root_sha256 "
                "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "JOIN programs p ON p.program_id=wo.program_id WHERE wo.work_order_id=?",
                (work_order_id,),
            ).fetchone()
            if not row:
                raise IdentityError("WORK_ORDER_UNKNOWN")
            claims = [
                dict(item)
                for item in connection.execute(
                    "SELECT path,kind FROM claims WHERE task_id=? ORDER BY path", (row["task_id"],)
                )
            ]
            resources = [
                item[0]
                for item in connection.execute(
                    "SELECT resource FROM resources WHERE task_id=? ORDER BY resource", (row["task_id"],)
                )
            ]
            active_dispatches = connection.execute(
                "SELECT COUNT(*) FROM dispatches WHERE task_id=? "
                "AND status IN ('PREPARED','DISPATCHED')",
                (row["task_id"],),
            ).fetchone()[0]
        finally:
            connection.close()
        try:
            relative = contract.canonical_repo_path(row["packet_path"])
            path = self._resolve_under(self.repo, self.repo / Path(*PurePosixPath(relative).parts))
            raw = path.read_bytes()
            order = json.loads(raw)
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError, contract.ContractError) as exc:
            raise IdentityError("WORK_ORDER_PACKET_INVALID") from exc
        current = contract.bound_work_order_context(order)
        if "worker_result_contract" in order:
            current["worker_result_contract"] = (
                contract.worker_result_contract_binding()
            )
        current.update(
            {
                "base_sha": row["base_sha"],
                "claims": claims,
                "program_packet_path": row["program_packet_path"],
                "program_packet_sha256": row["program_packet_sha256"],
                "resources": resources,
                "source_git_sha": row["source_git_sha"],
                "source_root_sha256": row["source_root_sha256"],
                "task_id": row["task_id"],
                "work_order_id": row["work_order_id"],
                "worker_id": row["task_worker_id"],
                "worktree_id": row["worktree_id"],
                "worktree_path": row["worktree_path"],
            }
        )
        compatibility: str | None = None
        terminal_historical = (
            allow_terminal_historical_contract
            and (row["task_status"], row["status"])
            in TERMINAL_TASK_ORDER_STATUS_PAIRS
            and active_dispatches == 0
        )

        def add_compatibility(marker: str) -> None:
            nonlocal compatibility
            if compatibility is None:
                compatibility = f"{row['work_order_id']}:{marker}"
            else:
                compatibility = f"{compatibility}+{marker}"

        try:
            packet_worktree_value = order.get("worktree_path")
            current["worktree_path"] = packet_worktree_value
            try:
                validated = contract.validate_work_order_identity(
                    raw, row["packet_sha256"], current
                )
            except contract.ContractError as exc:
                if not (
                    allow_terminal_historical_contract
                    and getattr(exc, "code", None)
                    == "WORK_ORDER_DRIFT:worker_result_contract"
                    and "worker_result_contract" in order
                    and terminal_historical
                ):
                    raise
                current["worker_result_contract"] = order[
                    "worker_result_contract"
                ]
                validated = contract.validate_work_order_identity(
                    raw, row["packet_sha256"], current
                )
                add_compatibility("TERMINAL_HISTORY_WORKER_RESULT_CONTRACT")
            if row["worker_id"] != row["task_worker_id"]:
                raise contract.ContractError("WORK_ORDER_DRIFT:worker_id")
            stored_worktree = Path(row["worktree_path"])
            packet_worktree = Path(packet_worktree_value)
            if not stored_worktree.is_absolute() or not packet_worktree.is_absolute():
                raise contract.ContractError("WORK_ORDER_DRIFT:worktree_path")
            stored_identity = os.path.normcase(os.path.abspath(str(stored_worktree)))
            packet_identity = os.path.normcase(os.path.abspath(str(packet_worktree)))
            if stored_identity != packet_identity:
                raise contract.ContractError("WORK_ORDER_DRIFT:worktree_path")
            for ref in validated["feature_packet_refs"]:
                ref_path = self._resolve_under(
                    self.repo, self.repo / Path(*PurePosixPath(ref["path"]).parts)
                )
                feature_raw = ref_path.read_bytes()
                if hashlib.sha256(feature_raw).hexdigest() != ref["sha256"]:
                    raise contract.ContractError("FEATURE_PACKET_DRIFT")
                feature = json.loads(feature_raw.decode("utf-8"))
                if (
                    terminal_historical
                    and feature.get("context_capsule_ref") is not None
                ):
                    context_compatibility = (
                        self._validate_terminal_historical_context_ref(
                            contract, feature
                        )
                    )
                    add_compatibility(
                        context_compatibility
                        or "TERMINAL_HISTORY_CONTEXT_REF_BOUND"
                    )
                else:
                    self._validate_project_context(
                        feature, phase="pre-dispatch"
                    )
            program_path = self._resolve_under(
                self.repo, self.repo / Path(*PurePosixPath(row["program_packet_path"]).parts)
            )
            if hashlib.sha256(program_path.read_bytes()).hexdigest() != row["program_packet_sha256"]:
                raise contract.ContractError("PROGRAM_PACKET_DRIFT")
        except (OSError, ValueError, RuntimeError, contract.ContractError) as exc:
            code = getattr(exc, "code", "WORK_ORDER_CONTEXT_INVALID")
            raise IdentityError(code) from exc
        return validated, compatibility

    def verify_work_order(self, work_order_id: str) -> dict[str, Any]:
        validated, _compatibility = self._verify_work_order(work_order_id)
        return validated

    def admit_thinker_review(
        self, work_order_id: str, request: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Deduplicate a bounded consultation before any model transport."""
        contract = _load_v7_contract()
        order = self.verify_work_order(work_order_id)
        required = {
            "action_class", "evidence_sha256", "question_sha256",
            "review_class", "staged_tree_sha256", "thinker_id",
        }
        if (
            not isinstance(request, Mapping)
            or not required.issubset(request)
            or set(request) - required - {"admission"}
        ):
            raise IdentityError("THINKER_REVIEW_REQUEST_INVALID")
        if request["action_class"] != order["action_class"]:
            raise IdentityError("THINKER_REVIEW_ACTION_CLASS_MISMATCH")
        admission = contract.classify_question_admission(
            request.get("admission")
        )
        if admission == "OWNER_REQUIRED":
            return {
                "status": admission,
                "reason": "QUESTION_ADMISSION_REQUIRED",
            }
        if admission != "THINKER_ALLOWED":
            return {
                "status": admission,
                "reason": "QUESTION_ADMISSION_REQUIRED",
            }
        permitted = {
            "TWO_DISTINCT_APPROACHES", "STAGED_DIFF", "EVIDENCE_CONFLICT",
            "ARCHITECTURE_SECURITY", "OWNER_CONTRADICTION", "FINAL_ACTIVATION",
        }
        if request["review_class"] not in permitted:
            return {
                "status": "CONTINUE_LOCAL",
                "reason": "QUESTION_ADMISSION_REQUIRED",
            }
        admission_record = request["admission"]
        reason_matches_class = (
            (
                request["review_class"] in {"STAGED_DIFF", "FINAL_ACTIVATION"}
                and admission_record["stable_material_diff"]
            )
            or (
                request["review_class"] == "ARCHITECTURE_SECURITY"
                and admission_record["architecture_security_boundary"]
            )
            or (
                request["review_class"] == "TWO_DISTINCT_APPROACHES"
                and admission_record["distinct_failed_approaches"] >= 2
            )
        )
        if not reason_matches_class:
            return {
                "status": "CONTINUE_LOCAL",
                "reason": "QUESTION_ADMISSION_REQUIRED",
            }
        staged = self._run_git(["diff", "--cached", "--binary"], self.repo)
        staged_paths = self._run_git(
            ["diff", "--cached", "--name-only"], self.repo
        )
        staged_sha256 = hashlib.sha256(
            staged.stdout.encode("utf-8")
        ).hexdigest()
        if (
            staged.returncode
            or staged_paths.returncode
            or not staged.stdout
            or request["evidence_sha256"] != staged_sha256
            or request["staged_tree_sha256"] != staged_sha256
        ):
            return {
                "status": "CONTINUE_LOCAL",
                "reason": "QUESTION_EVIDENCE_UNBOUND",
            }
        connection = self._connect()
        try:
            task_state = connection.execute(
                "SELECT status FROM tasks WHERE task_id=?", (order["task_id"],)
            ).fetchone()
        finally:
            connection.close()
        controller_surface = {
            "skills/devad-x9-loop/scripts/loopctl.py",
            "skills/devad-x9-loop/scripts/v7_contract.py",
        }
        changed_paths = {
            self._normal_path(path)
            for path in staged_paths.stdout.splitlines() if path
        }
        review_boundary = (
            request["review_class"] in {"STAGED_DIFF", "FINAL_ACTIVATION"}
            or (
                request["review_class"] == "ARCHITECTURE_SECURITY"
                and bool(changed_paths & controller_surface)
            )
            or (
                request["review_class"] == "TWO_DISTINCT_APPROACHES"
                and task_state is not None
                and task_state["status"] == "THINX_REVIEW_REQUIRED"
            )
        )
        if not review_boundary:
            return {
                "status": "CONTINUE_LOCAL",
                "reason": "QUESTION_EVIDENCE_UNBOUND",
            }
        try:
            key = contract.consultation_key(
                work_order_id=work_order_id,
                action_class=request["action_class"],
                review_class=request["review_class"],
                evidence_sha256=request["evidence_sha256"],
                question_sha256=request["question_sha256"],
                staged_tree_sha256=request["staged_tree_sha256"],
                thinker_id=request["thinker_id"],
            )
            contract._require_sha256(request["evidence_sha256"], "CONSULTATION_KEY_INVALID")
        except contract.ContractError as exc:
            raise IdentityError(exc.code) from exc
        name = f"consultation:{key}"

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            row = connection.execute(
                "SELECT status,note FROM gates WHERE task_id=? AND name=?",
                (order["task_id"], name),
            ).fetchone()
            thinker = connection.execute(
                "SELECT role FROM actors WHERE actor_id=?", (request["thinker_id"],)
            ).fetchone()
            if not thinker or thinker["role"] not in {"THINKER", "THINX"}:
                raise IdentityError("THINKER_REVIEWER_UNREGISTERED")
            if row is not None:
                return {
                    "consultation_key": key,
                    "status": "THINKER_REVIEW_REUSED",
                    "verdict": row["status"] if row["status"] != "PENDING" else None,
                }
            note = _json({
                "evidence_sha256": request["evidence_sha256"],
                "review_class": request["review_class"],
                "thinker_id": request["thinker_id"],
            })
            connection.execute(
                "INSERT INTO gates(task_id,name,status,note) VALUES(?,?,?,?)",
                (order["task_id"], name, "PENDING", note),
            )
            return {"consultation_key": key, "status": "THINKER_REVIEW_REQUIRED"}

        return self._mutate(operation)

    def record_thinker_verdict(
        self, work_order_id: str, consultation_key: str, verdict: str,
        thinker_id: str, verdict_sha256: str,
    ) -> dict[str, Any]:
        if (
            not re.fullmatch(r"[0-9a-f]{64}", consultation_key)
            or not re.fullmatch(r"[0-9a-f]{64}", verdict_sha256)
            or not isinstance(thinker_id, str) or not thinker_id
            or verdict not in {"PASS", "BLOCK"}
        ):
            raise IdentityError("THINKER_VERDICT_INVALID")
        order = self.verify_work_order(work_order_id)
        name = f"consultation:{consultation_key}"

        def status(connection: sqlite3.Connection) -> str:
            row = connection.execute(
                "SELECT status,note FROM gates WHERE task_id=? AND name=?",
                (order["task_id"], name),
            ).fetchone()
            if row is None:
                raise IdentityError("THINKER_REVIEW_UNKNOWN")
            try:
                request = json.loads(row["note"])
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise IdentityError("THINKER_REVIEW_INVALID") from exc
            actor = connection.execute(
                "SELECT role FROM actors WHERE actor_id=?", (thinker_id,)
            ).fetchone()
            expected = _sha({
                "consultation_key": consultation_key, "thinker_id": thinker_id,
                "verdict": verdict,
            })
            if (
                not actor or actor["role"] not in {"THINKER", "THINX"}
                or request.get("thinker_id") != thinker_id
                or verdict_sha256 != expected
            ):
                raise IdentityError("THINKER_VERDICT_INVALID")
            return row["status"]

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            current = status(connection)
            if current != "PENDING":
                if current == verdict:
                    return {"consultation_key": consultation_key, "status": current}
                raise IdentityError("THINKER_VERDICT_CONFLICT")
            connection.execute(
                "UPDATE gates SET status=? WHERE task_id=? AND name=?",
                (verdict, order["task_id"], name),
            )
            return {"consultation_key": consultation_key, "status": verdict}

        with self._mutation_lock:
            connection = self._connect()
            try:
                current = status(connection)
            finally:
                connection.close()
            if current != "PENDING":
                if current == verdict:
                    return {"consultation_key": consultation_key, "status": current}
                raise IdentityError("THINKER_VERDICT_CONFLICT")
            return self._mutate_locked(operation)

    def _validate_terminal_historical_context_ref(
        self, contract: Any, feature: Mapping[str, Any]
    ) -> str | None:
        reference = feature.get("context_capsule_ref")
        if reference is None:
            return None
        if (
            not isinstance(reference, Mapping)
            or "path" not in reference
            or "sha256" not in reference
            or set(reference) - {"bytes", "capsule_id", "path", "sha256"}
            or not isinstance(reference.get("sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", reference["sha256"]) is None
        ):
            raise IdentityError("PROJECT_CONTEXT_CAPSULE_REF_INVALID")
        expected_size = reference.get("bytes")
        if expected_size is not None and (
            isinstance(expected_size, bool)
            or not isinstance(expected_size, int)
            or expected_size <= 0
        ):
            raise IdentityError("PROJECT_CONTEXT_CAPSULE_REF_INVALID")
        try:
            relative = contract.canonical_repo_path(reference["path"])
            capsule_path = self._resolve_under(
                self.repo, self.repo / Path(*PurePosixPath(relative).parts)
            )
        except FileNotFoundError:
            return "TERMINAL_HISTORY_CONTEXT_REF_UNAVAILABLE"
        except (
            OSError,
            RuntimeError,
            ValueError,
            contract.ContractError,
        ) as exc:
            raise IdentityError("PROJECT_CONTEXT_CAPSULE_REF_INVALID") from exc
        try:
            raw = capsule_path.read_bytes()
        except FileNotFoundError:
            return "TERMINAL_HISTORY_CONTEXT_REF_UNAVAILABLE"
        except OSError as exc:
            raise IdentityError("PROJECT_CONTEXT_CAPSULE_REF_INVALID") from exc
        if (
            hashlib.sha256(raw).hexdigest() != reference["sha256"]
            or (
                expected_size is not None
                and len(raw) != expected_size
            )
        ):
            raise IdentityError("PROJECT_CONTEXT_CAPSULE_REF_DRIFT")
        return None

    def check_model_call(self, work_order_id: str, telemetry: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(telemetry, dict):
            raise IdentityError("MODEL_CALL_TELEMETRY_INVALID")
        allowed = {
            "action_class", "attempt", "call_id", "elapsed_seconds", "model_calls",
            "objective_satisfied", "prompt_prefix_sha256", "token_usage",
            "tool_schema_sha256", "intentional_change_reason",
        }
        required = {
            "action_class", "attempt", "call_id", "elapsed_seconds", "model_calls",
            "objective_satisfied", "prompt_prefix_sha256", "token_usage",
            "tool_schema_sha256",
        }
        if (
            set(telemetry) - allowed
            or not required.issubset(telemetry)
            or not isinstance(telemetry["call_id"], str)
            or not re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", telemetry["call_id"])
            or isinstance(telemetry["elapsed_seconds"], bool)
            or not isinstance(telemetry["elapsed_seconds"], int)
            or telemetry["elapsed_seconds"] < 0
            or isinstance(telemetry["model_calls"], bool)
            or not isinstance(telemetry["model_calls"], int)
            or telemetry["model_calls"] < 0
            or (
                telemetry["token_usage"] != "Unknown"
                and (
                    isinstance(telemetry["token_usage"], bool)
                    or not isinstance(telemetry["token_usage"], int)
                    or telemetry["token_usage"] < 0
                )
            )
            or (
                "intentional_change_reason" in telemetry
                and (
                    not isinstance(telemetry["intentional_change_reason"], str)
                    or not telemetry["intentional_change_reason"].strip()
                )
            )
        ):
            raise IdentityError("MODEL_CALL_TELEMETRY_INVALID")
        order = self.verify_work_order(work_order_id)
        contract = _load_v7_contract()
        work_order_sha256 = hashlib.sha256(
            contract.canonical_json_bytes(order)
        ).hexdigest()

        def inactive_result(status_row: sqlite3.Row) -> dict[str, Any]:
            return {
                "action_class": telemetry["action_class"],
                "allow_call": False,
                "call_id": telemetry["call_id"],
                "event": (
                    "FEATURE_DONE"
                    if status_row["work_order_status"] == "OBJECTIVE_SATISFIED"
                    else "OWNER_DECISION_REQUIRED"
                ),
                "reason": "WORK_ORDER_NOT_ACTIVE",
            }

        class InactiveWorkOrder(RuntimeError):
            def __init__(self, result: dict[str, Any]) -> None:
                super().__init__("WORK_ORDER_NOT_ACTIVE")
                self.result = result

        def retire_dispatches(
            connection: sqlite3.Connection,
        ) -> None:
            connection.execute(
                "UPDATE dispatches SET status='SUPERSEDED' "
                "WHERE task_id=? AND status IN ('PREPARED','DISPATCHED')",
                (order["task_id"],),
            )
        def stop_result(
            connection: sqlite3.Connection, reason: str
        ) -> dict[str, Any]:
            connection.execute(
                "UPDATE work_orders SET status='OWNER_DECISION_REQUIRED' "
                "WHERE work_order_id=?",
                (work_order_id,),
            )
            connection.execute(
                "UPDATE tasks SET status='OWNER_DECISION_REQUIRED' WHERE task_id=?",
                (order["task_id"],),
            )
            retire_dispatches(connection)
            return {
                "action_class": telemetry["action_class"],
                "allow_call": False,
                "call_id": telemetry["call_id"],
                "event": "OWNER_DECISION_REQUIRED",
                "reason": reason,
            }

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            status_row = connection.execute(
                "SELECT wo.status AS work_order_status,t.status AS task_status "
                "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                "WHERE wo.work_order_id=?",
                (work_order_id,),
            ).fetchone()
            if not status_row:
                raise IdentityError("WORK_ORDER_UNKNOWN")
            if (
                status_row["work_order_status"] != "CREATED"
                or status_row["task_status"] not in {"REGISTERED", "RETRY_READY"}
            ):
                raise InactiveWorkOrder(inactive_result(status_row))
            def metric_int(prefix: str, default: int = 0) -> int:
                row = connection.execute(
                    "SELECT value FROM metrics WHERE key=?",
                    (f"{prefix}:{work_order_id}",),
                ).fetchone()
                if not row:
                    return default
                try:
                    value = int(row[0])
                except (TypeError, ValueError) as exc:
                    raise StateNotDurableError("CALL_LEDGER_INVALID") from exc
                if value < 0:
                    raise StateNotDurableError("CALL_LEDGER_INVALID")
                return value

            receipt_rows = list(
                connection.execute(
                    "SELECT * FROM call_receipts WHERE work_order_id=? "
                    "ORDER BY sequence",
                    (work_order_id,),
                )
            )
            validated_receipts: list[dict[str, Any]] = []
            ordered_digests: list[str] = []
            tokens = 0
            unknown_tokens = 0
            try:
                for expected_sequence, row in enumerate(receipt_rows, start=1):
                    raw = (row["receipt"] + "\n").encode("utf-8")
                    validated = contract.validate_call_receipt(
                        json.loads(raw), work_order_sha256
                    )
                    digest = hashlib.sha256(raw).hexdigest()
                    if (
                        row["sequence"] != expected_sequence
                        or validated["sequence"] != expected_sequence
                        or row["call_id"] != validated["call_id"]
                        or row["receipt_sha256"] != digest
                        or contract.canonical_json_bytes(validated) != raw
                    ):
                        raise StateNotDurableError("CALL_LEDGER_INVALID")
                    validated_receipts.append(validated)
                    ordered_digests.append(digest)
                    if validated["token_usage"] == "Unknown":
                        unknown_tokens = 1
                    else:
                        tokens += validated["token_usage"]
            except (
                TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError,
                contract.ContractError,
            ) as exc:
                raise StateNotDurableError("CALL_LEDGER_INVALID") from exc

            reservation_rows = list(
                connection.execute(
                    "SELECT * FROM call_reservations WHERE work_order_id=? "
                    "ORDER BY sequence",
                    (work_order_id,),
                )
            )
            if (
                [row["sequence"] for row in reservation_rows]
                != list(range(1, len(reservation_rows) + 1))
                or any(
                    row["status"] not in {"RESERVED", "RECORDED"}
                    for row in reservation_rows
                )
            ):
                raise StateNotDurableError("CALL_LEDGER_INVALID")
            reservations = {row["call_id"]: row for row in reservation_rows}
            receipts = {
                receipt["call_id"]: receipt for receipt in validated_receipts
            }
            recorded = {
                row["call_id"]: row
                for row in reservation_rows
                if row["status"] == "RECORDED"
            }
            reserved = [
                row for row in reservation_rows if row["status"] == "RESERVED"
            ]
            if (
                len(reserved) > 1
                or set(recorded) != set(receipts)
                or any(
                    receipt["sequence"] != recorded[call_id]["sequence"]
                    or receipt["action_class"] != recorded[call_id]["action_class"]
                    or receipt["attempt"] != recorded[call_id]["attempt"]
                    or receipt["pre_compaction_prompt_prefix_sha256"]
                    != recorded[call_id]["prompt_prefix_sha256"]
                    or receipt["pre_compaction_tool_schema_sha256"]
                    != recorded[call_id]["tool_schema_sha256"]
                    for call_id, receipt in receipts.items()
                )
            ):
                raise StateNotDurableError("CALL_LEDGER_INVALID")

            completed_calls = len(validated_receipts)
            latest_row = connection.execute(
                "SELECT value FROM metrics WHERE key=?",
                (f"call-latest:{work_order_id}",),
            ).fetchone()
            latest_value = latest_row[0] if latest_row else None
            expected_latest = (
                _json(validated_receipts[-1]) if validated_receipts else None
            )
            root_row = connection.execute(
                "SELECT value FROM metrics WHERE key=?",
                (f"call-root:{work_order_id}",),
            ).fetchone()
            if (
                metric_int("call-count") != completed_calls
                or metric_int("call-tokens") != tokens
                or metric_int("call-unknown") != unknown_tokens
                or latest_value != expected_latest
                or (
                    root_row[0] if root_row else _sha([])
                ) != _sha(ordered_digests)
            ):
                raise StateNotDurableError("CALL_LEDGER_INVALID")

            try:
                reservation_created = datetime.fromisoformat(
                    order["created_at"].replace("Z", "+00:00")
                )
                reservation_now = datetime.fromisoformat(
                    self.now_fn().replace("Z", "+00:00")
                )
                reservation_elapsed = max(
                    0,
                    int(
                        (
                            reservation_now - reservation_created
                        ).total_seconds()
                    ),
                )
            except (TypeError, ValueError, OverflowError) as exc:
                raise StateNotDurableError(
                    "WORK_ORDER_TIME_INVALID"
                ) from exc
            existing = connection.execute(
                "SELECT * FROM call_reservations WHERE call_id=?",
                (telemetry["call_id"],),
            ).fetchone()
            if existing:
                if (
                    existing["status"] == "RESERVED"
                    and reservation_elapsed
                    >= order["stop_contract"]["max_wall_seconds"]
                ):
                    return stop_result(
                        connection, "MAX_WALL_SECONDS"
                    )
                candidate_actions = {telemetry["action_class"]}
                matching = (
                    existing["work_order_id"] == work_order_id
                    and existing["action_class"] in candidate_actions
                    and existing["attempt"] == telemetry["attempt"]
                    and existing["prompt_prefix_sha256"]
                    == telemetry["prompt_prefix_sha256"]
                    and existing["tool_schema_sha256"]
                    == telemetry["tool_schema_sha256"]
                )
                if not matching:
                    return stop_result(connection, "CALL_ID_DRIFT")
                return {
                    "action_class": existing["action_class"],
                    "allow_call": False,
                    "call_id": telemetry["call_id"],
                    "call_sequence": existing["sequence"],
                    "event": None,
                    "reason": (
                        "CALL_ALREADY_RECORDED"
                        if existing["status"] == "RECORDED"
                        else "CALL_IN_FLIGHT"
                    ),
                }
            if reserved:
                if (
                    reservation_elapsed
                    >= order["stop_contract"]["max_wall_seconds"]
                ):
                    return stop_result(
                        connection, "MAX_WALL_SECONDS"
                    )
                return {
                    "action_class": telemetry["action_class"],
                    "allow_call": False,
                    "call_id": telemetry["call_id"],
                    "call_sequence": reserved[0]["sequence"],
                    "event": None,
                    "reason": "CALL_IN_FLIGHT",
                }

            durable_calls = completed_calls
            prior = validated_receipts[-1] if validated_receipts else None
            if prior is None and telemetry["action_class"] != order["action_class"]:
                return stop_result(connection, "ACTION_CLASS_MISMATCH")
            attempt_floor = max(
                (receipt["attempt"] for receipt in validated_receipts),
                default=0,
            )
            if telemetry["attempt"] < attempt_floor:
                return stop_result(
                    connection, "STOP_TELEMETRY_REWIND:attempt"
                )
            if order["stop_contract"]["max_tokens"] is None:
                durable_tokens: int | str = "Unknown"
            elif unknown_tokens:
                durable_tokens = "Unknown"
            else:
                durable_tokens = tokens
            try:
                created = datetime.fromisoformat(
                    order["created_at"].replace("Z", "+00:00")
                )
                now = datetime.fromisoformat(
                    self.now_fn().replace("Z", "+00:00")
                )
                authoritative_elapsed = max(
                    0, int((now - created).total_seconds())
                )
            except (TypeError, ValueError, OverflowError) as exc:
                raise StateNotDurableError("WORK_ORDER_TIME_INVALID") from exc
            brain = _load_project_brain()
            try:
                failure_gate = brain.repeated_failure_gate(validated_receipts)
            except brain.ProjectBrainError as exc:
                raise StateNotDurableError(exc.code) from exc
            if failure_gate["open"]:
                return stop_result(connection, failure_gate["code"])

            try:
                result = contract.pre_model_call_gate(
                    action_class=telemetry["action_class"],
                    attempt=telemetry["attempt"],
                    elapsed_seconds=authoritative_elapsed,
                    model_calls=durable_calls,
                    objective_satisfied=telemetry["objective_satisfied"],
                    prior_receipt=prior,
                    prompt_prefix_sha256=telemetry["prompt_prefix_sha256"],
                    stop=order["stop_contract"],
                    token_usage=durable_tokens,
                    tool_schema_sha256=telemetry["tool_schema_sha256"],
                )
            except contract.ContractError as exc:
                raise IdentityError(exc.code) from exc
            result["authoritative_elapsed_seconds"] = authoritative_elapsed
            result["authoritative_model_calls"] = durable_calls
            result["authoritative_token_usage"] = durable_tokens
            result["call_id"] = telemetry["call_id"]
            if not result["allow_call"]:
                status = (
                    "OBJECTIVE_SATISFIED"
                    if result["event"] == "FEATURE_DONE"
                    else "OWNER_DECISION_REQUIRED"
                )
                connection.execute(
                    "UPDATE work_orders SET status=? WHERE work_order_id=?",
                    (status, work_order_id),
                )
                connection.execute(
                    "UPDATE tasks SET status=? WHERE task_id=?",
                    (status, order["task_id"]),
                )
                retire_dispatches(connection)
                return result
            connection.execute(
                "INSERT INTO call_reservations("
                "call_id,work_order_id,sequence,action_class,attempt,prompt_prefix_sha256,"
                "tool_schema_sha256,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    telemetry["call_id"],
                    work_order_id,
                    completed_calls + 1,
                    result["action_class"],
                    telemetry["attempt"],
                    telemetry["prompt_prefix_sha256"],
                    telemetry["tool_schema_sha256"],
                    "RESERVED",
                    self.now_fn(),
                ),
            )
            result["call_sequence"] = completed_calls + 1
            result["reservation_status"] = "RESERVED"
            return result

        try:
            result = self._mutate(operation)
        except InactiveWorkOrder as exc:
            return exc.result
        self._write_action(self._current_action())
        return result

    def record_call_receipt(self, work_order_id: str, receipt: dict[str, Any]) -> dict[str, Any]:
        contract = _load_v7_contract()
        if not isinstance(receipt, dict):
            raise IdentityError("CALL_RECEIPT_INVALID")
        try:
            receipt = contract.validate_call_receipt(receipt)
            raw = contract.canonical_json_bytes(receipt)
        except contract.ContractError as exc:
            raise IdentityError("CALL_RECEIPT_INVALID") from exc
        order = self.verify_work_order(work_order_id)
        digest = hashlib.sha256(raw).hexdigest()
        evidence_path = (
            self.root / "runtime" / "call-receipts" / work_order_id
            / f"{digest}.json"
        )

        if evidence_path.exists() and evidence_path.read_bytes() != raw:
            raise IdentityError("CALL_RECEIPT_EVIDENCE_DRIFT")
        if not evidence_path.exists():
            connection = self._connect()
            restore = False
            try:
                old = connection.execute(
                    "SELECT * FROM call_receipts WHERE call_id=?",
                    (receipt["call_id"],),
                ).fetchone()
                if old is not None:
                    reservation = connection.execute(
                        "SELECT * FROM call_reservations WHERE call_id=?",
                        (receipt["call_id"],),
                    ).fetchone()
                    old_raw = old["receipt"].encode("utf-8") + bytes((10,))
                    if (
                        old["receipt_sha256"] != digest
                        or old["work_order_id"] != work_order_id
                    ):
                        raise IdentityError("CALL_ID_DRIFT")
                    if (
                        old_raw != raw
                        or old["sequence"] != receipt["sequence"]
                        or reservation is None
                        or reservation["work_order_id"] != work_order_id
                        or reservation["sequence"] != receipt["sequence"]
                        or reservation["action_class"] != receipt["action_class"]
                        or reservation["attempt"] != receipt["attempt"]
                        or reservation["prompt_prefix_sha256"]
                        != receipt["pre_compaction_prompt_prefix_sha256"]
                        or reservation["tool_schema_sha256"]
                        != receipt["pre_compaction_tool_schema_sha256"]
                        or reservation["status"] != "RECORDED"
                    ):
                        raise StateNotDurableError("CALL_LEDGER_INVALID")
                    self._safe_state_path(self.snapshot_path)
                    snapshot_raw = self.snapshot_path.read_bytes()
                    snapshot = json.loads(snapshot_raw)
                    state = self._decode_snapshot(snapshot_raw)
                    relative = evidence_path.relative_to(self.repo).as_posix()
                    predicted_archive = self._call_receipt_archive(
                        (relative, raw)
                    )
                    if (
                        snapshot.get("schema") != SCHEMA
                        or state["generation"] != self._generation(connection)
                        or state["call_receipt_archive"] != predicted_archive
                        or self._snapshot_bundle(
                            connection,
                            current_snapshot_raw=snapshot_raw,
                            call_receipt_archive=predicted_archive,
                        )["root_raw"]
                        != snapshot_raw
                    ):
                        raise StateNotDurableError("SNAPSHOT_STALE")
                    restore = True
            finally:
                connection.close()
            if restore:
                if evidence_path.exists():
                    if evidence_path.read_bytes() != raw:
                        raise IdentityError("CALL_RECEIPT_EVIDENCE_DRIFT")
                else:
                    self._atomic_state_write(evidence_path, raw)

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            order_row = connection.execute(
                "SELECT packet_sha256 FROM work_orders WHERE work_order_id=?",
                (work_order_id,),
            ).fetchone()
            if not order_row or receipt["work_order_sha256"] != order_row["packet_sha256"]:
                raise IdentityError("CALL_RECEIPT_WORK_ORDER_MISMATCH")
            old = connection.execute(
                "SELECT * FROM call_receipts WHERE call_id=?",
                (receipt["call_id"],),
            ).fetchone()
            if old:
                reservation = connection.execute(
                    "SELECT * FROM call_reservations WHERE call_id=?",
                    (receipt["call_id"],),
                ).fetchone()
                old_raw = old["receipt"].encode("utf-8") + bytes((10,))
                if (
                    old["receipt_sha256"] != digest
                    or old["work_order_id"] != work_order_id
                ):
                    raise IdentityError("CALL_ID_DRIFT")
                if (
                    old_raw != raw
                    or old["sequence"] != receipt["sequence"]
                    or reservation is None
                    or reservation["work_order_id"] != work_order_id
                    or reservation["sequence"] != receipt["sequence"]
                    or reservation["action_class"]
                    != receipt["action_class"]
                    or reservation["attempt"] != receipt["attempt"]
                    or reservation["prompt_prefix_sha256"]
                    != receipt[
                        "pre_compaction_prompt_prefix_sha256"
                    ]
                    or reservation["tool_schema_sha256"]
                    != receipt[
                        "pre_compaction_tool_schema_sha256"
                    ]
                    or reservation["status"] != "RECORDED"
                ):
                    raise StateNotDurableError("CALL_LEDGER_INVALID")
                if (
                    evidence_path.exists()
                    and evidence_path.read_bytes() != raw
                ):
                    raise IdentityError(
                        "CALL_RECEIPT_EVIDENCE_DRIFT"
                    )
                if not evidence_path.exists():
                    self._atomic_state_write(evidence_path, raw)
                return {
                    "status": "RECORDED",
                    "call_id": receipt["call_id"],
                    "receipt_sha256": digest,
                    "evidence_path": str(
                        evidence_path.relative_to(self.repo)
                    ).replace(chr(92), "/"),
                }
            reservation = connection.execute(
                "SELECT * FROM call_reservations "
                "WHERE call_id=? AND work_order_id=? AND status='RESERVED'",
                (receipt["call_id"], work_order_id),
            ).fetchone()
            if not reservation:
                raise IdentityError("CALL_NOT_RESERVED")
            if (
                receipt["action_class"] != reservation["action_class"]
                or receipt["attempt"] != reservation["attempt"]
                or receipt["sequence"] != reservation["sequence"]
                or receipt["pre_compaction_prompt_prefix_sha256"]
                != reservation["prompt_prefix_sha256"]
                or receipt["pre_compaction_tool_schema_sha256"]
                != reservation["tool_schema_sha256"]
            ):
                raise IdentityError("CALL_RECEIPT_RESERVATION_MISMATCH")
            if evidence_path.exists() and evidence_path.read_bytes() != raw:
                raise IdentityError("CALL_RECEIPT_EVIDENCE_DRIFT")
            self._atomic_state_write(evidence_path, raw)
            connection.execute(
                "INSERT INTO call_receipts("
                "call_id,work_order_id,sequence,receipt_sha256,receipt,created_at"
                ") VALUES(?,?,?,?,?,?)",
                (
                    receipt["call_id"],
                    work_order_id,
                    receipt["sequence"],
                    digest,
                    raw.decode("utf-8").rstrip("\n"),
                    self.now_fn(),
                ),
            )
            connection.execute(
                "UPDATE call_reservations SET status='RECORDED' WHERE call_id=?",
                (receipt["call_id"],),
            )

            def metric_int(prefix: str, default: int = 0) -> int:
                row = connection.execute(
                    "SELECT value FROM metrics WHERE key=?",
                    (f"{prefix}:{work_order_id}",),
                ).fetchone()
                if not row:
                    return default
                try:
                    value = int(row[0])
                except (TypeError, ValueError) as exc:
                    raise StateNotDurableError("CALL_LEDGER_INVALID") from exc
                if value < 0:
                    raise StateNotDurableError("CALL_LEDGER_INVALID")
                return value

            count = metric_int("call-count") + 1
            tokens = metric_int("call-tokens")
            unknown = metric_int("call-unknown")
            if receipt["token_usage"] == "Unknown":
                unknown = 1
            else:
                tokens += receipt["token_usage"]
            receipt_digests = [
                row[0]
                for row in connection.execute(
                    "SELECT receipt_sha256 FROM call_receipts "
                    "WHERE work_order_id=? ORDER BY sequence",
                    (work_order_id,),
                )
            ]
            if (
                len(receipt_digests) != count
                or any(
                    not re.fullmatch(r"[0-9a-f]{64}", str(value))
                    for value in receipt_digests
                )
            ):
                raise StateNotDurableError("CALL_LEDGER_INVALID")
            root = _sha(receipt_digests)
            metrics = {
                f"call-count:{work_order_id}": str(count),
                f"call-latest:{work_order_id}": _json(receipt),
                f"call-root:{work_order_id}": root,
                f"call-tokens:{work_order_id}": str(tokens),
                f"call-unknown:{work_order_id}": str(unknown),
            }
            connection.executemany(
                "INSERT INTO metrics(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                sorted(metrics.items()),
            )
            if receipt["stability"] == "DRIFTED":
                connection.execute(
                    "UPDATE work_orders SET status='OWNER_DECISION_REQUIRED' "
                    "WHERE work_order_id=?",
                    (work_order_id,),
                )
                connection.execute(
                    "UPDATE tasks SET status='OWNER_DECISION_REQUIRED' WHERE task_id=?",
                    (order["task_id"],),
                )
            return {
                "status": "RECORDED",
                "call_id": receipt["call_id"],
                "receipt_sha256": digest,
                "evidence_path": str(evidence_path.relative_to(self.repo)).replace("\\", "/"),
            }

        result = self._mutate(operation)
        if receipt.get("failure") is not None:
            brain = _load_project_brain()
            try:
                memory = brain.ProjectMemory(self.repo, self._ensure_project_profile())
                memory.initialize()
                memory.record_incident(receipt["failure"], receipt_id=receipt["call_id"])
            except brain.ProjectBrainError:
                pass
        return result
    def register_task(
        self,
        task_id: str,
        worker_id: str,
        worktree_id: str,
        base_sha: str,
        claims: list[dict[str, str]],
        resources: list[str],
        dependencies: list[str],
        finish_line: str,
        owner_packet_path: str | None = None,
        owner_packet_sha256: str | None = None,
        schema: str = "x9-loop-lite-task-v1",
        gates: list[dict[str, str]] | None = None,
        forbidden: list[str] | None = None,
    ) -> dict[str, Any]:
        if schema != "x9-loop-lite-task-v1":
            raise IdentityError("TASK_SCHEMA_INVALID")
        contract = _load_v7_contract()
        if not isinstance(owner_packet_path, str) or not isinstance(owner_packet_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", owner_packet_sha256):
            raise IdentityError("OWNER_PACKET_REQUIRED")
        if not isinstance(base_sha, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", base_sha):
            raise IdentityError("TASK_BASE_SHA_INVALID")
        if not isinstance(finish_line, str) or not finish_line.strip():
            raise IdentityError("TASK_FINISH_LINE_INVALID")
        owner_packet_path = self._normal_path(owner_packet_path)
        normalized_claims = [
            (self._normal_path(item["path"]), self._claim_kind(item.get("kind", "file")))
            for item in claims
        ]
        if not isinstance(resources, list) or any(not isinstance(item, str) or not item.strip() for item in resources):
            raise IdentityError("TASK_RESOURCES_INVALID")
        try:
            normalized_resources = contract.canonical_resource_keys(resources)
        except contract.ContractError as exc:
            raise IdentityError("TASK_RESOURCES_INVALID") from exc
        if not isinstance(dependencies, list) or any(not isinstance(item, str) or not item for item in dependencies):
            raise IdentityError("TASK_DEPENDENCIES_INVALID")
        forbidden = [] if forbidden is None else forbidden
        if not isinstance(forbidden, list) or any(not isinstance(item, str) or not item.strip() for item in forbidden):
            raise IdentityError("TASK_FORBIDDEN_INVALID")
        normalized_forbidden = sorted(set(forbidden))
        gates = [] if gates is None else gates
        normalized_gates: list[dict[str, str]] = []
        for gate in gates:
            if not isinstance(gate, dict) or set(gate) != {"name", "status", "note"}:
                raise IdentityError("TASK_GATE_INVALID")
            if not all(isinstance(gate[field], str) and gate[field].strip() for field in gate):
                raise IdentityError("TASK_GATE_INVALID")
            normalized_gates.append(
                {"name": gate["name"], "status": gate["status"].upper(), "note": gate["note"]}
            )

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            existing_task = connection.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if existing_task or task_id in self._completed_task_ids(connection):
                raise IdentityError("TASK_ID_RETIRED" if (not existing_task or existing_task["status"] == "COMPLETE") else "TASK_ID_EXISTS")
            actor = connection.execute("SELECT role FROM actors WHERE actor_id=?", (worker_id,)).fetchone()
            if not actor or actor[0] != "WORKER":
                raise IdentityError("WORKER_IDENTITY_INVALID")
            if not connection.execute("SELECT 1 FROM worktrees WHERE worktree_id=?", (worktree_id,)).fetchone():
                raise IdentityError("WORKTREE_UNKNOWN")
            for existing in connection.execute("SELECT c.task_id,c.path,c.kind FROM claims c JOIN tasks t ON t.task_id=c.task_id WHERE t.status NOT IN ('COMPLETE','SUPERSEDED')"):
                for path, kind in normalized_claims:
                    if existing["task_id"] != task_id and self._overlap(path, kind, existing["path"], existing["kind"]):
                        raise ClaimConflictError(f"CLAIM_CONFLICT:{path}:{existing['task_id']}")
            for resource in normalized_resources:
                old = connection.execute("SELECT r.task_id FROM resources r JOIN tasks t ON t.task_id=r.task_id WHERE r.resource=? AND t.status NOT IN ('COMPLETE','SUPERSEDED')", (resource,)).fetchone()
                if old and old[0] != task_id:
                    raise ResourceConflictError(f"RESOURCE_CONFLICT:{resource}:{old[0]}")
            connection.execute(
                "INSERT INTO tasks(task_id,worker_id,worktree_id,base_sha,owner_packet_path,owner_packet_sha256,dependencies,finish_line,status) VALUES(?,?,?,?,?,?,?,?,?)",
                (task_id, worker_id, worktree_id, base_sha, owner_packet_path, owner_packet_sha256, _json(sorted(dependencies)), finish_line, "REGISTERED"),
            )
            connection.executemany("INSERT INTO claims(task_id,path,kind) VALUES(?,?,?)", [(task_id, path, kind) for path, kind in normalized_claims])
            connection.executemany("INSERT INTO resources(task_id,resource) VALUES(?,?)", [(task_id, item) for item in normalized_resources])
            connection.executemany(
                "INSERT INTO gates(task_id,name,status,note) VALUES(?,?,?,?)",
                [(task_id, gate["name"], gate["status"], gate["note"]) for gate in normalized_gates],
            )
            connection.execute(
                "INSERT INTO metrics(key,value) VALUES(?,?)",
                (f"task-contract:{task_id}", _json({"forbidden": normalized_forbidden, "schema": schema})),
            )
            return {"status": "REGISTERED", "task_id": task_id}

        return self._mutate(operation)
    def set_gate(self, task_id: str, name: str, status: str, note: str) -> dict[str, Any]:
        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            connection.execute(
                "INSERT INTO gates(task_id,name,status,note) VALUES(?,?,?,?) "
                "ON CONFLICT(task_id,name) DO UPDATE SET status=excluded.status,note=excluded.note",
                (task_id, name, status.upper(), note),
            )
            return {"status": status.upper(), "gate": name}
        return self._mutate(operation)

    def _transition_task_state(self, task_id: str, status: str) -> dict[str, Any]:
        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            row = connection.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not row:
                raise TaskNotReadyError("TASK_UNKNOWN")
            target = status.upper()
            connection.execute("UPDATE tasks SET status=? WHERE task_id=?", (target, task_id))
            work_order_status = (
                "CREATED"
                if target in {"REGISTERED", "RETRY_READY"}
                else target
            )
            connection.execute(
                "UPDATE work_orders SET status=? WHERE task_id=?",
                (work_order_status, task_id),
            )
            if target == "COMPLETE" and row["status"] != "COMPLETE":
                self._remember_completed_task(connection, task_id)
                connection.execute("INSERT INTO metrics(key,value) VALUES(?,'0') ON CONFLICT(key) DO UPDATE SET value='0'", (f"blocked:{task_id}",))
                connection.execute("INSERT INTO metrics(key,value) VALUES('completed_clean_dispatches','1') ON CONFLICT(key) DO UPDATE SET value=CAST(value AS INTEGER)+1")
            return {"status": target, "task_id": task_id}
        return self._mutate(operation)

    def request_claim_expansion(self, task_id: str, path: str) -> dict[str, Any]:
        canonical = self._normal_path(path)
        result = self.set_gate(task_id, f"claim-expansion:{canonical}", "PENDING", "owner approval required")
        return {"status": "CLAIM_EXPANSION_REQUEST", "gate_status": result["status"], "path": canonical}

    def _verify_owner_packet(self, task: sqlite3.Row) -> set[str]:
        root = Path(task["worktree_path"])
        owner_path = self._normal_path(task["owner_packet_path"])
        if (not owner_path.startswith(".devad/manager/owner-packets/")
                or PurePosixPath(owner_path).stem != task["owner_packet_sha256"]):
            raise IdentityError("OWNER_PACKET_INVALID")
        try:
            packet_path = self._resolve_under(root, root / Path(*PurePosixPath(owner_path).parts))
            data = packet_path.read_bytes()
            packet = json.loads(data.decode("utf-8"))
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            raise IdentityError("OWNER_PACKET_INVALID") from exc
        if hashlib.sha256(data).hexdigest() != task["owner_packet_sha256"] or not isinstance(packet, dict) or packet.get("schema") != "x9-owner-packet-v1" or not isinstance(packet.get("attachments"), list):
            raise IdentityError("OWNER_PACKET_INVALID")
        verified = {owner_path}
        for attachment in packet["attachments"]:
            if not isinstance(attachment, dict) or not isinstance(attachment.get("path"), str) or not isinstance(attachment.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", attachment["sha256"]):
                raise IdentityError("OWNER_PACKET_INVALID")
            try:
                attachment_path = self._normal_path(attachment["path"])
                if (not attachment_path.startswith(".devad/manager/owner-packets/artifacts/")
                        or PurePosixPath(attachment_path).stem != attachment["sha256"]):
                    raise IdentityError("OWNER_PACKET_INVALID")
                target = self._resolve_under(root, root / Path(*PurePosixPath(attachment_path).parts))
                if hashlib.sha256(target.read_bytes()).hexdigest() != attachment["sha256"]:
                    raise IdentityError("OWNER_PACKET_INVALID")
                verified.add(attachment_path)
            except (OSError, ValueError, RuntimeError, ScopeBreachError) as exc:
                raise IdentityError("OWNER_PACKET_INVALID") from exc
        for relative in sorted(verified):
            tracked = self._run_git(["ls-files", "--", relative], root)
            if tracked.returncode:
                raise GitStateError("GIT_STATE_UNKNOWN")
            if tracked.stdout.strip():
                raise IdentityError("OWNER_PACKET_TRACKED")
        return verified

    def _task_packet(self, connection: sqlite3.Connection, task_id: str, sender_id: str) -> dict[str, Any]:
        task = connection.execute("SELECT t.*,w.path AS worktree_path FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id WHERE t.task_id=?", (task_id,)).fetchone()
        if not task:
            raise TaskNotReadyError("TASK_UNKNOWN")
        if task["status"] not in {"REGISTERED", "RETRY_READY"}:
            raise TaskNotReadyError("TASK_STATE_NOT_DISPATCHABLE")
        owner_evidence = self._verify_owner_packet(task)
        controller_evidence = self._controller_snapshot_evidence(Path(task["worktree_path"]), connection)
        local_git = self._git_state(task["base_sha"], task["worktree_path"])
        validated_receipts = set(self._validated_receipt_entries(Path(task["worktree_path"]), connection))
        local_work = {key: [path for path in self._scope_paths(value) if path not in owner_evidence and path not in controller_evidence and path not in validated_receipts] for key, value in local_git.items()}
        claims_for_local = [(row["path"], row["kind"]) for row in connection.execute("SELECT path,kind FROM claims WHERE task_id=?", (task_id,))]
        for path in sorted({item for values in local_work.values() for item in values}):
            if not any(self._overlap(path, "file", claim, kind) for claim, kind in claims_for_local):
                raise ScopeBreachError(f"LOCAL_WORK_SCOPE_BREACH:{path}")
        if len(_json(local_work).encode("utf-8")) >= 1024:
            raise DeliveryError("LOCAL_WORK_TOO_LARGE")
        sender = connection.execute("SELECT role FROM actors WHERE actor_id=?", (sender_id,)).fetchone()
        if not sender or sender[0] != "LINX":
            raise IdentityError("SENDER_IDENTITY_INVALID")
        completed_ids = set(self._completed_task_ids(connection))
        for dependency in json.loads(task["dependencies"]):
            row = connection.execute("SELECT status FROM tasks WHERE task_id=?", (dependency,)).fetchone()
            if (not row or row[0] != "COMPLETE") and dependency not in completed_ids:
                raise TaskNotReadyError("DEPENDENCY_NOT_COMPLETE")
        for gate in connection.execute("SELECT status FROM gates WHERE task_id=?", (task_id,)):
            if gate["status"] != "PASS":
                raise TaskNotReadyError("GATE_NOT_PASS")
        contract_row = connection.execute(
            "SELECT value FROM metrics WHERE key=?", (f"task-contract:{task_id}",)
        ).fetchone()
        try:
            task_contract = json.loads(contract_row[0]) if contract_row else {
                "forbidden": [], "schema": "x9-loop-lite-task-v1"
            }
        except json.JSONDecodeError as exc:
            raise StateNotDurableError("TASK_CONTRACT_INVALID") from exc
        return {
            "schema": "x9-loop-lite-dispatch-v1", "task_id": task_id, "sender_id": sender_id,
            "task_schema": task_contract["schema"], "forbidden": task_contract["forbidden"],
            "target_actor_id": task["worker_id"], "worktree_id": task["worktree_id"], "worktree_path": task["worktree_path"],
            "base_sha": task["base_sha"], "owner_packet_path": task["owner_packet_path"], "owner_packet_sha256": task["owner_packet_sha256"], "local_work": local_work, "dependencies": json.loads(task["dependencies"]), "finish_line": task["finish_line"],
            "claims": [dict(row) for row in connection.execute("SELECT path,kind FROM claims WHERE task_id=? ORDER BY path", (task_id,))],
            "resources": [row[0] for row in connection.execute("SELECT resource FROM resources WHERE task_id=? ORDER BY resource", (task_id,))],
            "gates": [dict(row) for row in connection.execute("SELECT name,status,note FROM gates WHERE task_id=? ORDER BY name", (task_id,))],
        }

    def _enforce_coding_limit(self, connection: sqlite3.Connection, worker_id: str) -> None:
        metric = connection.execute("SELECT value FROM metrics WHERE key='completed_clean_dispatches'").fetchone()
        successful = int(metric[0]) if metric else connection.execute("SELECT COUNT(DISTINCT d.task_id) FROM dispatches d JOIN tasks t ON t.task_id=d.task_id WHERE t.status='COMPLETE'").fetchone()[0]
        metrics = {row["key"]: int(row["value"]) for row in connection.execute("SELECT key,value FROM metrics") if str(row["value"]).isdigit()}
        active = {row[0] for row in connection.execute("SELECT DISTINCT t.worker_id FROM tasks t JOIN dispatches d ON d.task_id=t.task_id WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') AND d.status IN ('PREPARED','DISPATCHED')")}
        if worker_id not in active and len(active) >= coding_limit(successful, metrics):
            raise TaskNotReadyError("CODING_LIMIT")

    def _action(self, dispatch_id: str, packet: dict[str, Any], packet_sha256: str,
                action_id: str | None = None, attempt: int = 1) -> dict[str, Any]:
        return {"schema": "x9-loop-lite-action-v1", "action_id": action_id or "act-" + str(uuid.uuid4()),
                "action": "SEND_DISPATCH", "dispatch_id": dispatch_id, "task_id": packet["task_id"],
                "target_actor_id": packet["target_actor_id"], "target_role": "WORKER",
                "packet_sha256": packet_sha256, "attempt": attempt, "packet": packet, "must_record_transport": True}

    def _status_action(self, action: str, reason: str) -> dict[str, Any]:
        seed = {"action": action, "reason": reason}
        return {"schema": "x9-loop-lite-action-v1", "action_id": "act-" + _sha(seed)[:20],
                "action": action, "dispatch_id": None, "task_id": None, "target_actor_id": None,
                "target_role": None, "packet_sha256": None, "attempt": 0, "packet": None, "reason": reason}

    def _write_action(self, action: dict[str, Any]) -> None:
        encoded = _load_v7_contract().canonical_json_bytes(action)
        if len(encoded) > 4096:
            raise DeliveryError("ACTION_TOO_LARGE")
        self._atomic_state_write(self.action_path, encoded)

    def _publish_current_action(self) -> dict[str, Any]:
        action = self._current_action()
        self._write_action(action)
        return action

    def _assert_v7_dispatch_preflight(
        self, connection: sqlite3.Connection, task_id: str
    ) -> None:
        task = connection.execute(
            "SELECT t.worker_id,t.base_sha,w.path,wo.work_order_id,"
            "wo.status AS work_order_status "
            "FROM tasks t "
            "JOIN worktrees w ON w.worktree_id=t.worktree_id "
            "JOIN work_orders wo ON wo.task_id=t.task_id "
            "WHERE t.task_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
            (task_id,),
        ).fetchone()
        if not task:
            raise TaskNotReadyError("TASK_STATE_NOT_DISPATCHABLE")
        candidate_handoff = None
        if task["work_order_status"] == "CREATED":
            verified_order = self.verify_work_order(task["work_order_id"])
            candidate_handoff = verified_order.get("candidate_handoff")
        elif task["work_order_status"] != "ACTIVE":
            raise TaskNotReadyError("WORK_ORDER_STATE_NOT_DISPATCHABLE")
        self._verify_v7_worktree_preflight(
            task["path"], task["base_sha"], connection,
            candidate_handoff,
        )
        active_for_worker = connection.execute(
            "SELECT COUNT(DISTINCT d.task_id) FROM dispatches d "
            "JOIN tasks t ON t.task_id=d.task_id "
            "WHERE t.worker_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED') "
            "AND d.status IN ('PREPARED','DISPATCHED')",
            (task["worker_id"],),
        ).fetchone()[0]
        if active_for_worker > 1:
            raise TaskNotReadyError("WORKER_ACTIVE_DISPATCH")
        claims = [
            dict(row)
            for row in connection.execute(
                "SELECT c.task_id,c.path,c.kind FROM claims c "
                "JOIN tasks t ON t.task_id=c.task_id "
                "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') ORDER BY c.task_id,c.path"
            )
        ]
        for index, left in enumerate(claims):
            for right in claims[index + 1 :]:
                if left["task_id"] != right["task_id"] and self._overlap(
                    left["path"], left["kind"], right["path"], right["kind"]
                ):
                    raise ClaimConflictError("CLAIM_CONFLICT")
        conflict = connection.execute(
            "SELECT 1 FROM resources r JOIN tasks t ON t.task_id=r.task_id "
            "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') GROUP BY r.resource "
            "HAVING COUNT(DISTINCT r.task_id) > 1 LIMIT 1"
        ).fetchone()
        if conflict:
            raise ResourceConflictError("RESOURCE_CONFLICT")

    def _current_action(self) -> dict[str, Any]:
        self._safe_state_path(self.db_path)
        connection = sqlite3.connect(
            f"file:{self.db_path.as_posix()}?mode=ro", uri=True
        )
        connection.row_factory = sqlite3.Row
        try:
            inbox_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' "
                "AND name='inbox'"
            ).fetchone()
            repair = (
                connection.execute(
                    "SELECT i.event_id,i.payload,i.status,d.dispatch_id,"
                    "d.task_id,d.target_id,o.payload AS original_action,"
                    "w.work_order_id,w.packet_path,w.packet_sha256 "
                    "FROM inbox i JOIN dispatches d "
                    "ON d.dispatch_id=i.dispatch_id JOIN tasks t "
                    "ON t.task_id=d.task_id JOIN work_orders w "
                    "ON w.task_id=d.task_id LEFT JOIN outbox o "
                    "ON o.dispatch_id=d.dispatch_id "
                    "WHERE i.status LIKE 'REJECTED:%' "
                    "AND d.status='DISPATCHED' "
                    "AND t.status NOT IN ('COMPLETE','SUPERSEDED') "
                    "ORDER BY i.created_at,i.event_id LIMIT 1"
                ).fetchone()
                if inbox_exists else None
            )
            if repair:
                try:
                    envelope = json.loads(repair["payload"])
                    original_action = (
                        json.loads(repair["original_action"])
                        if repair["original_action"]
                        else {}
                    )
                    payload_ref = envelope["payload_ref"]
                    profile_id = envelope["project_profile_id"]
                except (
                    KeyError, TypeError, ValueError, json.JSONDecodeError
                ) as exc:
                    raise StateNotDurableError(
                        "REJECTED_RECEIPT_REGISTRY_INVALID"
                    ) from exc
                reason = repair["status"].partition(":")[2]
                seed = {
                    "dispatch_id": repair["dispatch_id"],
                    "event_id": repair["event_id"],
                    "result_sha256": payload_ref.get("sha256"),
                }
                action_digest = _sha(seed)[:32]
                action_uuid = "-".join(
                    (action_digest[:8], action_digest[8:12],
                     action_digest[12:16], action_digest[16:20],
                     action_digest[20:])
                )
                return {
                    "action": "RESULT_SCHEMA_REPAIR",
                    "action_id": "act-" + action_uuid,
                    "attempt": original_action.get("attempt", 1),
                    "dispatch_id": repair["dispatch_id"],
                    "expected_result_schema": "x9-loop-result-v2",
                    "invalid_event_id": repair["event_id"],
                    "invalid_result_sha256": payload_ref.get("sha256"),
                    "must_record_transport": True,
                    "project_profile_id": profile_id,
                    "reason": reason,
                    "schema": "x9-loop-action-v2",
                    "target_actor_id": repair["target_id"],
                    "target_role": "WORKER",
                    "task_id": repair["task_id"],
                    "work_order_id": repair["work_order_id"],
                    "work_order_path": repair["packet_path"],
                    "work_order_sha256": repair["packet_sha256"],
                }
            row = connection.execute(
                "SELECT o.payload,d.task_id FROM outbox o "
                "JOIN dispatches d ON d.dispatch_id=o.dispatch_id "
                "WHERE d.status='PREPARED' "
                "ORDER BY d.created_at,d.dispatch_id LIMIT 1"
            ).fetchone()
            if row:
                action = json.loads(row["payload"])
                if action.get("schema") == "x9-loop-action-v2":
                    try:
                        self._assert_v7_dispatch_preflight(
                            connection, row["task_id"]
                        )
                    except (
                        LoopError,
                        OSError,
                        ValueError,
                    ) as exc:
                        reason = str(exc) or type(exc).__name__
                        return self._status_action(
                            "NOOP", f"dispatch-preflight-blocked:{reason}"
                        )
                return action
            waiting = connection.execute(
                "SELECT 1 FROM dispatches d JOIN tasks t ON t.task_id=d.task_id "
                "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') AND d.status='DISPATCHED' LIMIT 1"
            ).fetchone()
            repair_acknowledged = (
                connection.execute(
                    "SELECT 1 FROM inbox i JOIN dispatches d "
                    "ON d.dispatch_id=i.dispatch_id JOIN tasks t "
                    "ON t.task_id=d.task_id "
                    "WHERE i.status LIKE 'REPAIR_ACKNOWLEDGED:%' "
                    "AND d.status='DISPATCHED' "
                    "AND t.status NOT IN ('COMPLETE','SUPERSEDED') LIMIT 1"
                ).fetchone()
                if inbox_exists else None
            )
            return self._status_action(
                "WAIT" if waiting else "NOOP",
                (
                    "repair-acknowledged"
                    if waiting and repair_acknowledged
                    else "delivery-acknowledged"
                    if waiting
                    else "no-outbox"
                ),
            )
        finally:
            connection.close()
    def prepare_dispatch(self, task_id: str, sender_id: str) -> dict[str, Any]:
        self._assert_durable()
        connection = self._connect()
        replayed = None
        try:
            packet = self._task_packet(connection, task_id, sender_id)
            packet_sha256 = _sha(packet)
            old = connection.execute(
                "SELECT * FROM dispatches WHERE task_id=? AND packet_sha256=? "
                "AND status IN ('PREPARED','DISPATCHED') "
                "ORDER BY rowid DESC LIMIT 1",
                (task_id, packet_sha256),
            ).fetchone()
            if old is not None and old["status"] == "DISPATCHED":
                replayed = {
                    "status": "ALREADY_ACKNOWLEDGED",
                    "dispatch_id": old["dispatch_id"],
                    "packet_sha256": packet_sha256,
                    "supersedes": old["supersedes"],
                }
        finally:
            connection.close()
        if replayed is not None:
            self._publish_current_action()
            return replayed

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            packet = self._task_packet(connection, task_id, sender_id)
            packet_sha256 = _sha(packet)
            old = connection.execute("SELECT * FROM dispatches WHERE task_id=? AND packet_sha256=? AND status IN ('PREPARED','DISPATCHED') ORDER BY rowid DESC LIMIT 1", (task_id, packet_sha256)).fetchone()
            if old:
                if old["status"] == "DISPATCHED":
                    action = None
                    status = "ALREADY_ACKNOWLEDGED"
                else:
                    outbox = connection.execute("SELECT payload FROM outbox WHERE dispatch_id=?", (old["dispatch_id"],)).fetchone()
                    action = json.loads(outbox[0]) if outbox else self._action(old["dispatch_id"], packet, packet_sha256)
                    status = "PREPARED"
                return {"status": status, "dispatch_id": old["dispatch_id"], "packet_sha256": packet_sha256, "supersedes": old["supersedes"], "_action": action}
            self._enforce_coding_limit(connection, packet["target_actor_id"])
            dispatch_id = "dsp-" + str(uuid.uuid4())
            previous = connection.execute("SELECT dispatch_id FROM dispatches WHERE task_id=? ORDER BY rowid DESC LIMIT 1", (task_id,)).fetchone()
            connection.execute("UPDATE dispatches SET status='SUPERSEDED' WHERE task_id=? AND status IN ('PREPARED','DISPATCHED')", (task_id,))
            action = self._action(dispatch_id, packet, packet_sha256)
            if len(_json(action).encode("utf-8")) >= 4096:
                raise DeliveryError("ACTION_TOO_LARGE")
            connection.execute("INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)", (dispatch_id, task_id, sender_id, packet["target_actor_id"], packet_sha256, _json(packet), previous[0] if previous else None, "PREPARED", self.now_fn()))
            connection.execute("INSERT INTO outbox(dispatch_id,payload) VALUES(?,?)", (dispatch_id, _json(action)))
            return {"dispatch_id": dispatch_id, "packet_sha256": packet_sha256, "supersedes": previous[0] if previous else None, "_action": action}
        result = self._mutate(operation)
        result.pop("_action")
        self._publish_current_action()
        return result
    def _register_result_schema_rejection(
        self,
        event: Mapping[str, Any],
        event_sha256: str,
        event_text: str,
        result: Mapping[str, Any],
        reason: str,
    ) -> dict[str, Any]:
        if reason not in {"RESULT_FIELDS_INVALID", "RESULT_SCHEMA_INVALID"}:
            raise StaleCompletionError(reason)
        payload_ref = event["payload_ref"]
        expected_receipt = self._normal_path(
            f".devad/workers/{event['source_actor_id']}/receipts/"
            f"{event['event_id']}.json"
        )
        if self._normal_path(payload_ref["path"]) != expected_receipt:
            raise StaleCompletionError("STALE_COMPLETION")

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            duplicate = connection.execute(
                "SELECT event_sha256,payload,status FROM inbox "
                "WHERE event_id=?",
                (event["event_id"],),
            ).fetchone()
            expected_status = f"REJECTED:{reason}"
            if duplicate:
                if (
                    duplicate["event_sha256"] == event_sha256
                    and duplicate["payload"] == event_text
                    and duplicate["status"] == expected_status
                ):
                    raise _InboxAlreadyConsumed()
                raise IdentityError("INBOX_EVENT_CONFLICT")
            row = connection.execute(
                "SELECT d.task_id,d.target_id,d.packet_sha256,d.status,"
                "t.worker_id,t.status AS task_status,wo.status AS order_status,"
                "a.role,(SELECT dispatch_id FROM dispatches "
                "WHERE task_id=d.task_id ORDER BY rowid DESC LIMIT 1) "
                "AS latest_dispatch_id FROM dispatches d JOIN tasks t "
                "ON t.task_id=d.task_id JOIN work_orders wo "
                "ON wo.task_id=d.task_id LEFT JOIN actors a "
                "ON a.actor_id=? WHERE d.dispatch_id=?",
                (event["source_actor_id"], result.get("dispatch_id")),
            ).fetchone()
            if (
                row is None
                or row["status"] != "DISPATCHED"
                or row["task_status"] not in {"REGISTERED", "RETRY_READY"}
                or row["order_status"] != "CREATED"
                or row["latest_dispatch_id"] != result.get("dispatch_id")
                or row["role"] != "WORKER"
                or row["worker_id"] != event["source_actor_id"]
                or row["target_id"] != event["source_actor_id"]
                or row["task_id"] != result.get("task_id")
                or row["packet_sha256"] != result.get("packet_sha256")
                or result.get("event_id") != event["event_id"]
                or result.get("worker_id") != event["source_actor_id"]
                or result.get("role") != "WORKER"
                or payload_ref.get("sha256")
                != hashlib.sha256(
                    (self.repo / Path(*PurePosixPath(payload_ref["path"]).parts)).read_bytes()
                ).hexdigest()
            ):
                raise StaleCompletionError("STALE_COMPLETION")
            if connection.execute(
                "SELECT 1 FROM events WHERE event_id=?",
                (event["event_id"],),
            ).fetchone():
                raise StaleCompletionError("STALE_COMPLETION")
            connection.execute(
                "INSERT INTO inbox"
                "(event_id,task_id,dispatch_id,event_sha256,payload,status,created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    event["event_id"], row["task_id"],
                    result["dispatch_id"], event_sha256, event_text,
                    expected_status, self.now_fn(),
                ),
            )
            return {
                "event_id": event["event_id"],
                "status": "RESULT_SCHEMA_REPAIR",
            }

        try:
            response = self._mutate(operation)
        except _InboxAlreadyConsumed:
            response = {
                "event_id": event["event_id"],
                "status": "ALREADY_REJECTED",
            }
        self._publish_current_action()
        return response

    def _consume_result_schema_repair_ack(
        self,
        event: Mapping[str, Any],
        event_sha256: str,
        event_text: str,
        payload_raw: bytes,
        payload_sha256: str,
        profile_id: str,
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        action = self._current_action()
        if action.get("action") != "RESULT_SCHEMA_REPAIR":
            raise DeliveryError("REPAIR_ACTION_INACTIVE")
        action_raw = contract.canonical_json_bytes(action)
        action_sha256 = hashlib.sha256(action_raw).hexdigest()
        expected = {
            "action_id": action["action_id"],
            "action_sha256": action_sha256,
            "dispatch_id": action["dispatch_id"],
            "project_profile_id": profile_id,
            "work_order_id": action["work_order_id"],
            "work_order_sha256": action["work_order_sha256"],
            "worker_id": action["target_actor_id"],
        }
        try:
            ack = contract.validate_transport_ack(
                payload_raw, payload_sha256, expected
            )
        except contract.ContractError as exc:
            raise IdentityError(str(exc)) from exc
        if (
            ack["action"] != "RESULT_SCHEMA_REPAIR"
            or ack["ack_id"] != "ack-" + action_sha256[:32]
        ):
            raise IdentityError("TRANSPORT_ACK_IDENTITY_MISMATCH:action")

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            duplicate = connection.execute(
                "SELECT event_sha256,payload,status FROM inbox "
                "WHERE event_id=?",
                (event["event_id"],),
            ).fetchone()
            if duplicate:
                if (
                    duplicate["event_sha256"] == event_sha256
                    and duplicate["payload"] == event_text
                    and duplicate["status"] == "CONSUMED"
                ):
                    raise _InboxAlreadyConsumed()
                raise IdentityError("INBOX_EVENT_CONFLICT")
            actor = connection.execute(
                "SELECT role FROM actors WHERE actor_id=?",
                (event["source_actor_id"],),
            ).fetchone()
            rejected = connection.execute(
                "SELECT i.status,i.payload,d.status AS dispatch_status,"
                "d.sender_id AS dispatch_sender_id,"
                "t.status AS task_status,wo.status AS order_status "
                "FROM inbox i JOIN dispatches d "
                "ON d.dispatch_id=i.dispatch_id JOIN tasks t "
                "ON t.task_id=d.task_id JOIN work_orders wo "
                "ON wo.task_id=d.task_id WHERE i.event_id=? "
                "AND d.dispatch_id=?",
                (action["invalid_event_id"], action["dispatch_id"]),
            ).fetchone()
            if (
                actor is None
                or actor["role"] not in {"LINX", "LINKER"}
                or rejected is None
                or rejected["dispatch_sender_id"] != event["source_actor_id"]
                or rejected["status"] != f"REJECTED:{action['reason']}"
                or rejected["dispatch_status"] != "DISPATCHED"
                or rejected["task_status"] not in {"REGISTERED", "RETRY_READY"}
                or rejected["order_status"] != "CREATED"
            ):
                raise DeliveryError("REPAIR_ACTION_INACTIVE")
            try:
                rejected_envelope = json.loads(rejected["payload"])
            except (TypeError, json.JSONDecodeError) as exc:
                raise StateNotDurableError(
                    "REJECTED_RECEIPT_REGISTRY_INVALID"
                ) from exc
            if (
                rejected_envelope.get("payload_ref", {}).get("sha256")
                != action["invalid_result_sha256"]
            ):
                raise StateNotDurableError(
                    "REJECTED_RECEIPT_REGISTRY_INVALID"
                )
            connection.execute(
                "UPDATE inbox SET status=? WHERE event_id=?",
                (
                    f"REPAIR_ACKNOWLEDGED:{action['reason']}",
                    action["invalid_event_id"],
                ),
            )
            connection.execute(
                "INSERT INTO deliveries"
                "(dispatch_id,phase,method,result,created_at) "
                "VALUES(?,?,?,?,?)",
                (
                    action["dispatch_id"], "RESULT_SCHEMA_REPAIR",
                    "LINKER", "ACKNOWLEDGED", self.now_fn(),
                ),
            )
            connection.execute(
                "INSERT INTO inbox"
                "(event_id,task_id,dispatch_id,event_sha256,payload,status,created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    event["event_id"], action["task_id"],
                    action["dispatch_id"], event_sha256, event_text,
                    "CONSUMED", self.now_fn(),
                ),
            )
            return {
                "event_id": event["event_id"],
                "status": "CONSUMED",
            }

        try:
            response = self._mutate(operation)
        except _InboxAlreadyConsumed:
            response = {
                "event_id": event["event_id"],
                "status": "ALREADY_CONSUMED",
            }
        self._publish_current_action()
        return response

    def _resolve_registered_relative_file(
        self, root: Path, relative: str, error: str
    ) -> Path:
        try:
            normalized = self._normal_path(relative)
            resolved_root = root.resolve(strict=True)
            if (
                not resolved_root.is_dir()
                or self._is_reparse(resolved_root)
            ):
                raise ValueError("registered root")
            current = resolved_root
            parts = PurePosixPath(normalized).parts
            for index, part in enumerate(parts):
                current = current / part
                if (
                    not os.path.lexists(current)
                    or self._is_reparse(current)
                    or (index < len(parts) - 1 and not current.is_dir())
                ):
                    raise ValueError("registered path")
            resolved = self._resolve_under(
                resolved_root, resolved_root / Path(*parts)
            )
            if not resolved.is_file():
                raise ValueError("registered file")
            return resolved
        except (
            IdentityError,
            ScopeBreachError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            raise IdentityError(error) from exc

    def _resolve_registered_worker_outbox_event(
        self, event_file: str | Path
    ) -> tuple[sqlite3.Row, Path, str, Path]:
        raw_candidate = Path(event_file)
        if any(part == ".." for part in raw_candidate.parts):
            raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID")
        candidate = Path(os.path.abspath(raw_candidate))
        try:
            candidate_resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID") from exc
        if not candidate_resolved.is_file():
            raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID")
        connection = self._connect()
        try:
            self._schema(connection)
            rows = list(
                connection.execute(
                    "SELECT worktree_id,path FROM worktrees"
                )
            )
        finally:
            connection.close()
        contained_registered_root = False
        for row in rows:
            try:
                declared = Path(os.path.abspath(Path(row["path"])))
                if not declared.is_dir() or self._is_reparse(declared):
                    raise ValueError("registered root")
                try:
                    common = os.path.commonpath(
                        [
                            os.path.normcase(os.path.normpath(str(declared))),
                            os.path.normcase(os.path.normpath(str(candidate))),
                        ]
                    )
                except ValueError:
                    continue
                if common != os.path.normcase(os.path.normpath(str(declared))):
                    continue
                contained_registered_root = True
                root = declared.resolve(strict=True)
                if not root.is_dir() or self._is_reparse(root):
                    raise ValueError("registered root")
                relative = self._normal_path(
                    Path(os.path.relpath(candidate, declared)).as_posix()
                )
                parts = PurePosixPath(relative).parts
                if (
                    len(parts) != 6
                    or parts[0:2] != (".devad", "workers")
                    or parts[3] != "outbox"
                    or parts[5] != "inbox_event.json"
                ):
                    raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID")
                path = self._resolve_registered_relative_file(
                    root, relative, "WORKER_RESULT_EVENT_PATH_INVALID"
                )
                if path.resolve(strict=True) != candidate_resolved:
                    raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID")
                return row, root, relative, path
            except IdentityError:
                raise
            except (
                ScopeBreachError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as exc:
                if contained_registered_root:
                    raise IdentityError(
                        "WORKER_RESULT_EVENT_PATH_INVALID"
                    ) from exc
                continue
        raise IdentityError("WORKER_RESULT_WORKTREE_UNREGISTERED")

    def _validate_worker_result_ingest_proofs(
        self, root: Path, receipt: Mapping[str, Any]
    ) -> None:
        contract = _load_v7_contract()
        accepted: set[str] = set()
        try:
            proof_items = receipt.get("proof", [])
            if not isinstance(proof_items, list):
                raise ValueError("proof list")
            for item in proof_items:
                if not isinstance(item, Mapping):
                    raise ValueError("proof item")
                kind = item["kind"]
                relative = self._normal_path(item["path"])
                expected = self._normal_path(
                    f".devad/workers/{receipt['worker_id']}/proof/"
                    f"{receipt['event_id']}/{kind}.json"
                )
                if (
                    relative != expected
                    or relative in accepted
                    or item.get("sha256")
                    != self._require_sha256(
                        item.get("sha256"),
                        "WORKER_RESULT_PROOF_INVALID",
                    )
                ):
                    raise ValueError("proof identity")
                proof_path = self._resolve_registered_relative_file(
                    root, relative, "WORKER_RESULT_PROOF_INVALID"
                )
                proof_raw = proof_path.read_bytes()
                proof = json.loads(proof_raw)
                expected_proof = {
                    "dispatch_id": receipt["dispatch_id"],
                    "event_id": receipt["event_id"],
                    "kind": kind,
                    "schema": "x9-loop-proof-v2",
                    "status": "PASS",
                    "task_id": receipt["task_id"],
                    "work_order_id": receipt["work_order_id"],
                    "worker_id": receipt["worker_id"],
                }
                if (
                    hashlib.sha256(proof_raw).hexdigest() != item["sha256"]
                    or proof != expected_proof
                    or contract.canonical_json_bytes(proof) != proof_raw
                ):
                    raise ValueError("proof hash")
                accepted.add(relative)
        except (
            IdentityError,
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            contract.ContractError,
        ) as exc:
            raise IdentityError("WORKER_RESULT_PROOF_INVALID") from exc

    def _validate_worker_result_ingest_identity(
        self,
        *,
        root: Path,
        worktree_id: str,
        event: Mapping[str, Any],
        event_sha256: str,
        event_text: str,
        receipt: Mapping[str, Any],
        receipt_sha256: str,
    ) -> tuple[dict[str, str], str | None]:
        connection = self._connect()
        try:
            self._schema(connection)
            row = connection.execute(
                "SELECT a.role AS actor_role,t.task_id,t.worker_id,"
                "t.worktree_id,t.base_sha,t.status AS task_status,"
                "w.path AS worktree_path,wo.work_order_id,"
                "wo.packet_sha256 AS work_order_sha256,"
                "wo.status AS order_status,d.dispatch_id,d.target_id,"
                "d.packet_sha256,d.status AS dispatch_status,"
                "(SELECT dispatch_id FROM dispatches WHERE task_id=t.task_id "
                "ORDER BY rowid DESC LIMIT 1) AS latest_dispatch_id,"
                "i.event_sha256 AS inbox_event_sha256,"
                "i.payload AS inbox_payload,i.status AS inbox_status,"
                "e.event_sha256 AS recorded_result_sha256 "
                "FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "JOIN work_orders wo ON wo.task_id=t.task_id "
                "JOIN dispatches d ON d.dispatch_id=? AND d.task_id=t.task_id "
                "LEFT JOIN actors a ON a.actor_id=? "
                "LEFT JOIN inbox i ON i.event_id=? "
                "LEFT JOIN events e ON e.event_id=? AND e.task_id=t.task_id "
                "AND e.dispatch_id=d.dispatch_id "
                "WHERE t.task_id=? AND wo.work_order_id=?",
                (
                    receipt.get("dispatch_id"),
                    event.get("source_actor_id"),
                    event.get("event_id"),
                    event.get("event_id"),
                    receipt.get("task_id"),
                    receipt.get("work_order_id"),
                ),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise StaleCompletionError("STALE_COMPLETION")
        try:
            registered_root = Path(row["worktree_path"]).resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise StaleCompletionError("STALE_COMPLETION") from exc
        if (
            row["actor_role"] != "WORKER"
            or row["worker_id"] != event.get("source_actor_id")
            or row["worker_id"] != receipt.get("worker_id")
            or row["target_id"] != row["worker_id"]
            or row["worktree_id"] != worktree_id
            or registered_root != root.resolve(strict=True)
            or row["work_order_id"] != receipt.get("work_order_id")
            or row["work_order_sha256"] != receipt.get("work_order_sha256")
            or row["packet_sha256"] != receipt.get("packet_sha256")
        ):
            raise StaleCompletionError("STALE_COMPLETION")
        active = (
            row["dispatch_status"] == "DISPATCHED"
            and row["task_status"] in {"REGISTERED", "RETRY_READY"}
            and row["order_status"] == "CREATED"
            and row["latest_dispatch_id"] == row["dispatch_id"]
            and row["inbox_status"] is None
            and row["recorded_result_sha256"] is None
        )
        exact_inbox = (
            row["inbox_event_sha256"] == event_sha256
            and row["inbox_payload"] == event_text
        )
        terminal_replay = (
            exact_inbox
            and row["inbox_status"] == "CONSUMED"
            and row["dispatch_status"] == "COMPLETE"
            and row["task_status"] in {"COMPLETE", "SUPERSEDED"}
            and row["order_status"] == row["task_status"]
            and row["recorded_result_sha256"] == receipt_sha256
        )
        rejected_replay = (
            exact_inbox
            and isinstance(row["inbox_status"], str)
            and row["inbox_status"].startswith("REJECTED:")
            and row["dispatch_status"] == "DISPATCHED"
            and row["task_status"] in {"REGISTERED", "RETRY_READY"}
            and row["order_status"] == "CREATED"
            and row["latest_dispatch_id"] == row["dispatch_id"]
            and row["recorded_result_sha256"] is None
        )
        if row["inbox_status"] is not None and not exact_inbox:
            raise IdentityError("INBOX_EVENT_CONFLICT")
        if not (active or terminal_replay or rejected_replay):
            raise StaleCompletionError("STALE_COMPLETION")
        replay_status = None
        if terminal_replay:
            replay_status = "ALREADY_CONSUMED"
        elif rejected_replay:
            replay_status = "ALREADY_REJECTED"
        expected = {
            "dispatch_id": row["dispatch_id"],
            "event_id": event["event_id"],
            "packet_sha256": row["packet_sha256"],
            "task_id": row["task_id"],
            "work_order_id": row["work_order_id"],
            "work_order_sha256": row["work_order_sha256"],
            "worker_id": row["worker_id"],
        }
        return expected, replay_status

    def ingest_worker_result(
        self,
        event_file: str | Path,
        *,
        _receipt_entries_override: Mapping[str, str] | None = None,
        _preconsumption_result_ready_requester_id: str | None = None,
        _recovery_admission: Callable[[sqlite3.Connection], None] | None = None,
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        (
            worktree_row,
            worktree_root,
            outbox_relative,
            event_path,
        ) = self._resolve_registered_worker_outbox_event(event_file)
        try:
            event_raw = self._read_capped_packet(
                event_path, "INBOX_EVENT.json"
            )
            event_sha256 = hashlib.sha256(event_raw).hexdigest()
            event = contract.validate_inbox_event(
                event_raw, event_sha256, self._ensure_project_profile()
            )
        except contract.ContractError as exc:
            raise IdentityError(str(exc)) from exc
        except (LoopError, OSError, RuntimeError, TypeError, ValueError) as exc:
            raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID") from exc
        if (
            event["event_type"] != "WORKER_RESULT"
            or event["source_role"] != "WORKER"
        ):
            raise IdentityError("WORKER_RESULT_EVENT_TYPE_INVALID")
        expected_outbox = self._normal_path(
            f".devad/workers/{event['source_actor_id']}/outbox/"
            f"{event['event_id']}/INBOX_EVENT.json"
        )
        if outbox_relative != expected_outbox:
            raise IdentityError("WORKER_RESULT_EVENT_PATH_INVALID")
        try:
            receipt_relative = self._normal_path(
                contract.canonical_repo_path(event["payload_ref"]["path"])
            )
        except (ScopeBreachError, contract.ContractError) as exc:
            raise IdentityError("WORKER_RESULT_RECEIPT_PATH_INVALID") from exc
        expected_receipt = self._normal_path(
            f".devad/workers/{event['source_actor_id']}/receipts/"
            f"{event['event_id']}.json"
        )
        if receipt_relative != expected_receipt:
            raise IdentityError("WORKER_RESULT_RECEIPT_PATH_INVALID")
        receipt_path = self._resolve_registered_relative_file(
            worktree_root,
            receipt_relative,
            "WORKER_RESULT_RECEIPT_PATH_INVALID",
        )
        try:
            receipt_raw = self._read_capped_packet(receipt_path, "RESULT.json")
            receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()
            if receipt_sha256 != event["payload_ref"]["sha256"]:
                raise IdentityError("WORKER_RESULT_RECEIPT_HASH_MISMATCH")
            receipt = json.loads(receipt_raw)
            if (
                not isinstance(receipt, dict)
                or contract.canonical_json_bytes(receipt) != receipt_raw
                or receipt.get("event_id") != event["event_id"]
                or receipt.get("worker_id") != event["source_actor_id"]
                or receipt.get("role") != "WORKER"
            ):
                raise IdentityError("WORKER_RESULT_IDENTITY_INVALID")
        except IdentityError:
            raise
        except (
            contract.ContractError,
            LoopError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise IdentityError("WORKER_RESULT_RECEIPT_INVALID") from exc
        event_text = event_raw.decode("utf-8")
        expected, replay_status = self._validate_worker_result_ingest_identity(
            root=worktree_root,
            worktree_id=worktree_row["worktree_id"],
            event=event,
            event_sha256=event_sha256,
            event_text=event_text,
            receipt=receipt,
            receipt_sha256=receipt_sha256,
        )
        try:
            validated_receipt, _disposition = contract.validate_worker_result(
                receipt, expected
            )
        except contract.ContractError as exc:
            raise StaleCompletionError(exc.code) from exc
        if validated_receipt != receipt:
            raise IdentityError("WORKER_RESULT_CONTRACT_INVALID")
        self._validate_worker_result_ingest_proofs(
            worktree_root, validated_receipt
        )
        if replay_status is not None:
            self._publish_current_action()
            return {
                "event_id": event["event_id"],
                "status": replay_status,
            }
        return self.consume_event(
            {
                "actor_id": event["source_actor_id"],
                "dispatch_id": receipt["dispatch_id"],
                "event_id": event["event_id"],
                "event_type": "WORKER_RESULT",
                "packet_sha256": receipt["packet_sha256"],
                "result_path": receipt_relative,
                "result_sha256": receipt_sha256,
                "role": "WORKER",
                "task_id": receipt["task_id"],
            },
            _inbox_event={
                "dispatch_id": receipt["dispatch_id"],
                "event_id": event["event_id"],
                "event_sha256": event_sha256,
                "payload": event_text,
                "status": "CONSUMED",
            },
            _receipt_entries_override=_receipt_entries_override,
            _preconsumption_result_ready_requester_id=(
                _preconsumption_result_ready_requester_id
            ),
            _recovery_admission=_recovery_admission,
        )

    def recover_receipt_set_mismatch_worker_result(
        self, work_order_id: str, work_order_sha256: str, event_file: str | Path
    ) -> dict[str, Any]:
        """Admit one current Worker result after a typed receipt-set repair."""
        if (
            not isinstance(work_order_id, str)
            or not work_order_id
            or not isinstance(work_order_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", work_order_sha256) is None
        ):
            raise TaskNotReadyError("RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE")
        self._assert_durable()
        contract = _load_v7_contract()
        try:
            (
                worktree_row,
                worktree_root,
                _outbox_relative,
                event_path,
            ) = self._resolve_registered_worker_outbox_event(event_file)
            event_raw = self._read_capped_packet(
                event_path, "INBOX_EVENT.json"
            )
            event_sha256 = hashlib.sha256(event_raw).hexdigest()
            event = contract.validate_inbox_event(
                event_raw,
                event_sha256,
                self._ensure_project_profile(),
            )
            result_relative = self._normal_path(
                contract.canonical_repo_path(event["payload_ref"]["path"])
            )
            result_path = self._resolve_registered_relative_file(
                worktree_root,
                result_relative,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            )
            result_raw = self._read_capped_packet(result_path, "RESULT.json")
            result_sha256 = hashlib.sha256(result_raw).hexdigest()
            result = json.loads(result_raw)
        except (
            IdentityError,
            LoopError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            contract.ContractError,
        ) as exc:
            raise TaskNotReadyError(
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
            ) from exc
        if (
            event["event_type"] != "WORKER_RESULT"
            or event["source_role"] != "WORKER"
            or result_sha256 != event["payload_ref"]["sha256"]
            or result_relative
            != self._normal_path(
                f".devad/workers/{event['source_actor_id']}/receipts/"
                f"{event['event_id']}.json"
            )
            or not isinstance(result, dict)
            or contract.canonical_json_bytes(result) != result_raw
        ):
            raise TaskNotReadyError("RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE")

        try:
            current_order = self.verify_work_order(work_order_id)
        except (LoopError, OSError, ValueError) as exc:
            raise TaskNotReadyError(
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
            ) from exc
        if current_order.get("work_order_id") != work_order_id:
            raise TaskNotReadyError("RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE")

        def reject() -> None:
            raise TaskNotReadyError("RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE")

        def validate_terminal_history_compatibility(
            connection: sqlite3.Connection,
            target_row: sqlite3.Row,
            entries: Any,
        ) -> None:
            if not isinstance(entries, list):
                reject()
            seen: set[str] = set()
            seen_history_ids: set[str] = set()
            seen_task_ids: set[str] = set()
            seen_dispatch_ids: set[str] = set()
            seen_event_ids: set[str] = {event["event_id"]}
            seen_inbox_event_ids: set[str] = set()
            for entry in entries:
                if not isinstance(entry, str) or entry in seen:
                    reject()
                history_id, separator, markers = entry.partition(":")
                marker_values = markers.split("+") if separator else []
                if (
                    not history_id
                    or not separator
                    or not markers
                    or not marker_values
                    or any(
                        marker
                        not in {
                            "TERMINAL_HISTORY_CONTEXT_REF_BOUND",
                            "TERMINAL_HISTORY_CONTEXT_REF_UNAVAILABLE",
                            "TERMINAL_HISTORY_WORKER_RESULT_CONTRACT",
                        }
                        for marker in marker_values
                    )
                    or len(set(marker_values)) != len(marker_values)
                    or history_id in seen_history_ids
                    or history_id == target_row["work_order_id"]
                ):
                    reject()
                history = connection.execute(
                    "SELECT wo.work_order_id,wo.packet_path,wo.packet_sha256,"
                    "wo.status AS order_status,t.task_id,t.worker_id,"
                    "t.status AS task_status,t.worktree_id,w.path AS worktree_path "
                    "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                    "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                    "WHERE wo.work_order_id=?",
                    (history_id,),
                ).fetchone()
                if history is None:
                    reject()
                if (
                    history["task_id"] in seen_task_ids
                    or history["task_id"] == target_row["task_id"]
                    or connection.execute(
                        "SELECT COUNT(*) FROM work_orders WHERE task_id=?",
                        (history["task_id"],),
                    ).fetchone()[0]
                    != 1
                ):
                    reject()
                try:
                    history_root = Path(
                        history["worktree_path"]
                    ).resolve(strict=True)
                except (OSError, RuntimeError, TypeError, ValueError):
                    reject()
                if (
                    not Path(history["worktree_path"]).is_absolute()
                    or not history_root.is_dir()
                ):
                    reject()
                active_dispatches = connection.execute(
                    "SELECT COUNT(*) FROM dispatches WHERE task_id=? "
                    "AND status IN ('PREPARED','DISPATCHED')",
                    (history["task_id"],),
                ).fetchone()[0]
                if (
                    (
                        history["task_status"], history["order_status"]
                    ) not in TERMINAL_TASK_ORDER_STATUS_PAIRS
                    or active_dispatches != 0
                ):
                    reject()
                dispatch_rows = list(
                    connection.execute(
                        "SELECT d.*,sa.role AS sender_role,"
                        "ta.role AS target_role "
                        "FROM dispatches d "
                        "LEFT JOIN actors sa ON sa.actor_id=d.sender_id "
                        "LEFT JOIN actors ta ON ta.actor_id=d.target_id "
                        "WHERE d.task_id=? ORDER BY d.rowid",
                        (history["task_id"],),
                    )
                )
                if not dispatch_rows:
                    reject()
                history_dispatch_ids: set[str] = set()
                for dispatch in dispatch_rows:
                    dispatch_id = dispatch["dispatch_id"]
                    if (
                        not isinstance(dispatch_id, str)
                        or dispatch_id in history_dispatch_ids
                        or dispatch_id in seen_dispatch_ids
                        or dispatch_id == target_row["dispatch_id"]
                        or dispatch["status"]
                        not in {"COMPLETE", "SUPERSEDED"}
                        or dispatch["target_id"] != history["worker_id"]
                        or dispatch["target_role"] != "WORKER"
                        or dispatch["sender_role"] not in {"LINX", "LINKER"}
                        or dispatch["packet_sha256"] != history["packet_sha256"]
                    ):
                        reject()
                    expected_dispatch_packet = {
                        "schema": "x9-loop-work-order-dispatch-v1",
                        "task_id": history["task_id"],
                        "work_order_path": history["packet_path"],
                        "work_order_sha256": history["packet_sha256"],
                    }
                    try:
                        dispatch_packet = json.loads(dispatch["packet"])
                    except (TypeError, ValueError, json.JSONDecodeError):
                        reject()
                    if (
                        dispatch_packet != expected_dispatch_packet
                        or _json(dispatch_packet) != dispatch["packet"]
                    ):
                        reject()
                    history_dispatch_ids.add(dispatch_id)
                if (
                    connection.execute(
                        "SELECT 1 FROM tasks WHERE worktree_id=? "
                        "AND task_id NOT IN (?,?) "
                        "AND status NOT IN ('COMPLETE','SUPERSEDED')",
                        (
                            history["worktree_id"],
                            history["task_id"],
                            target_row["task_id"],
                        ),
                    ).fetchone()
                    is not None
                    or connection.execute(
                        "SELECT 1 FROM claims c JOIN tasks t "
                        "ON t.task_id=c.task_id WHERE c.task_id=? "
                        "AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
                        (history["task_id"],),
                    ).fetchone()
                    is not None
                    or connection.execute(
                        "SELECT 1 FROM resources r JOIN tasks t "
                        "ON t.task_id=r.task_id WHERE r.task_id=? "
                        "AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
                        (history["task_id"],),
                    ).fetchone()
                    is not None
                ):
                    reject()
                placeholders = ",".join("?" for _ in history_dispatch_ids)
                delivery_rows = connection.execute(
                    "SELECT phase,result FROM deliveries WHERE dispatch_id IN ("
                    + placeholders
                    + ")",
                    tuple(history_dispatch_ids),
                )
                for delivery in delivery_rows:
                    phase = str(delivery["phase"]).upper()
                    result_value = str(delivery["result"]).casefold()
                    if phase not in {"DISPATCH", "CALLBACK", "REVIEW"}:
                        reject()
                    if phase == "DISPATCH" and result_value not in {
                        "ack",
                        "acknowledged",
                    }:
                        reject()
                    if phase in {"CALLBACK", "REVIEW"} and result_value not in {
                        "ack",
                        "acknowledged",
                        "failed",
                    }:
                        reject()
                reservations = connection.execute(
                    "SELECT status FROM call_reservations "
                    "WHERE work_order_id=?",
                    (history_id,),
                )
                if any(row["status"] != "RECORDED" for row in reservations):
                    reject()
                dispatch_by_id = {
                    row["dispatch_id"]: row for row in dispatch_rows
                }
                event_rows = list(
                    connection.execute(
                        "SELECT event_id,task_id,dispatch_id,event_sha256 "
                        "FROM events WHERE task_id=?",
                        (history["task_id"],),
                    )
                )
                events_by_id: dict[str, sqlite3.Row] = {}
                for event_row in event_rows:
                    event_id = event_row["event_id"]
                    if (
                        not isinstance(event_id, str)
                        or event_id in events_by_id
                        or event_id in seen_event_ids
                        or event_row["task_id"] != history["task_id"]
                        or event_row["dispatch_id"]
                        not in history_dispatch_ids
                        or not isinstance(event_row["event_sha256"], str)
                        or re.fullmatch(
                            r"[0-9a-f]{64}", event_row["event_sha256"]
                        ) is None
                    ):
                        reject()
                    events_by_id[event_id] = event_row

                inbox_rows = list(
                    connection.execute(
                        "SELECT event_id,task_id,dispatch_id,event_sha256,payload,status "
                        "FROM inbox WHERE task_id=?",
                        (history["task_id"],),
                    )
                )
                inbox_by_id: dict[str, sqlite3.Row] = {}
                inbox_envelopes: dict[str, dict[str, Any]] = {}
                for inbox_row in inbox_rows:
                    event_id = inbox_row["event_id"]
                    status = inbox_row["status"]
                    if not isinstance(status, str):
                        reject()
                    if status != "CONSUMED":
                        if not (
                            status.startswith("REJECTED:")
                            or status.startswith("REPAIR_ACKNOWLEDGED:")
                        ):
                            reject()
                        if event_id in seen_event_ids:
                            reject()
                        continue
                    if (
                        not isinstance(event_id, str)
                        or event_id in inbox_by_id
                        or event_id in seen_inbox_event_ids
                        or event_id in seen_event_ids
                        or inbox_row["task_id"] != history["task_id"]
                        or inbox_row["dispatch_id"]
                        not in history_dispatch_ids
                        or not isinstance(inbox_row["payload"], str)
                    ):
                        reject()
                    try:
                        envelope = contract.validate_inbox_event(
                            inbox_row["payload"].encode("utf-8"),
                            inbox_row["event_sha256"],
                            self._ensure_project_profile(),
                        )
                    except (
                        AttributeError,
                        TypeError,
                        UnicodeEncodeError,
                        ValueError,
                        contract.ContractError,
                    ):
                        reject()
                    dispatch = dispatch_by_id[inbox_row["dispatch_id"]]
                    actor = connection.execute(
                        "SELECT role FROM actors WHERE actor_id=?",
                        (envelope["source_actor_id"],),
                    ).fetchone()
                    expected_source_role = {
                        "TRANSPORT_ACK": "LINKER",
                        "THINX_RESULT": "THINKER",
                        "WORKER_RESULT": "WORKER",
                    }[envelope["event_type"]]
                    if (
                        envelope["event_id"] != event_id
                        or actor is None
                        or envelope["source_role"] != expected_source_role
                        or (
                            envelope["event_type"] == "TRANSPORT_ACK"
                            and (
                                envelope["source_actor_id"]
                                != dispatch["sender_id"]
                                or actor["role"] != dispatch["sender_role"]
                                or actor["role"] not in {"LINX", "LINKER"}
                            )
                        )
                        or (
                            envelope["event_type"] == "WORKER_RESULT"
                            and (
                                envelope["source_actor_id"]
                                != history["worker_id"]
                                or actor["role"] != "WORKER"
                                or dispatch["target_id"]
                                != history["worker_id"]
                            )
                        )
                        or (
                            envelope["event_type"] == "THINX_RESULT"
                            and actor["role"] not in {"THINX", "THINKER"}
                        )
                    ):
                        reject()
                    inbox_by_id[event_id] = inbox_row
                    inbox_envelopes[event_id] = envelope

                def historical_repair_actions(
                    dispatch: sqlite3.Row,
                ) -> list[dict[str, Any]]:
                    action_fields = {
                        "action",
                        "action_id",
                        "attempt",
                        "dispatch_id",
                        "must_record_transport",
                        "project_profile_id",
                        "schema",
                        "target_actor_id",
                        "target_role",
                        "task_id",
                        "work_order_id",
                        "work_order_path",
                        "work_order_sha256",
                    }
                    outbox = connection.execute(
                        "SELECT payload FROM outbox WHERE dispatch_id=?",
                        (dispatch["dispatch_id"],),
                    ).fetchone()
                    if outbox is None:
                        reject()
                    try:
                        original_action = json.loads(outbox["payload"])
                    except (
                        TypeError,
                        ValueError,
                        json.JSONDecodeError,
                    ):
                        reject()
                    if (
                        not isinstance(original_action, dict)
                        or set(original_action) != action_fields
                        or original_action.get("action") != "SEND_WORK_ORDER"
                        or original_action.get("schema") != "x9-loop-action-v2"
                        or original_action.get("dispatch_id")
                        != dispatch["dispatch_id"]
                        or original_action.get("task_id")
                        != history["task_id"]
                        or original_action.get("work_order_id")
                        != history["work_order_id"]
                        or original_action.get("work_order_path")
                        != history["packet_path"]
                        or original_action.get("work_order_sha256")
                        != history["packet_sha256"]
                        or original_action.get("target_actor_id")
                        != history["worker_id"]
                        or original_action.get("target_role") != "WORKER"
                        or original_action.get("project_profile_id")
                        != self._ensure_project_profile()
                        or original_action.get("must_record_transport") is not True
                        or not isinstance(original_action.get("action_id"), str)
                        or re.fullmatch(
                            r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}",
                            original_action["action_id"],
                        ) is None
                        or not isinstance(original_action.get("attempt"), int)
                        or isinstance(original_action.get("attempt"), bool)
                        or original_action["attempt"] < 1
                    ):
                        reject()
                    try:
                        canonical_action = (
                            contract.canonical_json_bytes(original_action)
                            .decode("utf-8")
                            .rstrip("\n")
                        )
                    except (TypeError, ValueError, contract.ContractError):
                        reject()
                    if canonical_action != outbox["payload"]:
                        reject()
                    actions: list[dict[str, Any]] = [original_action]
                    repair_rows = connection.execute(
                        "SELECT event_id,event_sha256,payload,status "
                        "FROM inbox WHERE task_id=? AND dispatch_id=? "
                        "AND (status LIKE 'REJECTED:%' "
                        "OR status LIKE 'REPAIR_ACKNOWLEDGED:%')",
                        (history["task_id"], dispatch["dispatch_id"]),
                    )
                    for repair_row in repair_rows:
                        try:
                            repair_envelope = contract.validate_inbox_event(
                                repair_row["payload"].encode("utf-8"),
                                repair_row["event_sha256"],
                                self._ensure_project_profile(),
                            )
                        except (
                            AttributeError,
                            TypeError,
                            UnicodeEncodeError,
                            ValueError,
                            contract.ContractError,
                        ):
                            reject()
                        if (
                            repair_envelope["event_id"] != repair_row["event_id"]
                            or repair_envelope["event_type"] != "WORKER_RESULT"
                            or repair_envelope["source_actor_id"]
                            != history["worker_id"]
                            or repair_envelope["source_role"] != "WORKER"
                        ):
                            reject()
                        reason = repair_row["status"].partition(":")[2]
                        if not reason:
                            reject()
                        seed = {
                            "dispatch_id": dispatch["dispatch_id"],
                            "event_id": repair_row["event_id"],
                            "result_sha256": repair_envelope[
                                "payload_ref"
                            ]["sha256"],
                        }
                        action_digest = _sha(seed)[:32]
                        action_uuid = "-".join(
                            (
                                action_digest[:8],
                                action_digest[8:12],
                                action_digest[12:16],
                                action_digest[16:20],
                                action_digest[20:],
                            )
                        )
                        actions.append(
                            {
                                "action": "RESULT_SCHEMA_REPAIR",
                                "action_id": "act-" + action_uuid,
                                "attempt": original_action.get("attempt", 1),
                                "dispatch_id": dispatch["dispatch_id"],
                                "expected_result_schema": "x9-loop-result-v2",
                                "invalid_event_id": repair_row["event_id"],
                                "invalid_result_sha256": repair_envelope[
                                    "payload_ref"
                                ]["sha256"],
                                "must_record_transport": True,
                                "project_profile_id": self._ensure_project_profile(),
                                "reason": reason,
                                "schema": "x9-loop-action-v2",
                                "target_actor_id": history["worker_id"],
                                "target_role": "WORKER",
                                "task_id": history["task_id"],
                                "work_order_id": history["work_order_id"],
                                "work_order_path": history["packet_path"],
                                "work_order_sha256": history["packet_sha256"],
                            }
                        )
                    return actions

                def validate_historical_payload(
                    inbox_row: sqlite3.Row,
                    envelope: dict[str, Any],
                    dispatch: sqlite3.Row,
                ) -> str:
                    payload_ref = envelope["payload_ref"]
                    payload_relative = self._normal_path(
                        contract.canonical_repo_path(payload_ref["path"])
                    )
                    if envelope["event_type"] == "TRANSPORT_ACK":
                        expected_relative = self._normal_path(
                            f"runtime/inbox/{envelope['event_id']}"
                            "/TRANSPORT_ACK.json"
                        )
                        if payload_relative != expected_relative:
                            reject()
                        payload_path = self._safe_state_path(
                            self.repo
                            / Path(*PurePosixPath(payload_relative).parts)
                        )
                        payload_raw = self._read_capped_packet(
                            payload_path, "TRANSPORT_ACK.json"
                        )
                    else:
                        expected_relative = self._normal_path(
                            f".devad/workers/"
                            f"{envelope['source_actor_id']}/receipts/"
                            f"{envelope['event_id']}.json"
                        )
                        if payload_relative != expected_relative:
                            reject()
                        payload_path = self._resolve_registered_relative_file(
                            history_root,
                            payload_relative,
                            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
                        )
                        payload_raw = self._read_capped_packet(
                            payload_path, "RESULT.json"
                        )
                    payload_sha256 = hashlib.sha256(payload_raw).hexdigest()
                    if payload_sha256 != payload_ref["sha256"]:
                        reject()
                    try:
                        payload = json.loads(payload_raw)
                        if contract.canonical_json_bytes(payload) != payload_raw:
                            reject()
                    except (
                        contract.ContractError,
                        UnicodeDecodeError,
                        TypeError,
                        ValueError,
                        json.JSONDecodeError,
                    ):
                        reject()
                    if envelope["event_type"] == "TRANSPORT_ACK":
                        for action in historical_repair_actions(dispatch):
                            action_raw = contract.canonical_json_bytes(action)
                            action_sha256 = hashlib.sha256(action_raw).hexdigest()
                            expected_ack = {
                                "action_id": action["action_id"],
                                "action_sha256": action_sha256,
                                "dispatch_id": dispatch["dispatch_id"],
                                "project_profile_id": self._ensure_project_profile(),
                                "work_order_id": history["work_order_id"],
                                "work_order_sha256": history["packet_sha256"],
                                "worker_id": history["worker_id"],
                            }
                            try:
                                ack = contract.validate_transport_ack(
                                    payload_raw,
                                    payload_sha256,
                                    expected_ack,
                                )
                            except contract.ContractError:
                                continue
                            if (
                                ack["action"] == action.get("action")
                                and ack["ack_id"]
                                == "ack-" + action_sha256[:32]
                                and ack == payload
                            ):
                                return payload_sha256
                        reject()
                    elif envelope["event_type"] == "WORKER_RESULT":
                        expected_result = {
                            "dispatch_id": dispatch["dispatch_id"],
                            "event_id": envelope["event_id"],
                            "packet_sha256": history["packet_sha256"],
                            "task_id": history["task_id"],
                            "work_order_id": history["work_order_id"],
                            "work_order_sha256": history["packet_sha256"],
                            "worker_id": history["worker_id"],
                        }
                        try:
                            validated, _ = contract.validate_worker_result(
                                payload, expected_result
                            )
                            if validated != payload:
                                reject()
                            self._validate_worker_result_ingest_proofs(
                                history_root, validated
                            )
                        except (
                            IdentityError,
                            OSError,
                            RuntimeError,
                            TypeError,
                            ValueError,
                            json.JSONDecodeError,
                            contract.ContractError,
                        ):
                            reject()
                    else:
                        worker_event_id = payload.get("worker_event_id")
                        worker_event = events_by_id.get(worker_event_id)
                        worker_envelope = inbox_envelopes.get(worker_event_id)
                        if (
                            not isinstance(worker_event_id, str)
                            or worker_event is None
                            or worker_envelope is None
                            or worker_envelope["event_type"] != "WORKER_RESULT"
                            or worker_event["dispatch_id"]
                            != dispatch["dispatch_id"]
                            or worker_event["event_sha256"]
                            != payload.get("worker_result_sha256")
                        ):
                            reject()
                        expected_decision = {
                            "actor_id": envelope["source_actor_id"],
                            "dispatch_id": dispatch["dispatch_id"],
                            "event_id": envelope["event_id"],
                            "packet_sha256": history["packet_sha256"],
                            "task_id": history["task_id"],
                            "worker_event_id": worker_event_id,
                            "worker_result_sha256": worker_event["event_sha256"],
                            "work_order_id": history["work_order_id"],
                            "work_order_sha256": history["packet_sha256"],
                        }
                        try:
                            validated = contract.validate_thinx_decision(
                                payload, expected_decision
                            )
                        except contract.ContractError:
                            reject()
                        if validated != payload:
                            reject()
                    return payload_sha256

                for event_id, event_row in events_by_id.items():
                    inbox_row = inbox_by_id.get(event_id)
                    if inbox_row is None:
                        reject()
                    if (
                        event_row["task_id"] != inbox_row["task_id"]
                        or event_row["dispatch_id"]
                        != inbox_row["dispatch_id"]
                        or event_row["event_sha256"]
                        != inbox_envelopes[event_id]["payload_ref"]["sha256"]
                        or inbox_envelopes[event_id]["event_type"]
                        == "TRANSPORT_ACK"
                    ):
                        reject()

                for event_id, inbox_row in inbox_by_id.items():
                    envelope = inbox_envelopes[event_id]
                    dispatch = dispatch_by_id.get(inbox_row["dispatch_id"])
                    if dispatch is None:
                        reject()
                    validate_historical_payload(
                        inbox_row, envelope, dispatch
                    )
                    if (
                        envelope["event_type"] != "TRANSPORT_ACK"
                        and event_id not in events_by_id
                    ):
                        reject()

                history_event_ids = set(events_by_id) | set(inbox_by_id)
                if history_event_ids & seen_event_ids:
                    reject()
                inbox_event_ids = set(inbox_by_id)
                seen_event_ids.update(history_event_ids)
                seen_inbox_event_ids.update(inbox_event_ids)
                try:
                    _validated, compatibility = self._verify_work_order(
                        history_id,
                        allow_terminal_historical_contract=True,
                    )
                except (LoopError, OSError, ValueError):
                    reject()
                if compatibility != entry:
                    reject()
                seen_history_ids.add(history_id)
                seen_task_ids.add(history["task_id"])
                seen_dispatch_ids.update(history_dispatch_ids)
                seen.add(entry)

            receipts_root = worktree_root / ".devad" / "workers"
            seen_receipt_paths: set[str] = set()
            seen_receipt_digests: set[str] = {result_sha256}
            seen_receipt_event_ids: set[str] = {event["event_id"]}
            if receipts_root.is_dir():
                for candidate in receipts_root.glob("*/receipts/*.json"):
                    try:
                        receipt_path = self._resolve_registered_relative_file(
                            worktree_root,
                            candidate.relative_to(worktree_root).as_posix(),
                            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
                        )
                        relative = self._normal_path(
                            receipt_path.relative_to(worktree_root).as_posix()
                        )
                        raw = self._read_capped_packet(
                            receipt_path, "RESULT.json"
                        )
                        digest = hashlib.sha256(raw).hexdigest()
                        receipt = json.loads(raw)
                    except (
                        OSError,
                        RuntimeError,
                        TypeError,
                        ValueError,
                        json.JSONDecodeError,
                    ):
                        reject()
                    if (
                        not isinstance(receipt, dict)
                        or receipt_path.stem != receipt.get("event_id")
                        or contract.canonical_json_bytes(receipt) != raw
                    ):
                        reject()
                    if relative == result_relative:
                        if digest != result_sha256:
                            reject()
                        continue
                    receipt_event_id = receipt.get("event_id")
                    if (
                        not isinstance(receipt_event_id, str)
                        or relative in seen_receipt_paths
                        or digest in seen_receipt_digests
                        or receipt_event_id in seen_receipt_event_ids
                    ):
                        reject()
                    seen_receipt_paths.add(relative)
                    seen_receipt_digests.add(digest)
                    seen_receipt_event_ids.add(receipt_event_id)

        def rejected_entries(
            connection: sqlite3.Connection,
            worker_id: str,
        ) -> dict[str, list[dict[str, Any]]]:
            entries: dict[str, list[dict[str, Any]]] = {}
            rows = connection.execute(
                "SELECT i.event_id,i.task_id,i.dispatch_id,i.event_sha256,"
                "i.payload,i.status,t.worker_id,t.worktree_id,"
                "w.path AS worktree_path,d.sender_id,d.target_id,"
                "d.packet_sha256 AS dispatch_packet_sha256,"
                "d.status AS dispatch_status,wo.work_order_id,"
                "wo.packet_sha256 AS work_order_sha256 "
                "FROM inbox i JOIN tasks t ON t.task_id=i.task_id "
                "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "JOIN dispatches d ON d.dispatch_id=i.dispatch_id "
                "AND d.task_id=t.task_id JOIN work_orders wo "
                "ON wo.task_id=t.task_id "
                "WHERE i.status LIKE 'REJECTED:%' "
                "OR i.status LIKE 'REPAIR_ACKNOWLEDGED:%'"
            )
            for row in rows:
                try:
                    root = Path(row["worktree_path"]).resolve(strict=True)
                    if root != worktree_root.resolve(strict=True):
                        continue
                    raw = row["payload"].encode("utf-8")
                    envelope = contract.validate_inbox_event(
                        raw,
                        row["event_sha256"],
                        self._ensure_project_profile(),
                    )
                    relative = self._normal_path(
                        envelope["payload_ref"]["path"]
                    )
                    if (
                        envelope["event_type"] != "WORKER_RESULT"
                        or envelope["source_role"] != "WORKER"
                        or envelope["source_actor_id"] != worker_id
                        or envelope["event_id"] != row["event_id"]
                        or row["worker_id"] != worker_id
                        or relative
                        != self._normal_path(
                            f".devad/workers/{worker_id}/receipts/"
                            f"{row['event_id']}.json"
                        )
                    ):
                        reject()
                    receipt_path = self._resolve_registered_relative_file(
                        worktree_root,
                        relative,
                        "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
                    )
                    receipt_raw = self._read_capped_packet(
                        receipt_path, "RESULT.json"
                    )
                    digest = hashlib.sha256(receipt_raw).hexdigest()
                    if digest != envelope["payload_ref"]["sha256"]:
                        reject()
                    receipt = json.loads(receipt_raw)
                    if (
                        not isinstance(receipt, dict)
                        or contract.canonical_json_bytes(receipt)
                        != receipt_raw
                        or receipt.get("event_id") != row["event_id"]
                        or receipt.get("worker_id") != worker_id
                    ):
                        reject()
                    if connection.execute(
                        "SELECT 1 FROM events WHERE event_id=?",
                        (row["event_id"],),
                    ).fetchone() is not None:
                        reject()
                    record = {
                        "digest": digest,
                        "event_id": row["event_id"],
                        "task_id": row["task_id"],
                        "dispatch_id": row["dispatch_id"],
                        "work_order_id": row["work_order_id"],
                        "work_order_sha256": row["work_order_sha256"],
                        "dispatch_packet_sha256": row[
                            "dispatch_packet_sha256"
                        ],
                    }
                    existing = entries.setdefault(relative, [])
                    if any(item != record for item in existing):
                        reject()
                    existing.append(record)
                except TaskNotReadyError:
                    raise
                except (
                    OSError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                    json.JSONDecodeError,
                    contract.ContractError,
                ) as exc:
                    raise TaskNotReadyError(
                        "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                    ) from exc
            return entries

        def admission(
            connection: sqlite3.Connection,
            terminal_history_compatibility: Any,
        ) -> dict[str, Any]:
            try:
                receipt_dispatch_id = result.get("dispatch_id")
                if not isinstance(receipt_dispatch_id, str):
                    reject()
                rows = list(
                    connection.execute(
                        "SELECT wo.work_order_id,wo.packet_path,"
                        "wo.packet_sha256,wo.status AS order_status,"
                        "t.task_id,t.worker_id,t.worktree_id,"
                        "t.base_sha,t.status AS task_status,"
                        "d.dispatch_id,d.sender_id,d.target_id,"
                        "d.packet_sha256 AS dispatch_packet_sha256,"
                        "d.packet AS dispatch_packet,"
                        "d.status AS dispatch_status,"
                        "w.path AS worktree_path,"
                        "sa.role AS sender_role,ta.role AS target_role "
                        "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                        "JOIN dispatches d ON d.dispatch_id=? "
                        "AND d.task_id=t.task_id JOIN worktrees w "
                        "ON w.worktree_id=t.worktree_id "
                        "LEFT JOIN actors sa ON sa.actor_id=d.sender_id "
                        "LEFT JOIN actors ta ON ta.actor_id=d.target_id "
                        "WHERE wo.work_order_id=?",
                        (receipt_dispatch_id, work_order_id),
                    )
                )
                if len(rows) != 1:
                    reject()
                row = rows[0]
                if (
                    row["packet_sha256"] != work_order_sha256
                    or row["dispatch_packet_sha256"] != work_order_sha256
                    or row["task_id"] != current_order["task_id"]
                    or row["worker_id"] != current_order["worker_id"]
                    or row["worker_id"] != event["source_actor_id"]
                    or row["worktree_id"] != worktree_row["worktree_id"]
                    or Path(row["worktree_path"]).resolve(strict=True)
                    != worktree_root.resolve(strict=True)
                    or row["target_id"] != row["worker_id"]
                    or row["target_role"] != "WORKER"
                    or row["sender_role"] not in {"LINX", "LINKER"}
                    or row["task_status"] not in {"REGISTERED", "RETRY_READY"}
                    or row["order_status"] != "CREATED"
                    or row["dispatch_status"] != "DISPATCHED"
                    or result.get("task_id") != row["task_id"]
                    or result.get("work_order_id") != row["work_order_id"]
                    or result.get("work_order_sha256") != work_order_sha256
                    or result.get("worker_id") != row["worker_id"]
                    or result.get("packet_sha256") != work_order_sha256
                ):
                    reject()
                dispatch_packet = json.loads(row["dispatch_packet"])
                expected_dispatch_packet = {
                    "schema": "x9-loop-work-order-dispatch-v1",
                    "task_id": row["task_id"],
                    "work_order_path": row["packet_path"],
                    "work_order_sha256": work_order_sha256,
                }
                if (
                    dispatch_packet != expected_dispatch_packet
                    or _json(dispatch_packet) != row["dispatch_packet"]
                ):
                    reject()
                dispatch_count = connection.execute(
                    "SELECT COUNT(*) FROM dispatches WHERE task_id=?",
                    (row["task_id"],),
                ).fetchone()[0]
                latest = connection.execute(
                    "SELECT dispatch_id FROM dispatches WHERE task_id=? "
                    "ORDER BY rowid DESC LIMIT 1",
                    (row["task_id"],),
                ).fetchone()
                if (
                    dispatch_count != 1
                    or latest is None
                    or latest["dispatch_id"] != row["dispatch_id"]
                ):
                    reject()
                if connection.execute(
                    "SELECT 1 FROM events WHERE task_id=? OR dispatch_id=?",
                    (row["task_id"], row["dispatch_id"]),
                ).fetchone() is not None:
                    reject()
                if connection.execute(
                    "SELECT 1 FROM inbox WHERE task_id=? "
                    "AND status NOT LIKE 'REJECTED:%' "
                    "AND status NOT LIKE 'REPAIR_ACKNOWLEDGED:%'",
                    (row["task_id"],),
                ).fetchone() is not None:
                    reject()
                if connection.execute(
                    "SELECT 1 FROM call_receipts WHERE work_order_id=? "
                    "UNION ALL SELECT 1 FROM call_reservations "
                    "WHERE work_order_id=?",
                    (work_order_id, work_order_id),
                ).fetchone() is not None:
                    reject()
                if connection.execute(
                    "SELECT 1 FROM deliveries WHERE dispatch_id=? "
                    "AND phase<>'DISPATCH'",
                    (row["dispatch_id"],),
                ).fetchone() is not None:
                    reject()
                validate_terminal_history_compatibility(
                    connection, row, terminal_history_compatibility
                )
                if connection.execute(
                    "SELECT 1 FROM tasks WHERE worktree_id=? "
                    "AND task_id<>? AND status NOT IN ('COMPLETE','SUPERSEDED')",
                    (row["worktree_id"], row["task_id"]),
                ).fetchone() is not None:
                    reject()

                rejected = rejected_entries(
                    connection, row["worker_id"]
                )
                accepted: dict[str, str] = {}
                unfinalized: dict[str, str] = {}
                seen_rejected: set[str] = set()
                fresh_seen = False
                receipts_root = worktree_root / ".devad" / "workers"
                candidates = (
                    receipts_root.glob("*/receipts/*.json")
                    if receipts_root.is_dir()
                    else ()
                )
                expected_current = {
                    "dispatch_id": row["dispatch_id"],
                    "event_id": event["event_id"],
                    "packet_sha256": work_order_sha256,
                    "task_id": row["task_id"],
                    "work_order_id": work_order_id,
                    "work_order_sha256": work_order_sha256,
                    "worker_id": row["worker_id"],
                }

                def validate_scope(receipt_value: Mapping[str, Any]) -> None:
                    changed = {
                        self._normal_path(path)
                        for path in receipt_value.get("changed_files", [])
                    }
                    if len(changed) != len(receipt_value.get("changed_files", [])):
                        reject()
                    for path in changed:
                        if not self._claimed(
                            connection, row["task_id"], path
                        ):
                            reject()

                for candidate in candidates:
                    try:
                        receipt_path = self._resolve_registered_relative_file(
                            worktree_root,
                            candidate.relative_to(worktree_root).as_posix(),
                            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
                        )
                        relative = self._normal_path(
                            receipt_path.relative_to(worktree_root).as_posix()
                        )
                        raw = self._read_capped_packet(
                            receipt_path, "RESULT.json"
                        )
                        digest = hashlib.sha256(raw).hexdigest()
                        receipt = json.loads(raw)
                        parts = PurePosixPath(relative).parts
                        if (
                            len(parts) != 5
                            or parts[:2] != (".devad", "workers")
                            or parts[3] != "receipts"
                            or parts[2] != row["worker_id"]
                            or not isinstance(receipt, dict)
                            or receipt_path.stem != receipt.get("event_id")
                            or contract.canonical_json_bytes(receipt) != raw
                        ):
                            reject()
                    except TaskNotReadyError:
                        raise
                    except (
                        OSError,
                        RuntimeError,
                        TypeError,
                        ValueError,
                        json.JSONDecodeError,
                        contract.ContractError,
                    ) as exc:
                        raise TaskNotReadyError(
                            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                        ) from exc

                    if relative == result_relative:
                        fresh_seen = True
                        if (
                            digest != result_sha256
                            or receipt != result
                            or receipt.get("event_id") != event["event_id"]
                        ):
                            reject()
                        try:
                            validated, _ = contract.validate_worker_result(
                                receipt,
                                expected_current,
                                require_proof_bound_approaches=(
                                    "autonomy_contract" in current_order
                                ),
                            )
                            self._validate_worker_result_ingest_proofs(
                                worktree_root, validated
                            )
                            validate_scope(validated)
                        except (IdentityError, contract.ContractError) as exc:
                            raise TaskNotReadyError(
                                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                            ) from exc
                        continue

                    if relative in rejected:
                        if relative in seen_rejected:
                            reject()
                        if len(rejected[relative]) != 1:
                            reject()
                        metadata = rejected[relative][0]
                        expected_rejected = {
                            "dispatch_id": metadata["dispatch_id"],
                            "event_id": metadata["event_id"],
                            "packet_sha256": metadata[
                                "dispatch_packet_sha256"
                            ],
                            "task_id": metadata["task_id"],
                            "work_order_id": metadata["work_order_id"],
                            "work_order_sha256": metadata[
                                "work_order_sha256"
                            ],
                            "worker_id": row["worker_id"],
                        }
                        if digest != metadata["digest"]:
                            reject()
                        if receipt.get("schema") == "x9-loop-result-v2":
                            try:
                                validated, _ = contract.validate_worker_result(
                                    receipt, expected_rejected
                                )
                                self._validate_worker_result_ingest_proofs(
                                    worktree_root, validated
                                )
                            except (
                                IdentityError,
                                contract.ContractError,
                            ) as exc:
                                raise TaskNotReadyError(
                                    "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                                ) from exc
                        elif receipt.get("schema") == "x9-loop-lite-result-v1":
                            if (
                                any(
                                    receipt.get(field) != value
                                    for field, value in {
                                        "dispatch_id": expected_rejected[
                                            "dispatch_id"
                                        ],
                                        "event_id": expected_rejected[
                                            "event_id"
                                        ],
                                        "packet_sha256": expected_rejected[
                                            "packet_sha256"
                                        ],
                                        "task_id": expected_rejected[
                                            "task_id"
                                        ],
                                        "worker_id": expected_rejected[
                                            "worker_id"
                                        ],
                                        "role": "WORKER",
                                    }.items()
                                )
                                or not isinstance(
                                    receipt.get("changed_files"), list
                                )
                                or any(
                                    not isinstance(path, str)
                                    for path in receipt["changed_files"]
                                )
                            ):
                                reject()
                        else:
                            reject()
                        seen_rejected.add(relative)
                        continue

                    if receipt.get("schema") != "x9-loop-result-v2":
                        reject()

                    accepted_rows = list(
                        connection.execute(
                            "SELECT e.event_id,e.task_id,e.dispatch_id,"
                            "e.event_sha256,i.event_sha256 AS inbox_sha256,"
                            "i.payload,i.status,t.worker_id,t.worktree_id,"
                            "t.status AS task_status,w.path AS worktree_path,"
                            "wo.work_order_id,wo.packet_sha256 AS work_order_sha256,"
                            "wo.status AS order_status,d.sender_id,d.target_id,"
                            "d.packet_sha256 AS dispatch_packet_sha256,"
                            "d.status AS dispatch_status "
                            "FROM events e JOIN inbox i ON i.event_id=e.event_id "
                            "AND i.task_id=e.task_id AND i.dispatch_id=e.dispatch_id "
                            "JOIN tasks t ON t.task_id=e.task_id "
                            "JOIN worktrees w ON w.worktree_id=t.worktree_id "
                            "JOIN work_orders wo ON wo.task_id=t.task_id "
                            "JOIN dispatches d ON d.dispatch_id=e.dispatch_id "
                            "WHERE e.event_id=? AND e.event_sha256=? "
                            "AND i.status='CONSUMED'",
                            (receipt.get("event_id"), digest),
                        )
                    )
                    if len(accepted_rows) > 1:
                        reject()
                    if accepted_rows:
                        accepted_row = accepted_rows[0]
                        if (
                            accepted_row["task_status"]
                            not in {"COMPLETE", "SUPERSEDED"}
                            or accepted_row["order_status"]
                            != accepted_row["task_status"]
                            or accepted_row["dispatch_status"] != "COMPLETE"
                            or accepted_row["worker_id"] != row["worker_id"]
                            or Path(
                                accepted_row["worktree_path"]
                            ).resolve(strict=True)
                            != worktree_root.resolve(strict=True)
                            or accepted_row["event_id"]
                            in {event["event_id"]}
                        ):
                            reject()
                        expected_accepted = {
                            "dispatch_id": accepted_row["dispatch_id"],
                            "event_id": accepted_row["event_id"],
                            "packet_sha256": accepted_row[
                                "dispatch_packet_sha256"
                            ],
                            "task_id": accepted_row["task_id"],
                            "work_order_id": accepted_row["work_order_id"],
                            "work_order_sha256": accepted_row[
                                "work_order_sha256"
                            ],
                            "worker_id": accepted_row["worker_id"],
                        }
                        try:
                            if receipt.get("schema") == "x9-loop-result-v2":
                                accepted_order, _ = self._verify_work_order(
                                    accepted_row["work_order_id"],
                                    allow_terminal_historical_contract=True,
                                )
                                validated, _ = contract.validate_worker_result(
                                    receipt,
                                    expected_accepted,
                                    require_proof_bound_approaches=(
                                        "autonomy_contract" in accepted_order
                                    ),
                                )
                                if validated != receipt:
                                    reject()
                                self._validated_receipt_proof_paths(
                                    worktree_root,
                                    {relative: digest},
                                )
                            elif receipt.get("schema") == "x9-loop-lite-result-v1":
                                if any(
                                    receipt.get(field) != value
                                    for field, value in {
                                        "dispatch_id": expected_accepted[
                                            "dispatch_id"
                                        ],
                                        "event_id": expected_accepted[
                                            "event_id"
                                        ],
                                        "packet_sha256": expected_accepted[
                                            "packet_sha256"
                                        ],
                                        "task_id": expected_accepted[
                                            "task_id"
                                        ],
                                        "worker_id": expected_accepted[
                                            "worker_id"
                                        ],
                                        "role": "WORKER",
                                    }.items()
                                ):
                                    reject()
                            else:
                                reject()
                            inbox = contract.validate_inbox_event(
                                accepted_row["payload"].encode("utf-8"),
                                accepted_row["inbox_sha256"],
                                self._ensure_project_profile(),
                            )
                            expected_inbox = {
                                "event_id": accepted_row["event_id"],
                                "event_type": "WORKER_RESULT",
                                "payload_ref": {
                                    "path": relative,
                                    "sha256": digest,
                                },
                                "project_profile_id": self._ensure_project_profile(),
                                "schema": "x9-loop-inbox-event-v1",
                                "source_actor_id": row["worker_id"],
                                "source_role": "WORKER",
                            }
                            if inbox != expected_inbox:
                                reject()
                        except (
                            IdentityError,
                            OSError,
                            RuntimeError,
                            ValueError,
                            contract.ContractError,
                        ) as exc:
                            raise TaskNotReadyError(
                                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                            ) from exc
                        if relative in accepted:
                            reject()
                        accepted[relative] = digest
                        continue

                    if connection.execute(
                        "SELECT 1 FROM events WHERE event_id=? UNION ALL "
                        "SELECT 1 FROM inbox WHERE event_id=?",
                        (receipt.get("event_id"), receipt.get("event_id")),
                    ).fetchone() is not None:
                        reject()
                    expected_unfinalized = {
                        **expected_current,
                        "event_id": receipt.get("event_id"),
                    }
                    try:
                        validated, _ = contract.validate_worker_result(
                            receipt,
                            expected_unfinalized,
                            require_proof_bound_approaches=(
                                "autonomy_contract" in current_order
                            ),
                        )
                        self._validate_worker_result_ingest_proofs(
                            worktree_root, validated
                        )
                        validate_scope(validated)
                    except (IdentityError, contract.ContractError) as exc:
                        raise TaskNotReadyError(
                            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                        ) from exc
                    if relative in unfinalized:
                        reject()
                    unfinalized[relative] = digest

                if (
                    not fresh_seen
                    or seen_rejected != set(rejected)
                    or len(unfinalized) > 1
                ):
                    reject()
                count, root_hash = self._receipt_state(
                    connection, worktree_root
                )
                if (
                    count != len(accepted)
                    or root_hash != _sha(sorted(accepted.values()))
                ):
                    reject()
                return {
                    "accepted": accepted,
                    "rejected": {
                        path: records[0]["digest"]
                        for path, records in rejected.items()
                    },
                    "unfinalized": unfinalized,
                    "prior": {**accepted, **unfinalized},
                    "requester_id": row["sender_id"],
                    "result_relative": result_relative,
                    "result_sha256": result_sha256,
                    "task_id": row["task_id"],
                    "dispatch_id": row["dispatch_id"],
                }
            except TaskNotReadyError:
                raise
            except (
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
                KeyError,
                json.JSONDecodeError,
                contract.ContractError,
            ) as exc:
                raise TaskNotReadyError(
                    "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                ) from exc

        with self._mutation_lock:
            doctor = self.doctor()
            checks = doctor.get("checks", {})
            terminal_history_compatibility = checks.get(
                "terminal_history_compatibility"
            )
            receipt_error = (
                f"RECEIPT_SET_MISMATCH:{worktree_row['worktree_id']}"
            )
            if (
                doctor.get("status") != "FAIL"
                or checks.get("receipts") != [receipt_error]
                or checks.get("integrity_check") != "PASS"
                or checks.get("foreign_key_check") != "PASS"
                or checks.get("schema_shape") != "PASS"
                or checks.get("snapshot") != "PASS"
                or checks.get("action") != "PASS"
                or checks.get("errors")
                or checks.get("worktrees")
                or checks.get("historical_missing")
                or checks.get("recovery")
                or checks.get("conflicts", {}).get("claims")
                or checks.get("conflicts", {}).get("resources")
                or checks.get("work_orders")
                or not isinstance(terminal_history_compatibility, list)
                or checks.get("dispatch_identity")
                or checks.get("call_ledger")
                or checks.get("jobs", {}).get("core_loop_ready") is not True
            ):
                raise TaskNotReadyError("RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE")
            connection = self._connect()
            try:
                admitted = admission(
                    connection, terminal_history_compatibility
                )
            finally:
                connection.close()

            def revalidate(connection: sqlite3.Connection) -> None:
                current = admission(
                    connection, terminal_history_compatibility
                )
                for key in (
                    "accepted",
                    "rejected",
                    "unfinalized",
                    "prior",
                    "requester_id",
                    "result_relative",
                    "result_sha256",
                    "task_id",
                    "dispatch_id",
                ):
                    if current[key] != admitted[key]:
                        raise TaskNotReadyError(
                            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE"
                        )

            consumed = self.ingest_worker_result(
                event_path,
                _receipt_entries_override=admitted["prior"],
                _preconsumption_result_ready_requester_id=(
                    admitted["requester_id"]
                ),
                _recovery_admission=revalidate,
            )
        return {
            **consumed,
            "recovery": {
                "accepted_receipts": len(admitted["accepted"]),
                "rejected_receipts": len(admitted["rejected"]),
                "unfinalized_receipts": len(admitted["unfinalized"]),
                "work_order_id": work_order_id,
            },
        }

    def run_once(self, event_file: str | Path) -> dict[str, Any]:
        contract = _load_v7_contract()
        candidate = Path(event_file)
        if not candidate.is_absolute():
            candidate = self.repo / candidate
        try:
            event_path = self._safe_state_path(candidate)
            if (
                not event_path.is_file()
                or self._is_reparse(event_path)
            ):
                raise IdentityError("INBOX_EVENT_PATH_INVALID")
            event_raw = self._read_capped_packet(
                event_path, "INBOX_EVENT.json"
            )
        except IdentityError:
            raise
        except (LoopError, OSError, contract.ContractError) as exc:
            raise IdentityError("INBOX_EVENT_PATH_INVALID") from exc
        event_sha256 = hashlib.sha256(event_raw).hexdigest()
        profile_id = self._ensure_project_profile()
        try:
            event = contract.validate_inbox_event(
                event_raw, event_sha256, profile_id
            )
        except contract.ContractError as exc:
            raise IdentityError(str(exc)) from exc
        payload_ref = event["payload_ref"]
        try:
            relative = contract.canonical_repo_path(payload_ref["path"])
            payload_path = self._safe_state_path(
                self.repo / Path(*PurePosixPath(relative).parts)
            )
            if (
                not payload_path.is_file()
                or self._is_reparse(payload_path)
            ):
                raise IdentityError("INBOX_PAYLOAD_PATH_INVALID")
            packet_name = {
                "TRANSPORT_ACK": "TRANSPORT_ACK.json",
                "WORKER_RESULT": "RESULT.json",
                "THINX_RESULT": "THINX_DECISION.json",
            }[event["event_type"]]
            payload_raw = self._read_capped_packet(
                payload_path, packet_name
            )
        except IdentityError:
            raise
        except (
            KeyError, LoopError, OSError, contract.ContractError
        ) as exc:
            raise IdentityError("INBOX_PAYLOAD_PATH_INVALID") from exc
        if hashlib.sha256(payload_raw).hexdigest() != payload_ref["sha256"]:
            raise IdentityError("INBOX_PAYLOAD_HASH_MISMATCH")
        if event["event_type"] == "WORKER_RESULT":
            event_text = event_raw.decode("utf-8")
            existing_connection = self._connect()
            try:
                self._schema(existing_connection)
                existing = existing_connection.execute(
                    "SELECT event_sha256,payload,status FROM inbox "
                    "WHERE event_id=?",
                    (event["event_id"],),
                ).fetchone()
            finally:
                existing_connection.close()
            if existing:
                if (
                    existing["event_sha256"] != event_sha256
                    or existing["payload"] != event_text
                ):
                    raise IdentityError("INBOX_EVENT_CONFLICT")
                if existing["status"] == "CONSUMED":
                    replay_status = "ALREADY_CONSUMED"
                elif existing["status"].startswith("REJECTED:"):
                    replay_status = "ALREADY_REJECTED"
                else:
                    raise IdentityError("INBOX_EVENT_CONFLICT")
                self._publish_current_action()
                return {
                    "event_id": event["event_id"],
                    "status": replay_status,
                }
            try:
                result = json.loads(payload_raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise IdentityError("WORKER_RESULT_JSON_INVALID") from exc
            if (
                not isinstance(result, dict)
                or result.get("event_id") != event["event_id"]
                or result.get("worker_id") != event["source_actor_id"]
                or result.get("role") != event["source_role"]
            ):
                raise IdentityError("WORKER_RESULT_IDENTITY_INVALID")
            worker_event = {
                "actor_id": event["source_actor_id"],
                "dispatch_id": result.get("dispatch_id"),
                "event_id": event["event_id"],
                "event_type": "WORKER_RESULT",
                "packet_sha256": result.get("packet_sha256"),
                "result_path": relative,
                "result_sha256": payload_ref["sha256"],
                "role": event["source_role"],
                "task_id": result.get("task_id"),
            }
            inbox_record = {
                    "dispatch_id": result.get("dispatch_id"),
                    "event_id": event["event_id"],
                    "event_sha256": event_sha256,
                    "payload": event_text,
                    "status": "CONSUMED",
                }
            try:
                return self.consume_event(
                    worker_event, _inbox_event=inbox_record
                )
            except StaleCompletionError as exc:
                reason = str(exc)
                if reason not in {
                    "RESULT_FIELDS_INVALID", "RESULT_SCHEMA_INVALID"
                }:
                    raise
                return self._register_result_schema_rejection(
                    event, event_sha256, event_text, result, reason
                )
        if event["event_type"] == "THINX_RESULT":
            event_text = event_raw.decode("utf-8")
            existing_connection = self._connect()
            try:
                self._schema(existing_connection)
                existing = existing_connection.execute(
                    "SELECT event_sha256,payload,status FROM inbox "
                    "WHERE event_id=?",
                    (event["event_id"],),
                ).fetchone()
            finally:
                existing_connection.close()
            if existing:
                if (
                    existing["event_sha256"] != event_sha256
                    or existing["payload"] != event_text
                    or existing["status"] != "CONSUMED"
                ):
                    raise IdentityError("INBOX_EVENT_CONFLICT")
                self._publish_current_action()
                return {
                    "event_id": event["event_id"],
                    "status": "ALREADY_CONSUMED",
                }
            try:
                decision = json.loads(payload_raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise IdentityError("THINX_RESULT_JSON_INVALID") from exc
            if (
                not isinstance(decision, dict)
                or decision.get("event_id") != event["event_id"]
                or decision.get("actor_id") != event["source_actor_id"]
                or decision.get("role") != "THINX"
            ):
                raise IdentityError("THINX_RESULT_IDENTITY_INVALID")
            thinx_event = {
                "actor_id": event["source_actor_id"],
                "dispatch_id": decision.get("dispatch_id"),
                "event_id": event["event_id"],
                "event_type": "THINX_DECISION",
                "packet_sha256": decision.get("packet_sha256"),
                "result_path": relative,
                "result_sha256": payload_ref["sha256"],
                "role": "THINX",
                "task_id": decision.get("task_id"),
            }
            inbox_record = {
                "dispatch_id": decision.get("dispatch_id"),
                "event_id": event["event_id"],
                "event_sha256": event_sha256,
                "payload": event_text,
                "status": "CONSUMED",
            }
            return self.consume_event(
                thinx_event, _inbox_event=inbox_record
            )
        if event["event_type"] != "TRANSPORT_ACK":
            raise IdentityError("INBOX_EVENT_TYPE_UNSUPPORTED")
        try:
            ack_preview = json.loads(payload_raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IdentityError("TRANSPORT_ACK_JSON_INVALID") from exc
        if not isinstance(ack_preview, dict):
            raise IdentityError("TRANSPORT_ACK_JSON_INVALID")
        dispatch_id = ack_preview.get("dispatch_id")
        if not isinstance(dispatch_id, str):
            raise IdentityError("TRANSPORT_ACK_IDENTITY_INVALID")
        event_text = event_raw.decode("utf-8")

        existing_connection = self._connect()
        try:
            self._schema(existing_connection)
            existing = existing_connection.execute(
                "SELECT event_sha256,payload,status FROM inbox "
                "WHERE event_id=?",
                (event["event_id"],),
            ).fetchone()
        finally:
            existing_connection.close()
        if existing:
            if (
                existing["event_sha256"] != event_sha256
                or existing["payload"] != event_text
                or existing["status"] != "CONSUMED"
            ):
                raise IdentityError("INBOX_EVENT_CONFLICT")
            self._publish_current_action()
            return {
                "event_id": event["event_id"],
                "status": "ALREADY_CONSUMED",
            }
        if ack_preview.get("action") == "RESULT_SCHEMA_REPAIR":
            return self._consume_result_schema_repair_ack(
                event,
                event_sha256,
                event_text,
                payload_raw,
                payload_ref["sha256"],
                profile_id,
            )

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            duplicate = connection.execute(
                "SELECT event_sha256,payload,status FROM inbox "
                "WHERE event_id=?",
                (event["event_id"],),
            ).fetchone()
            if duplicate:
                if (
                    duplicate["event_sha256"] == event_sha256
                    and duplicate["payload"] == event_text
                    and duplicate["status"] == "CONSUMED"
                ):
                    raise _InboxAlreadyConsumed()
                raise IdentityError("INBOX_EVENT_CONFLICT")
            actor = connection.execute(
                "SELECT role FROM actors WHERE actor_id=?",
                (event["source_actor_id"],),
            ).fetchone()
            if (
                not actor
                or actor["role"] not in {"LINX", "LINKER"}
            ):
                raise IdentityError("INBOX_EVENT_ACTOR_INVALID")
            row = connection.execute(
                "SELECT d.task_id,d.sender_id,d.target_id,d.status,"
                "o.payload,w.work_order_id,w.packet_sha256,w.worker_id "
                "FROM dispatches d "
                "JOIN work_orders w ON w.task_id=d.task_id "
                "LEFT JOIN outbox o ON o.dispatch_id=d.dispatch_id "
                "WHERE d.dispatch_id=?",
                (dispatch_id,),
            ).fetchone()
            if not row or row["status"] != "PREPARED" or not row["payload"]:
                raise DeliveryError("DISPATCH_INACTIVE")
            if row["sender_id"] != event["source_actor_id"]:
                raise IdentityError("INBOX_EVENT_ACTOR_MISMATCH")
            try:
                action = json.loads(row["payload"])
                action_raw = contract.canonical_json_bytes(action)
            except (
                TypeError,
                ValueError,
                json.JSONDecodeError,
                contract.ContractError,
            ) as exc:
                raise IdentityError("ACTION_IDENTITY_INVALID") from exc
            action_sha256 = hashlib.sha256(action_raw).hexdigest()
            expected = {
                "action_id": action.get("action_id"),
                "action_sha256": action_sha256,
                "dispatch_id": dispatch_id,
                "project_profile_id": profile_id,
                "work_order_id": row["work_order_id"],
                "work_order_sha256": row["packet_sha256"],
                "worker_id": row["worker_id"],
            }
            if (
                action.get("schema") != "x9-loop-action-v2"
                or action.get("work_order_id") != row["work_order_id"]
                or action.get("project_profile_id") != profile_id
                or action.get("target_actor_id") != row["worker_id"]
                or action.get("work_order_sha256")
                != row["packet_sha256"]
            ):
                raise IdentityError("ACTION_IDENTITY_INVALID")
            try:
                ack = contract.validate_transport_ack(
                    payload_raw, payload_ref["sha256"], expected
                )
            except contract.ContractError as exc:
                raise IdentityError(str(exc)) from exc
            if ack["ack_id"] != "ack-" + action_sha256[:32]:
                raise IdentityError("TRANSPORT_ACK_IDENTITY_MISMATCH:ack_id")
            connection.execute(
                "UPDATE dispatches SET status='DISPATCHED' "
                "WHERE dispatch_id=?",
                (dispatch_id,),
            )
            connection.execute(
                "INSERT INTO deliveries"
                "(dispatch_id,phase,method,result,created_at) "
                "VALUES(?,?,?,?,?)",
                (
                    dispatch_id,
                    "DISPATCH",
                    "LINKER",
                    "ACKNOWLEDGED",
                    self.now_fn(),
                ),
            )
            connection.execute(
                "INSERT INTO inbox"
                "(event_id,task_id,dispatch_id,event_sha256,payload,status,created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    event["event_id"],
                    row["task_id"],
                    dispatch_id,
                    event_sha256,
                    event_text,
                    "CONSUMED",
                    self.now_fn(),
                ),
            )
            return {
                "event_id": event["event_id"],
                "status": "CONSUMED",
            }

        try:
            result = self._mutate(operation)
        except _InboxAlreadyConsumed:
            result = {
                "event_id": event["event_id"],
                "status": "ALREADY_CONSUMED",
            }
        self._publish_current_action()
        return result


    def record_delivery(self, dispatch_id: str, phase: str, method: str, result: str) -> dict[str, Any]:
        phase = phase.upper()
        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            dispatch = connection.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
            if not dispatch:
                raise DeliveryError("DISPATCH_UNKNOWN")
            task_status = connection.execute("SELECT status FROM tasks WHERE task_id=?", (dispatch["task_id"],)).fetchone()
            if phase == "REVIEW":
                if (dispatch["status"] != "COMPLETE" or not task_status
                        or task_status["status"] != "THINX_REVIEW_REQUIRED"
                        or result.casefold() not in {"ack", "acknowledged"}):
                    raise DeliveryError("REVIEW_DELIVERY_INVALID")
            else:
                if dispatch["status"] not in {"PREPARED", "DISPATCHED"}:
                    raise DeliveryError("DISPATCH_INACTIVE")
                if phase == "DISPATCH" and dispatch["status"] != "PREPARED":
                    raise DeliveryError("DISPATCH_ALREADY_DELIVERED")
            callbacks = connection.execute("SELECT COUNT(*) FROM deliveries WHERE dispatch_id=? AND phase='CALLBACK'", (dispatch_id,)).fetchone()[0]
            if phase == "CALLBACK" and callbacks >= 2:
                raise DeliveryError("CALLBACK_RETRY_LIMIT")
            connection.execute("INSERT INTO deliveries(dispatch_id,phase,method,result,created_at) VALUES(?,?,?,?,?)", (dispatch_id, phase, method, result, self.now_fn()))
            attempts = connection.execute("SELECT COUNT(*) FROM deliveries WHERE dispatch_id=? AND phase='DISPATCH'", (dispatch_id,)).fetchone()[0]
            action = None
            if phase == "DISPATCH":
                if result.casefold() in {"ack", "acknowledged"}:
                    connection.execute("UPDATE dispatches SET status='DISPATCHED' WHERE dispatch_id=?", (dispatch_id,))
                    action = self._status_action("WAIT", "delivery-acknowledged")
                else:
                    row = connection.execute("SELECT payload FROM outbox WHERE dispatch_id=?", (dispatch_id,)).fetchone()
                    action = json.loads(row[0]) if row else self._action(dispatch_id, json.loads(dispatch["packet"]), dispatch["packet_sha256"])
                    action["attempt"] = attempts + 1
                    connection.execute("INSERT INTO outbox(dispatch_id,payload) VALUES(?,?) ON CONFLICT(dispatch_id) DO UPDATE SET payload=excluded.payload", (dispatch_id, _json(action)))
            if phase == "CALLBACK" and result.casefold() == "failed":
                response = ({"status": "CALLBACK_FAILED", "next": "MANUAL_ONE_SHOT_PICKUP", "attempts": attempts} if callbacks + 1 == 2 else {"status": "CALLBACK_RETRY", "next": "RETRY_SAME_EVENT_ONCE", "attempts": attempts})
            else:
                acknowledged = result.casefold() in {"ack", "acknowledged"}
                response = {"status": "DELIVERED" if acknowledged else "DELIVERY_UNCONFIRMED", "attempts": attempts, "sent_once": acknowledged and attempts == 1}
            response["_action"] = action
            return response
        response = self._mutate(operation)
        response.pop("_action")
        self._publish_current_action()
        return response

    def _run_git(self, arguments: list[str], worktree_path: str | Path | None = None) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(["git", "-C", str(worktree_path or self.repo), *arguments], capture_output=True, text=True, check=False, timeout=GIT_TIMEOUT_SECONDS)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitStateError("GIT_STATE_UNKNOWN") from exc

    def _run_git_bytes(self, arguments: list[str], worktree_path: str | Path | None = None) -> subprocess.CompletedProcess[bytes]:
        try:
            return subprocess.run(
                ["git", "-C", str(worktree_path or self.repo), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitStateError("GIT_STATE_UNKNOWN") from exc

    def _git_paths(self, arguments: list[str], worktree_path: str | Path | None = None) -> list[str]:
        completed = self._run_git(arguments, worktree_path)
        if completed.returncode:
            raise GitStateError("GIT_STATE_UNKNOWN")
        return sorted({self._normal_path(path) for path in completed.stdout.splitlines() if path})

    def _git_history_paths(
        self, base_sha: str, end_sha: str, worktree_path: str | Path | None = None
    ) -> list[str]:
        return self._git_paths(
            ["log", "--format=", "--name-only", "--no-renames", f"{base_sha}..{end_sha}"],
            worktree_path,
        )

    def _git_state(self, base_sha: str, worktree_path: str | Path | None = None) -> dict[str, list[str]]:
        return {"staged": self._git_paths(["diff", "--cached", "--name-only"], worktree_path), "unstaged": self._git_paths(["diff", "--name-only"], worktree_path), "untracked": self._git_paths(["ls-files", "--others", "--exclude-standard"], worktree_path), "committed": self._git_history_paths(base_sha, "HEAD", worktree_path)}

    @staticmethod
    def _is_controller_runtime_path(path: str) -> bool:
        path = path.casefold()
        runtime = ".devad/manager/loop-lite/runtime/"
        database = ".devad/manager/loop-lite/loop.db"
        state_root = ".devad/manager/loop-lite/"
        return (
            path.startswith(runtime)
            or path.startswith(state_root + "programs/")
            or path.startswith(state_root + "recovery/")
            or path.startswith(state_root + "snapshots/")
            or path in {
                state_root + "action.json",
                state_root + "approved_jobs.json",
                state_root + "migration_state.json",
                state_root + "project_profile.json",
                state_root + "snapshot.json",
            }
            or path == database
            or path in {database + "-wal", database + "-shm"}
            or path.startswith(database + ".corrupt-")
            or path.startswith(database + ".rebuild-")
            or path.startswith(database + ".failed-")
            or path.startswith(database + "-wal.corrupt-")
            or path.startswith(database + "-wal.failed-")
            or path.startswith(database + "-shm.corrupt-")
            or path.startswith(database + "-shm.failed-")
            or path.startswith(state_root + "snapshot.json.corrupt-")
            or path.startswith(state_root + "snapshot.json.failed-")
        )

    def _scope_paths(self, paths: list[str], receipt_path: str | None = None) -> list[str]:
        receipt = self._normal_path(receipt_path) if receipt_path else None
        return [path for path in paths if not self._is_controller_runtime_path(path) and path != receipt]

    def reconcile(self, task_id: str | None = None) -> dict[str, Any]:
        task = None
        order: dict[str, Any] | None = None
        work_order_id: str | None = None
        claims: list[tuple[str, str]] = []
        tampered: set[str] = set()
        if task_id:
            connection = self._connect()
            try:
                task = connection.execute("SELECT t.*,w.path AS worktree_path FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id WHERE t.task_id=?", (task_id,)).fetchone()
                order_row = connection.execute(
                    "SELECT work_order_id FROM work_orders WHERE task_id=?",
                    (task_id,),
                ).fetchone()
                work_order_id = order_row["work_order_id"] if order_row else None
                claims = [(row["path"], row["kind"]) for row in connection.execute("SELECT path,kind FROM claims WHERE task_id=?", (task_id,))]
            finally:
                connection.close()
            if not task:
                raise TaskNotReadyError("TASK_UNKNOWN")
            tampered = self._controller_snapshot_tamper(Path(task["worktree_path"]))
        self._write_snapshot()
        self._safe_state_path(self.snapshot_path)
        snapshot_state = self._decode_snapshot(self.snapshot_path.read_bytes())
        result: dict[str, Any] = {
            "snapshot": "PASS",
            "recovery": self._recovery_evidence(
                snapshot_state["recovery_worktrees"], strict=False
            ),
        }
        if task:
            if work_order_id:
                order = self.verify_work_order(work_order_id)
                owner_evidence = {
                    self._normal_path(task["owner_packet_path"]),
                    self._normal_path(
                        order["program_packet_path"]
                    ),
                    *{
                        self._normal_path(feature["path"])
                        for feature in order["feature_packet_refs"]
                    },
                }
            else:
                owner_evidence = self._verify_owner_packet(task)
            controller_evidence = self._controller_snapshot_evidence(Path(task["worktree_path"])) - tampered
            git = self._git_state(task["base_sha"], task["worktree_path"])
            historical_evidence = self._historical_receipt_paths(
                Path(task["worktree_path"])
            )
            scoped_git = {key: [path for path in self._scope_paths(value) if path not in owner_evidence and path not in controller_evidence and path not in historical_evidence] for key, value in git.items()}
            changed = sorted(set(path for paths in scoped_git.values() for path in paths))
            scope_breach = sorted({path for path in changed if not any(self._overlap(path, "file", claim, kind) for claim, kind in claims)} | tampered)
            result.update({"git": scoped_git, "scope_breach": scope_breach, "controller_tamper": sorted(tampered)})
            violations: list[str] = []
            if task["status"] not in {"COMPLETE", "SUPERSEDED"}:
                if order is not None:
                    try:
                        created_at = datetime.fromisoformat(
                            order["created_at"].replace("Z", "+00:00")
                        )
                        observed_at = datetime.fromisoformat(
                            self.now_fn().replace("Z", "+00:00")
                        )
                        elapsed = max(
                            0, int((observed_at - created_at).total_seconds())
                        )
                    except (KeyError, TypeError, ValueError, OverflowError) as exc:
                        raise StateNotDurableError("WORK_ORDER_TIME_INVALID") from exc
                    result["authoritative_elapsed_seconds"] = elapsed
                    if elapsed >= order["stop_contract"]["max_wall_seconds"]:
                        violations.append("MAX_WALL_SECONDS")
                if scope_breach:
                    violations.append("SCOPE_BREACH")
                if violations:
                    result["event"] = "OWNER_DECISION_REQUIRED"
                    result["status"] = "CONTROLLER_VIOLATION_DETECTED"
                    result["violations"] = violations
        if (
            task
            and work_order_id
            and violations
            and task["status"] not in {"COMPLETE", "SUPERSEDED"}
        ):
            violation_code = "+".join(violations)
            violation_note = "CONTROLLER_VIOLATION_DETECTED:" + violation_code
            connection = self._connect()
            try:
                state = connection.execute(
                    "SELECT t.status AS task_status,wo.status AS order_status "
                    "FROM tasks t JOIN work_orders wo ON wo.task_id=t.task_id "
                    "WHERE t.task_id=? AND wo.work_order_id=?",
                    (task_id, work_order_id),
                ).fetchone()
                gate = connection.execute(
                    "SELECT status,note FROM gates WHERE task_id=? "
                    "AND name='controller:violation'",
                    (task_id,),
                ).fetchone()
                active_dispatches = connection.execute(
                    "SELECT COUNT(*) FROM dispatches WHERE task_id=? "
                    "AND status IN ('PREPARED','DISPATCHED')",
                    (task_id,),
                ).fetchone()[0]
            finally:
                connection.close()
            already_quarantined = bool(
                state
                and state["task_status"] == "OWNER_DECISION_REQUIRED"
                and state["order_status"] == "OWNER_DECISION_REQUIRED"
                and gate
                and tuple(gate) == ("BLOCKED", violation_note)
                and active_dispatches == 0
            )
            if not already_quarantined:
                self._write_action(
                    self._status_action(
                        "NOOP", "controller-violation-quarantine-pending"
                    )
                )

                def quarantine(connection: sqlite3.Connection) -> None:
                    current = connection.execute(
                        "SELECT t.status AS task_status,wo.status AS order_status "
                        "FROM tasks t JOIN work_orders wo ON wo.task_id=t.task_id "
                        "WHERE t.task_id=? AND wo.work_order_id=?",
                        (task_id, work_order_id),
                    ).fetchone()
                    if not current:
                        raise TaskNotReadyError("TASK_UNKNOWN")
                    if (
                        current["task_status"] in {"COMPLETE", "SUPERSEDED"}
                        or current["order_status"] in {"COMPLETE", "SUPERSEDED"}
                    ):
                        raise TaskNotReadyError("CONTROLLER_VIOLATION_TASK_TERMINAL")
                    connection.execute(
                        "UPDATE dispatches SET status='SUPERSEDED' "
                        "WHERE task_id=? AND status IN ('PREPARED','DISPATCHED')",
                        (task_id,),
                    )
                    connection.execute(
                        "UPDATE tasks SET status='OWNER_DECISION_REQUIRED' "
                        "WHERE task_id=?",
                        (task_id,),
                    )
                    connection.execute(
                        "UPDATE work_orders SET status='OWNER_DECISION_REQUIRED' "
                        "WHERE work_order_id=?",
                        (work_order_id,),
                    )
                    connection.execute(
                        "INSERT INTO gates(task_id,name,status,note) "
                        "VALUES(?, 'controller:violation', 'BLOCKED', ?) "
                        "ON CONFLICT(task_id,name) DO UPDATE SET "
                        "status=excluded.status,note=excluded.note",
                        (task_id, violation_note),
                    )

                self._mutate(quarantine)
            self._write_action(
                self._status_action(
                    "NOOP", "owner-decision-required:" + violation_code
                )
            )
        else:
            self._write_action(self._current_action())
        self._write_views()
        return result
    def _claimed(self, connection: sqlite3.Connection, task_id: str, path: str) -> bool:
        return any(self._overlap(path, "file", row["path"], row["kind"]) for row in connection.execute("SELECT path,kind FROM claims WHERE task_id=?", (task_id,)))

    def _validated_receipt_paths(
        self, worktree_root: Path, connection: sqlite3.Connection | None = None,
        exclude_paths: set[str] | None = None,
    ) -> set[str]:
        return set(self._validated_receipt_entries(worktree_root, connection, exclude_paths))

    def _actual_git_paths(
        self, task_id: str, receipt_path: str, validated_receipts: set[str] | None = None
    ) -> list[str]:
        connection = self._connect()
        try:
            task = connection.execute("SELECT t.base_sha,w.path AS worktree_path FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id WHERE t.task_id=?", (task_id,)).fetchone()
        finally:
            connection.close()
        if not task:
            raise StaleCompletionError("STALE_COMPLETION")
        worktree_root = Path(task["worktree_path"])
        receipt = self._normal_path(receipt_path)
        if validated_receipts is None:
            validated_receipts = self._validated_receipt_paths(
                worktree_root, exclude_paths={receipt}
            )
        excluded = (
            set(validated_receipts)
            | self._historical_receipt_paths(worktree_root)
            | {receipt}
        )
        state = self._git_state(task["base_sha"], task["worktree_path"])
        return sorted({path for paths in state.values() for path in self._scope_paths(paths) if path not in excluded})

    def _duplicate_event(self, event_id: str) -> bool:
        connection = self._connect()
        try:
            return bool(connection.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone())
        finally:
            connection.close()

    def _consume_v7_thinx_event(
        self,
        event: dict[str, Any],
        dispatch: sqlite3.Row,
        task: sqlite3.Row,
        actor: sqlite3.Row | None,
        stored_packet: dict[str, Any],
        latest: sqlite3.Row | None,
        inbox_event: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        if (
            event["event_type"] != "THINX_DECISION"
            or event["role"] != "THINX"
            or actor is None
            or actor["role"] not in {"THINX", "THINKER"}
            or dispatch["status"] != "COMPLETE"
            or task["status"] != "THINX_REVIEW_REQUIRED"
            or latest is None
            or latest["dispatch_id"] != dispatch["dispatch_id"]
            or event["packet_sha256"] != dispatch["packet_sha256"]
            or stored_packet.get("schema")
            != "x9-loop-work-order-dispatch-v1"
            or stored_packet.get("task_id") != task["task_id"]
        ):
            raise StaleCompletionError("STALE_COMPLETION")
        connection = self._connect()
        try:
            order_row = connection.execute(
                "SELECT * FROM work_orders WHERE task_id=?",
                (task["task_id"],),
            ).fetchone()
            worker_event = connection.execute(
                "SELECT event_id,event_sha256 FROM events "
                "WHERE dispatch_id=? ORDER BY rowid DESC LIMIT 1",
                (dispatch["dispatch_id"],),
            ).fetchone()
            review_ack = connection.execute(
                "SELECT 1 FROM deliveries WHERE dispatch_id=? "
                "AND phase='REVIEW' "
                "AND lower(result) IN ('ack','acknowledged') "
                "ORDER BY id DESC LIMIT 1",
                (dispatch["dispatch_id"],),
            ).fetchone()
        finally:
            connection.close()
        if (
            order_row is None
            or order_row["status"] != "THINX_REVIEW_REQUIRED"
            or order_row["packet_path"]
            != stored_packet.get("work_order_path")
            or order_row["packet_sha256"]
            != stored_packet.get("work_order_sha256")
            or worker_event is None
            or review_ack is None
        ):
            raise StaleCompletionError("STALE_COMPLETION")
        receipt_relative = self._normal_path(event["result_path"])
        expected_receipt = self._normal_path(
            f".devad/workers/{event['actor_id']}/receipts/"
            f"{event['event_id']}.json"
        )
        root = Path(task["worktree_path"])
        try:
            result_path = self._resolve_under(
                root,
                root / Path(*PurePosixPath(receipt_relative).parts),
            )
            raw = result_path.read_bytes()
            document = json.loads(raw)
        except (
            OSError,
            UnicodeDecodeError,
            ValueError,
            RuntimeError,
            json.JSONDecodeError,
        ) as exc:
            raise StaleCompletionError(
                "THINX_DECISION_INVALID"
            ) from exc
        expected = {
            "actor_id": event["actor_id"],
            "dispatch_id": dispatch["dispatch_id"],
            "event_id": event["event_id"],
            "packet_sha256": dispatch["packet_sha256"],
            "task_id": task["task_id"],
            "worker_event_id": worker_event["event_id"],
            "worker_result_sha256": worker_event["event_sha256"],
            "work_order_id": order_row["work_order_id"],
            "work_order_sha256": order_row["packet_sha256"],
        }
        try:
            decision = contract.validate_thinx_decision(
                document, expected
            )
        except contract.ContractError as exc:
            raise StaleCompletionError(exc.code) from exc
        if (
            receipt_relative != expected_receipt
            or hashlib.sha256(raw).hexdigest()
            != event["result_sha256"]
            or contract.canonical_json_bytes(decision) != raw
        ):
            raise StaleCompletionError("THINX_DECISION_INVALID")
        prior_receipts = self._validated_receipt_entries(
            root, exclude_paths={receipt_relative}
        )
        allowed_system = {
            receipt_relative,
            *self._registered_rejected_receipt_paths(root),
            *prior_receipts,
            *self._historical_receipt_paths(root),
        }
        for prior_path, prior_sha256 in prior_receipts.items():
            try:
                prior_absolute = self._resolve_under(
                    root,
                    root / Path(*PurePosixPath(prior_path).parts),
                )
                prior_raw = prior_absolute.read_bytes()
                prior = json.loads(prior_raw)
            except (
                OSError,
                UnicodeDecodeError,
                ValueError,
                RuntimeError,
                json.JSONDecodeError,
            ) as exc:
                raise StaleCompletionError(
                    "RECEIPT_SET_MISMATCH"
                ) from exc
            if hashlib.sha256(prior_raw).hexdigest() != prior_sha256:
                raise StaleCompletionError("RECEIPT_SET_MISMATCH")
            if prior.get("schema") != "x9-loop-result-v2":
                continue
            if contract.canonical_json_bytes(prior) != prior_raw:
                raise StaleCompletionError("RECEIPT_SET_MISMATCH")
            for approach in prior.get("approach_receipts", []):
                try:
                    approach_relative = self._normal_path(
                        approach["evidence_path"]
                    )
                    expected_approach_path = self._normal_path(
                        f".devad/workers/{prior['worker_id']}/proof/"
                        f"{prior['event_id']}/approaches/"
                        f"{approach['approach_id']}.json"
                    )
                    approach_path = self._resolve_under(
                        root,
                        root / Path(*PurePosixPath(approach_relative).parts),
                    )
                    approach_raw = approach_path.read_bytes()
                    approach_proof = json.loads(approach_raw)
                except (
                    KeyError,
                    OSError,
                    UnicodeDecodeError,
                    ValueError,
                    RuntimeError,
                    json.JSONDecodeError,
                ) as exc:
                    raise StaleCompletionError(
                        "APPROACH_EVIDENCE_INVALID"
                    ) from exc
                expected_approach_proof = {
                    "action_class": approach["action_class"],
                    "approach_id": approach["approach_id"],
                    "event_id": prior["event_id"],
                    "failure_code": approach["failure_code"],
                    "hypothesis": approach["hypothesis"],
                    "next_route": approach["next_route"],
                    "progress": approach["progress"],
                    "route": approach["route"],
                    "schema": "x9-loop-approach-proof-v1",
                    "source_hashes": approach["source_hashes"],
                    "task_id": prior["task_id"],
                    "work_order_id": prior["work_order_id"],
                    "worker_id": prior["worker_id"],
                }
                if (
                    approach_relative != expected_approach_path
                    or hashlib.sha256(approach_raw).hexdigest()
                    != approach["evidence_sha256"]
                    or approach_proof != expected_approach_proof
                    or contract.canonical_json_bytes(approach_proof)
                    != approach_raw
                ):
                    raise StaleCompletionError("APPROACH_EVIDENCE_INVALID")
                for source_relative, source_sha256 in (
                    approach["source_hashes"].items()
                ):
                    try:
                        source = self._resolve_under(
                            root,
                            root / Path(*PurePosixPath(source_relative).parts),
                        )
                        source_raw = source.read_bytes()
                    except (OSError, RuntimeError) as exc:
                        raise StaleCompletionError(
                            "APPROACH_EVIDENCE_INVALID"
                        ) from exc
                    if hashlib.sha256(source_raw).hexdigest() != source_sha256:
                        raise StaleCompletionError("APPROACH_EVIDENCE_INVALID")
                allowed_system.add(approach_relative)
            for item in prior.get("proof", []):
                proof_relative = self._normal_path(item["path"])
                try:
                    proof_path = self._resolve_under(
                        root,
                        root
                        / Path(*PurePosixPath(proof_relative).parts),
                    )
                    proof_raw = proof_path.read_bytes()
                    proof = json.loads(proof_raw)
                except (
                    OSError,
                    UnicodeDecodeError,
                    ValueError,
                    RuntimeError,
                    json.JSONDecodeError,
                ) as exc:
                    raise StaleCompletionError(
                        "RESULT_PROOF_INVALID"
                    ) from exc
                if (
                    hashlib.sha256(proof_raw).hexdigest()
                    != item["sha256"]
                    or contract.canonical_json_bytes(proof)
                    != proof_raw
                    or proof.get("event_id") != prior["event_id"]
                    or proof.get("work_order_id")
                    != prior["work_order_id"]
                ):
                    raise StaleCompletionError(
                        "RESULT_PROOF_INVALID"
                    )
                allowed_system.add(proof_relative)
        head = self._run_git(
            ["rev-parse", "HEAD"], task["worktree_path"]
        )
        state = self._git_state(
            task["base_sha"], task["worktree_path"]
        )
        dirty = {
            path
            for kind in ("staged", "unstaged", "untracked")
            for path in self._scope_paths(state[kind])
            if path not in allowed_system
        }
        if (
            head.returncode
            or head.stdout.strip() != task["base_sha"]
            or dirty
        ):
            raise StaleCompletionError("THINX_DECISION_GIT_INVALID")

        def operation(
            connection: sqlite3.Connection,
        ) -> dict[str, Any]:
            current = connection.execute(
                "SELECT t.status AS task_status,"
                "wo.status AS order_status,d.status AS dispatch_status "
                "FROM tasks t JOIN work_orders wo "
                "ON wo.task_id=t.task_id "
                "JOIN dispatches d ON d.task_id=t.task_id "
                "WHERE t.task_id=? AND d.dispatch_id=?",
                (task["task_id"], dispatch["dispatch_id"]),
            ).fetchone()
            current_latest = connection.execute(
                "SELECT dispatch_id FROM dispatches WHERE task_id=? "
                "ORDER BY rowid DESC LIMIT 1",
                (task["task_id"],),
            ).fetchone()
            current_worker = connection.execute(
                "SELECT event_id,event_sha256 FROM events "
                "WHERE dispatch_id=? ORDER BY rowid DESC LIMIT 1",
                (dispatch["dispatch_id"],),
            ).fetchone()
            current_review = connection.execute(
                "SELECT 1 FROM deliveries WHERE dispatch_id=? "
                "AND phase='REVIEW' "
                "AND lower(result) IN ('ack','acknowledged') "
                "ORDER BY id DESC LIMIT 1",
                (dispatch["dispatch_id"],),
            ).fetchone()
            if (
                current is None
                or current["task_status"]
                != "THINX_REVIEW_REQUIRED"
                or current["order_status"]
                != "THINX_REVIEW_REQUIRED"
                or current["dispatch_status"] != "COMPLETE"
                or current_latest is None
                or current_latest["dispatch_id"]
                != dispatch["dispatch_id"]
                or current_worker is None
                or current_worker["event_id"]
                != worker_event["event_id"]
                or current_worker["event_sha256"]
                != worker_event["event_sha256"]
                or current_review is None
            ):
                raise StaleCompletionError("STALE_COMPLETION")
            connection.execute(
                "INSERT INTO events("
                "event_id,task_id,dispatch_id,event_sha256,created_at"
                ") VALUES(?,?,?,?,?)",
                (
                    event["event_id"],
                    task["task_id"],
                    dispatch["dispatch_id"],
                    event["result_sha256"],
                    self.now_fn(),
                ),
            )
            if inbox_event is not None:
                if (
                    inbox_event.get("event_id") != event["event_id"]
                    or inbox_event.get("dispatch_id")
                    != dispatch["dispatch_id"]
                    or inbox_event.get("status") != "CONSUMED"
                ):
                    raise StaleCompletionError("INBOX_EVENT_INVALID")
                connection.execute(
                    "INSERT INTO inbox"
                    "(event_id,task_id,dispatch_id,event_sha256,payload,status,created_at) "
                    "VALUES(?,?,?,?,?,?,?)",
                    (
                        event["event_id"], task["task_id"],
                        dispatch["dispatch_id"],
                        inbox_event["event_sha256"],
                        inbox_event["payload"], "CONSUMED",
                        self.now_fn(),
                    ),
                )
            self._set_receipt_state(
                connection,
                task["worktree_id"],
                [*prior_receipts.values(), event["result_sha256"]],
            )
            passed = decision["decision"] == "PASS"
            connection.execute(
                "INSERT INTO gates(task_id,name,status,note) "
                "VALUES(?,?,?,?) "
                "ON CONFLICT(task_id,name) DO UPDATE SET "
                "status=excluded.status,note=excluded.note",
                (
                    task["task_id"],
                    "thinx:conditional",
                    "PASS" if passed else "BLOCKED",
                    decision["reason"],
                ),
            )
            if not passed:
                connection.execute(
                    "UPDATE tasks SET status='OWNER_DECISION_REQUIRED' "
                    "WHERE task_id=?",
                    (task["task_id"],),
                )
                connection.execute(
                    "UPDATE work_orders "
                    "SET status='OWNER_DECISION_REQUIRED' "
                    "WHERE work_order_id=?",
                    (order_row["work_order_id"],),
                )
                return {"status": "OWNER_DECISION_REQUIRED"}
            connection.execute(
                "UPDATE tasks SET status='RETRY_READY' "
                "WHERE task_id=?",
                (task["task_id"],),
            )
            connection.execute(
                "UPDATE work_orders SET status='CREATED' "
                "WHERE work_order_id=?",
                (order_row["work_order_id"],),
            )
            next_dispatch_id = "dsp-" + str(uuid.uuid4())
            action = self._v7_action(
                next_dispatch_id,
                task["task_id"],
                order_row["worker_id"],
                order_row["work_order_id"],
                order_row["packet_path"],
                order_row["packet_sha256"],
            )
            action_raw = contract.canonical_json_bytes(action)
            contract.validate_packet_cap("ACTION.json", action_raw)
            connection.execute(
                "INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    next_dispatch_id,
                    task["task_id"],
                    dispatch["sender_id"],
                    order_row["worker_id"],
                    order_row["packet_sha256"],
                    _json(stored_packet),
                    dispatch["dispatch_id"],
                    "PREPARED",
                    self.now_fn(),
                ),
            )
            connection.execute(
                "INSERT INTO outbox(dispatch_id,payload) VALUES(?,?)",
                (
                    next_dispatch_id,
                    action_raw.decode("utf-8").rstrip(chr(10)),
                ),
            )
            return {
                "status": "RETRY_READY",
                "dispatch_id": next_dispatch_id,
            }

        consumed = self._mutate(operation)
        self._write_action(self._current_action())
        self._write_views()
        return consumed
    def _declared_commit_outputs(
        self, verified_order: Mapping[str, Any]
    ) -> dict[str, dict[str, str]] | None:
        contract = _load_v7_contract()
        outputs = {"c1_outputs": {}, "c2_outputs": {}}
        declaration_modes: list[bool] = []
        claims = verified_order["claims"]
        for ref in verified_order["feature_packet_refs"]:
            try:
                packet_path = self._resolve_under(
                    self.repo,
                    self.repo / Path(*PurePosixPath(ref["path"]).parts),
                )
                raw = self._read_capped_packet(
                    packet_path, "FEATURE_PACKET.json"
                )
                packet = json.loads(raw)
            except (
                OSError,
                UnicodeDecodeError,
                ValueError,
                RuntimeError,
                json.JSONDecodeError,
                contract.ContractError,
            ) as exc:
                raise StaleCompletionError(
                    "WORK_ORDER_AUTHORITY_INCOMPLETE"
                ) from exc
            try:
                packet_valid = (
                    hashlib.sha256(raw).hexdigest() == ref["sha256"]
                    and isinstance(packet, dict)
                    and contract.canonical_json_bytes(packet) == raw
                    and packet.get("schema") == "x9-loop-feature-v1"
                    and packet.get("feature_id") == ref["feature_id"]
                )
            except contract.ContractError as exc:
                raise StaleCompletionError(
                    "WORK_ORDER_AUTHORITY_INCOMPLETE"
                ) from exc
            local_work = packet.get("local_work")
            if not packet_valid:
                raise StaleCompletionError(
                    "WORK_ORDER_AUTHORITY_INCOMPLETE"
                )
            if not isinstance(local_work, Mapping):
                declaration_modes.append(False)
                continue
            has_c1 = "c1_outputs" in local_work
            has_c2 = "c2_outputs" in local_work
            if has_c1 != has_c2:
                raise StaleCompletionError(
                    "WORK_ORDER_AUTHORITY_INCOMPLETE"
                )
            declaration_modes.append(has_c1)
            if not has_c1:
                continue
            for field in outputs:
                values = local_work.get(field)
                if (
                    not isinstance(values, list)
                    or not values
                    or any(not isinstance(item, str) for item in values)
                ):
                    raise StaleCompletionError(
                        "WORK_ORDER_AUTHORITY_INCOMPLETE"
                    )
                seen: set[str] = set()
                for value in values:
                    try:
                        canonical = contract.canonical_repo_path(value)
                        normalized = self._normal_path(canonical)
                    except (
                        ValueError,
                        RuntimeError,
                        contract.ContractError,
                    ) as exc:
                        raise StaleCompletionError(
                            "WORK_ORDER_AUTHORITY_INCOMPLETE"
                        ) from exc
                    folded = normalized.casefold()
                    if canonical != value or folded in seen:
                        raise StaleCompletionError(
                            "WORK_ORDER_AUTHORITY_INCOMPLETE"
                        )
                    seen.add(folded)
                    if not any(
                        self._overlap(
                            normalized, "file", claim["path"], claim["kind"]
                        )
                        for claim in claims
                    ):
                        raise StaleCompletionError(
                            "WORK_ORDER_AUTHORITY_INCOMPLETE"
                        )
                    prior = outputs[field].get(normalized)
                    if prior is not None and prior != canonical:
                        raise StaleCompletionError(
                            "WORK_ORDER_AUTHORITY_INCOMPLETE"
                        )
                    outputs[field][normalized] = canonical
        if any(declaration_modes) and not all(declaration_modes):
            raise StaleCompletionError("WORK_ORDER_AUTHORITY_INCOMPLETE")
        return outputs if any(declaration_modes) else None

    def _consume_v7_worker_event(
        self,
        event: dict[str, Any],
        dispatch: sqlite3.Row,
        task: sqlite3.Row,
        actor: sqlite3.Row | None,
        stored_packet: dict[str, Any],
        latest: sqlite3.Row | None,
        inbox_event: Mapping[str, Any] | None = None,
        _receipt_entries_override: Mapping[str, str] | None = None,
        _preconsumption_result_ready_requester_id: str | None = None,
        _recovery_admission: Callable[[sqlite3.Connection], None] | None = None,
    ) -> dict[str, Any]:
        contract = _load_v7_contract()
        active_states = {"REGISTERED", "RETRY_READY"}
        if (
            event["event_type"] != "WORKER_RESULT"
            or event["role"] != "WORKER"
            or actor is None
            or actor["role"] != "WORKER"
            or event["actor_id"] != task["worker_id"]
            or dispatch["target_id"] != task["worker_id"]
            or dispatch["status"] != "DISPATCHED"
            or task["status"] not in active_states
            or latest is None
            or latest["dispatch_id"] != dispatch["dispatch_id"]
            or event["packet_sha256"] != dispatch["packet_sha256"]
            or set(stored_packet)
            != {
                "schema",
                "task_id",
                "work_order_path",
                "work_order_sha256",
            }
            or stored_packet["schema"]
            != "x9-loop-work-order-dispatch-v1"
            or stored_packet["task_id"] != task["task_id"]
            or stored_packet["work_order_path"]
            != task["owner_packet_path"]
            or stored_packet["work_order_sha256"]
            != task["owner_packet_sha256"]
        ):
            raise StaleCompletionError("STALE_COMPLETION")

        connection = self._connect()
        try:
            order_row = connection.execute(
                "SELECT * FROM work_orders WHERE task_id=?",
                (task["task_id"],),
            ).fetchone()
        finally:
            connection.close()
        if (
            order_row is None
            or order_row["status"] != "CREATED"
            or order_row["worker_id"] != task["worker_id"]
            or order_row["packet_path"]
            != stored_packet["work_order_path"]
            or order_row["packet_sha256"]
            != stored_packet["work_order_sha256"]
        ):
            raise StaleCompletionError("STALE_COMPLETION")
        try:
            verified_order = self.verify_work_order(order_row["work_order_id"])
        except (LoopError, OSError, ValueError) as exc:
            raise StaleCompletionError("WORK_ORDER_INVALID") from exc

        receipt_relative = self._normal_path(event["result_path"])
        expected_receipt = self._normal_path(
            f".devad/workers/{task['worker_id']}/receipts/"
            f"{event['event_id']}.json"
        )
        if receipt_relative != expected_receipt:
            raise StaleCompletionError("STALE_COMPLETION")
        root = Path(task["worktree_path"])
        try:
            result_path = self._resolve_under(
                root, root / Path(*PurePosixPath(receipt_relative).parts)
            )
            raw = self._read_capped_packet(result_path, "RESULT.json")
            result_document = json.loads(raw)
        except (
            contract.ContractError,
            OSError,
            UnicodeDecodeError,
            ValueError,
            RuntimeError,
            json.JSONDecodeError,
        ) as exc:
            raise StaleCompletionError("RESULT_INVALID") from exc
        if (
            hashlib.sha256(raw).hexdigest() != event["result_sha256"]
            or not isinstance(result_document, dict)
            or contract.canonical_json_bytes(result_document) != raw
        ):
            raise StaleCompletionError("RESULT_INVALID")
        expected = {
            "dispatch_id": dispatch["dispatch_id"],
            "event_id": event["event_id"],
            "packet_sha256": dispatch["packet_sha256"],
            "task_id": task["task_id"],
            "work_order_id": order_row["work_order_id"],
            "work_order_sha256": order_row["packet_sha256"],
            "worker_id": task["worker_id"],
        }
        try:
            receipt, disposition = contract.validate_worker_result(
                result_document,
                expected,
                require_proof_bound_approaches=(
                    "autonomy_contract" in verified_order
                ),
            )
        except contract.ContractError as exc:
            raise StaleCompletionError(exc.code) from exc

        def approach_evidence_paths(document: dict[str, Any]) -> set[str]:
            paths: set[str] = set()
            for approach in document.get("approach_receipts", []):
                relative = self._normal_path(approach["evidence_path"])
                expected_path = self._normal_path(
                    f".devad/workers/{document['worker_id']}/proof/"
                    f"{document['event_id']}/approaches/"
                    f"{approach['approach_id']}.json"
                )
                try:
                    path = self._resolve_under(
                        root, root / Path(*PurePosixPath(relative).parts)
                    )
                    evidence_raw = path.read_bytes()
                    evidence = json.loads(evidence_raw)
                except (
                    OSError,
                    UnicodeDecodeError,
                    ValueError,
                    RuntimeError,
                    json.JSONDecodeError,
                ) as exc:
                    raise StaleCompletionError(
                        "APPROACH_EVIDENCE_INVALID"
                    ) from exc
                if (
                    relative != expected_path
                    or relative in paths
                    or hashlib.sha256(evidence_raw).hexdigest()
                    != approach["evidence_sha256"]
                    or evidence != {
                        "action_class": approach["action_class"],
                        "approach_id": approach["approach_id"],
                        "event_id": document["event_id"],
                        "failure_code": approach["failure_code"],
                        "hypothesis": approach["hypothesis"],
                        "next_route": approach["next_route"],
                        "progress": approach["progress"],
                        "route": approach["route"],
                        "schema": "x9-loop-approach-proof-v1",
                        "source_hashes": approach["source_hashes"],
                        "task_id": document["task_id"],
                        "work_order_id": document["work_order_id"],
                        "worker_id": document["worker_id"],
                    }
                    or contract.canonical_json_bytes(evidence) != evidence_raw
                ):
                    raise StaleCompletionError("APPROACH_EVIDENCE_INVALID")
                for source_relative, source_sha256 in (
                    approach["source_hashes"].items()
                ):
                    try:
                        source = self._resolve_under(
                            root,
                            root / Path(*PurePosixPath(source_relative).parts),
                        )
                        source_raw = source.read_bytes()
                    except (OSError, RuntimeError) as exc:
                        raise StaleCompletionError(
                            "APPROACH_EVIDENCE_INVALID"
                        ) from exc
                    if hashlib.sha256(source_raw).hexdigest() != source_sha256:
                        raise StaleCompletionError("APPROACH_EVIDENCE_INVALID")
                paths.add(relative)
            return paths

        current_approach_evidence = approach_evidence_paths(receipt)

        def proof_paths(document: dict[str, Any]) -> set[str]:
            paths: set[str] = set()
            for item in document.get("proof", []):
                relative = self._normal_path(item["path"])
                expected_path = self._normal_path(
                    f".devad/workers/{document['worker_id']}/proof/"
                    f"{document['event_id']}/{item['kind']}.json"
                )
                try:
                    path = self._resolve_under(
                        root,
                        root / Path(*PurePosixPath(relative).parts),
                    )
                    proof_raw = path.read_bytes()
                    proof = json.loads(proof_raw)
                except (
                    OSError,
                    UnicodeDecodeError,
                    ValueError,
                    RuntimeError,
                    json.JSONDecodeError,
                ) as exc:
                    raise StaleCompletionError(
                        "RESULT_PROOF_INVALID"
                    ) from exc
                expected_proof = {
                    "dispatch_id": document["dispatch_id"],
                    "event_id": document["event_id"],
                    "kind": item["kind"],
                    "schema": "x9-loop-proof-v2",
                    "status": "PASS",
                    "task_id": document["task_id"],
                    "work_order_id": document["work_order_id"],
                    "worker_id": document["worker_id"],
                }
                if (
                    relative != expected_path
                    or relative in paths
                    or hashlib.sha256(proof_raw).hexdigest()
                    != item["sha256"]
                    or proof != expected_proof
                    or contract.canonical_json_bytes(proof) != proof_raw
                ):
                    raise StaleCompletionError(
                        "RESULT_PROOF_INVALID"
                    )
                paths.add(relative)
            return paths

        current_proofs = proof_paths(receipt)
        if _receipt_entries_override is None:
            prior_receipts = self._validated_receipt_entries(
                root, exclude_paths={receipt_relative}
            )
        else:
            prior_receipts = {}
            for path, digest in _receipt_entries_override.items():
                normalized = self._normal_path(path)
                if (
                    normalized == receipt_relative
                    or normalized in prior_receipts
                    or not isinstance(digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                ):
                    raise StaleCompletionError("RECEIPT_SET_MISMATCH")
                try:
                    candidate = self._resolve_under(
                        root,
                        root / Path(*PurePosixPath(normalized).parts),
                    )
                    if (
                        self._is_reparse(candidate)
                        or not candidate.is_file()
                        or hashlib.sha256(candidate.read_bytes()).hexdigest()
                        != digest
                    ):
                        raise ValueError("receipt hash")
                except (OSError, RuntimeError, ValueError) as exc:
                    raise StaleCompletionError(
                        "RECEIPT_SET_MISMATCH"
                    ) from exc
                prior_receipts[normalized] = digest
        worker_outbox_relative: str | None = None
        result_ready_relative: str | None = None
        if inbox_event is not None:
            worker_outbox_relative = self._validate_consumed_worker_outbox(
                root,
                inbox_event=inbox_event,
                task_id=task["task_id"],
                worker_id=task["worker_id"],
                worktree_id=task["worktree_id"],
                worktree_path=task["worktree_path"],
                base_sha=task["base_sha"],
                work_order_id=order_row["work_order_id"],
                work_order_sha256=order_row["packet_sha256"],
                dispatch_id=dispatch["dispatch_id"],
                packet_sha256=dispatch["packet_sha256"],
                result_sha256=event["result_sha256"],
            )
            result_ready_relative = self._validate_consumed_result_ready(
                root,
                event_id=event["event_id"],
                task_id=task["task_id"],
                worker_id=task["worker_id"],
                work_order_id=order_row["work_order_id"],
                work_order_sha256=order_row["packet_sha256"],
                dispatch_id=dispatch["dispatch_id"],
                packet_sha256=dispatch["packet_sha256"],
                result_sha256=event["result_sha256"],
                requester_id=(
                    _preconsumption_result_ready_requester_id
                    if _preconsumption_result_ready_requester_id is not None
                    else dispatch["sender_id"]
                ),
                dispatch_sender_id=dispatch["sender_id"],
            )
        allowed_system = {
            receipt_relative,
            *current_approach_evidence,
            *current_proofs,
            *self._registered_rejected_receipt_paths(root),
            *prior_receipts,
            *self._historical_receipt_paths(root),
        }
        for prior_path, prior_sha256 in prior_receipts.items():
            try:
                path = self._resolve_under(
                    root, root / Path(*PurePosixPath(prior_path).parts)
                )
                prior_raw = path.read_bytes()
                prior = json.loads(prior_raw)
            except (
                OSError,
                UnicodeDecodeError,
                ValueError,
                RuntimeError,
                json.JSONDecodeError,
            ) as exc:
                raise StaleCompletionError(
                    "RECEIPT_SET_MISMATCH"
                ) from exc
            if hashlib.sha256(prior_raw).hexdigest() != prior_sha256:
                raise StaleCompletionError("RECEIPT_SET_MISMATCH")
            if prior.get("schema") == "x9-loop-result-v2":
                if contract.canonical_json_bytes(prior) != prior_raw:
                    raise StaleCompletionError(
                        "RECEIPT_SET_MISMATCH"
                    )
                allowed_system.update(proof_paths(prior))

        evidence_connection = self._connect()
        try:
            allowed_system.update(
                self._validated_consumed_worker_outbox_paths(
                    root,
                    evidence_connection,
                    {receipt_relative: event["result_sha256"], **prior_receipts},
                )
            )
        finally:
            evidence_connection.close()

        head_result = self._run_git(
            ["rev-parse", "HEAD"], task["worktree_path"]
        )
        if head_result.returncode:
            raise StaleCompletionError("RESULT_GIT_INVALID")
        head = head_result.stdout.strip()
        changed = {
            self._normal_path(path) for path in receipt["changed_files"]
        }
        if len(changed) != len(receipt["changed_files"]):
            raise StaleCompletionError(
                "RESULT_CHANGED_FILES_INVALID"
            )
        state = self._git_state(task["base_sha"], task["worktree_path"])
        if worker_outbox_relative is not None:
            allowed_system.add(worker_outbox_relative)
        if result_ready_relative is not None:
            allowed_system.add(result_ready_relative)
        dirty = {
            path
            for kind in ("staged", "unstaged", "untracked")
            for path in self._scope_paths(state[kind])
            if path not in allowed_system
        }
        if receipt["outcome"] == "SUCCESS" and changed:
            c1, c2 = receipt["c1"], receipt["c2"]
            attestation = self._normal_path(
                receipt["attestation_path"]
            )
            commit_outputs = self._declared_commit_outputs(verified_order)
            if commit_outputs is None:
                full_name = self._normal_path(
                    f".devad/docs/commits/{c1}.md"
                )
                short = PurePosixPath(attestation).stem.rsplit("-", 1)[-1]
                legacy_name = (
                    re.fullmatch(
                        r"\.devad/docs/commits/"
                        r"[0-9]{4}-[0-9]{2}-[0-9]{2}-"
                        r"[a-z0-9._-]+-[0-9a-f]{7,12}\.md",
                        attestation,
                    )
                    is not None
                    and c1.startswith(short)
                )
                declared_c1 = changed
                declared_c2 = {attestation}
                c2_output_paths = {
                    attestation: receipt["attestation_path"]
                }
                attestation_valid = (
                    attestation == full_name or legacy_name
                )
            else:
                declared_c1 = set(commit_outputs["c1_outputs"])
                declared_c2 = set(commit_outputs["c2_outputs"])
                c2_output_paths = commit_outputs["c2_outputs"]
                attestation_valid = attestation in declared_c2
            base_ancestor = self._run_git(
                ["merge-base", "--is-ancestor", task["base_sha"], c1],
                task["worktree_path"],
            )
            c1_ancestor = self._run_git(
                ["merge-base", "--is-ancestor", c1, c2],
                task["worktree_path"],
            )
            c1_paths = set(
                self._git_history_paths(
                    task["base_sha"], c1, task["worktree_path"]
                )
            )
            c2_paths = set(
                self._git_history_paths(c1, c2, task["worktree_path"])
            )
            if (
                head != c2
                or base_ancestor.returncode
                or c1_ancestor.returncode
                or c1_paths != changed
                or c1_paths != declared_c1
                or c2_paths != declared_c2
                or not attestation_valid
                or dirty
            ):
                raise StaleCompletionError("RESULT_GIT_INVALID")
            for output, canonical_output in sorted(
                c2_output_paths.items()
            ):
                try:
                    output_path = self._resolve_under(
                        root,
                        root / Path(*PurePosixPath(canonical_output).parts),
                    )
                    current_bytes = output_path.read_bytes()
                except (OSError, RuntimeError, ValueError) as exc:
                    raise StaleCompletionError(
                        "RESULT_ATTESTATION_INVALID"
                    ) from exc
                shown = self._run_git_bytes(
                    ["show", f"{c2}:{canonical_output}"],
                    task["worktree_path"],
                )
                if (
                    not output_path.is_file()
                    or shown.returncode
                    or shown.stdout != current_bytes
                ):
                    raise StaleCompletionError(
                        "RESULT_ATTESTATION_INVALID"
                    )
        elif receipt["outcome"] == "SUCCESS":
            if head != task["base_sha"] or dirty:
                raise StaleCompletionError("RESULT_GIT_INVALID")
        elif head != task["base_sha"] or dirty != changed:
            raise StaleCompletionError("RESULT_GIT_INVALID")

        candidate_handoff: dict[str, Any] | None = None
        if receipt["outcome"] == "SUCCESS_CANDIDATE":
            files: list[dict[str, Any]] = []
            for relative in sorted(changed):
                lexical = root / Path(*PurePosixPath(relative).parts)
                if os.path.lexists(lexical):
                    try:
                        candidate = self._resolve_under(root, lexical)
                    except (OSError, RuntimeError, ValueError) as exc:
                        raise StaleCompletionError(
                            "CANDIDATE_HANDOFF_FILE_INVALID"
                        ) from exc
                    if self._is_reparse(candidate) or not candidate.is_file():
                        raise StaleCompletionError(
                            "CANDIDATE_HANDOFF_FILE_INVALID"
                        )
                    files.append(
                        {
                            "path": relative,
                            "sha256": self._digest_file(candidate),
                            "state": "PRESENT",
                        }
                    )
                else:
                    try:
                        self._resolve_under(root, lexical.parent)
                    except (OSError, RuntimeError, ValueError) as exc:
                        raise StaleCompletionError(
                            "CANDIDATE_HANDOFF_FILE_INVALID"
                        ) from exc
                    files.append(
                        {"path": relative, "sha256": None, "state": "DELETED"}
                    )
            candidate_handoff = contract.validate_candidate_handoff(
                {
                    "files": files,
                    "schema": "x9-loop-candidate-handoff-v1",
                    "source_base_sha": task["base_sha"],
                    "source_event_id": event["event_id"],
                    "source_result_sha256": event["result_sha256"],
                    "source_task_id": task["task_id"],
                    "source_worker_id": task["worker_id"],
                    "source_work_order_id": order_row["work_order_id"],
                    "source_worktree_id": task["worktree_id"],
                    "source_worktree_path": str(root),
                }
            )

        def operation(
            connection: sqlite3.Connection,
        ) -> dict[str, Any]:
            if connection.execute(
                "SELECT 1 FROM events WHERE event_id=?",
                (event["event_id"],),
            ).fetchone():
                return {"status": "DUPLICATE_EVENT"}
            current = connection.execute(
                "SELECT t.status AS task_status,"
                "wo.status AS order_status,d.status AS dispatch_status "
                "FROM tasks t JOIN work_orders wo ON wo.task_id=t.task_id "
                "JOIN dispatches d ON d.task_id=t.task_id "
                "WHERE t.task_id=? AND d.dispatch_id=?",
                (task["task_id"], dispatch["dispatch_id"]),
            ).fetchone()
            current_latest = connection.execute(
                "SELECT dispatch_id FROM dispatches WHERE task_id=? "
                "ORDER BY rowid DESC LIMIT 1",
                (task["task_id"],),
            ).fetchone()
            if (
                current is None
                or current["dispatch_status"] != "DISPATCHED"
                or current["order_status"] != "CREATED"
                or current["task_status"] not in active_states
                or current_latest is None
                or current_latest["dispatch_id"]
                != dispatch["dispatch_id"]
            ):
                raise StaleCompletionError("STALE_COMPLETION")
            if _recovery_admission is not None:
                _recovery_admission(connection)
            continuation: dict[str, Any] | None = None
            for path in changed:
                if not self._claimed(
                    connection, task["task_id"], path
                ):
                    raise ScopeBreachError(f"SCOPE_BREACH:{path}")
            connection.execute(
                "INSERT INTO events("
                "event_id,task_id,dispatch_id,event_sha256,created_at"
                ") VALUES(?,?,?,?,?)",
                (
                    event["event_id"],
                    task["task_id"],
                    dispatch["dispatch_id"],
                    event["result_sha256"],
                    self.now_fn(),
                ),
            )
            if inbox_event is not None:
                if (
                    inbox_event.get("event_id") != event["event_id"]
                    or inbox_event.get("dispatch_id")
                    != dispatch["dispatch_id"]
                    or inbox_event.get("status") != "CONSUMED"
                ):
                    raise StaleCompletionError("INBOX_EVENT_INVALID")
                connection.execute(
                    "INSERT INTO inbox"
                    "(event_id,task_id,dispatch_id,event_sha256,payload,status,created_at) "
                    "VALUES(?,?,?,?,?,?,?)",
                    (
                        event["event_id"], task["task_id"],
                        dispatch["dispatch_id"], inbox_event["event_sha256"],
                        inbox_event["payload"], "CONSUMED", self.now_fn(),
                    ),
                )
            self._set_receipt_state(
                connection,
                task["worktree_id"],
                [*prior_receipts.values(), event["result_sha256"]],
            )
            connection.execute(
                "UPDATE dispatches SET status='COMPLETE' "
                "WHERE dispatch_id=?",
                (dispatch["dispatch_id"],),
            )
            if disposition == "FEATURE_DONE":
                connection.execute(
                    "UPDATE tasks SET status='COMPLETE' WHERE task_id=?",
                    (task["task_id"],),
                )
                connection.execute(
                    "UPDATE work_orders SET status='COMPLETE' "
                    "WHERE work_order_id=?",
                    (order_row["work_order_id"],),
                )
                self._remember_completed_task(
                    connection, task["task_id"]
                )
                connection.execute(
                    "INSERT INTO metrics(key,value) VALUES(?,'0') "
                    "ON CONFLICT(key) DO UPDATE SET value='0'",
                    (f"blocked:{task['task_id']}",),
                )
                connection.execute(
                    "INSERT INTO metrics(key,value) "
                    "VALUES('completed_clean_dispatches','1') "
                    "ON CONFLICT(key) DO UPDATE SET "
                    "value=CAST(value AS INTEGER)+1"
                )
                try:
                    successor = self.create_work_order(
                        program_id=order_row["program_id"],
                        stop=verified_order["stop_contract"],
                        linx_id=dispatch["sender_id"],
                        action_class=verified_order["action_class"],
                        _connection=connection,
                        _candidate_handoff=candidate_handoff,
                    )
                except TaskNotReadyError as exc:
                    reason = str(exc)
                    if reason not in {
                        "PROGRAM_COMPLETE",
                        "DEPENDENCY_NOT_COMPLETE",
                    }:
                        raise
                    continuation = {
                        "status": "WAIT",
                        "reason": reason,
                    }
                else:
                    successor.pop("_action_raw", None)
                    continuation = successor
            elif disposition in {
                "HARD_BLOCKER_AFTER_2_PROOFS",
                "HARD_BLOCKER_AFTER_3_PROOFS",
            }:
                connection.execute(
                    "UPDATE tasks SET status='THINX_REVIEW_REQUIRED' "
                    "WHERE task_id=?",
                    (task["task_id"],),
                )
                connection.execute(
                    "UPDATE work_orders "
                    "SET status='THINX_REVIEW_REQUIRED' "
                    "WHERE work_order_id=?",
                    (order_row["work_order_id"],),
                )
                connection.execute(
                    "INSERT INTO gates(task_id,name,status,note) "
                    "VALUES(?,?,'PENDING',?) "
                    "ON CONFLICT(task_id,name) DO UPDATE SET "
                    "status='PENDING',note=excluded.note",
                    (
                        task["task_id"],
                        "thinx:conditional",
                        "three verified approaches",
                    ),
                )
            else:
                connection.execute(
                    "UPDATE tasks SET status=? WHERE task_id=?",
                    (disposition, task["task_id"]),
                )
                connection.execute(
                    "UPDATE work_orders SET status=? "
                    "WHERE work_order_id=?",
                    (disposition, order_row["work_order_id"]),
                )
            response = {"status": disposition}
            if continuation is not None:
                response["continuation"] = continuation
            return response

        consumed = self._mutate(operation)
        identity = {
            "dispatch_id": dispatch["dispatch_id"],
            "event_id": event["event_id"],
            "packet_sha256": dispatch["packet_sha256"],
            "result_path": event["result_path"],
            "result_sha256": event["result_sha256"],
            "task_id": task["task_id"],
            "work_order_id": order_row["work_order_id"],
            "work_order_sha256": order_row["packet_sha256"],
            "worker_id": task["worker_id"],
        }
        consumed["result_ready"] = self._emit_result_ready_for_identity(
            identity,
            return_to_task_id=dispatch["sender_id"],
        )
        self._write_action(self._current_action())
        self._write_views()
        return consumed
    def consume_event(
        self, event: dict[str, Any], *,
        _inbox_event: Mapping[str, Any] | None = None,
        _receipt_entries_override: Mapping[str, str] | None = None,
        _preconsumption_result_ready_requester_id: str | None = None,
        _recovery_admission: Callable[[sqlite3.Connection], None] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(event, dict) or not isinstance(event.get("event_id"), str) or not event["event_id"]:
            raise StaleCompletionError("EVENT_INVALID")
        if self._duplicate_event(event["event_id"]):
            self._publish_current_action()
            return {"status": "DUPLICATE_EVENT"}
        required = ("event_type", "task_id", "dispatch_id", "actor_id", "role", "packet_sha256", "result_path", "result_sha256")
        if any(not isinstance(event.get(field), str) or not event[field] for field in required):
            raise StaleCompletionError("EVENT_INVALID")
        event_type = event["event_type"]
        expected_role = {"WORKER_RESULT": "WORKER", "THINX_DECISION": "THINX"}.get(event_type)
        if expected_role is None or event["role"] != expected_role or not re.fullmatch(r"[0-9a-f]{64}", event["result_sha256"]):
            raise StaleCompletionError("EVENT_INVALID")
        try:
            receipt_relative = self._normal_path(event["result_path"])
        except ScopeBreachError as exc:
            raise StaleCompletionError("EVENT_INVALID") from exc
        connection = self._connect()
        try:
            dispatch = connection.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (event["dispatch_id"],)).fetchone()
            task = connection.execute("SELECT t.*,w.path AS worktree_path FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id WHERE t.task_id=?", (event["task_id"],)).fetchone()
            actor = connection.execute("SELECT role FROM actors WHERE actor_id=?", (event["actor_id"],)).fetchone()
            latest = connection.execute("SELECT dispatch_id,status FROM dispatches WHERE task_id=? ORDER BY rowid DESC LIMIT 1", (event["task_id"],)).fetchone()
            review_ack = connection.execute("SELECT 1 FROM deliveries WHERE dispatch_id=? AND phase='REVIEW' AND lower(result) IN ('ack','acknowledged') ORDER BY id DESC LIMIT 1", (event["dispatch_id"],)).fetchone()
        finally:
            connection.close()
        if not dispatch or not task or dispatch["task_id"] != task["task_id"]:
            raise StaleCompletionError("STALE_COMPLETION")
        try:
            stored_packet = json.loads(dispatch["packet"])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise StaleCompletionError("STALE_COMPLETION") from exc
        if stored_packet.get("schema") == "x9-loop-work-order-dispatch-v1":
            if expected_role == "WORKER":
                return self._consume_v7_worker_event(
                    event, dispatch, task, actor, stored_packet, latest,
                    _inbox_event,
                    _receipt_entries_override,
                    _preconsumption_result_ready_requester_id,
                    _recovery_admission,
                )
            return self._consume_v7_thinx_event(
                event, dispatch, task, actor, stored_packet, latest,
                _inbox_event,
            )
        worker_ready = (
            expected_role == "WORKER" and dispatch and task
            and dispatch["status"] == "DISPATCHED"
            and task["status"] in {"REGISTERED", "RETRY_READY"}
            and latest and latest["dispatch_id"] == dispatch["dispatch_id"]
        )
        thinx_ready = (
            expected_role == "THINX" and dispatch and task
            and dispatch["status"] == "COMPLETE"
            and task["status"] == "THINX_REVIEW_REQUIRED"
            and latest and latest["dispatch_id"] == dispatch["dispatch_id"]
            and review_ack
        )
        if (not dispatch or not task or dispatch["task_id"] != task["task_id"]
                or not (worker_ready or thinx_ready)
                or not actor or actor["role"] != expected_role
                or event["packet_sha256"] != dispatch["packet_sha256"]):
            raise StaleCompletionError("STALE_COMPLETION")
        try:
            stored_worktree = Path(stored_packet["worktree_path"]).resolve(strict=True)
            current_worktree = Path(task["worktree_path"]).resolve(strict=True)
        except (KeyError, TypeError, ValueError, OSError, RuntimeError, json.JSONDecodeError) as exc:
            raise StaleCompletionError("STALE_COMPLETION") from exc
        if (stored_packet.get("task_id") != task["task_id"]
                or stored_packet.get("worktree_id") != task["worktree_id"]
                or stored_worktree != current_worktree
                or stored_packet.get("base_sha") != task["base_sha"]
                or stored_packet.get("target_actor_id") != task["worker_id"]):
            raise StaleCompletionError("STALE_COMPLETION")
        if expected_role == "WORKER" and event["actor_id"] != task["worker_id"]:
            raise StaleCompletionError("STALE_COMPLETION")
        expected_receipt = self._normal_path(f".devad/workers/{event['actor_id']}/receipts/{event['event_id']}.json")
        if receipt_relative != expected_receipt:
            raise StaleCompletionError("STALE_COMPLETION")
        worktree_root = Path(task["worktree_path"])
        try:
            result_path = self._resolve_under(worktree_root, worktree_root / Path(*PurePosixPath(receipt_relative).parts))
            data = result_path.read_bytes()
            receipt = json.loads(data.decode("utf-8"))
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            raise StaleCompletionError("STALE_COMPLETION") from exc
        if not isinstance(receipt, dict) or hashlib.sha256(data).hexdigest() != event["result_sha256"]:
            raise StaleCompletionError("STALE_COMPLETION")
        prior_receipts = self._validated_receipt_entries(
            worktree_root, exclude_paths={receipt_relative}
        )
        allowed_system = {receipt_relative, *self._verify_owner_packet(task), *self._controller_snapshot_evidence(worktree_root), *self._historical_receipt_paths(worktree_root)}
        if expected_role == "WORKER":
            expected = {"schema": "x9-loop-lite-result-v1", "event_id": event["event_id"], "task_id": task["task_id"], "dispatch_id": dispatch["dispatch_id"], "worker_id": task["worker_id"], "role": "WORKER", "packet_sha256": dispatch["packet_sha256"]}
            if any(receipt.get(field) != value for field, value in expected.items()):
                raise StaleCompletionError("RESULT_INVALID")
            changed_files = receipt.get("changed_files")
            proof = receipt.get("proof")
            outcome = receipt.get("outcome")
            if not isinstance(changed_files, list) or not all(isinstance(item, str) for item in changed_files) or not isinstance(proof, list) or outcome not in {"COMPLETE", "BLOCKED"}:
                raise StaleCompletionError("RESULT_INVALID")
            allowed_system = {receipt_relative, *self._verify_owner_packet(task), *self._controller_snapshot_evidence(worktree_root), *self._historical_receipt_paths(worktree_root)}
            if outcome == "COMPLETE" and changed_files:
                if not isinstance(receipt.get("c1"), str) or not isinstance(receipt.get("c2"), str) or not re.fullmatch(r"[0-9a-f]{40}", receipt["c1"]) or not re.fullmatch(r"[0-9a-f]{40}", receipt["c2"]) or not isinstance(proof, list):
                    raise StaleCompletionError("RESULT_INVALID")
                proof_paths: set[str] = set()
                for item in proof:
                    if not isinstance(item, dict) or item.get("kind") not in {"security", "tests"} or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
                        raise StaleCompletionError("RESULT_INVALID")
                    kind = item["kind"]
                    proof_path = self._normal_path(item["path"])
                    expected_proof = self._normal_path(f".devad/workers/{task['worker_id']}/proof/{event['event_id']}/{kind}.json")
                    if proof_path != expected_proof or proof_path in proof_paths:
                        raise StaleCompletionError("RESULT_INVALID")
                    try:
                        candidate = self._resolve_under(worktree_root, worktree_root / Path(*PurePosixPath(proof_path).parts))
                        proof_data = candidate.read_bytes()
                        proof_document = json.loads(proof_data.decode("utf-8"))
                    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
                        raise StaleCompletionError("RESULT_INVALID") from exc
                    expected_document = {
                        "schema": "x9-loop-lite-proof-v1", "event_id": event["event_id"],
                        "task_id": task["task_id"], "dispatch_id": dispatch["dispatch_id"],
                        "worker_id": task["worker_id"], "role": "WORKER", "kind": kind, "status": "PASS",
                    }
                    if hashlib.sha256(proof_data).hexdigest() != item["sha256"] or proof_document != expected_document:
                        raise StaleCompletionError("RESULT_INVALID")
                    proof_paths.add(proof_path)
                if proof_paths != {
                    self._normal_path(f".devad/workers/{task['worker_id']}/proof/{event['event_id']}/security.json"),
                    self._normal_path(f".devad/workers/{task['worker_id']}/proof/{event['event_id']}/tests.json"),
                }:
                    raise StaleCompletionError("RESULT_INVALID")
                allowed_system.update(proof_paths)
                c1_paths = set(self._git_history_paths(task["base_sha"], receipt["c1"], task["worktree_path"]))
                c2_paths = set(self._git_history_paths(receipt["c1"], receipt["c2"], task["worktree_path"]))
                changed_paths = {self._normal_path(path) for path in changed_files}
                attestation = self._normal_path(".devad/docs/commits/" + receipt["c1"] + ".md")
                c1_ancestor = self._run_git(["merge-base", "--is-ancestor", receipt["c1"], receipt["c2"]], task["worktree_path"])
                c2_ancestor = self._run_git(["merge-base", "--is-ancestor", receipt["c2"], "HEAD"], task["worktree_path"])
                current_head = self._run_git(["rev-parse", "HEAD"], task["worktree_path"])
                try:
                    attestation_path = self._resolve_under(worktree_root, worktree_root / Path(*PurePosixPath(attestation).parts))
                except (OSError, ValueError, RuntimeError) as exc:
                    raise StaleCompletionError("RESULT_INVALID") from exc
                shown = self._run_git(["show", f"{receipt['c2']}:{attestation}"], task["worktree_path"])
                c1_system = proof_paths | self._verify_owner_packet(task)
                c1_extra = sorted(c1_paths - c1_system - changed_paths)
                c2_extra = sorted(c2_paths - {attestation})
                if c1_extra or c2_extra:
                    raise ScopeBreachError(f"SCOPE_BREACH:{(c1_extra or c2_extra)[0]}")
                if (len(changed_paths) != len(changed_files) or c1_ancestor.returncode or c2_ancestor.returncode
                        or current_head.returncode or current_head.stdout.strip() != receipt["c2"]
                        or c1_paths - c1_system != changed_paths or c2_paths != {attestation}
                        or not attestation_path.is_file() or shown.returncode
                        or shown.stdout.encode("utf-8") != attestation_path.read_bytes()):
                    raise StaleCompletionError("RESULT_INVALID")
                allowed_system.add(attestation)
            if outcome == "BLOCKED" and (not isinstance(receipt.get("blocker"), str) or not receipt["blocker"]):
                raise StaleCompletionError("RESULT_INVALID")
            if outcome == "COMPLETE":
                expected_head = receipt["c2"] if changed_files else task["base_sha"]
                current_head = self._run_git(["rev-parse", "HEAD"], task["worktree_path"])
                working = {
                    key: self._scope_paths(value)
                    for key, value in self._git_state(task["base_sha"], task["worktree_path"]).items()
                    if key in {"staged", "unstaged", "untracked"}
                }
                permitted_dirty = allowed_system | set(prior_receipts) | {receipt_relative}
                unexpected_dirty = sorted({path for values in working.values() for path in values if path not in permitted_dirty})
                if current_head.returncode or current_head.stdout.strip() != expected_head:
                    raise StaleCompletionError("RESULT_INVALID")
                if unexpected_dirty:
                    raise ScopeBreachError(f"SCOPE_BREACH:{unexpected_dirty[0]}")
        else:
            expected = {"schema": "x9-loop-lite-thinx-decision-v1", "event_id": event["event_id"], "task_id": task["task_id"], "dispatch_id": dispatch["dispatch_id"], "actor_id": event["actor_id"], "role": "THINX", "packet_sha256": dispatch["packet_sha256"]}
            if any(receipt.get(field) != value for field, value in expected.items()) or receipt.get("decision") not in {"PASS", "BLOCKED", "FAIL"}:
                raise StaleCompletionError("RESULT_INVALID")
            changed_files = []
            outcome = None
        actual_paths = self._actual_git_paths(task["task_id"], receipt_relative, set(prior_receipts))
        if expected_role == "WORKER" and outcome == "COMPLETE" and not changed_files:
            if any(path not in allowed_system for path in actual_paths):
                raise StaleCompletionError("RESULT_INVALID")
        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            if connection.execute("SELECT 1 FROM events WHERE event_id=?", (event["event_id"],)).fetchone():
                return {"status": "DUPLICATE_EVENT"}
            latest = connection.execute("SELECT dispatch_id,status FROM dispatches WHERE task_id=? ORDER BY rowid DESC LIMIT 1", (task["task_id"],)).fetchone()
            current_task = connection.execute("SELECT status FROM tasks WHERE task_id=?", (task["task_id"],)).fetchone()
            current_dispatch = connection.execute("SELECT status FROM dispatches WHERE dispatch_id=?", (dispatch["dispatch_id"],)).fetchone()
            review_ack = connection.execute("SELECT 1 FROM deliveries WHERE dispatch_id=? AND phase='REVIEW' AND lower(result) IN ('ack','acknowledged') ORDER BY id DESC LIMIT 1", (dispatch["dispatch_id"],)).fetchone()
            worker_ready = expected_role == "WORKER" and current_dispatch and current_dispatch["status"] == "DISPATCHED" and current_task and current_task["status"] in {"REGISTERED", "RETRY_READY"}
            thinx_ready = expected_role == "THINX" and current_dispatch and current_dispatch["status"] == "COMPLETE" and current_task and current_task["status"] == "THINX_REVIEW_REQUIRED" and review_ack
            if (not latest or latest["dispatch_id"] != dispatch["dispatch_id"] or not (worker_ready or thinx_ready)):
                raise StaleCompletionError("STALE_COMPLETION")
            for changed in [*changed_files, *actual_paths]:
                try:
                    canonical = self._normal_path(changed)
                except ScopeBreachError as exc:
                    raise StaleCompletionError("RESULT_INVALID") from exc
                if canonical in allowed_system:
                    continue
                if not self._claimed(connection, task["task_id"], canonical):
                    raise ScopeBreachError(f"SCOPE_BREACH:{canonical}")
            connection.execute("INSERT INTO events(event_id,task_id,dispatch_id,event_sha256,created_at) VALUES(?,?,?,?,?)", (event["event_id"], task["task_id"], dispatch["dispatch_id"], event["result_sha256"], self.now_fn()))
            self._set_receipt_state(
                connection, task["worktree_id"],
                [*prior_receipts.values(), event["result_sha256"]],
            )
            if expected_role == "THINX":
                status = "PASS" if receipt["decision"] == "PASS" else "BLOCKED"
                connection.execute("INSERT INTO gates(task_id,name,status,note) VALUES(?,?,?,?) ON CONFLICT(task_id,name) DO UPDATE SET status=excluded.status,note=excluded.note", (task["task_id"], f"thinx:{event['actor_id']}", status, receipt["decision"]))
                if status == "PASS":
                    connection.execute("UPDATE tasks SET status='REGISTERED' WHERE task_id=?", (task["task_id"],))
                    connection.execute("INSERT INTO metrics(key,value) VALUES(?, '0') ON CONFLICT(key) DO UPDATE SET value='0'", (f"blocked:{task['task_id']}",))
                return {"status": "THINX_CONSUMED"}
            if outcome == "BLOCKED":
                metric_key = f"blocked:{task['task_id']}"
                old_count = connection.execute("SELECT value FROM metrics WHERE key=?", (metric_key,)).fetchone()
                count = int(old_count[0]) + 1 if old_count else 1
                connection.execute("INSERT INTO metrics(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (metric_key, str(count)))
                task_status = "THINX_REVIEW_REQUIRED" if count >= 3 else "RETRY_READY"
                connection.execute("UPDATE tasks SET status=? WHERE task_id=?", (task_status, task["task_id"]))
                connection.execute("UPDATE dispatches SET status='COMPLETE' WHERE dispatch_id=?", (dispatch["dispatch_id"],))
                return {"status": task_status}
            previous = connection.execute("SELECT status FROM tasks WHERE task_id=?", (task["task_id"],)).fetchone()
            connection.execute("UPDATE tasks SET status='COMPLETE' WHERE task_id=?", (task["task_id"],))
            connection.execute("UPDATE dispatches SET status='COMPLETE' WHERE dispatch_id=?", (dispatch["dispatch_id"],))
            if previous and previous[0] != "COMPLETE":
                self._remember_completed_task(connection, task["task_id"])
                connection.execute("INSERT INTO metrics(key,value) VALUES(?,'0') ON CONFLICT(key) DO UPDATE SET value='0'", (f"blocked:{task['task_id']}",))
                connection.execute("INSERT INTO metrics(key,value) VALUES('completed_clean_dispatches','1') ON CONFLICT(key) DO UPDATE SET value=CAST(value AS INTEGER)+1")
            return {"status": "CONSUMED"}
        result = self._mutate(operation)
        self._write_views()
        return result
    def supersede_paused(
        self, task_id: str, result_sha256: str
    ) -> dict[str, Any]:
        if not isinstance(task_id, str) or not task_id:
            raise IdentityError("TASK_UNKNOWN")
        if (
            not isinstance(result_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", result_sha256) is None
        ):
            raise StaleCompletionError("SUPERSEDE_RECEIPT_MISMATCH")
        self._assert_durable()

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            task = connection.execute(
                "SELECT t.status,t.worker_id,w.path AS worktree_path "
                "FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "WHERE t.task_id=?", (task_id,)
            ).fetchone()
            if task is None:
                raise IdentityError("TASK_UNKNOWN")
            order = connection.execute(
                "SELECT work_order_id,status FROM work_orders "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            gate = connection.execute(
                "SELECT status,note FROM gates "
                "WHERE task_id=? AND name='lifecycle:superseded'",
                (task_id,),
            ).fetchone()
            expected_note = f"result_sha256={result_sha256}"
            if task["status"] == "SUPERSEDED":
                if (
                    order is not None
                    and order["status"] == "SUPERSEDED"
                    and gate is not None
                    and gate["status"] == "PASS"
                    and gate["note"] == expected_note
                ):
                    return {"status": "ALREADY_SUPERSEDED", "task_id": task_id}
                raise StaleCompletionError("SUPERSEDE_RECEIPT_MISMATCH")
            if (
                task["status"] != "TASK_SCOPE_PAUSED"
                or order is None
                or order["status"] not in {"TASK_SCOPE_PAUSED", "EXPIRED"}
            ):
                raise TaskNotReadyError("TASK_NOT_PAUSED")
            dispatch = connection.execute(
                "SELECT dispatch_id,status FROM dispatches "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if dispatch is None or dispatch["status"] != "COMPLETE":
                raise TaskNotReadyError("TASK_NOT_PAUSED")
            if connection.execute(
                "SELECT 1 FROM dispatches WHERE task_id=? "
                "AND status IN ('PREPARED','DISPATCHED') LIMIT 1",
                (task_id,),
            ).fetchone():
                raise TaskNotReadyError("TASK_NOT_PAUSED")
            event = connection.execute(
                "SELECT event_id,event_sha256 FROM events "
                "WHERE task_id=? AND dispatch_id=? "
                "ORDER BY rowid DESC LIMIT 1",
                (task_id, dispatch["dispatch_id"]),
            ).fetchone()
            if event is None or event["event_sha256"] != result_sha256:
                raise StaleCompletionError("SUPERSEDE_RECEIPT_MISMATCH")
            expected_receipt = self._normal_path(
                f".devad/workers/{task['worker_id']}/receipts/"
                f"{event['event_id']}.json"
            )
            receipt_entries = self._validated_receipt_entries(
                Path(task["worktree_path"]), connection
            )
            if receipt_entries.get(expected_receipt) != result_sha256:
                raise StaleCompletionError("SUPERSEDE_RECEIPT_MISMATCH")
            connection.execute(
                "UPDATE tasks SET status='SUPERSEDED' WHERE task_id=?",
                (task_id,),
            )
            connection.execute(
                "UPDATE work_orders SET status='SUPERSEDED' "
                "WHERE work_order_id=?",
                (order["work_order_id"],),
            )
            connection.execute(
                "INSERT INTO gates(task_id,name,status,note) "
                "VALUES(?,'lifecycle:superseded','PASS',?) "
                "ON CONFLICT(task_id,name) DO UPDATE SET "
                "status='PASS',note=excluded.note",
                (task_id, expected_note),
            )
            return {"status": "SUPERSEDED", "task_id": task_id}

        result = self._mutate(operation)
        self._write_action(self._current_action())
        self._write_views()
        return result
    def supersede_owner_decision(
        self, task_id: str, result_sha256: str
    ) -> dict[str, Any]:
        if not isinstance(task_id, str) or not task_id:
            raise IdentityError("TASK_UNKNOWN")
        if (
            not isinstance(result_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", result_sha256) is None
        ):
            raise StaleCompletionError("OWNER_DECISION_RECEIPT_MISMATCH")
        self._assert_durable()

        class AlreadySuperseded(Exception):
            pass

        def operation(connection: sqlite3.Connection) -> dict[str, Any]:
            task = connection.execute(
                "SELECT t.status,t.worker_id,w.path AS worktree_path "
                "FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id "
                "WHERE t.task_id=?",
                (task_id,),
            ).fetchone()
            if task is None:
                raise IdentityError("TASK_UNKNOWN")
            order = connection.execute(
                "SELECT work_order_id,status,packet_sha256,worker_id "
                "FROM work_orders "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            gate = connection.execute(
                "SELECT status,note FROM gates WHERE task_id=? "
                "AND name='lifecycle:owner-decision-superseded'",
                (task_id,),
            ).fetchone()
            expected_note = f"result_sha256={result_sha256}"
            repeated = task["status"] == "SUPERSEDED"
            if repeated:
                if (
                    order is None
                    or order["status"] != "SUPERSEDED"
                    or gate is None
                    or gate["status"] != "PASS"
                    or gate["note"] != expected_note
                ):
                    raise StaleCompletionError(
                        "OWNER_DECISION_RECEIPT_MISMATCH"
                    )
            elif (
                task["status"] != "OWNER_DECISION_REQUIRED"
                or order is None
                or order["status"] != "OWNER_DECISION_REQUIRED"
            ):
                raise TaskNotReadyError("TASK_NOT_OWNER_DECISION_REQUIRED")
            dispatch = connection.execute(
                "SELECT dispatch_id,status,packet_sha256,target_id "
                "FROM dispatches "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if dispatch is None or dispatch["status"] != "COMPLETE":
                raise TaskNotReadyError("TASK_NOT_OWNER_DECISION_REQUIRED")
            if connection.execute(
                "SELECT 1 FROM dispatches WHERE task_id=? "
                "AND status IN ('PREPARED','DISPATCHED') LIMIT 1",
                (task_id,),
            ).fetchone():
                raise TaskNotReadyError("TASK_NOT_OWNER_DECISION_REQUIRED")
            if (
                order["worker_id"] != task["worker_id"]
                or dispatch["target_id"] != task["worker_id"]
            ):
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                )
            event = connection.execute(
                "SELECT event_id,event_sha256 FROM events "
                "WHERE task_id=? AND dispatch_id=? "
                "ORDER BY rowid DESC LIMIT 1",
                (task_id, dispatch["dispatch_id"]),
            ).fetchone()
            if event is None or event["event_sha256"] != result_sha256:
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                )
            expected_receipt = self._normal_path(
                f".devad/workers/{task['worker_id']}/receipts/"
                f"{event['event_id']}.json"
            )
            root = Path(task["worktree_path"])
            contract = _load_v7_contract()
            try:
                receipt_entries = self._validated_receipt_entries(
                    root, connection
                )
                receipt_path = self._resolve_under(
                    root,
                    root / Path(*PurePosixPath(expected_receipt).parts),
                )
                raw = self._read_capped_packet(receipt_path, "RESULT.json")
                receipt = json.loads(raw)
                canonical = contract.canonical_json_bytes(receipt)
            except (
                contract.ContractError,
                OSError,
                UnicodeDecodeError,
                ValueError,
                RuntimeError,
                json.JSONDecodeError,
            ) as exc:
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                ) from exc
            expected = {
                "dispatch_id": dispatch["dispatch_id"],
                "event_id": event["event_id"],
                "packet_sha256": dispatch["packet_sha256"],
                "role": "WORKER",
                "schema": "x9-loop-result-v2",
                "task_id": task_id,
                "work_order_id": order["work_order_id"],
                "work_order_sha256": order["packet_sha256"],
                "worker_id": task["worker_id"],
            }
            try:
                validated_receipt, disposition = contract.validate_worker_result(
                    receipt,
                    {
                        field: expected[field]
                        for field in (
                            "dispatch_id",
                            "event_id",
                            "packet_sha256",
                            "task_id",
                            "work_order_id",
                            "work_order_sha256",
                            "worker_id",
                        )
                    },
                )
            except contract.ContractError as exc:
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                ) from exc
            if (
                receipt_entries.get(expected_receipt) != result_sha256
                or hashlib.sha256(raw).hexdigest() != result_sha256
                or canonical != raw
                or not isinstance(receipt, dict)
                or any(receipt.get(field) != value for field, value in expected.items())
                or validated_receipt.get("outcome") != "HARD_EXTERNAL"
                or disposition != "OWNER_DECISION_REQUIRED"
            ):
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                )
            try:
                final_raw = self._read_capped_packet(
                    receipt_path, "RESULT.json"
                )
            except (OSError, ValueError, RuntimeError) as exc:
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                ) from exc
            if final_raw != raw:
                raise StaleCompletionError(
                    "OWNER_DECISION_RECEIPT_MISMATCH"
                )
            if repeated:
                raise AlreadySuperseded
            connection.execute(
                "UPDATE tasks SET status='SUPERSEDED' WHERE task_id=?",
                (task_id,),
            )
            connection.execute(
                "UPDATE work_orders SET status='SUPERSEDED' "
                "WHERE work_order_id=?",
                (order["work_order_id"],),
            )
            connection.execute(
                "INSERT INTO gates(task_id,name,status,note) "
                "VALUES(?,'lifecycle:owner-decision-superseded','PASS',?) "
                "ON CONFLICT(task_id,name) DO UPDATE SET "
                "status='PASS',note=excluded.note",
                (task_id, expected_note),
            )
            return {"status": "SUPERSEDED", "task_id": task_id}

        try:
            result = self._mutate(operation)
        except AlreadySuperseded:
            return {"status": "ALREADY_SUPERSEDED", "task_id": task_id}
        self._write_action(self._current_action())
        self._write_views()
        return result

    def recover_pre_dispatch_worker_result_contract_drift(
        self, work_order_id: str, work_order_sha256: str
    ) -> dict[str, Any]:
        """Retire one never-delivered order blocked only by result-contract drift."""
        if not isinstance(work_order_id, str) or not work_order_id:
            raise IdentityError("WORK_ORDER_UNKNOWN")
        if (
            not isinstance(work_order_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", work_order_sha256) is None
        ):
            raise IdentityError("WORK_ORDER_HASH_MISMATCH")
        self._assert_durable()
        contract = _load_v7_contract()

        with self._mutation_lock:
            try:
                self.verify_work_order(work_order_id)
            except IdentityError as exc:
                if str(exc) != "WORK_ORDER_DRIFT:worker_result_contract":
                    raise TaskNotReadyError(
                        "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE"
                    ) from exc
            else:
                raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")

            def admission(connection: sqlite3.Connection) -> sqlite3.Row:
                row = connection.execute(
                    "SELECT wo.work_order_id,wo.packet_path,wo.packet_sha256,"
                    "wo.status AS order_status,t.task_id,t.worker_id,"
                    "t.status AS task_status,d.dispatch_id,d.target_id,"
                    "d.packet_sha256 AS dispatch_packet_sha256,"
                    "d.packet AS dispatch_packet,d.status AS dispatch_status,"
                    "o.payload AS outbox_payload "
                    "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "LEFT JOIN outbox o ON o.dispatch_id=d.dispatch_id "
                    "WHERE wo.work_order_id=?",
                    (work_order_id,),
                ).fetchone()
                if row is None or row["packet_sha256"] != work_order_sha256:
                    raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
                try:
                    dispatch_packet = json.loads(row["dispatch_packet"])
                except (TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise TaskNotReadyError(
                        "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE"
                    ) from exc
                expected_dispatch_packet = {
                    "schema": "x9-loop-work-order-dispatch-v1",
                    "task_id": row["task_id"],
                    "work_order_path": row["packet_path"],
                    "work_order_sha256": work_order_sha256,
                }
                if (
                    row["target_id"] != row["worker_id"]
                    or row["dispatch_packet_sha256"] != work_order_sha256
                    or dispatch_packet != expected_dispatch_packet
                    or _json(dispatch_packet) != row["dispatch_packet"]
                ):
                    raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
                terminal = (
                    row["task_status"],
                    row["order_status"],
                    row["dispatch_status"],
                ) == ("SUPERSEDED", "SUPERSEDED", "SUPERSEDED")
                dispatch_count = connection.execute(
                    "SELECT COUNT(*) FROM dispatches WHERE task_id=?",
                    (row["task_id"],),
                ).fetchone()[0]
                side_effect_count = sum(
                    connection.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE task_id=?",
                        (row["task_id"],),
                    ).fetchone()[0]
                    for table in ("events", "inbox")
                ) + connection.execute(
                    "SELECT COUNT(*) FROM deliveries d JOIN dispatches x "
                    "ON x.dispatch_id=d.dispatch_id WHERE x.task_id=?",
                    (row["task_id"],),
                ).fetchone()[0]
                call_count = sum(
                    connection.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE work_order_id=?",
                        (work_order_id,),
                    ).fetchone()[0]
                    for table in ("call_receipts", "call_reservations")
                )
                if (
                    dispatch_count != 1
                    or side_effect_count != 0
                    or call_count != 0
                ):
                    raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
                if terminal:
                    if row["outbox_payload"] is not None:
                        raise TaskNotReadyError(
                            "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE"
                        )
                    return row
                try:
                    outbox_action = json.loads(row["outbox_payload"])
                except (
                    TypeError,
                    ValueError,
                    json.JSONDecodeError,
                ) as exc:
                    raise TaskNotReadyError(
                        "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE"
                    ) from exc
                expected_action = {
                    "action": "SEND_WORK_ORDER",
                    "dispatch_id": row["dispatch_id"],
                    "target_actor_id": row["worker_id"],
                    "target_role": "WORKER",
                    "task_id": row["task_id"],
                    "work_order_id": row["work_order_id"],
                    "work_order_path": row["packet_path"],
                    "work_order_sha256": work_order_sha256,
                }
                if (
                    not all(
                        outbox_action.get(field) == value
                        for field, value in expected_action.items()
                    )
                    or contract.canonical_json_bytes(outbox_action).decode(
                        "utf-8"
                    ).rstrip("\n") != row["outbox_payload"]
                ):
                    raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
                return row

            connection = self._connect()
            try:
                row = admission(connection)
            finally:
                connection.close()
            receipt_path = (
                self.root / "runtime" / "pre-dispatch-recoveries"
                / f"{work_order_id}.json"
            )
            if (
                row["task_status"], row["order_status"], row["dispatch_status"]
            ) == ("SUPERSEDED", "SUPERSEDED", "SUPERSEDED"):
                try:
                    receipt_raw = receipt_path.read_bytes()
                    receipt = json.loads(receipt_raw)
                    if contract.canonical_json_bytes(receipt) != receipt_raw:
                        raise ValueError("noncanonical receipt")
                    expected = {
                        "dispatch_id": row["dispatch_id"],
                        "dispatch_packet_sha256": row["dispatch_packet_sha256"],
                        "reason": "WORK_ORDER_DRIFT:worker_result_contract",
                        "schema": "x9-loop-pre-dispatch-worker-result-contract-recovery-v1",
                        "task_id": row["task_id"],
                        "work_order_id": work_order_id,
                        "work_order_sha256": work_order_sha256,
                    }
                    if (
                        not all(
                            receipt.get(key) == value
                            for key, value in expected.items()
                        )
                        or re.fullmatch(
                            r"[0-9a-f]{64}",
                            receipt.get("outbox_action_sha256", ""),
                        ) is None
                    ):
                        raise ValueError("receipt identity")
                except (
                    OSError,
                    TypeError,
                    ValueError,
                    json.JSONDecodeError,
                ) as exc:
                    raise TaskNotReadyError(
                        "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE"
                    ) from exc
                receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()
                expected_note = (
                    f"work_order_sha256={work_order_sha256};"
                    f"recovery_receipt_sha256={receipt_sha256}"
                )
                connection = self._connect()
                try:
                    gate = connection.execute(
                        "SELECT status,note FROM gates WHERE task_id=? AND name=?",
                        (
                            row["task_id"],
                            "lifecycle:pre-dispatch-worker-result-contract-drift",
                        ),
                    ).fetchone()
                finally:
                    connection.close()
                if (
                    gate is not None
                    and gate["status"] == "PASS"
                    and gate["note"] == expected_note
                ):
                    return {
                        "status": "ALREADY_RECOVERED",
                        "task_id": row["task_id"],
                        "work_order_id": work_order_id,
                    }
                raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
            receipt = {
                "dispatch_id": row["dispatch_id"],
                "dispatch_packet_sha256": row["dispatch_packet_sha256"],
                "outbox_action_sha256": hashlib.sha256(
                    row["outbox_payload"].encode("utf-8")
                ).hexdigest(),
                "reason": "WORK_ORDER_DRIFT:worker_result_contract",
                "schema": "x9-loop-pre-dispatch-worker-result-contract-recovery-v1",
                "task_id": row["task_id"],
                "work_order_id": work_order_id,
                "work_order_sha256": work_order_sha256,
            }
            receipt_raw = contract.canonical_json_bytes(receipt)
            receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()
            expected_note = (
                f"work_order_sha256={work_order_sha256};"
                f"recovery_receipt_sha256={receipt_sha256}"
            )
            if (
                row["task_status"], row["order_status"], row["dispatch_status"]
            ) != ("REGISTERED", "CREATED", "PREPARED"):
                raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
            try:
                action_raw = self.action_path.read_bytes()
                action = json.loads(action_raw)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise TaskNotReadyError(
                    "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE"
                ) from exc
            if (
                contract.canonical_json_bytes(action) != action_raw
                or action.get("action") != "NOOP"
            ):
                raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
            receipt_wrote = False

            def recovery_committed() -> bool:
                connection = self._connect()
                try:
                    current = connection.execute(
                        "SELECT t.status AS task_status,wo.status AS order_status,"
                        "d.status AS dispatch_status "
                        "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id "
                        "WHERE wo.work_order_id=?",
                        (work_order_id,),
                    ).fetchone()
                    gate = connection.execute(
                        "SELECT status,note FROM gates WHERE task_id=? AND name=?",
                        (
                            row["task_id"],
                            "lifecycle:pre-dispatch-worker-result-contract-drift",
                        ),
                    ).fetchone()
                    outbox = connection.execute(
                        "SELECT 1 FROM outbox WHERE dispatch_id=?",
                        (row["dispatch_id"],),
                    ).fetchone()
                finally:
                    connection.close()
                return (
                    current is not None
                    and (
                        current["task_status"],
                        current["order_status"],
                        current["dispatch_status"],
                    ) == ("SUPERSEDED", "SUPERSEDED", "SUPERSEDED")
                    and outbox is None
                    and gate is not None
                    and gate["status"] == "PASS"
                    and gate["note"] == expected_note
                )

            def operation(connection: sqlite3.Connection) -> dict[str, Any]:
                nonlocal receipt_wrote
                current = admission(connection)
                if (
                    current["task_status"], current["order_status"],
                    current["dispatch_status"]
                ) != ("REGISTERED", "CREATED", "PREPARED"):
                    raise TaskNotReadyError("PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE")
                connection.execute(
                    "UPDATE tasks SET status='SUPERSEDED' WHERE task_id=?",
                    (current["task_id"],),
                )
                connection.execute(
                    "UPDATE work_orders SET status='SUPERSEDED' WHERE work_order_id=?",
                    (work_order_id,),
                )
                connection.execute(
                    "UPDATE dispatches SET status='SUPERSEDED' WHERE dispatch_id=?",
                    (current["dispatch_id"],),
                )
                connection.execute(
                    "DE" + "LETE FROM outbox WHERE dispatch_id=?",
                    (current["dispatch_id"],),
                )
                connection.execute(
                    "INSERT INTO gates(task_id,name,status,note) VALUES(?,?,?,?) "
                    "ON CONFLICT(task_id,name) DO UPDATE SET status=excluded.status,note=excluded.note",
                    (
                        current["task_id"],
                        "lifecycle:pre-dispatch-worker-result-contract-drift",
                        "PASS",
                        expected_note,
                    ),
                )
                receipt_wrote = self._write_state_once(
                    receipt_path, receipt_raw, "LOOP_INCIDENT.json"
                )
                return {
                    "status": "RECOVERED",
                    "task_id": current["task_id"],
                    "work_order_id": work_order_id,
                    "recovery_receipt_path": str(
                        receipt_path.relative_to(self.repo)
                    ).replace("\\", "/"),
                    "recovery_receipt_sha256": receipt_sha256,
                }

            try:
                result = self._mutate_locked(operation)
            except Exception:
                if receipt_wrote and not recovery_committed():
                    target = self._safe_state_path(receipt_path)
                    if target.is_file() and target.read_bytes() == receipt_raw:
                        target.unlink()
                raise
        self._write_action(self._current_action())
        self._write_views()
        return result

    def _write_views(self) -> None:
        connection = self._connect()
        try:
            tasks = [dict(row) for row in connection.execute("SELECT task_id,worker_id,worktree_id,status FROM tasks ORDER BY task_id LIMIT 50")]
            dispatches = [dict(row) for row in connection.execute("SELECT dispatch_id,task_id,target_id,status FROM dispatches WHERE status IN ('PREPARED','DISPATCHED') ORDER BY dispatch_id LIMIT 30")]
            gates = [dict(row) for row in connection.execute("SELECT task_id,name,status FROM gates ORDER BY task_id,name LIMIT 30")]
        finally:
            connection.close()
        status_lines = ["# X9 Loop Lite Status (Generated)", "", "Generated convenience view; not parser authority.", "", "## Tasks"]
        status_lines.extend(f"- {row['task_id']}: {row['status']} worker={row['worker_id']} worktree={row['worktree_id']}" for row in tasks)
        handoff_lines = ["# X9 Loop Lite Handoffs (Generated)", "", "Generated convenience view; not parser authority.", "", "## Active Dispatches"]
        handoff_lines.extend(f"- {row['dispatch_id']}: task={row['task_id']} target={row['target_id']} status={row['status']}" for row in dispatches)
        handoff_lines.append("## Gates")
        handoff_lines.extend(f"- {row['task_id']}/{row['name']}: {row['status']}" for row in gates)
        for path, lines in ((self.root / "runtime" / "STATUS.md", status_lines), (self.root / "runtime" / "HANDOFFS.md", handoff_lines)):
            content = "\n".join(lines[:120]) + "\n"
            if len(content.encode("utf-8")) >= 12288:
                content = "\n".join(lines[:20]) + "\n"
            self._atomic_state_write(path, content.encode("utf-8"))

    def _doctor_v7_integrity(
        self, connection: sqlite3.Connection
    ) -> dict[str, list[str]]:
        contract = _load_v7_contract()
        issues = {
            "work_orders": [],
            "terminal_history_compatibility": [],
            "dispatch_identity": [],
            "call_ledger": [],
        }
        work_orders = [
            dict(row)
            for row in connection.execute(
                "SELECT wo.*,t.worker_id AS task_worker_id "
                "FROM work_orders wo JOIN tasks t ON t.task_id=wo.task_id "
                "ORDER BY wo.work_order_id"
            )
        ]
        by_task = {row["task_id"]: row for row in work_orders}
        for row in work_orders:
            try:
                if row["worker_id"] != row["task_worker_id"]:
                    raise IdentityError("WORK_ORDER_WORKER_MISMATCH")
                _order, compatibility = self._verify_work_order(
                    row["work_order_id"],
                    allow_terminal_historical_contract=True,
                )
                if compatibility is not None:
                    issues["terminal_history_compatibility"].append(
                        compatibility
                    )
            except (LoopError, OSError, ValueError) as exc:
                issues["work_orders"].append(type(exc).__name__)

        action_keys = {
            "action", "action_id", "attempt", "dispatch_id",
            "must_record_transport", "schema", "target_actor_id",
            "target_role", "task_id", "project_profile_id",
            "work_order_id", "work_order_path", "work_order_sha256",
        }
        profile_row = connection.execute(
            "SELECT value FROM meta WHERE key='project_profile_id'"
        ).fetchone()
        project_profile_id = profile_row[0] if profile_row else None
        for dispatch in connection.execute(
            "SELECT * FROM dispatches ORDER BY dispatch_id"
        ):
            try:
                packet = json.loads(dispatch["packet"])
            except (TypeError, json.JSONDecodeError):
                issues["dispatch_identity"].append("DISPATCH_PACKET_INVALID")
                continue
            if not isinstance(packet, dict) or packet.get("schema") != "x9-loop-work-order-dispatch-v1":
                continue
            order = by_task.get(dispatch["task_id"])
            sender = connection.execute(
                "SELECT role FROM actors WHERE actor_id=?",
                (dispatch["sender_id"],),
            ).fetchone()
            target = connection.execute(
                "SELECT role FROM actors WHERE actor_id=?",
                (dispatch["target_id"],),
            ).fetchone()
            valid = (
                set(packet)
                == {
                    "schema", "task_id", "work_order_path",
                    "work_order_sha256",
                }
                and order is not None
                and packet["task_id"] == dispatch["task_id"]
                and packet["work_order_path"] == order["packet_path"]
                and packet["work_order_sha256"] == order["packet_sha256"]
                and dispatch["packet_sha256"] == order["packet_sha256"]
                and dispatch["target_id"] == order["worker_id"]
                and packet["task_id"] == order["task_id"]
                and order["worker_id"] == order["task_worker_id"]
                and sender is not None
                and sender["role"] in {"LINX", "LINKER"}
                and target is not None
                and target["role"] == "WORKER"
            )
            outbox = connection.execute(
                "SELECT payload FROM outbox WHERE dispatch_id=?",
                (dispatch["dispatch_id"],),
            ).fetchone()
            if dispatch["status"] == "PREPARED" and not outbox:
                valid = False
            if outbox:
                try:
                    action = json.loads(outbox["payload"])
                except (TypeError, json.JSONDecodeError):
                    valid = False
                    action = {}
                valid = valid and (
                    isinstance(action, dict)
                    and set(action) == action_keys
                    and action.get("schema") == "x9-loop-action-v2"
                    and action.get("action") == "SEND_WORK_ORDER"
                    and isinstance(action.get("action_id"), str)
                    and re.fullmatch(
                        r"act-[0-9a-f-]{36}", action["action_id"]
                    )
                    is not None
                    and action.get("attempt") == 1
                    and action.get("dispatch_id") == dispatch["dispatch_id"]
                    and action.get("must_record_transport") is True
                    and project_profile_id is not None
                    and action.get("project_profile_id") == project_profile_id
                    and action.get("target_actor_id") == order["worker_id"]
                    and action.get("target_role") == "WORKER"
                    and action.get("task_id") == order["task_id"]
                    and action.get("work_order_id") == order["work_order_id"]
                    and action.get("work_order_path") == order["packet_path"]
                    and action.get("work_order_sha256")
                    == order["packet_sha256"]
                )
            if not valid:
                issues["dispatch_identity"].append(
                    "V7_DISPATCH_IDENTITY_INVALID"
                )

        for order in work_orders:
            work_order_id = order["work_order_id"]
            evidence_dir = (
                self.root / "runtime" / "call-receipts" / work_order_id
            )
            try:
                evidence_by_sequence: dict[
                    int, tuple[str, dict[str, Any]]
                ] = {}
                evidence_call_ids: set[str] = set()
                self._safe_state_path(evidence_dir)
                candidates = (
                    sorted(evidence_dir.glob("*.json"))
                    if evidence_dir.is_dir()
                    else []
                )
                for path in candidates:
                    self._safe_state_path(path)
                    raw = path.read_bytes()
                    digest = hashlib.sha256(raw).hexdigest()
                    validated = contract.validate_call_receipt(
                        json.loads(raw), order["packet_sha256"]
                    )
                    if (
                        path.stem != digest
                        or contract.canonical_json_bytes(validated) != raw
                        or validated["call_id"] in evidence_call_ids
                        or validated["sequence"] in evidence_by_sequence
                    ):
                        raise StateNotDurableError("CALL_EVIDENCE_INVALID")
                    evidence_call_ids.add(validated["call_id"])
                    evidence_by_sequence[validated["sequence"]] = (
                        digest,
                        validated,
                    )

                receipt_rows = list(
                    connection.execute(
                        "SELECT * FROM call_receipts WHERE work_order_id=? "
                        "ORDER BY sequence",
                        (work_order_id,),
                    )
                )
                receipts: list[dict[str, Any]] = []
                ordered_digests: list[str] = []
                tokens = 0
                unknown = 0
                for expected_sequence, row in enumerate(
                    receipt_rows, start=1
                ):
                    raw = (row["receipt"] + "\n").encode("utf-8")
                    validated = contract.validate_call_receipt(
                        json.loads(raw), order["packet_sha256"]
                    )
                    digest = hashlib.sha256(raw).hexdigest()
                    evidence = evidence_by_sequence.get(expected_sequence)
                    if (
                        row["sequence"] != expected_sequence
                        or validated["sequence"] != expected_sequence
                        or validated["call_id"] != row["call_id"]
                        or digest != row["receipt_sha256"]
                        or contract.canonical_json_bytes(validated) != raw
                        or evidence is None
                        or evidence[0] != digest
                        or evidence[1] != validated
                    ):
                        raise StateNotDurableError("CALL_RECEIPT_INVALID")
                    receipts.append(validated)
                    ordered_digests.append(digest)
                    if validated["token_usage"] == "Unknown":
                        unknown = 1
                    else:
                        tokens += validated["token_usage"]
                if len(receipts) != len(evidence_by_sequence):
                    raise StateNotDurableError("CALL_EVIDENCE_INVALID")

                reservation_rows = [
                    dict(row)
                    for row in connection.execute(
                        "SELECT * FROM call_reservations "
                        "WHERE work_order_id=? ORDER BY sequence",
                        (work_order_id,),
                    )
                ]
                if (
                    [row["sequence"] for row in reservation_rows]
                    != list(range(1, len(reservation_rows) + 1))
                    or any(
                        row["status"] not in {"RESERVED", "RECORDED"}
                        or not isinstance(row["call_id"], str)
                        or re.fullmatch(
                            r"[A-Za-z0-9._:-]{1,128}", row["call_id"]
                        )
                        is None
                        or isinstance(row["attempt"], bool)
                        or not isinstance(row["attempt"], int)
                        or row["attempt"] < 0
                        or re.fullmatch(
                            r"[0-9a-f]{64}", row["prompt_prefix_sha256"]
                        )
                        is None
                        or re.fullmatch(
                            r"[0-9a-f]{64}", row["tool_schema_sha256"]
                        )
                        is None
                        for row in reservation_rows
                    )
                ):
                    raise StateNotDurableError("CALL_LEDGER_INVALID")
                recorded = {
                    row["call_id"]: row
                    for row in reservation_rows
                    if row["status"] == "RECORDED"
                }
                reserved = [
                    row
                    for row in reservation_rows
                    if row["status"] == "RESERVED"
                ]
                for reservation in reserved:
                    issues["call_ledger"].append(
                        "CALL_RESERVATION_IN_FLIGHT:"
                        f"{work_order_id}:{reservation['call_id']}"
                    )
                receipt_by_id = {
                    receipt["call_id"]: receipt for receipt in receipts
                }
                if (
                    len(reserved) > 1
                    or set(recorded) != set(receipt_by_id)
                    or len(reservation_rows)
                    != len(receipts) + len(reserved)
                    or (
                        reserved
                        and reserved[0]["sequence"] != len(receipts) + 1
                    )
                    or any(
                        receipt["sequence"]
                        != recorded[call_id]["sequence"]
                        or receipt["action_class"]
                        != recorded[call_id]["action_class"]
                        or receipt["attempt"]
                        != recorded[call_id]["attempt"]
                        or receipt[
                            "pre_compaction_prompt_prefix_sha256"
                        ]
                        != recorded[call_id]["prompt_prefix_sha256"]
                        or receipt[
                            "pre_compaction_tool_schema_sha256"
                        ]
                        != recorded[call_id]["tool_schema_sha256"]
                        for call_id, receipt in receipt_by_id.items()
                    )
                ):
                    raise StateNotDurableError("CALL_LEDGER_INVALID")

                metrics = {
                    row["key"]: row["value"]
                    for row in connection.execute(
                        "SELECT key,value FROM metrics WHERE key LIKE ?",
                        (f"call-%:{work_order_id}",),
                    )
                }
                allowed_metric_keys = {
                    f"{prefix}:{work_order_id}"
                    for prefix in (
                        "call-count",
                        "call-latest",
                        "call-root",
                        "call-tokens",
                        "call-unknown",
                    )
                }
                count = int(
                    metrics.get(f"call-count:{work_order_id}", "0")
                )
                stored_tokens = int(
                    metrics.get(f"call-tokens:{work_order_id}", "0")
                )
                stored_unknown = int(
                    metrics.get(f"call-unknown:{work_order_id}", "0")
                )
                root = metrics.get(
                    f"call-root:{work_order_id}", _sha([])
                )
                latest_raw = metrics.get(
                    f"call-latest:{work_order_id}"
                )
                expected_latest = _json(receipts[-1]) if receipts else None
                if (
                    set(metrics) - allowed_metric_keys
                    or count != len(receipts)
                    or stored_tokens != tokens
                    or stored_unknown != unknown
                    or root != _sha(ordered_digests)
                    or latest_raw != expected_latest
                ):
                    raise StateNotDurableError("CALL_LEDGER_INVALID")
            except (
                LoopError,
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
                contract.ContractError,
            ):
                issues["call_ledger"].append("CALL_LEDGER_INVALID")
        return issues

    def _inventory_codex_recurring_jobs(
        self, project_profile_id: str | None = None,
    ) -> tuple[list[dict[str, str]], str]:
        contract = _load_v7_contract()
        jobs: list[dict[str, str]] = []
        try:
            codex_home = Path(
                os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
            )
            automations = codex_home / "automations"
            if not automations.is_dir() or self._is_reparse(automations):
                return [], "UNKNOWN"
            for entry in sorted(
                automations.iterdir(), key=lambda path: path.name.encode("utf-8")
            ):
                if (
                    entry.name == ".run-jitter-salt"
                    and entry.is_file()
                    and not self._is_reparse(entry)
                ):
                    continue
                if not entry.is_dir() or self._is_reparse(entry):
                    raise ValueError("unexpected Codex automation entry")
                manifest = entry / "automation.toml"
                if not manifest.is_file() or self._is_reparse(manifest):
                    raise ValueError("Codex automation manifest unavailable")
                data = tomllib.loads(manifest.read_text(encoding="utf-8"))
                status = data.get("status")
                if status not in {"ACTIVE", "PAUSED"}:
                    raise ValueError("Codex automation status invalid")
                if status == "PAUSED":
                    continue
                raw_id = data.get("id", entry.name)
                prompt = data.get("prompt")
                rrule = data.get("rrule")
                cwds = data.get("cwds", [])
                if (
                    not isinstance(raw_id, str)
                    or not raw_id
                    or not isinstance(prompt, str)
                    or not prompt
                    or not isinstance(rrule, str)
                    or not rrule
                    or not isinstance(cwds, list)
                    or any(not isinstance(item, str) for item in cwds)
                ):
                    raise ValueError("Codex automation identity invalid")
                current_project = False
                for cwd in cwds:
                    try:
                        Path(cwd).resolve(strict=False).relative_to(self.repo)
                        current_project = True
                    except (OSError, RuntimeError, ValueError):
                        continue
                if project_profile_id and project_profile_id in prompt:
                    current_project = True
                jobs.append(
                    {
                        "provider": "codex",
                        "job_id": hashlib.sha256(
                            raw_id.encode("utf-8")
                        ).hexdigest(),
                        "command_hash": contract.sha256_bytes(
                            contract.canonical_json_bytes(
                                {"cwds": cwds, "prompt": prompt}
                            )
                        ),
                        "schedule_hash": contract.sha256_bytes(
                            rrule.strip().encode("utf-8")
                        ),
                        "relevance": (
                            "CURRENT_PROJECT_MONITOR"
                            if current_project
                            else "OTHER_PROJECT_JOB"
                        ),
                    }
                )
        except (
            OSError, RuntimeError, UnicodeDecodeError, ValueError,
            tomllib.TOMLDecodeError,
        ):
            return [], "UNKNOWN"
        return jobs, "AVAILABLE"

    def _inventory_windows_recurring_jobs(
        self, project_profile_id: str | None = None,
    ) -> tuple[list[dict[str, str]], str | None]:
        if os.name != "nt":
            return [], None
        script = r"""
$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
function Get-X9Sha256([string] $Value) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString(
            $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value))
        )).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}
$projectRoot = ([string] $env:X9_PROJECT_ROOT).TrimEnd('\').ToLowerInvariant()
$profileId = ([string] $env:X9_PROJECT_PROFILE_ID).ToLowerInvariant()
$rows = @()
foreach ($task in Get-ScheduledTask) {
    if ($task.State -eq 'Disabled') {
        continue
    }
    $xml = [xml](Export-ScheduledTask -TaskName $task.TaskName -TaskPath $task.TaskPath)
    $recurring = $false
    foreach ($trigger in @($xml.Task.Triggers.ChildNodes)) {
        if ($trigger.LocalName -in @(
            'BootTrigger', 'CalendarTrigger', 'EventTrigger', 'IdleTrigger',
            'LogonTrigger', 'SessionStateChangeTrigger'
        )) {
            $recurring = $true
        }
        elseif ($null -ne $trigger.Repetition -and
                -not [string]::IsNullOrWhiteSpace([string] $trigger.Repetition.Interval)) {
            $recurring = $true
        }
    }
    if (-not $recurring) {
        continue
    }
    $rawId = [string] $task.TaskPath + [string] $task.TaskName
    $classificationText = ($rawId + ' ' + [string] $xml.Task.Actions.OuterXml).Replace('/', '\').ToLowerInvariant()
    $projectBound = -not [string]::IsNullOrWhiteSpace($projectRoot) -and
        ($classificationText.Contains($projectRoot + '\') -or $classificationText.Contains('"' + $projectRoot + '"'))
    $profileBound = -not [string]::IsNullOrWhiteSpace($profileId) -and $classificationText.Contains($profileId)
    $relevance = if ($projectBound -or $profileBound) { 'CURRENT_PROJECT_MONITOR' } else { 'UNRELATED_OS_JOB' }
    $rows += [pscustomobject]@{
        provider = 'windows-task-scheduler'
        job_id = Get-X9Sha256 $rawId
        command_hash = Get-X9Sha256 ([string] $xml.Task.Actions.OuterXml)
        schedule_hash = Get-X9Sha256 ([string] $xml.Task.Triggers.OuterXml)
        relevance = $relevance
    }
}
ConvertTo-Json -InputObject @($rows) -Compress
"""
        try:
            environment = os.environ.copy()
            environment["X9_PROJECT_ROOT"] = str(self.repo.resolve(strict=True))
            environment["X9_PROJECT_PROFILE_ID"] = project_profile_id or ""
            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    script,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                check=False,
                timeout=30,
                env=environment,
            )
            if completed.returncode:
                return [], "UNKNOWN"
            raw = completed.stdout.strip()
            parsed = [] if raw in {"", "null"} else json.loads(raw)
            if not isinstance(parsed, list):
                raise ValueError("scheduled task inventory is not a list")
            return [dict(row) for row in parsed], "AVAILABLE"
        except (
            OSError, subprocess.SubprocessError, UnicodeDecodeError,
            json.JSONDecodeError, TypeError, ValueError,
        ):
            return [], "UNKNOWN"

    def _inventory_scheduled_jobs(
        self, project_profile_id: str | None = None,
    ) -> dict[str, Any]:
        jobs, codex_status = self._inventory_codex_recurring_jobs(project_profile_id)
        providers = {"codex": codex_status}
        windows_jobs, windows_status = self._inventory_windows_recurring_jobs(
            project_profile_id
        )
        if windows_status is not None:
            providers["windows-task-scheduler"] = windows_status
            jobs.extend(windows_jobs)
        jobs.sort(key=lambda row: (row["provider"], row["job_id"]))
        _load_v7_contract().compare_scheduled_jobs(
            {
                "jobs": [],
                "monitor_mode": "DISABLED",
                "schema": "x9-loop-approved-jobs-v1",
            },
            jobs,
            providers,
        )
        return {"jobs": jobs, "providers": providers}

    def doctor_v7(self) -> dict[str, Any]:
        checks: dict[str, Any] = {
            "integrity_check": "FAIL",
            "foreign_key_check": "FAIL",
            "schema_shape": "FAIL",
            "snapshot": "FAIL",
            "action": "FAIL",
            "errors": [],
        }
        connection: sqlite3.Connection | None = None
        try:
            self._safe_state_path(self.db_path)
            connection = sqlite3.connect(
                f"file:{self.db_path.as_posix()}?mode=ro", uri=True
            )
            connection.row_factory = sqlite3.Row
            self._validate_v2_schema_shape(connection)
            checks["schema_shape"] = "PASS"
            checks["integrity_check"] = (
                "PASS"
                if connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]
                == "ok"
                else "FAIL"
            )
            checks["foreign_key_check"] = (
                "PASS"
                if not connection.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
                else "FAIL"
            )
            generation_row = connection.execute(
                "SELECT value FROM meta WHERE key='generation'"
            ).fetchone()
            generation = int(generation_row[0]) if generation_row else None
            self._safe_state_path(self.snapshot_path)
            snapshot_raw = self.snapshot_path.read_bytes()
            snapshot = json.loads(snapshot_raw)
            checks["snapshot"] = (
                "PASS"
                if len(snapshot_raw) <= 8192
                and _load_v7_contract().canonical_json_bytes(snapshot)
                == snapshot_raw
                and snapshot.get("schema") in {SCHEMA_V2, SCHEMA}
                and snapshot.get("generation") == generation == 7
                and self._v7_database_matches_snapshot(
                    connection, snapshot_raw
                )
                else "FAIL"
            )
            self._safe_state_path(self.action_path)
            action_raw = self.action_path.read_bytes()
            action = json.loads(action_raw)
            contract = _load_v7_contract()
            checks["action"] = (
                "PASS"
                if len(action_raw) <= 4096
                and contract.canonical_json_bytes(action) == action_raw
                and action_raw
                == contract.canonical_json_bytes(self._current_action())
                else "FAIL"
            )
        except (
            LoopError,
            OSError,
            sqlite3.Error,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            checks["errors"].append(type(exc).__name__)
        finally:
            if connection is not None:
                connection.close()
        healthy = (
            checks["integrity_check"] == "PASS"
            and checks["foreign_key_check"] == "PASS"
            and checks["schema_shape"] == "PASS"
            and checks["snapshot"] == "PASS"
            and checks["action"] == "PASS"
            and not checks["errors"]
        )
        return {
            "status": "PASS" if healthy else "FAIL",
            "durable": checks["snapshot"] == "PASS",
            "checks": checks,
            "metrics": {"token_telemetry": "Unknown"},
        }
    def doctor(self) -> dict[str, Any]:
        checks: dict[str, Any] = {
            "integrity_check": "FAIL",
            "foreign_key_check": "FAIL",
            "schema_shape": "FAIL",
            "snapshot": "FAIL",
            "action": "ABSENT",
            "worktrees": [],
            "historical_missing": [],
            "receipts": [],
            "recovery": [],
            "conflicts": {"claims": [], "resources": []},
            "work_orders": [],
            "terminal_history_compatibility": [],
            "dispatch_identity": [],
            "call_ledger": [],
            "jobs": {
                "activation_allowed": True,
                "core_loop_ready": True,
                "external_wake_ready": None,
                "error": "JOB_INVENTORY_UNAVAILABLE",
                "monitor_mode": "DISABLED",
            },
            "errors": [],
        }
        if self.migration_state_path.exists():
            checks["errors"].append("MIGRATION_RECOVERY_REQUIRED")
        generation = None
        expected_snapshot_raw: bytes | None = None
        historical_ids: set[str] = set()
        connection: sqlite3.Connection | None = None
        try:
            self._safe_state_path(self.db_path)
            connection = sqlite3.connect(f"file:{self.db_path.as_posix()}?mode=ro", uri=True)
            connection.row_factory = sqlite3.Row
            try:
                self._validate_v3_schema_shape(connection)
                checks["schema_shape"] = "PASS"
            except StateNotDurableError:
                checks["errors"].append("V2_DATABASE_INVALID")
            checks["integrity_check"] = (
                "PASS" if connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok" else "FAIL"
            )
            checks["foreign_key_check"] = (
                "PASS" if not connection.execute("PRAGMA foreign_key_check").fetchall() else "FAIL"
            )
            row = connection.execute("SELECT value FROM meta WHERE key='generation'").fetchone()
            generation = int(row[0]) if row else None
            tables = {
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            classifications = {}
            if "worktree_classifications" in tables:
                classifications = {
                    row["worktree_id"]: dict(row)
                    for row in connection.execute("SELECT * FROM worktree_classifications")
                }
            worktrees = [
                dict(row)
                for row in connection.execute("SELECT worktree_id,path FROM worktrees ORDER BY worktree_id")
            ]
            for worktree in worktrees:
                worktree_id = worktree["worktree_id"]
                root = Path(worktree["path"])
                if not root.is_dir():
                    classification = classifications.get(worktree_id, {})
                    active_tasks = connection.execute(
                        "SELECT COUNT(*) FROM tasks WHERE worktree_id=? AND status NOT IN ('COMPLETE','SUPERSEDED')",
                        (worktree_id,),
                    ).fetchone()[0]
                    active_dispatches = connection.execute(
                        "SELECT COUNT(*) FROM dispatches d JOIN tasks t ON t.task_id=d.task_id "
                        "WHERE t.worktree_id=? AND d.status IN ('PREPARED','DISPATCHED')",
                        (worktree_id,),
                    ).fetchone()[0]
                    active_claims = connection.execute(
                        "SELECT COUNT(*) FROM claims c JOIN tasks t ON t.task_id=c.task_id "
                        "WHERE t.worktree_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
                        (worktree_id,),
                    ).fetchone()[0]
                    active_resources = connection.execute(
                        "SELECT COUNT(*) FROM resources r JOIN tasks t ON t.task_id=r.task_id "
                        "WHERE t.worktree_id=? AND t.status NOT IN ('COMPLETE','SUPERSEDED')",
                        (worktree_id,),
                    ).fetchone()[0]
                    historical = (
                        worktree_id == "core-legacy"
                        and classification.get("classification") == "HISTORICAL_MISSING"
                        and isinstance(classification.get("owner_decision_sha256"), str)
                        and re.fullmatch(r"[0-9a-f]{64}", classification["owner_decision_sha256"])
                        and not any((active_tasks, active_dispatches, active_claims, active_resources))
                    )
                    if historical:
                        historical_ids.add(worktree_id)
                        checks["historical_missing"].append(worktree_id)
                    else:
                        checks["worktrees"].append(f"WORKTREE_MISSING:{worktree_id}")
                    continue
                try:
                    self._historical_receipt_paths(root, connection)
                    self._validated_receipt_entries(root, connection)
                except StateNotDurableError:
                    checks["receipts"].append(f"RECEIPT_SET_MISMATCH:{worktree_id}")
            complete = [
                dict(row)
                for row in connection.execute(
                    "SELECT t.task_id,t.worker_id,w.path FROM tasks t JOIN worktrees w ON w.worktree_id=t.worktree_id "
                    "WHERE t.status='COMPLETE'"
                )
            ]
            checks["receipts"].extend(
                row["task_id"]
                for row in complete
                if Path(row["path"]).is_dir()
                and not any(
                    (Path(row["path"]) / ".devad" / "workers" / row["worker_id"] / "receipts").glob("*.json")
                )
            )
            active_claims = [
                dict(row)
                for row in connection.execute(
                    "SELECT c.task_id,c.path,c.kind FROM claims c JOIN tasks t ON t.task_id=c.task_id "
                    "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED')"
                )
            ]
            for index, left in enumerate(active_claims):
                for right in active_claims[index + 1:]:
                    if left["task_id"] != right["task_id"] and self._overlap(
                        left["path"], left["kind"], right["path"], right["kind"]
                    ):
                        checks["conflicts"]["claims"].append(f"{left['task_id']}:{right['task_id']}")
            for row in connection.execute(
                "SELECT r.resource,group_concat(r.task_id) AS tasks FROM resources r "
                "JOIN tasks t ON t.task_id=r.task_id WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') "
                "GROUP BY r.resource HAVING COUNT(*) > 1"
            ):
                checks["conflicts"]["resources"].append(f"{row['resource']}:{row['tasks']}")
            v7_integrity = self._doctor_v7_integrity(connection)
            checks.update(v7_integrity)
            self._safe_state_path(self.snapshot_path)
            current_snapshot_raw = self.snapshot_path.read_bytes()
            current_snapshot = json.loads(current_snapshot_raw)
            if current_snapshot.get("schema") == SCHEMA_V2:
                expected_snapshot_raw = _load_v7_contract().canonical_json_bytes(
                    self._snapshot_v2_data(connection)
                )
            elif current_snapshot.get("schema") == SCHEMA:
                expected_snapshot_raw = self._snapshot_bundle(
                    connection, current_snapshot_raw=current_snapshot_raw
                )["root_raw"]
        except (LoopError, OSError, sqlite3.Error, ValueError) as exc:
            checks["errors"].append(type(exc).__name__)
        finally:
            if connection is not None:
                connection.close()

        try:
            self._safe_state_path(self.snapshot_path)
            snapshot_raw = self.snapshot_path.read_bytes()
            snapshot = json.loads(snapshot_raw)
            snapshot_state = self._decode_snapshot(snapshot_raw)
            checks["snapshot"] = (
                "PASS"
                if expected_snapshot_raw is not None
                and len(snapshot_raw) <= 8192
                and snapshot_raw == expected_snapshot_raw
                and snapshot.get("schema") in {SCHEMA_V2, SCHEMA}
                and snapshot.get("generation") == generation
                else "FAIL"
            )
            recovery_worktrees = snapshot_state["recovery_worktrees"]
            issues = self._recovery_evidence(
                recovery_worktrees, strict=False
            )["issues"]
            checks["recovery"] = [
                issue
                for issue in issues
                if not (
                    issue.startswith("WORKTREE_MISSING:")
                    and issue.split(":", 1)[1] in historical_ids
                )
            ]
        except (LoopError, OSError, json.JSONDecodeError, ValueError) as exc:
            checks["errors"].append(type(exc).__name__)

        try:
            self._safe_state_path(self.action_path)
            if not self.action_path.is_file():
                checks["action"] = "FAIL"
            else:
                contract = _load_v7_contract()
                actual_raw = self.action_path.read_bytes()
                action = json.loads(actual_raw)
                expected_action_raw = contract.canonical_json_bytes(
                    self._current_action()
                )
                checks["action"] = (
                    "PASS"
                    if len(actual_raw) <= 4096
                    and contract.canonical_json_bytes(action) == actual_raw
                    and actual_raw == expected_action_raw
                    else "FAIL"
                )
        except (LoopError, OSError, json.JSONDecodeError, ValueError) as exc:
            checks["action"] = "FAIL"
            checks["errors"].append(type(exc).__name__)
        try:
            self._safe_state_path(self.approved_jobs_path)
            approved_raw = self.approved_jobs_path.read_bytes()
            approved = json.loads(approved_raw)
            contract = _load_v7_contract()
            if contract.canonical_json_bytes(approved) != approved_raw:
                raise StateNotDurableError("APPROVED_JOBS_NONCANONICAL")
            profile_raw = self.project_profile_path.read_bytes()
            profile = json.loads(profile_raw)
            project_profile_id = profile["project_profile_id"]
            inventory = self._inventory_scheduled_jobs(project_profile_id)
            if not isinstance(inventory, Mapping) or set(inventory) != {"jobs", "providers"}:
                raise StateNotDurableError("JOB_INVENTORY_INVALID")
            checks["jobs"] = contract.compare_scheduled_jobs(
                approved,
                inventory["jobs"],
                inventory["providers"],
                project_profile_id=project_profile_id,
            )
        except (LoopError, OSError, json.JSONDecodeError, ValueError) as exc:
            requested_mode = (
                approved.get("monitor_mode")
                if isinstance(locals().get("approved"), Mapping)
                else "DISABLED"
            )
            if requested_mode not in {"DISABLED", "EXTERNAL"}:
                requested_mode = "DISABLED"
            checks["jobs"] = {
                "activation_allowed": True,
                "core_loop_ready": True,
                "external_wake_ready": (
                    False if requested_mode == "EXTERNAL" else None
                ),
                "error": type(exc).__name__,
                "monitor_mode": requested_mode,
            }

        durable = checks["snapshot"] == "PASS"
        healthy = (
            durable
            and checks["integrity_check"] == "PASS"
            and checks["foreign_key_check"] == "PASS"
            and checks["schema_shape"] == "PASS"
            and checks["action"] == "PASS"
            and checks["jobs"].get("core_loop_ready") is True
            and not checks["errors"]
            and not checks["worktrees"]
            and not checks["receipts"]
            and not checks["recovery"]
            and not checks["conflicts"]["claims"]
            and not checks["conflicts"]["resources"]
            and not checks["work_orders"]
            and not checks["dispatch_identity"]
            and not checks["call_ledger"]
        )
        return {
            "status": "PASS" if healthy else "FAIL",
            "durable": durable,
            "checks": checks,
            "metrics": {"token_telemetry": "Unknown"},
        }
    def _is_durable_read_only(self) -> bool:
        try:
            self._safe_state_path(self.db_path)
            self._safe_state_path(self.snapshot_path)
            raw = self.snapshot_path.read_bytes()
            connection = sqlite3.connect(
                f"file:{self.db_path.as_posix()}?mode=ro", uri=True
            )
            connection.row_factory = sqlite3.Row
            try:
                self._validate_v3_schema_shape(connection)
                return self._snapshot_matches_connection(connection, raw)
            finally:
                connection.close()
        except (
            LoopError,
            OSError,
            sqlite3.Error,
            json.JSONDecodeError,
            ValueError,
        ):
            return False

    def _pre_dispatch_recovery_rebuild_bundle(
        self, snapshot_raw: bytes
    ) -> dict[str, Any] | None:
        """Repair only the stale root left after this recovery commits."""
        contract = _load_v7_contract()
        receipt_root = self.root / "runtime" / "pre-dispatch-recoveries"
        try:
            self._safe_state_path(receipt_root, directory=True)
        except LoopError:
            return None
        if not receipt_root.is_dir() or not any(receipt_root.glob("*.json")):
            return None
        try:
            snapshot = self._decode_snapshot(snapshot_raw)
        except SnapshotExportError:
            return None
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT g.note,t.task_id,t.status AS task_status,"
                "wo.work_order_id,wo.packet_sha256,wo.status AS order_status,"
                "d.dispatch_id,d.packet_sha256 AS dispatch_packet_sha256,"
                "d.status AS dispatch_status "
                "FROM gates g JOIN tasks t ON t.task_id=g.task_id "
                "JOIN work_orders wo ON wo.task_id=t.task_id "
                "JOIN dispatches d ON d.task_id=t.task_id "
                "WHERE g.name=? AND g.status='PASS'",
                ("lifecycle:pre-dispatch-worker-result-contract-drift",),
            ).fetchall()
            generation = self._generation(connection)
            if len(rows) != 1:
                return None
            row = rows[0]
            outbox = connection.execute(
                "SELECT 1 FROM outbox WHERE dispatch_id=?",
                (row["dispatch_id"],),
            ).fetchone()
            if (
                (row["task_status"], row["order_status"], row["dispatch_status"])
                != ("SUPERSEDED", "SUPERSEDED", "SUPERSEDED")
                or outbox is not None
                or snapshot["generation"] + 1 != generation
            ):
                return None
            receipt_path = (
                self.root / "runtime" / "pre-dispatch-recoveries"
                / f"{row['work_order_id']}.json"
            )
            receipt_raw = receipt_path.read_bytes()
            receipt = json.loads(receipt_raw)
            expected_receipt = {
                "dispatch_id": row["dispatch_id"],
                "dispatch_packet_sha256": row["dispatch_packet_sha256"],
                "reason": "WORK_ORDER_DRIFT:worker_result_contract",
                "schema": "x9-loop-pre-dispatch-worker-result-contract-recovery-v1",
                "task_id": row["task_id"],
                "work_order_id": row["work_order_id"],
                "work_order_sha256": row["packet_sha256"],
            }
            if (
                contract.canonical_json_bytes(receipt) != receipt_raw
                or not all(
                    receipt.get(key) == value
                    for key, value in expected_receipt.items()
                )
                or re.fullmatch(
                    r"[0-9a-f]{64}", receipt.get("outbox_action_sha256", "")
                ) is None
                or row["note"]
                != (
                    f"work_order_sha256={row['packet_sha256']};"
                    "recovery_receipt_sha256="
                    f"{hashlib.sha256(receipt_raw).hexdigest()}"
                )
            ):
                return None
            tables = snapshot["tables"]
            previous_task = [
                item for item in tables["tasks"]
                if item["task_id"] == row["task_id"]
            ]
            previous_order = [
                item for item in tables["work_orders"]
                if item["work_order_id"] == row["work_order_id"]
            ]
            previous_dispatch = [
                item for item in tables["dispatches"]
                if item["dispatch_id"] == row["dispatch_id"]
            ]
            previous_outbox = [
                item for item in tables["outbox"]
                if item["dispatch_id"] == row["dispatch_id"]
            ]
            if (
                len(previous_task) != 1
                or len(previous_order) != 1
                or len(previous_dispatch) != 1
                or len(previous_outbox) != 1
                or previous_task[0]["status"] != "REGISTERED"
                or previous_order[0]["status"] != "CREATED"
                or previous_dispatch[0]["status"] != "PREPARED"
                or previous_order[0]["packet_sha256"] != row["packet_sha256"]
                or previous_dispatch[0]["packet_sha256"]
                != row["dispatch_packet_sha256"]
                or hashlib.sha256(
                    previous_outbox[0]["payload"].encode("utf-8")
                ).hexdigest()
                != receipt["outbox_action_sha256"]
            ):
                return None
            return self._snapshot_bundle(
                connection, current_snapshot_raw=snapshot_raw
            )
        except (
            OSError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            sqlite3.Error,
        ):
            return None
        finally:
            connection.close()

    def rebuild(self) -> dict[str, Any]:
        self._safe_state_path(self.root, directory=True)
        self._safe_state_path(self.snapshot_path)
        self._safe_state_path(self.db_path)
        if not self.snapshot_path.is_file():
            raise SnapshotExportError("SNAPSHOT_MISSING")
        try:
            snapshot_raw = self.snapshot_path.read_bytes()
            snapshot = json.loads(snapshot_raw)
            state = self._decode_snapshot(snapshot_raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SnapshotExportError("SNAPSHOT_INVALID") from exc
        recovery_bundle = self._pre_dispatch_recovery_rebuild_bundle(snapshot_raw)
        if recovery_bundle is not None:
            self._write_snapshot_bundle(recovery_bundle)
            self._write_action(self._current_action())
            self._write_views()
            return {
                "status": "PASS",
                "recovery": {"pre_dispatch_contract_recovery": 1},
            }
        source_schema = snapshot.get("schema")
        capacity = _load_snapshot_capacity()
        legacy_v3 = (
            source_schema == SCHEMA
            and snapshot.get("active_layout") != capacity.ACTIVE_LAYOUT
        )
        target_generation = state["generation"] + (
            1 if source_schema == SCHEMA_V2 or legacy_v3 else 0
        )
        tables = state["tables"]
        completed = state["completed_task_ids"]
        attempts = state["dispatch_attempts"]
        call_archive = state["call_receipt_archive"]
        recovery_worktrees = state["recovery_worktrees"]
        try:
            if self._call_receipt_archive() != call_archive:
                raise SnapshotExportError("CALL_ARCHIVE_DRIFT")
        except StateNotDurableError as exc:
            raise SnapshotExportError("CALL_ARCHIVE_INVALID") from exc

        classifications = {
            row["worktree_id"]: row
            for row in tables["worktree_classifications"]
        }
        tasks = {row["task_id"]: row for row in tables["tasks"]}
        active_task_ids = {
            task_id
            for task_id, row in tasks.items()
            if row["status"] not in {"COMPLETE", "SUPERSEDED"}
        }
        active_worktrees = {
            tasks[task_id]["worktree_id"] for task_id in active_task_ids
        }
        for dispatch in tables["dispatches"]:
            task = tasks.get(dispatch["task_id"])
            if task and dispatch["status"] in {"PREPARED", "DISPATCHED"}:
                active_worktrees.add(task["worktree_id"])
        for table in ("claims", "resources"):
            for row in tables[table]:
                if row["task_id"] in active_task_ids:
                    active_worktrees.add(tasks[row["task_id"]]["worktree_id"])
        strict_recovery_worktrees: list[dict[str, str]] = []
        for row in recovery_worktrees:
            classification = classifications.get(row["worktree_id"], {})
            historical_missing = (
                not Path(row["path"]).is_dir()
                and row["worktree_id"] == "core-legacy"
                and classification.get("classification")
                == "HISTORICAL_MISSING"
                and isinstance(
                    classification.get("owner_decision_sha256"), str
                )
                and re.fullmatch(
                    r"[0-9a-f]{64}",
                    classification["owner_decision_sha256"],
                )
                is not None
                and row["worktree_id"] not in active_worktrees
            )
            if not historical_missing:
                strict_recovery_worktrees.append(row)
        recovery = self._recovery_evidence(
            strict_recovery_worktrees, strict=True
        )
        temporary = self.db_path.with_name(f"loop.db.rebuild-{uuid.uuid4().hex}.tmp")
        self._safe_state_path(temporary, create_parents=True)
        connection: sqlite3.Connection | None = None
        built = False
        try:
            connection = sqlite3.connect(temporary, isolation_level=None)
            self._enable_v7_connection(connection)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            self._schema(connection)
            self._ensure_project_profile(connection)
            connection.execute("BEGIN IMMEDIATE")
            for table in SNAPSHOT_TABLES:
                columns = SNAPSHOT_COLUMNS[table]
                statement = f"INSERT INTO {table}({','.join(columns)}) VALUES({','.join('?' for _ in columns)})"
                for row in tables.get(table, []):
                    connection.execute(statement, tuple(row[column] for column in columns))
            for worktree in recovery_worktrees:
                existing = connection.execute("SELECT path FROM worktrees WHERE worktree_id=?", (worktree["worktree_id"],)).fetchone()
                if existing and existing[0] != worktree["path"]:
                    raise SnapshotExportError("SNAPSHOT_INVALID")
                if not existing:
                    connection.execute("INSERT INTO worktrees(worktree_id,path,repository_id) VALUES(?,?,?)", (worktree["worktree_id"], worktree["path"], "recovery"))
            connection.execute(
                "INSERT INTO metrics(key,value) VALUES('completed_task_ids',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (_json(completed),),
            )
            contract = _load_v7_contract()
            for order in tables.get("work_orders", []):
                evidence_dir = (
                    self.root / "runtime" / "call-receipts"
                    / order["work_order_id"]
                )
                self._safe_state_path(evidence_dir)
                for path in (
                    sorted(evidence_dir.glob("*.json"))
                    if evidence_dir.is_dir()
                    else []
                ):
                    try:
                        self._safe_state_path(path)
                        raw = path.read_bytes()
                        digest = hashlib.sha256(raw).hexdigest()
                        receipt = contract.validate_call_receipt(
                            json.loads(raw), order["packet_sha256"]
                        )
                        if (
                            path.stem != digest
                            or contract.canonical_json_bytes(receipt) != raw
                        ):
                            raise ValueError("receipt evidence")
                        connection.execute(
                            "INSERT INTO call_receipts("
                            "call_id,work_order_id,sequence,receipt_sha256,receipt,created_at"
                            ") VALUES(?,?,?,?,?,?)",
                            (
                                receipt["call_id"],
                                order["work_order_id"],
                                receipt["sequence"],
                                digest,
                                raw.decode("utf-8").rstrip("\n"),
                                self.now_fn(),
                            ),
                        )
                        connection.execute(
                            "INSERT INTO call_reservations("
                            "call_id,work_order_id,sequence,action_class,attempt,"
                            "prompt_prefix_sha256,tool_schema_sha256,status,created_at"
                            ") VALUES(?,?,?,?,?,?,?,?,?)",
                            (
                                receipt["call_id"],
                                order["work_order_id"],
                                receipt["sequence"],
                                receipt["action_class"],
                                receipt["attempt"],
                                receipt["pre_compaction_prompt_prefix_sha256"],
                                receipt["pre_compaction_tool_schema_sha256"],
                                "RECORDED",
                                self.now_fn(),
                            ),
                        )
                    except (
                        OSError, UnicodeDecodeError, json.JSONDecodeError,
                        ValueError, contract.ContractError, sqlite3.Error,
                    ) as exc:
                        raise SnapshotExportError(
                            "CALL_EVIDENCE_INVALID"
                        ) from exc
            try:
                for worktree in strict_recovery_worktrees:
                    root = Path(worktree["path"])
                    self._historical_receipt_paths(root, connection)
                    self._validated_receipt_entries(root, connection)
            except StateNotDurableError as exc:
                raise SnapshotExportError("RECOVERY_RECEIPT_INVALID") from exc

            existing_outbox = {
                row["dispatch_id"] for row in tables.get("outbox", [])
            }
            for row in tables.get("dispatches", []):
                if row["dispatch_id"] not in existing_outbox:
                    if row["status"] != "PREPARED":
                        continue
                    try:
                        packet = json.loads(row["packet"])
                    except (TypeError, json.JSONDecodeError) as exc:
                        raise SnapshotExportError("SNAPSHOT_INVALID") from exc
                    if packet.get("schema") == "x9-loop-work-order-dispatch-v1":
                        order = connection.execute(
                            "SELECT work_order_id,worker_id,packet_path,packet_sha256 "
                            "FROM work_orders WHERE task_id=?",
                            (row["task_id"],),
                        ).fetchone()
                        if not order:
                            raise SnapshotExportError("SNAPSHOT_INVALID")
                        action = self._v7_action(
                            row["dispatch_id"],
                            row["task_id"],
                            order["worker_id"],
                            order["work_order_id"],
                            order["packet_path"],
                            order["packet_sha256"],
                        )
                        action["attempt"] = attempts.get(row["dispatch_id"], 1)
                    else:
                        action = self._action(
                            row["dispatch_id"],
                            packet,
                            row["packet_sha256"],
                            attempt=attempts.get(row["dispatch_id"], 1),
                        )
                    connection.execute(
                        "INSERT INTO outbox(dispatch_id,payload) VALUES(?,?)",
                        (row["dispatch_id"], _json(action)),
                    )
            connection.execute("UPDATE meta SET value=? WHERE key='generation'", (str(target_generation),))
            if connection.execute("PRAGMA foreign_key_check").fetchall() or connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise SnapshotExportError("SNAPSHOT_INVALID")
            connection.commit()
            built = True
        except SnapshotExportError:
            if connection:
                connection.rollback()
            raise
        except (sqlite3.Error, OSError, ValueError) as exc:
            if connection:
                connection.rollback()
            raise SnapshotExportError("SNAPSHOT_INVALID") from exc
        finally:
            if connection:
                connection.close()
            if not built and temporary.exists():
                temporary.unlink()
        preview = sqlite3.connect(
            f"file:{temporary.as_posix()}?mode=ro", uri=True
        )
        preview.row_factory = sqlite3.Row
        try:
            self._validate_v3_schema_shape(preview)
            bundle = self._snapshot_bundle(
                preview,
                current_snapshot_raw=snapshot_raw,
                generation=target_generation,
            )
            self._validate_bundle_targets(bundle)
        finally:
            preview.close()
        self._write_snapshot_bundle(bundle, write_root=False)

        recovery_id = uuid.uuid4().hex
        originals = [
            self.db_path,
            Path(str(self.db_path) + "-wal"),
            Path(str(self.db_path) + "-shm"),
            self.snapshot_path,
        ]
        backups: list[tuple[Path, Path]] = []
        installed = False
        hold_complete = False
        try:
            for original in originals:
                self._safe_state_path(original)
                if original.exists():
                    backup = original.with_name(
                        original.name + f".corrupt-{recovery_id}"
                    )
                    self._safe_state_path(backup, create_parents=True)
                    os.replace(original, backup)
                    backups.append((original, backup))
            hold_complete = True
            os.replace(temporary, self.db_path)
            installed = True
            self._safe_state_path(self.db_path)
            self._write_snapshot_bundle(bundle)
            self._assert_durable()
        except BaseException as exc:
            if hold_complete:
                for current in (
                    self.db_path,
                    Path(str(self.db_path) + "-wal"),
                    Path(str(self.db_path) + "-shm"),
                    self.snapshot_path,
                ):
                    try:
                        self._safe_state_path(current)
                        if current.exists():
                            failed = current.with_name(
                                current.name + f".failed-{recovery_id}"
                            )
                            self._safe_state_path(failed, create_parents=True)
                            os.replace(current, failed)
                    except OSError:
                        pass
            for original, backup in reversed(backups):
                if backup.exists() and not original.exists():
                    os.replace(backup, original)
            if temporary.exists():
                failed = self.db_path.with_name(
                    f"loop.db.failed-{recovery_id}"
                )
                self._safe_state_path(failed, create_parents=True)
                try:
                    os.replace(temporary, failed)
                except OSError:
                    pass
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise SnapshotExportError("REBUILD_REPLACE_FAILED") from exc
        self._write_action(self._current_action())
        self._write_views()
        return {"status": "PASS", "recovery": recovery}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=None)
    subcommands = parser.add_subparsers(dest="command", required=True)
    def command(name: str) -> argparse.ArgumentParser:
        child = subcommands.add_parser(name)
        child.add_argument("--repo", dest="command_repo", default=None)
        child.add_argument("--json", action="store_true", help="emit JSON result or error")
        return child
    init = command("init")
    init.add_argument("--import-v5", action="store_true")
    register = command("register")
    register.add_argument("--file")
    reconcile = command("reconcile")
    reconcile.add_argument("--task")
    prepare = command("prepare-dispatch")
    prepare.add_argument("--task")
    prepare.add_argument("--sender")
    delivery = command("record-delivery")
    delivery.add_argument("--dispatch")
    delivery.add_argument("--phase")
    delivery.add_argument("--method")
    delivery.add_argument("--result")
    consume = command("consume-event")
    consume.add_argument("--file")
    run_once_command = command("run-once")
    run_once_command.add_argument("--file", required=True)
    ingest_worker_result = command("ingest-worker-result")
    ingest_worker_result.add_argument("--file", required=True)
    migrate = command("migrate-v2")
    migrate.add_argument("--file")
    command("migrate-v3")
    rollback = command("rollback-v6")
    rollback.add_argument("--recovery", required=True)
    rollback_v7 = command("rollback-v7")
    rollback_v7.add_argument("--recovery", required=True)
    command("recover-migration")
    import_program_command = command("import-program")
    import_program_command.add_argument("--file", required=True)
    import_program_command.add_argument("--source-git-sha", required=True)
    import_program_command.add_argument("--source-root", required=True)
    import_program_command.add_argument(
        "--source-root-sha256", required=True
    )
    import_program_command.add_argument("--metadata-file", required=True)
    import_program_command.add_argument("--required-source-class", action="append", default=[])
    create_order = command("create-work-order")
    create_order.add_argument("--file", required=True)
    verify_order = command("verify-work-order")
    verify_order.add_argument("--work-order", required=True)
    check_call = command("check-model-call")
    check_call.add_argument("--work-order", required=True)
    check_call.add_argument("--file", required=True)
    record_call = command("record-call-receipt")
    record_call.add_argument("--work-order", required=True)
    record_call.add_argument("--file", required=True)
    thinker_review = command("admit-thinker-review")
    thinker_review.add_argument("--work-order", required=True)
    thinker_review.add_argument("--file", required=True)
    thinker_verdict = command("record-thinker-verdict")
    thinker_verdict.add_argument("--work-order", required=True)
    thinker_verdict.add_argument("--consultation-key", required=True)
    thinker_verdict.add_argument("--verdict", required=True)
    thinker_verdict.add_argument("--thinker", required=True)
    thinker_verdict.add_argument("--verdict-sha256", required=True)
    supersede = command("supersede-paused")
    supersede.add_argument("--task", required=True)
    supersede.add_argument("--result-sha256", required=True)
    supersede_owner = command("supersede-owner-decision")
    supersede_owner.add_argument("--task", required=True)
    supersede_owner.add_argument("--result-sha256", required=True)
    pre_dispatch_recovery = command(
        "recover-pre-dispatch-worker-result-contract-drift"
    )
    pre_dispatch_recovery.add_argument("--work-order", required=True)
    pre_dispatch_recovery.add_argument("--work-order-sha256", required=True)
    receipt_set_recovery = command(
        "recover-receipt-set-mismatch-worker-result"
    )
    receipt_set_recovery.add_argument("--work-order", required=True)
    receipt_set_recovery.add_argument("--work-order-sha256", required=True)
    receipt_set_recovery.add_argument("--file", required=True)
    command("doctor")
    command("doctor-v7")
    command("rebuild")
    args = parser.parse_args()
    def payload(file_path: str | None = None) -> dict[str, Any]:
        if not file_path:
            return {}
        value = json.loads(Path(file_path).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise IdentityError("PAYLOAD_INVALID")
        return value
    controller = Controller(args.command_repo or args.repo or ".")
    try:
        if args.command == "init":
            result = controller.init(args.import_v5)
        elif args.command == "migrate-v2":
            result = controller.migrate_v1_to_v2(
                payload(args.file)
            )
        elif args.command == "migrate-v3":
            result = controller.migrate_v2_to_v3()
        elif args.command == "rollback-v6":
            result = controller.rollback_to_v6(args.recovery)
        elif args.command == "rollback-v7":
            result = controller.rollback_to_v7(args.recovery)
        elif args.command == "recover-migration":
            result = controller.recover_interrupted_migration()
        elif args.command == "register":
            data = payload(args.file)
            kind = data.pop("kind", None)
            if kind is None:
                schema = data.get("schema")
                if schema == "x9-loop-lite-task-v1":
                    kind = "task"
                elif "actor_id" in data:
                    kind = "actor"
                elif "worktree_id" in data and "task_id" not in data:
                    kind = "worktree"
            if kind not in {"actor", "worktree", "task"}:
                raise IdentityError("REGISTER_KIND_INVALID")
            result = getattr(controller, f"register_{kind}")(**data)
        elif args.command == "import-program":
            result = controller.import_program(
                payload(args.file),
                source_git_sha=args.source_git_sha,
                source_root=args.source_root,
                source_root_sha256=args.source_root_sha256,
                metadata_by_path=payload(args.metadata_file),
                required_source_classes=args.required_source_class,
            )
        elif args.command == "create-work-order":
            result = controller.create_work_order(
                **payload(args.file)
            )
        elif args.command == "verify-work-order":
            result = controller.verify_work_order(
                args.work_order
            )
        elif args.command == "check-model-call":
            result = controller.check_model_call(
                args.work_order, payload(args.file)
            )
        elif args.command == "record-call-receipt":
            result = controller.record_call_receipt(
                args.work_order, payload(args.file)
            )
        elif args.command == "admit-thinker-review":
            result = controller.admit_thinker_review(
                args.work_order, payload(args.file)
            )
        elif args.command == "record-thinker-verdict":
            result = controller.record_thinker_verdict(
                args.work_order,
                args.consultation_key,
                args.verdict,
                args.thinker,
                args.verdict_sha256,
            )
        elif args.command == "supersede-paused":
            result = controller.supersede_paused(
                args.task, args.result_sha256
            )
        elif args.command == "supersede-owner-decision":
            result = controller.supersede_owner_decision(
                args.task, args.result_sha256
            )
        elif args.command == "recover-pre-dispatch-worker-result-contract-drift":
            result = controller.recover_pre_dispatch_worker_result_contract_drift(
                args.work_order, args.work_order_sha256
            )
        elif args.command == "recover-receipt-set-mismatch-worker-result":
            result = controller.recover_receipt_set_mismatch_worker_result(
                args.work_order, args.work_order_sha256, args.file
            )

        elif args.command == "reconcile":
            result = controller.reconcile(args.task)
        elif args.command == "prepare-dispatch":
            result = controller.prepare_dispatch(args.task, args.sender)
        elif args.command == "record-delivery":
            result = controller.record_delivery(args.dispatch, args.phase, args.method, args.result)
        elif args.command == "consume-event":
            result = controller.consume_event(payload(args.file))
        elif args.command == "ingest-worker-result":
            result = controller.ingest_worker_result(args.file)
        elif args.command == "run-once":
            result = controller.run_once(args.file)
        elif args.command == "doctor":
            result = controller.doctor()
        elif args.command == "doctor-v7":
            result = controller.doctor_v7()
        else:
            result = controller.rebuild()
    except (LoopError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(_json({"status": "ERROR", "error": str(exc)}))
        return 2
    print(_json(result))
    return 0

if __name__ == "__main__":
    # CLI execution must not leave bytecode in the immutable package.
    sys.dont_write_bytecode = True
    raise SystemExit(main())
