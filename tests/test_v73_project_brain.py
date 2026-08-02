from __future__ import annotations

import importlib.util
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_BRAIN = ROOT / "skills" / "devad-x9-loop" / "scripts" / "project_brain.py"


def load_project_brain():
    name = "project_brain_v73_tests"
    spec = importlib.util.spec_from_file_location(name, PROJECT_BRAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PROJECT_BRAIN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
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

class ProjectBrainStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = load_project_brain()

    def test_profile_store_is_hashed_isolated_and_fts_backed(self):
        with tempfile.TemporaryDirectory(prefix="x9-brain-store-") as directory:
            repo = Path(directory)
            first = self.brain.ProjectMemory(repo, "profile:one")
            second = self.brain.ProjectMemory(repo, "profile:two")
            first.initialize()
            second.initialize()

            self.assertNotEqual(first.profile_root, second.profile_root)
            self.assertTrue(first.profile_root.name.startswith("profile-"))
            self.assertEqual("PASS", first.probe_fts5())
            with sqlite3.connect(first.database_path) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type IN ('table','shadow')"
                    )
                }
            connection.close()
            self.assertIn("facts_fts", tables)
            self.assertIn("decisions_fts", tables)
            self.assertIn("episodes_fts", tables)
            self.assertIn("document_titles_fts", tables)
            self.assertIn("documents", tables)
            first.put_fact(
                fact_id="fact-one",
                semantic_key="owner.example",
                value="first profile",
                source_ref_ids=[],
            )
            self.assertEqual([], second.search("first"))
            self.assertEqual("first profile", first.search("first")[0]["value"])
            first.put_decision(
                decision_id="decision-one",
                owner="controller",
                scope="project brain",
                status="APPROVED",
                evidence="exact plan",
            )
            first.put_document_title(
                document_id="doc-one",
                title="Project Brain Plan",
                path="docs/project-brain.md",
            )
            self.assertEqual("decision-one", first.search_decisions("controller")[0]["decision_id"])
            self.assertEqual("docs/project-brain.md", first.search_document_titles("brain")[0]["path"])
            first.put_episode(
                episode_id="episode-one",
                feature_id="feature-one",
                result_sha256="b" * 64,
                summary="accepted brain result",
                citations="receipt-one",
            )
            self.assertEqual("episode-one", first.search_episodes("accepted")[0]["episode_id"])
            with self.assertRaises(self.brain.ProjectBrainError) as immutable:
                first.put_fact(
                    fact_id="fact-one",
                    semantic_key="owner.example",
                    value="changed value",
                    source_ref_ids=[],
                )
            self.assertEqual("PROJECT_MEMORY_FACT_IMMUTABLE", immutable.exception.code)
            with self.assertRaises(self.brain.ProjectBrainError) as decision_immutable:
                first.put_decision(
                    decision_id="decision-one",
                    owner="different-owner",
                    scope="project brain",
                    status="APPROVED",
                    evidence="exact plan",
                )
            self.assertEqual("PROJECT_MEMORY_DECISION_IMMUTABLE", decision_immutable.exception.code)
            with self.assertRaises(self.brain.ProjectBrainError) as episode_immutable:
                first.put_episode(
                    episode_id="episode-one",
                    feature_id="different-feature",
                    result_sha256="b" * 64,
                    summary="accepted brain result",
                    citations="receipt-one",
                )
            self.assertEqual("PROJECT_MEMORY_EPISODE_IMMUTABLE", episode_immutable.exception.code)
            self.assertEqual("PASS", first.integrity_check())


if __name__ == "__main__":
    unittest.main()


class ProjectBrainValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = load_project_brain()

    @staticmethod
    def owner(mode: str, existing: str = "existing source seam") -> dict[str, str]:
        return {
            "EXISTING_FEATURE": existing,
            "UI_SETTINGS": "settings seam",
            "SERVER_AUTHORITY": "server seam",
            "PLAN_ENTITLEMENT": "plan seam",
            "REFERENCE_REUSE": "reference seam",
            "PERSISTENCE_CONSUMPTION": "persistence seam",
            "INTEGRATED_HISTORY": "history seam",
            "TEST_PROOF": "test seam",
            "GAP": "bounded gap",
            "CHANGE_MODE": mode,
        }

    def test_source_span_drift_and_safe_path_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="x9-brain-source-") as directory:
            repo = Path(directory)
            source = repo / "source.txt"
            source.write_bytes(b"alpha\nbeta\n")
            data = source.read_bytes()
            ref = {
                "ref_id": "src-one",
                "path": "source.txt",
                "file_sha256": self.brain.sha256_bytes(data),
                "byte_start": 0,
                "byte_end": len(data),
                "span_sha256": self.brain.sha256_bytes(data),
            }
            self.assertEqual("source.txt", self.brain.validate_source_ref(repo, ref)["path"])
            source.write_bytes(b"changed\n")
            with self.assertRaises(self.brain.ProjectBrainError) as drift:
                self.brain.validate_source_ref(repo, ref)
            self.assertEqual("PROJECT_SOURCE_FILE_DRIFT", drift.exception.code)
            with self.assertRaises(self.brain.ProjectBrainError):
                self.brain.canonical_repo_path("../outside.txt")

    def test_ownership_modes_and_repeated_failure_gate(self):
        with self.assertRaises(self.brain.ProjectBrainError) as conflict:
            self.brain.validate_ownership(self.owner("NEW"))
        self.assertEqual("PROJECT_OWNERSHIP_NEW_CONFLICT", conflict.exception.code)
        self.assertEqual("REUSE", self.brain.validate_ownership(self.owner("REUSE"))[0]["CHANGE_MODE"])
        failure = {
            "class": "PRODUCT",
            "code": "PROJECT_CONTEXT_DRIFT",
            "signature": self.brain.failure_signature("PRODUCT", "PROJECT_CONTEXT_DRIFT"),
            "progress": False,
        }
        gate = self.brain.repeated_failure_gate([{"failure": failure}] * 3)
        self.assertTrue(gate["open"])
        infra = dict(failure, **{"class": "INFRASTRUCTURE"})
        self.assertFalse(self.brain.repeated_failure_gate([{"failure": infra}] * 4)["open"])

    def test_docs_are_linked_manifest_bound_and_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="x9-brain-docs-") as directory:
            repo = Path(directory)
            result = accepted_result()
            binding = accepted_binding(self.brain, result, "feature-one", repo)
            first = self.brain.generate_feature_docs(repo, "feature-one", result, profile_id="profile:fixture", binding=binding)
            second = self.brain.generate_feature_docs(repo, "feature-one", result, profile_id="profile:fixture", binding=binding)
            self.assertEqual(first, second)
            docs = repo / ".devad" / "features" / "feature-one"
            self.assertEqual("PASS", self.brain.validate_sitemap(docs / "TASK.md", manifest_path=docs / "MANIFEST.sha256")["status"])

    def test_execution_sitemap_requires_complete_hash_bound_transfer_sections(self):
        with tempfile.TemporaryDirectory(prefix="x9-execution-sitemap-") as directory:
            docs = Path(directory)
            detail = docs / "DETAILS.md"
            detail.write_text("durable detail\n", encoding="utf-8")
            task = docs / "TASK.md"
            task.write_text(
                "# execution sitemap\n\n" + "\n".join(
                    f"## {heading}\n\n- [details](DETAILS.md)\n"
                    for heading in self.brain.EXECUTION_SITEMAP_HEADINGS
                ),
                encoding="utf-8",
            )
            manifest = docs / "MANIFEST.sha256"
            manifest.write_text(
                f"{self.brain.sha256_bytes(task.read_bytes())}  TASK.md\n"
                f"{self.brain.sha256_bytes(detail.read_bytes())}  DETAILS.md\n",
                encoding="utf-8",
            )
            self.assertTrue(self.brain.validate_execution_sitemap(
                task, manifest_path=manifest
            )["execution_sitemap"])
            task.write_text("# incomplete\n", encoding="utf-8")
            with self.assertRaises(self.brain.ProjectBrainError):
                self.brain.validate_execution_sitemap(task, manifest_path=manifest)

    def test_docs_accept_real_v7_work_order_packet_binding(self):
        with tempfile.TemporaryDirectory(prefix="x9-brain-real-v7-docs-") as directory:
            repo = Path(directory)
            result = accepted_result()
            feature_id = "feature-real-v7"
            base_sha = "e" * 40
            for item in result["proof"]:
                payload = (
                    f'{{"dispatch_id":"{result["dispatch_id"]}",'
                    f'"event_id":"{result["event_id"]}",'
                    f'"kind":"{item["kind"]}",'
                    '"schema":"x9-loop-proof-v2","status":"PASS",'
                    f'"task_id":"{result["task_id"]}",'
                    f'"work_order_id":"{result["work_order_id"]}",'
                    f'"worker_id":"{result["worker_id"]}"}}\n'
                ).encode()
                path = repo / item["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                item["sha256"] = self.brain.sha256_bytes(payload)

            feature_path = repo / ".devad" / "manager" / "loop-lite" / "programs" / "program-real-v7" / "features" / feature_id / "FEATURE_PACKET.json"
            feature_path.parent.mkdir(parents=True, exist_ok=True)
            feature_path.write_bytes(self.brain.canonical_json_bytes({
                "schema": "x9-loop-feature-v1",
                "feature_id": feature_id,
                "base_sha": base_sha,
                "owner_requirement": "real V7 feature packet has no standalone plan_sha256",
            }) + b"\n")
            feature_sha = self.brain.sha256_bytes(feature_path.read_bytes())
            work_order_path = repo / ".devad" / "manager" / "loop-lite" / "runtime" / "work-orders" / result["work_order_id"] / "WORK_ORDER.json"
            work_order_path.parent.mkdir(parents=True, exist_ok=True)
            work_order_path.write_bytes(self.brain.canonical_json_bytes({
                "schema": "x9-loop-work-order-v1",
                "work_order_id": result["work_order_id"],
                "task_id": result["task_id"],
                "worker_id": result["worker_id"],
                "base_sha": base_sha,
                "feature_packet_refs": [{
                    "feature_id": feature_id,
                    "path": feature_path.relative_to(repo).as_posix(),
                    "sha256": feature_sha,
                }],
            }) + b"\n")
            work_order_sha = self.brain.sha256_bytes(work_order_path.read_bytes())
            result["packet_sha256"] = work_order_sha
            result["work_order_sha256"] = work_order_sha
            source_manifest_path = repo / "SOURCE_MANIFEST.sha256"
            source_manifest_path.write_bytes(b"real v7 source manifest\n")
            result_path = repo / ".devad" / "workers" / result["worker_id"] / "receipts" / (result["event_id"] + ".json")
            result_path.parent.mkdir(parents=True, exist_ok=True)
            result_path.write_bytes(self.brain.canonical_json_bytes(result) + b"\n")
            result_sha = self.brain.sha256_bytes(result_path.read_bytes())
            result_ready_path = repo / ".devad" / "manager" / "loop-lite" / "runtime" / "result-ready" / result["event_id"] / "RESULT_READY.json"
            result_ready_path.parent.mkdir(parents=True, exist_ok=True)
            result_ready_path.write_bytes(self.brain.canonical_json_bytes({
                "schema": "x9-loop-result-ready-v1",
                "status": "READY",
                "expected_result_identity": {
                    "dispatch_id": result["dispatch_id"],
                    "event_id": result["event_id"],
                    "packet_sha256": result["packet_sha256"],
                    "result_path": result_path.relative_to(repo).as_posix(),
                    "result_sha256": result_sha,
                    "task_id": result["task_id"],
                    "work_order_id": result["work_order_id"],
                    "work_order_sha256": result["work_order_sha256"],
                    "worker_id": result["worker_id"],
                },
            }) + b"\n")
            subprocess.run(["git", "-C", str(repo), "init", "--quiet"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "fixture@example.invalid"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "X9 Fixture"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "--allow-empty", "-m", "real v7 fixture"], check=True, capture_output=True)
            current_sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            binding = {
                "feature_id": feature_id,
                "feature_packet_sha256": feature_sha,
                "plan_sha256": None,
                "task_id": result["task_id"],
                "work_order_id": result["work_order_id"],
                "work_order_sha256": work_order_sha,
                "dispatch_id": result["dispatch_id"],
                "event_id": result["event_id"],
                "worker_id": result["worker_id"],
                "profile_id": "profile:fixture",
                "base_sha": base_sha,
                "current_sha": current_sha,
                "result_sha256": result_sha,
                "source_manifest_sha256": self.brain.sha256_bytes(source_manifest_path.read_bytes()),
                "proof": result["proof"],
                "changed_files": result["changed_files"],
                "attestation_path": result["attestation_path"],
                "c2_sha256": None,
                "unknown_items": [],
                "rollback": "restore fixture",
                "canonical_refs": {
                    "feature_packet": {"path": feature_path.relative_to(repo).as_posix(), "sha256": feature_sha},
                    "work_order": {"path": work_order_path.relative_to(repo).as_posix(), "sha256": work_order_sha},
                    "result": {"path": result_path.relative_to(repo).as_posix(), "sha256": self.brain.sha256_bytes(result_path.read_bytes())},
                    "source_manifest": {"path": source_manifest_path.relative_to(repo).as_posix(), "sha256": self.brain.sha256_bytes(source_manifest_path.read_bytes())},
                    "result_ready": {"path": result_ready_path.relative_to(repo).as_posix(), "sha256": self.brain.sha256_bytes(result_ready_path.read_bytes())},
                },
            }
            generated = self.brain.generate_feature_docs(repo, feature_id, result, profile_id="profile:fixture", binding=binding)
            self.assertEqual("VERIFIED", generated["status"])
            self.assertEqual("PASS", self.brain.validate_sitemap(repo / ".devad" / "features" / feature_id / "TASK.md", manifest_path=repo / ".devad" / "features" / feature_id / "MANIFEST.sha256")["status"])

    def test_memory_backup_migrate_and_rollback_validate_fts(self):
        with tempfile.TemporaryDirectory(prefix="x9-brain-migration-") as directory:
            repo = Path(directory)
            memory = self.brain.ProjectMemory(repo, "profile:migrate")
            memory.initialize()
            memory.put_fact(
                fact_id="before",
                semantic_key="capability.before",
                value="before rollback",
                source_ref_ids=[],
            )
            backup = repo / "memory-backup.sqlite"
            self.assertEqual(backup, memory.backup(backup))
            memory.put_fact(
                fact_id="after",
                semantic_key="capability.after",
                value="after backup",
                source_ref_ids=[],
            )
            self.assertEqual("PASS", memory.migrate())
            self.assertEqual("PASS", memory.rollback(backup))
            self.assertEqual([], memory.search("after"))
            self.assertEqual("before rollback", memory.search("before")[0]["value"])
            self.assertEqual("PASS", memory.integrity_check())

    def test_migration_rejects_fts_drift_and_missing_surface_then_restores_backup(self):
        with tempfile.TemporaryDirectory(prefix="x9-brain-fts-failure-") as directory:
            repo = Path(directory)
            memory = self.brain.ProjectMemory(repo, "profile:fts-failure")
            memory.initialize()
            memory.put_fact(
                fact_id="before",
                semantic_key="capability.before",
                value="before rollback",
                source_ref_ids=[],
            )
            memory.put_episode(
                episode_id="episode-before",
                feature_id="feature-one",
                result_sha256="c" * 64,
                summary="before rollback episode",
                citations="receipt-before",
            )
            backup = repo / "memory-backup.sqlite"
            memory.backup(backup)
            backup_bytes = backup.read_bytes()
            connection = sqlite3.connect(memory.database_path)
            connection.execute("UPDATE facts_fts SET value=? WHERE fact_id=?", ("drifted", "before"))
            connection.commit()
            connection.close()
            with self.assertRaises(self.brain.ProjectBrainError) as drift:
                memory.migrate()
            self.assertEqual("PROJECT_MEMORY_FTS_DRIFT", drift.exception.code)
            self.assertEqual(backup_bytes, backup.read_bytes())
            self.assertEqual("PASS", memory.rollback(backup))
            self.assertEqual("before rollback", memory.search("before")[0]["value"])
            connection = sqlite3.connect(memory.database_path)
            connection.execute("D" + "ROP TABLE document_titles_fts")
            connection.commit()
            connection.close()
            with self.assertRaises(self.brain.ProjectBrainError) as missing:
                memory.migrate()
            self.assertEqual("PROJECT_MEMORY_SCHEMA_INVALID", missing.exception.code)
            self.assertEqual("PASS", memory.rollback(backup))
            self.assertEqual("PASS", memory.integrity_check())
            original_validate = memory._validate_database
            validation_calls = {"current": 0}
            def fail_after_candidate(database_path=None):
                if database_path is None:
                    validation_calls["current"] += 1
                    if validation_calls["current"] == 2:
                        raise self.brain.ProjectBrainError("PROJECT_MEMORY_CORRUPT")
                return original_validate(database_path)
            memory._validate_database = fail_after_candidate
            with self.assertRaises(self.brain.ProjectBrainError) as migration_failure:
                memory.migrate()
            memory._validate_database = original_validate
            self.assertEqual("PROJECT_MEMORY_MIGRATION_FAILED", migration_failure.exception.code)
            self.assertEqual("PASS", memory.integrity_check())
            self.assertFalse(Path(str(memory.database_path) + ".next").exists())
            self.assertFalse(Path(str(memory.database_path) + ".rollback.next").exists())

    def test_v7_rollback_doctor_is_covered_in_claimed_brain_gate(self):
        migration_path = ROOT / "tests" / "test_v73_migration.py"
        spec = importlib.util.spec_from_file_location(
            "v73_migration_fixture_for_brain", migration_path
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        migration = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = migration
        spec.loader.exec_module(migration)
        migration.V73MigrationTests.setUpClass()
        case = migration.V73MigrationTests("runTest")
        case.setUp()
        try:
            case._write_authentic_v7_state()
            migrated = case.controller.migrate_v2_to_v3()
            self.assertEqual("PASS", migrated["status"])
            rollback = case.controller.rollback_to_v7(migrated["recovery_id"])
            self.assertEqual("PASS", rollback["status"])
            proof = case.controller.doctor_v7()
            self.assertEqual("PASS", proof["status"], proof)
        finally:
            case.doCleanups()

if __name__ == "__main__":
    unittest.main()
