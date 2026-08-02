from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "x9-project-docs" / "SKILL.md"
CONTRACT = ROOT / "skills" / "x9-project-docs" / "references" / "project-docs-contract.md"


def load_brain():
    path = ROOT / "skills" / "devad-x9-loop" / "scripts" / "project_brain.py"
    spec = importlib.util.spec_from_file_location("project_brain_docs_tests", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("project brain loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def accepted_result() -> dict[str, object]:
    digest = "a" * 64
    proof = [
        {"kind": "security", "path": ".devad/workers/worker-docs-1/proof/evt-docs-1/security.json", "sha256": digest},
        {"kind": "tests", "path": ".devad/workers/worker-docs-1/proof/evt-docs-1/tests.json", "sha256": digest},
    ]
    return {
        "attestation_path": None,
        "blocker": None,
        "budget_remaining": True,
        "c1": None,
        "c2": None,
        "change_map": {
            "changed_surface": [],
            "proof_refs": [item["path"] for item in proof],
            "reason": "accepted fixture",
            "remaining_risk": "none",
            "rollback": "restore fixture",
        },
        "changed_files": [],
        "dispatch_id": "dsp-docs-1",
        "event_id": "evt-docs-1",
        "failed_verified_approaches": 0,
        "outcome": "SUCCESS",
        "packet_sha256": digest,
        "proof": proof,
        "role": "WORKER",
        "schema": "x9-loop-result-v2",
        "task_id": "task-docs-1",
        "work_order_id": "wo-docs-1",
        "work_order_sha256": digest,
        "worker_id": "worker-docs-1",
    }

def accepted_binding(brain, result: dict[str, object], feature_id: str, repo: Path) -> dict[str, object]:
    proof_payloads = {
        "security": b'{"proof_schema":"x9-loop-proof-v2","kind":"security"}' + b"\n",
        "tests": b'{"proof_schema":"x9-loop-proof-v2","kind":"tests"}' + b"\n",
    }
    for item in result["proof"]:
        payload = proof_payloads[item["kind"]]
        path = repo / item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        item["sha256"] = brain.sha256_bytes(payload)
    plan_path = repo / ".devad" / "fixtures" / (feature_id + "-PLAN.md")
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_bytes(b"accepted plan fixture\n")
    plan_sha = brain.sha256_bytes(plan_path.read_bytes())
    feature_path = repo / ".devad" / "fixtures" / (feature_id + "-FEATURE_PACKET.json")
    base_sha = "e" * 40
    feature_path.write_bytes(brain.canonical_json_bytes({"feature_id": feature_id, "plan_sha256": plan_sha, "base_sha": base_sha}))
    feature_sha = brain.sha256_bytes(feature_path.read_bytes())
    result["packet_sha256"] = feature_sha
    work_order_path = repo / ".devad" / "fixtures" / (feature_id + "-WORK_ORDER.json")
    work_order_path.write_bytes(brain.canonical_json_bytes({"work_order_id": result["work_order_id"], "task_id": result["task_id"], "worker_id": result["worker_id"], "base_sha": base_sha, "feature_id": feature_id, "plan_sha256": plan_sha, "feature_packet_refs": [{"feature_id": feature_id, "sha256": feature_sha}]}))
    work_order_sha = brain.sha256_bytes(work_order_path.read_bytes())
    result["work_order_sha256"] = work_order_sha
    dispatch_path = repo / ".devad" / "fixtures" / (feature_id + "-DISPATCH.json")
    dispatch_path.write_bytes(brain.canonical_json_bytes({"dispatch_id": result["dispatch_id"], "event_id": result["event_id"], "worker_id": result["worker_id"]}))
    source_manifest_path = repo / "SOURCE_MANIFEST.sha256"
    source_manifest_path.write_bytes(b"fixture source manifest\n")
    result_path = repo / ".devad" / "fixtures" / (feature_id + "-RESULT.json")
    result_path.write_bytes(brain.canonical_json_bytes(result))
    subprocess.run(["git", "-C", str(repo), "init", "--quiet"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "fixture@example.invalid"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "X9 Fixture"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "--allow-empty", "-m", "fixture"], check=True, capture_output=True)
    current_sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    refs = {
        "feature_packet": {"path": feature_path.relative_to(repo).as_posix(), "sha256": feature_sha},
        "plan": {"path": plan_path.relative_to(repo).as_posix(), "sha256": plan_sha},
        "work_order": {"path": work_order_path.relative_to(repo).as_posix(), "sha256": work_order_sha},
        "dispatch": {"path": dispatch_path.relative_to(repo).as_posix(), "sha256": brain.sha256_bytes(dispatch_path.read_bytes())},
        "result": {"path": result_path.relative_to(repo).as_posix(), "sha256": brain.sha256_bytes(result_path.read_bytes())},
        "source_manifest": {"path": source_manifest_path.relative_to(repo).as_posix(), "sha256": brain.sha256_bytes(source_manifest_path.read_bytes())},
    }
    return {
        "feature_id": feature_id,
        "feature_packet_sha256": result["packet_sha256"],
        "plan_sha256": plan_sha,
        "task_id": result["task_id"],
        "work_order_id": result["work_order_id"],
        "work_order_sha256": result["work_order_sha256"],
        "dispatch_id": result["dispatch_id"],
        "event_id": result["event_id"],
        "worker_id": result["worker_id"],
        "profile_id": "profile:fixture",
        "base_sha": base_sha,
        "current_sha": current_sha,
        "result_sha256": brain.sha256_json(result),
        "source_manifest_sha256": refs["source_manifest"]["sha256"],
        "proof": result["proof"],
        "changed_files": result["changed_files"],
        "attestation_path": result["attestation_path"],
        "c2_sha256": None,
        "unknown_items": [],
        "rollback": "restore fixture",
        "canonical_refs": refs,
    }


def style_receipt(brain, feature_id: str, repo: Path) -> dict[str, object]:
    plan_path = repo / ".devad" / "features" / feature_id / "plans" / "PLAN.md"
    source_path = repo / "src" / "owner.py"
    proof_path = repo / ".devad" / "features" / feature_id / "artifacts" / "tests.json"
    for path, payload in (
        (plan_path, b"style plan fixture\n"),
        (source_path, b"def current_owner():\n    return 'reuse'\n"),
        (proof_path, b'{"proof_schema":"x9-loop-proof-v2","kind":"tests"}\n'),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    subprocess.run(["git", "-C", str(repo), "init", "--quiet"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "fixture@example.invalid"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "X9 Fixture"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "-m", "fixture"], check=True, capture_output=True)
    current_sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    source = source_path.read_bytes()
    return {
        "schema": "x9-loop-style-result-v1",
        "outcome": "SUCCESS",
        "feature_id": feature_id,
        "profile_id": "profile:style-fixture",
        "base_sha": "f" * 40,
        "current_sha": current_sha,
        "plan_ref": {"path": plan_path.relative_to(repo).as_posix(), "sha256": brain.sha256_bytes(plan_path.read_bytes())},
        "source_refs": [{
            "ref_id": "owner-source", "path": source_path.relative_to(repo).as_posix(),
            "file_sha256": brain.sha256_bytes(source), "byte_start": 0,
            "byte_end": len(source), "span_sha256": brain.sha256_bytes(source),
        }],
        "proof": [{"kind": "tests", "path": proof_path.relative_to(repo).as_posix(), "sha256": brain.sha256_bytes(proof_path.read_bytes())}],
        "changed_files": ["src/owner.py"],
        "unknown_items": [],
        "rollback": "restore fixture",
    }

class ProjectDocsSkillTests(unittest.TestCase):
    def test_package_contract_is_profile_local_and_evidence_bound(self):
        skill = SKILL.read_text(encoding="utf-8")
        contract = CONTRACT.read_text(encoding="utf-8")
        for text in (skill, contract):
            self.assertIn("TASK.md", text)
            self.assertIn("FEATURE.json", text)
            self.assertIn("MANIFEST.sha256", text)
            self.assertIn("VERIFIED", text)
            self.assertIn("profile-", text)
            self.assertIn("idempotent", text.lower())
        self.assertLessEqual(len(skill.splitlines()), 300)
        self.assertTrue((SKILL.parent / "agents" / "openai.yaml").is_file())
        self.assertIn("x9-loop-style-result-v1", skill + contract)

    def test_accepted_result_generation_has_direct_links_and_zero_delta_replay(self):
        brain = load_brain()
        with tempfile.TemporaryDirectory(prefix="x9-project-docs-") as directory:
            repo = Path(directory)
            result = accepted_result()
            binding = accepted_binding(brain, result, "fixture-feature", repo)
            first = brain.generate_feature_docs(repo, "fixture-feature", result, profile_id="profile:fixture", binding=binding)
            second = brain.generate_feature_docs(repo, "fixture-feature", result, profile_id="profile:fixture", binding=binding)
            self.assertEqual(first, second)
            with self.assertRaises(brain.ProjectBrainError) as missing_binding:
                brain.generate_feature_docs(repo, "fixture-feature-missing-binding", result)
            self.assertEqual("PROJECT_DOCS_BINDING_REQUIRED", missing_binding.exception.code)
            custom_result = accepted_result()
            custom_binding = accepted_binding(brain, custom_result, "fixture-feature-custom-output", repo)
            with self.assertRaises(brain.ProjectBrainError) as custom_output:
                brain.generate_feature_docs(repo, "fixture-feature-custom-output", custom_result, profile_id="profile:fixture", binding=custom_binding, output_root=repo / "outside")
            self.assertEqual("PROJECT_DOCS_OUTPUT_ROOT_FORBIDDEN", custom_output.exception.code)
            bad_binding = dict(binding)
            bad_binding["plan_sha256"] = "f" * 64
            with self.assertRaises(brain.ProjectBrainError) as identity_drift:
                brain.generate_feature_docs(repo, "fixture-feature", result, profile_id="profile:fixture", binding=bad_binding)
            self.assertEqual("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT", identity_drift.exception.code)
            plan_path = repo / binding["canonical_refs"]["plan"]["path"]
            plan_path.write_bytes(b"changed plan fixture\n")
            with self.assertRaises(brain.ProjectBrainError) as artifact_drift:
                brain.generate_feature_docs(repo, "fixture-feature", result, profile_id="profile:fixture", binding=binding)
            self.assertEqual("PROJECT_DOCS_BINDING_ARTIFACT_DRIFT", artifact_drift.exception.code)
            packet = repo / ".devad" / "features" / "fixture-feature"
            self.assertEqual("PASS", brain.validate_sitemap(packet / "TASK.md", manifest_path=packet / "MANIFEST.sha256")["status"])

    def test_unaccepted_result_cannot_create_docs(self):
        brain = load_brain()
        with tempfile.TemporaryDirectory(prefix="x9-project-docs-reject-") as directory:
            with self.assertRaises(brain.ProjectBrainError) as failure:
                brain.generate_feature_docs(Path(directory), "fixture-feature", {"status": "WAIT"})
            self.assertEqual("PROJECT_DOCS_RESULT_NOT_ACCEPTED", failure.exception.code)

    def test_style_receipt_generation_is_bound_and_idempotent(self):
        brain = load_brain()
        with tempfile.TemporaryDirectory(prefix="x9-style-project-docs-") as directory:
            repo = Path(directory)
            receipt = style_receipt(brain, "style-feature", repo)
            first = brain.generate_style_feature_docs(repo, "style-feature", receipt, profile_id="profile:style-fixture")
            second = brain.generate_style_feature_docs(repo, "style-feature", receipt, profile_id="profile:style-fixture")
            self.assertEqual(first, second)
            self.assertEqual("STYLE_ONLY", first["mode"])
            packet = repo / ".devad" / "features" / "style-feature"
            feature = (packet / "FEATURE.json").read_text(encoding="utf-8")
            self.assertIn("STYLE_ONLY", feature)
            self.assertEqual("PASS", brain.validate_sitemap(packet / "TASK.md", manifest_path=packet / "MANIFEST.sha256")["status"])
            bad_outcome = dict(receipt)
            bad_outcome["outcome"] = "FAIL"
            with self.assertRaises(brain.ProjectBrainError) as unaccepted:
                brain.generate_style_feature_docs(repo, "style-feature-fail", bad_outcome)
            self.assertEqual("PROJECT_STYLE_DOCS_RECEIPT_NOT_ACCEPTED", unaccepted.exception.code)
            bad_sha = dict(receipt)
            bad_sha["current_sha"] = "0" * 40
            with self.assertRaises(brain.ProjectBrainError) as stale_head:
                brain.generate_style_feature_docs(repo, "style-feature", bad_sha)
            self.assertEqual("PROJECT_STYLE_DOCS_RECEIPT_DRIFT", stale_head.exception.code)
            source_path = repo / "src" / "owner.py"
            source_path.write_bytes(b"def current_owner():\n    return 'drift'\n")
            with self.assertRaises(brain.ProjectBrainError) as stale_source:
                brain.generate_style_feature_docs(repo, "style-feature", receipt)
            self.assertEqual("PROJECT_SOURCE_FILE_DRIFT", stale_source.exception.code)


if __name__ == "__main__":
    unittest.main()
