from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENAMES = {"seo-content-engine": "z-content"}
EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "benchmarks",
    "recovery",
    "results",
    "runs",
    "archives",
    "backups",
    "sessions",
    "visualizations",
}
EXCLUDED_FILE_PATTERNS = {
    "auth.json",
    "cap_sid",
    "*.bak",
    "*.bak.*",
    "*.db",
    "*.db-*",
    "*.jsonl",
    "*.log",
    "*.pyc",
    "*.redacted",
    "*.sqlite",
    "*.sqlite-*",
    "*.zip",
    "spama-page.html",
    "spama-text.txt",
    ".env",
    ".env.*",
    "*cookie*",
    "*cookies*",
}

_PRIVATE_REPLACEMENTS = (
    (re.compile(r"(?i)C:[\\/]Users[\\/][^\\/\s`'\"<>|]+[\\/]\.codex"), "$CODEX_HOME"),
    (re.compile(r"(?i)C:[\\/]Users[\\/][^\\/\s`'\"<>|]+[\\/]\.agents"), "$AGENTS_HOME"),
    (re.compile(r"(?i)C:[\\/]Users[\\/][^\\/\s`'\"<>|]+[\\/]AppData"), "$LOCAL_APP_DATA"),
    (re.compile(r"(?i)C:[\\/]Users[\\/][^\\/\s`'\"<>|]+"), "$USER_HOME"),
    (re.compile(r"(?i)D:[\\/]CDx9-tools"), "$DEVAD_TOOLS_ROOT"),
    (re.compile(r"(?i)D:[\\/]CDx9"), "$DEVAD_ROOT"),
    (re.compile(r"(?i)D:[\\/]CDX-3"), "$DEVAD_ROOT"),
    (re.compile(r"(?i)" + "devadio/" + "codex-x9-backup"), "<PRIVATE_BACKUP_REPO>"),
    (re.compile(r"(?i)" + "devadio/" + "x9-loop-private"), "<PRIVATE_X9_REPO>"),
    (re.compile(r"(?i)devadio/core"), "<DEVAD_CORE_REPO>"),
    (re.compile(r"(?i)" + "env-" + "extra"), "<PRIVATE_ENV_DIR>"),
    (re.compile(r"(?i)\b" + "spama" + r"\b"), "<PRIVATE_EXAMPLE>"),
    (re.compile(r"(?i)actingBusinessId=\d+"), "actingBusinessId=<business-id>"),
)


def renamed_name(name: str) -> str:
    return RENAMES.get(name, name)


def excluded(relative: Path) -> str | None:
    if any(part.casefold() in EXCLUDED_DIR_NAMES for part in relative.parts[:-1]):
        return "private-or-generated-directory"
    name = relative.name.casefold()
    if name in {"skill.template.disabled.md"} or name.startswith("skill.archived-"):
        return "disabled-or-archived-entrypoint"
    if any(fnmatch.fnmatch(name, pattern.casefold()) for pattern in EXCLUDED_FILE_PATTERNS):
        return "private-or-generated-file"
    return None


def sanitize_text(text: str) -> str:
    for pattern, replacement in _PRIVATE_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text.replace("\r\n", "\n")


def copy_tree(source: Path, destination: Path, source_name: str) -> dict[str, int | str]:
    files = 0
    bytes_written = 0
    excluded_files = 0
    destination.mkdir(parents=True, exist_ok=False)
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        reason = excluded(relative)
        if reason:
            if path.is_file():
                excluded_files += 1
            continue
        if path.is_symlink():
            excluded_files += 1
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        data = path.read_bytes()
        try:
            data = sanitize_text(data.decode("utf-8")).encode("utf-8")
        except UnicodeDecodeError:
            pass
        if source_name == "seo-content-engine" and relative.as_posix() == "SKILL.md":
            text = data.decode("utf-8")
            text = re.sub(r"(?m)^name:\s*seo-content-engine\s*$", "name: z-content", text)
            data = text.encode("utf-8")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files += 1
        bytes_written += len(data)
    return {"files": files, "bytes": bytes_written, "excluded_files": excluded_files}


