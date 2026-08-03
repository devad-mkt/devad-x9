from __future__ import annotations

import copy
import hashlib
import importlib.util
import threading
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "skills" / "devad-x9-loop" / "scripts" / "omp_worker_adapter.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("omp_worker_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeRunner:
    def __init__(self, result=None, error: BaseException | None = None):
        self.result = result or {"returncode": 0, "stdout": "ok", "stderr": ""}
        self.error = error
        self.calls: list[dict[str, object]] = []

    def run(
        self,
        argv: list[str],
        *,
        cwd: str,
        env_overrides: dict[str, str | None],
        input_text: str,
        timeout_seconds: int,
        cancel_event: object,
    ) -> dict[str, object]:
        self.calls.append(
            {
                "argv": list(argv),
                "cwd": cwd,
                "env_overrides": dict(env_overrides),
                "input_text": input_text,
                "timeout_seconds": timeout_seconds,
                "cancel_event": cancel_event,
            }
        )
        if self.error is not None:
            raise self.error
        return dict(self.result)


class OmpWorkerAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = load_adapter()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = self.root / "runtime"
        self.sessions = self.runtime / "sessions"
        self.sessions.mkdir(parents=True)
        self.worktree = self.root / "worktree"
        self.worktree.mkdir()
        self.git_dir = self.root / "git"
        self.git_dir.mkdir()
        self.common_dir = self.root / "common"
        self.common_dir.mkdir()
        self.settings = self.runtime / "settings.json"
        self.settings.write_bytes(b'{"profile":"isolated"}\n')
        self.discovery_home = self.runtime / "discovery-home"
        self.discovery_home.mkdir()
        self.omp_agent_dir = self.root / "omp-agent"
        self.omp_agent_dir.mkdir()
        self.executable = self.root / "omp.exe"
        self.executable.write_bytes(b"fake omp 17.0.5")
        self.session = self.sessions / "session-1.json"
        self.session.write_bytes(b"authoritative transcript\n")
        self.base_sha = "a" * 40
        self.identity = {
            "worktree_id": "wt-test",
            "worktree_path": str(self.worktree),
            "base_sha": self.base_sha,
            "head_sha": self.base_sha,
            "head_state": "CLEAN",
            "branch": None,
            "git_dir": str(self.git_dir),
            "common_dir": str(self.common_dir),
        }
        self.request = {
            "schema": "x9-omp-worker-request-v1",
            "profile": "omp",
            "session_policy": {
                "mode": "RESUME_EXACT",
                "session_id": "sess-1",
                "session_path": str(self.session),
                "session_sha256": sha256(self.session.read_bytes()),
                "parent_session_id": None,
                "parent_session_path": None,
                "parent_session_sha256": None,
                "model_policy": "KEEP",
                "recorded_model": "deepseek-chat",
                "requested_model": None,
                "requested_thinking": None,
            },
            "session_dir": str(self.runtime),
            "omp_profile": "omp-s0",
            "executable_path": str(self.executable),
            "executable_sha256": sha256(self.executable.read_bytes()),
            "omp_version": "17.0.5",
            "work_order_id": "wo-test",
            "dispatch_id": "dsp-test",
            "target_actor_id": "actor-test",
            "project_profile_id": "profile-test",
            "worktree": copy.deepcopy(self.identity),
            "current_worktree": copy.deepcopy(self.identity),
            "settings_path": str(self.settings),
            "settings_sha256": sha256(self.settings.read_bytes()),
            "prompt": "continue the bounded task",
            "prompt_sha256": sha256(b"continue the bounded task"),
            "context_capsule_sha256": "c" * 64,
            "allowed_tools": [],
            "denied_effects": ["provider", "scheduler", "worktree-mutation"],
            "provider_call_budget": 0,
            "timeout_seconds": 5,
            "run_id": "run-test",
        }

    def tearDown(self):
        self.temp.cleanup()

    def expect_error(self, code: str, callable_obj, *args, **kwargs):
        with self.assertRaises(self.adapter.AdapterError) as context:
            callable_obj(*args, **kwargs)
        self.assertEqual(code, context.exception.code)
        return context.exception

    def test_omp_resume_uses_argument_array_and_exact_cwd(self):
        command = self.adapter.build_command(self.request)

        self.assertEqual(
            [
                str(self.executable),
                "--profile",
                "omp-s0",
                "--session-dir",
                str(self.runtime),
                "--cwd",
                str(self.worktree),
                "--no-tools",
                "--resume",
                str(self.session),
            ],
            command,
        )
        self.assertNotIn(self.request["prompt"], command)

    def test_pi_resume_preserves_exact_pi_identity(self):
        request = copy.deepcopy(self.request)
        request["profile"] = "pi"

        command = self.adapter.build_command(request)

        self.assertEqual(
            [str(self.executable), "--session-dir", str(self.runtime), "--no-tools", "--session", "sess-1"],
            command,
        )
        self.assertNotIn("--profile", command)
        self.assertNotIn("--cwd", command)
        self.assertEqual("--session", command[-2])
        self.assertEqual("sess-1", command[-1])
        self.assertNotIn("--resume", command)

    def test_pi_fork_requires_parent_id_for_distinct_parent_path(self):
        parent = self.sessions / "parent-session.json"
        child = self.sessions / "child-session.json"
        parent.write_bytes(b"parent authoritative transcript\n")
        child.write_bytes(b"child target transcript\n")
        request = copy.deepcopy(self.request)
        request["profile"] = "pi"
        request["session_policy"].update(
            {
                "mode": "FORK_FROM_EXACT",
                "session_id": "child-session",
                "session_path": str(child),
                "session_sha256": sha256(child.read_bytes()),
                "parent_session_id": None,
                "parent_session_path": str(parent),
                "parent_session_sha256": sha256(parent.read_bytes()),
                "model_policy": "CHANGE_EXACT",
                "requested_model": "other-model",
            }
        )
        runner = FakeRunner()

        self.expect_error("SESSION_ID_INVALID", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_pi_fork_requires_parent_path_for_parent_id(self):
        request = copy.deepcopy(self.request)
        request["profile"] = "pi"
        request["session_policy"].update(
            {
                "mode": "FORK_FROM_EXACT",
                "parent_session_id": "parent-session",
                "parent_session_path": None,
                "parent_session_sha256": None,
                "model_policy": "CHANGE_EXACT",
                "requested_model": "other-model",
            }
        )
        runner = FakeRunner()

        self.expect_error("SESSION_INCOMPATIBLE", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_keep_has_no_model_or_thinking_override(self):
        command = self.adapter.build_command(self.request)

        self.assertNotIn("--model", command)
        self.assertNotIn("deepseek-chat", command)
        self.assertNotIn("--thinking", command)

    def test_change_exact_emits_only_bound_model_and_thinking(self):
        request = copy.deepcopy(self.request)
        request["session_policy"].update(
            {
                "mode": "FORK_FROM_EXACT",
                "parent_session_id": "sess-1",
                "parent_session_path": str(self.session),
                "parent_session_sha256": sha256(self.session.read_bytes()),
                "model_policy": "CHANGE_EXACT",
                "requested_model": "deepseek-reasoner",
                "requested_thinking": "high",
            }
        )

        command = self.adapter.build_command(request)

        self.assertEqual("deepseek-reasoner", command[command.index("--model") + 1])
        self.assertEqual("high", command[command.index("--thinking") + 1])
        self.assertEqual(1, command.count("--model"))

    def test_wrong_session_hash_rejects_before_process(self):
        request = copy.deepcopy(self.request)
        request["session_policy"]["session_sha256"] = "b" * 64
        runner = FakeRunner()

        self.expect_error("SESSION_INCOMPATIBLE", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_wrong_settings_hash_rejects_before_process(self):
        request = copy.deepcopy(self.request)
        request["settings_sha256"] = "d" * 64
        runner = FakeRunner()

        self.expect_error("SETTINGS_DRIFT", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_wrong_worktree_identity_rejects_before_process(self):
        request = copy.deepcopy(self.request)
        request["current_worktree"]["head_sha"] = "e" * 40
        runner = FakeRunner()

        self.expect_error("WORKTREE_MISMATCH", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_omp_resume_model_change_is_live_proven_and_bound(self):
        request = copy.deepcopy(self.request)
        request["session_policy"].update(
            {
                "model_policy": "CHANGE_EXACT",
                "requested_model": "opencode-go/deepseek-v4-pro",
                "requested_thinking": "high",
            }
        )
        request["allowed_tools"] = ["read"]
        runner = FakeRunner(result={"returncode": 0, "stdout": "OMP_RESUME_MODEL_OK", "stderr": ""})
        before = self.session.read_bytes()

        result = self.adapter.execute(request, runner=runner)

        self.assertEqual(1, len(runner.calls))
        self.assertEqual(before, self.session.read_bytes())
        command = runner.calls[0]["argv"]
        self.assertEqual(str(self.session), command[command.index("--resume") + 1])
        self.assertEqual("read", command[command.index("--tools") + 1])
        self.assertEqual("opencode-go/deepseek-v4-pro", command[command.index("--model") + 1])
        self.assertEqual("high", command[command.index("--thinking") + 1])
        self.assertEqual("OMP_RESUME_MODEL_OK", result["stdout"])
        self.assertEqual(0, result["provider_calls"])

    def test_omp_discovery_isolation_is_exact_and_secret_free(self):
        request = copy.deepcopy(self.request)
        request["discovery_home"] = str(self.discovery_home)
        request["omp_agent_dir"] = str(self.omp_agent_dir)
        runner = FakeRunner()

        result = self.adapter.execute(request, runner=runner)

        self.assertEqual(
            {
                "USERPROFILE": str(self.discovery_home),
                "HOME": str(self.discovery_home),
                "PI_CODING_AGENT_DIR": str(self.omp_agent_dir),
                "OMP_PROFILE": None,
                "PI_PROFILE": None,
            },
            runner.calls[0]["env_overrides"],
        )
        self.assertEqual(str(self.discovery_home), result["discovery_home"])
        self.assertEqual(str(self.omp_agent_dir), result["omp_agent_dir"])
        self.assertNotIn("token", str(runner.calls[0]["env_overrides"]).lower())
        self.assertNotIn("password", str(runner.calls[0]["env_overrides"]).lower())

    def test_tool_allowlist_rejects_comma_expansion_before_process(self):
        request = copy.deepcopy(self.request)
        request["allowed_tools"] = ["read,write"]
        runner = FakeRunner()

        error = self.expect_error(
            "EFFECT_POLICY_INVALID",
            self.adapter.execute,
            request,
            runner=runner,
        )

        self.assertEqual("allowed_tools[0]", error.details["field"])
        self.assertEqual([], runner.calls)

    def test_discovery_isolation_rejects_partial_or_out_of_scope_binding(self):
        partial = copy.deepcopy(self.request)
        partial["discovery_home"] = str(self.discovery_home)
        partial_runner = FakeRunner()
        self.expect_error(
            "DISCOVERY_ISOLATION_INVALID",
            self.adapter.execute,
            partial,
            runner=partial_runner,
        )
        self.assertEqual([], partial_runner.calls)

        outside = copy.deepcopy(self.request)
        outside_home = self.root / "outside-home"
        outside_home.mkdir()
        outside["discovery_home"] = str(outside_home)
        outside["omp_agent_dir"] = str(self.omp_agent_dir)
        outside_runner = FakeRunner()
        self.expect_error(
            "SCOPE_VIOLATION",
            self.adapter.execute,
            outside,
            runner=outside_runner,
        )
        self.assertEqual([], outside_runner.calls)

    def test_pi_resume_model_change_is_live_proven_and_bound(self):
        request = copy.deepcopy(self.request)
        request["profile"] = "pi"
        request["session_policy"].update(
            {
                "model_policy": "CHANGE_EXACT",
                "requested_model": "opencode-go/deepseek-v4-pro",
                "requested_thinking": "high",
            }
        )
        runner = FakeRunner(result={"returncode": 0, "stdout": "PI_RESUME_MODEL_VISIBLE_OK", "stderr": ""})
        before = self.session.read_bytes()

        result = self.adapter.execute(request, runner=runner)

        self.assertEqual(1, len(runner.calls))
        self.assertEqual(before, self.session.read_bytes())
        command = runner.calls[0]["argv"]
        self.assertEqual(str(self.worktree), runner.calls[0]["cwd"])
        self.assertNotIn("--profile", command)
        self.assertNotIn("--cwd", command)
        self.assertEqual("opencode-go/deepseek-v4-pro", command[command.index("--model") + 1])
        self.assertEqual("high", command[command.index("--thinking") + 1])
        self.assertEqual("PI_RESUME_MODEL_VISIBLE_OK", result["stdout"])
        self.assertEqual(0, result["provider_calls"])

    def test_fork_model_change_preserves_parent_and_reports_zero_calls(self):
        request = copy.deepcopy(self.request)
        request["session_policy"].update(
            {
                "mode": "FORK_FROM_EXACT",
                "parent_session_id": "sess-1",
                "parent_session_path": str(self.session),
                "parent_session_sha256": sha256(self.session.read_bytes()),
                "model_policy": "CHANGE_EXACT",
                "requested_model": "other-model",
            }
        )
        runner = FakeRunner(result={"returncode": 0, "stdout": "forked", "stderr": ""})
        before = self.session.read_bytes()

        result = self.adapter.execute(request, runner=runner)

        self.assertEqual(1, len(runner.calls))
        self.assertEqual(before, self.session.read_bytes())
        self.assertEqual(0, result["provider_calls"])
        self.assertEqual("PASS", result["status"])
        self.assertEqual("other-model", result["requested_model"])
        self.assertIn("command_sha256", result)
        self.assertNotIn("command", result)

    def test_fork_uses_bound_parent_target_not_child_session(self):
        parent = self.sessions / "parent-session.json"
        child = self.sessions / "child-session.json"
        parent.write_bytes(b"parent authoritative transcript\n")
        child.write_bytes(b"child target transcript\n")
        request = copy.deepcopy(self.request)
        request["session_policy"].update(
            {
                "mode": "FORK_FROM_EXACT",
                "session_id": "child-session",
                "session_path": str(child),
                "session_sha256": sha256(child.read_bytes()),
                "parent_session_id": "parent-session",
                "parent_session_path": str(parent),
                "parent_session_sha256": sha256(parent.read_bytes()),
                "model_policy": "CHANGE_EXACT",
                "requested_model": "other-model",
            }
        )
        runner = FakeRunner(result={"returncode": 0, "stdout": "forked", "stderr": ""})

        result = self.adapter.execute(request, runner=runner)

        self.assertEqual(1, len(runner.calls))
        self.assertIn(str(parent), runner.calls[0]["argv"])
        self.assertNotIn(str(child), runner.calls[0]["argv"])
        self.assertEqual(sha256(parent.read_bytes()), result["parent_session_sha256"])
        self.assertEqual(sha256(child.read_bytes()), result["session_sha256"])

    def test_duplicate_dispatch_is_idempotent_and_does_not_run_again(self):
        runner = FakeRunner()
        receipts: dict[str, dict[str, object]] = {}

        first = self.adapter.execute(self.request, runner=runner, receipt_store=receipts)
        second = self.adapter.execute(self.request, runner=runner, receipt_store=receipts)

        self.assertEqual(1, len(runner.calls))
        self.assertEqual("PASS", first["status"])
        self.assertEqual("IDEMPOTENT_REPLAY", second["status"])
        self.assertEqual(first["idempotency_key"], second["idempotency_key"])

    def test_idempotent_replay_rejects_stored_receipt_identity_drift(self):
        runner = FakeRunner()
        receipts: dict[str, dict[str, object]] = {}
        first = self.adapter.execute(self.request, runner=runner, receipt_store=receipts)
        receipts[first["idempotency_key"]]["target_actor_id"] = "actor-other"

        self.expect_error(
            "IDEMPOTENCY_CONFLICT",
            self.adapter.execute,
            self.request,
            runner=runner,
            receipt_store=receipts,
        )

        self.assertEqual(1, len(runner.calls))

    def test_missing_or_out_of_scope_session_fails_closed(self):
        request = copy.deepcopy(self.request)
        request["session_policy"]["session_path"] = str(self.root / "outside.json")
        request["session_policy"]["session_sha256"] = "f" * 64
        runner = FakeRunner()

        self.expect_error("SCOPE_VIOLATION", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_settings_outside_declared_runtime_scope_is_rejected(self):
        request = copy.deepcopy(self.request)
        request["settings_path"] = str(self.root / "outside-settings.json")
        Path(request["settings_path"]).write_bytes(b"outside")
        request["settings_sha256"] = sha256(b"outside")
        runner = FakeRunner()

        self.expect_error("SCOPE_VIOLATION", self.adapter.execute, request, runner=runner)

        self.assertEqual([], runner.calls)

    def test_timeout_and_cancellation_are_typed_and_prelaunch(self):
        timeout_runner = FakeRunner(error=TimeoutError("slow"))
        self.expect_error("TIMEOUT", self.adapter.execute, self.request, runner=timeout_runner)

        cancelled = threading.Event()
        cancelled.set()
        cancel_runner = FakeRunner()
        self.expect_error(
            "CANCELLED",
            self.adapter.execute,
            self.request,
            runner=cancel_runner,
            cancel_event=cancelled,
        )
        self.assertEqual([], cancel_runner.calls)

    def test_stream_redaction_never_returns_credentials(self):
        text = (
            "api_" + "key=" + "secret-value "
            + "Bearer " + "bearer-value "
            + "pass" + "word:" + "pass-value"
        )

        redacted = self.adapter.redact_stream(text)

        self.assertNotIn("secret-value", redacted)
        self.assertNotIn("bearer-value", redacted)
        self.assertNotIn("pass-value", redacted)
        self.assertIn("[REDACTED]", redacted)

    def test_process_streams_are_redacted_in_receipt(self):
        runner = FakeRunner(
            result={
                "returncode": 0,
                "stdout": "token=" + "secret-value",
                "stderr": "Bearer " + "bearer-value",
            }
        )

        result = self.adapter.execute(self.request, runner=runner)

        self.assertNotIn("secret-value", result["stdout"])
        self.assertNotIn("bearer-value", result["stderr"])
        self.assertEqual(0, result["provider_calls"])

    def test_disabled_profiles_fail_without_fallback(self):
        for profile, expected in (("opencode", "PROFILE_DISABLED"), ("command-code", "RESUME_UNSUPPORTED")):
            request = copy.deepcopy(self.request)
            request["profile"] = profile
            runner = FakeRunner()

            self.expect_error(expected, self.adapter.execute, request, runner=runner)
            self.assertEqual([], runner.calls)

    def test_new_model_choice_is_scoped_to_one_request(self):
        first = copy.deepcopy(self.request)
        first["session_policy"] = {
            "mode": "NEW",
            "session_id": None,
            "session_path": None,
            "session_sha256": None,
            "parent_session_id": None,
            "parent_session_path": None,
            "parent_session_sha256": None,
            "model_policy": "CHANGE_EXACT",
            "recorded_model": None,
            "requested_model": "model-one",
            "requested_thinking": None,
        }
        second = copy.deepcopy(first)
        second["session_policy"]["requested_model"] = "model-two"
        runner = FakeRunner()

        self.adapter.execute(first, runner=runner)
        self.adapter.execute(second, runner=runner)

        self.assertEqual(2, len(runner.calls))
        self.assertEqual("model-one", runner.calls[0]["argv"][runner.calls[0]["argv"].index("--model") + 1])
        self.assertEqual("model-two", runner.calls[1]["argv"][runner.calls[1]["argv"].index("--model") + 1])

    def test_session_hash_and_update_failure_preserve_old_bytes(self):
        before = self.session.read_bytes()
        expected = sha256(before)

        self.assertEqual(
            "PASS",
            self.adapter.verify_update_compatibility(
                str(self.session), expected, compatible=True
            )["status"],
        )
        self.expect_error(
            "SESSION_VERSION_INCOMPATIBLE",
            self.adapter.verify_update_compatibility,
            str(self.session),
            expected,
            compatible=False,
        )
        self.assertEqual(before, self.session.read_bytes())

    def test_no_runner_means_no_provider_call(self):
        self.expect_error("PROVIDER_CALLS_FORBIDDEN", self.adapter.execute, self.request)


if __name__ == "__main__":
    unittest.main()
