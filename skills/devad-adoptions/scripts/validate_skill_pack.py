#!/usr/bin/env python3
"""Validate the Devad Adoptions skill pack shape.

This is intentionally separate from validate_adoption_packet.py. Skill folders
and adoption packets have different contracts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "scripts/validate_adoption_packet.py",
    "scripts/validate_skill_pack.py",
    "references/adoption-gates.md",
    "references/post-patterns.md",
    "references/api-cli-mcp-proof.md",
    "references/ai-content-lab-lessons.md",
    "references/creative-suite-media-lessons.md",
    "references/worker-packets.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Devad Adoptions skill pack.")
    parser.add_argument("skill", help="Path to devad-adoptions skill folder")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero unless status is PASS")
    args = parser.parse_args()

    root = Path(args.skill).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not root.exists() or not root.is_dir():
        errors.append(f"Skill folder not found: {root}")
    else:
        for relative in REQUIRED_FILES:
            if not (root / relative).is_file():
                errors.append(f"Missing required skill file: {relative}")

        skill_md = root / "SKILL.md"
        if skill_md.exists():
            body = read_text(skill_md)
            for required in [
                "failing proof test",
                "adoption-packets/<feature>",
                "action contract",
                "Adoption Caps",
                "PixelRAG",
                "validate_adoption_packet.py",
                "administrator plus user/workspace frontend settings",
                "Separate UI engine",
            ]:
                if required not in body:
                    errors.append(f"SKILL.md missing required phrase: {required}")
            if "TODO" in body:
                errors.append("SKILL.md still contains TODO")

        adoption_gates = root / "references" / "adoption-gates.md"
        if adoption_gates.exists():
            body = read_text(adoption_gates)
            for required in ["source-controls.json", "local-controls.json", "action-contracts.json", "Playwright", "Dusk"]:
                if required not in body:
                    warnings.append(f"adoption-gates.md may be missing: {required}")

    status = "BLOCKED" if errors else "PARTIAL" if warnings else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "skill": str(root),
                "errors": errors,
                "warnings": warnings,
            },
            indent=2,
        )
    )

    if args.strict and status != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
