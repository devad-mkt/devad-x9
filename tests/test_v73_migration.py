from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
LOOPCTL = ROOT / "skills" / "devad-x9-loop" / "scripts" / "loopctl.py"


def load_loopctl():
    name = "loopctl_v73_migration_under_test"
    spec = importlib.util.spec_from_file_location(name, LOOPCTL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {LOOPCTL}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class V73MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loopctl = load_loopctl()

    def setUp(self):
        temp_parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        temp_parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="x9v73-migrate-", dir=temp_parent)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir(parents=True)
        self.controller = self.loopctl.Controller(
            self.repo,
            now_fn=lambda: "2026-07-16T12:00:00Z",
        )

    def _write_reference(self, relative: str, raw: bytes) -> None:
        target = self.repo / Path(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def _write_authentic_v7_state(self) -> dict[str, object]:
        controller = self.controller
        controller.root.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(controller.db_path)
        connection.row_factory = sqlite3.Row
        self.loopctl.Controller._enable_v7_connection(connection)
        try:
            self.loopctl.Controller._schema_v1(connection)
            self.loopctl.Controller._upgrade_schema_v2(connection)
            connection.execute("UPDATE meta SET value='7' WHERE key='generation'")
            connection.execute(
                "INSERT INTO actors VALUES(?,?,?,?)",
                ("linx", "LINX", "AI - LINX v7", "Unknown"),
            )
            connection.execute(
                "INSERT INTO actors VALUES(?,?,?,?)",
                ("worker", "WORKER", "AI - WORKER", "Unknown"),
            )
            connection.execute(
                "INSERT INTO worktrees VALUES(?,?,?)",
                ("x9-loop", str(self.repo), "x9-loop-private"),
            )
            connection.execute(
                "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    "task-complete",
                    "worker",
                    "x9-loop",
                    "a" * 40,
                    ".devad/owner/task.json",
                    "b" * 64,
                    "[]",
                    "fixture complete",
                    "COMPLETE",
                ),
            )
            connection.execute(
                "INSERT INTO metrics VALUES(?,?)",
                ("completed_task_ids", '["task-complete"]'),
            )
            connection.commit()
            self.loopctl.Controller._validate_v2_schema_shape(connection)
            v2_columns = {
                table: self.loopctl.SNAPSHOT_COLUMNS[table]
                for table in self.loopctl.V2_SNAPSHOT_TABLES
            }
            tables = {
                table: [
                    dict(row)
                    for row in connection.execute(
                        f"SELECT * FROM {table} ORDER BY 1"
                    )
                ]
                for table in self.loopctl.V2_SNAPSHOT_TABLES
            }
        finally:
            connection.close()

        capacity = self.loopctl._load_snapshot_capacity()
        contract = self.loopctl._load_v7_contract()
        layout_hint = capacity.canonical_bytes(
            {
                "generation": 7,
                "previous_generation": None,
                "schema": "x9-loop-lite-snapshot-v3",
            }
        )
        bundle = capacity.build_bundle(
            generation=7,
            columns=v2_columns,
            tables=tables,
            recovery_worktrees=[
                {"path": str(self.repo), "worktree_id": "x9-loop"}
            ],
            completed_task_ids=["task-complete"],
            dispatch_attempts={},
            call_receipt_archive={
                "count": 0,
                "root_sha256": hashlib.sha256(
                    contract.canonical_json_bytes([])
                ).hexdigest(),
            },
            current_snapshot_raw=layout_hint,
        )
        self.assertNotIn("active_shards", bundle["root"])
        self.assertEqual(
            set(self.loopctl.V2_SNAPSHOT_TABLES),
            set(bundle["root"]["tables"]),
        )
        for shard in bundle["shards"]:
            self._write_reference(shard["reference"]["path"], shard["raw"])
        controller.snapshot_path.write_bytes(bundle["root_raw"])

        action = controller._status_action("NOOP", "no-outbox")
        action_raw = contract.canonical_json_bytes(action)
        controller.action_path.parent.mkdir(parents=True, exist_ok=True)
        controller.action_path.write_bytes(action_raw)

        reference_bytes = {
            shard["reference"]["path"]: shard["raw"]
            for shard in bundle["shards"]
        }
        return {
            "action": action_raw,
            "database": controller.db_path.read_bytes(),
            "references": reference_bytes,
            "snapshot": bundle["root_raw"],
            "v2_columns": v2_columns,
        }

    def _next_artifacts(self) -> list[Path]:
        controller = self.controller
        return [
            Path(str(controller.db_path) + ".next"),
            Path(str(controller.db_path) + ".next-wal"),
            Path(str(controller.db_path) + ".next-shm"),
            Path(str(controller.snapshot_path) + ".next"),
        ]

    def test_public_v2_v3_migration_api_surface_exists(self):
        missing = [
            name
            for name in ("migrate_v2_to_v3", "rollback_to_v7")
            if not callable(getattr(self.controller, name, None))
        ]
        self.assertEqual([], missing)

    def test_decoder_accepts_authentic_v7_bundle_and_synthesizes_empty_inbox(self):
        original = self._write_authentic_v7_state()
        decoded = self.controller._decode_snapshot(original["snapshot"])
        self.assertEqual(7, decoded["generation"])
        self.assertEqual([], decoded["tables"]["inbox"])
        self.assertEqual(
            {"inbox", *self.loopctl.V2_SNAPSHOT_TABLES},
            set(decoded["tables"]),
        )
        self.assertEqual(
            "task-complete",
            decoded["tables"]["tasks"][0]["task_id"],
        )

    def test_v2_to_v3_is_side_by_side_and_exactly_rollback_safe(self):
        original = self._write_authentic_v7_state()
        result = self.controller.migrate_v2_to_v3()
        self.assertEqual("PASS", result["status"])
        self.assertEqual(8, result["migration_generation"])
        self.assertEqual(
            hashlib.sha256(original["snapshot"]).hexdigest(),
            result["source_snapshot_sha256"],
        )
        self.assertFalse(any(path.exists() for path in self._next_artifacts()))

        connection = sqlite3.connect(self.controller.db_path)
        try:
            self.assertEqual(3, connection.execute("PRAGMA user_version").fetchone()[0])
            self.assertEqual(
                8,
                int(
                    connection.execute(
                        "SELECT value FROM meta WHERE key='generation'"
                    ).fetchone()[0]
                ),
            )
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM inbox").fetchone()[0])
        finally:
            connection.close()

        rollback = self.controller.rollback_to_v7(result["recovery_id"])
        self.assertEqual("PASS", rollback["status"])
        self.assertEqual(original["database"], self.controller.db_path.read_bytes())
        self.assertEqual(original["snapshot"], self.controller.snapshot_path.read_bytes())
        self.assertEqual(original["action"], self.controller.action_path.read_bytes())
        self.assertFalse(any(path.exists() for path in self._next_artifacts()))
        for relative, expected in original["references"].items():
            actual = self.repo / Path(*PurePosixPath(relative).parts)
            self.assertEqual(expected, actual.read_bytes())

    def test_migration_fences_existing_controller_connection_before_source_recheck(self):
        self._write_authentic_v7_state()
        existing = sqlite3.connect(
            self.controller.db_path, isolation_level=None
        )
        self.controller._enable_v7_connection(
            existing,
            lambda: 0
            if self.controller.migration_state_path.exists()
            else 1,
        )
        original_write_state = self.controller._write_migration_state
        blocked_errors: list[str] = []

        def write_state_and_probe(**kwargs):
            original_write_state(**kwargs)
            if (
                kwargs["operation"] == "MIGRATE_V3"
                and kwargs["phase"] == "PREPARED"
            ):
                try:
                    with self.assertRaises(sqlite3.DatabaseError) as caught:
                        existing.execute(
                            "UPDATE meta SET value=value WHERE key='generation'"
                        )
                    blocked_errors.append(str(caught.exception))
                finally:
                    existing.close()

        self.controller._write_migration_state = write_state_and_probe
        try:
            result = self.controller.migrate_v2_to_v3()
        finally:
            existing.close()

        self.assertEqual("PASS", result["status"])
        self.assertEqual(1, len(blocked_errors))
        self.assertIn("V7_WRITE_FENCED", blocked_errors[0])

    def test_v2_to_v3_rejects_untrusted_source_shape_without_mutation(self):
        original = self._write_authentic_v7_state()
        connection = sqlite3.connect(self.controller.db_path)
        try:
            connection.execute("DROP TRIGGER x9_v7_write_fence_update")
            connection.commit()
        finally:
            connection.close()
        malformed = self.controller.db_path.read_bytes()

        with self.assertRaises(self.loopctl.StateNotDurableError):
            self.controller.migrate_v2_to_v3()

        self.assertEqual(malformed, self.controller.db_path.read_bytes())
        self.assertEqual(original["snapshot"], self.controller.snapshot_path.read_bytes())
        self.assertEqual(original["action"], self.controller.action_path.read_bytes())
        self.assertFalse(any(path.exists() for path in self._next_artifacts()))


if __name__ == "__main__":
    unittest.main()
