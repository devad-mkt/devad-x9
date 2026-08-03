from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "devad-x9-loop" / "scripts"
PROFILE_FALLBACK = "profile-0123456789abcdef"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


def run_git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )
    if completed.returncode:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


class LocalAdapter:
    adapter_id = "test-local-v1"
    delivery_mode = "DURABLE_NONWAKING_DROP"

    def __init__(self) -> None:
        self.calls = 0

    def deliver(self, action_bytes: bytes, action_sha256: str) -> str:
        self.calls += 1
        if hashlib.sha256(action_bytes).hexdigest() != action_sha256:
            raise AssertionError("action hash mismatch")
        return "ACKNOWLEDGED"


class V73RunOnceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loopctl = load_module("loopctl_v73_run_once_test", SCRIPTS / "loopctl.py")
        cls.importer = load_module(
            "program_import_v73_run_once_test", SCRIPTS / "program_import.py"
        )
        cls.contract = load_module(
            "v7_contract_v73_run_once_test", SCRIPTS / "v7_contract.py"
        )
        cls.linker = load_module(
            "linker_once_v73_run_once_test", SCRIPTS / "linker_once.py"
        )

    def setUp(self) -> None:
        parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="x9-v73-run-once-", dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        run_git(self.repo, "init", "-b", "main")
        run_git(self.repo, "config", "user.name", "X9 Lite Test")
        run_git(self.repo, "config", "user.email", "x9-lite@example.invalid")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "a.py").write_text("A = 1\n", encoding="utf-8")
        (self.repo / "src" / "b.py").write_text("B = 1\n", encoding="utf-8")
        (self.repo / "import-source").mkdir()
        (self.repo / "import-source" / "feature.md").write_text(
            "bounded feature\n", encoding="utf-8"
        )
        run_git(self.repo, "add", "src", "import-source")
        run_git(self.repo, "commit", "-m", "fixture")
        self.base_sha = run_git(self.repo, "rev-parse", "HEAD")
        self.controller = self.loopctl.Controller(
            self.repo, now_fn=lambda: "2026-07-16T12:00:00Z"
        )
        self.controller.init()
        self.controller.register_actor("linker", "LINX", "LINKER", "code-only")
        self.controller.register_actor("worker-a", "WORKER", "WORKER A", "Unknown")
        self.controller.register_actor("worker-b", "WORKER", "WORKER B", "Unknown")
        self.controller.register_worktree("wt-a", self.repo, "fixture")
        self.controller.register_worktree("wt-b", self.repo, "fixture")

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

    def profile_id(self) -> str:
        connection = self.controller._connect()
        try:
            row = connection.execute(
                "SELECT value FROM meta WHERE key='project_profile_id'"
            ).fetchone()
            return row[0] if row else PROFILE_FALLBACK
        finally:
            connection.close()

    def feature(self, feature_id: str, worker_id: str, suffix: str) -> dict:
        return {
            "accepted": [],
            "allowed_autonomy": ["local edits"],
            "attachment_hashes": [],
            "base_sha": self.base_sha,
            "branch": "main",
            "browser_acceptance": "none",
            "claims": [{"kind": "file", "path": f"src/{suffix}.py"}],
            "commit_rules": ["C1 then C2"],
            "dependencies": [],
            "deploy_gate": "none",
            "feature_id": feature_id,
            "finish_line": "bounded proof passes",
            "implementation_evidence": [],
            "known_decisions": [],
            "local_work": {},
            "out_of_scope": [],
            "owner_decision_boundaries": ["external state"],
            "owner_requirement": "implement one bounded feature",
            "paused": [],
            "prior_failed_attempts": [],
            "rejected": [],
            "resources": [f"fixture:{suffix}"],
            "schema": "x9-loop-feature-v1",
            "security_checks": ["secret scan"],
            "source_references": [],
            "subfeature_ids": [],
            "tests": ["unit"],
            "tool_lessons": [],
            "unknown": [],
            "worker_id": worker_id,
            "worktree_id": f"wt-{suffix}",
            "worktree_path": str(self.repo),
        }

    def create_order(self, suffix: str = "a") -> dict:
        feature_id = f"feature-{suffix}"
        metadata = {"feature.md": {"feature_ids": [feature_id]}}
        artifacts = self.importer.build_import_artifacts(
            self.repo / "import-source", metadata_by_path=metadata
        )
        self.controller.import_program(
            {
                "feature_packets": [
                    self.feature(feature_id, f"worker-{suffix}", suffix)
                ],
                "features": [feature_id],
                "program_id": f"program-{suffix}",
                "schema": "x9-loop-program-v1",
            },
            source_git_sha=self.base_sha,
            source_root=self.repo / "import-source",
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )
        return self.controller.create_work_order(
            program_id=f"program-{suffix}",
            stop={
                "max_attempts": 3,
                "max_model_calls": 4,
                "max_tokens": None,
                "max_wall_seconds": 600,
                "schema": "x9-loop-stop-contract-v1",
                "success_predicate": "proof passes",
            },
            linx_id="linker",
            action_class="implementation",
        )

    def write_ack_event(
        self,
        action_raw: bytes,
        *,
        event_id: str = "evt-transport-ack",
        profile_id: str | None = None,
    ) -> tuple[Path, Path]:
        action = json.loads(action_raw)
        action_sha256 = hashlib.sha256(action_raw).hexdigest()
        ack = {
            "ack_id": "ack-" + action_sha256[:32],
            "action": "SEND_WORK_ORDER",
            "action_id": action["action_id"],
            "action_sha256": action_sha256,
            "dispatch_id": action["dispatch_id"],
            "project_profile_id": action.get(
                "project_profile_id", self.profile_id()
            ),
            "schema": "x9-loop-transport-ack-v1",
            "status": "DELIVERED",
            "work_order_id": action.get("work_order_id", "wo-missing-in-action"),
            "work_order_sha256": action["work_order_sha256"],
            "worker_id": action["target_actor_id"],
        }
        ack_raw = canonical(ack)
        inbox = self.controller.root / "runtime" / "inbox" / event_id
        inbox.mkdir(parents=True, exist_ok=True)
        ack_path = inbox / "TRANSPORT_ACK.json"
        ack_path.write_bytes(ack_raw)
        envelope = {
            "event_id": event_id,
            "event_type": "TRANSPORT_ACK",
            "payload_ref": {
                "path": ack_path.relative_to(self.repo).as_posix(),
                "sha256": hashlib.sha256(ack_raw).hexdigest(),
            },
            "project_profile_id": profile_id or self.profile_id(),
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "linker",
            "source_role": "LINKER",
        }
        event_path = inbox / "INBOX_EVENT.json"
        event_path.write_bytes(canonical(envelope))
        return event_path, ack_path

    def test_action_v2_binds_profile_and_work_order_under_cap(self):
        order = self.create_order()
        raw = self.controller.action_path.read_bytes()
        action = json.loads(raw)
        self.assertEqual(canonical(action), raw)
        self.assertLessEqual(len(raw), 4 * 1024)
        self.assertEqual(order["work_order_id"], action["work_order_id"])
        self.assertEqual(self.profile_id(), action["project_profile_id"])
        self.assertRegex(action["project_profile_id"], r"^[A-Za-z0-9._:-]{16,128}$")

    def test_run_once_rejects_oversized_event_and_payload_before_read(self):
        inbox = self.controller.root / "runtime" / "inbox" / "oversized-event"
        inbox.mkdir(parents=True, exist_ok=True)
        event_path = inbox / "INBOX_EVENT.json"
        event_path.write_bytes(
            b"x" * (self.contract.PACKET_CAPS["INBOX_EVENT.json"] + 1)
        )
        generation_before = self.generation()
        original_read_bytes = Path.read_bytes

        def guard_event(path):
            if path == event_path:
                raise AssertionError("oversized event must not be read")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guard_event):
            with self.assertRaisesRegex(
                self.loopctl.IdentityError, "INBOX_EVENT_PATH_INVALID"
            ):
                self.controller.run_once(event_path)
        self.assertEqual(generation_before, self.generation())

        self.create_order()
        payload_event, payload_path = self.write_ack_event(
            self.controller.action_path.read_bytes(),
            event_id="evt-oversized-payload",
        )
        payload_raw = b"x" * (
            self.contract.PACKET_CAPS["TRANSPORT_ACK.json"] + 1
        )
        payload_path.write_bytes(payload_raw)
        envelope = json.loads(payload_event.read_bytes())
        envelope["payload_ref"]["sha256"] = hashlib.sha256(
            payload_raw
        ).hexdigest()
        payload_event.write_bytes(canonical(envelope))
        generation_before = self.generation()

        def guard_payload(path):
            if path == payload_path:
                raise AssertionError("oversized payload must not be read")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guard_payload):
            with self.assertRaisesRegex(
                self.loopctl.IdentityError, "INBOX_PAYLOAD_PATH_INVALID"
            ):
                self.controller.run_once(payload_event)
        self.assertEqual(generation_before, self.generation())

    def test_run_once_consumes_one_canonical_transport_ack_atomically(self):
        self.create_order()
        action_raw = self.controller.action_path.read_bytes()
        action = json.loads(action_raw)
        event_path, _ = self.write_ack_event(action_raw)
        before = self.generation()

        result = self.controller.run_once(event_path)

        self.assertEqual("CONSUMED", result["status"])
        self.assertEqual("evt-transport-ack", result["event_id"])
        self.assertEqual(before + 1, self.generation())
        connection = self.controller._connect()
        try:
            self.assertEqual(
                ("CONSUMED", action["dispatch_id"]),
                tuple(
                    connection.execute(
                        "SELECT status,dispatch_id FROM inbox WHERE event_id=?",
                        ("evt-transport-ack",),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                "DISPATCHED",
                connection.execute(
                    "SELECT status FROM dispatches WHERE dispatch_id=?",
                    (action["dispatch_id"],),
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM deliveries WHERE dispatch_id=? AND phase='DISPATCH'",
                    (action["dispatch_id"],),
                ).fetchone()[0],
            )
        finally:
            connection.close()

    def test_exact_duplicate_is_zero_delta_and_republishes_current_action(self):
        self.create_order()
        original_action = self.controller.action_path.read_bytes()
        event_path, _ = self.write_ack_event(original_action)
        self.controller.run_once(event_path)
        expected_current = self.controller.action_path.read_bytes()
        before = self.generation()
        self.controller.action_path.write_bytes(original_action)

        result = self.controller.run_once(event_path)

        self.assertEqual("ALREADY_CONSUMED", result["status"])
        self.assertEqual(before, self.generation())
        self.assertEqual(expected_current, self.controller.action_path.read_bytes())
        connection = self.controller._connect()
        try:
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM inbox WHERE event_id='evt-transport-ack'"
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM deliveries WHERE phase='DISPATCH'"
                ).fetchone()[0],
            )
        finally:
            connection.close()

    def test_cross_profile_and_tampered_payload_fail_before_state_change(self):
        self.create_order()
        action_raw = self.controller.action_path.read_bytes()
        action_before = self.controller.action_path.read_bytes()
        generation_before = self.generation()
        cross_event, _ = self.write_ack_event(
            action_raw,
            event_id="evt-cross-profile",
            profile_id="profile-ffffffffffffffff",
        )
        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "INBOX_EVENT_PROFILE_MISMATCH"
        ):
            self.controller.run_once(cross_event)

        tampered_event, ack_path = self.write_ack_event(
            action_raw, event_id="evt-tampered-payload"
        )
        ack = json.loads(ack_path.read_bytes())
        ack["ack_id"] = "ack-tampered"
        ack_path.write_bytes(canonical(ack))
        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "INBOX_PAYLOAD_HASH_MISMATCH"
        ):
            self.controller.run_once(tampered_event)

        self.assertEqual(generation_before, self.generation())
        self.assertEqual(action_before, self.controller.action_path.read_bytes())
        connection = self.controller._connect()
        try:
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM inbox").fetchone()[0])
            self.assertEqual(
                "PREPARED",
                connection.execute("SELECT status FROM dispatches").fetchone()[0],
            )
        finally:
            connection.close()

    def test_one_cycle_exposes_at_most_one_next_ready_action(self):
        first = self.create_order("a")
        second = self.create_order("b")
        current_raw = self.controller.action_path.read_bytes()
        current = json.loads(current_raw)
        other_dispatch = (
            second["dispatch_id"]
            if current["dispatch_id"] == first["dispatch_id"]
            else first["dispatch_id"]
        )
        connection = self.controller._connect()
        try:
            other_payload = connection.execute(
                "SELECT payload FROM outbox WHERE dispatch_id=?", (other_dispatch,)
            ).fetchone()[0]
        finally:
            connection.close()
        event_path, _ = self.write_ack_event(current_raw, event_id="evt-one-cycle")

        self.controller.run_once(event_path)

        self.assertEqual(json.loads(other_payload), json.loads(self.controller.action_path.read_bytes()))
        connection = self.controller._connect()
        try:
            self.assertEqual(
                [(other_dispatch, "PREPARED")],
                [
                    tuple(row)
                    for row in connection.execute(
                        "SELECT dispatch_id,status FROM dispatches WHERE status='PREPARED'"
                    )
                ],
            )
            self.assertEqual(2, connection.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0])
            self.assertEqual(1, connection.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0])
        finally:
            connection.close()

    def test_linker_and_controller_cycle_has_no_model_or_provider_hook(self):
        self.create_order()
        action_path = self.controller.action_path
        ack_path = self.controller.root / "runtime" / "linker" / "ACK.json"
        adapter = LocalAdapter()
        self.assertFalse(
            {"model", "model_call", "provider", "provider_call"}
            & set(inspect.signature(self.controller.run_once).parameters)
        )
        self.assertFalse(
            {"model", "model_call", "provider", "provider_call"}
            & set(inspect.signature(self.linker.link_once).parameters)
        )
        self.assertFalse(hasattr(self.linker, "model_call"))
        self.assertFalse(hasattr(self.linker, "provider_call"))

        self.linker.link_once(action_path, ack_path, adapter)
        ack_raw = ack_path.read_bytes()
        inbox = self.controller.root / "runtime" / "inbox" / "evt-zero-model"
        inbox.mkdir(parents=True, exist_ok=True)
        inbox_ack = inbox / "TRANSPORT_ACK.json"
        inbox_ack.write_bytes(ack_raw)
        envelope = {
            "event_id": "evt-zero-model",
            "event_type": "TRANSPORT_ACK",
            "payload_ref": {
                "path": inbox_ack.relative_to(self.repo).as_posix(),
                "sha256": hashlib.sha256(ack_raw).hexdigest(),
            },
            "project_profile_id": self.profile_id(),
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "linker",
            "source_role": "LINKER",
        }
        event_path = inbox / "INBOX_EVENT.json"
        event_path.write_bytes(canonical(envelope))

        with mock.patch.object(
            self.controller,
            "check_model_call",
            side_effect=AssertionError("model call forbidden in deterministic cycle"),
        ) as model_hook:
            self.controller.run_once(event_path)

        model_hook.assert_not_called()
        self.assertEqual(1, adapter.calls)


if __name__ == "__main__":
    unittest.main()
