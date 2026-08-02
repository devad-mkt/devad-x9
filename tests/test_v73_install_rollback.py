from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-suite.ps1"
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


class V73InstallRollbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.powershell = shutil.which("powershell.exe") or shutil.which(
            "powershell"
        )
        if cls.powershell is None:
            raise unittest.SkipTest("Windows PowerShell is unavailable")

    def setUp(self) -> None:
        parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(
            prefix="x9-v73-install-", dir=parent
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.codex_home = self.root / "codex-home"
        self.project = self.root / "project"
        self.project.mkdir(parents=True)
        self.validator = self.root / "quick_validate.py"
        self.validator.write_text(
            "raise SystemExit(0)\n", encoding="utf-8", newline="\n"
        )

    def seed_installed_skills(self) -> dict[str, bytes]:
        expected: dict[str, bytes] = {}
        for index, skill in enumerate(SKILLS):
            raw = f"original:{index}:{skill}\n".encode("utf-8")
            target = self.codex_home / "skills" / skill / "ORIGINAL.txt"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            expected[skill] = raw
        return expected

    def install(
        self, *, include_skill_validator: bool = True
    ) -> subprocess.CompletedProcess[str]:
        command = [
            self.powershell,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(INSTALLER),
            "-CodexHome",
            str(self.codex_home),
            "-ProjectRoot",
            str(self.project),
            "-Python",
            sys.executable,
        ]
        if include_skill_validator:
            command.extend(["-SkillValidator", str(self.validator)])
        command.append("-Apply")
        return subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_temporary_install_preserves_backup_and_initializes_v3(self):
        original = self.seed_installed_skills()
        completed = self.install()
        self.assertEqual(
            0, completed.returncode, completed.stdout + completed.stderr
        )

        snapshot = json.loads(
            (
                self.project
                / ".devad"
                / "manager"
                / "loop-lite"
                / "SNAPSHOT.json"
            ).read_bytes()
        )
        profile = json.loads(
            (
                self.project
                / ".devad"
                / "manager"
                / "loop-lite"
                / "PROJECT_PROFILE.json"
            ).read_bytes()
        )
        self.assertEqual("x9-loop-lite-snapshot-v3", snapshot["schema"])
        self.assertEqual("x9-loop-project-profile-v1", profile["schema"])
        backups = list((self.codex_home / "x9-install-backups").iterdir())
        self.assertEqual(1, len(backups))
        for skill, raw in original.items():
            self.assertTrue(
                (self.codex_home / "skills" / skill / "SKILL.md").is_file()
            )
            self.assertEqual(
                raw, (backups[0] / skill / "ORIGINAL.txt").read_bytes()
            )

    def test_omitted_validator_does_not_auto_discover_codex_home(self):
        marker = self.root / "auto-discovered-validator-ran.txt"
        candidate = (
            self.codex_home
            / "skills"
            / ".system"
            / "skill-creator"
            / "scripts"
            / "quick_validate.py"
        )
        candidate.parent.mkdir(parents=True)
        candidate.write_text(
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('ran', encoding='utf-8')\n"
            "raise SystemExit(97)\n",
            encoding="utf-8",
            newline="\n",
        )

        completed = self.install(include_skill_validator=False)
        output = completed.stdout + completed.stderr
        self.assertEqual(0, completed.returncode, output)
        self.assertIn(
            "PASS: installed X9 Loop Style plus experimental Code trial and sixteen skills",
            output,
        )
        self.assertIn(
            "VALIDATOR_DEPENDENCY_UNAVAILABLE: optional external "
            "quick_validate was not supplied; dependency-free package "
            "validation plus manifest verification remain active.",
            output,
        )
        self.assertFalse(marker.exists())
        for skill in SKILLS:
            self.assertTrue(
                (self.codex_home / "skills" / skill / "SKILL.md").is_file()
            )

    def test_project_precondition_failure_restores_every_original_byte(self):
        original = self.seed_installed_skills()
        existing = self.project / ".devad" / "OWNER.txt"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"existing-project-truth\n")

        completed = self.install()
        self.assertNotEqual(0, completed.returncode)
        self.assertIn(
            "Project .devad exists", completed.stdout + completed.stderr
        )
        self.assertEqual(b"existing-project-truth\n", existing.read_bytes())
        for skill, raw in original.items():
            target = self.codex_home / "skills" / skill
            self.assertEqual(raw, (target / "ORIGINAL.txt").read_bytes())
            self.assertFalse((target / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
