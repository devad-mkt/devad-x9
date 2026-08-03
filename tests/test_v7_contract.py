from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "devad-x9-loop" / "scripts" / "v7_contract.py"
_MODULE = None


def contract_module():
    global _MODULE
    if _MODULE is not None:
        return _MODULE
    if not MODULE_PATH.is_file():
        raise AssertionError(f"missing V7 contract module: {MODULE_PATH}")
    spec = importlib.util.spec_from_file_location("x9_v7_contract_tests", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _MODULE = module
    return module


def complete_feature(feature_id: str = "feature-a") -> dict[str, object]:
    return {
        "accepted": [],
        "allowed_autonomy": [],
        "attachment_hashes": [],
        "base_sha": "b" * 40,
        "branch": "feature/test",
        "browser_acceptance": [],
        "claims": [{"path": "src/feature.py", "kind": "file"}],
        "commit_rules": [],
        "dependencies": [],
        "deploy_gate": "DENIED_UNLESS_EXPLICIT",
        "feature_id": feature_id,
        "finish_line": ["tests pass"],
        "implementation_evidence": [],
        "known_decisions": [],
        "local_work": [],
        "out_of_scope": [],
        "owner_decision_boundaries": [],
        "owner_requirement": "Implement the bounded feature.",
        "paused": [],
        "prior_failed_attempts": [],
        "rejected": [],
        "resources": ["resource:test"],
        "schema": "x9-loop-feature-v1",
        "security_checks": ["secret scan"],
        "source_references": ["TASK.md"],
        "subfeature_ids": [],
        "tests": ["focused unit test"],
        "tool_lessons": [],
        "unknown": [],
        "worktree_id": "core-x9",
        "worktree_path": "D:/repo",
    }


def feature_assignment(feature_id: str = "feature-a") -> dict[str, object]:
    return {
        "atomic_bundle": "bundle-a",
        "atomic_compatible": True,
        "base_sha": "b" * 40,
        "claims": [{"path": "src/feature.py", "kind": "file"}],
        "compatibility_hash": "c" * 64,
        "dependencies": [],
        "feature_id": feature_id,
        "finish_line": ["tests pass"],
        "path": f".devad/features/{feature_id}/FEATURE_PACKET.json",
        "resources": ["resource:test"],
        "sha256": "f" * 64,
        "worker_id": "worker-1",
        "worktree_id": "core-x9",
        "worktree_path": "D:/repo",
    }


def stop_contract(max_tokens: int | None = None) -> dict[str, object]:
    return {
        "max_attempts": 3,
        "max_model_calls": 4,
        "max_tokens": max_tokens,
        "max_wall_seconds": 60,
        "schema": "x9-loop-stop-contract-v1",
        "success_predicate": "tests pass",
    }


class CanonicalContractTests(unittest.TestCase):
    def test_canonical_json_is_sorted_compact_lf_and_rejects_floats(self):
        module = contract_module()
        self.assertEqual(b'{"a":"\xc3\xa9","b":1}\n', module.canonical_json_bytes({"b": 1, "a": chr(0xE9)}))
        with self.assertRaises(module.ContractError) as caught:
            module.canonical_json_bytes({"bad": 1.5})
        self.assertEqual("CANONICAL_FLOAT_FORBIDDEN", caught.exception.code)

    def test_context_gate_reports_exact_missing_field(self):
        module = contract_module()
        feature = complete_feature()
        module.validate_context_complete(feature)
        feature.pop("owner_requirement")
        with self.assertRaises(module.ContractError) as caught:
            module.validate_context_complete(feature)
        self.assertEqual("CONTEXT_INCOMPLETE:owner_requirement", caught.exception.code)


class WorkOrderTests(unittest.TestCase):
    def build(self, features: list[dict[str, object]]):
        module = contract_module()
        return module.build_work_order(
            action_class="worker-implementation",
            created_at="2026-07-14T00:00:00Z",
            features=features,
            program_packet_ref={"path": ".devad/manager/loop-lite/PROGRAM_PACKET.json", "sha256": "e" * 64},
            source_git_sha="a" * 40,
            source_root_sha256="d" * 64,
            stop=stop_contract(),
            task_id="task-1",
            work_order_id="wo-1",
        )

    def test_controller_builds_one_feature_order_with_canonical_hash(self):
        module = contract_module()
        order, raw, digest = self.build([feature_assignment()])
        self.assertEqual("Controller", order["writer"])
        self.assertEqual("ACTION_ONLY", order["linx_read_scope"])
        self.assertEqual(1, len(order["feature_packet_refs"]))
        self.assertEqual(raw, module.canonical_json_bytes(order))
        self.assertEqual(digest, module.sha256_bytes(raw))
        self.assertLessEqual(len(raw), module.PACKET_CAPS["WORK_ORDER.json"])

    def test_two_features_require_explicit_atomic_compatibility(self):
        module = contract_module()
        second = feature_assignment("feature-b")
        order, _, _ = self.build([feature_assignment(), second])
        self.assertEqual(2, len(order["feature_packet_refs"]))
        second["compatibility_hash"] = "d" * 64
        with self.assertRaises(module.ContractError) as caught:
            self.build([feature_assignment(), second])
        self.assertEqual("TWO_FEATURE_NOT_ATOMIC", caught.exception.code)
        with self.assertRaises(module.ContractError) as caught:
            self.build([feature_assignment(), feature_assignment("b"), feature_assignment("c")])
        self.assertEqual("WORK_ORDER_FEATURE_LIMIT", caught.exception.code)
        second = feature_assignment("feature-b")
        second["dependencies"] = ["missing-task"]
        with self.assertRaises(module.ContractError) as caught:
            self.build([feature_assignment(), second])
        self.assertEqual("TWO_FEATURE_NOT_ATOMIC", caught.exception.code)

    def test_casefold_resource_collision_is_rejected_before_work_order_build(self):
        module = contract_module()
        feature = feature_assignment()
        feature["resources"] = ["Dokploy-A", "dokploy-a"]
        with self.assertRaises(module.ContractError) as caught:
            self.build([feature])
        self.assertEqual("CANONICAL_RESOURCE_COLLISION", caught.exception.code)

    def test_any_bound_identity_drift_invalidates_order(self):
        module = contract_module()
        order, raw, digest = self.build([feature_assignment()])
        current = module.bound_work_order_context(order)
        module.validate_work_order_identity(raw, digest, current)
        current["source_root_sha256"] = "z" * 64
        with self.assertRaises(module.ContractError) as caught:
            module.validate_work_order_identity(raw, digest, current)
        self.assertEqual("WORK_ORDER_DRIFT:source_root_sha256", caught.exception.code)


class StopAndCacheTests(unittest.TestCase):
    def gate(self, **overrides):
        module = contract_module()
        values = {
            "action_class": "worker-implementation",
            "attempt": 0,
            "elapsed_seconds": 0,
            "model_calls": 0,
            "objective_satisfied": False,
            "prior_receipt": None,
            "prompt_prefix_sha256": "a" * 64,
            "stop": stop_contract(),
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        }
        values.update(overrides)
        return module.pre_model_call_gate(**values)

    def test_success_precedes_exhaustion_and_hard_bounds_forbid_call(self):
        success = self.gate(objective_satisfied=True, attempt=3, model_calls=4)
        self.assertFalse(success["allow_call"])
        self.assertEqual("FEATURE_DONE", success["event"])
        exhausted = self.gate(attempt=3)
        self.assertFalse(exhausted["allow_call"])
        self.assertEqual("OWNER_DECISION_REQUIRED", exhausted["event"])
        self.assertEqual("MAX_ATTEMPTS", exhausted["reason"])

    def test_null_token_budget_records_unknown_but_numeric_unknown_stops(self):
        allowed = self.gate(stop=stop_contract(None), token_usage="Unknown")
        self.assertTrue(allowed["allow_call"])
        stopped = self.gate(stop=stop_contract(100), token_usage="Unknown")
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("TOKEN_USAGE_UNKNOWN", stopped["reason"])

    def test_unexplained_hash_drift_stops_before_another_call(self):
        prior = {
            "action_class": "worker-implementation",
            "prompt_prefix_sha256": "a" * 64,
            "tool_schema_sha256": "b" * 64,
            "stability": "STABLE",
        }
        drift = self.gate(prior_receipt=prior, prompt_prefix_sha256="c" * 64)
        self.assertFalse(drift["allow_call"])
        self.assertEqual("CACHE_PREFIX_CHANGED", drift["event"])
        new_action_class = self.gate(
            action_class="new-controller-action-class",
            prior_receipt=prior,
            prompt_prefix_sha256="c" * 64,
        )
        self.assertFalse(new_action_class["allow_call"])
        self.assertEqual("CACHE_PREFIX_CHANGED", new_action_class["event"])

    def test_call_receipt_records_compaction_stability_and_unknown_tokens(self):
        module = contract_module()
        receipt = module.build_call_receipt(
            action_class="worker-implementation",
            attempt=1,
            call_id="call-1",
            compaction_generation=2,
            sequence=1,
            post_prompt_prefix_sha256="a" * 64,
            post_tool_schema_sha256="b" * 64,
            pre_prompt_prefix_sha256="a" * 64,
            pre_tool_schema_sha256="b" * 64,
            token_usage="Unknown",
            work_order_sha256="c" * 64,
        )
        self.assertEqual("STABLE", receipt["stability"])
        self.assertEqual("Unknown", receipt["token_usage"])
        drifted = module.build_call_receipt(**{
            **{k: v for k, v in receipt.items() if k not in {"schema", "stability", "drift_reason", "prompt_prefix_sha256", "tool_schema_sha256"}},
            "post_prompt_prefix_sha256": "c" * 64,
            "pre_prompt_prefix_sha256": "a" * 64,
            "post_tool_schema_sha256": "b" * 64,
            "pre_tool_schema_sha256": "b" * 64,
        })
        self.assertEqual("DRIFTED", drifted["stability"])


class EventJobCheckpointTests(unittest.TestCase):
    def test_exact_event_mapping_and_three_proof_budget_gate(self):
        module = contract_module()
        self.assertEqual("FEATURE_DONE", module.map_worker_event("SUCCESS"))
        self.assertEqual(
            "FEATURE_DONE", module.map_worker_event("SUCCESS_CANDIDATE")
        )
        for outcome in ("HARD_EXTERNAL", "OWNER_CONFLICT", "STOP_EXHAUSTED", "CACHE_DRIFT_UNRESOLVED"):
            self.assertEqual("OWNER_DECISION_REQUIRED", module.map_worker_event(outcome))
        self.assertEqual(
            "HARD_BLOCKER_AFTER_3_PROOFS",
            module.map_worker_event("VERIFIED_FAILURE", failed_verified_approaches=3, budget_remaining=True),
        )
        self.assertEqual(
            "OWNER_DECISION_REQUIRED",
            module.map_worker_event("VERIFIED_FAILURE", failed_verified_approaches=3, budget_remaining=False),
        )
        self.assertIsNone(module.map_worker_event("SOFT_LOCAL"))

    def test_autonomy_uses_two_distinct_bound_approaches_without_rewriting_legacy(self):
        module = contract_module()
        def approach(identifier: str, route: str) -> dict[str, object]:
            unsigned = {
                "action_class": "implementation", "approach_id": identifier,
                "evidence_path": f"proof/{identifier}.json", "evidence_sha256": identifier[0] * 64,
                "failure_code": "LOCAL_FAILURE", "hypothesis": "bounded hypothesis",
                "next_route": "different route", "progress": False, "route": route,
                "schema": module.APPROACH_RECEIPT_SCHEMA,
                "source_hashes": {"src/feature.py": "a" * 64},
            }
            return {**unsigned, "approach_sha256": module.sha256_bytes(module.canonical_json_bytes(unsigned))}
        approaches = [approach("a", "route-one"), approach("b", "route-two")]
        self.assertEqual(
            "HARD_BLOCKER_AFTER_2_PROOFS",
            module.map_worker_event(
                "VERIFIED_FAILURE", failed_verified_approaches=2,
                approach_receipts=module.validate_approach_receipts(approaches),
            ),
        )
        self.assertEqual("EXECUTE_NOW", module.classify_autonomy_action(
            local=True, reversible=True, in_scope=True, external_effect=False,
            destructive=False, owner_boundary=False,
        ))
        self.assertEqual("OWNER_ACTION", module.classify_autonomy_action(
            local=True, reversible=True, in_scope=True, external_effect=True,
            destructive=False, owner_boundary=False,
        ))
        self.assertEqual(
            1, len(module.validate_approach_receipts([approaches[0], approaches[0]]))
        )

    def test_question_admission_keeps_routine_questions_local(self):
        module = contract_module()
        base = {
            "architecture_security_boundary": False,
            "distinct_failed_approaches": 0,
            "owner_boundary": False,
            "schema": module.QUESTION_ADMISSION_SCHEMA,
            "single_route_failed": False,
            "stable_material_diff": False,
            "subagent_available": False,
        }
        self.assertEqual("CONTINUE_LOCAL", module.classify_question_admission(None))
        self.assertEqual("CONTINUE_LOCAL", module.classify_question_admission({}))
        self.assertEqual("CONTINUE_LOCAL", module.classify_question_admission(base))
        self.assertEqual(
            "LOCAL_FALLBACK",
            module.classify_question_admission({**base, "single_route_failed": True}),
        )
        self.assertEqual(
            "SUBAGENT_ONCE",
            module.classify_question_admission({
                **base, "single_route_failed": True, "subagent_available": True,
            }),
        )
        self.assertEqual(
            "THINKER_ALLOWED",
            module.classify_question_admission({
                **base, "stable_material_diff": True,
            }),
        )
        self.assertEqual(
            "THINKER_ALLOWED",
            module.classify_question_admission({
                **base, "distinct_failed_approaches": 2,
            }),
        )
        self.assertEqual(
            "OWNER_REQUIRED",
            module.classify_question_admission({**base, "owner_boundary": True}),
        )

    def test_disabled_monitor_keeps_core_ready_without_scheduler(self):
        module = contract_module()
        approved = {
            "jobs": [],
            "monitor_mode": "DISABLED",
            "schema": "x9-loop-approved-jobs-v1",
        }
        observed = [{
            "command_hash": "c" * 64,
            "job_id": "job-1",
            "provider": "windows-task-scheduler",
            "relevance": "CURRENT_PROJECT_MONITOR",
            "schedule_hash": "d" * 64,
        }]
        before = json.dumps(observed, sort_keys=True)
        result = module.compare_scheduled_jobs(
            approved, observed, {"windows-task-scheduler": "UNKNOWN"}
        )
        self.assertTrue(result["activation_allowed"])
        self.assertTrue(result["core_loop_ready"])
        self.assertIsNone(result["external_wake_ready"])
        self.assertEqual("NEW_JOB", result["job_findings"][0]["status"])
        self.assertEqual([], result["unavailable_providers"])
        self.assertEqual(before, json.dumps(observed, sort_keys=True))
        self.assertNotIn("command", json.dumps(result))
        for provider in (
            "windows-task-scheduler",
            "platform:linux-systemd",
            "platform:macos-launchd",
        ):
            with self.subTest(provider=provider):
                absent = module.compare_scheduled_jobs(
                    approved, [], {provider: "UNKNOWN"}
                )
                self.assertTrue(absent["core_loop_ready"])
                self.assertIsNone(absent["external_wake_ready"])
                self.assertEqual([], absent["unavailable_providers"])

    def test_external_monitor_is_project_bound_and_preserves_drift_reasons(self):
        module = contract_module()
        profile = "profile-1234567890abcdef"
        approved_row = {
            "command_hash": "a" * 64,
            "job_id": "job-1",
            "provider": "windows-task-scheduler",
            "schedule_hash": "b" * 64,
        }
        external = {
            "jobs": [approved_row],
            "monitor_mode": "EXTERNAL",
            "project_profile_id": profile,
            "schema": "x9-loop-approved-jobs-v1",
        }
        exact = module.compare_scheduled_jobs(
            external,
            [
                {**approved_row, "relevance": "CURRENT_PROJECT_MONITOR"},
                {
                    **approved_row,
                    "job_id": "other-project-job",
                    "relevance": "OTHER_PROJECT_JOB",
                },
            ],
            {"windows-task-scheduler": "AVAILABLE"},
            project_profile_id=profile,
        )
        self.assertTrue(exact["core_loop_ready"])
        self.assertTrue(exact["external_wake_ready"])
        self.assertEqual("OTHER_PROJECT_JOB", exact["job_findings"][0]["status"])
        drift = module.compare_scheduled_jobs(
            external,
            [{
                **approved_row,
                "command_hash": "c" * 64,
                "schedule_hash": "d" * 64,
                "relevance": "CURRENT_PROJECT_MONITOR",
            }],
            {"windows-task-scheduler": "AVAILABLE"},
            project_profile_id=profile,
        )
        self.assertTrue(drift["core_loop_ready"])
        self.assertFalse(drift["external_wake_ready"])
        self.assertEqual(
            ["COMMAND_DRIFT", "SCHEDULE_DRIFT"],
            [row["status"] for row in drift["job_findings"]],
        )
        unapproved = module.compare_scheduled_jobs(
            external,
            [
                {**approved_row, "relevance": "CURRENT_PROJECT_MONITOR"},
                {
                    **approved_row,
                    "job_id": "unapproved-current-project",
                    "relevance": "CURRENT_PROJECT_MONITOR",
                },
            ],
            {"windows-task-scheduler": "AVAILABLE"},
            project_profile_id=profile,
        )
        self.assertFalse(unapproved["external_wake_ready"])
        self.assertEqual("NEW_JOB", unapproved["unauthorized_jobs"][0]["status"])

    def test_checkpoint_is_local_non_authoritative_expires_and_rejects_tamper(self):
        module = contract_module()
        checkpoint, raw, digest = module.build_worker_checkpoint(
            attempt=1,
            proof_refs=[],
            state="TESTING",
            worker_id="worker-1",
            work_order_id="wo-1",
            work_order_sha256="c" * 64,
        )
        self.assertFalse(checkpoint["authoritative"])
        self.assertTrue(checkpoint["local_only"])
        module.validate_worker_checkpoint(raw, digest, "wo-1", "c" * 64, "worker-1", True)
        with self.assertRaises(module.ContractError) as caught:
            module.validate_worker_checkpoint(raw + b" ", digest, "wo-1", "c" * 64, "worker-1", True)
        self.assertEqual("CHECKPOINT_TAMPERED", caught.exception.code)
        with self.assertRaises(module.ContractError) as caught:
            module.validate_worker_checkpoint(raw, digest, "wo-1", "c" * 64, "worker-1", False)
        self.assertEqual("CHECKPOINT_EXPIRED", caught.exception.code)

    def test_result_requires_compact_change_map(self):
        module = contract_module()
        change_map = {
            "changed_surface": ["scripts/v7_contract.py"],
            "proof_refs": ["tests/test_v7_contract.py"],
            "reason": "enforce V7",
            "remaining_risk": "live provider inventory",
            "rollback": "restore V6 recovery set",
        }
        module.validate_change_map(change_map)
        change_map.pop("rollback")
        with self.assertRaises(module.ContractError) as caught:
            module.validate_change_map(change_map)
        self.assertEqual("RESULT_CHANGE_MAP_INCOMPLETE:rollback", caught.exception.code)


class ContractChallengeTests(unittest.TestCase):
    def build_order(self, features=None, program_sha="e" * 64):
        module = contract_module()
        return module.build_work_order(
            action_class="worker-implementation",
            created_at="2026-07-14T00:00:00Z",
            features=features or [feature_assignment()],
            program_packet_ref={
                "path": ".devad/manager/loop-lite/PROGRAM_PACKET.json",
                "sha256": program_sha,
            },
            source_git_sha="a" * 40,
            source_root_sha256="d" * 64,
            stop=stop_contract(),
            task_id="task-1",
            work_order_id="wo-1",
        )

    def test_canonical_json_rejects_non_string_keys(self):
        module = contract_module()
        with self.assertRaises(module.ContractError) as caught:
            module.canonical_json_bytes({1.5: "forbidden"})
        self.assertEqual("CANONICAL_KEY_INVALID", caught.exception.code)

    def test_work_order_rejects_unsafe_refs_bad_hashes_and_non_controller_authority(self):
        module = contract_module()
        unsafe = feature_assignment()
        unsafe["path"] = "../escape/FEATURE_PACKET.json"
        with self.assertRaises(module.ContractError):
            self.build_order([unsafe])
        with self.assertRaises(module.ContractError):
            self.build_order(program_sha="z" * 64)
        order, _, _ = self.build_order()
        order["writer"] = "Worker"
        raw = module.canonical_json_bytes(order)
        with self.assertRaises(module.ContractError) as caught:
            module.validate_work_order_identity(
                raw, module.sha256_bytes(raw), module.bound_work_order_context(order)
            )
        self.assertEqual("WORK_ORDER_AUTHORITY_INVALID", caught.exception.code)

    def test_two_feature_atomicity_includes_claims_and_resources(self):
        module = contract_module()
        second = feature_assignment("feature-b")
        second["claims"] = [{"path": "src/other.py", "kind": "file"}]
        with self.assertRaises(module.ContractError) as caught:
            self.build_order([feature_assignment(), second])
        self.assertEqual("TWO_FEATURE_NOT_ATOMIC", caught.exception.code)

    def test_drifted_receipt_and_unrecorded_action_class_transition_stop(self):
        module = contract_module()
        common = {
            "attempt": 0,
            "elapsed_seconds": 0,
            "model_calls": 0,
            "objective_satisfied": False,
            "prompt_prefix_sha256": "a" * 64,
            "stop": stop_contract(),
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        }
        drifted = {
            "action_class": "worker-implementation",
            "prompt_prefix_sha256": "a" * 64,
            "tool_schema_sha256": "b" * 64,
            "stability": "DRIFTED",
        }
        stopped = module.pre_model_call_gate(
            action_class="worker-implementation", prior_receipt=drifted, **common
        )
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("CACHE_PREFIX_CHANGED", stopped["event"])
        stable = dict(drifted, stability="STABLE")
        stopped = module.pre_model_call_gate(
            action_class="new-action-class", prior_receipt=stable, **common
        )
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("CACHE_PREFIX_CHANGED", stopped["event"])

    def test_stop_telemetry_must_be_nonnegative_and_boolean(self):
        module = contract_module()
        base = {
            "action_class": "worker-implementation",
            "attempt": 0,
            "elapsed_seconds": 0,
            "model_calls": 0,
            "objective_satisfied": False,
            "prior_receipt": None,
            "prompt_prefix_sha256": "a" * 64,
            "stop": stop_contract(),
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        }
        for field in ("attempt", "elapsed_seconds", "model_calls"):
            values = dict(base, **{field: -1})
            with self.subTest(field=field), self.assertRaises(module.ContractError):
                module.pre_model_call_gate(**values)
        with self.assertRaises(module.ContractError):
            module.pre_model_call_gate(**dict(base, objective_satisfied="yes"))

    def test_jobs_require_explicit_provider_access_and_redact_job_ids(self):
        module = contract_module()
        row = {
            "command_hash": "c" * 64,
            "job_id": "sk-secretvalue",
            "provider": "codex",
            "schedule_hash": "d" * 64,
        }
        profile = "profile-1234567890abcdef"
        approved = {
            "jobs": [row],
            "monitor_mode": "EXTERNAL",
            "project_profile_id": profile,
            "schema": "x9-loop-approved-jobs-v1",
        }
        observed = [{**row, "relevance": "CURRENT_PROJECT_MONITOR"}]
        missing = module.compare_scheduled_jobs(
            approved, observed, {}, project_profile_id=profile
        )
        self.assertTrue(missing["core_loop_ready"])
        self.assertFalse(missing["external_wake_ready"])
        self.assertEqual(["codex"], missing["unavailable_providers"])
        unexpected = module.compare_scheduled_jobs(
            {"jobs": [], "monitor_mode": "DISABLED", "schema": "x9-loop-approved-jobs-v1"},
            [{**row, "relevance": "OTHER_PROJECT_JOB"}],
            {"codex": "UNKNOWN"},
        )
        serialized = json.dumps(unexpected)
        self.assertNotIn("sk-secretvalue", serialized)
        self.assertNotIn('"job_id"', serialized)

    def test_proof_boundary_scope_pause_and_checkpoint_identity_are_fail_closed(self):
        module = contract_module()
        self.assertEqual(
            "HARD_BLOCKER_AFTER_3_PROOFS",
            module.map_worker_event(
                "VERIFIED_FAILURE", failed_verified_approaches=4, budget_remaining=True
            ),
        )
        self.assertEqual("TASK_SCOPE_PAUSED", module.map_worker_event("SCOPE_CONFLICT"))
        checkpoint, _, _ = module.build_worker_checkpoint(
            attempt=1,
            proof_refs=[],
            state="TESTING",
            worker_id="worker-1",
            work_order_id="wo-1",
            work_order_sha256="c" * 64,
        )
        checkpoint["schema"] = "wrong"
        checkpoint["expires_with_work_order"] = False
        checkpoint["worker_id"] = "attacker"
        checkpoint["proof_refs"] = ["x" * 20000]
        raw = module.canonical_json_bytes(checkpoint)
        with self.assertRaises(module.ContractError):
            module.validate_worker_checkpoint(
                raw, module.sha256_bytes(raw), "wo-1", "c" * 64, "worker-1", True
            )

class LiteInboxAndTransportContractTests(unittest.TestCase):
    PROFILE_ID = "profile-0123456789abcdef"

    def inbox_event(self, event_type: str = "WORKER_RESULT") -> dict[str, object]:
        role_by_type = {
            "THINX_RESULT": "THINKER",
            "TRANSPORT_ACK": "LINKER",
            "WORKER_RESULT": "WORKER",
        }
        return {
            "event_id": "evt-11111111-1111-4111-8111-111111111111",
            "event_type": event_type,
            "payload_ref": {
                "path": f"runtime/inbox/{event_type.lower()}.json",
                "sha256": "a" * 64,
            },
            "project_profile_id": self.PROFILE_ID,
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "worker-1",
            "source_role": role_by_type[event_type],
        }

    @staticmethod
    def transport_ack() -> dict[str, object]:
        return {
            "ack_id": "ack-22222222-2222-4222-8222-222222222222",
            "action": "SEND_WORK_ORDER",
            "action_id": "act-33333333-3333-4333-8333-333333333333",
            "action_sha256": "b" * 64,
            "dispatch_id": "dsp-44444444-4444-4444-8444-444444444444",
            "project_profile_id": "profile-0123456789abcdef",
            "schema": "x9-loop-transport-ack-v1",
            "status": "DELIVERED",
            "work_order_id": "wo-55555555-5555-4555-8555-555555555555",
            "work_order_sha256": "c" * 64,
            "worker_id": "worker-1",
        }

    @staticmethod
    def ack_identity(ack: dict[str, object]) -> dict[str, object]:
        return {
            key: ack[key]
            for key in (
                "action_id", "action_sha256", "dispatch_id",
                "project_profile_id", "work_order_id", "work_order_sha256",
                "worker_id",
            )
        }

    def validate_event(self, event: dict[str, object], digest: str | None = None):
        module = contract_module()
        raw = module.canonical_json_bytes(event)
        return module.validate_inbox_event(
            raw, digest or module.sha256_bytes(raw), self.PROFILE_ID
        )

    def test_inbox_event_accepts_only_typed_payload_references(self):
        for event_type in ("WORKER_RESULT", "THINX_RESULT", "TRANSPORT_ACK"):
            with self.subTest(event_type=event_type):
                event = self.inbox_event(event_type)
                self.assertEqual(event, self.validate_event(event))

        event = self.inbox_event()
        event["command"] = "powershell -encoded secret"
        with self.assertRaises(contract_module().ContractError) as caught:
            self.validate_event(event)
        self.assertEqual("INBOX_EVENT_FIELDS_INVALID", caught.exception.code)

        event = self.inbox_event()
        event["payload_ref"]["provider_payload"] = {"token": "secret"}
        with self.assertRaises(contract_module().ContractError) as caught:
            self.validate_event(event)
        self.assertEqual("INBOX_PAYLOAD_REF_INVALID", caught.exception.code)

    def test_deep_canonical_json_recursion_fails_closed(self):
        module = contract_module()
        deeply_nested = 0
        for _ in range(sys.getrecursionlimit() + 100):
            deeply_nested = [deeply_nested]

        with self.assertRaises(module.ContractError) as caught:
            module.canonical_json_bytes(deeply_nested)

        self.assertEqual(
            "CANONICAL_JSON_RECURSION", caught.exception.code
        )

    def test_inbox_event_rejects_tamper_cross_profile_float_and_oversize(self):
        module = contract_module()
        event = self.inbox_event()
        raw = module.canonical_json_bytes(event)
        digest = module.sha256_bytes(raw)
        with self.assertRaises(module.ContractError) as caught:
            self.validate_event(dict(event, source_actor_id="worker-2"), digest)
        self.assertEqual("INBOX_EVENT_HASH_MISMATCH", caught.exception.code)

        with self.assertRaises(module.ContractError) as caught:
            module.validate_inbox_event(raw, digest, "profile-other")
        self.assertEqual("INBOX_EVENT_PROFILE_MISMATCH", caught.exception.code)

        wrong_role = dict(event, source_role="LINKER")
        with self.assertRaises(module.ContractError) as caught:
            self.validate_event(wrong_role)
        self.assertEqual("INBOX_EVENT_ROLE_MISMATCH", caught.exception.code)

        noncanonical_raw = json.dumps(event, indent=2).encode("utf-8") + b"\n"
        with self.assertRaises(module.ContractError) as caught:
            module.validate_inbox_event(
                noncanonical_raw,
                module.sha256_bytes(noncanonical_raw),
                self.PROFILE_ID,
            )
        self.assertEqual("INBOX_EVENT_BYTES_NONCANONICAL", caught.exception.code)

        nonfinite_raw = raw.replace(
            b'"source_actor_id":"worker-1"', b'"source_actor_id":NaN'
        )
        with self.assertRaises(module.ContractError) as caught:
            module.validate_inbox_event(
                nonfinite_raw, module.sha256_bytes(nonfinite_raw), self.PROFILE_ID
            )
        self.assertEqual("CANONICAL_FLOAT_FORBIDDEN", caught.exception.code)

        floating_raw = raw.replace(b'"source_actor_id":"worker-1"', b'"source_actor_id":1.5')
        with self.assertRaises(module.ContractError) as caught:
            module.validate_inbox_event(
                floating_raw, module.sha256_bytes(floating_raw), self.PROFILE_ID
            )
        self.assertEqual("CANONICAL_FLOAT_FORBIDDEN", caught.exception.code)

        oversized = dict(event, source_actor_id="w" * 5000)
        oversized_raw = module.canonical_json_bytes(oversized)
        with self.assertRaises(module.ContractError) as caught:
            module.validate_inbox_event(
                oversized_raw, module.sha256_bytes(oversized_raw), self.PROFILE_ID
            )
        self.assertEqual("PACKET_CAP_EXCEEDED:INBOX_EVENT.json", caught.exception.code)

    def test_transport_ack_binds_exact_action_order_dispatch_worker_and_profile(self):
        module = contract_module()
        ack = self.transport_ack()
        expected = self.ack_identity(ack)
        raw = module.canonical_json_bytes(ack)
        self.assertEqual(
            ack,
            module.validate_transport_ack(raw, module.sha256_bytes(raw), expected),
        )
        for field in expected:
            with self.subTest(field=field):
                wrong = dict(expected)
                wrong[field] = "d" * 64 if field.endswith("sha256") else f"wrong-{field}"
                with self.assertRaises(module.ContractError) as caught:
                    module.validate_transport_ack(raw, module.sha256_bytes(raw), wrong)
                self.assertEqual(
                    f"TRANSPORT_ACK_IDENTITY_MISMATCH:{field}", caught.exception.code
                )

    def test_transport_ack_rejects_unknown_tamper_float_and_oversize(self):
        module = contract_module()
        ack = self.transport_ack()
        expected = self.ack_identity(ack)
        raw = module.canonical_json_bytes(ack)
        digest = module.sha256_bytes(raw)

        unknown = dict(ack, provider_payload={"key": "secret"})
        unknown_raw = module.canonical_json_bytes(unknown)
        with self.assertRaises(module.ContractError) as caught:
            module.validate_transport_ack(
                unknown_raw, module.sha256_bytes(unknown_raw), expected
            )
        self.assertEqual("TRANSPORT_ACK_FIELDS_INVALID", caught.exception.code)

        with self.assertRaises(module.ContractError) as caught:
            module.validate_transport_ack(
                module.canonical_json_bytes(dict(ack, status="FAILED")), digest, expected
            )
        self.assertEqual("TRANSPORT_ACK_HASH_MISMATCH", caught.exception.code)

        floating_raw = raw.replace(b'"status":"DELIVERED"', b'"status":1.5')
        with self.assertRaises(module.ContractError) as caught:
            module.validate_transport_ack(
                floating_raw, module.sha256_bytes(floating_raw), expected
            )
        self.assertEqual("CANONICAL_FLOAT_FORBIDDEN", caught.exception.code)

        oversized = dict(ack, ack_id="a" * 5000)
        oversized_raw = module.canonical_json_bytes(oversized)
        with self.assertRaises(module.ContractError) as caught:
            module.validate_transport_ack(
                oversized_raw, module.sha256_bytes(oversized_raw), expected
            )
        self.assertEqual(
            "PACKET_CAP_EXCEEDED:TRANSPORT_ACK.json", caught.exception.code
        )


class ProjectBrainContractExtensionTests(unittest.TestCase):
    def test_context_capsule_reference_is_bounded_and_path_safe(self):
        module = contract_module()
        feature = complete_feature()
        feature["context_capsule_ref"] = {
            "bytes": 128,
            "capsule_id": "ctx-feature-a",
            "path": ".devad/features/feature-a/runs/run-1/CONTEXT_CAPSULE.json",
            "sha256": "a" * 64,
        }
        module.validate_context_complete(feature)
        feature["context_capsule_ref"]["path"] = "../outside.json"
        with self.assertRaises(module.ContractError):
            module.validate_context_complete(feature)

    def test_call_receipt_accepts_only_bounded_failure_projection(self):
        module = contract_module()
        failure = {
            "class": "PRODUCT",
            "code": "PROJECT_MEMORY_CIRCUIT_OPEN",
            "signature": "a" * 64,
            "progress": False,
        }
        receipt = module.build_call_receipt(
            action_class="worker-implementation",
            attempt=1,
            call_id="call-failure",
            compaction_generation=0,
            sequence=1,
            post_prompt_prefix_sha256="a" * 64,
            post_tool_schema_sha256="b" * 64,
            pre_prompt_prefix_sha256="a" * 64,
            pre_tool_schema_sha256="b" * 64,
            token_usage="Unknown",
            work_order_sha256="c" * 64,
            failure=failure,
        )
        self.assertEqual(failure, receipt["failure"])
        module.validate_call_receipt(receipt)
        invalid = dict(receipt)
        invalid["failure"] = {**failure, "raw_command": "forbidden"}
        with self.assertRaises(module.ContractError):
            module.validate_call_receipt(invalid)

if __name__ == "__main__":
    unittest.main()
