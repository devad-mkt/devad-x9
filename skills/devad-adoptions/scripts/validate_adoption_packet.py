#!/usr/bin/env python3
"""Validate a Devad adoption evidence packet.

This script validates adoption packets, not skill folders. It checks packet
shape, source/local control parity, action contracts, PASS proof rows, adoption
cap violations, risky done claims, and obvious secret leakage.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


REQUIRED_PACKET_FILES = [
    "MANIFEST.md",
    "TASK.md",
    "source-controls.json",
    "local-controls.json",
    "parity-matrix.json",
    "action-contracts.json",
    "browser-proof.json",
    "backend-proof.json",
    "progress-ledger.json",
    "proof-checklist.md",
]

TEXT_EXTENSIONS = {
    ".csv",
    ".html",
    ".json",
    ".md",
    ".php",
    ".ps1",
    ".py",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(?:OPENROUTER|RUNWARE|OPENAI|ANTHROPIC)_[A-Z0-9_]*(?:KEY|SECRET|TOKEN)\b", re.I),
    re.compile(
        r"\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password|oauth[_-]?code)\b"
        r"\s*(?:=|:|=>)\s*['\"]?(?!REDACTED|redacted|xxxxx|xxxx|placeholder|example|none|null|\[redacted\])"
        r"[A-Za-z0-9_./+=:-]{8,}",
        re.I,
    ),
]


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def load_json(path: Path, errors: list[str], *, required: bool = True) -> Any:
    if not path.exists():
        if required:
            errors.append(f"Missing required file: {path.name}")
        return []

    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path.name}: {exc}")
        return []


def normalize_rows(data: Any, preferred_keys: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in preferred_keys:
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if all(isinstance(value, dict) for value in data.values()):
            return [value for value in data.values() if isinstance(value, dict)]
    return []


def truthy_proof(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, str) and value.strip().lower() in {"no", "none", "false", "missing", "blocked", "todo"}:
        return False
    return True


def find_screenshots(files: list[Path], keyword: str) -> list[Path]:
    return [
        path
        for path in files
        if path.suffix.lower() in SCREENSHOT_EXTENSIONS and keyword.lower() in path.name.lower()
    ]


def secret_findings(root: Path, text_files: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in text_files:
        for index, line in enumerate(read_text(path).splitlines(), start=1):
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel(path, root)}:{index}: secret-like string")
                    break
    return findings


def risky_done_claims(root: Path, text_files: list[Path]) -> list[str]:
    claims: list[str] = []
    pattern = re.compile(
        r"\b(?:status|result|verdict|final|overall)\s*(?:=|:|-)?\s*(?:PASS|DONE|COMPLETE|COMPLETED)\b"
        r"|\bready to merge\b"
        r"|\b(?:is|called|mark(?:ed)?)\s+(?:production parity|done|complete)\b",
        re.I,
    )
    for path in text_files:
        for index, line in enumerate(read_text(path).splitlines(), start=1):
            if pattern.search(line):
                claims.append(f"{rel(path, root)}:{index}: done/PASS-style claim must be backed by progress-ledger proof")
    return claims


def validate_required_files(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_PACKET_FILES:
        if not (root / name).is_file():
            errors.append(f"Missing required packet file: {name}")


def validate_screenshots(files: list[Path], errors: list[str]) -> None:
    if not find_screenshots(files, "source"):
        errors.append("Missing source screenshot artifact")
    if not find_screenshots(files, "local"):
        errors.append("Missing local screenshot artifact")


def control_key(row: dict[str, Any]) -> str:
    return str(row.get("key") or row.get("control_key") or row.get("id") or "").strip()


def is_interactive(row: dict[str, Any]) -> bool:
    if "interactive" in row:
        return bool(row.get("interactive"))
    role = str(row.get("role") or row.get("tag") or row.get("type") or "").lower()
    return role in {
        "a",
        "button",
        "checkbox",
        "combobox",
        "input",
        "link",
        "radio",
        "select",
        "switch",
        "tab",
        "textarea",
        "textbox",
    }


def validate_control_parity(root: Path, errors: list[str]) -> None:
    source = normalize_rows(load_json(root / "source-controls.json", errors, required=False), ("controls", "items"))
    local = normalize_rows(load_json(root / "local-controls.json", errors, required=False), ("controls", "items"))
    contracts = normalize_rows(load_json(root / "action-contracts.json", errors, required=False), ("contracts", "actions", "items"))

    local_keys = {control_key(row) for row in local if control_key(row)}
    contract_keys = {str(row.get("control_key") or row.get("key") or "").strip() for row in contracts}

    for row in source:
        key = control_key(row)
        if not key:
            errors.append("Source control missing key/control_key/id")
            continue
        if row.get("source_required", True) and key not in local_keys:
            errors.append(f"Missing local control: {key}")
        if is_interactive(row) and key in local_keys and key not in contract_keys:
            errors.append(f"Interactive control without action contract: {key}")


def validate_action_contracts(root: Path, errors: list[str]) -> None:
    contracts = normalize_rows(load_json(root / "action-contracts.json", errors, required=False), ("contracts", "actions", "items"))
    required_fields = ["control_key", "route", "request_fields", "validation", "service", "persistence", "tests", "status"]
    for row in contracts:
        key = str(row.get("control_key") or row.get("key") or "<missing>")
        missing = [field for field in required_fields if not truthy_proof(row.get(field))]
        if missing:
            errors.append(f"Action contract {key} missing fields: {missing}")


def validate_pass_rows(root: Path, errors: list[str]) -> None:
    ledger = normalize_rows(load_json(root / "progress-ledger.json", errors, required=False), ("rows", "ledger", "items"))
    required = ["source_proof", "browser_proof", "backend_proof", "tests", "security_proof"]
    for row in ledger:
        status = str(row.get("status") or "").upper()
        feature = row.get("feature") or row.get("provider") or row.get("name") or "<unknown>"
        if status == "PASS":
            missing = [field for field in required if not truthy_proof(row.get(field))]
            if missing:
                errors.append(f"PASS row missing proof for {feature}: {missing}")


def validate_adoption_caps(root: Path, errors: list[str], warnings: list[str]) -> None:
    rows = normalize_rows(load_json(root / "parity-matrix.json", errors, required=False), ("rows", "features", "items"))
    browser = load_json(root / "browser-proof.json", errors, required=False)
    backend = load_json(root / "backend-proof.json", errors, required=False)

    has_browser = truthy_proof(browser) and str(browser).lower().find("blocked") == -1
    has_backend = truthy_proof(backend) and str(backend).lower().find("blocked") == -1

    for row in rows:
        name = row.get("feature") or row.get("control_key") or row.get("name") or "<unknown>"
        status = str(row.get("status") or "").upper()
        percent_raw = row.get("adoption_percent", row.get("adoption", 0))
        try:
            percent = float(str(percent_raw).replace("%", ""))
        except ValueError:
            warnings.append(f"Adoption percent is not numeric for {name}: {percent_raw}")
            continue

        has_source = truthy_proof(row.get("source_proof") or row.get("source_url") or row.get("source_control"))
        has_local = truthy_proof(row.get("local_proof") or row.get("local_url") or row.get("local_control"))
        has_contract = truthy_proof(row.get("action_contract") or row.get("backend_contract"))
        has_permissions = truthy_proof(row.get("permission_proof") or row.get("workspace_proof"))

        if not has_source and percent > 0:
            errors.append(f"{name} has adoption percent above 0 without source proof")
        if has_local and not has_contract and percent > 35:
            errors.append(f"{name} exceeds 35% cap without action/backend contract")
        if has_contract and not has_browser and percent > 60:
            errors.append(f"{name} exceeds 60% cap without browser proof")
        if not has_permissions and percent > 70:
            errors.append(f"{name} exceeds 70% cap without workspace/permission proof")
        if status == "PASS" and percent < 100:
            warnings.append(f"{name} is PASS but adoption_percent is below 100")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Devad adoption packet.")
    parser.add_argument("packet", help="Path to adoption packet folder")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero unless status is PASS")
    args = parser.parse_args()

    root = Path(args.packet).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(json.dumps({"status": "BLOCKED", "errors": [f"Packet folder not found: {root}"]}, indent=2))
        return 2

    if (root / "SKILL.md").exists() and (root / "agents" / "openai.yaml").exists():
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "errors": [
                        "This looks like a Codex skill folder, not an adoption packet. Use validate_skill_pack.py or the official quick_validate.py.",
                    ],
                },
                indent=2,
            )
        )
        return 2

    files = list(iter_files(root))
    text_files = [path for path in files if path.suffix.lower() in TEXT_EXTENSIONS]

    errors: list[str] = []
    warnings: list[str] = []

    validate_required_files(root, errors)
    validate_screenshots(files, errors)
    validate_control_parity(root, errors)
    validate_action_contracts(root, errors)
    validate_pass_rows(root, errors)
    validate_adoption_caps(root, errors, warnings)
    errors.extend(secret_findings(root, text_files))
    warnings.extend(risky_done_claims(root, text_files))

    if errors:
        status = "BLOCKED"
    elif warnings:
        status = "PARTIAL"
    else:
        status = "PASS"

    result = {
        "status": status,
        "packet": str(root),
        "summary": {
            "files": len(files),
            "text_files": len(text_files),
            "source_screenshots": [rel(path, root) for path in find_screenshots(files, "source")],
            "local_screenshots": [rel(path, root) for path in find_screenshots(files, "local")],
        },
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))

    if args.strict and status != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
