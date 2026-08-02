#!/usr/bin/env python3
"""One-shot, zero-model transport for one canonical Controller ACTION.

This module deliberately has no provider, network, database, scheduler, model,
or task-selection capability.  The injected adapter receives the exact ACTION
bytes once and the module emits one canonical acknowledgement event suitable
for a later Controller ``run-once --file`` boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import sys
import unicodedata
import uuid
from typing import Any, Protocol


ACTION_CAP_BYTES = 4 * 1024
DELIVERY_MODE_DURABLE_NONWAKING_DROP = "DURABLE_NONWAKING_DROP"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_TOKEN = re.compile(r"[A-Za-z0-9._:-]{1,128}")
_ACTION_ID = re.compile(r"act-[0-9a-f-]{36}")


class LinkerError(RuntimeError):
    """Stable, secret-safe LINKER failure code."""


class ActionAdapter(Protocol):
    adapter_id: str
    delivery_mode: str

    def deliver(self, action_bytes: bytes, action_sha256: str) -> str: ...


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


def _decode_canonical(raw: bytes, code: str) -> dict[str, Any]:
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            parse_float=lambda _value: (_ for _ in ()).throw(
                ValueError("floating number")
            ),
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LinkerError(code) from exc
    if not isinstance(payload, dict):
        raise LinkerError(code)
    try:
        expected = _canonical_json_bytes(payload)
    except (TypeError, ValueError) as exc:
        raise LinkerError(code) from exc
    if raw != expected:
        raise LinkerError(code)
    return payload


def _is_reparse(path: Path) -> bool:
    try:
        stat = path.lstat()
    except OSError:
        return False
    attributes = getattr(stat, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & 0x400)


def _assert_plain_parents(path: Path) -> None:
    current = path.parent
    while True:
        if current.exists() and _is_reparse(current):
            raise LinkerError("OUTPUT_PATH_INVALID")
        if current == current.parent:
            return
        current = current.parent


def _read_plain(
    path: Path,
    missing_code: str,
    invalid_code: str,
    *,
    maximum_bytes: int,
    too_large_code: str,
) -> bytes:
    try:
        if not path.exists():
            raise LinkerError(missing_code)
        if _is_reparse(path) or not path.is_file():
            raise LinkerError(invalid_code)
        if path.stat().st_size > maximum_bytes:
            raise LinkerError(too_large_code)
        return path.read_bytes()
    except LinkerError:
        raise
    except OSError as exc:
        raise LinkerError(invalid_code) from exc


def _write_once(path: Path, raw: bytes, conflict_code: str) -> bool:
    """Write new exact bytes atomically; return False for an exact replay."""
    _assert_plain_parents(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _assert_plain_parents(path)
        if path.exists():
            if _is_reparse(path) or not path.is_file():
                raise LinkerError("OUTPUT_PATH_INVALID")
            if path.stat().st_size != len(raw):
                raise LinkerError(conflict_code)
            if path.read_bytes() == raw:
                return False
            raise LinkerError(conflict_code)
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
                    raise LinkerError("OUTPUT_PATH_INVALID")
                if path.stat().st_size != len(raw):
                    raise LinkerError(conflict_code)
                if path.read_bytes() == raw:
                    return False
                raise LinkerError(conflict_code)
        finally:
            if temporary.exists():
                temporary.unlink()
        return True
    except LinkerError:
        raise
    except OSError as exc:
        raise LinkerError("OUTPUT_WRITE_FAILED") from exc


def _canonical_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise LinkerError("ACTION_IDENTITY_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value or normalized.startswith("/"):
        raise LinkerError("ACTION_IDENTITY_INVALID")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise LinkerError("ACTION_IDENTITY_INVALID")
    canonical = str(PurePosixPath(*parts))
    if canonical != normalized or re.match(r"^[A-Za-z]:", canonical):
        raise LinkerError("ACTION_IDENTITY_INVALID")
    return canonical


def _validate_action(action: dict[str, Any]) -> str:
    if (
        action.get("schema") == "x9-loop-lite-action-v1"
        and action.get("action") in {"WAIT", "NOOP"}
    ):
        return "NO_ACTION"
    required = {
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
    repair_fields = {
        *required,
        "expected_result_schema",
        "invalid_event_id",
        "invalid_result_sha256",
        "reason",
    }
    if frozenset(action) not in {frozenset(required), frozenset(repair_fields)}:
        raise LinkerError("ACTION_FIELDS_INVALID")
    action_type = action.get("action")
    if (
        action["schema"] != "x9-loop-action-v2"
        or action_type not in {"SEND_WORK_ORDER", "RESULT_SCHEMA_REPAIR"}
        or action["must_record_transport"] is not True
        or action["target_role"] != "WORKER"
        or not isinstance(action["attempt"], int)
        or isinstance(action["attempt"], bool)
        or action["attempt"] < 1
        or not isinstance(action["action_id"], str)
        or _ACTION_ID.fullmatch(action["action_id"]) is None
    ):
        raise LinkerError("ACTION_IDENTITY_INVALID")
    if action_type == "RESULT_SCHEMA_REPAIR" and (
        set(action) != repair_fields
        or action["expected_result_schema"] != "x9-loop-result-v2"
        or action["reason"] not in {
            "RESULT_FIELDS_INVALID", "RESULT_SCHEMA_INVALID"
        }
        or not isinstance(action["invalid_event_id"], str)
        or _TOKEN.fullmatch(action["invalid_event_id"]) is None
        or not isinstance(action["invalid_result_sha256"], str)
        or _SHA256.fullmatch(action["invalid_result_sha256"]) is None
    ):
        raise LinkerError("ACTION_IDENTITY_INVALID")
    for field in (
        "dispatch_id",
        "project_profile_id",
        "target_actor_id",
        "task_id",
        "work_order_id",
    ):
        value = action[field]
        if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
            raise LinkerError("ACTION_IDENTITY_INVALID")
    if (
        not isinstance(action["work_order_sha256"], str)
        or _SHA256.fullmatch(action["work_order_sha256"]) is None
    ):
        raise LinkerError("ACTION_IDENTITY_INVALID")
    _canonical_repo_path(action["work_order_path"])
    return action_type


def validate_result_ready_signal(
    source: bytes | str | Path,
    *,
    expected_requester: str | None = None,
    expected_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one signal-only RESULT_READY without waking or delivering."""
    if isinstance(source, (str, Path)):
        raw = _read_plain(
            Path(source),
            "RESULT_READY_MISSING",
            "RESULT_READY_PATH_INVALID",
            maximum_bytes=ACTION_CAP_BYTES,
            too_large_code="RESULT_READY_TOO_LARGE",
        )
    elif isinstance(source, bytes):
        raw = source
    else:
        raise LinkerError("RESULT_READY_INVALID")
    if len(raw) > ACTION_CAP_BYTES:
        raise LinkerError("RESULT_READY_TOO_LARGE")
    signal = _decode_canonical(raw, "RESULT_READY_INVALID")
    required = {
        "callback_id",
        "expected_result_identity",
        "expires_at",
        "project_profile_id",
        "return_to_task_id",
        "schema",
        "source_role",
        "status",
    }
    if (
        set(signal) != required
        or signal["schema"] != "x9-loop-result-ready-v1"
        or signal["source_role"] != "WORKER"
        or signal["status"] != "READY"
        or not isinstance(signal["callback_id"], str)
        or _TOKEN.fullmatch(signal["callback_id"]) is None
        or not isinstance(signal["expires_at"], str)
        or _TOKEN.fullmatch(signal["expires_at"]) is None
        or not isinstance(signal["project_profile_id"], str)
        or _TOKEN.fullmatch(signal["project_profile_id"]) is None
        or not isinstance(signal["return_to_task_id"], str)
        or _TOKEN.fullmatch(signal["return_to_task_id"]) is None
    ):
        raise LinkerError("RESULT_READY_IDENTITY_INVALID")
    identity = signal["expected_result_identity"]
    identity_fields = {
        "dispatch_id", "event_id", "packet_sha256", "result_path",
        "result_sha256", "task_id", "work_order_id", "work_order_sha256",
        "worker_id",
    }
    if not isinstance(identity, dict) or set(identity) != identity_fields:
        raise LinkerError("RESULT_READY_IDENTITY_INVALID")
    for field in ("dispatch_id", "event_id", "task_id", "work_order_id", "worker_id"):
        if not isinstance(identity[field], str) or _TOKEN.fullmatch(identity[field]) is None:
            raise LinkerError("RESULT_READY_IDENTITY_INVALID")
    for field in ("packet_sha256", "result_sha256", "work_order_sha256"):
        if not isinstance(identity[field], str) or _SHA256.fullmatch(identity[field]) is None:
            raise LinkerError("RESULT_READY_IDENTITY_INVALID")
    _canonical_repo_path(identity["result_path"])
    if expected_requester is not None:
        if signal["return_to_task_id"] != expected_requester:
            raise LinkerError("RESULT_READY_REQUESTER_MISMATCH")
    if expected_identity is not None and identity != expected_identity:
        raise LinkerError("RESULT_READY_IDENTITY_MISMATCH")
    return signal


