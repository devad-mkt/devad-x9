from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import socket
import unittest
from unittest import mock
import urllib.request

from tests import test_loop_lite_v7_controller as v7_fixture


class V73ThinkerRunOnceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        v7_fixture.V7ControllerTests.setUpClass()

    def setUp(self) -> None:
        self.fixture = v7_fixture.V7ControllerTests(
            "test_fresh_state_is_snapshot_and_sqlite_v3"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.controller = self.fixture.controller()
        self.order = self.fixture._create_order(self.controller)
        self.controller.record_delivery(
            self.order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        self.worker_event = self.fixture._write_v7_worker_event(
            self.controller,
            self.order,
            outcome="VERIFIED_FAILURE",
            failed_verified_approaches=3,
            budget_remaining=True,
            event_id="event-v73-worker-three-proofs",
        )
        blocked = self.controller.consume_event(self.worker_event)
        self.assertEqual("HARD_BLOCKER_AFTER_2_PROOFS", blocked["status"])
        review = self.controller.record_delivery(
            self.order["dispatch_id"], "REVIEW", "task", "ack"
        )
        self.assertEqual("DELIVERED", review["status"])

    def durable_counts(self) -> tuple[int, int, int, int]:
        connection = self.controller._connect()
        try:
            return (
                int(
                    connection.execute(
                        "SELECT value FROM meta WHERE key='generation'"
                    ).fetchone()[0]
                ),
                connection.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM inbox").fetchone()[0],
            )
        finally:
            connection.close()

    def write_thinker_event(self, event_id: str) -> Path:
        contract = self.fixture.loopctl._load_v7_contract()
        actor_id = "thinker"
        decision = {
            "actor_id": actor_id,
            "decision": "PASS",
            "dispatch_id": self.order["dispatch_id"],
            "event_id": event_id,
            "packet_sha256": self.order["work_order_sha256"],
            "reason": "silent conditional review passed",
            "role": "THINX",
            "schema": "x9-loop-thinx-decision-v2",
            "task_id": self.order["task_id"],
            "worker_event_id": self.worker_event["event_id"],
            "worker_result_sha256": self.worker_event["result_sha256"],
            "work_order_id": self.order["work_order_id"],
            "work_order_sha256": self.order["work_order_sha256"],
        }
        decision_raw = contract.canonical_json_bytes(decision)
        receipt_relative = (
            f".devad/workers/{actor_id}/receipts/{event_id}.json"
        )
        receipt_path = self.fixture.repo / Path(
            *PurePosixPath(receipt_relative).parts
        )
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_bytes(decision_raw)

        profile_id = json.loads(
            self.controller.project_profile_path.read_text(encoding="utf-8")
        )["project_profile_id"]
        envelope = {
            "event_id": event_id,
            "event_type": "THINX_RESULT",
            "payload_ref": {
                "path": receipt_relative,
                "sha256": hashlib.sha256(decision_raw).hexdigest(),
            },
            "project_profile_id": profile_id,
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": actor_id,
            "source_role": "THINKER",
        }
        event_path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / event_id
            / "INBOX_EVENT.json"
        )
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_bytes(contract.canonical_json_bytes(envelope))
        return event_path

    def exercise_thinker_run_once(self, durable_role: str, event_id: str) -> None:
        self.controller.register_actor(
            "thinker", durable_role, "AI THINKER", "Unknown"
        )
        event_path = self.write_thinker_event(event_id)
        before = self.durable_counts()

        with (
            mock.patch.object(
                self.controller,
                "_consume_v7_thinx_event",
                wraps=self.controller._consume_v7_thinx_event,
            ) as deterministic_consumer,
            mock.patch.object(
                self.controller,
                "check_model_call",
                side_effect=AssertionError("model hook must not run"),
            ) as model_hook,
            mock.patch.object(
                self.controller,
                "provider_call",
                side_effect=AssertionError("provider hook must not run"),
                create=True,
            ) as provider_hook,
            mock.patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("network hook must not run"),
            ) as network_hook,
            mock.patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network hook must not run"),
            ) as urlopen_hook,
        ):
            first = self.controller.run_once(event_path)
            after_first = self.durable_counts()
            replay = self.controller.run_once(event_path)
            after_replay = self.durable_counts()

        self.assertEqual("RETRY_READY", first["status"])
        self.assertEqual("ALREADY_CONSUMED", replay["status"])
        self.assertEqual(before[0] + 1, after_first[0])
        self.assertEqual(after_first, after_replay)
        self.assertEqual(before[1], after_first[1])
        self.assertEqual(before[2] + 1, after_first[2])
        self.assertEqual(before[3] + 1, after_first[3])
        deterministic_consumer.assert_called_once()
        model_hook.assert_not_called()
        provider_hook.assert_not_called()
        network_hook.assert_not_called()
        urlopen_hook.assert_not_called()

        connection = self.controller._connect()
        try:
            self.assertEqual(
                ("CONSUMED", self.order["dispatch_id"]),
                tuple(
                    connection.execute(
                        "SELECT status,dispatch_id FROM inbox WHERE event_id=?",
                        (event_id,),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                ("RETRY_READY", "CREATED"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (self.order["task_id"],),
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

    def test_run_once_accepts_thinker_envelope_for_legacy_thinx_actor(self) -> None:
        self.exercise_thinker_run_once(
            "THINX", "event-v73-thinker-legacy-role"
        )

    def test_run_once_accepts_thinker_envelope_for_new_thinker_actor(self) -> None:
        self.exercise_thinker_run_once(
            "THINKER", "event-v73-thinker-new-role"
        )


if __name__ == "__main__":
    unittest.main()
