from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_CATALOG = ROOT / "active" / "catalog.json"
PUBLIC_ROOT = ROOT / "skills"

# One public root entry is reused for these same-capability local aliases.
# Their complete current bodies remain available under active/.
REUSED = {
    "z-backup": ("codex-x9-backup", "same profile backup and restore boundary"),
    "z-browser": ("chrome-control", "same authenticated browser-control router"),
    "z-devad-adopt": ("devad-adoptions", "same Devad source-adoption gate"),
    "z-devad-docs": ("devad-docs", "same durable Devad documentation route"),
    "z-dokploy": ("dokploy", "same Dokploy provider boundary"),
    "z-evidence-v2": ("evidence-to-implementation", "same evidence-library capability"),
    "z-loop-code": ("x9-loop-code", "same disposable controller-trial boundary"),
    "z-loop-style": ("x9-loop-style", "same Style coordination contract"),
    "z-memory": ("devad-memory", "same durable memory boundary"),
    "z-native-adopt": ("semantic-adoption", "same native semantic-adoption boundary"),
    "z-plan": ("xplan", "same durable delivery-plan capability"),
    "z-sdlc": ("sdlc", "same risk-scaled lifecycle capability"),
    "z-ship": ("smooth-coding", "same accepted-plan execution boundary"),
    "z-subagent": ("x-subagent", "same bounded worker-routing boundary"),
    "z-tldr": ("tldr", "same evidence-bounded summary boundary"),
    "z-tokens": ("codex-token-budget", "same token-usage diagnosis boundary"),
    "z-x9": ("devad-x9", "same repository and release-safety boundary"),
    "z-x9-manager": ("devad-x9-manager", "same manager-prompt compatibility boundary"),
}


def _description(text: str, fallback: str) -> str:
    lines = text.replace("\r\n", "\n").splitlines()
    in_frontmatter = False
    collecting = False
    values: list[str] = []
    for line in lines:
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if not in_frontmatter:
            continue
        match = re.match(r"^description:\s*(.*)$", line)
        if match:
            value = match.group(1).strip()
            if value in {">", ">-", "|", "|-"}:
                collecting = True
                continue
            return _compact(value, fallback)
        if collecting:
            if line.startswith(" ") or line.startswith("\t"):
                values.append(line.strip())
            else:
                break
    return _compact(" ".join(values), fallback)


def _compact(value: str, fallback: str) -> str:
    value = re.sub(r"\s+", " ", value).strip().strip("'\"")
    return (value or fallback)[:240].rstrip(" .")


def _yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _card(name: str, description: str, full_source: str) -> str:
    link = f"../../{full_source}"
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {_yaml_quote(description)}\n"
        "---\n\n"
        f"# {name}\n\n"
        "Compact public routing card.\n\n"
        f"Use when: {description}\n\n"
        f"Full source: [{full_source}/SKILL.md]({link}/SKILL.md)\n\n"
        "- Load the full source before non-trivial execution.\n"
        "- Preserve its scope, ownership, evidence, and stop conditions.\n"
        "- Do not merge this capability with a different skill because names look similar.\n"
        "- Never publish secrets, tokens, cookies, private paths, or provider payloads.\n"
    )


