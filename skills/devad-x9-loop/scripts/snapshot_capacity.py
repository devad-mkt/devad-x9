"""Canonical sharded snapshot storage for X9 Loop V7 capacity releases."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any, Callable, Mapping, Sequence


SCHEMA_V2 = "x9-loop-lite-snapshot-v2"
SCHEMA_V3 = "x9-loop-lite-snapshot-v3"
SHARD_SCHEMA = "x9-loop-snapshot-terminal-shard-v1"
ACTIVE_SHARD_SCHEMA = "x9-loop-snapshot-active-detail-shard-v1"
ROOT_CAP_BYTES = 8 * 1024
SHARD_CAP_BYTES = 64 * 1024
ACTIVE_ORDER_CAP = 3
ACTIVE_ORDER_RESERVATION_BYTES = 2200
LEGACY_ACTIVE_DETAIL_TABLES = ("claims", "resources")
ACTIVE_DETAIL_TABLES = (
    "tasks",
    "claims",
    "resources",
    "dispatches",
    "deliveries",
    "events",
    "gates",
    "metrics",
    "outbox",
    "programs",
    "work_orders",
    "call_reservations",
    "inbox",
)
ACTIVE_LAYOUT = "active-lifecycle-v1"


class SnapshotCapacityError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _legacy_v1_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def table_schema_sha256(columns: Mapping[str, Sequence[str]]) -> str:
    return sha256(
        canonical_bytes(
            {name: list(values) for name, values in sorted(columns.items())}
        )
    )


def _active_sets(tables: Mapping[str, list[dict[str, Any]]]) -> dict[str, set[str]]:
    tasks = {
        row["task_id"]: row
        for row in tables["tasks"]
        if row["status"] not in {"COMPLETE", "SUPERSEDED"}
    }
    task_ids = set(tasks)
    dispatches = {
        row["dispatch_id"]: row
        for row in tables["dispatches"]
        if row["task_id"] in task_ids
        and row["status"] in {"PREPARED", "DISPATCHED"}
    }
    for task_id, task in tasks.items():
        if task["status"] != "THINX_REVIEW_REQUIRED":
            continue
        candidates = [
            row for row in tables["dispatches"] if row["task_id"] == task_id
        ]
        if candidates:
            latest = candidates[-1]
            dispatches[latest["dispatch_id"]] = latest
    dispatch_ids = set(dispatches)
    orders = {
        row["work_order_id"]: row
        for row in tables["work_orders"]
        if row["task_id"] in task_ids
        and row["status"] not in {"COMPLETE", "EXPIRED", "SUPERSEDED"}
    }
    order_ids = set(orders)
    actor_ids = {row["worker_id"] for row in tasks.values()}
    for row in dispatches.values():
        actor_ids.update((row["sender_id"], row["target_id"]))
    worktree_ids = {row["worktree_id"] for row in tasks.values()}
    program_ids = {row["program_id"] for row in orders.values()}
    metric_keys = {f"blocked:{task_id}" for task_id in task_ids}
    metric_keys.update(f"task-contract:{task_id}" for task_id in task_ids)
    for order_id in order_ids:
        metric_keys.update(
            f"{prefix}:{order_id}"
            for prefix in (
                "call-count",
                "call-latest",
                "call-root",
                "call-tokens",
                "call-unknown",
            )
        )
    return {
        "tasks": task_ids,
        "dispatches": dispatch_ids,
        "orders": order_ids,
        "actors": actor_ids,
        "worktrees": worktree_ids,
        "programs": program_ids,
        "metrics": metric_keys,
    }


def _is_active(
    table: str, row: Mapping[str, Any], active: Mapping[str, set[str]]
) -> bool:
    if table == "actors":
        return row["actor_id"] in active["actors"]
    if table == "worktrees":
        return row["worktree_id"] in active["worktrees"]
    if table in {"tasks", "claims", "resources", "gates"}:
        return row["task_id"] in active["tasks"]
    if table in {"dispatches", "deliveries", "events", "outbox"}:
        return row["dispatch_id"] in active["dispatches"]
    if table == "metrics":
        return row["key"] in active["metrics"]
    if table == "programs":
        return row["program_id"] in active["programs"]
    if table == "work_orders":
        return row["work_order_id"] in active["orders"]
    if table == "worktree_classifications":
        return row["worktree_id"] in active["worktrees"]
    if table == "call_reservations":
        return (
            row["work_order_id"] in active["orders"]
            and row["status"] == "RESERVED"
        )
    if table == "inbox":
        return row["status"] == "PENDING"
    return False


def _default_receipt_metric(row: Mapping[str, Any]) -> bool:
    key, value = row["key"], row["value"]
    empty_root = hashlib.sha256(b"[]").hexdigest()
    return (
        (key.startswith("historical-receipts:") and value == "{}")
        or (key.startswith("receipt-count:") and value == "0")
        or (key.startswith("receipt-root:") and value == empty_root)
    )


def _previous_reference(
    current_raw: bytes | None, generation: int
) -> tuple[dict[str, Any] | None, tuple[str, bytes] | None]:
    if not current_raw:
        return None, None
    try:
        current = json.loads(current_raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID") from exc
    schema = current.get("schema")
    expected_raw = (
        _legacy_v1_bytes(current)
        if schema == "x9-loop-lite-snapshot-v1"
        else canonical_bytes(current)
    )
    if expected_raw != current_raw or len(current_raw) > ROOT_CAP_BYTES:
        raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID")
    if (
        current.get("schema") == SCHEMA_V3
        and current.get("generation") == generation
    ):
        previous = current.get("previous_generation")
        if previous is not None and not isinstance(previous, dict):
            raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID")
        return previous, None
    previous_generation = current.get("generation")
    if (
        schema not in {"x9-loop-lite-snapshot-v1", SCHEMA_V2, SCHEMA_V3}
        or isinstance(previous_generation, bool)
        or not isinstance(previous_generation, int)
        or previous_generation >= generation
    ):
        raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID")
    digest = sha256(current_raw)
    path = f".devad/manager/loop-lite/snapshots/roots/{digest}.json"
    return (
        {
            "byte_size": len(current_raw),
            "generation": previous_generation,
            "path": path,
            "schema": schema,
            "sha256": digest,
        },
        (path, current_raw),
    )


def _shard_records(
    generation: int,
    records: list[list[Any]],
    *,
    kind: str,
    schema: str,
    allow_empty: bool,
) -> list[tuple[dict[str, Any], bytes]]:
    shards: list[tuple[dict[str, Any], bytes]] = []
    index = 0
    current: list[list[Any]] = []

    def payload(rows: list[list[Any]], shard_index: int) -> dict[str, Any]:
        return {
            "generation": generation,
            "index": shard_index,
            "kind": kind,
            "records": rows,
            "schema": schema,
        }

    for record in records:
        candidate = canonical_bytes(payload([*current, record], index))
        if len(candidate) <= SHARD_CAP_BYTES:
            current.append(record)
            continue
        if not current:
            raise SnapshotCapacityError("SNAPSHOT_SHARD_TOO_LARGE")
        raw = canonical_bytes(payload(current, index))
        digest = sha256(raw)
        path = (
            ".devad/manager/loop-lite/snapshots/generations/"
            f"{generation}/shards/{digest}.json"
        )
        shards.append(
            (
                {
                    "byte_size": len(raw),
                    "count": len(current),
                    "generation": generation,
                    "index": index,
                    "kind": kind,
                    "path": path,
                    "schema": schema,
                    "sha256": digest,
                },
                raw,
            )
        )
        index += 1
        current = [record]
    if current or (allow_empty and not shards):
        raw = canonical_bytes(payload(current, index))
        if len(raw) > SHARD_CAP_BYTES:
            raise SnapshotCapacityError("SNAPSHOT_SHARD_TOO_LARGE")
        digest = sha256(raw)
        path = (
            ".devad/manager/loop-lite/snapshots/generations/"
            f"{generation}/shards/{digest}.json"
        )
        shards.append(
            (
                {
                    "byte_size": len(raw),
                    "count": len(current),
                    "generation": generation,
                    "index": index,
                    "kind": kind,
                    "path": path,
                    "schema": schema,
                    "sha256": digest,
                },
                raw,
            )
        )
    return shards


def build_bundle(
    *,
    generation: int,
    columns: Mapping[str, Sequence[str]],
    tables: Mapping[str, list[dict[str, Any]]],
    recovery_worktrees: list[dict[str, str]],
    completed_task_ids: list[str],
    dispatch_attempts: Mapping[str, int],
    call_receipt_archive: Mapping[str, Any],
    current_snapshot_raw: bytes | None,
) -> dict[str, Any]:
    if set(tables) != set(columns):
        raise SnapshotCapacityError("SNAPSHOT_TABLE_UNKNOWN")
    active = _active_sets(tables)
    current_layout: str | None = None
    if current_snapshot_raw:
        try:
            current_snapshot = json.loads(current_snapshot_raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            current_snapshot = {}
        if (
            current_snapshot.get("schema") == SCHEMA_V3
            and current_snapshot.get("generation") == generation
        ):
            if "active_shards" not in current_snapshot:
                current_layout = "legacy-inline"
            elif "active_layout" not in current_snapshot:
                current_layout = "legacy-active-detail"
            elif current_snapshot.get("active_layout") == ACTIVE_LAYOUT:
                current_layout = ACTIVE_LAYOUT
    detail_tables = (
        ()
        if current_layout == "legacy-inline"
        else tuple(
            table
            for table in LEGACY_ACTIVE_DETAIL_TABLES
            if table in columns
        )
        if current_layout == "legacy-active-detail"
        else tuple(
            table for table in ACTIVE_DETAIL_TABLES if table in columns
        )
    )
    active_tables: dict[str, list[list[Any]]] = {}
    active_detail_rows: dict[str, list[list[Any]]] = {
        table: [] for table in detail_tables
    }
    records: list[list[Any]] = []
    for table in columns:
        active_rows: list[list[Any]] = []
        for row in tables[table]:
            if set(row) != set(columns[table]):
                raise SnapshotCapacityError("SNAPSHOT_COLUMN_UNKNOWN")
            values = [row[column] for column in columns[table]]
            if table == "metrics" and (
                row["key"] == "completed_task_ids"
                or _default_receipt_metric(row)
            ):
                continue
            if table == "call_reservations" and row["status"] != "RESERVED":
                continue
            active_row = _is_active(table, row, active)
            if (
                table == "outbox"
                and active_row
                and current_layout in {"legacy-inline", "legacy-active-detail"}
            ):
                continue
            if active_row:
                if table in detail_tables:
                    active_detail_rows[table].append(values)
                else:
                    active_rows.append(values)
            else:
                records.append(["table", table, values])
        active_tables[table] = active_rows

    referenced_complete: set[str] = set()
    completed_set = set(completed_task_ids)
    dependency_index = columns["tasks"].index("dependencies")
    task_rows = [*active_tables["tasks"]]
    if "tasks" in active_detail_rows:
        task_rows.extend(active_detail_rows["tasks"])
    for row in task_rows:
        try:
            dependencies = json.loads(row[dependency_index])
        except (TypeError, json.JSONDecodeError) as exc:
            raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DEPENDENCY_INVALID") from exc
        if not isinstance(dependencies, list):
            raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DEPENDENCY_INVALID")
        referenced_complete.update(
            item for item in dependencies if item in completed_set
        )
    active_completed = sorted(referenced_complete)
    for task_id in completed_task_ids:
        if task_id not in referenced_complete:
            records.append(["completed", task_id])
    for row in recovery_worktrees:
        records.append(["recovery", [row["worktree_id"], row["path"]]])
    records.sort(key=canonical_bytes)

    terminal_shards = _shard_records(
        generation,
        records,
        kind="terminal-state",
        schema=SHARD_SCHEMA,
        allow_empty=True,
    )
    active_detail_records: list[list[Any]] = []
    active_detail_summaries: dict[str, Any] = {}
    for table in detail_tables:
        for values in active_detail_rows[table]:
            active_detail_records.append(["table", table, values])
    if current_layout == "legacy-active-detail":
        for table in detail_tables:
            task_index = columns[table].index("task_id")
            counts: dict[str, int] = {}
            for values in active_detail_rows[table]:
                task_id = values[task_index]
                counts[task_id] = counts.get(task_id, 0) + 1
            active_detail_summaries[table] = [
                [task_id, count] for task_id, count in sorted(counts.items())
            ]
    elif current_layout != "legacy-inline":
        def compact_rows(table: str, selected: Sequence[str]) -> list[list[Any]]:
            indices = [columns[table].index(column) for column in selected]
            return sorted(
                [
                    [values[index] for index in indices]
                    for values in active_detail_rows[table]
                ],
                key=canonical_bytes,
            )

        active_detail_summaries = {
            "counts": [
                [table, len(active_detail_rows[table])]
                for table in detail_tables
                if active_detail_rows[table]
            ],
            "dispatches": compact_rows(
                "dispatches",
                ("dispatch_id", "task_id", "sender_id", "target_id", "status"),
            ),
            "tasks": compact_rows(
                "tasks", ("task_id", "worker_id", "worktree_id", "status")
            ),
            "work_orders": compact_rows(
                "work_orders",
                ("work_order_id", "task_id", "worker_id", "program_id", "status"),
            ),
        }
    active_detail_records.sort(key=canonical_bytes)
    active_shards = _shard_records(
        generation,
        active_detail_records,
        kind="active-detail",
        schema=ACTIVE_SHARD_SCHEMA,
        allow_empty=False,
    )
    previous, previous_archive = _previous_reference(
        current_snapshot_raw, generation
    )
    root = {
        "active_completed_task_ids": active_completed,
        "call_receipt_archive": dict(call_receipt_archive),
        "dispatch_attempts": dict(sorted(dispatch_attempts.items())),
        "generation": generation,
        "previous_generation": previous,
        "schema": SCHEMA_V3,
        "table_schema_sha256": table_schema_sha256(columns),
        "tables": active_tables,
        "terminal_shards": [reference for reference, _ in terminal_shards],
    }
    if current_layout != "legacy-inline":
        root["active_detail_summaries"] = active_detail_summaries
        root["active_shards"] = [
            reference for reference, _ in active_shards
        ]
        if current_layout != "legacy-active-detail":
            root["active_layout"] = ACTIVE_LAYOUT
    root_raw = canonical_bytes(root)
    if len(root_raw) > ROOT_CAP_BYTES:
        raise SnapshotCapacityError("SNAPSHOT_TOO_LARGE")
    return {
        "previous_archive": previous_archive,
        "root": root,
        "root_raw": root_raw,
        "shards": [
            {"reference": reference, "raw": raw}
            for reference, raw in [*terminal_shards, *active_shards]
        ],
    }


def _validate_reference_path(path: Any, expected_prefix: str) -> str:
    if not isinstance(path, str) or not path or "\\" in path:
        raise SnapshotCapacityError("SNAPSHOT_SHARD_PATH_INVALID")
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or path != pure.as_posix():
        raise SnapshotCapacityError("SNAPSHOT_SHARD_PATH_INVALID")
    if not path.startswith(expected_prefix):
        raise SnapshotCapacityError("SNAPSHOT_SHARD_PATH_INVALID")
    return path


def decode_v3(
    *,
    snapshot: Mapping[str, Any],
    snapshot_raw: bytes,
    columns: Mapping[str, Sequence[str]],
    read_reference: Callable[[str], bytes],
    list_generation_shards: Callable[[int], set[str]],
) -> dict[str, Any]:
    legacy_root = {
        "active_completed_task_ids",
        "call_receipt_archive",
        "dispatch_attempts",
        "generation",
        "previous_generation",
        "schema",
        "table_schema_sha256",
        "tables",
        "terminal_shards",
    }
    legacy_active_root = legacy_root | {
        "active_detail_summaries",
        "active_shards",
    }
    lifecycle_root = legacy_active_root | {"active_layout"}
    root_fields = set(snapshot)
    if root_fields == legacy_root:
        layout = "legacy-inline"
        detail_tables: Sequence[str] = ()
    elif root_fields == legacy_active_root:
        layout = "legacy-active-detail"
        detail_tables = LEGACY_ACTIVE_DETAIL_TABLES
    elif (
        root_fields == lifecycle_root
        and snapshot.get("active_layout") == ACTIVE_LAYOUT
    ):
        layout = ACTIVE_LAYOUT
        detail_tables = tuple(
            table for table in ACTIVE_DETAIL_TABLES if table in columns
        )
    else:
        raise SnapshotCapacityError("SNAPSHOT_INVALID")
    has_active_shards = layout != "legacy-inline"
    if (
        len(snapshot_raw) > ROOT_CAP_BYTES
        or snapshot.get("schema") != SCHEMA_V3
        or canonical_bytes(snapshot) != snapshot_raw
    ):
        raise SnapshotCapacityError("SNAPSHOT_INVALID")
    call_archive = snapshot["call_receipt_archive"]
    attempts = snapshot["dispatch_attempts"]
    if (
        not isinstance(call_archive, dict)
        or set(call_archive) != {"count", "root_sha256"}
        or isinstance(call_archive["count"], bool)
        or not isinstance(call_archive["count"], int)
        or call_archive["count"] < 0
        or not isinstance(call_archive["root_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", call_archive["root_sha256"])
        is None
        or not isinstance(attempts, dict)
        or not all(
            isinstance(key, str)
            and key
            and isinstance(value, int)
            and not isinstance(value, bool)
            and value >= 1
            for key, value in attempts.items()
        )
    ):
        raise SnapshotCapacityError("SNAPSHOT_INVALID")
    generation = snapshot["generation"]
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        raise SnapshotCapacityError("SNAPSHOT_INVALID")
    if snapshot["table_schema_sha256"] != table_schema_sha256(columns):
        raise SnapshotCapacityError("SNAPSHOT_TABLE_SCHEMA_INVALID")
    active_tables = snapshot["tables"]
    if not isinstance(active_tables, dict) or set(active_tables) != set(columns):
        raise SnapshotCapacityError("SNAPSHOT_TABLE_UNKNOWN")
    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in columns}
    terminal_tables: dict[str, list[dict[str, Any]]] = {
        name: [] for name in columns
    }
    active_detail_tables: dict[str, list[dict[str, Any]]] = {
        name: [] for name in detail_tables
    }
    for table, rows in active_tables.items():
        if not isinstance(rows, list):
            raise SnapshotCapacityError("SNAPSHOT_TABLE_INVALID")
        for values in rows:
            if not isinstance(values, list) or len(values) != len(columns[table]):
                raise SnapshotCapacityError("SNAPSHOT_COLUMN_UNKNOWN")
            tables[table].append(dict(zip(columns[table], values)))

    if has_active_shards and any(
        active_tables[table] for table in detail_tables
    ):
        raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")

    active_completed = snapshot["active_completed_task_ids"]
    if (
        not isinstance(active_completed, list)
        or not all(isinstance(item, str) and item for item in active_completed)
        or len(set(active_completed)) != len(active_completed)
    ):
        raise SnapshotCapacityError("SNAPSHOT_INVALID")
    completed = list(active_completed)
    recovery_worktrees: list[dict[str, str]] = []
    seen_records: set[bytes] = set()
    expected_paths: set[str] = set()

    def read_shard_records(
        references: Any,
        *,
        expected_schema: str,
        expected_kind: str,
        allow_no_references: bool,
    ) -> list[list[Any]]:
        if (
            not isinstance(references, list)
            or (not references and not allow_no_references)
        ):
            raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
        decoded: list[list[Any]] = []
        for expected_index, reference in enumerate(references):
            expected_fields = {
                "byte_size",
                "count",
                "generation",
                "index",
                "kind",
                "path",
                "schema",
                "sha256",
            }
            if not isinstance(reference, dict) or set(reference) != expected_fields:
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
            if (
                reference["schema"] != expected_schema
                or reference["kind"] != expected_kind
                or reference["generation"] != generation
                or reference["index"] != expected_index
                or isinstance(reference["count"], bool)
                or not isinstance(reference["count"], int)
                or reference["count"] < 0
                or (expected_kind == "active-detail" and reference["count"] == 0)
                or isinstance(reference["byte_size"], bool)
                or not isinstance(reference["byte_size"], int)
                or not 0 < reference["byte_size"] <= SHARD_CAP_BYTES
                or not isinstance(reference["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", reference["sha256"]) is None
            ):
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
            prefix = (
                ".devad/manager/loop-lite/snapshots/generations/"
                f"{generation}/shards/"
            )
            path = _validate_reference_path(reference["path"], prefix)
            if PurePosixPath(path).name != reference["sha256"] + ".json":
                raise SnapshotCapacityError("SNAPSHOT_SHARD_PATH_INVALID")
            if path in expected_paths:
                raise SnapshotCapacityError("SNAPSHOT_SHARD_DUPLICATE")
            expected_paths.add(path)
            raw = read_reference(path)
            if (
                len(raw) != reference["byte_size"]
                or len(raw) > SHARD_CAP_BYTES
                or sha256(raw) != reference["sha256"]
            ):
                raise SnapshotCapacityError("SNAPSHOT_SHARD_HASH_MISMATCH")
            try:
                shard = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID") from exc
            if canonical_bytes(shard) != raw or set(shard) != {
                "generation", "index", "kind", "records", "schema"
            }:
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
            records = shard["records"]
            if (
                shard["schema"] != expected_schema
                or shard["generation"] != generation
                or shard["index"] != expected_index
                or shard["kind"] != expected_kind
                or not isinstance(records, list)
                or len(records) != reference["count"]
            ):
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
            for record in records:
                encoded = canonical_bytes(record)
                if encoded in seen_records:
                    raise SnapshotCapacityError("SNAPSHOT_SHARD_DUPLICATE")
                seen_records.add(encoded)
                if (
                    not isinstance(record, list)
                    or len(record) not in {2, 3}
                ):
                    raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
                decoded.append(record)
        return decoded

    terminal_records = read_shard_records(
        snapshot["terminal_shards"],
        expected_schema=SHARD_SCHEMA,
        expected_kind="terminal-state",
        allow_no_references=False,
    )
    for record in terminal_records:
        if record[0] == "table" and len(record) == 3:
            table, values = record[1], record[2]
            if (
                table not in columns
                or not isinstance(values, list)
                or len(values) != len(columns[table])
            ):
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
            terminal_row = dict(zip(columns[table], values))
            terminal_tables[table].append(terminal_row)
        elif record[0] == "completed" and len(record) == 2:
            if (
                not isinstance(record[1], str)
                or not record[1]
                or record[1] in completed
            ):
                raise SnapshotCapacityError("SNAPSHOT_SHARD_DUPLICATE")
            completed.append(record[1])
        elif record[0] == "recovery" and len(record) == 2:
            values = record[1]
            if (
                not isinstance(values, list)
                or len(values) != 2
                or not all(isinstance(item, str) and item for item in values)
            ):
                raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")
            recovery_worktrees.append(
                {"worktree_id": values[0], "path": values[1]}
            )
        else:
            raise SnapshotCapacityError("SNAPSHOT_SHARD_INVALID")

    if has_active_shards:
        active_records = read_shard_records(
            snapshot["active_shards"],
            expected_schema=ACTIVE_SHARD_SCHEMA,
            expected_kind="active-detail",
            allow_no_references=True,
        )
        for record in active_records:
            if record[0] != "table" or len(record) != 3:
                raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
            table, values = record[1], record[2]
            if (
                table not in detail_tables
                or not isinstance(values, list)
                or len(values) != len(columns[table])
            ):
                raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
            active_detail_tables[table].append(
                dict(zip(columns[table], values))
            )

        if not isinstance(snapshot["active_detail_summaries"], dict):
            raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")

    inline_tables = {table: list(rows) for table, rows in tables.items()}
    if has_active_shards:
        for table in detail_tables:
            tables[table].extend(active_detail_tables[table])
    for table in columns:
        if table == "dispatches":
            tables[table] = [*terminal_tables[table], *tables[table]]
        else:
            tables[table].extend(terminal_tables[table])

    active_state = _active_sets(tables)
    for table in columns:
        if any(not _is_active(table, row, active_state) for row in inline_tables[table]):
            raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
        if any(_is_active(table, row, active_state) for row in terminal_tables[table]):
            raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
    for table in detail_tables:
        if any(
            not _is_active(table, row, active_state)
            for row in active_detail_tables[table]
        ):
            raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")

    if has_active_shards:
        summaries = snapshot["active_detail_summaries"]
        if layout == "legacy-active-detail":
            if set(summaries) != set(LEGACY_ACTIVE_DETAIL_TABLES):
                raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
            active_task_ids = active_state["tasks"]
            for table in LEGACY_ACTIVE_DETAIL_TABLES:
                counts: dict[str, int] = {}
                for row in active_detail_tables[table]:
                    task_id = row["task_id"]
                    if not isinstance(task_id, str) or task_id not in active_task_ids:
                        raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
                    counts[task_id] = counts.get(task_id, 0) + 1
                expected_summary = [
                    [task_id, count] for task_id, count in sorted(counts.items())
                ]
                if summaries[table] != expected_summary or any(
                    not isinstance(item, list)
                    or len(item) != 2
                    or isinstance(item[1], bool)
                    or not isinstance(item[1], int)
                    or item[1] < 1
                    for item in summaries[table]
                ):
                    raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")
        else:
            expected_fields = {"counts", "dispatches", "tasks", "work_orders"}
            counts = summaries.get("counts")
            if (
                set(summaries) != expected_fields
                or not isinstance(counts, list)
                or any(
                    not isinstance(item, list)
                    or len(item) != 2
                    or item[0] not in detail_tables
                    or isinstance(item[1], bool)
                    or not isinstance(item[1], int)
                    or item[1] < 1
                    for item in counts
                )
                or len({item[0] for item in counts}) != len(counts)
            ):
                raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")

            def compact_rows(
                table: str, selected: Sequence[str]
            ) -> list[list[Any]]:
                return sorted(
                    [
                        [row[column] for column in selected]
                        for row in active_detail_tables[table]
                    ],
                    key=canonical_bytes,
                )

            expected_summaries = {
                "counts": [
                    [table, len(active_detail_tables[table])]
                    for table in detail_tables
                    if active_detail_tables[table]
                ],
                "dispatches": compact_rows(
                    "dispatches",
                    ("dispatch_id", "task_id", "sender_id", "target_id", "status"),
                ),
                "tasks": compact_rows(
                    "tasks", ("task_id", "worker_id", "worktree_id", "status")
                ),
                "work_orders": compact_rows(
                    "work_orders",
                    ("work_order_id", "task_id", "worker_id", "program_id", "status"),
                ),
            }
            if summaries != expected_summaries:
                raise SnapshotCapacityError("SNAPSHOT_ACTIVE_DETAIL_INVALID")

    actual_paths = list_generation_shards(generation)
    if actual_paths != expected_paths:
        raise SnapshotCapacityError("SNAPSHOT_SHARD_EXTRA_OR_MISSING")

    previous = snapshot["previous_generation"]
    if previous is not None:
        expected_previous = {"byte_size", "generation", "path", "schema", "sha256"}
        if not isinstance(previous, dict) or set(previous) != expected_previous:
            raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID")
        path = _validate_reference_path(
            previous["path"],
            ".devad/manager/loop-lite/snapshots/roots/",
        )
        if (
            previous["schema"]
            not in {"x9-loop-lite-snapshot-v1", SCHEMA_V2, SCHEMA_V3}
            or isinstance(previous["generation"], bool)
            or not isinstance(previous["generation"], int)
            or isinstance(previous["byte_size"], bool)
            or not isinstance(previous["byte_size"], int)
            or not 0 < previous["byte_size"] <= ROOT_CAP_BYTES
            or previous["generation"] >= generation
            or re.fullmatch(r"[0-9a-f]{64}", previous["sha256"]) is None
            or PurePosixPath(path).name != previous["sha256"] + ".json"
        ):
            raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID")
        raw = read_reference(path)
        try:
            parsed = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID") from exc
        if (
            len(raw) != previous["byte_size"]
            or sha256(raw) != previous["sha256"]
            or parsed.get("schema") != previous["schema"]
            or parsed.get("generation") != previous["generation"]
            or (
                _legacy_v1_bytes(parsed)
                if previous["schema"] == "x9-loop-lite-snapshot-v1"
                else canonical_bytes(parsed)
            )
            != raw
        ):
            raise SnapshotCapacityError("SNAPSHOT_PREVIOUS_INVALID")

    return {
        "call_receipt_archive": snapshot["call_receipt_archive"],
        "completed_task_ids": completed,
        "dispatch_attempts": snapshot["dispatch_attempts"],
        "generation": generation,
        "recovery_worktrees": recovery_worktrees,
        "tables": tables,
    }
