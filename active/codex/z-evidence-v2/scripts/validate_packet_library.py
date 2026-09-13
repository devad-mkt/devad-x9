#!/usr/bin/env python3
"""Validate the structural contract of an evidence-to-implementation library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


EXPECTED_FILES = {
    "01-SURFACES-CONTROLS-AND-STATES.md",
    "02-SETTINGS-PERMISSIONS-AND-CONDITIONS.md",
    "03-JOURNEYS-INTEGRATIONS-ERRORS-AND-RECOVERY.md",
    "04-NATIVE-FRONTEND-BACKEND-AND-TEST-MAP.md",
    "05-MEGA-SPEC-GAPS-AND-IMPLEMENTATION-CONTRACT.md",
}
EXCLUDED_CHANNEL_NAMES = {"line", "viber", "wechat", "zalo"}
REQUIRED_MARKERS = ("Author:", "Table of Contents")
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer-token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I),
    "generic-secret": re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\b"
        r"\s*[:=]\s*[\"']?"
        r"(?!(?:\[[^\]]*(?:REDACTED|NOT_(?:READ|CAPTURED))[^\]]*\]))\S{8,}"
    ),
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\((?:<([^>]+)>|([^)]+))\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected-packets", type=int)
    parser.add_argument(
        "--packet-index",
        type=Path,
        help=(
            "JSON file containing packet_directories. Use when the output root "
            "also retains historical or superseded packet folders."
        ),
    )
    parser.add_argument("--requirement-ledger", type=Path)
    parser.add_argument("--expected-requirements", type=int)
    return parser.parse_args()


def is_packet(directory: Path) -> bool:
    names = {path.name for path in directory.glob("*.md")}
    return bool(EXPECTED_FILES & names)


def local_link_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for match in MARKDOWN_LINK.finditer(text):
        target = (match.group(1) or match.group(2)).strip().split("#", 1)[0]
        if not target or "://" in target or target.startswith(("mailto:", "#", "[")):
            continue
        if any(marker in target for marker in ("[", "]", "*")):
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"{path}: unresolved local link: {target}")
    return errors


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return [f"{path}: not UTF-8"]
    if not text.endswith("\n"):
        errors.append(f"{path}: missing final newline")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"{path}: missing {marker}")
    for category, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            errors.append(f"{path}: possible {category}")
    errors.extend(local_link_errors(path, text))
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: output root does not exist: {root}")
        return 2

    errors: list[str] = []
    if args.packet_index is not None:
        packet_index_path = args.packet_index.resolve()
        try:
            packet_index = json.loads(packet_index_path.read_text(encoding="utf-8"))
            directory_names = packet_index.get("packet_directories")
            if not isinstance(directory_names, list) or not all(
                isinstance(name, str) and name for name in directory_names
            ):
                raise ValueError("packet_directories must be a non-empty string list")
            packet_dirs = [root / name for name in directory_names]
            missing_directories = [
                str(directory) for directory in packet_dirs if not directory.is_dir()
            ]
            if missing_directories:
                errors.append(
                    f"{packet_index_path}: missing packet directories "
                    f"{missing_directories}"
                )
            packet_dirs = sorted(
                directory for directory in packet_dirs if directory.is_dir()
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{packet_index_path}: invalid packet index: {exc}")
            packet_dirs = []
    else:
        packet_dirs = sorted(
            directory
            for directory in root.rglob("*")
            if directory.is_dir() and is_packet(directory)
        )

    if args.expected_packets is not None and len(packet_dirs) != args.expected_packets:
        errors.append(
            f"{root}: expected {args.expected_packets} packets, found {len(packet_dirs)}"
        )

    for directory in packet_dirs:
        names = {path.name for path in directory.glob("*.md")}
        if names != EXPECTED_FILES:
            errors.append(
                f"{directory}: missing={sorted(EXPECTED_FILES - names)} "
                f"extra={sorted(names - EXPECTED_FILES)}"
            )
        parts = {part.lower() for part in directory.parts}
        excluded = sorted(parts & EXCLUDED_CHANNEL_NAMES)
        if excluded:
            errors.append(f"{directory}: excluded channel folder present: {excluded}")
        for path in sorted(directory.glob("*.md")):
            errors.extend(validate_file(path))

    if args.requirement_ledger is not None:
        ledger_path = args.requirement_ledger.resolve()
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{ledger_path}: invalid requirement ledger: {exc}")
        else:
            requirements = ledger.get("requirements")
            if not isinstance(requirements, list):
                errors.append(f"{ledger_path}: requirements must be a list")
                requirements = []
            if (
                args.expected_requirements is not None
                and len(requirements) != args.expected_requirements
            ):
                errors.append(
                    f"{ledger_path}: expected {args.expected_requirements} "
                    f"requirements, found {len(requirements)}"
                )
            required_fields = {
                "id",
                "requirement",
                "sources_or_actions",
                "artifact_rows",
                "gate",
                "status",
                "evidence_ids",
                "decision",
                "proof_or_blocker",
            }
            seen_ids: set[str] = set()
            for index, row in enumerate(requirements):
                if not isinstance(row, dict):
                    errors.append(f"{ledger_path}: row {index} is not an object")
                    continue
                missing = required_fields - row.keys()
                if missing:
                    errors.append(
                        f"{ledger_path}: row {index} missing {sorted(missing)}"
                    )
                requirement_id = row.get("id")
                if not isinstance(requirement_id, str) or not re.fullmatch(
                    r"[A-Z]+-\d{3}", requirement_id
                ):
                    errors.append(
                        f"{ledger_path}: row {index} has invalid id {requirement_id!r}"
                    )
                elif requirement_id in seen_ids:
                    errors.append(f"{ledger_path}: duplicate id {requirement_id}")
                else:
                    seen_ids.add(requirement_id)
                for field in ("sources_or_actions", "artifact_rows", "evidence_ids"):
                    if not isinstance(row.get(field), list):
                        errors.append(
                            f"{ledger_path}: {requirement_id or index} "
                            f"{field} must be a list"
                        )
                if row.get("status") not in {
                    "SATISFIED",
                    "SUPERSEDED_BY_OWNER",
                    "NOT_APPLICABLE_WITH_PROOF",
                    "UNKNOWN",
                    "BLOCKED",
                }:
                    errors.append(
                        f"{ledger_path}: {requirement_id or index} invalid status"
                    )
                if row.get("decision") not in {
                    "REUSE",
                    "EXTEND",
                    "NEW",
                    "OWNER_DECISION",
                    "DROP",
                    "UNKNOWN",
                }:
                    errors.append(
                        f"{ledger_path}: {requirement_id or index} invalid decision"
                    )

    print(f"root={root}")
    print(f"packets={len(packet_dirs)}")
    print(f"reports={sum(len(list(directory.glob('*.md'))) for directory in packet_dirs)}")
    print(f"errors={len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
