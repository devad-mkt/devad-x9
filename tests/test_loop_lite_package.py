from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "devad-x9-loop"
TEMPLATE = ROOT / "templates" / "x9-project" / ".devad"
LOOP_LITE = TEMPLATE / "manager" / "loop-lite"
OPENCODE_DOCTOR = SKILL / "scripts" / "opencode_doctor.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class LoopLitePackageTests(unittest.TestCase):
    def make_package_copy(self, directory: str) -> Path:
        destination = Path(directory) / "kit"
        shutil.copytree(
            ROOT,
            destination,
            ignore=shutil.ignore_patterns(
                ".git", ".temp", "archives", "__pycache__", "*.pyc"
            ),
        )
        return destination

    def rebuild_manifest(self, package: Path) -> None:
        subprocess.run(
            [sys.executable, str(package / "scripts" / "build_source_manifest.py")],
            cwd=package,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_manifest_excludes_and_rejects_git_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package_copy(directory)
            git_config = package / ".git" / "config"
            git_config.parent.mkdir()
            git_config.write_text("[remote]\nurl = private\n", encoding="utf-8")
            self.rebuild_manifest(package)
            manifest = package / "SOURCE_MANIFEST.sha256"
            lines = manifest.read_text(encoding="utf-8-sig").splitlines()
            self.assertFalse(any("  .git/" in line for line in lines))
            manifest.write_text(
                manifest.read_text(encoding="utf-8")
                + f"{'0' * 64}  .git/config\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(package / "scripts" / "validate_suite.py")],
                cwd=package,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("manifest includes Git metadata", result.stdout)

    def test_manifest_excludes_linked_worktree_git_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package_copy(directory)
            (package / ".git").write_text(
                "gitdir: C:/example/repo/.git/worktrees/kit\n",
                encoding="utf-8",
            )
            self.rebuild_manifest(package)
            lines = (package / "SOURCE_MANIFEST.sha256").read_text(
                encoding="utf-8-sig"
            ).splitlines()
        self.assertFalse(any(line.endswith("  .git") for line in lines))

    def test_manifest_excludes_host_agents_runtime_state(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package_copy(directory)
            host_skill = package / ".agents" / "skills" / "local-only" / "SKILL.md"
            host_skill.parent.mkdir(parents=True)
            host_skill.write_bytes(b"---\r\nname: local-only\r\n---\r\n")
            self.rebuild_manifest(package)
            lines = (package / "SOURCE_MANIFEST.sha256").read_text(
                encoding="utf-8-sig"
            ).splitlines()
            result = subprocess.run(
                [sys.executable, str(package / "scripts" / "validate_suite.py")],
                cwd=package,
                capture_output=True,
                text=True,
            )
        self.assertFalse(any("  .agents/" in line for line in lines))
        self.assertEqual(0, result.returncode, result.stdout)

    def test_manifest_rejects_crlf_utf8_text(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package_copy(directory)
            bad = package / "crlf.txt"
            data = b"one\r\ntwo\r\n"
            bad.write_bytes(data)
            build = subprocess.run(
                [sys.executable, str(package / "scripts" / "build_source_manifest.py")],
                cwd=package,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, build.returncode)
            self.assertIn("UTF-8 text must use LF", build.stderr + build.stdout)
            manifest = package / "SOURCE_MANIFEST.sha256"
            manifest.write_text(
                manifest.read_text(encoding="utf-8")
                + f"{hashlib.sha256(data).hexdigest()}  crlf.txt\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(package / "scripts" / "validate_suite.py")],
                cwd=package,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("manifest includes CRLF UTF-8 text", result.stdout)

    def test_validator_requires_loop_lite_recovery_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package_copy(directory)
            snapshot = package / "templates" / "x9-project" / ".devad" / "manager" / "loop-lite" / "SNAPSHOT.json"
            snapshot.unlink()
            self.rebuild_manifest(package)
            result = subprocess.run(
                [sys.executable, str(package / "scripts" / "validate_suite.py")],
                cwd=package,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing loop-lite recovery snapshot", result.stdout)

    def test_validator_reports_v7_with_historical_v5_loop(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package_copy(directory)
            self.rebuild_manifest(package)
            result = subprocess.run(
                [sys.executable, str(package / "scripts" / "validate_suite.py")],
                cwd=package,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("PASS: X9 Loop V7", result.stdout)

    def test_quarantined_v7_contract_retains_one_action_route(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("X9 Loop V7 Compatibility Redirect", text)
        self.assertIn("$x9-loop-style", text)
        self.assertIn("Archived V7 contract", text)
        self.assertIn("scripts/loopctl.py", text)
        self.assertIn("--repo <repo> reconcile", text)
        self.assertIn("runtime/ACTION.json", text)
        self.assertIn("linker never selects", text.lower())
        self.assertIn("No recurring heartbeat", text)
        self.assertIn("gpt-5.6-sol ultra", text)

    def test_template_has_small_recovery_truth_and_contracts(self):
        expected = {
            ".gitignore",
            "README.md",
            "SNAPSHOT.json",
            "contracts",
        }
        self.assertTrue(expected.issubset({path.name for path in LOOP_LITE.iterdir()}))
        snapshot = json.loads((LOOP_LITE / "SNAPSHOT.json").read_text(encoding="utf-8"))
        self.assertEqual("x9-loop-lite-snapshot-v3", snapshot["schema"])
        self.assertEqual(
            {
                "actors",
                "worktrees",
                "tasks",
                "claims",
                "resources",
                "dispatches",
                "deliveries",
                "events",
                "gates",
                "outbox",
                "inbox",
                "metrics",
                "programs",
                "work_orders",
                "worktree_classifications",
                "call_reservations",
            },
            set(snapshot["tables"]),
        )
        self.assertLess((LOOP_LITE / "SNAPSHOT.json").stat().st_size, 8192)
        ignore = (LOOP_LITE / ".gitignore").read_text(encoding="utf-8")
        for item in ("loop.db", "loop.db-shm", "loop.db-wal", "runtime/"):
            self.assertIn(item, ignore)
        contracts = {path.name for path in (LOOP_LITE / "contracts").glob("*.json")}
        self.assertEqual(
            {
                "ACTION.json",
                "CALL_RECEIPT.json",
                "FEATURE_PACKET.json",
                "OWNER_PACKET.json",
                "PROGRAM_PACKET.json",
                "RESULT.json",
                "STOP_CONTRACT.json",
                "TASK.json",
                "WORKER_CHECKPOINT.json",
                "WORK_ORDER.json",
            },
            contracts,
        )
        for path in (LOOP_LITE / "contracts").glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn(
                payload["schema"],
                {
                    "x9-owner-packet-v1",
                    "x9-loop-lite-task-v1",
                    "x9-loop-action-v2",
                    "x9-loop-result-v2",
                    "x9-loop-call-receipt-v1",
                    "x9-loop-feature-v1",
                    "x9-loop-program-v1",
                    "x9-loop-stop-contract-v1",
                    "x9-loop-worker-checkpoint-v1",
                    "x9-loop-work-order-v1",
                },
            )
        action = json.loads((LOOP_LITE / "contracts" / "ACTION.json").read_text(encoding="utf-8"))
        self.assertEqual("x9-loop-action-v2", action["schema"])
        self.assertEqual("SEND_WORK_ORDER", action["action"])
        self.assertEqual(
            {
                "action",
                "action_id",
                "attempt",
                "dispatch_id",
                "must_record_transport",
                "project_profile_id",
                "schema",
                "target_actor_id",
                "target_role",
                "task_id",
                "work_order_id",
                "work_order_path",
                "work_order_sha256",
            },
            set(action),
        )
        self.assertNotIn("packet", action)
        task = json.loads((LOOP_LITE / "contracts" / "TASK.json").read_text(encoding="utf-8"))
        self.assertEqual(".devad/manager/owner-packets/<packet_sha256>.json", task["owner_packet_path"])
        self.assertEqual("task", task["kind"])
        self.assertIn("owner_packet_sha256", task)
        owner = json.loads((LOOP_LITE / "contracts" / "OWNER_PACKET.json").read_text(encoding="utf-8"))
        self.assertEqual("x9-owner-packet-v1", owner["schema"])
        self.assertEqual(".devad/manager/owner-packets/artifacts/<attachment_sha256>.txt", owner["attachments"][0]["path"])
        self.assertNotIn("packet_sha256", owner)
        result = json.loads((LOOP_LITE / "contracts" / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual("SUCCESS", result["outcome"])
        self.assertIsInstance(result["proof"], list)
        self.assertTrue(all({"kind", "path", "sha256"}.issubset(item) for item in result["proof"]))
        self.assertEqual({"security", "tests"}, {item["kind"] for item in result["proof"]})
        proof_paths = {item["kind"]: item["path"] for item in result["proof"]}
        self.assertEqual(".devad/workers/<worker_id>/proof/<event_id>/security.json", proof_paths["security"])
        self.assertEqual(".devad/workers/<worker_id>/proof/<event_id>/tests.json", proof_paths["tests"])
        self.assertIsInstance(result["c1"], str)
        self.assertIsInstance(result["c2"], str)
        self.assertEqual({"changed_surface", "proof_refs", "reason", "remaining_risk", "rollback"}, set(result["change_map"]))
        self.assertEqual("x9-loop-result-v2", result["schema"])
        self.assertLess((LOOP_LITE / "contracts" / "ACTION.json").stat().st_size, 4096)
        owner_store = LOOP_LITE.parent / "owner-packets"
        self.assertTrue((owner_store / ".gitignore").is_file())
        self.assertTrue((owner_store / "README.md").is_file())
        owner_ignore = (owner_store / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*", owner_ignore.splitlines())
        self.assertIn("!.gitignore", owner_ignore.splitlines())
        self.assertIn("!README.md", owner_ignore.splitlines())
        self.assertIn("local sensitive state", (owner_store / "README.md").read_text(encoding="utf-8"))

    def test_generated_registry_is_portable_lf(self):
        self.assertNotIn(b"\r\n", (ROOT / "features.registry.json").read_bytes())
        generator = (ROOT / "scripts" / "build_feature_registry.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(2, generator.count('newline="\\n"'))
    def test_old_v5_state_stays_as_legacy_evidence(self):
        old = TEMPLATE / "manager" / "loop"
        self.assertTrue((old / "PASS_CAPSULE.json").is_file())
        self.assertTrue((old / "ROLE_REGISTRY.json").is_file())
        router = (TEMPLATE / "ROUTER.md").read_text(encoding="utf-8")
        self.assertIn("manager/loop-lite/SNAPSHOT.json", router)
        self.assertIn("manager/loop-lite/runtime/ACTION.json", router)
        self.assertIn("manager/loop/", router)
        self.assertIn("historical", router.lower())
        self.assertNotIn("Acquire `.devad/manager/MANAGER_PASS_LOCK.md`", router)

    def test_v7_contract_preserves_machine_authority_and_hard_gates(self):
        contract = (SKILL / "references" / "loop-lite-v7-contract.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "controller is the sole writer",
            "linx reads only",
            "deterministic acceptance",
            "any staged-byte change invalidates the review",
            "before every call",
            "no model call occurs after exhaustion",
            "cache_prefix_changed",
            "approved_jobs.json",
            "complete v6 database",
            "no polling",
        ):
            self.assertIn(phrase, contract.lower())

    def test_orca_boundary_is_explicit(self):
        text = (ROOT / "docs" / "ORCA_LESSONS.md").read_text(encoding="utf-8")
        for kept in (
            "task and dispatch identity",
            "dependency-ready",
            "worker-owned completion",
            "decision gates",
        ):
            self.assertIn(kept, text.lower())
        for rejected in (
            "runtime dependency",
            "message bus",
            "heartbeat",
            "terminal",
            "polling",
        ):
            self.assertIn(rejected, text.lower())

    def test_feature_registry_classifies_v6(self):
        registry = json.loads((ROOT / "features.registry.json").read_text(encoding="utf-8"))
        ids = {feature["id"] for feature in registry["features"]}
        required = {
            "loop-lite-controller",
            "loop-lite-recovery-snapshot",
            "loop-lite-machine-contracts",
            "loop-lite-scope-claims",
            "loop-lite-direct-callback",
            "loop-lite-sidecar-doctor",
            "loop-lite-generated-human-views",
        }
        self.assertTrue(required.issubset(ids), required - ids)

    def test_readme_has_v7_fast_path_and_performance_gates(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("X9 Loop V7", text)
        self.assertIn("under five seconds", text)
        self.assertIn("median under 60 seconds", text)
        self.assertIn("p95 under two minutes", text)
        self.assertIn("Unknown", text)
        self.assertIn("Three coding Workers", text)


    def test_v7_package_metadata_and_skill_interface(self):
        kit = json.loads((ROOT / "kit.manifest.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "skills.index.json").read_text(encoding="utf-8"))
        interface = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        style = (ROOT / "skills" / "x9-loop-style" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertEqual("7.3-lite", kit["version"])
        self.assertEqual("devad-x9-loop-codex-kit-v7.3-lite", kit["schema"])
        self.assertEqual("devad-x9-loop-kit-v7.3-lite", index["schema"])
        self.assertEqual("2026-07-30", index["date"])
        self.assertEqual(16, kit["packaged_skills"])
        self.assertEqual("x9-loop-style", kit["manager_skill"])
        self.assertEqual("x9-loop-code", kit["experimental_engine_skill"])
        self.assertIn('display_name: "X9 Loop (Style redirect)"', interface)
        self.assertIn("$x9-loop-style", interface)
        self.assertIn('display_name: "X9 Loop Style"', style)


class OpenCodeDoctorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doctor = load_module("opencode_doctor", OPENCODE_DOCTOR)

    def sidecar_packet(
        self, repo: Path, payload: dict[str, object] | None = None
    ) -> Path:
        sidecar = repo / ".devad" / "manager" / "sidecar"
        sidecar.mkdir(parents=True)
        packet = sidecar / "packet.json"
        packet.write_text(
            json.dumps(
                payload
                or {
                    "schema": "x9-sidecar-packet-v1",
                    "owner_requirement": "Review the bounded blocker.",
                    "claims": ["The local test is reproducible."],
                    "relevant_diff": ["src/example.py"],
                    "proof": ["tests/test_example.py"],
                    "failure": "The first local attempt failed.",
                    "question": "What is the smallest safe next step?",
                }
            ),
            encoding="utf-8",
        )
        return packet

    def test_packet_requires_exact_x9_sidecar_schema_before_process_start(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            packet = self.sidecar_packet(
                repo,
                {
                    "schema": "x9-sidecar-packet-v1",
                    "owner_requirement": "Review this.",
                    "claims": ["One claim."],
                    "relevant_diff": ["src/example.py"],
                    "proof": ["tests/test_example.py"],
                    "failure": "A failure happened.",
                    "question": "What next?",
                    "unexpected": "not allowed",
                },
            )
            with mock.patch("subprocess.run") as process:
                result = self.doctor.run_request(
                    packet=packet,
                    model="opencode-go/glm-5.2",
                    repo=repo,
                    timeout=5,
                    executable="opencode",
                )
        self.assertEqual("PACKET_SCHEMA_INVALID", result["status"])
        process.assert_not_called()

    def test_secret_packet_is_rejected_before_process_start(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            packet = self.sidecar_packet(
                repo,
                {
                    "schema": "x9-sidecar-packet-v1",
                    "owner_requirement": "Review this.",
                    "claims": ["API_KEY=super-secret-value"],
                    "relevant_diff": ["src/example.py"],
                    "proof": ["tests/test_example.py"],
                    "failure": "A failure happened.",
                    "question": "What next?",
                },
            )
            with mock.patch("subprocess.run") as process:
                result = self.doctor.run_request(
                    packet=packet,
                    model="opencode-go/glm-5.2",
                    repo=repo,
                    timeout=5,
                    executable="opencode",
                )
        self.assertEqual("PACKET_SECRET_BLOCKED", result["status"])
        process.assert_not_called()
        self.assertNotIn("super-secret-value", json.dumps(result))

    def test_bearer_aws_and_database_credentials_are_rejected_before_process_start(self):
        secret_values = (
            "Authorization: " + "Bearer " + "eyJhbGciOiJIUzI1NiJ9.payload.signature",
            "AKIA" + "IOSFODNN7EXAMPLE",
            "postgresql://app_user:" + "password@db.example.test/app",
            "ghp_" + "A" * 36,
            "github_pat_" + "A" * 30,
        )
        for secret_value in secret_values:
            with self.subTest(secret_value=secret_value), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                packet = self.sidecar_packet(
                    repo,
                    {
                        "schema": "x9-sidecar-packet-v1",
                        "owner_requirement": "Review this.",
                        "claims": [secret_value],
                        "relevant_diff": ["src/example.py"],
                        "proof": ["tests/test_example.py"],
                        "failure": "A failure happened.",
                        "question": "What next?",
                    },
                )
                with mock.patch("subprocess.run") as process:
                    result = self.doctor.run_request(
                        packet=packet,
                        model="opencode-go/glm-5.2",
                        repo=repo,
                        timeout=5,
                        executable="opencode",
                    )
            self.assertEqual("PACKET_SECRET_BLOCKED", result["status"])
            process.assert_not_called()

    def test_packet_symlink_escape_is_rejected_before_process_start(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            outside = Path(td) / "outside.json"
            repo.mkdir()
            outside.write_text("{}", encoding="utf-8")
            link = repo / ".devad" / "manager" / "sidecar" / "packet.json"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(outside)
            except OSError as exc:
                if os.name != "nt":
                    self.skipTest(f"symlinks are unavailable: {exc}")
                link.parent.rmdir()
                outside_dir = Path(td) / "outside"
                outside_dir.mkdir()
                (outside_dir / "packet.json").write_text("{}", encoding="utf-8")
                junction = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(link.parent), str(outside_dir)],
                    capture_output=True,
                    check=False,
                )
                if junction.returncode:
                    self.skipTest(f"junctions are unavailable: {junction.stderr!r}")
            with mock.patch("subprocess.run") as process:
                result = self.doctor.run_request(
                    packet=link,
                    model="opencode-go/glm-5.2",
                    repo=repo,
                    timeout=5,
                    executable="opencode",
                )
        self.assertEqual("PACKET_PATH_BLOCKED", result["status"])
        process.assert_not_called()

    def test_output_must_stay_with_the_packet_in_its_approved_sidecar_folder(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            packet = self.sidecar_packet(repo)
            with mock.patch("subprocess.run") as process:
                result = self.doctor.run_request(
                    packet=packet,
                    model="opencode-go/glm-5.2",
                    repo=repo,
                    output=repo / "outside.md",
                    timeout=5,
                    executable="opencode",
                )
        self.assertEqual("OUTPUT_PATH_BLOCKED", result["status"])
        process.assert_not_called()

    def test_valid_output_uses_tools_denied_isolated_runner(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            packet = self.sidecar_packet(repo)
            output = packet.with_name("glm-review.md")
            completed = subprocess.CompletedProcess(
                args=["opencode.exe"], returncode=0, stdout="review", stderr=""
            )
            observed = {}

            def execute(command, **kwargs):
                observed["command"] = command
                observed["cwd"] = Path(kwargs["cwd"])
                observed["env"] = kwargs["env"]
                config = json.loads(
                    (observed["cwd"] / "opencode.json").read_text(encoding="utf-8")
                )
                self.assertEqual({"*": "deny"}, config["permission"])
                attached = Path(command[command.index("--file") + 1])
                self.assertEqual(observed["cwd"], attached.parent)
                self.assertEqual(packet.read_bytes(), attached.read_bytes())
                return completed

            with mock.patch.dict(
                os.environ,
                {"TEST_SECRET_SENTINEL": "must-not-reach-opencode"},
            ), mock.patch.object(
                self.doctor,
                "resolve_executable",
                return_value=r"C:\safe\opencode.exe",
            ), mock.patch("subprocess.run", side_effect=execute):
                result = self.doctor.run_request(
                    packet=packet,
                    model="opencode-go/glm-5.2",
                    repo=repo,
                    output=output,
                    timeout=5,
                    executable="opencode",
                )
            self.assertEqual("PASS", result["status"])
            self.assertEqual("review\n", output.read_text(encoding="utf-8"))
            self.assertEqual("run", observed["command"][1])
            self.assertIn("--pure", observed["command"])
            self.assertNotIn("--auto", observed["command"])
            self.assertNotIn(str(repo), observed["command"])
            self.assertNotEqual(repo.resolve(), observed["cwd"])
            self.assertNotIn("TEST_SECRET_SENTINEL", observed["env"])

    def test_unavailable_model_is_one_attempt_and_nonblocking(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            packet = self.sidecar_packet(repo)
            failed = subprocess.CompletedProcess(
                args=["opencode"], returncode=1, stdout="", stderr="model not found"
            )
            with mock.patch.object(
                self.doctor,
                "resolve_executable",
                return_value=r"C:\safe\opencode.exe",
            ), mock.patch("subprocess.run", return_value=failed) as process:
                result = self.doctor.run_request(
                    packet=packet,
                    model="opencode-go/kimi-k2.7-code",
                    repo=repo,
                    timeout=5,
                    executable="opencode",
                )
        self.assertEqual("TOOL_UNAVAILABLE", result["status"])
        self.assertEqual(1, result["attempts"])
        self.assertFalse(result["blocks_worker"])
        self.assertEqual(1, process.call_count)

    def test_context_cap_blocks_oversize_packet(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            packet = self.sidecar_packet(repo)
            packet.write_bytes(b"x" * (self.doctor.MAX_PACKET_BYTES + 1))
            with mock.patch("subprocess.run") as process:
                result = self.doctor.run_request(
                    packet=packet,
                    model="opencode-go/glm-5.2",
                    repo=repo,
                    timeout=5,
                    executable="opencode",
                )
        self.assertEqual("PACKET_TOO_LARGE", result["status"])
        process.assert_not_called()
    def test_doctor_never_dumps_environment_values(self):
        fake = subprocess.CompletedProcess(
            args=["opencode", "models"],
            returncode=0,
            stdout="opencode-go/glm-5.2\nopencode-go/kimi-k2.7-code\n",
            stderr="",
        )
        with mock.patch.dict(os.environ, {"TEST_SECRET_SENTINEL": "never-print-me"}):
            with mock.patch.object(
                self.doctor,
                "resolve_executable",
                return_value=r"C:\safe\opencode.exe",
            ), mock.patch("subprocess.run", return_value=fake) as process:
                result = self.doctor.doctor(executable="opencode", timeout=5)
        self.assertEqual("PASS", result["status"])
        self.assertNotIn("never-print-me", json.dumps(result))
        self.assertEqual(
            [r"C:\safe\opencode.exe", "--pure", "models"],
            process.call_args.args[0],
        )
        self.assertNotIn("TEST_SECRET_SENTINEL", process.call_args.kwargs["env"])

    @unittest.skipUnless(os.name == "nt", "Windows resolver test")
    def test_windows_resolver_maps_cmd_shim_to_real_exe(self):
        with tempfile.TemporaryDirectory() as td:
            npm = Path(td)
            shim = npm / "opencode.cmd"
            shim.write_text("@echo off\n", encoding="utf-8")
            executable = npm / "node_modules" / "opencode-ai" / "bin" / "opencode.exe"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"MZ")
            with mock.patch.object(
                self.doctor.shutil,
                "which",
                side_effect=[None, str(shim)],
            ) as which:
                resolved = self.doctor.resolve_executable("opencode")
        self.assertEqual(str(executable.resolve()), resolved)
        self.assertEqual(
            [mock.call("opencode.exe"), mock.call("opencode.cmd")],
            which.call_args_list,
        )
        self.assertIsNone(self.doctor.resolve_executable(str(shim)))

    def test_executable_unavailable_has_a_nonblocking_failure_class(self):
        with mock.patch("subprocess.run", side_effect=FileNotFoundError):
            result = self.doctor.doctor(executable="missing-opencode", timeout=5)
        self.assertEqual("TOOL_UNAVAILABLE", result["status"])
        self.assertEqual("EXECUTABLE_UNAVAILABLE", result["failure_class"])
        self.assertEqual(1, result["attempts"])
        self.assertFalse(result["blocks_worker"])


if __name__ == "__main__":
    unittest.main()
