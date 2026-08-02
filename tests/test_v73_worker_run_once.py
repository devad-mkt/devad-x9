from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
import urllib.request

from tests import test_loop_lite_v7_controller as v7_fixture


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "devad-x9-loop" / "scripts"


def load_worker_finalizer():
    path = SCRIPTS / "worker_finalizer.py"
    spec = importlib.util.spec_from_file_location(
        "worker_finalizer_v73_run_once_red", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V73WorkerRunOnceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        v7_fixture.V7ControllerTests.setUpClass()
        cls.finalizer = load_worker_finalizer()

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

    def test_finalized_worker_result_runs_once_and_duplicate_is_zero_delta(self):
        worker_event = self.fixture._write_v7_worker_event(
            self.controller,
            self.order,
            outcome="SUCCESS",
            event_id="event-v73-worker-run-once",
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

        with (
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
            mock.patch(
                "socket.create_connection",
                side_effect=AssertionError("network hook must not run"),
            ) as network_hook,
            mock.patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network hook must not run"),
            ) as urlopen_hook,
        ):
            finalized = self.finalizer.finalize_result(
                self.fixture.repo,
                worker_event["result_path"],
                event_path,
                project_profile_id=profile_id,
            )
            with mock.patch.object(
                self.controller,
                "consume_event",
                wraps=self.controller.consume_event,
            ) as deterministic_validator:
                first = self.controller.run_once(event_path)
                after_first = self.durable_counts()
                replay = self.controller.run_once(event_path)
                after_replay = self.durable_counts()

        self.assertEqual("FINALIZED", finalized["status"])
        self.assertEqual("FEATURE_DONE", first["status"])
        self.assertEqual("ALREADY_CONSUMED", replay["status"])
        deterministic_validator.assert_called_once()
        self.assertEqual(after_first, after_replay)
        self.assertEqual(1, after_first[2])
        self.assertEqual(1, after_first[3])
        model_hook.assert_not_called()
        provider_hook.assert_not_called()
        network_hook.assert_not_called()
        urlopen_hook.assert_not_called()

        connection = self.controller._connect()
        try:
            self.assertEqual(
                ("COMPLETE", "COMPLETE", "COMPLETE"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status,d.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (self.order["task_id"],),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                ("CONSUMED", self.order["dispatch_id"]),
                tuple(
                    connection.execute(
                        "SELECT status,dispatch_id FROM inbox WHERE event_id=?",
                        (worker_event["event_id"],),
                    ).fetchone()
                ),
            )
        finally:
            connection.close()


class V73WorkerWorktreeIngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        v7_fixture.V7ControllerTests.setUpClass()
        cls.finalizer = load_worker_finalizer()

    def make_context(self):
        fixture = v7_fixture.V7ControllerTests(
            "test_fresh_state_is_snapshot_and_sqlite_v3"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        worker_root = Path(fixture.temp.name) / "worker-wt"
        v7_fixture.run(
            "git",
            "worktree",
            "add",
            "--detach",
            str(worker_root),
            fixture.base_sha,
            cwd=fixture.repo,
        )
        controller = fixture.controller()
        controller.init()
        controller.register_actor("linx", "LINX", "AI - LINX v6", "Unknown")
        controller.register_actor("worker", "WORKER", "AI - WORKER", "Unknown")
        controller.register_worktree("worker-wt", worker_root, "core")
        feature = fixture._feature("feature-a")
        feature.update(
            {
                "base_sha": fixture.base_sha,
                "worktree_id": "worker-wt",
                "worktree_path": str(worker_root),
            }
        )
        fixture._import_program(
            controller,
            {
                "feature_packets": [feature],
                "features": ["feature-a"],
                "program_id": "program-worker-wt",
                "schema": "x9-loop-program-v1",
            },
        )
        order = controller.create_work_order(
            program_id="program-worker-wt",
            stop=fixture._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        return {
            "controller": controller,
            "fixture": fixture,
            "order": order,
            "worker_root": worker_root,
        }

    def durable_counts(self, controller) -> tuple[int, int, int, int]:
        connection = controller._connect()
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

    def write_worker_result(
        self,
        context,
        *,
        event_id: str,
        root: Path | None = None,
        mutate_result=None,
        mutate_event=None,
        noncanonical_event: bool = False,
    ) -> Path:
        controller = context["controller"]
        fixture = context["fixture"]
        order = context["order"]
        worker_root = root or context["worker_root"]
        contract = fixture.loopctl._load_v7_contract()
        proof = []
        for kind in ("security", "tests"):
            proof_path = f".devad/workers/worker/proof/{event_id}/{kind}.json"
            proof_document = {
                "dispatch_id": order["dispatch_id"],
                "event_id": event_id,
                "kind": kind,
                "schema": "x9-loop-proof-v2",
                "status": "PASS",
                "task_id": order["task_id"],
                "work_order_id": order["work_order_id"],
                "worker_id": "worker",
            }
            proof_raw = contract.canonical_json_bytes(proof_document)
            absolute = worker_root / Path(*proof_path.split("/"))
            absolute.parent.mkdir(parents=True, exist_ok=True)
            absolute.write_bytes(proof_raw)
            proof.append(
                {
                    "kind": kind,
                    "path": proof_path,
                    "sha256": hashlib.sha256(proof_raw).hexdigest(),
                }
            )
        result = {
            "attestation_path": None,
            "blocker": None,
            "budget_remaining": True,
            "c1": None,
            "c2": None,
            "change_map": {
                "changed_surface": [],
                "proof_refs": [item["path"] for item in proof],
                "reason": "bounded worker result",
                "remaining_risk": "none known",
                "rollback": "no source changes",
            },
            "changed_files": [],
            "dispatch_id": order["dispatch_id"],
            "event_id": event_id,
            "failed_verified_approaches": 0,
            "outcome": "SUCCESS",
            "packet_sha256": order["work_order_sha256"],
            "proof": proof,
            "role": "WORKER",
            "schema": "x9-loop-result-v2",
            "task_id": order["task_id"],
            "work_order_id": order["work_order_id"],
            "work_order_sha256": order["work_order_sha256"],
            "worker_id": "worker",
        }
        if mutate_result is not None:
            result = mutate_result(result)
        receipt_path = f".devad/workers/worker/receipts/{event_id}.json"
        receipt_raw = contract.canonical_json_bytes(result)
        absolute_receipt = worker_root / Path(*receipt_path.split("/"))
        absolute_receipt.parent.mkdir(parents=True, exist_ok=True)
        absolute_receipt.write_bytes(receipt_raw)
        profile_id = json.loads(
            controller.project_profile_path.read_bytes()
        )["project_profile_id"]
        event_path = (
            worker_root
            / ".devad"
            / "workers"
            / "worker"
            / "outbox"
            / event_id
            / "INBOX_EVENT.json"
        )
        self.finalizer.finalize_result(
            worker_root,
            receipt_path,
            event_path,
            project_profile_id=profile_id,
        )
        if mutate_event is not None or noncanonical_event:
            event = json.loads(event_path.read_bytes())
            if mutate_event is not None:
                event = mutate_event(event)
            if noncanonical_event:
                event_path.write_text(
                    json.dumps(event, indent=2), encoding="utf-8"
                )
            else:
                event_path.write_bytes(contract.canonical_json_bytes(event))
        return event_path

    def assert_rejected_without_state_change(
        self, context, event_path: Path, pattern: str
    ) -> None:
        controller = context["controller"]
        before = self.durable_counts(controller)
        with self.assertRaisesRegex(Exception, pattern):
            controller.ingest_worker_result(event_path)
        self.assertEqual(before, self.durable_counts(controller))

    def test_registered_worker_worktree_event_ingests_and_replays_zero_delta(self):
        context = self.make_context()
        controller = context["controller"]
        event_path = self.write_worker_result(
            context, event_id="event-worker-worktree-ingest"
        )
        with self.assertRaisesRegex(
            context["fixture"].loopctl.IdentityError,
            "INBOX_EVENT_PATH_INVALID",
        ):
            controller.run_once(event_path)

        first = controller.ingest_worker_result(event_path)
        after_first = self.durable_counts(controller)
        replay = controller.ingest_worker_result(event_path)
        after_replay = self.durable_counts(controller)

        self.assertEqual("FEATURE_DONE", first["status"])
        self.assertEqual("ALREADY_CONSUMED", replay["status"])
        self.assertEqual(after_first, after_replay)
        connection = controller._connect()
        try:
            self.assertEqual(
                ("COMPLETE", "COMPLETE", "COMPLETE"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status,d.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id"
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

    def test_registered_worker_ingest_rejects_identity_hash_and_path_drift(self):
        cases = [
            (
                "wrong-worker",
                "WORKER_RESULT_EVENT_PATH_INVALID",
                {
                    "mutate_event": lambda event: {
                        **event,
                        "source_actor_id": "worker-b",
                    }
                },
            ),
            (
                "wrong-task",
                "STALE_COMPLETION",
                {
                    "mutate_result": lambda result: {
                        **result,
                        "task_id": "task-wrong",
                    }
                },
            ),
            (
                "wrong-dispatch",
                "STALE_COMPLETION",
                {
                    "mutate_result": lambda result: {
                        **result,
                        "dispatch_id": "dsp-wrong",
                    }
                },
            ),
            (
                "wrong-receipt-hash",
                "WORKER_RESULT_RECEIPT_HASH_MISMATCH",
                {
                    "mutate_event": lambda event: {
                        **event,
                        "payload_ref": {
                            **event["payload_ref"],
                            "sha256": "0" * 64,
                        },
                    }
                },
            ),
            (
                "wrong-event-hash",
                "INBOX_EVENT_BYTES_NONCANONICAL",
                {"noncanonical_event": True},
            ),
            (
                "wrong-payload-path",
                "WORKER_RESULT_RECEIPT_PATH_INVALID",
                {
                    "mutate_event": lambda event: {
                        **event,
                        "payload_ref": {
                            **event["payload_ref"],
                            "path": ".devad/workers/worker/receipts/other.json",
                        },
                    }
                },
            ),
        ]
        for suffix, pattern, options in cases:
            with self.subTest(suffix=suffix):
                context = self.make_context()
                event_path = self.write_worker_result(
                    context,
                    event_id=f"event-{suffix}",
                    **options,
                )
                self.assert_rejected_without_state_change(
                    context, event_path, pattern
                )

    def test_registered_worker_ingest_rejects_unregistered_escape_and_conflict(self):
        unregistered = self.make_context()
        unregistered_root = Path(unregistered["fixture"].temp.name) / "unregistered"
        event_path = self.write_worker_result(
            unregistered,
            event_id="event-unregistered-worktree",
            root=unregistered_root,
        )
        self.assert_rejected_without_state_change(
            unregistered, event_path, "WORKER_RESULT_WORKTREE_UNREGISTERED"
        )

        escaped = self.make_context()
        escaped_event = self.write_worker_result(
            escaped, event_id="event-path-escape"
        )
        escape_path = (
            escaped_event.parent / ".." / escaped_event.parent.name / "INBOX_EVENT.json"
        )
        self.assert_rejected_without_state_change(
            escaped, escape_path, "WORKER_RESULT_EVENT_PATH_INVALID"
        )

        conflicted = self.make_context()
        conflict_event = self.write_worker_result(
            conflicted, event_id="event-active-conflict"
        )
        (
            conflicted["worker_root"] / "src" / "unclaimed.py"
        ).write_text("X = 1\n", encoding="utf-8")
        self.assert_rejected_without_state_change(
            conflicted, conflict_event, "RESULT_GIT_INVALID"
        )


if __name__ == "__main__":
    unittest.main()
