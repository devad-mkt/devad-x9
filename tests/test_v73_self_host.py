from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import urllib.request


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


def git(repo: Path, *arguments: str) -> str:
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


class V73SelfHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loopctl = load_module("loopctl_v73_self_host", SCRIPTS / "loopctl.py")
        cls.importer = load_module(
            "program_import_v73_self_host", SCRIPTS / "program_import.py"
        )
        cls.linker = load_module(
            "linker_once_v73_self_host", SCRIPTS / "linker_once.py"
        )
        cls.finalizer = load_module(
            "worker_finalizer_v73_self_host", SCRIPTS / "worker_finalizer.py"
        )

    def setUp(self) -> None:
        parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(
            prefix="x9-v73-self-host-", dir=parent
        )
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "X9 Self Host Test")
        git(self.repo, "config", "user.email", "x9-self-host@example.invalid")
        (self.repo / "src").mkdir()
        for lane in ("bootstrap", "lane-1", "lane-2", "lane-3"):
            (self.repo / "src" / f"{lane}.py").write_text(
                f'LANE = "{lane}"\n', encoding="utf-8"
            )
        (self.repo / "import-source").mkdir()
        (self.repo / "import-source" / "feature.md").write_text(
            "bounded self-host feature\n", encoding="utf-8"
        )
        git(self.repo, "add", "src", "import-source")
        git(self.repo, "commit", "-m", "self-host fixture")
        self.base_sha = git(self.repo, "rev-parse", "HEAD")
        self.controller = self.loopctl.Controller(
            self.repo, now_fn=lambda: "2026-07-16T18:00:00Z"
        )
        self.controller.init()
        self.controller.register_actor("linker", "LINX", "LINKER", "Unknown")
        for worker in ("bootstrap", "lane-1", "lane-2", "lane-3"):
            self.controller.register_actor(
                f"worker-{worker}", "WORKER", f"WORKER {worker}", "Unknown"
            )
            self.controller.register_worktree(
                f"wt-{worker}", self.repo, "self-host-fixture"
            )

    def profile_id(self) -> str:
        return json.loads(
            self.controller.project_profile_path.read_bytes()
        )["project_profile_id"]

    def stop(self) -> dict[str, object]:
        return {
            "max_attempts": 3,
            "max_model_calls": 3,
            "max_tokens": None,
            "max_wall_seconds": 600,
            "schema": "x9-loop-stop-contract-v1",
            "success_predicate": "local deterministic proof passes",
        }

    def feature(self, lane: str) -> dict[str, object]:
        return {
            "accepted": [],
            "allowed_autonomy": ["local deterministic work"],
            "attachment_hashes": [],
            "base_sha": self.base_sha,
            "branch": "main",
            "browser_acceptance": "none",
            "claims": [{"kind": "file", "path": f"src/{lane}.py"}],
            "commit_rules": ["no commit in acceptance fixture"],
            "dependencies": [],
            "deploy_gate": "none",
            "feature_id": f"feature-{lane}",
            "finish_line": "local deterministic proof passes",
            "implementation_evidence": [],
            "known_decisions": [],
            "local_work": {},
            "out_of_scope": [],
            "owner_decision_boundaries": ["external state"],
            "owner_requirement": f"complete bounded {lane} work",
            "paused": [],
            "prior_failed_attempts": [],
            "rejected": [],
            "resources": [f"self-host:{lane}"],
            "schema": "x9-loop-feature-v1",
            "security_checks": ["local secret scan"],
            "source_references": [],
            "subfeature_ids": [],
            "tests": ["local unit"],
            "tool_lessons": [],
            "unknown": [],
            "worker_id": f"worker-{lane}",
            "worktree_id": f"wt-{lane}",
            "worktree_path": str(self.repo),
        }

    def create_order(self, lane: str) -> dict[str, object]:
        feature_id = f"feature-{lane}"
        metadata = {"feature.md": {"feature_ids": [feature_id]}}
        artifacts = self.importer.build_import_artifacts(
            self.repo / "import-source", metadata_by_path=metadata
        )
        self.controller.import_program(
            {
                "feature_packets": [self.feature(lane)],
                "features": [feature_id],
                "program_id": f"program-{lane}",
                "schema": "x9-loop-program-v1",
            },
            source_git_sha=self.base_sha,
            source_root=self.repo / "import-source",
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )
        return self.controller.create_work_order(
            program_id=f"program-{lane}",
            stop=self.stop(),
            linx_id="linker",
            action_class="implementation",
        )

    def create_order_with_worktree_path(
        self, worktree_path: str, program_id: str
    ) -> dict[str, object]:
        feature_id = "feature-bootstrap"
        feature = self.feature("bootstrap")
        feature["worktree_path"] = worktree_path
        metadata = {"feature.md": {"feature_ids": [feature_id]}}
        artifacts = self.importer.build_import_artifacts(
            self.repo / "import-source", metadata_by_path=metadata
        )
        self.controller.import_program(
            {
                "feature_packets": [feature],
                "features": [feature_id],
                "program_id": program_id,
                "schema": "x9-loop-program-v1",
            },
            source_git_sha=self.base_sha,
            source_root=self.repo / "import-source",
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )
        return self.controller.create_work_order(
            program_id=program_id,
            stop=self.stop(),
            linx_id="linker",
            action_class="implementation",
        )

    def create_bootstrap_successor(self, controller) -> dict[str, object]:
        feature_id = "feature-bootstrap-successor"
        feature = self.feature("lane-1")
        feature.update(
            {
                "feature_id": feature_id,
                "worker_id": "worker-bootstrap",
                "worktree_id": "wt-bootstrap",
                "worktree_path": str(self.repo),
            }
        )
        metadata = {"feature.md": {"feature_ids": [feature_id]}}
        artifacts = self.importer.build_import_artifacts(
            self.repo / "import-source", metadata_by_path=metadata
        )
        controller.import_program(
            {
                "feature_packets": [feature],
                "features": [feature_id],
                "program_id": "program-bootstrap-successor",
                "schema": "x9-loop-program-v1",
            },
            source_git_sha=self.base_sha,
            source_root=self.repo / "import-source",
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )
        return controller.create_work_order(
            program_id="program-bootstrap-successor",
            stop=self.stop(),
            linx_id="linker",
            action_class="implementation",
        )

    def link_current_action(self, event_id: str) -> dict[str, object]:
        event_root = self.controller.root / "runtime" / "inbox" / event_id
        ack_path = event_root / "TRANSPORT_ACK.json"
        drop_path = event_root / "delivered" / "ACTION.json"
        result = self.linker.link_once(
            self.controller.action_path,
            ack_path,
            self.linker.LocalFileAdapter(drop_path),
        )
        ack_raw = ack_path.read_bytes()
        event = {
            "event_id": event_id,
            "event_type": "TRANSPORT_ACK",
            "payload_ref": {
                "path": ack_path.relative_to(self.repo).as_posix(),
                "sha256": hashlib.sha256(ack_raw).hexdigest(),
            },
            "project_profile_id": self.profile_id(),
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "linker",
            "source_role": "LINKER",
        }
        event_path = event_root / "INBOX_EVENT.json"
        event_path.write_bytes(canonical(event))
        consumed = self.controller.run_once(event_path)
        self.assertEqual("ACKNOWLEDGED", result["status"])
        self.assertEqual("CONSUMED", consumed["status"])
        return consumed

    def complete_worker(
        self,
        lane: str,
        order: dict[str, object],
        event_id: str,
        *,
        retain_worker_outbox: bool = False,
        outbox_variant: str = "exact",
    ) -> dict[str, object]:
        proof = []
        for kind in ("security", "tests"):
            relative = (
                f".devad/workers/worker-{lane}/proof/{event_id}/{kind}.json"
            )
            document = {
                "dispatch_id": order["dispatch_id"],
                "event_id": event_id,
                "kind": kind,
                "schema": "x9-loop-proof-v2",
                "status": "PASS",
                "task_id": order["task_id"],
                "work_order_id": order["work_order_id"],
                "worker_id": f"worker-{lane}",
            }
            raw = canonical(document)
            absolute = self.repo / Path(*PurePosixPath(relative).parts)
            absolute.parent.mkdir(parents=True, exist_ok=True)
            absolute.write_bytes(raw)
            proof.append(
                {
                    "kind": kind,
                    "path": relative,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
        proof_paths = [item["path"] for item in proof]
        result = {
            "attestation_path": None,
            "blocker": None,
            "budget_remaining": True,
            "c1": None,
            "c2": None,
            "change_map": {
                "changed_surface": [],
                "proof_refs": proof_paths,
                "reason": "deterministic local no-change work completed",
                "remaining_risk": "none known",
                "rollback": "no product bytes changed",
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
            "worker_id": f"worker-{lane}",
        }
        result_raw = canonical(result)
        relative_result = (
            f".devad/workers/worker-{lane}/receipts/{event_id}.json"
        )
        result_path = self.repo / Path(*PurePosixPath(relative_result).parts)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_bytes(result_raw)
        controller_event_path = (
            self.controller.root
            / "runtime"
            / "inbox"
            / event_id
            / "INBOX_EVENT.json"
        )
        event_path = controller_event_path
        if retain_worker_outbox:
            event_path = (
                self.repo
                / ".devad"
                / "workers"
                / f"worker-{lane}"
                / "outbox"
                / event_id
                / "INBOX_EVENT.json"
            )
        finalized = self.finalizer.finalize_result(
            self.repo,
            relative_result,
            event_path,
            project_profile_id=self.profile_id(),
        )
        self.assertEqual("FINALIZED", finalized["status"])
        if retain_worker_outbox:
            controller_event_path.parent.mkdir(parents=True, exist_ok=True)
            controller_event_path.write_bytes(event_path.read_bytes())
            if outbox_variant in {"result-ready", "result-ready-wrong-requester"}:
                contract = self.loopctl._load_v7_contract()
                requester = (
                    "wrong-linker"
                    if outbox_variant == "result-ready-wrong-requester"
                    else "linker"
                )
                identity = {
                    "dispatch_id": order["dispatch_id"],
                    "event_id": event_id,
                    "packet_sha256": order["work_order_sha256"],
                    "result_path": relative_result,
                    "result_sha256": hashlib.sha256(result_raw).hexdigest(),
                    "task_id": order["task_id"],
                    "work_order_id": order["work_order_id"],
                    "work_order_sha256": order["work_order_sha256"],
                    "worker_id": f"worker-{lane}",
                }
                signal = contract.build_result_ready(
                    callback_id=self.controller._result_ready_callback_id(
                        identity, requester
                    ),
                    expected_result_identity=identity,
                    expires_at="2026-07-16T18:30:00Z",
                    project_profile_id=self.profile_id(),
                    return_to_task_id=requester,
                )
                event_path.with_name("RESULT_READY.json").write_bytes(
                    contract.canonical_json_bytes(signal)
                )
            elif outbox_variant == "tampered":
                event_path.write_bytes(canonical({"tampered": True}))
            elif outbox_variant == "extra":
                event_path.with_name("unexpected.json").write_bytes(
                    canonical({"unexpected": True})
                )
            elif outbox_variant == "staged":
                git(self.repo, "add", event_path.relative_to(self.repo).as_posix())
            elif outbox_variant == "reparse":
                original_is_reparse = self.controller._is_reparse
                with mock.patch.object(
                    self.controller,
                    "_is_reparse",
                    side_effect=lambda path: path.name == "outbox"
                    or original_is_reparse(path),
                ):
                    return self.controller.run_once(controller_event_path)
        return self.controller.run_once(controller_event_path)

    def test_no_change_result_accepts_exact_worker_outbox_copy(self):
        order = self.create_order("bootstrap")
        self.link_current_action("event-outbox-linker-ack")

        completed = self.complete_worker(
            "bootstrap",
            order,
            "event-outbox-worker-result",
            retain_worker_outbox=True,
        )

        self.assertEqual("FEATURE_DONE", completed["status"])
        self.assertEqual(self.base_sha, git(self.repo, "rev-parse", "HEAD"))

    def test_worker_result_accepts_exact_result_ready_sibling(self):
        order = self.create_order("bootstrap")
        self.link_current_action("event-result-ready-linker-ack")

        completed = self.complete_worker(
            "bootstrap",
            order,
            "event-result-ready-worker-result",
            retain_worker_outbox=True,
            outbox_variant="result-ready",
        )

        self.assertEqual("FEATURE_DONE", completed["status"])

    def test_worker_result_rejects_wrong_result_ready_requester_zero_delta(self):
        order = self.create_order("bootstrap")
        self.link_current_action("event-result-ready-wrong-linker-ack")
        connection = self.controller._connect()
        try:
            before = (
                self.controller._generation(connection),
                connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            )
        finally:
            connection.close()

        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError, "RESULT_GIT_INVALID"
        ):
            self.complete_worker(
                "bootstrap",
                order,
                "event-result-ready-wrong-worker-result",
                retain_worker_outbox=True,
                outbox_variant="result-ready-wrong-requester",
            )

        connection = self.controller._connect()
        try:
            after = (
                self.controller._generation(connection),
                connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            )
        finally:
            connection.close()
        self.assertEqual(before, after)

    def test_terminal_consumed_worker_outbox_allows_restart_and_reuse(self):
        order = self.create_order("bootstrap")
        self.link_current_action("event-reuse-linker-ack")
        completed = self.complete_worker(
            "bootstrap",
            order,
            "event-reuse-worker-result",
            retain_worker_outbox=True,
        )
        self.assertEqual("FEATURE_DONE", completed["status"])

        restarted = self.loopctl.Controller(
            self.repo, now_fn=lambda: "2026-07-16T18:01:00Z"
        )
        successor = self.create_bootstrap_successor(restarted)

        self.assertEqual("CREATED", successor["status"])
        self.assertEqual(
            "SEND_WORK_ORDER",
            json.loads(restarted.action_path.read_bytes())["action"],
        )
        self.assertEqual(self.base_sha, git(self.repo, "rev-parse", "HEAD"))

    def test_superseded_consumed_worker_outbox_allows_restart_and_reuse(self):
        order = self.create_order("bootstrap")
        self.link_current_action("event-superseded-linker-ack")
        completed = self.complete_worker(
            "bootstrap",
            order,
            "event-superseded-worker-result",
            retain_worker_outbox=True,
        )
        self.assertEqual("FEATURE_DONE", completed["status"])

        def supersede(connection):
            connection.execute(
                "UPDATE tasks SET status='SUPERSEDED' WHERE task_id=?",
                (order["task_id"],),
            )
            connection.execute(
                "UPDATE work_orders SET status='SUPERSEDED' "
                "WHERE work_order_id=?",
                (order["work_order_id"],),
            )
            return {"status": "SUPERSEDED"}

        self.controller._mutate(supersede)
        restarted = self.loopctl.Controller(
            self.repo, now_fn=lambda: "2026-07-16T18:01:00Z"
        )
        successor = self.create_bootstrap_successor(restarted)

        self.assertEqual("CREATED", successor["status"])

    def controller_state(self, controller) -> tuple[object, ...]:
        connection = controller._connect()
        try:
            state = (
                controller._generation(connection),
                *(
                    connection.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    ).fetchone()[0]
                    for table in (
                        "tasks",
                        "work_orders",
                        "dispatches",
                        "events",
                        "inbox",
                    )
                ),
            )
        finally:
            connection.close()
        return (*state, controller.action_path.read_bytes())

    def assert_terminal_outbox_preflight_rejected_without_state_change(
        self, variant: str, error: str
    ) -> None:
        event_id = f"event-terminal-{variant}-worker-result"
        order = self.create_order("bootstrap")
        self.link_current_action(f"event-terminal-{variant}-linker-ack")
        completed = self.complete_worker(
            "bootstrap",
            order,
            event_id,
            retain_worker_outbox=True,
        )
        self.assertEqual("FEATURE_DONE", completed["status"])
        outbox = (
            self.repo
            / ".devad"
            / "workers"
            / "worker-bootstrap"
            / "outbox"
            / event_id
            / "INBOX_EVENT.json"
        )
        restarted = self.loopctl.Controller(
            self.repo, now_fn=lambda: "2026-07-16T18:01:00Z"
        )
        patcher = None
        if variant == "tampered":
            outbox.write_bytes(canonical({"tampered": True}))
        elif variant == "status":
            connection = restarted._connect()
            try:
                connection.execute(
                    "UPDATE inbox SET status='REJECTED:TEST' WHERE event_id=?",
                    (event_id,),
                )
                connection.commit()
            finally:
                connection.close()
        elif variant == "second-read":
            original = restarted._read_capped_packet
            reads = {"count": 0}

            def drift(path, packet_name):
                value = original(path, packet_name)
                if path == outbox and packet_name == "INBOX_EVENT.json":
                    reads["count"] += 1
                    if reads["count"] == 2:
                        return canonical({"drifted": True})
                return value

            patcher = mock.patch.object(
                restarted, "_read_capped_packet", side_effect=drift
            )
        else:
            raise AssertionError(f"unknown variant {variant}")
        before = self.controller_state(restarted)
        connection = restarted._connect()
        try:
            context = patcher if patcher is not None else mock.patch.object(
                restarted, "_read_capped_packet", wraps=restarted._read_capped_packet
            )
            with context:
                with self.assertRaisesRegex(self.loopctl.LoopError, error):
                    restarted._verify_v7_worktree_preflight(
                        self.repo, self.base_sha, connection
                    )
        finally:
            connection.close()
        self.assertEqual(before, self.controller_state(restarted))

    def test_terminal_outbox_tamper_rejects_reuse_without_state_change(self):
        self.assert_terminal_outbox_preflight_rejected_without_state_change(
            "tampered", "INBOX_EVENT_INVALID"
        )

    def test_terminal_outbox_status_drift_rejects_reuse_without_state_change(self):
        self.assert_terminal_outbox_preflight_rejected_without_state_change(
            "status", "RECEIPT_SET_MISMATCH"
        )

    def test_terminal_outbox_second_read_drift_rejects_without_state_change(self):
        self.assert_terminal_outbox_preflight_rejected_without_state_change(
            "second-read", "RESULT_GIT_INVALID"
        )

    def assert_worker_result_rejected_without_state_change(
        self, variant: str, error: str
    ) -> None:
        order = self.create_order("bootstrap")
        self.link_current_action(f"event-{variant}-linker-ack")
        connection = self.controller._connect()
        try:
            before = (
                connection.execute(
                    "SELECT value FROM meta WHERE key='generation'"
                ).fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM inbox").fetchone()[0],
            )
        finally:
            connection.close()

        with self.assertRaisesRegex(self.loopctl.StaleCompletionError, error):
            self.complete_worker(
                "bootstrap",
                order,
                f"event-{variant}-worker-result",
                retain_worker_outbox=True,
                outbox_variant=variant,
            )

        connection = self.controller._connect()
        try:
            after = (
                connection.execute(
                    "SELECT value FROM meta WHERE key='generation'"
                ).fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                connection.execute("SELECT COUNT(*) FROM inbox").fetchone()[0],
            )
            lifecycle = tuple(
                connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone()
            )
        finally:
            connection.close()
        self.assertEqual(before, after)
        self.assertEqual(("REGISTERED", "CREATED", "DISPATCHED"), lifecycle)

    def test_tampered_worker_outbox_is_rejected_without_state_change(self):
        self.assert_worker_result_rejected_without_state_change(
            "tampered", "INBOX_EVENT_INVALID"
        )

    def test_extra_worker_outbox_sibling_is_rejected_without_state_change(self):
        self.assert_worker_result_rejected_without_state_change(
            "extra", "RESULT_GIT_INVALID"
        )

    def test_staged_worker_outbox_is_rejected_without_state_change(self):
        self.assert_worker_result_rejected_without_state_change(
            "staged", "RESULT_GIT_INVALID"
        )

    def test_reparse_worker_outbox_is_rejected_without_state_change(self):
        self.assert_worker_result_rejected_without_state_change(
            "reparse", "INBOX_EVENT_INVALID"
        )

    def test_self_host_bootstrap_then_preserves_three_non_overlapping_workers(self):
        bootstrap = self.create_order("bootstrap")

        with (
            mock.patch.object(
                self.controller,
                "check_model_call",
                side_effect=AssertionError("model calls are forbidden"),
            ) as model_hook,
            mock.patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("network calls are forbidden"),
            ) as socket_hook,
            mock.patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("provider calls are forbidden"),
            ) as urlopen_hook,
        ):
            self.link_current_action("event-bootstrap-linker-ack")
            completed = self.complete_worker(
                "bootstrap", bootstrap, "event-bootstrap-worker-result"
            )

        self.assertEqual("FEATURE_DONE", completed["status"])
        model_hook.assert_not_called()
        socket_hook.assert_not_called()
        urlopen_hook.assert_not_called()

        orders = [self.create_order(f"lane-{index}") for index in range(1, 4)]
        self.assertTrue(all(order["status"] == "CREATED" for order in orders))

        connection = self.controller._connect()
        try:
            prepared = list(
                connection.execute(
                    "SELECT d.dispatch_id,o.payload "
                    "FROM dispatches d JOIN outbox o ON o.dispatch_id=d.dispatch_id "
                    "WHERE d.status='PREPARED' ORDER BY d.created_at,d.dispatch_id"
                )
            )
            active_claims = list(
                connection.execute(
                    "SELECT c.path,c.kind FROM claims c JOIN tasks t ON t.task_id=c.task_id "
                    "WHERE t.status='REGISTERED' ORDER BY c.path"
                )
            )
            active_resources = list(
                connection.execute(
                    "SELECT r.resource FROM resources r JOIN tasks t ON t.task_id=r.task_id "
                    "WHERE t.status='REGISTERED' ORDER BY r.resource"
                )
            )
        finally:
            connection.close()

        self.assertEqual(3, len(prepared))
        self.assertEqual(
            [(f"src/lane-{index}.py", "file") for index in range(1, 4)],
            [tuple(row) for row in active_claims],
        )
        self.assertEqual(
            [(f"self-host:lane-{index}",) for index in range(1, 4)],
            [tuple(row) for row in active_resources],
        )
        queued_payloads = [
            canonical(json.loads(row["payload"])) for row in prepared
        ]
        current_action = self.controller.action_path.read_bytes()
        self.assertEqual(1, queued_payloads.count(current_action))
        self.assertEqual(
            [self.controller.action_path],
            list(self.controller.action_path.parent.glob("ACTION*.json")),
        )
        self.assertEqual(3, len({order["dispatch_id"] for order in orders}))

    def test_verify_work_order_accepts_equivalent_worktree_path_spelling(self):
        created = self.create_order_with_worktree_path(
            str(self.repo / ".." / self.repo.name),
            "program-equivalent-worktree-path",
        )

        verified = self.controller.verify_work_order(created["work_order_id"])

        self.assertEqual(
            created["work_order_id"], verified["work_order_id"]
        )

    def test_verify_work_order_authenticates_before_untrusted_path_resolution(self):
        created = self.create_order_with_worktree_path(
            str(self.repo), "program-tampered-worktree-path"
        )
        packet_path = self.repo / created["work_order_path"]
        tampered = json.loads(packet_path.read_bytes())
        tampered["worktree_path"] = r"\\untrusted.invalid\share\repo"
        packet_path.write_bytes(canonical(tampered))
        original_resolve = Path.resolve

        def reject_untrusted_resolve(candidate, *args, **kwargs):
            if str(candidate) == tampered["worktree_path"]:
                raise AssertionError("untrusted Work Order path was resolved")
            return original_resolve(candidate, *args, **kwargs)

        with mock.patch.object(Path, "resolve", reject_untrusted_resolve):
            with self.assertRaisesRegex(
                self.loopctl.IdentityError, "WORK_ORDER_HASH_MISMATCH"
            ):
                self.controller.verify_work_order(created["work_order_id"])

    def test_verify_work_order_rejects_different_absolute_worktree(self):
        created = self.create_order_with_worktree_path(
            str(self.repo), "program-different-worktree-path"
        )
        packet_path = self.repo / created["work_order_path"]
        changed = json.loads(packet_path.read_bytes())
        changed["worktree_path"] = str(self.repo.parent)
        changed_raw = canonical(changed)
        changed_sha = hashlib.sha256(changed_raw).hexdigest()
        packet_path.write_bytes(changed_raw)
        connection = self.controller._connect()
        try:
            connection.execute(
                "UPDATE work_orders SET packet_sha256=? WHERE work_order_id=?",
                (changed_sha, created["work_order_id"]),
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "WORK_ORDER_DRIFT:worktree_path"
        ):
            self.controller.verify_work_order(created["work_order_id"])


if __name__ == "__main__":
    unittest.main()