consume_result_ready_signal = validate_result_ready_signal


def _ack_payload(
    action: dict[str, Any],
    action_sha256: str,
) -> dict[str, Any]:
    return {
        "ack_id": "ack-" + action_sha256[:32],
        "action": action["action"],
        "action_id": action["action_id"],
        "action_sha256": action_sha256,
        "dispatch_id": action["dispatch_id"],
        "project_profile_id": action["project_profile_id"],
        "schema": "x9-loop-transport-ack-v1",
        "status": "DELIVERED",
        "work_order_id": action["work_order_id"],
        "work_order_sha256": action["work_order_sha256"],
        "worker_id": action["target_actor_id"],
    }


def _validate_existing_ack(
    raw: bytes,
    action: dict[str, Any],
    action_sha256: str,
) -> dict[str, Any]:
    if len(raw) > ACTION_CAP_BYTES:
        raise LinkerError("ACK_RECEIPT_INVALID")
    ack = _decode_canonical(raw, "ACK_RECEIPT_INVALID")
    required = {
        "ack_id",
        "action",
        "action_id",
        "action_sha256",
        "dispatch_id",
        "project_profile_id",
        "schema",
        "status",
        "work_order_id",
        "work_order_sha256",
        "worker_id",
    }
    valid = (
        set(ack) == required
        and ack.get("schema") == "x9-loop-transport-ack-v1"
        and ack.get("action") == action["action"]
        and ack.get("status") == "DELIVERED"
        and ack.get("action_id") == action["action_id"]
        and ack.get("action_sha256") == action_sha256
        and ack.get("dispatch_id") == action["dispatch_id"]
        and ack.get("project_profile_id") == action["project_profile_id"]
        and ack.get("ack_id") == "ack-" + action_sha256[:32]
        and ack.get("work_order_id") == action["work_order_id"]
        and ack.get("work_order_sha256") == action["work_order_sha256"]
        and ack.get("worker_id") == action["target_actor_id"]
    )
    if not valid:
        raise LinkerError("ACK_RECEIPT_CONFLICT")
    return ack


