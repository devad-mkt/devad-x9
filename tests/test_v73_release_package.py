from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class V73LiteReleasePackageTests(unittest.TestCase):
    def test_package_metadata_identifies_v73_lite_and_current_roles(self):
        kit = json.loads((ROOT / "kit.manifest.json").read_text(encoding="utf-8"))
        skills = json.loads((ROOT / "skills.index.json").read_text(encoding="utf-8"))

        release_identity = " ".join(
            str(kit.get(field, ""))
            for field in ("schema", "version", "name", "display_name", "release")
        ).casefold()
        self.assertIn("v7.3", release_identity)
        self.assertIn("lite", release_identity)

        role_identity = json.dumps(skills, sort_keys=True).casefold()
        self.assertIn("linker", role_identity)
        self.assertIn("thinker", role_identity)

    def test_installer_and_project_migration_name_the_lite_target(self):
        installer = (ROOT / "scripts" / "install-suite.ps1").read_text(
            encoding="utf-8"
        ).casefold()
        migration = (ROOT / "scripts" / "migrate_project.py").read_text(
            encoding="utf-8"
        ).casefold()

        self.assertIn("v7.3", installer)
        self.assertIn("lite", installer)
        self.assertNotIn("x9 loop lite v6 source", installer)

        self.assertIn("v7.3", migration)
        self.assertIn("lite", migration)
        self.assertNotIn("x9 loop lite v6 activation packet", migration)
        self.assertNotIn("x9 loop lite v6 old migration report", migration)

    def test_template_and_validator_use_v3_profile_bound_state(self):
        loop_lite = (
            ROOT / "templates" / "x9-project" / ".devad" / "manager" / "loop-lite"
        )
        snapshot = json.loads((loop_lite / "SNAPSHOT.json").read_text(encoding="utf-8"))
        action = json.loads(
            (loop_lite / "contracts" / "ACTION.json").read_text(encoding="utf-8")
        )
        validator = (ROOT / "scripts" / "validate_suite.py").read_text(
            encoding="utf-8"
        )

        self.assertEqual("x9-loop-lite-snapshot-v3", snapshot.get("schema"))
        self.assertTrue(
            {"project_profile_id", "work_order_id"}.issubset(action),
            action,
        )
        self.assertIn("x9-loop-lite-snapshot-v3", validator)
        self.assertIn('"project_profile_id"', validator)

    def test_source_manifest_builder_includes_tracked_devad_content(self):
        builder = load_module(
            "v73_release_build_source_manifest",
            ROOT / "scripts" / "build_source_manifest.py",
        )
        with tempfile.TemporaryDirectory(prefix="x9-v73-manifest-") as directory:
            package = Path(directory)
            feature = package / ".devad" / "features" / "feature.md"
            feature.parent.mkdir(parents=True)
            feature.write_text("tracked feature\n", encoding="utf-8", newline="\n")
            (package / "source.py").write_text(
                "value = 1\n", encoding="utf-8", newline="\n"
            )
            subprocess.run(
                ["git", "init", "--quiet"], cwd=package, check=True
            )
            subprocess.run(
                [
                    "git", "-c", "core.autocrlf=false", "add", "--",
                    ".devad/features/feature.md", "source.py",
                ],
                cwd=package, check=True,
            )

            old_root, old_output = builder.ROOT, builder.OUTPUT
            generated_manifest = package / "SOURCE_MANIFEST.sha256"
            try:
                builder.ROOT = package
                builder.OUTPUT = generated_manifest
                self.assertEqual(0, builder.main())
            finally:
                builder.ROOT, builder.OUTPUT = old_root, old_output

            entries = generated_manifest.read_text(encoding="utf-8").splitlines()

        self.assertTrue(
            any(line.endswith("  .devad/features/feature.md") for line in entries),
            entries,
        )

    def test_source_manifest_separates_self_host_state_from_devad_source(self):
        builder = load_module(
            "v73_release_build_source_manifest_self_host",
            ROOT / "scripts" / "build_source_manifest.py",
        )
        validator = load_module(
            "v73_release_validate_suite_self_host",
            ROOT / "scripts" / "validate_suite.py",
        )
        with tempfile.TemporaryDirectory(prefix="x9-v73-self-host-manifest-") as directory:
            package = Path(directory)
            source_paths = (
                ".devad/features/feature.md",
                ".devad/import/program.json",
                ".devad/memory/MEMORY.md",
                ".devad/managerial/source.md",
            )
            runtime_paths = (
                ".devad/manager/loop-lite/SNAPSHOT.json",
                ".devad/workers/worker-1/proof/result.json",
            )
            for relative in source_paths + runtime_paths:
                path = package / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"{relative}\n", encoding="utf-8", newline="\n")

            old_root, old_output = builder.ROOT, builder.OUTPUT
            generated_manifest = package / "SOURCE_MANIFEST.sha256"
            try:
                builder.ROOT = package
                builder.OUTPUT = generated_manifest
                self.assertEqual(0, builder.main())
            finally:
                builder.ROOT, builder.OUTPUT = old_root, old_output

            entries = generated_manifest.read_text(encoding="utf-8").splitlines()
            listed = {line.split("  ", 1)[1] for line in entries}
            self.assertTrue(set(source_paths).issubset(listed), listed)
            self.assertTrue(set(runtime_paths).isdisjoint(listed), listed)
            self.assertEqual(builder.PROJECT_STATE_ROOTS, validator.PROJECT_STATE_ROOTS)

            old_root = validator.ROOT
            errors: list[str] = []
            try:
                validator.ROOT = package
                validator.validate_manifest(errors)
            finally:
                validator.ROOT = old_root

        self.assertEqual([], errors)

    def test_manifest_validator_rejects_a_listed_self_host_state_file(self):
        validator = load_module(
            "v73_release_validate_suite_listed_self_host",
            ROOT / "scripts" / "validate_suite.py",
        )
        with tempfile.TemporaryDirectory(prefix="x9-v73-listed-self-host-") as directory:
            package = Path(directory)
            runtime = package / ".devad" / "manager" / "loop-lite" / "loop.db"
            runtime.parent.mkdir(parents=True)
            runtime.write_bytes(b"runtime-state")
            digest = hashlib.sha256(runtime.read_bytes()).hexdigest()
            (package / "SOURCE_MANIFEST.sha256").write_text(
                f"{digest}  .devad/manager/loop-lite/loop.db\n",
                encoding="utf-8",
                newline="\n",
            )

            old_root = validator.ROOT
            errors: list[str] = []
            try:
                validator.ROOT = package
                validator.validate_manifest(errors)
            finally:
                validator.ROOT = old_root

        self.assertTrue(
            any("manifest entry is not an eligible source file" in error for error in errors),
            errors,
        )
    def test_manifest_validator_rejects_an_unlisted_source_file(self):
        validator = load_module(
            "v73_release_validate_suite",
            ROOT / "scripts" / "validate_suite.py",
        )
        with tempfile.TemporaryDirectory(prefix="x9-v73-unlisted-") as directory:
            package = Path(directory)
            listed = package / "listed.txt"
            listed.write_text("listed\n", encoding="utf-8", newline="\n")
            unlisted = package / "unlisted.txt"
            unlisted.write_text("unlisted\n", encoding="utf-8", newline="\n")
            digest = hashlib.sha256(listed.read_bytes()).hexdigest()
            (package / "SOURCE_MANIFEST.sha256").write_text(
                f"{digest}  listed.txt\n", encoding="utf-8", newline="\n"
            )

            old_root = validator.ROOT
            errors: list[str] = []
            try:
                validator.ROOT = package
                validator.validate_manifest(errors)
            finally:
                validator.ROOT = old_root

        self.assertTrue(any("unlisted.txt" in error for error in errors), errors)

    def test_release_gate_entrypoint_lists_every_required_gate(self):
        candidates = (
            ROOT / "scripts" / "release_gate.py",
            ROOT / "scripts" / "release-gate.py",
            ROOT / "scripts" / "release_gate.ps1",
            ROOT / "scripts" / "release-gate.ps1",
        )
        entrypoint = next((path for path in candidates if path.is_file()), None)
        self.assertIsNotNone(entrypoint, "missing deterministic release-gate entrypoint")
        text = entrypoint.read_text(encoding="utf-8").casefold()

        required_markers = {
            "full suite": ("unittest",),
            "skill validation": ("quick_validate",),
            "secret scan": ("secret-scan",),
            "source manifest": ("build_source_manifest", "validate_suite"),
            "diff check": ("diff --check",),
            "temporary install": ("install-suite", "temp"),
            "migration rollback": ("migrate-v3", "rollback-v7"),
        }
        for gate, markers in required_markers.items():
            with self.subTest(gate=gate):
                self.assertTrue(
                    all(marker in text for marker in markers),
                    f"release gate does not list {gate}: {markers}",
                )


if __name__ == "__main__":
    unittest.main()
