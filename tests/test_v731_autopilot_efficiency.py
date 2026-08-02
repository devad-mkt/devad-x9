from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "devad-x9-loop" / "SKILL.md"
POLICY = ROOT / "skills" / "devad-x9-loop" / "references" / "autopilot-install-intent.md"
MODEL_POLICY = ROOT / "skills" / "devad-x9-loop" / "references" / "model-policy.md"
CALLBACK = ROOT / "skills" / "devad-x9-loop" / "references" / "direct-event-callback.md"
ENROLLMENT = ROOT / "skills" / "devad-x9-loop" / "references" / "manual-task-enrollment.md"
LESSON = ROOT / ".devad" / "features" / "x9-loop-v7-3" / "live-lessons" / "LESSON-48-AUTOPILOT-EFFICIENCY.md"


class AutopilotEfficiencyPolicyTests(unittest.TestCase):
    def test_skill_links_complete_intent_and_completion_policy(self):
        skill = SKILL.read_text(encoding="utf-8")
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("references/autopilot-install-intent.md", skill)
        for label in (
            "STYLE_ONLY", "SKILL_ONLY", "FULL_PROJECT_LOOP", "VERIFY_ONLY",
            "STYLE_APPLIED", "SKILLS_VERIFIED_EXISTING", "SKILLS_INSTALLED",
            "LOOP_PROFILE_INITIALIZED", "LOOP_ACTIVATED",
        ):
            self.assertIn(label, policy)
        self.assertIn("not a universal or community default", policy)
        self.assertIn("external_wake_ready=false", policy)
        self.assertIn("do not call THINKER", policy)
        self.assertIn("CORE_LOOP_READY", policy)
        self.assertIn("EXTERNAL_WAKE_READY", policy)

    def test_policy_orders_gates_quiets_progress_and_separates_model_surfaces(self):
        policy = POLICY.read_text(encoding="utf-8")
        gate_markers = [
            "Bind source, intent, scope", "Check links, paths, diff",
            "Run focused regressions", "Run package validation",
            "Run the full suite once", "Request one review",
            "Create unchanged reviewed C1", "Run temporary-install",
        ]
        positions = [policy.index(marker) for marker in gate_markers]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("A background test or wait consumes no model narration", policy)
        self.assertIn("visible task-creation tool's advertised model identifiers", policy)
        self.assertIn("packaged companion skills", policy)
        self.assertIn("does not make them", policy)
        self.assertIn("internal subagents", MODEL_POLICY.read_text(encoding="utf-8"))

    def test_lesson_48_has_required_durable_fields_and_exact_task_ids(self):
        lesson = LESSON.read_text(encoding="utf-8")
        for field in (
            "Trigger", "Violated invariants", "Root cause", "Minimal reproducer",
            "Corrections", "Regressions", "Rollback", "Token telemetry: `Unknown`",
            "Host-enforcement status",
        ):
            self.assertIn(field, lesson)
        ids = [
            "019f8626-2ae3-72c2-9fcc-d29fd3c4ee1a",
            "019f8606-886c-7a42-bfec-a8a684483a10",
        ]
        self.assertEqual(2, sum(lesson.count(task_id) for task_id in ids))

    def test_p0_callback_policy_is_signal_only_and_bounded(self):
        callback = CALLBACK.read_text(encoding="utf-8")
        for marker in (
            "return_to_task_id", "RESULT_READY", "LOOP_INCIDENT.json",
            "one deterministic idempotent", "no polling", "model",
            "thinking", "zero state delta",
        ):
            self.assertIn(marker, callback)
        enrollment = ENROLLMENT.read_text(encoding="utf-8")
        self.assertIn("Creation profiles", enrollment)
        self.assertIn("follow-up", enrollment)
        self.assertIn("MODEL_PROFILE_NOT_TOOL_ENFORCED", enrollment)

    def test_future_visible_names_are_short_and_identity_neutral(self):
        skill = SKILL.read_text(encoding="utf-8")
        enrollment = ENROLLMENT.read_text(encoding="utf-8")
        policy = f"{skill}\n{enrollment}"
        for label in ("Thinker", "Looper", "Linker", "Worker", "X9 Loop"):
            self.assertIn(label, policy)
            self.assertLessEqual(len(label.split()), 2)
        self.assertIn("one-or-two-word visible titles", enrollment)
        self.assertIn("stable task/thread ID", enrollment)
        self.assertIn("Follow-up messages continue to omit `model` and `thinking`", enrollment)


if __name__ == "__main__":
    unittest.main()
