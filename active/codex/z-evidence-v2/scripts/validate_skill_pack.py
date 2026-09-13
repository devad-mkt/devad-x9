#!/usr/bin/env python3
"""Validate the evidence-to-implementation skill's routed contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "references/ADOPTION-AND-VERSION-GATES.md",
    "references/IMPLEMENTATION-READINESS-CONTRACTS.md",
    "references/CASE-LESSONS.md",
    "references/BROWSER-DOM-LIVE-TESTING.md",
    "references/SOURCE-TO-NATIVE-MAPPING.md",
    "references/SAFETY-STATUS-VALIDATION.md",
    "references/METHODS-AND-TOOLS.md",
    "scripts/validate_packet_library.py",
    "scripts/validate_skill_pack.py",
    "templates/REQUIREMENT-LEDGER.template.json",
    "templates/SOURCE-VERSION-MANIFEST.template.json",
    "templates/VISUAL-MANIFEST.template.json",
    "templates/WORK-ORDER.template.md",
}

REQUIRED_PHRASES = {
    "owner-requirement ledger",
    "versions independently",
    "admin settings",
    "state machines",
    "Lower-Model Handoff Gate",
    "NOT_EXECUTED_UNSAFE",
    "validate_packet_library.py",
}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1]).resolve()
    errors: list[str] = []
    for relative in sorted(REQUIRED_FILES):
        if not (root / relative).is_file():
            errors.append(f"missing: {relative}")

    skill = root / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        if not re.match(r"^---\nname: evidence-to-implementation\n", text):
            errors.append("invalid SKILL.md frontmatter")
        for phrase in sorted(REQUIRED_PHRASES):
            if phrase not in text:
                errors.append(f"SKILL.md missing phrase: {phrase}")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" not in link and not (root / link).exists():
                errors.append(f"unresolved SKILL.md link: {link}")

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            continue
        raw = path.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"not UTF-8: {relative}")
        if raw and not raw.endswith(b"\n"):
            errors.append(f"missing final LF: {relative}")

    for relative in (
        "templates/REQUIREMENT-LEDGER.template.json",
        "templates/SOURCE-VERSION-MANIFEST.template.json",
        "templates/VISUAL-MANIFEST.template.json",
    ):
        try:
            json.loads((root / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {relative}: {exc}")

    print(json.dumps({"status": "PASS" if not errors else "BLOCKED", "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
