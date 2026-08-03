from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import unittest

from tests import test_loop_lite_v7_controller as v7_fixture


class V73ResultSchemaRepairTests(unittest.TestCase):
    """Regression for a V7 Worker that returns an obsolete V1 receipt."""

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
        self.contract = self.fixture.loopctl._load_v7_contract()

        connection = self.controller._connect()
        try:
            self.original_action = json.loads(
                connection.execute(
                    "SELECT payload FROM outbox WHERE dispatch_id=?",
                    (self.order["dispatch_id"],),
                ).fetchone()[0]
            )
        finally:
            connection.close()
        self.controller.record_delivery(
            self.order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        self.profile_id = json.loads(
            self.controller.project_profile_path.read_text(encoding="utf-8")
        )["project_profile_id"]

    def _canonical_receipt(self, document: dict) -> tuple[Path, bytes]:
        relative = (
            f".devad/workers/worker/receipts/{document['event_id']}.json"
        )
        path = self.fixture.repo / Path(*PurePosixPath(relative).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = self.contract.canonical_json_bytes(document)
        path.write_bytes(raw)
        return path, raw

    def _inbox_event(
        self,
        *,
        event_id: str,
        result_path: str,
        result_sha256: str,
    ) -> tuple[Path, bytes]:
        # The deployed V1 Worker cannot pass the current V2-only
        # worker_finalizer.  This directly seals the canonical inbox envelope
        # that an older Worker/Linx pair already emitted in production.
        event = {
            "event_id": event_id,
            "event_type": "WORKER_RESULT",
            "payload_ref": {
                "path": result_path,
                "sha256": result_sha256,
            },
            "project_profile_id": self.profile_id,
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "worker",
            "source_role": "WORKER",
        }
        raw = self.contract.canonical_json_bytes(event)
        path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / event_id
            / "INBOX_EVENT.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path, raw

    def _implementation_state(self) -> dict:
        connection = self.controller._connect()
        try:
            status = connection.execute(
                "SELECT t.status,wo.status,d.status FROM tasks t "
                "JOIN work_orders wo ON wo.task_id=t.task_id "
                "JOIN dispatches d ON d.task_id=t.task_id "
                "WHERE t.task_id=? AND d.dispatch_id=?",
                (self.order["task_id"], self.order["dispatch_id"]),
            ).fetchone()
            return {
                "statuses": tuple(status),
                "dispatches": connection.execute(
                    "SELECT COUNT(*) FROM dispatches WHERE task_id=?",
                    (self.order["task_id"],),
                ).fetchone()[0],
                "deliveries": connection.execute(
                    "SELECT COUNT(*) FROM deliveries WHERE dispatch_id=?",
                    (self.order["dispatch_id"],),
                ).fetchone()[0],
                "events": connection.execute(
                    "SELECT COUNT(*) FROM events WHERE dispatch_id=?",
                    (self.order["dispatch_id"],),
                ).fetchone()[0],
                "call_reservations": connection.execute(
                    "SELECT COUNT(*) FROM call_reservations "
                    "WHERE work_order_id=?",
                    (self.order["work_order_id"],),
                ).fetchone()[0],
                "call_receipts": connection.execute(
                    "SELECT COUNT(*) FROM call_receipts "
                    "WHERE work_order_id=?",
                    (self.order["work_order_id"],),
                ).fetchone()[0],
            }
        finally:
            connection.close()

    def _registered_rejection(self, event_id: str) -> tuple:
        connection = self.controller._connect()
        try:
            row = connection.execute(
                "SELECT event_id,task_id,dispatch_id,event_sha256,payload,status "
                "FROM inbox WHERE event_id=?",
                (event_id,),
            ).fetchone()
            self.assertIsNotNone(row)
            return tuple(row)
        finally:
            connection.close()

    def _product_diff(self) -> str:
        completed = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "src"],
            cwd=self.fixture.repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        return completed.stdout.strip()

    def test_v1_result_gets_one_repair_action_then_new_v2_event_completes(self):
        legacy_event_id = "event-v73-obsolete-v1"
        legacy = {
            "changed_files": [],
            "dispatch_id": self.order["dispatch_id"],
            "event_id": legacy_event_id,
            "outcome": "COMPLETE",
            "packet_sha256": self.order["work_order_sha256"],
            "proof": [],
            "role": "WORKER",
            "schema": "x9-loop-lite-result-v1",
            "task_id": self.order["task_id"],
            "worker_id": "worker",
        }
        legacy_path, legacy_raw = self._canonical_receipt(legacy)
        legacy_sha256 = hashlib.sha256(legacy_raw).hexdigest()
        relative_legacy = legacy_path.relative_to(self.fixture.repo).as_posix()
        legacy_event_path, legacy_event_raw = self._inbox_event(
            event_id=legacy_event_id,
            result_path=relative_legacy,
            result_sha256=legacy_sha256,
        )

        before_reject = self._implementation_state()
        head_before = v7_fixture.run(
            "git", "rev-parse", "HEAD", cwd=self.fixture.repo
        )
        first = self.controller.run_once(legacy_event_path)

        self.assertEqual("RESULT_SCHEMA_REPAIR", first["status"])
        self.assertEqual(before_reject, self._implementation_state())
        self.assertEqual("", self._product_diff())
        self.assertEqual(
            head_before,
            v7_fixture.run("git", "rev-parse", "HEAD", cwd=self.fixture.repo),
        )

        repair_raw = self.controller.action_path.read_bytes()
        repair = json.loads(repair_raw)
        self.assertEqual(repair_raw, self.contract.canonical_json_bytes(repair))
        self.assertLessEqual(len(repair_raw), 4 * 1024)
        self.assertEqual(
            {
                "action": "RESULT_SCHEMA_REPAIR",
                "attempt": self.original_action["attempt"],
                "dispatch_id": self.order["dispatch_id"],
                "expected_result_schema": "x9-loop-result-v2",
                "invalid_event_id": legacy_event_id,
                "invalid_result_sha256": legacy_sha256,
                "project_profile_id": self.profile_id,
                "reason": "RESULT_FIELDS_INVALID",
                "target_actor_id": "worker",
                "target_role": "WORKER",
                "task_id": self.order["task_id"],
                "work_order_id": self.order["work_order_id"],
                "work_order_path": self.order["work_order_path"],
                "work_order_sha256": self.order["work_order_sha256"],
            },
            {key: repair.get(key) for key in {
                "action", "attempt", "dispatch_id", "expected_result_schema",
                "invalid_event_id", "invalid_result_sha256",
                "project_profile_id", "reason", "target_actor_id",
                "target_role", "task_id", "work_order_id", "work_order_path",
                "work_order_sha256",
            }},
        )
        self.assertEqual("x9-loop-action-v2", repair["schema"])
        self.assertNotEqual("SEND_WORK_ORDER", repair["action"])
        self.assertNotIn("packet", repair)

        rejected = self._registered_rejection(legacy_event_id)
        self.assertEqual(legacy_event_id, rejected[0])
        self.assertEqual(self.order["task_id"], rejected[1])
        self.assertEqual(self.order["dispatch_id"], rejected[2])
        self.assertEqual(hashlib.sha256(legacy_event_raw).hexdigest(), rejected[3])
        self.assertEqual(legacy_event_raw.decode("utf-8"), rejected[4])
        self.assertEqual("REJECTED:RESULT_FIELDS_INVALID", rejected[5])
        registered_payload = json.loads(rejected[4])
        self.assertEqual(
            legacy_sha256, registered_payload["payload_ref"]["sha256"]
        )

        # A byte-identical invalid replay is a zero-delta acknowledgement.  It
        # republishes the same repair bytes instead of retrying the bad result.
        snapshot_after_reject = self.controller.snapshot_path.read_bytes()
        state_after_reject = self._implementation_state()
        replay = self.controller.run_once(legacy_event_path)
        self.assertEqual("ALREADY_REJECTED", replay["status"])
        self.assertEqual(snapshot_after_reject, self.controller.snapshot_path.read_bytes())
        self.assertEqual(state_after_reject, self._implementation_state())
        self.assertEqual(rejected, self._registered_rejection(legacy_event_id))
        self.assertEqual(repair_raw, self.controller.action_path.read_bytes())

        corrected = self.fixture._write_v7_worker_event(
            self.controller,
            self.order,
            outcome="SUCCESS",
            event_id="event-v73-corrected-v2",
        )
        corrected_path, _ = self._inbox_event(
            event_id=corrected["event_id"],
            result_path=corrected["result_path"],
            result_sha256=corrected["result_sha256"],
        )
        self.assertNotEqual(legacy_event_id, corrected["event_id"])
        self.assertNotEqual(legacy_sha256, corrected["result_sha256"])

        # Rejected receipts are outside the active receipt root only while the
        # exact registered bytes remain unchanged.  Tampering must fail closed.
        before_tamper_attempt = self._implementation_state()
        snapshot_before_tamper_attempt = self.controller.snapshot_path.read_bytes()
        legacy_path.write_bytes(legacy_raw + b" ")
        with self.assertRaises(self.fixture.loopctl.LoopError):
            self.controller.run_once(corrected_path)
        self.assertEqual(before_tamper_attempt, self._implementation_state())
        self.assertEqual(
            snapshot_before_tamper_attempt,
            self.controller.snapshot_path.read_bytes(),
        )
        legacy_path.write_bytes(legacy_raw)

        completed = self.controller.run_once(corrected_path)
        self.assertEqual("FEATURE_DONE", completed["status"])
        self.assertEqual(legacy_raw, legacy_path.read_bytes())
        self.assertEqual(rejected, self._registered_rejection(legacy_event_id))
        self.assertEqual("", self._product_diff())

        final = self._implementation_state()
        self.assertEqual(("COMPLETE", "COMPLETE", "COMPLETE"), final["statuses"])
        self.assertEqual(1, final["dispatches"])
        self.assertEqual(before_reject["deliveries"], final["deliveries"])
        self.assertEqual(1, final["events"])
        self.assertEqual(0, final["call_reservations"])
        self.assertEqual(0, final["call_receipts"])


if __name__ == "__main__":
    unittest.main()
