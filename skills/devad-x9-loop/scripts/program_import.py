#!/usr/bin/env python3
"""Deterministic, content-free V7 program import inventory helpers.

The inventory reads file bytes only in bounded chunks for hashing.  File content
is never placed in an inventory row, coverage summary, packet, or CLI output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import numbers
import ntpath
import os
import stat
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROGRAM_PACKET_MAX_BYTES = 16 * 1024
FEATURE_PACKET_MAX_BYTES = 32 * 1024
COVERAGE_SUMMARY_MAX_BYTES = 16 * 1024
COVERAGE_SHARD_MAX_BYTES = 64 * 1024

CLASSIFICATIONS = frozenset(
    {"IMPORTED", "POINTER", "STALE", "CONFLICT", "REJECTED", "NOT_RELEVANT"}
)
INVENTORY_FIELDS = frozenset(
    {
        "path",
        "sha256",
        "size",
        "source_class",
        "classification",
        "feature_ids",
        "chosen_fact_owner",
        "reason",
    }
)
_METADATA_FIELDS = INVENTORY_FIELDS - {"path", "sha256", "size"}
_SHA256_HEX = frozenset("0123456789abcdef")
_READ_CHUNK_BYTES = 1024 * 1024

# This order is the durable precedence recorded in the V7 adoption packet.
_SOURCE_PRECEDENCE_GROUPS = (
    frozenset({"OWNER_MESSAGE", "OWNER_PACKET", "OWNER_ATTACHMENT"}),
    frozenset(
        {
            "CURRENT_GIT",
            "CURRENT_WORKTREE",
            "CURRENT_RUNTIME",
            "CURRENT_DEPLOY_PROOF",
            "CURRENT_BROWSER_PROOF",
            "CURRENT_FILESYSTEM",
        }
    ),
    frozenset({"FEATURE_CONTRACT", "ANSWERED_DECISION", "OWNER_DECISION"}),
    frozenset({"WORKER_RECEIPT"}),
    frozenset({"MANAGER_FACT", "LOCAL_WORK_LEDGER", "LOOP_LITE_STATE"}),
    frozenset({"HISTORICAL_HANDOFF", "OLD_LOOP_STATE", "HISTORICAL_EVIDENCE", "LEGACY"}),
    frozenset({"CHAT_HISTORY"}),
)


class ProgramImportError(ValueError):
    """Base class for deterministic import contract failures."""


class CanonicalEncodingError(ProgramImportError):
    pass


class PathSafetyError(ProgramImportError):
    pass


class PathEscapeError(PathSafetyError):
    pass


class PathCollisionError(PathSafetyError):
    pass


class InventoryConflictError(ProgramImportError):
    pass


class InventoryOmissionError(ProgramImportError):
    pass


class RootDriftError(ProgramImportError):
    pass


class PacketTooLargeError(ProgramImportError):
    pass


class ShardTooLargeError(PacketTooLargeError):
    pass


def _nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _validate_json_value(value: Any, seen: set[int] | None = None) -> None:
    if isinstance(value, float):
        raise CanonicalEncodingError("canonical JSON forbids floats and non-finite values")
    if isinstance(value, numbers.Number) and not isinstance(value, (int, bool)):
        raise CanonicalEncodingError("canonical JSON numeric values must be integers")
    if value is None or isinstance(value, (str, int, bool)):
        return

    if seen is None:
        seen = set()
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in seen:
            raise CanonicalEncodingError("canonical JSON forbids cyclic containers")
        seen.add(identity)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise CanonicalEncodingError("canonical JSON object keys must be strings")
                _validate_json_value(item, seen)
        finally:
            seen.remove(identity)
        return
    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in seen:
            raise CanonicalEncodingError("canonical JSON forbids cyclic containers")
        seen.add(identity)
        try:
            for item in value:
                _validate_json_value(item, seen)
        finally:
            seen.remove(identity)
        return
    raise CanonicalEncodingError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_json_bytes(payload: Any) -> bytes:
    """Return sorted compact UTF-8 JSON with exactly one trailing LF."""

    _validate_json_value(payload)
    try:
        text = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CanonicalEncodingError(str(exc)) from exc
    return (text + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    """Encode objects in the supplied order as canonical JSONL."""

    encoded: list[bytes] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise CanonicalEncodingError("each JSONL record must be an object")
        encoded.append(canonical_json_bytes(dict(row)))
    return b"".join(encoded)


def canonical_repo_path(path: os.PathLike[str] | str, root: os.PathLike[str] | str | None = None) -> str:
    """Canonicalize a repository-relative path and optionally prove containment."""

    raw = os.fspath(path)
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise PathSafetyError("path must be a non-empty text path without NUL")
    normalized = _nfc(raw).replace("\\", "/")
    drive, _ = ntpath.splitdrive(normalized)
    if drive or normalized.startswith("/"):
        raise PathSafetyError(f"absolute path is forbidden: {raw!r}")

    parts: list[str] = []
    for part in normalized.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            raise PathSafetyError(f"parent traversal is forbidden: {raw!r}")
        parts.append(part)
    if not parts:
        raise PathSafetyError("repository-relative file path cannot be empty")
    canonical = "/".join(parts)

    if root is not None:
        root_path = Path(root).resolve(strict=True)
        candidate = Path(root) / Path(*parts)
        _assert_contained(root_path, candidate)
    return canonical


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _assert_contained(root: Path, candidate: Path) -> Path:
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PathSafetyError(f"cannot resolve durable path {candidate}: {exc}") from exc
    if not _is_within(resolved, root):
        raise PathEscapeError(f"linked or reparse path escapes source root: {candidate}")
    return resolved


def is_reparse_point(path: os.PathLike[str] | str) -> bool:
    """Return true for a POSIX symlink or Windows reparse point."""

    metadata = os.lstat(path)
    attributes = int(getattr(metadata, "st_file_attributes", 0))
    reparse_flag = int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    return stat.S_ISLNK(metadata.st_mode) or bool(attributes & reparse_flag)


def _source_paths(root: Path) -> list[tuple[str, Path]]:
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise PathSafetyError(f"inventory root is not a directory: {root}")

    discovered: list[tuple[str, Path]] = []
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise PathSafetyError(f"cannot enumerate durable directory {directory}: {exc}") from exc
        entries.sort(key=lambda entry: _nfc(entry.name).encode("utf-8"))
        child_directories: list[Path] = []
        for entry in entries:
            candidate = Path(entry.path)
            relative = os.path.relpath(candidate, root)
            canonical = canonical_repo_path(relative)
            resolved = _assert_contained(resolved_root, candidate)
            try:
                linked = is_reparse_point(candidate)
            except OSError as exc:
                raise PathSafetyError(f"cannot inspect durable path {candidate}: {exc}") from exc

            if linked:
                if resolved.is_file():
                    discovered.append((canonical, candidate))
                # Do not traverse a linked directory; its physical target is either
                # inventoried at its real in-root path or is outside and rejected.
                continue
            if entry.is_dir(follow_symlinks=False):
                child_directories.append(candidate)
            elif entry.is_file(follow_symlinks=False):
                discovered.append((canonical, candidate))
        stack.extend(reversed(child_directories))
    discovered.sort(key=lambda item: item[0].encode("utf-8"))
    return discovered


def _stream_sha256(path: Path, root: Path) -> tuple[str, int]:
    resolved_root = root.resolve(strict=True)
    before_target = _assert_contained(resolved_root, path)
    try:
        before = before_target.stat()
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(_READ_CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
        after_target = _assert_contained(resolved_root, path)
        after = after_target.stat()
    except OSError as exc:
        raise RootDriftError(f"durable file changed or became unreadable: {path}: {exc}") from exc

    identity_before = (before_target, before.st_size, before.st_mtime_ns, before.st_ino)
    identity_after = (after_target, after.st_size, after.st_mtime_ns, after.st_ino)
    if identity_before != identity_after or size != after.st_size:
        raise RootDriftError(f"durable file changed while hashing: {path}")
    return digest.hexdigest(), size


def _normalized_metadata(
    metadata_by_path: Mapping[str, Mapping[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    folded: dict[str, str] = {}
    for raw_path, raw_metadata in (metadata_by_path or {}).items():
        path = canonical_repo_path(raw_path)
        collision_key = path.casefold()
        if collision_key in folded and folded[collision_key] != path:
            raise PathCollisionError(f"metadata path case-fold collision: {folded[collision_key]} / {path}")
        if path in normalized:
            raise InventoryConflictError(f"duplicate metadata path: {path}")
        if not isinstance(raw_metadata, Mapping):
            raise InventoryConflictError(f"metadata for {path} must be an object")
        extra = set(raw_metadata) - _METADATA_FIELDS
        if extra:
            raise InventoryConflictError(f"metadata for {path} overrides mechanical fields: {sorted(extra)}")
        folded[collision_key] = path
        normalized[path] = dict(raw_metadata)
    return normalized


def inventory_durable_files(
    root: os.PathLike[str] | str,
    *,
    metadata_by_path: Mapping[str, Mapping[str, Any]] | None = None,
    default_source_class: str = "CURRENT_FILESYSTEM",
    default_classification: str = "IMPORTED",
    default_fact_owner: str = "filesystem",
    default_reason: str = "mechanical durable-file inventory",
) -> list[dict[str, Any]]:
    """Mechanically inventory every regular durable file below ``root``."""

    root_path = Path(root)
    metadata = _normalized_metadata(metadata_by_path)
    seen_metadata: set[str] = set()
    rows: list[dict[str, Any]] = []
    for path, disk_path in _source_paths(root_path):
        sha256, size = _stream_sha256(disk_path, root_path)
        overrides = metadata.get(path, {})
        if path in metadata:
            seen_metadata.add(path)
        rows.append(
            {
                "path": path,
                "sha256": sha256,
                "size": size,
                "source_class": overrides.get("source_class", default_source_class),
                "classification": overrides.get("classification", default_classification),
                "feature_ids": overrides.get("feature_ids", []),
                "chosen_fact_owner": overrides.get("chosen_fact_owner", default_fact_owner),
                "reason": overrides.get("reason", default_reason),
            }
        )

    missing_metadata = sorted(set(metadata) - seen_metadata, key=lambda item: item.encode("utf-8"))
    if missing_metadata:
        raise InventoryOmissionError(f"declared durable paths are missing: {missing_metadata}")
    return validate_inventory_rows(rows)


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and set(value) <= _SHA256_HEX
    )


def validate_inventory_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Validate, normalize, collision-check, and byte-sort inventory rows."""

    validated: list[dict[str, Any]] = []
    exact_paths: set[str] = set()
    folded_paths: dict[str, str] = {}
    for raw_row in rows:
        if not isinstance(raw_row, Mapping):
            raise InventoryConflictError("inventory row must be an object")
        if set(raw_row) != INVENTORY_FIELDS:
            missing = sorted(INVENTORY_FIELDS - set(raw_row))
            extra = sorted(set(raw_row) - INVENTORY_FIELDS)
            raise InventoryConflictError(f"inventory row fields mismatch; missing={missing}; extra={extra}")

        path = canonical_repo_path(raw_row["path"])
        folded = path.casefold()
        if path in exact_paths:
            raise InventoryConflictError(f"duplicate inventory path: {path}")
        if folded in folded_paths and folded_paths[folded] != path:
            raise PathCollisionError(f"inventory path case-fold collision: {folded_paths[folded]} / {path}")
        if not _valid_sha256(raw_row["sha256"]):
            raise InventoryConflictError(f"invalid SHA-256 for {path}")
        size = raw_row["size"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise InventoryConflictError(f"invalid byte size for {path}")
        classification = raw_row["classification"]
        if classification not in CLASSIFICATIONS:
            raise InventoryConflictError(f"invalid classification for {path}: {classification!r}")
        source_class = raw_row["source_class"]
        owner = raw_row["chosen_fact_owner"]
        reason = raw_row["reason"]
        if not isinstance(source_class, str) or not source_class.strip():
            raise InventoryConflictError(f"source_class must be non-empty for {path}")
        if not isinstance(owner, str) or not isinstance(reason, str):
            raise InventoryConflictError(f"fact owner and reason must be strings for {path}")
        feature_ids = raw_row["feature_ids"]
        if not isinstance(feature_ids, (list, tuple)) or any(
            not isinstance(item, str) or not item for item in feature_ids
        ):
            raise InventoryConflictError(f"feature_ids must be non-empty strings for {path}")
        normalized_features = sorted((_nfc(item) for item in feature_ids), key=lambda item: item.encode("utf-8"))
        if len(set(normalized_features)) != len(normalized_features):
            raise InventoryConflictError(f"duplicate feature_ids for {path}")

        exact_paths.add(path)
        folded_paths[folded] = path
        validated.append(
            {
                "path": path,
                "sha256": raw_row["sha256"],
                "size": size,
                "source_class": _nfc(source_class.strip()),
                "classification": classification,
                "feature_ids": normalized_features,
                "chosen_fact_owner": _nfc(owner),
                "reason": _nfc(reason),
            }
        )
    validated.sort(key=lambda row: row["path"].encode("utf-8"))
    return validated


def inventory_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return canonical_jsonl_bytes(validate_inventory_rows(rows))


def inventory_root_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    return hashlib.sha256(inventory_jsonl_bytes(rows)).hexdigest()


def shard_inventory(
    rows: Iterable[Mapping[str, Any]], *, max_bytes: int = COVERAGE_SHARD_MAX_BYTES
) -> list[bytes]:
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes <= 0:
        raise ShardTooLargeError("shard maximum must be a positive integer")
    if max_bytes > COVERAGE_SHARD_MAX_BYTES:
        raise ShardTooLargeError("coverage shards may not exceed 64 KB")

    shards: list[bytes] = []
    current = bytearray()
    for row in validate_inventory_rows(rows):
        line = canonical_json_bytes(row)
        if len(line) > max_bytes:
            raise ShardTooLargeError(f"one inventory row exceeds shard cap: {row['path']}")
        if current and len(current) + len(line) > max_bytes:
            shards.append(bytes(current))
            current.clear()
        current.extend(line)
    if current:
        shards.append(bytes(current))
    return shards


def build_coverage_summary(
    rows: Iterable[Mapping[str, Any]],
    shards: Sequence[bytes],
    *,
    required_source_classes: Iterable[str] = (),
    conflicts: Sequence[Mapping[str, Any] | str] = (),
) -> bytes:
    normalized_rows = validate_inventory_rows(rows)
    exact_jsonl = canonical_jsonl_bytes(normalized_rows)
    if any(not isinstance(shard, bytes) for shard in shards):
        raise InventoryConflictError("coverage shards must be bytes")
    if any(len(shard) > COVERAGE_SHARD_MAX_BYTES for shard in shards):
        raise ShardTooLargeError("coverage shard exceeds 64 KB")
    if b"".join(shards) != exact_jsonl:
        raise InventoryConflictError("coverage shards do not exactly reconstruct inventory JSONL")

    source_counts = Counter(row["source_class"] for row in normalized_rows)
    classification_counts = Counter(row["classification"] for row in normalized_rows)
    required = sorted({_nfc(item) for item in required_source_classes}, key=lambda item: item.encode("utf-8"))
    missing_required = [item for item in required if source_counts[item] == 0]
    feature_ids = {feature for row in normalized_rows for feature in row["feature_ids"]}
    descriptors = [
        {
            "index": index,
            "row_count": shard.count(b"\n"),
            "sha256": hashlib.sha256(shard).hexdigest(),
            "size": len(shard),
        }
        for index, shard in enumerate(shards)
    ]
    payload = {
        "classification_counts": dict(classification_counts),
        "conflicts": list(conflicts),
        "feature_count": len(feature_ids),
        "file_count": len(normalized_rows),
        "inventory_jsonl_bytes": len(exact_jsonl),
        "inventory_root_sha256": hashlib.sha256(exact_jsonl).hexdigest(),
        "missing_required_source_classes": missing_required,
        "schema": "x9-loop-import-coverage-v1",
        "shard_count": len(shards),
        "shards": descriptors,
        "source_class_counts": dict(source_counts),
    }
    encoded = canonical_json_bytes(payload)
    if len(encoded) > COVERAGE_SUMMARY_MAX_BYTES:
        raise PacketTooLargeError("coverage summary exceeds 16 KB")
    return encoded


def verify_inventory(
    root: os.PathLike[str] | str,
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_root_sha256: str | None = None,
) -> str:
    """Reinventory a source root and fail on omission, conflict, or drift."""

    expected_rows = validate_inventory_rows(rows)
    expected_hash = hashlib.sha256(canonical_jsonl_bytes(expected_rows)).hexdigest()
    if expected_root_sha256 is not None and expected_hash != expected_root_sha256:
        raise RootDriftError(
            f"declared inventory root changed: expected {expected_root_sha256}, got {expected_hash}"
        )

    metadata = {
        row["path"]: {field: row[field] for field in _METADATA_FIELDS}
        for row in expected_rows
    }
    try:
        current_rows = inventory_durable_files(root, metadata_by_path=metadata)
    except InventoryOmissionError as exc:
        raise InventoryOmissionError(str(exc)) from exc

    expected_paths = {row["path"] for row in expected_rows}
    current_paths = {row["path"] for row in current_rows}
    missing = sorted(expected_paths - current_paths, key=lambda item: item.encode("utf-8"))
    unrecorded = sorted(current_paths - expected_paths, key=lambda item: item.encode("utf-8"))
    if missing or unrecorded:
        raise InventoryOmissionError(f"inventory coverage changed; missing={missing}; unrecorded={unrecorded}")
    if current_rows != expected_rows:
        raise RootDriftError("durable file hashes or sizes changed without reconciliation")
    current_hash = hashlib.sha256(canonical_jsonl_bytes(current_rows)).hexdigest()
    if current_hash != expected_hash:
        raise RootDriftError(f"inventory root drift: expected {expected_hash}, got {current_hash}")
    return current_hash


def _normalize_source_class(source_class: str) -> str:
    if not isinstance(source_class, str) or not source_class.strip():
        raise InventoryConflictError("source_class must be a non-empty string")
    return _nfc(source_class).strip().upper().replace("-", "_").replace(" ", "_")


def source_precedence(source_class: str) -> int:
    normalized = _normalize_source_class(source_class)
    for rank, group in enumerate(_SOURCE_PRECEDENCE_GROUPS):
        if normalized in group:
            return rank
    return len(_SOURCE_PRECEDENCE_GROUPS)


def choose_precedent_source(candidates: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Choose the highest-precedence fact, failing closed on an equal-rank conflict."""

    choices = [dict(candidate) for candidate in candidates]
    if not choices:
        raise InventoryConflictError("at least one source candidate is required")
    for candidate in choices:
        if "source_class" not in candidate:
            raise InventoryConflictError("source candidate is missing source_class")
    best_rank = min(source_precedence(candidate["source_class"]) for candidate in choices)
    winners = [
        candidate for candidate in choices if source_precedence(candidate["source_class"]) == best_rank
    ]
    if len(winners) == 1:
        return winners[0]

    signatures = {
        (
            candidate.get("path"),
            candidate.get("sha256", candidate.get("value_sha256")),
            candidate.get("size"),
        )
        for candidate in winners
    }
    if len(signatures) != 1:
        raise InventoryConflictError("equal-precedence sources disagree")
    return min(winners, key=canonical_json_bytes)


def _build_packet(
    payload: Mapping[str, Any] | None,
    fields: Mapping[str, Any],
    *,
    schema: str,
    maximum: int,
) -> bytes:
    if payload is not None and not isinstance(payload, Mapping):
        raise CanonicalEncodingError("packet payload must be an object")
    merged = dict(payload or {})
    overlap = set(merged) & set(fields)
    if overlap:
        raise InventoryConflictError(f"packet fields supplied twice: {sorted(overlap)}")
    merged.update(fields)
    declared_schema = merged.setdefault("schema", schema)
    if declared_schema != schema:
        raise InventoryConflictError(f"packet schema must be {schema}")
    encoded = canonical_json_bytes(merged)
    if len(encoded) > maximum:
        raise PacketTooLargeError(f"{schema} exceeds {maximum} bytes")
    return encoded


def build_program_packet(
    payload: Mapping[str, Any] | None = None, **fields: Any
) -> bytes:
    return _build_packet(
        payload,
        fields,
        schema="x9-loop-program-v1",
        maximum=PROGRAM_PACKET_MAX_BYTES,
    )


def build_feature_packet(
    payload: Mapping[str, Any] | None = None, **fields: Any
) -> bytes:
    return _build_packet(
        payload,
        fields,
        schema="x9-loop-feature-v1",
        maximum=FEATURE_PACKET_MAX_BYTES,
    )


def build_import_artifacts(
    root: os.PathLike[str] | str,
    *,
    metadata_by_path: Mapping[str, Mapping[str, Any]] | None = None,
    required_source_classes: Iterable[str] = (),
) -> dict[str, Any]:
    """Build one deterministic in-memory inventory artifact set."""

    rows = inventory_durable_files(root, metadata_by_path=metadata_by_path)
    inventory = inventory_jsonl_bytes(rows)
    shards = shard_inventory(rows)
    summary = build_coverage_summary(
        rows,
        shards,
        required_source_classes=required_source_classes,
    )
    return {
        "coverage_summary": summary,
        "inventory_jsonl": inventory,
        "inventory_root_sha256": hashlib.sha256(inventory).hexdigest(),
        "rows": rows,
        "shards": shards,
    }


def import_program(
    root: os.PathLike[str] | str,
    *,
    metadata_by_path: Mapping[str, Mapping[str, Any]] | None = None,
    required_source_classes: Iterable[str] = (),
) -> dict[str, Any]:
    """Compatibility name for the high-level deterministic import operation."""

    return build_import_artifacts(
        root,
        metadata_by_path=metadata_by_path,
        required_source_classes=required_source_classes,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a content-free V7 import coverage summary")
    parser.add_argument("root", type=Path, help="durable source root to inventory")
    args = parser.parse_args(argv)
    artifacts = build_import_artifacts(args.root)
    sys.stdout.buffer.write(artifacts["coverage_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