def folder_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(item.read_bytes()).digest())
    return digest.hexdigest()


def declared_name(path: Path) -> str | None:
    try:
        text = (path / "SKILL.md").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None
    match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", text)
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the sanitized public active-skill catalog.")
    parser.add_argument("--source-root", required=True, type=Path, help="Snapshot active root containing codex/ and agents/.")
    parser.add_argument("--destination", type=Path, default=ROOT / "active")
    parser.add_argument("--apply", action="store_true", help="Write the catalog; without this flag only argument checks run.")
    args = parser.parse_args()

    source = args.source_root.resolve()
    destination = args.destination.resolve()
    if not (source / "codex").is_dir() or not (source / "agents").is_dir():
        raise SystemExit("source root must contain codex and agents directories")
    if destination.exists():
        raise SystemExit(f"destination already exists; use a fresh clone: {destination}")
    if not args.apply:
        print(f"DRY_RUN source={source} destination={destination}")
        return 0

    destination.mkdir(parents=True)
    entries: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    names: dict[str, str] = {}
    for root_name in ("codex", "agents"):
        root = source / root_name
        for item in sorted(root.iterdir(), key=lambda p: p.name.casefold()):
            if not item.is_dir():
                continue
            if not (item / "SKILL.md").is_file():
                skipped.append({"root": root_name, "name": item.name, "reason": "marker-only-or-no-entrypoint"})
                continue
            source_declared_name = declared_name(item)
            public_name = renamed_name(source_declared_name or item.name)
            if public_name in names:
                raise SystemExit(f"duplicate active skill name: {public_name}: {names[public_name]} and {root_name}/{item.name}")
            names[public_name] = f"{root_name}/{item.name}"
            target = destination / root_name / public_name
            stats = copy_tree(item, target, item.name)
            entries.append(
                {
                    "name": public_name,
                    "source_name": item.name,
                    "source_root": root_name,
                    "path": target.relative_to(destination).as_posix(),
                    "declared_name": declared_name(target),
                    "files": stats["files"],
                    "bytes": stats["bytes"],
                    "excluded_files": stats["excluded_files"],
                    "folder_sha256": folder_digest(target),
                }
            )

    for root_name in ("codex", "agents"):
        root = destination / root_name
        for entrypoint in sorted(root.rglob("SKILL.md")):
            relative = entrypoint.parent.relative_to(destination)
            if len(relative.parts) <= 2:
                continue
            name = declared_name(entrypoint.parent) or entrypoint.parent.name
            if name in names:
                continue
            names[name] = relative.as_posix()
            entries.append(
                {
                    "name": name,
                    "source_name": name,
                    "source_root": root_name,
                    "path": relative.as_posix(),
                    "declared_name": declared_name(entrypoint.parent),
                    "files": len([p for p in entrypoint.parent.rglob("*") if p.is_file()]),
                    "bytes": sum(p.stat().st_size for p in entrypoint.parent.rglob("*") if p.is_file()),
                    "excluded_files": 0,
                    "folder_sha256": folder_digest(entrypoint.parent),
                    "nested": True,
                }
            )

    catalog = {
        "schema": "devad-x9-public-active-catalog-v1",
        "snapshot": "2026-09-13",
        "distribution": "public",
        "source_roots": ["active/codex", "active/agents"],
        "entries": sorted(entries, key=lambda item: str(item["name"]).casefold()),
        "skipped": skipped,
        "renames": [{"from": key, "to": value, "reason": "Z naming; content preserved"} for key, value in RENAMES.items()],
        "exclusions": sorted(EXCLUDED_DIR_NAMES | EXCLUDED_FILE_PATTERNS),
        "sanitization": ["profile paths -> portable environment placeholders", "private repository names -> placeholders", "business identifiers -> placeholders"],
    }
    (destination / "catalog.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {destination / 'catalog.json'} with {len(entries)} entrypoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
