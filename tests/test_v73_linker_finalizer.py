from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "devad-x9-loop" / "scripts"
PROFILE_ID = "profile-0123456789abcdef"


def load_module(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


class SpyAdapter:
    adapter_id = "test-local-v1"
    delivery_mode = "DURABLE_NONWAKING_DROP"

    def __init__(self) -> None:
        self.calls: list[bytes] = []

    def deliver(self, action_bytes: bytes, action_sha256: str) -> str:
        self.calls.append(action_bytes)
        if hashlib.sha256(action_bytes).hexdigest() != action_sha256:
            raise AssertionError("adapter received wrong hash")
        return "ACKNOWLEDGED"


class WakingAdapter(SpyAdapter):
    delivery_mode = "MODEL_WAKING"


class LinkerOnceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.linker = load_module("linker_once")

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def action(action_id: str = "act-11111111-1111-1111-1111-111111111111") -> dict:
        return {
            "action": "SEND_WORK_ORDER",
            "action_id": action_id,
            "attempt": 1,
            "dispatch_id": "dsp-one",
            "must_record_transport": True,
            "project_profile_id": "profile-0123456789abcdef",
            "schema": "x9-loop-action-v2",
            "target_actor_id": "worker-one",
            "target_role": "WORKER",
            "task_id": "task-one",
            "work_order_id": "wo-one",
            "work_order_path": ".devad/manager/loop-lite/programs/p/WORK_ORDER.json",
            "work_order_sha256": "a" * 64,
        }

    def test_transports_exact_action_once_and_emits_secret_safe_ack(self):
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        raw = canonical(self.action())
        action_path.write_bytes(raw)
        adapter = SpyAdapter()

        result = self.linker.link_once(action_path, ack_path, adapter)

        self.assertEqual([raw], adapter.calls)
        self.assertEqual("ACKNOWLEDGED", result["status"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), result["action_sha256"])
        ack_raw = ack_path.read_bytes()
        self.assertEqual(canonical(json.loads(ack_raw)), ack_raw)
        ack = json.loads(ack_raw)
        self.assertEqual(
            {
                "ack_id": "ack-" + hashlib.sha256(raw).hexdigest()[:32],
                "action": "SEND_WORK_ORDER",
                "action_id": "act-11111111-1111-1111-1111-111111111111",
                "action_sha256": hashlib.sha256(raw).hexdigest(),
                "dispatch_id": "dsp-one",
                "project_profile_id": "profile-0123456789abcdef",
                "schema": "x9-loop-transport-ack-v1",
                "status": "DELIVERED",
                "work_order_id": "wo-one",
                "work_order_sha256": "a" * 64,
                "worker_id": "worker-one",
            },
            ack,
        )
        contract = load_module("v7_contract")
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
            contract.validate_transport_ack(
                ack_raw, hashlib.sha256(ack_raw).hexdigest(), expected
            ),
        )

    def test_rejects_model_waking_adapter_before_delivery(self):
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        action_path.write_bytes(canonical(self.action()))
        adapter = WakingAdapter()

        with self.assertRaisesRegex(
            self.linker.LinkerError, "WAKING_ADAPTER_FORBIDDEN"
        ):
            self.linker.link_once(action_path, ack_path, adapter)

        self.assertEqual([], adapter.calls)
        self.assertFalse(ack_path.exists())

    def test_rejects_action_without_profile_or_work_order_identity(self):
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        adapter = SpyAdapter()
        for missing in ("project_profile_id", "work_order_id"):
            with self.subTest(missing=missing):
                action = self.action()
                del action[missing]
                action_path.write_bytes(canonical(action))
                with self.assertRaisesRegex(
                    self.linker.LinkerError, "ACTION_FIELDS_INVALID"
                ):
                    self.linker.link_once(action_path, ack_path, adapter)
        self.assertEqual([], adapter.calls)

    def test_exact_ack_replay_rechecks_delivery_and_conflict_fails_closed(self):
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        action_path.write_bytes(canonical(self.action()))
        adapter = SpyAdapter()
        first = self.linker.link_once(action_path, ack_path, adapter)
        first_raw = ack_path.read_bytes()

        replay = self.linker.link_once(action_path, ack_path, adapter)

        self.assertEqual("ALREADY_ACKNOWLEDGED", replay["status"])
        self.assertEqual(2, len(adapter.calls))
        self.assertEqual(first_raw, ack_path.read_bytes())
        self.assertEqual(first["ack_sha256"], replay["ack_sha256"])

        action_path.write_bytes(canonical(self.action("act-22222222-2222-2222-2222-222222222222")))
        with self.assertRaisesRegex(self.linker.LinkerError, "ACK_RECEIPT_CONFLICT"):
            self.linker.link_once(action_path, ack_path, adapter)
        self.assertEqual(2, len(adapter.calls))

    def test_local_file_adapter_is_exact_byte_idempotent(self):
        destination = self.root / "worker" / "ACTION.json"
        adapter = self.linker.LocalFileAdapter(destination, "file-drop-v1")
        raw = canonical(self.action())
        digest = hashlib.sha256(raw).hexdigest()

        self.assertEqual("ACKNOWLEDGED", adapter.deliver(raw, digest))
        self.assertEqual(raw, destination.read_bytes())
        self.assertEqual("ALREADY_DELIVERED", adapter.deliver(raw, digest))

        with self.assertRaisesRegex(self.linker.LinkerError, "DELIVERY_TARGET_CONFLICT"):
            adapter.deliver(canonical(self.action("act-33333333-3333-3333-3333-333333333333")), hashlib.sha256(canonical(self.action("act-33333333-3333-3333-3333-333333333333"))).hexdigest())

    def test_oversized_ack_and_drop_fail_closed(self):
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        raw = canonical(self.action())
        action_path.write_bytes(raw)
        ack_path.write_bytes(b"x" * (self.linker.ACTION_CAP_BYTES + 1))
        with self.assertRaisesRegex(self.linker.LinkerError, "ACK_RECEIPT_INVALID"):
            self.linker.link_once(action_path, ack_path, SpyAdapter())

        destination = self.root / "oversized-drop" / "ACTION.json"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"x" * (len(raw) + 1))
        with self.assertRaisesRegex(self.linker.LinkerError, "DELIVERY_TARGET_CONFLICT"):
            self.linker.LocalFileAdapter(destination).deliver(
                raw, hashlib.sha256(raw).hexdigest()
            )

    def test_local_file_publication_race_never_overwrites_competing_bytes(self):
        destination = self.root / "worker" / "ACTION.json"
        adapter = self.linker.LocalFileAdapter(destination, "file-drop-v1")
        raw = canonical(self.action())
        original_link = self.linker.os.link

        def racing_link(source, target, *args, **kwargs):
            Path(target).write_bytes(b"competing-bytes")
            return original_link(source, target, *args, **kwargs)

        with mock.patch.object(
            self.linker.os,
            "link",
            side_effect=racing_link,
        ):
            with self.assertRaisesRegex(
                self.linker.LinkerError, "DELIVERY_TARGET_CONFLICT"
            ):
                adapter.deliver(raw, hashlib.sha256(raw).hexdigest())
        self.assertEqual(b"competing-bytes", destination.read_bytes())

    def test_rejects_noncanonical_or_oversized_action_before_adapter(self):
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        adapter = SpyAdapter()
        action_path.write_text(json.dumps(self.action(), indent=2), encoding="utf-8")
        with self.assertRaisesRegex(self.linker.LinkerError, "ACTION_NOT_CANONICAL"):
            self.linker.link_once(action_path, ack_path, adapter)

        action_path.write_bytes(b"{" + b" " * 4096 + b"}\n")
        with self.assertRaisesRegex(self.linker.LinkerError, "ACTION_TOO_LARGE"):
            self.linker.link_once(action_path, ack_path, adapter)
        self.assertEqual([], adapter.calls)

    def test_wait_is_a_deterministic_no_action(self):
        action = {
            "action": "WAIT",
            "action_id": "act-wait",
            "attempt": 0,
            "dispatch_id": None,
            "packet": None,
            "packet_sha256": None,
            "reason": "delivery-acknowledged",
            "schema": "x9-loop-lite-action-v1",
            "target_actor_id": None,
            "target_role": None,
            "task_id": None,
        }
        action_path = self.root / "ACTION.json"
        ack_path = self.root / "ACK.json"
        action_path.write_bytes(canonical(action))
        adapter = SpyAdapter()

        result = self.linker.link_once(action_path, ack_path, adapter)

        self.assertEqual("NO_ACTION", result["status"])
        self.assertEqual([], adapter.calls)
        self.assertFalse(ack_path.exists())


class WorkerFinalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.finalizer = load_module("worker_finalizer")

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def result(event_id: str = "event-one") -> dict:
        return {
            "attestation_path": None,
            "blocker": None,
            "budget_remaining": True,
            "c1": None,
            "c2": None,
            "change_map": {
                "changed_surface": [],
                "proof_refs": [
                    ".devad/workers/worker/proof/event-one/security.json",
                    ".devad/workers/worker/proof/event-one/tests.json",
                ],
                "reason": "verified no-change result",
                "remaining_risk": "none known",
                "rollback": "no source changes",
            },
            "changed_files": [],
            "dispatch_id": "dsp-one",
            "event_id": event_id,
            "failed_verified_approaches": 0,
            "outcome": "SUCCESS",
            "packet_sha256": "a" * 64,
            "proof": [
                {
                    "kind": "security",
                    "path": ".devad/workers/worker/proof/event-one/security.json",
                    "sha256": "b" * 64,
                },
                {
                    "kind": "tests",
                    "path": ".devad/workers/worker/proof/event-one/tests.json",
                    "sha256": "c" * 64,
                },
            ],
            "role": "WORKER",
            "schema": "x9-loop-result-v2",
            "task_id": "task-one",
            "work_order_id": "wo-one",
            "work_order_sha256": "a" * 64,
            "worker_id": "worker-one",
        }

    def test_seals_existing_result_as_exact_controller_event_locator(self):
        relative = ".devad/workers/worker-one/receipts/event-one.json"
        result_path = self.repo / Path(*relative.split("/"))
        result_path.parent.mkdir(parents=True)
        result_raw = canonical(self.result())
        result_path.write_bytes(result_raw)
        event_path = self.repo / ".devad" / "workers" / "worker-one" / "outbox" / "event-one.json"

        finalized = self.finalizer.finalize_result(
            self.repo, relative, event_path, project_profile_id=PROFILE_ID
        )

        self.assertEqual("FINALIZED", finalized["status"])
        self.assertEqual(result_raw, result_path.read_bytes())
        event_raw = event_path.read_bytes()
        self.assertEqual(canonical(json.loads(event_raw)), event_raw)
        event = json.loads(event_raw)
        self.assertEqual(
            {
                "event_id": "event-one",
                "event_type": "WORKER_RESULT",
                "payload_ref": {
                    "path": relative,
                    "sha256": hashlib.sha256(result_raw).hexdigest(),
                },
                "project_profile_id": PROFILE_ID,
                "schema": "x9-loop-inbox-event-v1",
                "source_actor_id": "worker-one",
                "source_role": "WORKER",
            },
            event,
        )

    def test_finalizer_exact_replay_is_zero_write_and_conflict_fails_closed(self):
        relative = ".devad/workers/worker-one/receipts/event-one.json"
        result_path = self.repo / Path(*relative.split("/"))
        result_path.parent.mkdir(parents=True)
        result_path.write_bytes(canonical(self.result()))
        event_path = self.repo / "ingress" / "event.json"
        first = self.finalizer.finalize_result(
            self.repo, relative, event_path, project_profile_id=PROFILE_ID
        )
        first_raw = event_path.read_bytes()

        replay = self.finalizer.finalize_result(
            self.repo, relative, event_path, project_profile_id=PROFILE_ID
        )

        self.assertEqual("ALREADY_FINALIZED", replay["status"])
        self.assertEqual(first_raw, event_path.read_bytes())
        self.assertEqual(first["event_sha256"], replay["event_sha256"])

        result_path.write_bytes(canonical(self.result("event-two")))
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "EVENT_RECEIPT_CONFLICT"):
            self.finalizer.finalize_result(
                self.repo, relative, event_path, project_profile_id=PROFILE_ID
            )
        self.assertEqual(first_raw, event_path.read_bytes())

    def test_result_and_existing_event_caps_fail_closed(self):
        relative = ".devad/workers/worker-one/receipts/event-one.json"
        result_path = self.repo / Path(*relative.split("/"))
        result_path.parent.mkdir(parents=True)
        event_path = self.repo / "ingress" / "oversized-event.json"

        result_path.write_bytes(b"x" * (self.finalizer.RESULT_CAP_BYTES + 1))
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "RESULT_TOO_LARGE"):
            self.finalizer.finalize_result(
                self.repo, relative, event_path, project_profile_id=PROFILE_ID
            )

        result_path.write_bytes(canonical(self.result()))
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(b"x" * (self.finalizer.EVENT_CAP_BYTES + 1))
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "EVENT_RECEIPT_CONFLICT"):
            self.finalizer.finalize_result(
                self.repo, relative, event_path, project_profile_id=PROFILE_ID
            )

    def test_event_publication_race_never_overwrites_competing_bytes(self):
        relative = ".devad/workers/worker-one/receipts/event-one.json"
        result_path = self.repo / Path(*relative.split("/"))
        result_path.parent.mkdir(parents=True)
        result_path.write_bytes(canonical(self.result()))
        event_path = self.repo / "ingress" / "event.json"
        original_link = self.finalizer.os.link

        def racing_link(source, target, *args, **kwargs):
            Path(target).write_bytes(b"competing-bytes")
            return original_link(source, target, *args, **kwargs)

        with mock.patch.object(
            self.finalizer.os,
            "link",
            side_effect=racing_link,
        ):
            with self.assertRaisesRegex(
                self.finalizer.FinalizerError, "EVENT_RECEIPT_CONFLICT"
            ):
                self.finalizer.finalize_result(
                    self.repo,
                    relative,
                    event_path,
                    project_profile_id=PROFILE_ID,
                )
        self.assertEqual(b"competing-bytes", event_path.read_bytes())

    def test_missing_work_order_id_returns_stable_identity_error(self):
        relative = "missing-work-order.json"
        result = self.result()
        del result["work_order_id"]
        (self.repo / relative).write_bytes(canonical(result))
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "RESULT_IDENTITY_INVALID"):
            self.finalizer.finalize_result(
                self.repo,
                relative,
                self.repo / "missing-work-order-event.json",
                project_profile_id=PROFILE_ID,
            )

    def test_finalizer_rejects_escape_noncanonical_and_identity_mismatch(self):
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "RESULT_PATH_INVALID"):
            self.finalizer.finalize_result(
                self.repo,
                "../outside-result.json",
                self.repo / "event.json",
                project_profile_id=PROFILE_ID,
            )

        relative = "result.json"
        result_path = self.repo / relative
        result_path.write_text(json.dumps(self.result(), indent=2), encoding="utf-8")
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "RESULT_NOT_CANONICAL"):
            self.finalizer.finalize_result(
                self.repo, relative, self.repo / "event.json", project_profile_id=PROFILE_ID
            )

        mismatch = self.result()
        mismatch["role"] = "THINX"
        result_path.write_bytes(canonical(mismatch))
        with self.assertRaisesRegex(self.finalizer.FinalizerError, "RESULT_IDENTITY_INVALID"):
            self.finalizer.finalize_result(
                self.repo, relative, self.repo / "event.json", project_profile_id=PROFILE_ID
            )


if __name__ == "__main__":
    unittest.main()
