from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from tests import test_v73_run_once as run_once_fixture
from tests import test_loop_lite_v7_controller as controller_fixture
from tests import test_v73_worker_run_once as worker_ingest_fixture
from tests.test_v73_worker_finalizer import worker_result


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "devad-x9-loop" / "scripts"
PROFILE_ID = "profile-0123456789abcdef"
VALIDATOR_PATH = "skills/devad-x9-loop/scripts/v7_contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class WorkOrderResultContractBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        run_once_fixture.V73RunOnceTests.setUpClass()

    def setUp(self) -> None:
        self.fixture = run_once_fixture.V73RunOnceTests(methodName="runTest")
        self.fixture.setUp()

    def tearDown(self) -> None:
        self.fixture.doCleanups()

    def test_new_work_order_hash_binds_exact_result_contract(self):
        created = self.fixture.create_order()
        work_order_path = self.fixture.repo / Path(
            *created["work_order_path"].split("/")
        )
        raw = work_order_path.read_bytes()
        order = json.loads(raw)
        validator_raw = (ROOT / VALIDATOR_PATH).read_bytes()
        expected = {
            "proof_schema": "x9-loop-proof-v2",
            "result_schema": "x9-loop-result-v2",
            "validator_path": VALIDATOR_PATH,
            "validator_sha256": hashlib.sha256(validator_raw).hexdigest(),
        }

        self.assertEqual(run_once_fixture.canonical(order), raw)
        self.assertLessEqual(len(raw), 16 * 1024)
        self.assertEqual(expected, order["worker_result_contract"])

    def test_verify_recomputes_current_result_validator_binding(self):
        created = self.fixture.create_order()
        contract = self.fixture.loopctl._load_v7_contract()
        current = contract.worker_result_contract_binding()
        drifted = {
            **current,
            "validator_sha256": (
                "0" * 64
                if current["validator_sha256"] != "0" * 64
                else "1" * 64
            ),
        }

        with mock.patch.object(
            contract, "worker_result_contract_binding", return_value=drifted
        ):
            with self.assertRaisesRegex(
                self.fixture.loopctl.IdentityError,
                "WORK_ORDER_DRIFT:worker_result_contract",
            ):
                self.fixture.controller.verify_work_order(
                    created["work_order_id"]
                )


class PreDispatchResultContractRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        run_once_fixture.V73RunOnceTests.setUpClass()

    def setUp(self) -> None:
        self.fixture = run_once_fixture.V73RunOnceTests(methodName="runTest")
        self.fixture.setUp()
        self.controller = self.fixture.controller

    def tearDown(self) -> None:
        self.fixture.doCleanups()

    def _state(self) -> tuple[bytes, bytes, bytes]:
        return (
            self.controller.db_path.read_bytes(),
            self.controller.snapshot_path.read_bytes(),
            self.controller.action_path.read_bytes(),
        )

    def _drifted_binding(self) -> dict[str, str]:
        current = self.fixture.loopctl._load_v7_contract().worker_result_contract_binding()
        return {
            **current,
            "validator_sha256": (
                "0" * 64
                if current["validator_sha256"] != "0" * 64
                else "1" * 64
            ),
        }

    def _run_with_drift(self, order, operation):
        contract = self.fixture.loopctl._load_v7_contract()
        with mock.patch.object(
            contract,
            "worker_result_contract_binding",
            return_value=self._drifted_binding(),
        ):
            self.controller._publish_current_action()
            self.assertEqual(
                "NOOP", json.loads(self.controller.action_path.read_bytes())["action"]
            )
            return operation(order)

    def _assert_rejected_after_mutation(self, order, mutation) -> None:
        contract = self.fixture.loopctl._load_v7_contract()
        with mock.patch.object(
            contract,
            "worker_result_contract_binding",
            return_value=self._drifted_binding(),
        ):
            self.controller._publish_current_action()
            self.controller._mutate(mutation)
            before = self._state()
            with self.assertRaisesRegex(
                self.fixture.loopctl.TaskNotReadyError,
                "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE",
            ):
                self.controller.recover_pre_dispatch_worker_result_contract_drift(
                    order["work_order_id"], order["work_order_sha256"]
                )
            self.assertEqual(before, self._state())

    def test_recovery_terminalizes_exact_prepared_order_and_releases_active_ownership(self):
        order = self.fixture.create_order()
        packet_path = self.fixture.repo / Path(*order["work_order_path"].split("/"))
        packet_raw = packet_path.read_bytes()
        connection = self.controller._connect()
        try:
            outbox_payload = connection.execute(
                "SELECT payload FROM outbox WHERE dispatch_id=?",
                (order["dispatch_id"],),
            ).fetchone()[0]
        finally:
            connection.close()
        recovered = self._run_with_drift(
            order,
            lambda created: self.controller.recover_pre_dispatch_worker_result_contract_drift(
                created["work_order_id"], created["work_order_sha256"]
            ),
        )

        self.assertEqual("RECOVERED", recovered["status"])
        self.assertEqual(packet_raw, packet_path.read_bytes())
        receipt_path = self.fixture.repo / Path(
            *recovered["recovery_receipt_path"].split("/")
        )
        receipt_raw = receipt_path.read_bytes()
        self.assertEqual(
            recovered["recovery_receipt_sha256"],
            hashlib.sha256(receipt_raw).hexdigest(),
        )
        self.assertEqual(
            receipt_raw,
            self.fixture.loopctl._load_v7_contract().canonical_json_bytes(
                json.loads(receipt_raw)
            ),
        )
        self.assertEqual(
            hashlib.sha256(outbox_payload.encode("utf-8")).hexdigest(),
            json.loads(receipt_raw)["outbox_action_sha256"],
        )
        connection = self.controller._connect()
        try:
            self.assertEqual(
                ("SUPERSEDED", "SUPERSEDED", "SUPERSEDED"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status,d.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id "
                        "WHERE wo.work_order_id=?",
                        (order["work_order_id"],),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                0,
                connection.execute(
                    "SELECT COUNT(*) FROM claims c JOIN tasks t ON t.task_id=c.task_id "
                    "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED')"
                ).fetchone()[0],
            )
            self.assertEqual(
                0,
                connection.execute(
                    "SELECT COUNT(*) FROM resources r JOIN tasks t ON t.task_id=r.task_id "
                    "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED')"
                ).fetchone()[0],
            )
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0])
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM events").fetchone()[0])
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM outbox").fetchone()[0])
        finally:
            connection.close()
        self.assertEqual("NOOP", json.loads(self.controller.action_path.read_bytes())["action"])
        self.assertEqual("PASS", self.controller.doctor()["status"])
        self.assertEqual(
            "ALREADY_RECOVERED",
            self._run_with_drift(
                order,
                lambda created: self.controller.recover_pre_dispatch_worker_result_contract_drift(
                    created["work_order_id"], created["work_order_sha256"]
                ),
            )["status"],
        )

    def test_recovery_rejects_hash_or_action_without_delta(self):
        order = self.fixture.create_order()
        with mock.patch.object(
            self.fixture.loopctl._load_v7_contract(),
            "worker_result_contract_binding",
            return_value=self._drifted_binding(),
        ):
            self.controller._publish_current_action()
            before = self._state()
            with self.assertRaisesRegex(
                self.fixture.loopctl.TaskNotReadyError,
                "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE",
            ):
                self.controller.recover_pre_dispatch_worker_result_contract_drift(
                    order["work_order_id"], "0" * 64
                )
            self.assertEqual(before, self._state())
            self.controller._write_action(
                self.controller._v7_action(
                    order["dispatch_id"], order["task_id"], "worker-a",
                    order["work_order_id"], order["work_order_path"],
                    order["work_order_sha256"],
                )
            )
            before = self._state()
            with self.assertRaisesRegex(
                self.fixture.loopctl.TaskNotReadyError,
                "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE",
            ):
                self.controller.recover_pre_dispatch_worker_result_contract_drift(
                    order["work_order_id"], order["work_order_sha256"]
                )
            self.assertEqual(before, self._state())

    def test_recovery_rejects_non_registered_lifecycle_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "UPDATE tasks SET status='RETRY_READY' WHERE task_id=?",
                (order["task_id"],),
            ),
        )

    def test_recovery_rejects_order_not_created_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "UPDATE work_orders SET status='ACTIVE' WHERE work_order_id=?",
                (order["work_order_id"],),
            ),
        )

    def test_recovery_rejects_non_contract_drift_zero_delta(self):
        order = self.fixture.create_order()
        before = self._state()
        with mock.patch.object(
            self.controller,
            "verify_work_order",
            side_effect=self.fixture.loopctl.IdentityError("WORK_ORDER_DRIFT:resources"),
        ):
            with self.assertRaisesRegex(
                self.fixture.loopctl.TaskNotReadyError,
                "PRE_DISPATCH_RECOVERY_NOT_ADMISSIBLE",
            ):
                self.controller.recover_pre_dispatch_worker_result_contract_drift(
                    order["work_order_id"], order["work_order_sha256"]
                )
        self.assertEqual(before, self._state())

    def test_recovery_rejects_non_prepared_dispatch_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "UPDATE dispatches SET status='DISPATCHED' WHERE dispatch_id=?",
                (order["dispatch_id"],),
            ),
        )

    def test_recovery_rejects_multiple_dispatches_zero_delta(self):
        order = self.fixture.create_order()

        def add_dispatch(connection):
            original = connection.execute(
                "SELECT * FROM dispatches WHERE dispatch_id=?",
                (order["dispatch_id"],),
            ).fetchone()
            connection.execute(
                "INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    "dsp-extra-pre-dispatch", order["task_id"], original["sender_id"],
                    original["target_id"], original["packet_sha256"], original["packet"],
                    original["dispatch_id"], "SUPERSEDED", original["created_at"],
                ),
            )

        self._assert_rejected_after_mutation(order, add_dispatch)

    def test_recovery_rejects_dispatch_packet_mismatch_zero_delta(self):
        order = self.fixture.create_order()

        def corrupt_dispatch_packet(connection):
            packet = json.loads(
                connection.execute(
                    "SELECT packet FROM dispatches WHERE dispatch_id=?",
                    (order["dispatch_id"],),
                ).fetchone()[0]
            )
            packet["task_id"] = "task-not-the-order-task"
            connection.execute(
                "UPDATE dispatches SET packet=? WHERE dispatch_id=?",
                (json.dumps(packet, sort_keys=True, separators=(",", ":")), order["dispatch_id"]),
            )

        self._assert_rejected_after_mutation(order, corrupt_dispatch_packet)

    def test_recovery_rejects_unbound_or_missing_outbox_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "UPDATE outbox SET payload='{}' WHERE dispatch_id=?",
                (order["dispatch_id"],),
            ),
        )

    def test_recovery_rejects_missing_outbox_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "DE" + "LETE FROM outbox WHERE dispatch_id=?",
                (order["dispatch_id"],),
            ),
        )

    def test_recovery_rolls_back_receipt_when_snapshot_mutation_fails(self):
        order = self.fixture.create_order()
        receipt_path = (
            self.controller.root / "runtime" / "pre-dispatch-recoveries"
            / f"{order['work_order_id']}.json"
        )
        contract = self.fixture.loopctl._load_v7_contract()
        with mock.patch.object(
            contract,
            "worker_result_contract_binding",
            return_value=self._drifted_binding(),
        ):
            self.controller._publish_current_action()
            before = self._state()
            with mock.patch.object(
                self.controller,
                "_snapshot_bundle",
                side_effect=RuntimeError("forced snapshot failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "forced snapshot failure"):
                    self.controller.recover_pre_dispatch_worker_result_contract_drift(
                        order["work_order_id"], order["work_order_sha256"]
                    )
        self.assertFalse(receipt_path.exists())
        self.assertEqual(before, self._state())

    def test_recovery_retains_receipt_after_post_commit_snapshot_failure(self):
        order = self.fixture.create_order()
        receipt_path = (
            self.controller.root / "runtime" / "pre-dispatch-recoveries"
            / f"{order['work_order_id']}.json"
        )
        contract = self.fixture.loopctl._load_v7_contract()
        with mock.patch.object(
            contract,
            "worker_result_contract_binding",
            return_value=self._drifted_binding(),
        ):
            self.controller._publish_current_action()
            with mock.patch.object(
                self.controller,
                "_write_snapshot_bundle",
                side_effect=self.fixture.loopctl.SnapshotExportError(
                    "forced post-commit snapshot failure"
                ),
            ):
                with self.assertRaisesRegex(
                    self.fixture.loopctl.SnapshotExportError,
                    "forced post-commit snapshot failure",
                ):
                    self.controller.recover_pre_dispatch_worker_result_contract_drift(
                        order["work_order_id"], order["work_order_sha256"]
                    )
            self.assertTrue(receipt_path.is_file())
            connection = self.controller._connect()
            try:
                self.assertEqual(
                    ("SUPERSEDED", "SUPERSEDED", "SUPERSEDED"),
                    tuple(
                        connection.execute(
                            "SELECT t.status,wo.status,d.status FROM tasks t "
                            "JOIN work_orders wo ON wo.task_id=t.task_id "
                            "JOIN dispatches d ON d.task_id=t.task_id "
                            "WHERE wo.work_order_id=?",
                            (order["work_order_id"],),
                        ).fetchone()
                    ),
                )
                self.assertEqual(
                    0,
                    connection.execute(
                        "SELECT COUNT(*) FROM outbox WHERE dispatch_id=?",
                        (order["dispatch_id"],),
                    ).fetchone()[0],
                )
            finally:
                connection.close()
            self.assertEqual("PASS", self.controller.rebuild()["status"])
            self.assertEqual(
                "ALREADY_RECOVERED",
                self.controller.recover_pre_dispatch_worker_result_contract_drift(
                    order["work_order_id"], order["work_order_sha256"]
                )["status"],
            )

    def test_recovery_rejects_delivery_evidence_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "INSERT INTO deliveries(dispatch_id,phase,method,result,created_at) VALUES(?,?,?,?,?)",
                (order["dispatch_id"], "DISPATCH", "test", "ack", "2026-07-16T12:00:00Z"),
            ),
        )

    def test_recovery_rejects_inbox_evidence_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "INSERT INTO inbox(event_id,task_id,dispatch_id,event_sha256,payload,status,created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    "evt-pre-dispatch-inbox", order["task_id"], order["dispatch_id"],
                    "0" * 64, "{}", "PENDING", "2026-07-16T12:00:00Z",
                ),
            ),
        )

    def test_recovery_rejects_event_evidence_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "INSERT INTO events(event_id,task_id,dispatch_id,event_sha256,created_at) VALUES(?,?,?,?,?)",
                ("evt-pre-dispatch", order["task_id"], order["dispatch_id"], "0" * 64, "2026-07-16T12:00:00Z"),
            ),
        )

    def test_recovery_rejects_call_receipt_evidence_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "INSERT INTO call_receipts(call_id,work_order_id,sequence,receipt_sha256,receipt,created_at) "
                "VALUES(?,?,?,?,?,?)",
                (
                    "call-receipt-pre-dispatch", order["work_order_id"], 1,
                    "0" * 64, "{}", "2026-07-16T12:00:00Z",
                ),
            ),
        )

    def test_recovery_rejects_call_evidence_zero_delta(self):
        order = self.fixture.create_order()
        self._assert_rejected_after_mutation(
            order,
            lambda connection: connection.execute(
                "INSERT INTO call_reservations(call_id,work_order_id,sequence,action_class,attempt,prompt_prefix_sha256,tool_schema_sha256,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                ("call-pre-dispatch", order["work_order_id"], 1, "implementation", 1, "a" * 64, "b" * 64, "RECORDED", "2026-07-16T12:00:00Z"),
            ),
        )


class WorkerFinalizerResultContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.finalizer = load_module(
            "worker_finalizer_v73_result_contract_test",
            SCRIPTS / "worker_finalizer.py",
        )
        cls.contract = load_module(
            "v7_contract_v73_result_contract_test",
            SCRIPTS / "v7_contract.py",
        )

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="x9-v73-result-contract-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.relative = ".devad/workers/worker-one/receipts/event-one.json"
        self.result_path = self.repo / Path(*self.relative.split("/"))
        self.result_path.parent.mkdir(parents=True)
        self.event_path = self.repo / "runtime" / "inbox" / "event-one.json"

    def expected_identity(self, result: dict[str, object]) -> dict[str, str]:
        return {
            field: str(result[field])
            for field in (
                "dispatch_id",
                "event_id",
                "packet_sha256",
                "task_id",
                "work_order_id",
                "work_order_sha256",
                "worker_id",
            )
        }

    def test_finalizer_calls_shared_worker_result_validator_before_publish(self):
        result = worker_result()
        self.result_path.write_bytes(run_once_fixture.canonical(result))
        proxy = mock.Mock()
        proxy.ContractError = self.contract.ContractError
        proxy.validate_worker_result = mock.Mock(
            wraps=self.contract.validate_worker_result
        )
        proxy.validate_inbox_event = self.contract.validate_inbox_event

        with mock.patch.object(
            self.finalizer, "_load_v7_contract", return_value=proxy
        ):
            finalized = self.finalizer.finalize_result(
                self.repo,
                self.relative,
                self.event_path,
                project_profile_id=PROFILE_ID,
            )

        self.assertEqual("FINALIZED", finalized["status"])
        proxy.validate_worker_result.assert_called_once_with(
            result, self.expected_identity(result)
        )
        self.assertTrue(self.event_path.is_file())

    def test_obsolete_v1_result_cannot_publish_worker_result_callback(self):
        result = worker_result()
        result["schema"] = "x9-loop-lite-result-v1"
        self.result_path.write_bytes(run_once_fixture.canonical(result))

        with self.assertRaisesRegex(
            self.finalizer.FinalizerError,
            r"RESULT_(?:IDENTITY|CONTRACT|SCHEMA)_INVALID",
        ):
            self.finalizer.finalize_result(
                self.repo,
                self.relative,
                self.event_path,
                project_profile_id=PROFILE_ID,
            )

        self.assertFalse(self.event_path.exists())


class ReceiptSetMismatchWorkerResultRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        worker_ingest_fixture.V73WorkerWorktreeIngestTests.setUpClass()

    def setUp(self) -> None:
        self.worker = worker_ingest_fixture.V73WorkerWorktreeIngestTests(
            methodName="runTest"
        )
        self.worker.setUp()
        self.addCleanup(self.worker.doCleanups)

    def _state(self, controller) -> tuple[bytes, bytes, bytes]:
        return (
            controller.db_path.read_bytes(),
            controller.snapshot_path.read_bytes(),
            controller.action_path.read_bytes(),
        )

    def _shared_executor_base(self):
        fixture = controller_fixture.V7ControllerTests(
            "test_fresh_state_is_snapshot_and_sqlite_v3"
        )
        fixture.setUp()
        self.worker.addCleanup(fixture.doCleanups)
        worker_root = Path(fixture.temp.name) / "worker-wt"
        controller_fixture.run(
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
        return {
            "controller": controller,
            "fixture": fixture,
            "worker_root": worker_root,
        }

    def _recovery_context(self):
        context = self._shared_executor_base()
        controller = context["controller"]
        fixture = context["fixture"]
        history_entries = self._create_historical_compatibility(context)
        feature = fixture._feature("feature-worker-target")
        feature.update(
            {
                "base_sha": fixture.base_sha,
                "claims": [
                    {"path": "src/target.py", "kind": "file"}
                ],
                "resources": ["fixture:target"],
                "worker_id": "worker",
                "worktree_id": "worker-wt",
                "worktree_path": str(context["worker_root"]),
            }
        )
        fixture._import_program(
            controller,
            {
                "feature_packets": [feature],
                "features": [feature["feature_id"]],
                "program_id": "program-worker-target",
                "schema": "x9-loop-program-v1",
            },
        )
        order = controller.create_work_order(
            program_id="program-worker-target",
            stop=fixture._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        context["order"] = order
        context["history_entries"] = history_entries
        context["fixture"] = fixture
        residual_event = self.worker.write_worker_result(
            context, event_id="event-receipt-residual"
        )
        residual_event.unlink()
        fresh_event = self.worker.write_worker_result(
            context, event_id="event-receipt-fresh"
        )
        order = context["order"]
        worker_root = context["worker_root"]
        contract = context["fixture"].loopctl._load_v7_contract()
        result_path = (
            worker_root
            / ".devad"
            / "workers"
            / "worker"
            / "receipts"
            / "event-receipt-fresh.json"
        )
        result_sha256 = hashlib.sha256(result_path.read_bytes()).hexdigest()
        identity = {
            "dispatch_id": order["dispatch_id"],
            "event_id": "event-receipt-fresh",
            "packet_sha256": order["work_order_sha256"],
            "result_path": (
                ".devad/workers/worker/receipts/event-receipt-fresh.json"
            ),
            "result_sha256": result_sha256,
            "task_id": order["task_id"],
            "work_order_id": order["work_order_id"],
            "work_order_sha256": order["work_order_sha256"],
            "worker_id": "worker",
        }
        ready = contract.build_result_ready(
            callback_id=controller._result_ready_callback_id(identity, "linx"),
            expected_result_identity=identity,
            expires_at=controller._result_ready_expiry(),
            project_profile_id=controller._ensure_project_profile(),
            return_to_task_id="linx",
        )
        fresh_event.with_name("RESULT_READY.json").write_bytes(
            contract.canonical_json_bytes(ready)
        )
        return context, fresh_event

    def _create_historical_compatibility(self, context) -> list[str]:
        controller = context["controller"]
        fixture = context["fixture"]
        contract = fixture.loopctl._load_v7_contract()
        for index in range(2):
            worker_id = "worker"
            worktree_id = "worker-wt"
            history_root = context["worker_root"]
            feature = fixture._feature(f"history-feature-{index}")
            feature.update(
                {
                    "claims": [
                        {"path": f"src/history-{index}.py", "kind": "file"}
                    ],
                    "resources": [f"integration:history-{index}"],
                    "worker_id": worker_id,
                    "worktree_id": worktree_id,
                    "worktree_path": str(history_root),
                }
            )
            fixture._import_program(
                controller,
                {
                    "feature_packets": [feature],
                    "features": [feature["feature_id"]],
                    "program_id": f"program-history-{index}",
                    "schema": "x9-loop-program-v1",
                },
            )
            order = controller.create_work_order(
                program_id=f"program-history-{index}",
                stop=fixture._stop(),
                linx_id="linx",
                action_class="implementation",
            )
            order_path = fixture.repo / Path(
                *order["work_order_path"].split("/")
            )
            document = json.loads(order_path.read_bytes())
            current_sha = document["worker_result_contract"]["validator_sha256"]
            document["worker_result_contract"]["validator_sha256"] = (
                "0" * 64 if current_sha != "0" * 64 else "1" * 64
            )
            raw = contract.canonical_json_bytes(document)
            order_path.write_bytes(raw)
            packet_sha256 = hashlib.sha256(raw).hexdigest()
            dispatch_packet = {
                "schema": "x9-loop-work-order-dispatch-v1",
                "task_id": order["task_id"],
                "work_order_path": order["work_order_path"],
                "work_order_sha256": packet_sha256,
            }
            receipt_relative = (
                f".devad/workers/{worker_id}/receipts/"
                f"history-{index}.json"
            )
            receipt_digest = None
            history_event_path = None
            if index == 1:
                history_order = {
                    **order,
                    "work_order_sha256": packet_sha256,
                }
                history_event_path = self.worker.write_worker_result(
                    {**context, "order": history_order},
                    event_id="history-event-1",
                )
                receipt_path = history_root / Path(
                    *".devad/workers/worker/receipts/history-event-1.json".split(
                        "/"
                    )
                )
                receipt_digest = hashlib.sha256(
                    receipt_path.read_bytes()
                ).hexdigest()

            def terminalize(
                connection,
                order=order,
                packet_sha256=packet_sha256,
                worktree_id=worktree_id,
                receipt_digest=receipt_digest,
                history_status=(
                    "SUPERSEDED" if index == 0 else "COMPLETE"
                ),
                history_event_path=history_event_path,
            ):
                outbox = connection.execute(
                    "SELECT payload FROM outbox WHERE dispatch_id=?",
                    (order["dispatch_id"],),
                ).fetchone()
                action = json.loads(outbox["payload"])
                action["work_order_sha256"] = packet_sha256
                connection.execute(
                    "UPDATE tasks SET status=? WHERE task_id=?",
                    (history_status, order["task_id"]),
                )
                connection.execute(
                    "UPDATE work_orders SET status=?,packet_sha256=? "
                    "WHERE work_order_id=?",
                    (history_status, packet_sha256, order["work_order_id"]),
                )
                connection.execute(
                    "UPDATE dispatches SET status=?,packet_sha256=?,packet=? "
                    "WHERE dispatch_id=?",
                    (
                        history_status,
                        packet_sha256,
                        contract.canonical_json_bytes(dispatch_packet)
                        .decode("utf-8")
                        .rstrip("\n"),
                        order["dispatch_id"],
                    ),
                )
                connection.execute(
                    "UPDATE outbox SET payload=? WHERE dispatch_id=?",
                    (
                        contract.canonical_json_bytes(action)
                        .decode("utf-8")
                        .rstrip("\n"),
                        order["dispatch_id"],
                    ),
                )
                controller._set_receipt_state(
                    connection,
                    worktree_id,
                    [receipt_digest] if receipt_digest else [],
                )
                if history_event_path is not None:
                    event_raw = history_event_path.read_bytes()
                    event = json.loads(event_raw)
                    connection.execute(
                        "INSERT INTO events(event_id,task_id,dispatch_id,"
                        "event_sha256,created_at) VALUES(?,?,?,?,?)",
                        (
                            event["event_id"],
                            order["task_id"],
                            order["dispatch_id"],
                            receipt_digest,
                            controller.now_fn(),
                        ),
                    )
                    connection.execute(
                        "INSERT INTO inbox(event_id,task_id,dispatch_id,"
                        "event_sha256,payload,status,created_at) "
                        "VALUES(?,?,?,?,?,?,?)",
                        (
                            event["event_id"],
                            order["task_id"],
                            order["dispatch_id"],
                            hashlib.sha256(event_raw).hexdigest(),
                            event_raw.decode("utf-8"),
                            "CONSUMED",
                            controller.now_fn(),
                        ),
                    )

            controller._mutate(terminalize)
            controller._publish_current_action()

        doctor = controller.doctor()
        entries = doctor["checks"]["terminal_history_compatibility"]
        self.assertEqual(2, len(entries))
        connection = controller._connect()
        try:
            statuses = [
                tuple(row)
                for row in connection.execute(
                    "SELECT t.status,wo.status,d.status "
                    "FROM tasks t JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "WHERE t.worker_id='worker' ORDER BY wo.created_at"
                )
            ]
        finally:
            connection.close()
        self.assertEqual(
            [("SUPERSEDED", "SUPERSEDED", "SUPERSEDED"),
             ("COMPLETE", "COMPLETE", "COMPLETE")],
            statuses,
        )
        return entries

    def test_recovers_one_current_candidate_and_preserves_residual_receipt(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        self.assertEqual("FAIL", controller.doctor()["status"])

        recovered = controller.recover_receipt_set_mismatch_worker_result(
            order["work_order_id"], order["work_order_sha256"], fresh_event
        )

        self.assertEqual("FEATURE_DONE", recovered["status"])
        self.assertEqual(1, recovered["recovery"]["unfinalized_receipts"])
        self.assertEqual("PASS", controller.doctor()["status"])
        connection = controller._connect()
        try:
            self.assertEqual(
                ("COMPLETE", "COMPLETE", "COMPLETE"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status,d.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (order["task_id"],),
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

    def test_recovery_tolerates_two_independently_validated_history_entries(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]

        recovered = controller.recover_receipt_set_mismatch_worker_result(
            order["work_order_id"], order["work_order_sha256"], fresh_event
        )

        self.assertEqual("FEATURE_DONE", recovered["status"])
        self.assertEqual(2, len(entries))
        self.assertEqual("PASS", controller.doctor()["status"])

    def test_recovery_rejects_orphan_historical_event_without_state_delta(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]
        doctor = controller.doctor()
        history_id = entries[1].split(":", 1)[0]
        connection = controller._connect()
        try:
            history = connection.execute(
                "SELECT wo.task_id,d.dispatch_id FROM work_orders wo "
                "JOIN dispatches d ON d.task_id=wo.task_id "
                "WHERE wo.work_order_id=?",
                (history_id,),
            ).fetchone()
        finally:
            connection.close()

        def insert_orphan(connection):
            connection.execute(
                "INSERT INTO events(event_id,task_id,dispatch_id,"
                "event_sha256,created_at) VALUES(?,?,?,?,?)",
                (
                    "history-event-orphan",
                    history["task_id"],
                    history["dispatch_id"],
                    "0" * 64,
                    controller.now_fn(),
                ),
            )

        controller._mutate(insert_orphan)
        doctor["checks"]["terminal_history_compatibility"] = entries
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_schema_valid_inbox_row_identity_mismatch_without_state_delta(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]
        doctor = controller.doctor()
        fresh_raw = fresh_event.read_bytes()
        fresh_sha256 = hashlib.sha256(fresh_raw).hexdigest()

        def replace_historical_inbox(connection):
            connection.execute(
                "UPDATE inbox SET event_sha256=?,payload=? "
                "WHERE event_id='history-event-1'",
                (fresh_sha256, fresh_raw.decode("utf-8")),
            )

        controller._mutate(replace_historical_inbox)
        doctor["checks"]["terminal_history_compatibility"] = entries
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_target_related_history_compatibility(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        doctor = controller.doctor()
        doctor["checks"]["terminal_history_compatibility"] = [
            f"{order['work_order_id']}:TERMINAL_HISTORY_WORKER_RESULT_CONTRACT"
        ]
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_active_history_compatibility(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]
        history_id = entries[0].split(":", 1)[0]
        doctor = controller.doctor()

        def activate_history(connection):
            task_id = connection.execute(
                "SELECT task_id FROM work_orders WHERE work_order_id=?",
                (history_id,),
            ).fetchone()[0]
            dispatch_id = connection.execute(
                "SELECT dispatch_id FROM dispatches WHERE task_id=?",
                (task_id,),
            ).fetchone()[0]
            connection.execute(
                "UPDATE tasks SET status='REGISTERED' WHERE task_id=?",
                (task_id,),
            )
            connection.execute(
                "UPDATE work_orders SET status='CREATED' WHERE work_order_id=?",
                (history_id,),
            )
            connection.execute(
                "UPDATE dispatches SET status='DISPATCHED' WHERE dispatch_id=?",
                (dispatch_id,),
            )

        controller._mutate(activate_history)
        doctor["checks"]["terminal_history_compatibility"] = [entries[0]]
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_history_receipt_alias(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]
        doctor = controller.doctor()
        history_receipt = (
            context["worker_root"]
            / ".devad"
            / "workers"
            / "worker"
            / "receipts"
            / "history-event-1.json"
        )
        fresh_receipt = (
            context["worker_root"]
            / ".devad"
            / "workers"
            / "worker"
            / "receipts"
            / "event-receipt-fresh.json"
        )
        history_receipt.write_bytes(fresh_receipt.read_bytes())
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_history_event_alias(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]
        doctor = controller.doctor()
        connection = controller._connect()
        try:
            history_id = connection.execute(
                "SELECT wo.work_order_id FROM events e "
                "JOIN work_orders wo ON wo.task_id=e.task_id LIMIT 1"
            ).fetchone()[0]
        finally:
            connection.close()

        def alias_history_event(connection):
            connection.execute(
                "UPDATE events SET event_id=? WHERE event_id=("
                "SELECT event_id FROM events e JOIN tasks t "
                "ON t.task_id=e.task_id JOIN work_orders wo "
                "ON wo.task_id=t.task_id WHERE wo.work_order_id=?)",
                ("event-receipt-fresh", history_id),
            )

        controller._mutate(alias_history_event)
        doctor["checks"]["terminal_history_compatibility"] = entries
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_history_dispatch_alias(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        entries = context["history_entries"]
        doctor = controller.doctor()
        connection = controller._connect()
        try:
            history_id = connection.execute(
                "SELECT wo.work_order_id FROM events e "
                "JOIN work_orders wo ON wo.task_id=e.task_id LIMIT 1"
            ).fetchone()[0]
        finally:
            connection.close()

        def alias_history_dispatch(connection):
            connection.execute(
                "UPDATE events SET dispatch_id=? WHERE event_id=("
                "SELECT event_id FROM events e JOIN tasks t "
                "ON t.task_id=e.task_id JOIN work_orders wo "
                "ON wo.task_id=t.task_id WHERE wo.work_order_id=?)",
                (order["dispatch_id"], history_id),
            )

        controller._mutate(alias_history_dispatch)
        doctor["checks"]["terminal_history_compatibility"] = entries
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_recovery_rejects_malformed_history_compatibility(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        doctor = controller.doctor()
        doctor["checks"]["terminal_history_compatibility"] = [
            "malformed-terminal-history-entry"
        ]
        before = self._state(controller)

        with mock.patch.object(controller, "doctor", return_value=doctor):
            with self.assertRaisesRegex(
                context["fixture"].loopctl.TaskNotReadyError,
                "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"], order["work_order_sha256"], fresh_event
                )

        self.assertEqual(before, self._state(controller))

    def test_rejects_foreign_unfinalized_receipt_without_state_delta(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        residual_path = (
            context["worker_root"]
            / ".devad"
            / "workers"
            / "worker"
            / "receipts"
            / "event-receipt-residual.json"
        )
        residual = json.loads(residual_path.read_bytes())
        residual["task_id"] = "foreign-task"
        residual_path.write_bytes(
            context["fixture"].loopctl._load_v7_contract().canonical_json_bytes(
                residual
            )
        )
        before = self._state(controller)

        with self.assertRaisesRegex(
            context["fixture"].loopctl.TaskNotReadyError,
            "RECEIPT_SET_RECOVERY_NOT_ADMISSIBLE",
        ):
            controller.recover_receipt_set_mismatch_worker_result(
                order["work_order_id"], order["work_order_sha256"], fresh_event
            )

        self.assertEqual(before, self._state(controller))

    def test_snapshot_failure_rolls_back_receipt_set_accounting(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        before = self._state(controller)

        with mock.patch.object(
            controller,
            "_snapshot_bundle",
            side_effect=RuntimeError("forced snapshot failure"),
        ):
            with self.assertRaisesRegex(
                RuntimeError, "forced snapshot failure"
            ):
                controller.recover_receipt_set_mismatch_worker_result(
                    order["work_order_id"],
                    order["work_order_sha256"],
                    fresh_event,
                )

        self.assertEqual(before, self._state(controller))

    def test_rejects_result_ready_requester_drift_without_state_delta(self):
        context, fresh_event = self._recovery_context()
        controller = context["controller"]
        order = context["order"]
        contract = context["fixture"].loopctl._load_v7_contract()
        result_path = (
            context["worker_root"]
            / ".devad"
            / "workers"
            / "worker"
            / "receipts"
            / "event-receipt-fresh.json"
        )
        result_sha256 = hashlib.sha256(result_path.read_bytes()).hexdigest()
        identity = {
            "dispatch_id": order["dispatch_id"],
            "event_id": "event-receipt-fresh",
            "packet_sha256": order["work_order_sha256"],
            "result_path": (
                ".devad/workers/worker/receipts/event-receipt-fresh.json"
            ),
            "result_sha256": result_sha256,
            "task_id": order["task_id"],
            "work_order_id": order["work_order_id"],
            "work_order_sha256": order["work_order_sha256"],
            "worker_id": "worker",
        }
        wrong = contract.build_result_ready(
            callback_id=controller._result_ready_callback_id(
                identity, "wrong-linx"
            ),
            expected_result_identity=identity,
            expires_at=controller._result_ready_expiry(),
            project_profile_id=controller._ensure_project_profile(),
            return_to_task_id="wrong-linx",
        )
        fresh_event.with_name("RESULT_READY.json").write_bytes(
            contract.canonical_json_bytes(wrong)
        )
        before = self._state(controller)

        with self.assertRaisesRegex(
            context["fixture"].loopctl.StaleCompletionError,
            "RESULT_GIT_INVALID",
        ):
            controller.recover_receipt_set_mismatch_worker_result(
                order["work_order_id"], order["work_order_sha256"], fresh_event
            )

        self.assertEqual(before, self._state(controller))


if __name__ == "__main__":
    unittest.main()