def _load_entries() -> list[dict[str, object]]:
    payload = json.loads(ACTIVE_CATALOG.read_text(encoding="utf-8-sig"))
    return list(payload["entries"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact public skill cards without semantic duplicates.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    entries = _load_entries()
    names = {str(entry["name"]): entry for entry in entries}
    if len(names) != len(entries):
        raise SystemExit("active catalog contains duplicate names")
    unknown_reuse = sorted(set(REUSED) - set(names))
    if unknown_reuse:
        raise SystemExit(f"reuse map names missing from active catalog: {unknown_reuse}")
    if not args.apply:
        new = sorted(name for name in names if name not in REUSED)
        print(f"DRY_RUN compact_cards={len(new)} reused_aliases={len(REUSED)} s3_addon=1")
        return 0

    compact_entries: list[dict[str, object]] = []
    for name in sorted(names, key=str.casefold):
        entry = names[name]
        source = f"active/{entry['path']}"
        if name in REUSED:
            public_name, reason = REUSED[name]
            if not (PUBLIC_ROOT / public_name / "SKILL.md").is_file():
                raise SystemExit(f"reuse target is missing: {public_name}")
            compact_entries.append(
                {
                    "local_name": name,
                    "public_name": public_name,
                    "public_path": f"skills/{public_name}/SKILL.md",
                    "full_path": f"{source}/SKILL.md",
                    "mode": "REUSE_EXISTING_PUBLIC_ENTRY",
                    "reason": reason,
                }
            )
            continue

        destination = PUBLIC_ROOT / name
        if destination.exists():
            raise SystemExit(f"refusing to overwrite existing public skill: {destination}")
        full_entrypoint = ROOT / source / "SKILL.md"
        if not full_entrypoint.is_file():
            raise SystemExit(f"active full source is missing: {full_entrypoint}")
        description = _description(full_entrypoint.read_text(encoding="utf-8-sig"), name)
        destination.mkdir(parents=True)
        (destination / "SKILL.md").write_text(
            _card(name, description, source), encoding="utf-8", newline="\n"
        )
        compact_entries.append(
            {
                "local_name": name,
                "public_name": name,
                "public_path": f"skills/{name}/SKILL.md",
                "full_path": f"{source}/SKILL.md",
                "mode": "COMPACT_CARD",
                "description": description,
            }
        )

    s3 = PUBLIC_ROOT / "x9-s3-continuity"
    if s3.exists():
        raise SystemExit(f"refusing to overwrite existing S3 skill: {s3}")
    s3.mkdir(parents=True)
    s3_card = (
        "---\n"
        "name: x9-s3-continuity\n"
        "description: \"Provider-offline, Contabo-first selected-project S3 continuity with client-side encryption, immutable generations, verification, restore, and rollback.\"\n"
        "---\n\n"
        "# x9-s3-continuity\n\n"
        "Compact public routing card for the standalone S3 continuity addon.\n\n"
        "Use only for explicitly selected-project continuity work. The addon uses an injected, already-approved SDK boundary; it never discovers credential values, constructs a client, contacts a provider, or mutates a bucket by itself.\n\n"
        "Full implementation: `skills/x9-s3-continuity/`.\n"
        "Contract: `docs/S3_CONTINUITY_ADDON.md`.\n"
        "Focused proof: `tests/test_x9_s3_continuity.py`.\n\n"
        "- Keep real provider capability, credential, retention, and restore proof behind a separate owner-approved gate.\n"
        "- Preserve path validation, authenticated encryption, immutable conditional writes, manifest/marker ordering, complete verification, and non-overwriting restore.\n"
        "- Never publish credentials, bucket values, provider payloads, or live evidence.\n"
    )
    (s3 / "SKILL.md").write_text(s3_card, encoding="utf-8", newline="\n")
    compact_entries.append(
        {
            "local_name": "x9-s3-continuity",
            "public_name": "x9-s3-continuity",
            "public_path": "skills/x9-s3-continuity/SKILL.md",
            "full_path": "skills/x9-s3-continuity/",
            "mode": "FULL_ADDON_WITH_COMPACT_ENTRYPOINT",
            "source": "Worker S3 provider-offline candidate; no provider calls",
        }
    )

    payload = {
        "schema": "devad-x9-public-compact-skill-catalog-v1",
        "snapshot": "2026-09-13",
        "source_catalog": "active/catalog.json",
        "full_source_root": "active",
        "public_root": "skills",
        "local_entrypoint_count": len(entries),
        "compact_card_count": len(entries) - len(REUSED),
        "reused_alias_count": len(REUSED),
        "s3_addon_count": 1,
        "entries": sorted(compact_entries, key=lambda item: str(item["local_name"]).casefold()),
        "reuse_policy": "One public root entry per same-capability family; full active source remains preserved.",
    }
    (PUBLIC_ROOT / "compact-catalog.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"wrote {PUBLIC_ROOT / 'compact-catalog.json'} "
        f"with {len(entries) - len(REUSED)} compact cards, {len(REUSED)} reused aliases, and 1 S3 addon"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