class LocalFileAdapter:
    """Conformance adapter that atomically drops exact ACTION bytes locally."""

    delivery_mode = DELIVERY_MODE_DURABLE_NONWAKING_DROP

    def __init__(self, destination: str | Path, adapter_id: str = "local-file-v1"):
        if not isinstance(adapter_id, str) or _TOKEN.fullmatch(adapter_id) is None:
            raise LinkerError("ADAPTER_ID_INVALID")
        self.destination = Path(destination)
        self.adapter_id = adapter_id

    def deliver(self, action_bytes: bytes, action_sha256: str) -> str:
        if hashlib.sha256(action_bytes).hexdigest() != action_sha256:
            raise LinkerError("ACTION_HASH_MISMATCH")
        wrote = _write_once(
            self.destination,
            action_bytes,
            "DELIVERY_TARGET_CONFLICT",
        )
        return "ACKNOWLEDGED" if wrote else "ALREADY_DELIVERED"


def link_once(
    action_path: str | Path,
    acknowledgement_path: str | Path,
    adapter: ActionAdapter,
) -> dict[str, Any]:
    """Transport one canonical ACTION and seal one acknowledgement event."""
    action_file = Path(action_path)
    ack_file = Path(acknowledgement_path)
    raw = _read_plain(
        action_file,
        "ACTION_MISSING",
        "ACTION_PATH_INVALID",
        maximum_bytes=ACTION_CAP_BYTES,
        too_large_code="ACTION_TOO_LARGE",
    )
    action = _decode_canonical(raw, "ACTION_NOT_CANONICAL")
    disposition = _validate_action(action)
    action_sha256 = hashlib.sha256(raw).hexdigest()
    if disposition == "NO_ACTION":
        return {"action_sha256": action_sha256, "status": "NO_ACTION"}

    adapter_id = getattr(adapter, "adapter_id", None)
    if not isinstance(adapter_id, str) or _TOKEN.fullmatch(adapter_id) is None:
        raise LinkerError("ADAPTER_ID_INVALID")
    if (
        getattr(adapter, "delivery_mode", None)
        != DELIVERY_MODE_DURABLE_NONWAKING_DROP
    ):
        raise LinkerError("WAKING_ADAPTER_FORBIDDEN")
    existing_ack_raw: bytes | None = None
    if ack_file.exists():
        existing_ack_raw = _read_plain(
            ack_file,
            "ACK_RECEIPT_INVALID",
            "ACK_RECEIPT_INVALID",
            maximum_bytes=ACTION_CAP_BYTES,
            too_large_code="ACK_RECEIPT_INVALID",
        )
        _validate_existing_ack(
            existing_ack_raw, action, action_sha256
        )

    result = adapter.deliver(raw, action_sha256)
    if result not in {"ACKNOWLEDGED", "ALREADY_DELIVERED"}:
        raise LinkerError("ADAPTER_ACK_INVALID")
    if existing_ack_raw is not None:
        return {
            "ack_sha256": hashlib.sha256(existing_ack_raw).hexdigest(),
            "action_sha256": action_sha256,
            "status": "ALREADY_ACKNOWLEDGED",
        }

    ack_raw = _canonical_json_bytes(
        _ack_payload(action, action_sha256)
    )
    if len(ack_raw) > ACTION_CAP_BYTES:
        raise LinkerError("ACK_RECEIPT_INVALID")
    wrote = _write_once(ack_file, ack_raw, "ACK_RECEIPT_CONFLICT")
    if not wrote:
        _validate_existing_ack(
            _read_plain(
                ack_file,
                "ACK_RECEIPT_INVALID",
                "ACK_RECEIPT_INVALID",
                maximum_bytes=ACTION_CAP_BYTES,
                too_large_code="ACK_RECEIPT_INVALID",
            ),
            action, action_sha256
        )
    return {
        "ack_sha256": hashlib.sha256(ack_raw).hexdigest(),
        "action_sha256": action_sha256,
        "status": result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", required=True)
    parser.add_argument("--ack", required=True)
    parser.add_argument("--drop", required=True)
    parser.add_argument("--adapter-id", default="local-file-v1")
    args = parser.parse_args(argv)
    try:
        result = link_once(
            args.action,
            args.ack,
            LocalFileAdapter(args.drop, args.adapter_id),
        )
    except (LinkerError, OSError, TypeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, LinkerError) else "LINKER_FAILED"
        sys.stdout.buffer.write(
            _canonical_json_bytes({"error": code, "status": "ERROR"})
        )
        return 2
    sys.stdout.buffer.write(_canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
