from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import stat
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "devad-x9",
    "x9-loop-style",
    "x9-loop-code",
    "devad-x9-loop",
    "devad-x9-manager",
    "codex-x9-backup",
    "codex-token-budget",
    "devad-memory",
    "x9-project-docs",
    "dokploy",
    "devad-docs",
    "tldr",
    "smooth-coding",
    "sdlc",
    "xplan",
    "devad-adoptions",
)
ACTIVE_SOURCE_ROOTS = ("scripts", "skills", "templates", "tests")
TEMPORARY_PROJECT_MARKER = ".x9-release-gate-temporary"
SOURCE_MANIFEST = ROOT / "scripts" / "build_source_manifest.py"
PACKAGE_VALIDATOR = ROOT / "scripts" / "validate_suite.py"
SECRET_SCAN = ROOT / "skills" / "codex-x9-backup" / "scripts" / "secret-scan.py"
ARCHIVE_VALIDATOR = ROOT / "scripts" / "validate_archive.py"
INSTALLER = ROOT / "scripts" / "install-suite.ps1"
LOOPCTL = ROOT / "skills" / "devad-x9-loop" / "scripts" / "loopctl.py"


class GateFailure(RuntimeError):
    pass


def _plan(temporary_project: Path | None) -> dict[str, Any]:
    gates: list[dict[str, Any]] = [
        {
            "gate": "full unittest suite",
            "command": ["<python>", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        },
        {"gate": "Python syntax", "command": ["internal", "ast.parse", "active Python files"]},
        {"gate": "PowerShell syntax", "command": ["PowerShell Parser.ParseFile", "active PowerShell files"]},
        {
            "gate": "sixteen quick_validate skills",
            "command": ["<python>", "<quick_validate.py>", "skills/<skill>"],
            "skills": list(SKILLS),
        },
        {
            "gate": "secret scan",
            "command": ["<python>", "skills/codex-x9-backup/scripts/secret-scan.py", "--root", str(ROOT)],
        },
        {"gate": "archive manifest", "command": ["<python>", "scripts/validate_archive.py"]},
        {"gate": "git diff --check", "command": ["<absolute-git>", "diff", "--check"]},
        {
            "gate": "source manifest and package",
            "commands": [
                ["<python>", "scripts/build_source_manifest.py"],
                ["<python>", "scripts/validate_suite.py"],
            ],
        },
        {
            "gate": "temporary install dry/apply",
            "commands": [
                ["<absolute-powershell>", "scripts/install-suite.ps1", "-CodexHome", "<temporary-codex-home>"],
                ["<absolute-powershell>", "scripts/install-suite.ps1", "-CodexHome", "<temporary-codex-home>", "-Apply"],
            ],
        },
    ]
    gates.append(
        {
            "gate": "temporary V7 to V7.3 migration and rollback",
            "enabled": temporary_project is not None,
            "temporary_project": str(temporary_project) if temporary_project else None,
            "commands": [
                ["<python>", "loopctl.py", "migrate-v3"],
                ["<python>", "loopctl.py", "doctor"],
                ["<python>", "loopctl.py", "rollback-v7"],
                ["<python>", "loopctl.py", "doctor-v7"],
            ],
        }
    )
    return {
        "schema": "x9-loop-v73-lite-release-plan-v1",
        "mode": "DRY_RUN",
        "network_or_provider_calls": 0,
        "root": str(ROOT),
        "gates": gates,
    }


def _display(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def _run(
    gate: str,
    command: list[str],
    *,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> str:
    print(json.dumps({"gate": gate, "command": _display(command)}, sort_keys=True))
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=capture,
        )
    except OSError as exc:
        raise GateFailure(f"{gate}: executable unavailable: {exc.__class__.__name__}") from exc
    if capture:
        if completed.stdout:
            print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    if completed.returncode:
        raise GateFailure(f"{gate}: exit {completed.returncode}")
    return completed.stdout if capture else ""


def _active_files(suffix: str) -> list[Path]:
    files: list[Path] = []
    for root_name in ACTIVE_SOURCE_ROOTS:
        source_root = ROOT / root_name
        if not source_root.is_dir():
            continue
        files.extend(
            path
            for path in source_root.rglob(f"*{suffix}")
            if path.is_file() and "__pycache__" not in path.parts
        )
    return sorted(set(files), key=lambda path: path.relative_to(ROOT).as_posix())


def _python_syntax() -> None:
    files = _active_files(".py")
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as exc:
            raise GateFailure(f"Python syntax: {path.relative_to(ROOT).as_posix()}: {exc}") from exc
    print(json.dumps({"gate": "Python syntax", "status": "PASS", "files": len(files)}, sort_keys=True))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _link_or_reparse(path: Path) -> bool:
    item = os.lstat(path)
    return stat.S_ISLNK(item.st_mode) or bool(
        getattr(item, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _resolve_trusted_executable(requested: str | None, label: str) -> str:
    if not requested:
        raise GateFailure(f"{label}: explicit absolute executable required")
    candidate = Path(requested).expanduser()
    if not candidate.is_absolute():
        raise GateFailure(f"{label}: executable must be an explicit absolute path")
    try:
        absolute = Path(os.path.abspath(candidate))
        current = Path(absolute.anchor)
        for part in absolute.parts[1:]:
            current = current / part
            if _link_or_reparse(current):
                raise GateFailure(f"{label}: linked or reparse executable path rejected")
        resolved = absolute.resolve(strict=True)
    except OSError as exc:
        raise GateFailure(f"{label}: requested executable unavailable") from exc
    if not resolved.is_file():
        raise GateFailure(f"{label}: requested executable is not a file")
    package = ROOT.resolve()
    if _is_within(absolute, package) or _is_within(resolved, package):
        raise GateFailure(f"{label}: package-root executable rejected")
    return str(resolved)


def _resolve_powershell(requested: str | None) -> str:
    return _resolve_trusted_executable(requested, "PowerShell")


def _resolve_git(requested: str | None) -> str:
    return _resolve_trusted_executable(requested, "Git")


def _powershell_syntax(requested: str | None) -> str:
    executable = _resolve_powershell(requested)
    parser = (
        "$tokens=$null;$errors=$null;"
        "[void][System.Management.Automation.Language.Parser]::ParseFile("
        "$env:X9_RELEASE_GATE_PS_FILE,[ref]$tokens,[ref]$errors);"
        "if($errors.Count -gt 0){"
        "$errors|ForEach-Object{[Console]::Error.WriteLine($_.Message)};exit 1}"
    )
    files = _active_files(".ps1")
    for path in files:
        environment = os.environ.copy()
        environment["X9_RELEASE_GATE_PS_FILE"] = str(path)
        _run(
            f"PowerShell syntax:{path.relative_to(ROOT).as_posix()}",
            [executable, "-NoProfile", "-NonInteractive", "-Command", parser],
            env=environment,
        )
    print(json.dumps({"gate": "PowerShell syntax", "status": "PASS", "files": len(files)}, sort_keys=True))
    return executable


def _resolve_quick_validate(requested: Path | None) -> Path:
    candidates = []
    if requested:
        candidates.append(requested.expanduser())
    candidates.append(Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py")
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise GateFailure("quick_validate: validator unavailable; pass --quick-validate")


def _parse_result(output: str, gate: str) -> dict[str, Any]:
    for line in reversed(output.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            if value.get("status") == "ERROR":
                raise GateFailure(f"{gate}: {value.get('error', 'unknown error')}")
            return value
    raise GateFailure(f"{gate}: JSON result missing")


def _manifest_project_path(project: Path, relative: str) -> Path:
    parts = relative.split("/")
    if (
        not relative
        or "\\" in relative
        or relative.startswith("/")
        or any(not part or part in {".", ".."} for part in parts)
        or ":" in parts[0]
        or "/".join(parts) != relative
    ):
        raise GateFailure(f"temporary rollback: unsafe manifest path: {relative}")
    project_root = project.resolve(strict=True)
    candidate = project_root.joinpath(*parts)
    current = project_root
    for part in parts:
        current = current / part
        if _link_or_reparse(current):
            raise GateFailure(f"temporary rollback: linked manifest path: {relative}")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise GateFailure(f"temporary rollback: manifest file missing: {relative}") from exc
    if not _is_within(resolved, project_root) or not resolved.is_file():
        raise GateFailure(f"temporary rollback: manifest path escapes project: {relative}")
    return resolved


def _file_identity(path: Path) -> tuple[str, int]:
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size


def _recovery_manifest_hashes(
    project: Path, recovery_id: str
) -> dict[str, tuple[Path, str, int]]:
    root_relative = ".devad/manager/loop-lite"
    recovery_relative = f"{root_relative}/recovery/{recovery_id}"
    manifest_path = _manifest_project_path(
        project, f"{recovery_relative}/RECOVERY.json"
    )
    try:
        manifest = json.loads(manifest_path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateFailure("temporary rollback: recovery manifest invalid") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != "x9-loop-v7-recovery-v1"
        or manifest.get("recovery_id") != recovery_id
        or not isinstance(manifest.get("files"), list)
        or not isinstance(manifest.get("snapshot_references"), list)
    ):
        raise GateFailure("temporary rollback: recovery manifest invalid")

    expected: dict[str, tuple[Path, str, int]] = {}
    for row in manifest["files"]:
        if (
            not isinstance(row, dict)
            or set(row) != {"name", "sha256", "size"}
            or not isinstance(row.get("name"), str)
            or "/" in row["name"]
            or "\\" in row["name"]
            or row["name"] in {"", ".", ".."}
            or re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256"))) is None
            or isinstance(row.get("size"), bool)
            or not isinstance(row.get("size"), int)
            or row["size"] < 0
        ):
            raise GateFailure("temporary rollback: recovery file row invalid")
        name = row["name"]
        label = f"file:{name}"
        active_relative = (
            f"{root_relative}/runtime/ACTION.json"
            if name == "ACTION.json"
            else f"{root_relative}/{name}"
        )
        if label in expected:
            raise GateFailure("temporary rollback: duplicate recovery file")
        recovery_copy = _manifest_project_path(
            project, f"{recovery_relative}/{name}"
        )
        if _file_identity(recovery_copy) != (row["sha256"], row["size"]):
            raise GateFailure("temporary rollback: recovery copy differs from manifest")
        expected[label] = (
            project.resolve().joinpath(*active_relative.split("/")),
            row["sha256"],
            row["size"],
        )

    for row in manifest["snapshot_references"]:
        if (
            not isinstance(row, dict)
            or set(row) != {"path", "sha256", "size"}
            or not isinstance(row.get("path"), str)
            or re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256"))) is None
            or isinstance(row.get("size"), bool)
            or not isinstance(row.get("size"), int)
            or row["size"] < 0
        ):
            raise GateFailure("temporary rollback: snapshot reference row invalid")
        label = f"snapshot:{row['path']}"
        if label in expected:
            raise GateFailure("temporary rollback: duplicate snapshot reference")
        active = _manifest_project_path(project, row["path"])
        if _file_identity(active) != (row["sha256"], row["size"]):
            raise GateFailure("temporary rollback: snapshot reference differs from manifest")
        expected[label] = (active, row["sha256"], row["size"])
    if not expected:
        raise GateFailure("temporary rollback: recovery manifest is empty")
    return expected


def _active_recovery_hashes(
    project: Path, expected: dict[str, tuple[Path, str, int]]
) -> dict[str, str]:
    actual: dict[str, str] = {}
    project_root = project.resolve(strict=True)
    for label, (path, digest, size) in expected.items():
        try:
            resolved = path.resolve(strict=True)
        except OSError as exc:
            raise GateFailure(f"temporary rollback: restored file missing: {label}") from exc
        if not _is_within(resolved, project_root) or not resolved.is_file():
            raise GateFailure(f"temporary rollback: restored path escaped: {label}")
        relative = resolved.relative_to(project_root).as_posix()
        checked = _manifest_project_path(project_root, relative)
        actual_digest, actual_size = _file_identity(checked)
        if actual_digest != digest or actual_size != size:
            raise GateFailure(f"temporary rollback: restored bytes differ: {label}")
        actual[label] = actual_digest
    return actual


def _assert_temporary_project(project: Path) -> Path:
    resolved = project.expanduser().resolve()
    if resolved == ROOT or not resolved.is_dir():
        raise GateFailure("temporary migration: project is missing or is the package root")
    if not (resolved / TEMPORARY_PROJECT_MARKER).is_file():
        raise GateFailure(
            f"temporary migration: missing explicit {TEMPORARY_PROJECT_MARKER} marker"
        )
    item = os.lstat(resolved)
    attributes = getattr(item, "st_file_attributes", 0)
    if resolved.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
        raise GateFailure("temporary migration: reparse project root rejected")
    return resolved


def _migration_proof(python: str, project: Path) -> None:
    project = _assert_temporary_project(project)
    base = [python, str(LOOPCTL)]
    migration_output = _run(
        "temporary migrate-v3",
        [*base, "migrate-v3", "--repo", str(project), "--json"],
        capture=True,
    )
    migration = _parse_result(migration_output, "temporary migrate-v3")
    recovery_id = migration.get("recovery_id")
    if migration.get("status") != "PASS" or not isinstance(recovery_id, str):
        raise GateFailure("temporary migrate-v3: PASS recovery identity missing")
    expected = _recovery_manifest_hashes(project, recovery_id)

    doctor_problem: GateFailure | None = None
    try:
        doctor_output = _run(
            "temporary migrated doctor",
            [*base, "doctor", "--repo", str(project), "--json"],
            capture=True,
        )
        doctor = _parse_result(doctor_output, "temporary migrated doctor")
        if doctor.get("status") != "PASS":
            doctor_problem = GateFailure("temporary migrated doctor: status is not PASS")
    except GateFailure as exc:
        doctor_problem = exc

    rollback_output = _run(
        "temporary rollback-v7",
        [
            *base,
            "rollback-v7",
            "--repo",
            str(project),
            "--recovery",
            recovery_id,
            "--json",
        ],
        capture=True,
    )
    rollback = _parse_result(rollback_output, "temporary rollback-v7")
    if rollback.get("status") != "PASS":
        raise GateFailure("temporary rollback-v7: status is not PASS")
    after = _active_recovery_hashes(project, expected)
    expected_hashes = {
        label: digest for label, (_, digest, _) in expected.items()
    }
    if after != expected_hashes:
        raise GateFailure("temporary rollback-v7: recovery bytes differ")
    post_doctor_output = _run(
        "temporary post-rollback doctor",
        [*base, "doctor-v7", "--repo", str(project), "--json"],
        capture=True,
    )
    post_doctor = _parse_result(
        post_doctor_output, "temporary post-rollback doctor"
    )
    if post_doctor.get("status") != "PASS":
        raise GateFailure("temporary post-rollback doctor: status is not PASS")
    if doctor_problem:
        raise doctor_problem
    print(json.dumps({"gate": "temporary migration rollback", "status": "PASS", "files": len(expected)}, sort_keys=True))


def _resolve_python(requested: str) -> str:
    candidate = Path(requested).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    resolved = shutil.which(requested)
    if resolved:
        return resolved
    raise GateFailure("Python executable unavailable")


def _execute(args: argparse.Namespace) -> int:
    python = _resolve_python(args.python)
    git = _resolve_git(args.git)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    _run(
        "full unittest suite",
        [python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        env=environment,
    )
    _python_syntax()
    powershell = _powershell_syntax(args.powershell)

    quick_validate = _resolve_quick_validate(args.quick_validate)
    for skill in SKILLS:
        _run(
            f"quick_validate:{skill}",
            [python, str(quick_validate), str(ROOT / "skills" / skill)],
            env=environment,
        )

    with tempfile.TemporaryDirectory(prefix="x9-v73-release-gate-") as directory:
        temporary_root = Path(directory)
        evidence = args.evidence_dir.resolve() if args.evidence_dir else temporary_root / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        _run(
            "secret scan",
            [
                python,
                str(SECRET_SCAN),
                "--root",
                str(ROOT),
                "--output",
                str(evidence / "secret-scan.json"),
                "--max-findings",
                "50",
            ],
            env=environment,
        )
        _run("validate archive", [python, str(ARCHIVE_VALIDATOR)], env=environment)
        _run("git diff --check", [git, "diff", "--check"])
        _run("build source manifest", [python, str(SOURCE_MANIFEST)], env=environment)
        _run("validate suite", [python, str(PACKAGE_VALIDATOR)], env=environment)

        codex_home = temporary_root / "codex-home"
        install_base = [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(INSTALLER),
            "-CodexHome",
            str(codex_home),
            "-Python",
            python,
            "-SkillValidator",
            str(quick_validate),
        ]
        _run("temporary install dry run", install_base, env=environment)
        _run("temporary install apply", [*install_base, "-Apply"], env=environment)

        if args.temporary_project:
            _migration_proof(python, args.temporary_project)

    print(json.dumps({"schema": "x9-loop-v73-lite-release-result-v1", "status": "PASS"}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic local X9 Loop V7.3 Lite release gate"
    )
    parser.add_argument("--execute", action="store_true", help="run local gates; default only prints the plan")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--powershell", default=None)
    parser.add_argument("--git", default=None)
    parser.add_argument("--quick-validate", type=Path, default=None)
    parser.add_argument("--evidence-dir", type=Path, default=None)
    parser.add_argument(
        "--temporary-project",
        type=Path,
        default=None,
        help=f"disposable V7 fixture containing {TEMPORARY_PROJECT_MARKER}",
    )
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps(_plan(args.temporary_project), indent=2, sort_keys=True))
        return 0
    try:
        return _execute(args)
    except (GateFailure, OSError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "schema": "x9-loop-v73-lite-release-result-v1",
                    "status": "BLOCKED",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
