from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from tests import test_loop_lite_v7_controller as v7_fixture


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "devad-x9-loop" / "scripts"


def load_worker_finalizer():
    path = SCRIPTS / "worker_finalizer.py"
    spec = importlib.util.spec_from_file_location(
        "worker_finalizer_v732_result_ready", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_linker_once():
    path = SCRIPTS / "linker_once.py"
    spec = importlib.util.spec_from_file_location(
        "linker_once_v732_result_ready", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V732ResultReadyRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        v7_fixture.V7ControllerTests.setUpClass()
        cls.finalizer = load_worker_finalizer()
        cls.linker = load_linker_once()

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

    def _complete_result(self, event_id: str = "event-v732-result-ready"):
        worker_event = self.fixture._write_v7_worker_event(
            self.controller,
            self.order,
            outcome="SUCCESS",
            event_id=event_id,
        )
        profile_id = json.loads(
            self.controller.project_profile_path.read_text(encoding="utf-8")
        )["project_profile_id"]
        event_path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / worker_event["event_id"]
            / "INBOX_EVENT.json"
        )
        self.finalizer.finalize_result(
            self.fixture.repo,
            worker_event["result_path"],
            event_path,
            project_profile_id=profile_id,
        )
        completed = self.controller.run_once(event_path)
        self.assertEqual("FEATURE_DONE", completed["status"])
        return worker_event, self.controller.result_ready_path(event_id)

    def test_completed_result_emits_one_bound_signal_and_rereads_durable_result(self):
        worker_event, signal_path = self._complete_result()
        signal_raw = signal_path.read_bytes()
        signal = json.loads(signal_raw)
        self.assertEqual(signal_raw, self.controller.loop_contract.canonical_json_bytes(signal))
        self.assertEqual("x9-loop-result-ready-v1", signal["schema"])
        self.assertEqual("READY", signal["status"])
        self.assertEqual("linx", signal["return_to_task_id"])
        self.assertEqual("WORKER", signal["source_role"])
        self.assertNotIn("model", signal)
        self.assertNotIn("thinking", signal)
        self.assertNotIn("result", signal)
        self.assertEqual(
            {
                "dispatch_id": self.order["dispatch_id"],
                "event_id": worker_event["event_id"],
                "packet_sha256": self.order["work_order_sha256"],
                "result_path": worker_event["result_path"],
                "result_sha256": worker_event["result_sha256"],
                "task_id": self.order["task_id"],
                "work_order_id": self.order["work_order_id"],
                "work_order_sha256": self.order["work_order_sha256"],
                "worker_id": "worker",
            },
            signal["expected_result_identity"],
        )

        before = self.controller.snapshot_path.read_bytes()
        reread = self.controller.consume_result_ready(
            signal_path, requester_id="linx"
        )
        replay = self.controller.consume_result_ready(
            signal_path, requester_id="linx"
        )
        self.assertEqual("RESULT_READY_ACKNOWLEDGED", reread["status"])
        self.assertEqual(reread, replay)
        self.assertEqual(worker_event["result_sha256"], reread["result_sha256"])
        self.assertEqual(before, self.controller.snapshot_path.read_bytes())

    def test_one_reconcile_then_circuit_open_incident_is_deduplicated(self):
        worker_event, signal_path = self._complete_result(
            "event-v732-reconcile"
        )
        state_path = self.controller._result_ready_state_path(
            worker_event["event_id"]
        )
        signal_path.rename(signal_path.with_name("RESULT_READY.lost.json"))
        first = self.controller.reconcile_result_ready(
            signal_path, requester_id="linx"
        )
        self.assertEqual("REDELIVERED", first["status"])
        first_signal = signal_path.read_bytes()

        signal_path.rename(signal_path.with_name("RESULT_READY.lost-2.json"))
        before_second = self.controller.snapshot_path.read_bytes()
        second = self.controller.reconcile_result_ready(
            signal_path, requester_id="linx"
        )
        self.assertEqual("CIRCUIT_OPEN", second["status"])
        incident_path = self.controller._loop_incident_path(
            worker_event["event_id"]
        )
        incident_raw = incident_path.read_bytes()
        incident = json.loads(incident_raw)
        self.assertEqual(incident_raw, self.controller.loop_contract.canonical_json_bytes(incident))
        self.assertEqual("x9-loop-incident-v1", incident["schema"])
        self.assertEqual("OPEN", incident["circuit"])
        self.assertEqual("ONE_REDELIVERY_EXHAUSTED", incident["repair_outcome"])
        self.assertEqual(worker_event["result_sha256"], incident["expected_result_identity"]["result_sha256"])
        self.assertNotIn("model", incident)
        self.assertNotIn("thinking", incident)

        third = self.controller.reconcile_result_ready(
            signal_path, requester_id="linx"
        )
        self.assertEqual("CIRCUIT_OPEN", third["status"])
        self.assertEqual(incident_raw, incident_path.read_bytes())
        self.assertEqual(before_second, self.controller.snapshot_path.read_bytes())
        self.assertEqual(first_signal, signal_path.read_bytes()) if signal_path.exists() else None

    def test_finalizer_and_linker_keep_result_ready_signal_only(self):
        worker_event = self.fixture._write_v7_worker_event(
            self.controller,
            self.order,
            outcome="SUCCESS",
            event_id="event-v732-finalizer-signal",
        )
        profile_id = json.loads(
            self.controller.project_profile_path.read_text(encoding="utf-8")
        )["project_profile_id"]
        event_path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / worker_event["event_id"]
            / "INBOX_EVENT.json"
        )
        signal_path = self.controller.result_ready_path(
            worker_event["event_id"]
        )
        finalized = self.finalizer.finalize_result(
            self.fixture.repo,
            worker_event["result_path"],
            event_path,
            project_profile_id=profile_id,
            result_ready_output=signal_path,
            return_to_task_id="linx",
            result_ready_expires_at="2026-07-14T13:00:00Z",
        )
        self.assertEqual("RESULT_READY", finalized["result_ready"]["status"])
        raw = signal_path.read_bytes()
        checked = self.linker.validate_result_ready_signal(
            raw, expected_requester="linx"
        )
        self.assertEqual("x9-loop-result-ready-v1", checked["schema"])
        self.assertNotIn("model", checked)
        self.assertNotIn("thinking", checked)
        self.assertNotIn("result", checked)

        replay = self.finalizer.finalize_result(
            self.fixture.repo,
            worker_event["result_path"],
            event_path,
            project_profile_id=profile_id,
            result_ready_output=signal_path,
            return_to_task_id="linx",
        )
        self.assertEqual("ALREADY_RESULT_READY", replay["result_ready"]["status"])
        self.assertEqual(raw, signal_path.read_bytes())

        self.assertEqual("FEATURE_DONE", self.controller.run_once(event_path)["status"])
        self.assertEqual(raw, signal_path.read_bytes())

    def test_wrong_requester_or_hash_is_zero_delta(self):
        worker_event, signal_path = self._complete_result(
            "event-v732-identity-drift"
        )
        signal_raw = signal_path.read_bytes()
        state_raw = self.controller._result_ready_state_path(
            worker_event["event_id"]
        ).read_bytes()
        snapshot = self.controller.snapshot_path.read_bytes()
        with self.assertRaises(self.fixture.loopctl.IdentityError):
            self.controller.consume_result_ready(
                signal_path, requester_id="wrong-requester"
            )
        self.assertEqual(snapshot, self.controller.snapshot_path.read_bytes())
        self.assertEqual(signal_raw, signal_path.read_bytes())
        self.assertEqual(
            state_raw,
            self.controller._result_ready_state_path(
                worker_event["event_id"]
            ).read_bytes(),
        )

        signal = json.loads(signal_raw)
        signal["expected_result_identity"]["result_sha256"] = "0" * 64
        signal_path.write_bytes(
            self.controller.loop_contract.canonical_json_bytes(signal)
        )
        with self.assertRaises(self.fixture.loopctl.IdentityError):
            self.controller.consume_result_ready(signal_path, requester_id="linx")
        self.assertEqual(snapshot, self.controller.snapshot_path.read_bytes())
        self.assertEqual(
            state_raw,
            self.controller._result_ready_state_path(
                worker_event["event_id"]
            ).read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
