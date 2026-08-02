from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import unittest
from unittest import mock

from tests import test_loop_lite_v7_controller as v7_fixture


AVAILABLE_JOBS = {
    "jobs": [],
    "providers": {
        "codex": "AVAILABLE",
        "windows-task-scheduler": "AVAILABLE",
    },
}


class TerminalHistoryContractDoctorTests(unittest.TestCase):
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

    def _doctor(self) -> dict[str, object]:
        return self.fixture._doctor_with_inventory(
            self.controller, AVAILABLE_JOBS
        )

    def _work_order_path(self, order: dict[str, str]) -> Path:
        return self.fixture.repo / Path(
            *PurePosixPath(order["work_order_path"]).parts
        )

    def _rewrite_result_contract(
        self,
        order: dict[str, str],
        *,
        terminal: bool,
        task_status: str = "SUPERSEDED",
        work_order_status: str = "SUPERSEDED",
    ) -> tuple[dict[str, object], str]:
        contract = self.fixture.loopctl._load_v7_contract()
        path = self._work_order_path(order)
        document = json.loads(path.read_bytes())
        current_sha = document["worker_result_contract"]["validator_sha256"]
        document["worker_result_contract"]["validator_sha256"] = (
            "0" * 64 if current_sha != "0" * 64 else "1" * 64
        )
        raw = contract.canonical_json_bytes(document)
        path.write_bytes(raw)
        packet_sha256 = hashlib.sha256(raw).hexdigest()
        dispatch_packet = {
            "schema": "x9-loop-work-order-dispatch-v1",
            "task_id": order["task_id"],
            "work_order_path": order["work_order_path"],
            "work_order_sha256": packet_sha256,
        }
        action = json.loads(self.controller.action_path.read_bytes())
        action["work_order_sha256"] = packet_sha256
        action_payload = (
            contract.canonical_json_bytes(action).decode("utf-8").rstrip("\n")
        )

        def operation(connection):
            connection.execute(
                "UPDATE work_orders SET packet_sha256=? WHERE work_order_id=?",
                (packet_sha256, order["work_order_id"]),
            )
            connection.execute(
                "UPDATE dispatches SET packet_sha256=?,packet=? "
                "WHERE dispatch_id=?",
                (
                    packet_sha256,
                    json.dumps(
                        dispatch_packet,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    order["dispatch_id"],
                ),
            )
            connection.execute(
                "UPDATE outbox SET payload=? WHERE dispatch_id=?",
                (action_payload, order["dispatch_id"]),
            )
            if terminal:
                connection.execute(
                    "UPDATE tasks SET status=? WHERE task_id=?",
                    (task_status, order["task_id"]),
                )
                connection.execute(
                    "UPDATE work_orders SET status=? "
                    "WHERE work_order_id=?",
                    (work_order_status, order["work_order_id"]),
                )
                connection.execute(
                    "UPDATE dispatches SET status='COMPLETE' "
                    "WHERE dispatch_id=?",
                    (order["dispatch_id"],),
                )

        self.controller._mutate(operation)
        self.controller._publish_current_action()
        return document, packet_sha256

    def _create_order_with_historical_contract(
        self, *, terminal: bool = True
    ) -> tuple[dict[str, str], dict[str, object]]:
        order = self.fixture._create_order(self.controller)
        document, _packet_sha256 = self._rewrite_result_contract(
            order, terminal=terminal
        )
        return order, document

    def _create_order_with_context_ref(
        self, *, terminal: bool = True
    ) -> dict[str, str]:
        contract = self.fixture.loopctl._load_v7_contract()
        suffix = "terminal" if terminal else "active"
        capsule_relative = (
            f".devad/features/feature-a/runs/run-context-{suffix}/"
            "CONTEXT_CAPSULE.json"
        )
        capsule_raw = b"{}\n"
        capsule_path = self.fixture.repo / Path(
            *PurePosixPath(capsule_relative).parts
        )
        capsule_path.parent.mkdir(parents=True, exist_ok=True)
        capsule_path.write_bytes(capsule_raw)
        v7_fixture.run("git", "add", capsule_relative, cwd=self.fixture.repo)
        v7_fixture.run(
            "git", "commit", "-m", "context capsule fixture",
            cwd=self.fixture.repo,
        )
        self.fixture.base_sha = v7_fixture.run(
            "git", "rev-parse", "HEAD", cwd=self.fixture.repo
        )
        program_id = f"program-context-{suffix}"
        feature = self.fixture._feature("feature-a")
        feature["context_capsule_ref"] = {
            "bytes": len(capsule_raw),
            "capsule_id": f"capsule-{suffix}-context",
            "path": capsule_relative,
            "sha256": hashlib.sha256(capsule_raw).hexdigest(),
        }
        self.controller.init()
        self.fixture._register_v7_actors(self.controller)
        with mock.patch.object(
            self.controller,
            "_validate_project_context",
            return_value={"status": "PASS"},
        ):
            self.fixture._import_program(
                self.controller,
                {
                    "feature_packets": [feature],
                    "features": ["feature-a"],
                    "program_id": program_id,
                    "schema": "x9-loop-program-v1",
                },
            )
            order = self.controller.create_work_order(
                program_id=program_id,
                stop=self.fixture._stop(),
                linx_id="linx",
                action_class="implementation",
            )
        if terminal:
            def operation(connection):
                connection.execute(
                    "UPDATE tasks SET status='COMPLETE' WHERE task_id=?",
                    (order["task_id"],),
                )
                connection.execute(
                    "UPDATE work_orders SET status='COMPLETE' "
                    "WHERE work_order_id=?",
                    (order["work_order_id"],),
                )
                connection.execute(
                    "UPDATE dispatches SET status='COMPLETE' "
                    "WHERE dispatch_id=?",
                    (order["dispatch_id"],),
                )

            self.controller._mutate(operation)
            self.controller._publish_current_action()
        return order

    def test_doctor_reports_terminal_history_compatibility_without_failure(self):
        order, _document = self._create_order_with_historical_contract()

        result = self._doctor()

        self.assertEqual("PASS", result["status"])
        self.assertEqual([], result["checks"]["work_orders"])
        self.assertEqual(
            [
                f"{order['work_order_id']}:"
                "TERMINAL_HISTORY_WORKER_RESULT_CONTRACT"
            ],
            result["checks"]["terminal_history_compatibility"],
        )
        with self.assertRaisesRegex(
            self.fixture.loopctl.IdentityError,
            "WORK_ORDER_DRIFT:worker_result_contract",
        ):
            self.controller.verify_work_order(order["work_order_id"])

    def test_historical_receipt_proofs_keep_terminal_contract_compatibility(self):
        order, document = self._create_order_with_historical_contract()
        order = dict(order)
        order["work_order_sha256"] = hashlib.sha256(
            self.fixture.loopctl._load_v7_contract().canonical_json_bytes(document)
        ).hexdigest()
        event = self.fixture._write_v7_worker_event(
            self.controller,
            order,
            outcome="SUCCESS",
            event_id="event-terminal-history-proof",
        )
        receipt_relative = (
            f".devad/workers/worker/receipts/{event['event_id']}.json"
        )

        def record_receipt_state(connection):
            self.controller._set_receipt_state(
                connection, "core-x9", [event["result_sha256"]]
            )
            return {"status": "PASS"}

        self.controller._mutate(record_receipt_state)
        paths = self.controller._validated_receipt_proof_paths(
            self.fixture.repo,
            {receipt_relative: event["result_sha256"]},
        )
        self.assertEqual(
            {
                f".devad/workers/worker/proof/{event['event_id']}/security.json",
                f".devad/workers/worker/proof/{event['event_id']}/tests.json",
            },
            paths,
        )

    def test_nonterminal_historical_contract_still_fails_doctor(self):
        self._create_order_with_historical_contract(terminal=False)

        result = self._doctor()

        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["IdentityError"], result["checks"]["work_orders"])
        self.assertEqual(
            [], result["checks"]["terminal_history_compatibility"]
        )

    def test_terminal_context_ref_uses_bound_capsule_without_masking_active(self):
        terminal_order = self._create_order_with_context_ref(terminal=True)

        with mock.patch.object(
            self.controller,
            "_validate_project_context",
            side_effect=self.fixture.loopctl.IdentityError(
                "WORK_ORDER_CONTEXT_INVALID"
            ),
        ):
            _validated, compatibility = self.controller._verify_work_order(
                terminal_order["work_order_id"],
                allow_terminal_historical_contract=True,
            )
            with self.assertRaisesRegex(
                self.fixture.loopctl.IdentityError,
                "WORK_ORDER_CONTEXT_INVALID",
            ):
                self.controller.verify_work_order(
                    terminal_order["work_order_id"]
                )

        self.assertEqual(
            f"{terminal_order['work_order_id']}:"
            "TERMINAL_HISTORY_CONTEXT_REF_BOUND",
            compatibility,
        )

        active_order = self._create_order_with_context_ref(terminal=False)
        with mock.patch.object(
            self.controller,
            "_validate_project_context",
            side_effect=self.fixture.loopctl.IdentityError(
                "WORK_ORDER_CONTEXT_INVALID"
            ),
        ):
            active_result = self._doctor()

        self.assertEqual("FAIL", active_result["status"])
        self.assertEqual(["IdentityError"], active_result["checks"]["work_orders"])
        self.assertNotIn(
            f"{active_order['work_order_id']}:"
            "TERMINAL_HISTORY_CONTEXT_REF_BOUND",
            active_result["checks"]["terminal_history_compatibility"],
        )

    def test_mismatched_terminal_statuses_still_fail_doctor(self):
        order = self.fixture._create_order(self.controller)
        self._rewrite_result_contract(
            order,
            terminal=True,
            task_status="SUPERSEDED",
            work_order_status="COMPLETE",
        )

        result = self._doctor()

        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["IdentityError"], result["checks"]["work_orders"])
        self.assertEqual(
            [], result["checks"]["terminal_history_compatibility"]
        )

    def test_terminal_history_compatibility_does_not_mask_packet_drift(self):
        order, _document = self._create_order_with_historical_contract()
        self._work_order_path(order).write_bytes(b"{}\n")

        result = self._doctor()

        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["IdentityError"], result["checks"]["work_orders"])

    def test_terminal_history_compatibility_does_not_mask_program_drift(self):
        _order, document = self._create_order_with_historical_contract()
        program_path = self.fixture.repo / Path(
            *PurePosixPath(str(document["program_packet_path"])).parts
        )
        program_path.write_bytes(b"{}\n")

        result = self._doctor()

        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["IdentityError"], result["checks"]["work_orders"])

    def test_terminal_history_compatibility_does_not_mask_feature_drift(self):
        _order, document = self._create_order_with_historical_contract()
        feature_ref = document["feature_packet_refs"][0]
        feature_path = self.fixture.repo / Path(
            *PurePosixPath(str(feature_ref["path"])).parts
        )
        feature_path.write_bytes(b"{}\n")

        result = self._doctor()

        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["IdentityError"], result["checks"]["work_orders"])


if __name__ == "__main__":
    unittest.main()
