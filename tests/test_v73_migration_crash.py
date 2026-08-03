from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath

from tests import test_v73_migration as migration_fixture


LOOPCTL = migration_fixture.LOOPCTL

class V73MigrationCrashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loopctl = migration_fixture.load_loopctl()

    def _new_v7_state(
        self, *, profile_present: bool, wal_sidecars: bool
    ) -> tuple[Path, object, dict[str, bytes]]:
        temp_parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        temp_parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(
            prefix="x9v73-crash-", dir=temp_parent
        )
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name) / "repo"
        self.repo.mkdir(parents=True)
        self.controller = self.loopctl.Controller(
            self.repo,
            now_fn=lambda: "2026-07-16T12:00:00Z",
        )
        migration_fixture.V73MigrationTests._write_authentic_v7_state(self)

        if profile_present:
            profile = {
                "project_profile_id": "profile-crash-regression",
                "schema": "x9-loop-project-profile-v1",
            }
            self.controller.project_profile_path.write_bytes(
                self.loopctl._load_v7_contract().canonical_json_bytes(profile)
            )

        if wal_sidecars:
            code = f"""
import os
import sqlite3
from pathlib import Path
db = Path(r"{self.controller.db_path}")
connection = sqlite3.connect(db)
connection.create_function("x9_v7_write_allowed", 0, lambda: 1, deterministic=True)
connection.execute("PRAGMA journal_mode=WAL")
connection.execute("PRAGMA wal_autocheckpoint=0")
connection.execute("BEGIN IMMEDIATE")
connection.execute("UPDATE meta SET value=value WHERE key='generation'")
connection.commit()
os._exit(0)
"""
            result = subprocess.run(
                [sys.executable, "-B", "-c", code],
                cwd=LOOPCTL.parents[3],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(Path(str(self.controller.db_path) + "-wal").is_file())
            self.assertTrue(Path(str(self.controller.db_path) + "-shm").is_file())

        original = {
            name: path.read_bytes()
            for name, path in self.controller._v7_recovery_paths()
            if path.is_file()
        }
        expected_names = {
            "loop.db",
            "SNAPSHOT.json",
            "ACTION.json",
        }
        if wal_sidecars:
            expected_names.update({"loop.db-wal", "loop.db-shm"})
        if profile_present:
            expected_names.add("PROJECT_PROFILE.json")
        self.assertEqual(expected_names, set(original))
        return self.repo, self.controller, original

    def _write_reference(self, relative: str, raw: bytes) -> None:
        target = self.repo / Path(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def _crash_after_active_replacement(self) -> None:
        code = f"""
import importlib.util
import os
import sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("loopctl_v73_crash_child", r"{LOOPCTL}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
controller = module.Controller(Path(r"{self.repo}"))
original_replace = module.os.replace
next_snapshot = Path(str(controller.snapshot_path) + ".next")
def crash_after_replace(source, destination):
    result = original_replace(source, destination)
    if Path(source) == next_snapshot and Path(destination) == controller.snapshot_path:
        os._exit(91)
    return result
module.os.replace = crash_after_replace
controller.migrate_v2_to_v3()
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=LOOPCTL.parents[3],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(91, result.returncode, result.stderr)

    def _crash_during_rollback(self, recovery_id: str) -> None:
        code = f"""
import importlib.util
import os
import sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("loopctl_v73_rollback_crash_child", r"{LOOPCTL}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
controller = module.Controller(Path(r"{self.repo}"))
original_replace = module.os.replace
def crash_after_replace(source, destination):
    result = original_replace(source, destination)
    source_path = Path(source)
    if (
        Path(destination) == controller.snapshot_path
        and source_path.parent.name.startswith("rollback-stage-")
    ):
        os._exit(92)
    return result
module.os.replace = crash_after_replace
controller.rollback_to_v7(r"{recovery_id}")
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=LOOPCTL.parents[3],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(92, result.returncode, result.stderr)

    def test_process_death_after_v3_replacement_leaves_durable_journal(self):
        _, controller, _ = self._new_v7_state(
            profile_present=False,
            wal_sidecars=False,
        )
        self._crash_after_active_replacement()
        self.assertTrue(
            controller.migration_state_path.is_file(),
            "V7->Lite replacement must be preceded by a durable crash journal",
        )

    def test_next_recovery_restores_exact_optional_v7_recovery_set(self):
        for profile_present in (False, True):
            with self.subTest(profile_present=profile_present):
                repo, controller, original = self._new_v7_state(
                    profile_present=profile_present,
                    wal_sidecars=True,
                )
                self._crash_after_active_replacement()

                restarted = self.loopctl.Controller(
                    repo,
                    now_fn=lambda: "2026-07-16T12:00:01Z",
                )
                recovered = restarted.recover_interrupted_migration()
                self.assertEqual("RECOVERED", recovered["status"])

                restored = {
                    name: path.read_bytes()
                    for name, path in restarted._v7_recovery_paths()
                    if path.is_file()
                }
                self.assertEqual(set(original), set(restored))
                self.assertEqual(original, restored)
                self.assertFalse(restarted.migration_state_path.exists())

    def test_process_death_during_rollback_is_exactly_recoverable(self):
        repo, controller, original = self._new_v7_state(
            profile_present=False,
            wal_sidecars=False,
        )
        migrated = controller.migrate_v2_to_v3()

        self._crash_during_rollback(migrated["recovery_id"])
        self.assertTrue(controller.migration_state_path.is_file())

        restarted = self.loopctl.Controller(
            repo,
            now_fn=lambda: "2026-07-16T12:00:02Z",
        )
        recovered = restarted.recover_interrupted_migration()
        self.assertEqual("RECOVERED", recovered["status"])
        restored = {
            name: path.read_bytes()
            for name, path in restarted._v7_recovery_paths()
            if path.is_file()
        }
        self.assertEqual(original, restored)
        self.assertFalse(restarted.migration_state_path.exists())


if __name__ == "__main__":
    unittest.main()
