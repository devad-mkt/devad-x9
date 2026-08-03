from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archives" / "pre-v5-2026-07-13"
MANIFEST = ARCHIVE / "SHA256SUMS"


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.is_file():
        print("ERROR: missing archive manifest")
        return 1
    for line in MANIFEST.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        path = ARCHIVE / relative
        if not path.is_file():
            errors.append(f"missing:{relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f"mismatch:{relative}")
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        return 1
    print("PASS: pre-v5 archive hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
