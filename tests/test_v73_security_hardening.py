from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class V73SecurityHardeningTests(unittest.TestCase):
    def test_manifest_helpers_reject_resolved_escape_contract(self):
        builder = load("v73_secure_builder", "scripts/build_source_manifest.py")
        validator = load("v73_secure_validator", "scripts/validate_suite.py")
        self.assertTrue(callable(builder._assert_manifest_path_safe))
        self.assertTrue(callable(validator._assert_manifest_path_safe))
        self.assertTrue(callable(validator._manifest_path))
        with tempfile.TemporaryDirectory(prefix="x9-manifest-path-") as directory:
            parent = Path(directory)
            root = parent / "package"
            root.mkdir()
            outside = parent / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            with self.assertRaises(ValueError):
                builder._assert_manifest_path_safe(root, outside)
            with self.assertRaises(ValueError):
                validator._assert_manifest_path_safe(root, outside)
            with self.assertRaises(ValueError):
                validator._manifest_path(root, "../outside.txt")
            link = root / "linked.txt"
            try:
                link.symlink_to(outside)
            except OSError:
                pass
            else:
                with self.assertRaises(ValueError):
                    builder._assert_manifest_path_safe(root, link)
                with self.assertRaises(ValueError):
                    validator._manifest_path(root, "linked.txt")

    def test_package_validator_uses_runtime_decoder_for_v3_snapshot(self):
        validator = load("v73_secure_v3_validator", "scripts/validate_suite.py")
        with tempfile.TemporaryDirectory(prefix="x9-secure-v3-") as directory:
            package = Path(directory)
            project = package / "templates" / "x9-project"
            shutil.copytree(ROOT / "templates" / "x9-project" / ".devad", project / ".devad")
            loopctl = package / "skills" / "devad-x9-loop" / "scripts" / "loopctl.py"
            loopctl.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "skills" / "devad-x9-loop" / "scripts" / "loopctl.py", loopctl)
            shutil.copyfile(
                ROOT / "skills" / "devad-x9-loop" / "scripts" / "snapshot_capacity.py",
                loopctl.with_name("snapshot_capacity.py"),
            )
            snapshot = project / ".devad" / "manager" / "loop-lite" / "SNAPSHOT.json"
            payload = json.loads(snapshot.read_bytes())
            payload["table_schema_sha256"] = "0" * 64
            snapshot.write_bytes(validator._canonical_json_bytes(payload))
            old_root = validator.ROOT
            errors: list[str] = []
            try:
                validator.ROOT = package
                validator.validate_loop_lite(errors)
            finally:
                validator.ROOT = old_root
        self.assertTrue(any("SNAPSHOT_TABLE_SCHEMA_INVALID" in item for item in errors), errors)

    def test_release_tools_must_be_explicit_absolute_and_outside_package(self):
        gate = load("v73_secure_release_gate", "scripts/release_gate.py")
        with self.assertRaises(gate.GateFailure):
            gate._resolve_powershell(None)
        with self.assertRaises(gate.GateFailure):
            gate._resolve_git(None)
        with self.assertRaises(gate.GateFailure):
            gate._resolve_powershell(str(ROOT / "scripts" / "release_gate.py"))

    def test_installer_revalidates_staged_and_installed_skill_trees(self):
        text = (ROOT / "scripts" / "install-suite.ps1").read_text(encoding="utf-8")
        self.assertIn("function Assert-ManifestTree", text)
        self.assertGreaterEqual(text.count("Assert-ManifestTree"), 4)
        self.assertIn("Get-FileHash", text)

    def test_rollback_proof_is_manifest_driven_and_runs_post_rollback_doctor(self):
        gate = load("v73_secure_release_recovery", "scripts/release_gate.py")
        text = (ROOT / "scripts" / "release_gate.py").read_text(encoding="utf-8")
        self.assertIn("def _recovery_manifest_hashes", text)
        self.assertIn("temporary post-rollback doctor", text)
        self.assertNotIn("relatives = (\n        \"loop.db\"", text)
        with tempfile.TemporaryDirectory(prefix="x9-recovery-manifest-") as directory:
            project = Path(directory)
            runtime = project / ".devad" / "manager" / "loop-lite"
            recovery_id = "test-recovery"
            recovery = runtime / "recovery" / recovery_id
            recovery.mkdir(parents=True)
            active = runtime / "EXTRA.json"
            active.write_bytes(b"extra\n")
            (recovery / "EXTRA.json").write_bytes(active.read_bytes())
            reference = runtime / "snapshots" / "extra.json"
            reference.parent.mkdir(parents=True)
            reference.write_bytes(b"reference\n")
            manifest = {
                "schema": "x9-loop-v7-recovery-v1",
                "recovery_id": recovery_id,
                "files": [{
                    "name": "EXTRA.json",
                    "sha256": hashlib.sha256(active.read_bytes()).hexdigest(),
                    "size": active.stat().st_size,
                }],
                "snapshot_references": [{
                    "path": reference.relative_to(project).as_posix(),
                    "sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
                    "size": reference.stat().st_size,
                }],
            }
            (recovery / "RECOVERY.json").write_text(json.dumps(manifest), encoding="utf-8")
            expected = gate._recovery_manifest_hashes(project, recovery_id)
            self.assertEqual(set(expected), {
                "file:EXTRA.json",
                f"snapshot:{reference.relative_to(project).as_posix()}",
            })
            self.assertEqual(
                gate._active_recovery_hashes(project, expected),
                {label: row[1] for label, row in expected.items()},
            )


if __name__ == "__main__":
    unittest.main()
