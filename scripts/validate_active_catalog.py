from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "active"
PRIVATE_PATTERNS = (
    re.compile(r"(?i)" + "A-" + "haj"),
    re.compile(r"(?i)C:[\\/]Users[\\/](?!<[^>]+>|%[^%]+%)[A-Za-z0-9._-]+(?:[\\/]|$)"),
    re.compile(r"(?i)D:[\\/]CDx9"),
    re.compile(r"(?i)github_pat_[A-Za-z0-9_]+"),
    re.compile(r"(?i)ghp_[A-Za-z0-9]+"),
    re.compile(r"(?i)-----BEGIN (?:OPENSSH|RSA|EC|DSA|PRIVATE) KEY-----"),
)
FORBIDDEN_NAMES = {"auth.json", "cap_sid", ".env", "config.toml"}


def folder_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(item.read_bytes()).digest())
    return digest.hexdigest()


def validate(errors: list[str]) -> None:
    catalog_path = ACTIVE / "catalog.json"
    if not catalog_path.is_file():
        errors.append("missing active/catalog.json")
        return
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"active catalog load failed: {exc}")
        return
    if catalog.get("schema") != "devad-x9-public-active-catalog-v1":
        errors.append("active catalog schema mismatch")
    entries = catalog.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("active catalog has no entries")
        return
    names: set[str] = set()
    for entry in entries:
        name = entry.get("name")
        relative = entry.get("path")
        if not isinstance(name, str) or not isinstance(relative, str):
            errors.append("active catalog entry missing name/path")
            continue
        if name in names:
            errors.append(f"duplicate active catalog name: {name}")
        names.add(name)
        path = ACTIVE / relative
        if not path.is_dir() or not (path / "SKILL.md").is_file():
            errors.append(f"active catalog entry missing entrypoint: {relative}")
            continue
        if entry.get("declared_name") not in {name, None}:
            errors.append(f"entrypoint name mismatch: {relative}")
        files = [item for item in path.rglob("*") if item.is_file()]
        if entry.get("files") != len(files):
            errors.append(f"file count mismatch: {relative}")
        if entry.get("bytes") != sum(item.stat().st_size for item in files):
            errors.append(f"byte count mismatch: {relative}")
        if entry.get("folder_sha256") != folder_digest(path):
            errors.append(f"folder digest mismatch: {relative}")

    for item in ACTIVE.rglob("*"):
        if not item.is_file() or item == catalog_path:
            continue
        if item.name.casefold() in FORBIDDEN_NAMES or item.suffix.casefold() in {".jsonl", ".sqlite", ".db", ".pyc"}:
            errors.append(f"forbidden active file: {item.relative_to(ROOT)}")
            continue
        try:
            text = item.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                errors.append(f"private marker in active file: {item.relative_to(ROOT)}")
                break


def main() -> int:
    errors: list[str] = []
    validate(errors)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    catalog = json.loads((ACTIVE / "catalog.json").read_text(encoding="utf-8-sig"))
    print(f"PASS: sanitized active catalog ({len(catalog['entries'])} entrypoints)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
