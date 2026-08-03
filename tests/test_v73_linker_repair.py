from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import unittest

from tests import test_loop_lite_v7_controller as v7_fixture


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "devad-x9-loop" / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SpyAdapter:
    adapter_id = "test-local-repair-v1"
    delivery_mode = "DURABLE_NONWAKING_DROP"

    def __init__(self) -> None:
        self.calls: list[tuple[bytes, str]] = []

    def deliver(self, action_bytes: bytes, action_sha256: str) -> str:
        if hashlib.sha256(action_bytes).hexdigest() != action_sha256:
            raise AssertionError("action hash mismatch")
        self.calls.append((action_bytes, action_sha256))
        return "ACKNOWLEDGED"


class V73LinkerRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        v7_fixture.V7ControllerTests.setUpClass()
        cls.linker = load_module(
            "linker_once_v73_repair_test", SCRIPTS / "linker_once.py"
        )

    def setUp(self) -> None:
        self.fixture = v7_fixture.V7ControllerTests(
            "test_fresh_state_is_snapshot_and_sqlite_v3"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.controller = self.fixture.controller()
        self.order = self.fixture._create_order(self.controller)
        self.contract = self.fixture.loopctl._load_v7_contract()
        self.profile_id = json.loads(
            self.controller.project_profile_path.read_text(encoding="utf-8")
        )["project_profile_id"]
        self.original_action_raw = self.controller.action_path.read_bytes()
        self.original_action = json.loads(self.original_action_raw)
        self.controller.record_delivery(
            self.order["dispatch_id"], "DISPATCH", "test", "ack"
        )
        self.invalid_result_raw = self._register_obsolete_result()
        self.repair_raw = self.controller.action_path.read_bytes()
        self.repair = json.loads(self.repair_raw)

    def _register_obsolete_result(self) -> bytes:
        event_id = "event-v73-obsolete-for-linker"
        result = {
            "changed_files": [],
            "dispatch_id": self.order["dispatch_id"],
            "event_id": event_id,
            "outcome": "COMPLETE",
            "packet_sha256": self.order["work_order_sha256"],
            "proof": [],
            "role": "WORKER",
            "schema": "x9-loop-lite-result-v1",
            "task_id": self.order["task_id"],
            "worker_id": "worker",
        }
        relative = f".devad/workers/worker/receipts/{event_id}.json"
        result_path = self.fixture.repo / Path(*PurePosixPath(relative).parts)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_raw = self.contract.canonical_json_bytes(result)
        result_path.write_bytes(result_raw)
        envelope = {
            "event_id": event_id,
            "event_type": "WORKER_RESULT",
            "payload_ref": {
                "path": relative,
                "sha256": hashlib.sha256(result_raw).hexdigest(),
            },
            "project_profile_id": self.profile_id,
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "worker",
            "source_role": "WORKER",
        }
        event_path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / event_id
            / "INBOX_EVENT.json"
        )
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_bytes(self.contract.canonical_json_bytes(envelope))

        result = self.controller.run_once(event_path)

        self.assertEqual("RESULT_SCHEMA_REPAIR", result["status"])
        return result_raw

    def _state(self) -> dict[str, object]:
        connection = self.controller._connect()
        try:
            statuses = connection.execute(
                "SELECT t.status,wo.status,d.status FROM tasks t "
                "JOIN work_orders wo ON wo.task_id=t.task_id "
                "JOIN dispatches d ON d.task_id=t.task_id "
                "WHERE t.task_id=? AND d.dispatch_id=?",
                (self.order["task_id"], self.order["dispatch_id"]),
            ).fetchone()
            rejected = connection.execute(
                "SELECT event_id,event_sha256,payload,status FROM inbox "
                "WHERE event_id='event-v73-obsolete-for-linker'"
            ).fetchone()
            return {
                "statuses": tuple(statuses),
                "task_count": connection.execute(
                    "SELECT COUNT(*) FROM tasks"
                ).fetchone()[0],
                "order_count": connection.execute(
                    "SELECT COUNT(*) FROM work_orders"
                ).fetchone()[0],
                "dispatch_count": connection.execute(
                    "SELECT COUNT(*) FROM dispatches"
                ).fetchone()[0],
                "call_reservations": connection.execute(
                    "SELECT COUNT(*) FROM call_reservations"
                ).fetchone()[0],
                "call_receipts": connection.execute(
                    "SELECT COUNT(*) FROM call_receipts"
                ).fetchone()[0],
                "rejected": tuple(rejected),
            }
        finally:
            connection.close()

    def _transport_repair(
        self,
        event_id: str,
        *,
        source_actor_id: str = "linx",
    ) -> tuple[Path, Path, SpyAdapter]:
        inbox = self.controller.root / "runtime" / "inbox" / event_id
        inbox.mkdir(parents=True, exist_ok=True)
        ack_path = inbox / "TRANSPORT_ACK.json"
        adapter = SpyAdapter()
        self.linker.link_once(self.controller.action_path, ack_path, adapter)
        ack_raw = ack_path.read_bytes()
        envelope = {
            "event_id": event_id,
            "event_type": "TRANSPORT_ACK",
            "payload_ref": {
                "path": ack_path.relative_to(self.fixture.repo).as_posix(),
                "sha256": hashlib.sha256(ack_raw).hexdigest(),
            },
            "project_profile_id": self.profile_id,
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": source_actor_id,
            "source_role": "LINKER",
        }
        event_path = inbox / "INBOX_EVENT.json"
        event_path.write_bytes(self.contract.canonical_json_bytes(envelope))
        return event_path, ack_path, adapter

    def test_linker_transports_repair_once_and_never_sends_invalid_result(self):
        self.assertEqual("RESULT_SCHEMA_REPAIR", self.repair["action"])
        self.assertEqual("worker", self.repair["target_actor_id"])
        self.assertEqual(
            hashlib.sha256(self.invalid_result_raw).hexdigest(),
            self.repair["invalid_result_sha256"],
        )
        event_path, ack_path, adapter = self._transport_repair(
            "event-v73-repair-ack"
        )
        del event_path

        action_sha256 = hashlib.sha256(self.repair_raw).hexdigest()
        self.assertEqual([(self.repair_raw, action_sha256)], adapter.calls)
        self.assertNotIn(self.invalid_result_raw, [raw for raw, _ in adapter.calls])
        ack_raw = ack_path.read_bytes()
        ack = json.loads(ack_raw)
        self.assertEqual(self.contract.canonical_json_bytes(ack), ack_raw)
        self.assertEqual("RESULT_SCHEMA_REPAIR", ack["action"])
        self.assertEqual(action_sha256, ack["action_sha256"])
        self.assertEqual("worker", ack["worker_id"])
        expected = {
            field: ack[field]
            for field in (
                "action_id",
                "action_sha256",
                "dispatch_id",
                "project_profile_id",
                "work_order_id",
                "work_order_sha256",
                "worker_id",
            )
        }
        self.assertEqual(
            ack,
            self.contract.validate_transport_ack(
                ack_raw, hashlib.sha256(ack_raw).hexdigest(), expected
            ),
        )

        first_call_count = len(adapter.calls)
        replay = self.linker.link_once(
            self.controller.action_path, ack_path, adapter
        )
        self.assertEqual("ALREADY_ACKNOWLEDGED", replay["status"])
        self.assertEqual(first_call_count + 1, len(adapter.calls))

    def test_controller_acknowledges_only_repair_without_new_attempt(self):
        before = self._state()
        rejected_before = before.pop("rejected")
        event_path, ack_path, adapter = self._transport_repair(
            "event-v73-repair-controller-ack"
        )
        ack = json.loads(ack_path.read_bytes())

        result = self.controller.run_once(event_path)

        self.assertEqual("CONSUMED", result["status"])
        self.assertEqual("RESULT_SCHEMA_REPAIR", ack["action"])
        self.assertEqual([(self.repair_raw, hashlib.sha256(self.repair_raw).hexdigest())], adapter.calls)
        after = self._state()
        rejected_after = after.pop("rejected")
        self.assertEqual(before, after)
        self.assertEqual(
            rejected_before[:3], rejected_after[:3]
        )
        self.assertEqual(
            "REJECTED:RESULT_FIELDS_INVALID", rejected_before[3]
        )
        self.assertEqual(
            "REPAIR_ACKNOWLEDGED:RESULT_FIELDS_INVALID", rejected_after[3]
        )
        current_action = json.loads(self.controller.action_path.read_bytes())
        self.assertEqual("WAIT", current_action["action"])
        self.assertEqual("repair-acknowledged", current_action["reason"])
        connection = self.controller._connect()
        try:
            self.assertEqual(
                ("CONSUMED", self.order["dispatch_id"]),
                tuple(
                    connection.execute(
                        "SELECT status,dispatch_id FROM inbox WHERE event_id=?",
                        ("event-v73-repair-controller-ack",),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                ("RESULT_SCHEMA_REPAIR", "LINKER", "ACKNOWLEDGED"),
                tuple(
                    connection.execute(
                        "SELECT phase,method,result FROM deliveries "
                        "WHERE dispatch_id=? ORDER BY id DESC LIMIT 1",
                        (self.order["dispatch_id"],),
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

    def test_repair_ack_must_come_from_original_dispatch_linker(self):
        self.controller.register_actor(
            "other-linx", "LINX", "OTHER LINKER", "Unknown"
        )
        before = self._state()
        action_before = self.controller.action_path.read_bytes()
        event_path, _, _ = self._transport_repair(
            "event-v73-repair-wrong-linker",
            source_actor_id="other-linx",
        )

        with self.assertRaisesRegex(
            self.fixture.loopctl.DeliveryError, "REPAIR_ACTION_INACTIVE"
        ):
            self.controller.run_once(event_path)

        self.assertEqual(before, self._state())
        self.assertEqual(action_before, self.controller.action_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
