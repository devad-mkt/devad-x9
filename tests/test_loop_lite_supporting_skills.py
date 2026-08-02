from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SupportingSkillV6Tests(unittest.TestCase):
    def read(self, skill: str, relative: str = "SKILL.md") -> str:
        return (SKILLS / skill / relative).read_text(encoding="utf-8-sig")

    def test_x9_worker_uses_loop_lite_and_terra_policy(self):
        text = self.read("devad-x9")
        self.assertIn("Devad X9 v6", text)
        self.assertIn("loop-lite/SNAPSHOT.json", text)
        self.assertIn("Terra high", text)
        self.assertIn("staged, unstaged, untracked, and committed", text)
        self.assertIn("SCOPE_BREACH", text)
        self.assertIn("C1", text)
        self.assertIn("C2", text)
        self.assertIn("security", text.lower())

    def test_style_is_default_and_shims_do_not_start_second_flow(self):
        style = self.read("x9-loop-style")
        code = self.read("x9-loop-code")
        loop = self.read("devad-x9-loop")
        text = self.read("devad-x9-manager")
        self.assertIn("v6", text)
        self.assertIn("x9-loop-style", text)
        self.assertIn("x9-loop-style", loop)
        self.assertIn("STYLE_ONLY", style)
        self.assertIn("experimental", code)
        self.assertIn("production-ready", code)
        self.assertIn("RESULT_READY", style)
        self.assertIn("Do **not** run `loopctl`", style)
        self.assertIn("Do not activate a Controller", loop)
        self.assertIn("Do not run a second manager flow", text)

    def test_validator_accepts_archived_v7_contract_with_style_redirect(self):
        path = ROOT / "scripts" / "validate_suite.py"
        spec = importlib.util.spec_from_file_location("x9_style_validator", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        errors: list[str] = []
        module.validate_skills(errors)
        self.assertEqual([], errors)

    def test_memory_names_loop_lite_as_active_and_v5_as_history(self):
        text = self.read("devad-memory")
        self.assertIn(".devad/manager/loop-lite/SNAPSHOT.json", text)
        self.assertIn(".devad/manager/loop/", text)
        self.assertIn("historical", text.lower())

    def test_workspace_policy_is_loop_optional_and_native_worktree_only(self):
        x9 = self.read("devad-x9")
        style = self.read("x9-loop-style")
        layout = self.read("devad-x9", "references/cdx9-workspace-layout.md")

        self.assertIn("That policy works without X9 Loop", x9)
        self.assertIn("require Controller bootstrap unless the owner", x9)
        self.assertIn("X9 Loop is optional orchestration", layout)
        self.assertIn("STYLE_ONLY", style)
        self.assertIn("quarantined", style)
        self.assertIn(r"D:\CDx9\0-cdx-wt", x9 + style + layout)
        self.assertIn("Do not create new loose scripts", layout)
        self.assertIn("unknown item stays in place", layout)

    def test_sticky_lane_policy_avoids_repeated_worktree_churn(self):
        x9 = self.read("devad-x9")
        style = self.read("x9-loop-style")
        autonomy = self.read(
            "devad-x9", "references/worker-autonomy-and-escalation.md"
        )
        combined = "\n".join((x9, style, autonomy))
        self.assertIn("Sticky Worker Lanes", x9)
        self.assertIn("sticky\n   lane", style)
        self.assertIn("REBIND_DUE", combined)
        self.assertIn("Remote-main movement alone", combined)
        self.assertIn("not a reason to stop, reattach, rebase, copy, or replace", style)
        self.assertIn("WAITING_CAPABILITY", autonomy)
        self.assertIn("same-project successor task", style)
        self.assertIn("replacement worktree or copy a", autonomy)
        self.assertIn("Canonical manager queue", autonomy)
        self.assertIn("one durable ordered checklist", style)

    def test_cached_plugin_worktree_override_is_hash_bound(self):
        policy = self.read(
            "devad-x9", "references/plugin-cache-durability.md"
        )
        patch_path = (
            SKILLS
            / "devad-x9"
            / "assets"
            / "superpowers-6.1.1-devad-worktree-override.patch"
        )
        patch = patch_path.read_bytes()

        self.assertIn("PLUGIN_CACHE_NON_DURABLE", policy)
        self.assertIn("replaceable installation bytes", policy)
        self.assertIn("7CCC3D2712BBBF7D02CCB974EEBCC30", policy)
        self.assertEqual(
            "7ccc3d2712bbbf7d02ccb974eebcc30b9dfb38aef37cef3f62ce1c66a9f388a7",
            hashlib.sha256(patch).hexdigest(),
        )
        self.assertIn(b"Do not use Step 1b", patch)
        self.assertIn(b"WORKSPACE_POLICY_CONFLICT", patch)

    def test_memory_routes_exact_tasks_and_preserves_evidence_states(self):
        text = self.read("devad-memory")
        self.assertIn("For an exact Codex task UUID", text)
        self.assertIn("One chat UUID maps to one canonical session", text)
        self.assertIn("Use explicit evidence states", text)
        self.assertIn("continuation-quality gate", text)
        self.assertIn("source-read boundary", text)

    def test_token_budget_uses_event_metrics_without_fallback_lifetime_totals(self):
        text = self.read("codex-token-budget")
        self.assertIn("X9 Loop Lite v6 Audit", text)
        self.assertIn("SNAPSHOT.json", text)
        self.assertIn("ACTION.json", text)
        self.assertIn("wall time", text.lower())
        self.assertIn("prompt bytes", text.lower())
        self.assertIn("first-pass success", text.lower())
        self.assertIn("fallback lifetime totals are forbidden", text.lower())
        self.assertIn("Unknown", text)
        self.assertNotIn("top thread lifetime/fallback totals", text.lower())

    def test_backup_and_installer_cover_all_packaged_skills(self):
        backup = self.read("codex-x9-backup")
        installer = (ROOT / "scripts" / "install-suite.ps1").read_text(
            encoding="utf-8-sig"
        )
        for name in (
            "devad-x9",
            "x9-loop-style",
            "x9-loop-code",
            "devad-x9-loop",
            "devad-x9-manager",
            "codex-x9-backup",
            "codex-token-budget",
            "devad-memory",
            "x9-project-docs",
            "dokploy",
            "devad-docs",
            "tldr",
            "smooth-coding",
            "sdlc",
            "xplan",
            "devad-adoptions",
        ):
            self.assertIn(name, backup + installer)
        self.assertIn("rollback", installer.lower())

    def test_workspace_outputs_are_role_neutral_and_bounded(self):
        x9 = self.read("devad-x9")
        layout = self.read("devad-x9", "references/cdx9-workspace-layout.md")
        docs = self.read("devad-docs")
        combined = "\n".join((x9, layout, docs))

        for marker in (
            r"docs\<subject>",
            r".devad\features\<feature>",
            "plans",
            "artifacts",
            "screenshots",
            "other",
            r".temp\<task-id-or-short-slug>",
            r"D:\CDx9\1-core-x9",
            "main task and every subagent",
            "Contabo S3",
            "S3 is backup",
        ):
            self.assertIn(marker, combined)
        self.assertIn(r"Never use `C:\tmp`", x9)
        self.assertIn("Do not use `.docs`", docs)

    def test_packaged_companion_skills_have_valid_entrypoints(self):
        for name in (
            "x9-loop-code",
            "dokploy",
            "devad-docs",
            "tldr",
            "smooth-coding",
            "sdlc",
            "xplan",
            "devad-adoptions",
        ):
            text = self.read(name)
            self.assertIn(f"name: {name}", text)

    def test_agent_prompts_default_to_style_and_quarantine_v7(self):
        style = self.read("x9-loop-style", "agents/openai.yaml")
        code = self.read("x9-loop-code", "agents/openai.yaml")
        loop = self.read("devad-x9-loop", "agents/openai.yaml")
        self.assertIn("$x9-loop-style", style)
        self.assertIn("without a Controller", style)
        self.assertIn("$x9-loop-style", loop)
        self.assertIn("fresh disposable", loop)
        self.assertIn("Trial", code)


    def test_backup_mirrors_reject_reparse_roots(self):
        for relative in (
            "scripts/restore-codex-x9-backup.ps1",
            "scripts/sync-codex-x9-backup.ps1",
        ):
            text = self.read("codex-x9-backup", relative)
            self.assertIn("Assert-NoReparsePath", text)
            self.assertIn("ReparsePoint", text)
            self.assertLess(text.index("Assert-NoReparsePath"), text.index("& robocopy"))

    def test_backup_secret_tools_skip_project_temp(self):
        for relative in (
            "scripts/secret-scan.py",
            "scripts/redact-secrets.py",
        ):
            text = self.read("codex-x9-backup", relative)
            self.assertIn('".temp"', text)

    def test_project_template_is_staged_before_atomic_install(self):
        installer = (ROOT / "scripts" / "install-suite.ps1").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("$ProjectStage", installer)
        self.assertIn("Move-Item -LiteralPath $ProjectStage -Destination $DevadTarget", installer)
        self.assertNotIn("Copy-Item -LiteralPath $Template -Destination $ProjectRoot", installer)


if __name__ == "__main__":
    unittest.main()
