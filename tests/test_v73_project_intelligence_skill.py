from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "devad-x9-loop" / "SKILL.md"
REFERENCE = (
    ROOT
    / "skills"
    / "devad-x9-loop"
    / "references"
    / "project-intelligence-v1.md"
)


class ProjectIntelligenceSkillContractTests(unittest.TestCase):
    def test_skill_requires_context_capsule_before_work_order_and_dispatch(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("## Required Project Intelligence Gate", text)
        self.assertIn("references/project-intelligence-v1.md", text)
        self.assertIn("CONTEXT_CAPSULE.json", text)
        self.assertIn("before Work Order creation", text)
        self.assertIn("again before dispatch", text)

    def test_reference_requires_source_backed_coverage_and_advisory_memory(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")

        for relation in (
            "UI control",
            "request/API field",
            "server authority",
            "persistence/default/migration",
            "entitlement",
            "runtime consumer",
            "regression test",
        ):
            self.assertIn(relation, text)

        self.assertIn("advisory", text.lower())
        self.assertIn("cannot satisfy a required relation", text)
        self.assertIn("file_sha256", text)
        self.assertIn("span_sha256", text)

    def test_reference_fails_closed_on_duplicate_stale_or_missing_context(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")

        for code in (
            "CONTEXT_AUTHORITY_DUPLICATE",
            "CONTEXT_AUTHORITY_CONFLICT",
            "CONTEXT_SOURCE_DRIFT",
            "CONTEXT_SPAN_DRIFT",
            "CONTEXT_ADVISORY_ONLY",
            "CONTEXT_COVERAGE_MISSING",
            "CONTEXT_CAPSULE_DRIFT",
        ):
            self.assertIn(code, text)

    def test_reference_keeps_controller_and_memory_authorities_separate(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")

        self.assertIn("never creates, dispatches, acknowledges, or completes", text)
        self.assertIn("16 KB", text)
        self.assertIn("64 KB", text)
        self.assertIn("re-read exact current repository bytes", text)


if __name__ == "__main__":
    unittest.main()
