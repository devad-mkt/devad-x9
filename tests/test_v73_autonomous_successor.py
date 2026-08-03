from __future__ import annotations

import json
import unittest

from tests import test_v73_self_host as self_host_fixture


class V73AutonomousSuccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        self_host_fixture.V73SelfHostTests.setUpClass()

    def setUp(self) -> None:
        self.fixture = self_host_fixture.V73SelfHostTests(
            "test_self_host_bootstrap_then_preserves_three_non_overlapping_workers"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.controller = self.fixture.controller

    def generation(self) -> int:
        connection = self.controller._connect()
        try:
            return int(
                connection.execute(
                    "SELECT value FROM meta WHERE key='generation'"
                ).fetchone()[0]
            )
        finally:
            connection.close()

    def import_two_feature_program(self) -> None:
        feature_a = self.fixture.feature("bootstrap")
        feature_a.update(
            {
                "feature_id": "feature-a",
                "owner_requirement": "complete deterministic feature A",
            }
        )
        feature_b = self.fixture.feature("lane-1")
        feature_b.update(
            {
                "dependencies": ["feature-a"],
                "feature_id": "feature-b",
                "owner_requirement": "complete deterministic feature B",
                "worker_id": "worker-bootstrap",
                "worktree_id": "wt-bootstrap",
            }
        )
        metadata = {
            "feature.md": {"feature_ids": ["feature-a", "feature-b"]}
        }
        artifacts = self.fixture.importer.build_import_artifacts(
            self.fixture.repo / "import-source", metadata_by_path=metadata
        )
        self.controller.import_program(
            {
                "feature_packets": [feature_a, feature_b],
                "features": ["feature-a", "feature-b"],
                "program_id": "program-successor",
                "schema": "x9-loop-program-v1",
            },
            source_git_sha=self.fixture.base_sha,
            source_root=self.fixture.repo / "import-source",
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )

    def test_completion_atomically_publishes_one_dependency_successor(self):
        self.import_two_feature_program()
        first = self.controller.create_work_order(
            program_id="program-successor",
            stop=self.fixture.stop(),
            linx_id="linker",
            action_class="implementation",
        )
        first_action = self.controller.action_path.read_bytes()
        self.fixture.link_current_action("event-feature-a-linker-ack")
        before_completion = self.generation()

        completed = self.fixture.complete_worker(
            "bootstrap", first, "event-feature-a-worker-result"
        )

        self.assertEqual("FEATURE_DONE", completed["status"])
        self.assertEqual(before_completion + 1, self.generation())
        successor_raw = self.controller.action_path.read_bytes()
        self.assertNotEqual(first_action, successor_raw)
        successor_action = json.loads(successor_raw)
        self.assertEqual("SEND_WORK_ORDER", successor_action["action"])
        self.assertEqual("worker-bootstrap", successor_action["target_actor_id"])
        successor_order = json.loads(
            (self.fixture.repo / successor_action["work_order_path"]).read_bytes()
        )
        self.assertEqual(
            ["feature-b"],
            [
                reference["feature_id"]
                for reference in successor_order["feature_packet_refs"]
            ],
        )

        connection = self.controller._connect()
        try:
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM dispatches WHERE status='PREPARED'"
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM outbox o JOIN dispatches d "
                    "ON d.dispatch_id=o.dispatch_id WHERE d.status='PREPARED'"
                ).fetchone()[0],
            )
        finally:
            connection.close()

        event_path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / "event-feature-a-worker-result"
            / "INBOX_EVENT.json"
        )
        before_replay = self.generation()
        replay = self.controller.run_once(event_path)
        self.assertEqual("ALREADY_CONSUMED", replay["status"])
        self.assertEqual(before_replay, self.generation())
        self.assertEqual(successor_raw, self.controller.action_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
