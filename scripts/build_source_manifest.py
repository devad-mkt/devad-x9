from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "SOURCE_MANIFEST.sha256"
EXCLUDE = {"SOURCE_MANIFEST.sha256"}
PROJECT_STATE_ROOTS = (".devad/manager", ".devad/workers")
HOST_RUNTIME_ROOTS = (".agents",)
LOCAL_TEMP_ROOTS = (".temp",)


def _is_project_state_path(relative: str) -> bool:
    return any(
        relative == root or relative.startswith(root + "/")
        for root in PROJECT_STATE_ROOTS
    )


def _is_host_runtime_path(relative: str) -> bool:
    return any(
        relative == root or relative.startswith(root + "/")
        for root in HOST_RUNTIME_ROOTS
    )

def _is_local_temp_path(relative: str) -> bool:
    return any(
        relative == root or relative.startswith(root + "/")
        for root in LOCAL_TEMP_ROOTS
    )


def _is_link_or_reparse(path: Path) -> bool:
    item = os.lstat(path)
    return stat.S_ISLNK(item.st_mode) or bool(
        getattr(item, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _assert_manifest_path_safe(root: Path, path: Path) -> Path:
    root_absolute = Path(os.path.abspath(root))
    path_absolute = Path(os.path.abspath(path))
    try:
        relative = path_absolute.relative_to(root_absolute)
    except ValueError as exc:
        raise ValueError(f"manifest path escapes package root: {path}") from exc
    current = root_absolute
    if _is_link_or_reparse(current):
        raise ValueError(f"manifest package root is a link or reparse point: {root}")
    for part in relative.parts:
        current = current / part
        if _is_link_or_reparse(current):
            raise ValueError(f"manifest path is a link or reparse point: {path}")
    resolved_root = root_absolute.resolve(strict=True)
    resolved_path = path_absolute.resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"resolved manifest path escapes package root: {path}") from exc
    return resolved_path


def main() -> int:
    try:
        _assert_manifest_path_safe(ROOT, ROOT)
        if os.path.lexists(OUTPUT):
            _assert_manifest_path_safe(ROOT, OUTPUT)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"unsafe source manifest output: {exc}") from exc
    lines: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT).as_posix()
        if (
            relative in EXCLUDE
            or relative == ".git"
            or relative.startswith(".git/")
            or "__pycache__" in path.parts
            or path.suffix == ".pyc"
            or _is_project_state_path(relative)
            or _is_host_runtime_path(relative)
            or _is_local_temp_path(relative)
        ):
            continue
        try:
            safe_path = _assert_manifest_path_safe(ROOT, path)
        except (OSError, ValueError) as exc:
            raise SystemExit(f"unsafe manifest path: {relative}: {exc}") from exc
        if not safe_path.is_file():
            continue
        data = safe_path.read_bytes()
        if (
            not relative.startswith(".devad/")
            and b"\r\n" in data
            and b"\0" not in data
        ):
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                pass
            else:
                raise SystemExit(f"UTF-8 text must use LF before manifest build: {relative}")
        digest = hashlib.sha256(data).hexdigest()
        lines.append(f"{digest}  {relative}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT} with {len(lines)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
