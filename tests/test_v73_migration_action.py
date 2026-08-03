from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sqlite3
import tempfile
import unittest
from pathlib import Path, PurePosixPath

from tests import test_v73_migration as migration_fixture


class V73PreparedActionMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loopctl = migration_fixture.load_loopctl()

    def setUp(self):
        temp_parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        temp_parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(
            prefix="x9v73-action-migrate-", dir=temp_parent
        )
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir(parents=True)
        (self.repo / ".gitignore").write_text(
            ".devad/manager/loop-lite/\n", encoding="utf-8"
        )
        subprocess.run(
            ["git", "init"], cwd=self.repo, check=True,
            capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "fixture@example.invalid"],
            cwd=self.repo, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "X9 Fixture"],
            cwd=self.repo, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "add", ".gitignore"], cwd=self.repo, check=True,
            capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "fixture"], cwd=self.repo, check=True,
            capture_output=True, text=True,
        )
        self.base_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        self.repo.mkdir(parents=True, exist_ok=True)
        self.controller = self.loopctl.Controller(
            self.repo,
            now_fn=lambda: "2026-07-16T12:00:00Z",
        )

    def _write_reference(self, relative: str, raw: bytes) -> None:
        target = self.repo / Path(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def _write_v2_prepared_action(self) -> dict[str, object]:
        self.controller.root.mkdir(parents=True, exist_ok=True)
        controller = self.controller
        contract = self.loopctl._load_v7_contract()
        connection = sqlite3.connect(controller.db_path)
        connection.row_factory = sqlite3.Row
        self.loopctl.Controller._enable_v7_connection(connection)
        try:
            self.loopctl.Controller._schema_v1(connection)
            self.loopctl.Controller._upgrade_schema_v2(connection)
            connection.execute(
                "UPDATE meta SET value='11' WHERE key='generation'"
            )
            connection.executemany(
                "INSERT INTO actors VALUES(?,?,?,?)",
                [
                    ("linker", "LINX", "AI - LINX v7", "Unknown"),
                    ("worker", "WORKER", "AI - WORKER", "Unknown"),
                ],
            )
            connection.execute(
                "INSERT INTO worktrees VALUES(?,?,?)",
                ("x9-loop", str(self.repo), "x9-loop-private"),
            )
            connection.execute(
                "INSERT INTO programs VALUES(?,?,?,?,?,?,?)",
                (
                    "program-v7",
                    ".devad/packets/PROGRAM_PACKET.json",
                    "1" * 64,
                    self.base_sha,
                    "2" * 64,
                    "ACTIVE",
                    "2026-07-16T11:58:00Z",
                ),
            )
            connection.execute(
                "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    "task-v7",
                    "worker",
                    "x9-loop",
                    self.base_sha,
                    ".devad/owner/task.json",
                    "3" * 64,
                    "[]",
                    "finish the bounded slice",
                    "ACTIVE",
                ),
            )
            connection.execute(
                "INSERT INTO work_orders VALUES(?,?,?,?,?,?,?,?)",
                (
                    "wo-v7-existing",
                    "task-v7",
                    "worker",
                    ".devad/work-orders/wo-v7-existing.json",
                    "4" * 64,
                    "program-v7",
                    "ACTIVE",
                    "2026-07-16T11:59:00Z",
                ),
            )
            connection.execute(
                "INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    "dispatch-v7-existing",
                    "task-v7",
                    "linker",
                    "worker",
                    "5" * 64,
                    '{"kind":"v7-work-order"}',
                    None,
                    "PREPARED",
                    "2026-07-16T12:00:00Z",
                ),
            )
            old_action = {
                "action": "SEND_WORK_ORDER",
                "action_id": "act-v7-existing",
                "attempt": 1,
                "dispatch_id": "dispatch-v7-existing",
                "must_record_transport": True,
                "schema": "x9-loop-action-v2",
                "target_actor_id": "worker",
                "target_role": "WORKER",
                "task_id": "task-v7",
                "work_order_path": ".devad/work-orders/wo-v7-existing.json",
                "work_order_sha256": "4" * 64,
            }
            connection.execute(
                "INSERT INTO outbox VALUES(?,?)",
                (
                    "dispatch-v7-existing",
                    json.dumps(
                        old_action,
                        ensure_ascii=False,
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                ),
            )
            connection.commit()
            self.loopctl.Controller._validate_v2_schema_shape(connection)
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
        bundle = capacity.build_bundle(
            generation=11,
            columns=self.loopctl.V2_SNAPSHOT_COLUMNS,
            tables=tables,
            recovery_worktrees=[
                {"path": str(self.repo), "worktree_id": "x9-loop"}
            ],
            completed_task_ids=[],
            dispatch_attempts={"dispatch-v7-existing": 1},
            call_receipt_archive={
                "count": 0,
                "root_sha256": hashlib.sha256(
                    contract.canonical_json_bytes([])
                ).hexdigest(),
            },
            current_snapshot_raw=capacity.canonical_bytes(
                {
                    "generation": 11,
                    "previous_generation": None,
                    "schema": "x9-loop-lite-snapshot-v3",
                }
            ),
        )
        for shard in bundle["shards"]:
            self._write_reference(shard["reference"]["path"], shard["raw"])
        controller.snapshot_path.write_bytes(bundle["root_raw"])
        action_raw = contract.canonical_json_bytes(old_action)
        controller.action_path.parent.mkdir(parents=True, exist_ok=True)
        controller.action_path.write_bytes(action_raw)
        return {
            "action": action_raw,
            "database": controller.db_path.read_bytes(),
            "snapshot": bundle["root_raw"],
        }

    def test_prepared_v7_action_is_upgraded_and_exactly_rollback_safe(self):
        original = self._write_v2_prepared_action()

        migration = self.controller.migrate_v2_to_v3()
        self.assertEqual("PASS", migration["status"])

        profile_raw = self.controller.project_profile_path.read_bytes()
        profile = json.loads(profile_raw)
        contract = self.loopctl._load_v7_contract()
        self.assertEqual(contract.canonical_json_bytes(profile), profile_raw)
        profile_id = profile["project_profile_id"]

        action_raw = self.controller.action_path.read_bytes()
        action = json.loads(action_raw)
        self.assertLess(len(action_raw), 4096)
        self.assertEqual(contract.canonical_json_bytes(action), action_raw)
        self.assertEqual("x9-loop-action-v2", action["schema"])
        self.assertEqual("dispatch-v7-existing", action["dispatch_id"])
        self.assertEqual("wo-v7-existing", action["work_order_id"])
        self.assertEqual(profile_id, action["project_profile_id"])

        connection = sqlite3.connect(self.controller.db_path)
        connection.row_factory = sqlite3.Row
        try:
            self.assertEqual(
                ["wo-v7-existing"],
                [
                    row["work_order_id"]
                    for row in connection.execute(
                        "SELECT work_order_id FROM work_orders"
                    )
                ],
            )
            dispatch = connection.execute(
                "SELECT dispatch_id,status FROM dispatches"
            ).fetchone()
            self.assertEqual(
                ("dispatch-v7-existing", "PREPARED"), tuple(dispatch)
            )
            outbox = connection.execute(
                "SELECT dispatch_id,payload FROM outbox"
            ).fetchall()
            self.assertEqual(1, len(outbox))
            self.assertEqual("dispatch-v7-existing", outbox[0]["dispatch_id"])
            self.assertEqual(action, json.loads(outbox[0]["payload"]))
            self.assertEqual(
                profile_id,
                connection.execute(
                    "SELECT value FROM meta WHERE key='project_profile_id'"
                ).fetchone()[0],
            )
        finally:
            connection.close()

        rollback = self.controller.rollback_to_v7(migration["recovery_id"])
        self.assertEqual("PASS", rollback["status"])
        self.assertEqual(original["database"], self.controller.db_path.read_bytes())
        self.assertEqual(original["snapshot"], self.controller.snapshot_path.read_bytes())
        self.assertEqual(original["action"], self.controller.action_path.read_bytes())
        self.assertFalse(self.controller.project_profile_path.exists())


if __name__ == "__main__":
    unittest.main()
