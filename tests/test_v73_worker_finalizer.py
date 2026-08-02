from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import importlib.util
import io
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


def worker_result(event_id: str = "event-one") -> dict[str, object]:
    security_path = ".devad/workers/worker-one/proof/event-one/security.json"
    tests_path = ".devad/workers/worker-one/proof/event-one/tests.json"
    return {
        "attestation_path": None,
        "blocker": None,
        "budget_remaining": True,
        "c1": None,
        "c2": None,
        "change_map": {
            "changed_surface": [],
            "proof_refs": [security_path, tests_path],
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
            {"kind": "security", "path": security_path, "sha256": "b" * 64},
            {"kind": "tests", "path": tests_path, "sha256": "c" * 64},
        ],
        "role": "WORKER",
        "schema": "x9-loop-result-v2",
        "task_id": "task-one",
        "work_order_id": "wo-one",
        "work_order_sha256": "a" * 64,
        "worker_id": "worker-one",
    }


class WorkerFinalizerInboxEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.finalizer = load_module("worker_finalizer")
        cls.contract = load_module("v7_contract")

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.relative = ".devad/workers/worker-one/receipts/event-one.json"
        self.result_path = self.repo / Path(*self.relative.split("/"))
        self.result_path.parent.mkdir(parents=True)
        self.result_raw = canonical(worker_result())
        self.result_path.write_bytes(self.result_raw)
        self.event_path = self.repo / "runtime" / "inbox" / "event-one.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def finalize(self, profile: str = PROFILE_ID):
        return self.finalizer.finalize_result(
            self.repo,
            self.relative,
            self.event_path,
            project_profile_id=profile,
        )

    def test_emits_exact_hash_bound_inbox_envelope_accepted_by_contract(self):
        finalized = self.finalize()

        self.assertEqual("FINALIZED", finalized["status"])
        self.assertEqual(self.result_raw, self.result_path.read_bytes())
        event_raw = self.event_path.read_bytes()
        result_sha = hashlib.sha256(self.result_raw).hexdigest()
        expected = {
            "event_id": "event-one",
            "event_type": "WORKER_RESULT",
            "payload_ref": {"path": self.relative, "sha256": result_sha},
            "project_profile_id": PROFILE_ID,
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "worker-one",
            "source_role": "WORKER",
        }
        self.assertEqual(canonical(expected), event_raw)
        event_sha = hashlib.sha256(event_raw).hexdigest()
        self.assertEqual(event_sha, finalized["event_sha256"])
        self.assertEqual(
            expected,
            self.contract.validate_inbox_event(event_raw, event_sha, PROFILE_ID),
        )
        self.assertNotIn(b"command", event_raw)
        self.assertNotIn(b"secret", event_raw)
        self.assertNotIn(b"provider", event_raw)

    def test_exact_replay_is_zero_write_and_profile_conflict_fails_closed(self):
        first = self.finalize()
        first_raw = self.event_path.read_bytes()

        replay = self.finalize()

        self.assertEqual("ALREADY_FINALIZED", replay["status"])
        self.assertEqual(first["event_sha256"], replay["event_sha256"])
        self.assertEqual(first_raw, self.event_path.read_bytes())
        with self.assertRaisesRegex(
            self.finalizer.FinalizerError, "EVENT_RECEIPT_CONFLICT"
        ):
            self.finalize("profile-fedcba9876543210")
        self.assertEqual(first_raw, self.event_path.read_bytes())

    def test_rejects_noncanonical_escape_and_non_worker_identity(self):
        with self.assertRaisesRegex(
            self.finalizer.FinalizerError, "RESULT_PATH_INVALID"
        ):
            self.finalizer.finalize_result(
                self.repo,
                "../outside.json",
                self.event_path,
                project_profile_id=PROFILE_ID,
            )

        self.result_path.write_text(
            json.dumps(worker_result(), indent=2), encoding="utf-8"
        )
        with self.assertRaisesRegex(
            self.finalizer.FinalizerError, "RESULT_NOT_CANONICAL"
        ):
            self.finalize()

        invalid = worker_result()
        invalid["role"] = "THINX"
        self.result_path.write_bytes(canonical(invalid))
        with self.assertRaisesRegex(
            self.finalizer.FinalizerError, "RESULT_IDENTITY_INVALID"
        ):
            self.finalize()

    def test_publication_race_never_overwrites_competing_bytes(self):
        original_link = self.finalizer.os.link

        def racing_link(source, target, *args, **kwargs):
            Path(target).write_bytes(b"competing-bytes")
            return original_link(source, target, *args, **kwargs)

        with mock.patch.object(self.finalizer.os, "link", side_effect=racing_link):
            with self.assertRaisesRegex(
                self.finalizer.FinalizerError, "EVENT_RECEIPT_CONFLICT"
            ):
                self.finalize()
        self.assertEqual(b"competing-bytes", self.event_path.read_bytes())

    def test_cli_requires_and_accepts_project_profile_id(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            self.finalizer.main(
                [
                    "--repo",
                    str(self.repo),
                    "--result-path",
                    self.relative,
                    "--event-output",
                    str(self.event_path),
                ]
            )
        self.assertEqual(2, caught.exception.code)

        class BinaryStdout:
            def __init__(self) -> None:
                self.buffer = io.BytesIO()

        stdout = BinaryStdout()
        with mock.patch.object(self.finalizer.sys, "stdout", stdout):
            code = self.finalizer.main(
                [
                    "--repo",
                    str(self.repo),
                    "--result-path",
                    self.relative,
                    "--event-output",
                    str(self.event_path),
                    "--project-profile-id",
                    PROFILE_ID,
                ]
            )
        self.assertEqual(0, code)
        self.assertEqual(
            "FINALIZED", json.loads(stdout.buffer.getvalue())["status"]
        )


if __name__ == "__main__":
    unittest.main()
