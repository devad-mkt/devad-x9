from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {
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
    "evidence-to-implementation",
    "x-subagent",
    "ultra-reasoning-protocol",
    "chrome-control",
    "semantic-adoption",
}
PRIVATE_MARKERS = (
    "A-" + "haj",
    r"D:" + r"\CDX-3",
    "devadio/" + "codex-x9-backup",
    "env-" + "extra",
)


class PublicPackageTests(unittest.TestCase):
    def test_public_package_has_style_and_trial_skills(self) -> None:
        actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(actual, REQUIRED_SKILLS)

    def test_source_manifest_excludes_git_metadata(self) -> None:
        lines = (ROOT / "SOURCE_MANIFEST.sha256").read_text(encoding="utf-8-sig").splitlines()
        self.assertFalse(any("  .git/" in line for line in lines))

    def test_public_manifest_marks_distribution(self) -> None:
        manifest = json.loads((ROOT / "kit.manifest.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(manifest["distribution"], "public")
        self.assertNotIn("baseline_main_sha", manifest)

    def test_private_evidence_is_not_distributed(self) -> None:
        self.assertFalse((ROOT / "archives").exists())
        self.assertFalse((ROOT / "docs" / "commits").exists())
        self.assertFalse((ROOT / "docs" / "security").exists())
        self.assertFalse((ROOT / "benchmarks" / "model-routing" / "results").exists())

    def test_no_personal_paths_or_private_backup_remote(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path.suffix in {".pyc", ".zip"}:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                continue
            for marker in PRIVATE_MARKERS:
                self.assertNotIn(marker, text, f"private marker in {path.relative_to(ROOT)}")

    def test_readme_sets_style_as_default_and_keeps_trial_honest(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        for phrase in (
            "X9 Loop — Style G",
            "x9-loop-style",
            "Style does **not** start a Controller",
            "x9-loop-code",
            "Public distribution boundary",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
