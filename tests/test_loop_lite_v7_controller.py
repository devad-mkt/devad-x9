from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
LOOPCTL = ROOT / "skills" / "devad-x9-loop" / "scripts" / "loopctl.py"
LINKER_ONCE = ROOT / "skills" / "devad-x9-loop" / "scripts" / "linker_once.py"
PROGRAM_IMPORT = ROOT / "skills" / "devad-x9-loop" / "scripts" / "program_import.py"
SNAPSHOT_CAPACITY = ROOT / "skills" / "devad-x9-loop" / "scripts" / "snapshot_capacity.py"


def load_loopctl():
    name = "loopctl_v7_controller_under_test"
    spec = importlib.util.spec_from_file_location(name, LOOPCTL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {LOOPCTL}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_linker_once():
    name = "linker_once_v7_controller_under_test"
    spec = importlib.util.spec_from_file_location(name, LINKER_ONCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {LINKER_ONCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_program_import():
    name = "program_import_v7_controller_under_test"
    spec = importlib.util.spec_from_file_location(name, PROGRAM_IMPORT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PROGRAM_IMPORT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_snapshot_capacity():
    name = "snapshot_capacity_v7_controller_under_test"
    spec = importlib.util.spec_from_file_location(name, SNAPSHOT_CAPACITY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SNAPSHOT_CAPACITY}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        [*args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if result.returncode:
        raise AssertionError(f"command failed: {args}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def git_repo(path: Path) -> str:
    path.mkdir(parents=True)
    run("git", "init", "-b", "main", cwd=path)
    run("git", "config", "user.name", "X9 V7 Test", cwd=path)
    run("git", "config", "user.email", "x9-v7@example.invalid", cwd=path)
    (path / "src").mkdir()
    (path / "src" / "a.py").write_text("A = 1\n", encoding="utf-8")
    (path / "import-source").mkdir()
    (path / "import-source" / "feature.md").write_text("feature a\n", encoding="utf-8")
    run("git", "add", "src/a.py", "import-source/feature.md", cwd=path)
    run("git", "commit", "-m", "fixture", cwd=path)
    return run("git", "rev-parse", "HEAD", cwd=path)


V1_TABLES = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE actors (actor_id TEXT PRIMARY KEY, role TEXT NOT NULL, title TEXT NOT NULL, model TEXT NOT NULL);
CREATE TABLE worktrees (worktree_id TEXT PRIMARY KEY, path TEXT NOT NULL, repository_id TEXT NOT NULL);
CREATE TABLE tasks (task_id TEXT PRIMARY KEY, worker_id TEXT NOT NULL REFERENCES actors(actor_id), worktree_id TEXT NOT NULL REFERENCES worktrees(worktree_id), base_sha TEXT NOT NULL, owner_packet_path TEXT NOT NULL, owner_packet_sha256 TEXT NOT NULL, dependencies TEXT NOT NULL, finish_line TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE claims (task_id TEXT NOT NULL REFERENCES tasks(task_id), path TEXT NOT NULL, kind TEXT NOT NULL, PRIMARY KEY(task_id,path));
CREATE TABLE resources (task_id TEXT NOT NULL REFERENCES tasks(task_id), resource TEXT NOT NULL, PRIMARY KEY(task_id,resource));
CREATE TABLE dispatches (dispatch_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id), sender_id TEXT NOT NULL REFERENCES actors(actor_id), target_id TEXT NOT NULL REFERENCES actors(actor_id), packet_sha256 TEXT NOT NULL, packet TEXT NOT NULL, supersedes TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE deliveries (id INTEGER PRIMARY KEY AUTOINCREMENT, dispatch_id TEXT NOT NULL REFERENCES dispatches(dispatch_id), phase TEXT NOT NULL, method TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE events (event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id), dispatch_id TEXT NOT NULL REFERENCES dispatches(dispatch_id), event_sha256 TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE gates (task_id TEXT NOT NULL REFERENCES tasks(task_id), name TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL, PRIMARY KEY(task_id,name));
CREATE TABLE outbox (dispatch_id TEXT PRIMARY KEY REFERENCES dispatches(dispatch_id), payload TEXT NOT NULL);
CREATE TABLE metrics (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def write_v1_state(repo: Path, base_sha: str, *, active_legacy: bool = False) -> dict[str, bytes]:
    root = repo / ".devad" / "manager" / "loop-lite"
    root.mkdir(parents=True)
    db = root / "loop.db"
    connection = sqlite3.connect(db)
    connection.executescript(V1_TABLES)
    connection.execute("INSERT INTO meta VALUES('generation','7')")
    connection.execute("INSERT INTO actors VALUES('linx','LINX','AI - LINX v6','Unknown')")
    connection.execute("INSERT INTO actors VALUES('worker','WORKER','AI - WORKER','Unknown')")
    connection.execute("INSERT INTO worktrees VALUES('core-x9',?, 'core')", (str(repo),))
    connection.execute("INSERT INTO worktrees VALUES('core-legacy',?, 'core')", (str(repo.parent / 'missing-core'),))
    if active_legacy:
        connection.execute(
            "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?)",
            ('active-legacy','worker','core-legacy',base_sha,'owner.json','0' * 64,'[]','done','REGISTERED'),
        )
        connection.execute("INSERT INTO claims VALUES('active-legacy','src/a.py','file')")
        connection.execute("INSERT INTO resources VALUES('active-legacy','integration:default')")
    connection.commit()
    connection.close()
    tables = {
        'actors': [
            {'actor_id': 'linx', 'role': 'LINX', 'title': 'AI - LINX v6', 'model': 'Unknown'},
        ],
        'worktrees': [],
        'tasks': [],
        'claims': [],
        'resources': [],
        'dispatches': [],
        'deliveries': [],
        'events': [],
        'gates': [],
        'outbox': [],
        'metrics': [],
    }
    if active_legacy:
        tables['actors'].append(
            {'actor_id': 'worker', 'role': 'WORKER', 'title': 'AI - WORKER', 'model': 'Unknown'}
        )
        tables['worktrees'].append(
            {
                'worktree_id': 'core-legacy',
                'path': str(repo.parent / 'missing-core'),
                'repository_id': 'core',
            }
        )
        tables['tasks'].append(
            {
                'task_id': 'active-legacy',
                'worker_id': 'worker',
                'worktree_id': 'core-legacy',
                'base_sha': base_sha,
                'owner_packet_path': 'owner.json',
                'owner_packet_sha256': '0' * 64,
                'dependencies': '[]',
                'finish_line': 'done',
                'status': 'REGISTERED',
            }
        )
        tables['claims'].append(
            {'task_id': 'active-legacy', 'path': 'src/a.py', 'kind': 'file'}
        )
        tables['resources'].append(
            {'task_id': 'active-legacy', 'resource': 'integration:default'}
        )
    snapshot = {
        'schema': 'x9-loop-lite-snapshot-v1',
        'generation': 7,
        'recovery_worktrees': [
            {'worktree_id': 'core-legacy', 'path': str(repo.parent / 'missing-core')},
            {'worktree_id': 'core-x9', 'path': str(repo)},
        ],
        'dispatch_attempts': {},
        'completed_task_ids': [],
        'tables': tables,
    }
    snapshot_path = root / "SNAPSHOT.json"
    snapshot_path.write_text(json.dumps(snapshot, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return {'loop.db': db.read_bytes(), 'SNAPSHOT.json': snapshot_path.read_bytes()}


class V7ControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loopctl = load_loopctl()

    def setUp(self):
        temp_parent = Path(
            os.environ.get("X9_TEST_TEMP_ROOT", tempfile.gettempdir())
        )
        temp_parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="x9v7-", dir=temp_parent)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.base_sha = git_repo(self.repo)

    def controller(self):
        return self.loopctl.Controller(self.repo, now_fn=lambda: "2026-07-14T12:00:00Z")

    def _decode_v3_snapshot(self, controller):
        capacity = load_snapshot_capacity()
        raw = controller.snapshot_path.read_bytes()
        snapshot = json.loads(raw)

        def read_reference(relative):
            return (self.repo / Path(*PurePosixPath(relative).parts)).read_bytes()

        def list_generation_shards(generation):
            root = (
                controller.root
                / "snapshots"
                / "generations"
                / str(generation)
                / "shards"
            )
            if not root.is_dir():
                return set()
            return {
                path.relative_to(self.repo).as_posix()
                for path in root.iterdir()
                if path.is_file()
            }

        return capacity.decode_v3(
            snapshot=snapshot,
            snapshot_raw=raw,
            columns=self.loopctl.SNAPSHOT_COLUMNS,
            read_reference=read_reference,
            list_generation_shards=list_generation_shards,
        )

    def test_fresh_state_is_snapshot_and_sqlite_v3(self):
        controller = self.controller()
        controller.init()
        snapshot = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual("x9-loop-lite-snapshot-v3", snapshot["schema"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(3, connection.execute("PRAGMA user_version").fetchone()[0])
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            connection.close()
        self.assertTrue(
            {
                "call_receipts",
                "inbox",
                "programs",
                "work_orders",
                "worktree_classifications",
            }.issubset(tables)
        )

    def test_snapshot_roundtrip_preserves_pending_inbox(self):
        controller = self.controller()
        controller.init()
        envelope = {
            "event_id": "evt-pending-inbox",
            "event_type": "WORKER_RESULT",
            "payload_ref": {
                "path": "runtime/inbox/worker-result.json",
                "sha256": "a" * 64,
            },
            "project_profile_id": "profile-test",
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": "worker-a",
            "source_role": "WORKER",
        }
        raw = self.loopctl._load_v7_contract().canonical_json_bytes(envelope)

        def add_pending(connection):
            connection.execute(
                "INSERT INTO inbox VALUES(?,?,?,?,?,?,?)",
                (
                    envelope["event_id"],
                    "task-a",
                    "dsp-a",
                    hashlib.sha256(raw).hexdigest(),
                    raw.decode("utf-8").rstrip("\n"),
                    "PENDING",
                    "2026-07-14T12:00:00Z",
                ),
            )

        controller._mutate(add_pending)
        decoded = self._decode_v3_snapshot(controller)
        self.assertEqual("PENDING", decoded["tables"]["inbox"][0]["status"])
        self.assertEqual("PASS", controller.rebuild()["status"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("evt-pending-inbox", "PENDING"),
                connection.execute("SELECT event_id,status FROM inbox").fetchone(),
            )
        finally:
            connection.close()

    def test_v1_migration_is_side_by_side_validated_and_exactly_rollback_safe(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        result = controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        self.assertEqual("PASS", result["status"])
        self.assertEqual(hashlib.sha256(original["SNAPSHOT.json"]).hexdigest(), result["source_snapshot_sha256"])
        self.assertEqual(8, result["migration_generation"])
        next_artifacts = [
            Path(str(controller.db_path) + suffix)
            for suffix in (".next", ".next-wal", ".next-shm")
        ] + [Path(str(controller.snapshot_path) + ".next")]
        self.assertFalse(any(path.exists() for path in next_artifacts))
        migrated_git = controller._git_state(self.base_sha, self.repo)
        self.assertFalse(
            any(
                ".next" in path
                for paths in migrated_git.values()
                for path in controller._scope_paths(paths)
            )
        )
        snapshot = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual("x9-loop-lite-snapshot-v3", snapshot["schema"])
        self.assertEqual(8, snapshot["generation"])
        connection = sqlite3.connect(controller.db_path)
        try:
            classification = connection.execute(
                "SELECT classification,owner_decision_sha256 FROM worktree_classifications WHERE worktree_id='core-legacy'"
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(("HISTORICAL_MISSING", "a" * 64), classification)
        for path in next_artifacts[1:3]:
            path.write_bytes(b"disposable-v7-sidecar")
        self.assertTrue(all(path.exists() for path in next_artifacts[1:3]))
        rollback = controller.rollback_to_v6(result["recovery_id"])
        self.assertEqual("PASS", rollback["status"])
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(original["SNAPSHOT.json"], controller.snapshot_path.read_bytes())
        self.assertFalse(any(path.exists() for path in next_artifacts))
        rollback_git = controller._git_state(self.base_sha, self.repo)
        self.assertFalse(
            any(
                ".next" in path
                for paths in rollback_git.values()
                for path in controller._scope_paths(paths)
            )
        )

    def test_v1_retry_after_rollback_archives_conflicting_generation_shards(self):
        repo = self.repo
        write_v1_state(repo, self.base_sha)
        controller = self.controller()
        first = controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        self.assertEqual("PASS", first["status"])
        first_root = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual("x9-loop-lite-snapshot-v3", first_root["schema"])
        first_shards = {
            reference["path"]: (
                repo / Path(*PurePosixPath(reference["path"]).parts)
            ).read_bytes()
            for reference in first_root["terminal_shards"]
        }
        self.assertEqual("PASS", controller.rollback_to_v6(first["recovery_id"])["status"])

        second = controller.migrate_v1_to_v2({"core-legacy": "b" * 64})
        self.assertEqual("PASS", second["status"])
        second_root = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(8, second_root["generation"])
        active_paths = {
            reference["path"] for reference in second_root["terminal_shards"]
        }
        self.assertEqual(active_paths, controller._list_generation_shards(8))
        connection = controller._connect()
        try:
            self.assertEqual(
                ("HISTORICAL_MISSING", "b" * 64),
                tuple(
                    connection.execute(
                        "SELECT classification,owner_decision_sha256 "
                        "FROM worktree_classifications WHERE worktree_id='core-legacy'"
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

        active_directory = (
            controller.root / "snapshots" / "generations" / "8" / "shards"
        ).resolve()
        for relative, raw in first_shards.items():
            digest_name = PurePosixPath(relative).name
            preserved = []
            for candidate in list(controller.root.rglob(digest_name)):
                if active_directory in candidate.resolve().parents:
                    continue
                self.assertTrue(candidate.is_file(), candidate)
                if candidate.read_bytes() == raw:
                    preserved.append(candidate)
            self.assertTrue(preserved, digest_name)
    def test_v1_schema_semantics_reject_missing_composite_primary_key(self):
        malformed = V1_TABLES.replace(
            "CREATE TABLE claims (task_id TEXT NOT NULL REFERENCES tasks(task_id), path TEXT NOT NULL, kind TEXT NOT NULL, PRIMARY KEY(task_id,path));",
            "CREATE TABLE claims (task_id TEXT NOT NULL REFERENCES tasks(task_id), path TEXT NOT NULL, kind TEXT NOT NULL);",
        )
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        try:
            connection.executescript(malformed)
            with self.assertRaisesRegex(
                self.loopctl.StateNotDurableError, "V6_DATABASE_INVALID"
            ):
                self.loopctl.Controller._validate_v1_schema_shape(connection)
        finally:
            connection.close()
    def test_missing_active_worktree_is_fatal_even_with_owner_hash(self):
        original = write_v1_state(self.repo, self.base_sha, active_legacy=True)
        controller = self.controller()
        with self.assertRaisesRegex(self.loopctl.StateNotDurableError, "ACTIVE_WORKTREE_MISSING:core-legacy"):
            controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(original["SNAPSHOT.json"], controller.snapshot_path.read_bytes())

    def _register_v7_actors(self, controller):
        controller.register_actor("linx", "LINX", "AI - LINX v6", "Unknown")
        controller.register_actor("worker", "WORKER", "AI - WORKER", "Unknown")
        controller.register_worktree("core-x9", self.repo, "core")

    def _import_program(self, controller, program):
        descriptor = dict(program)
        descriptor.setdefault(
            "feature_packets",
            [self._feature(feature_id) for feature_id in descriptor["features"]],
        )
        metadata = {
            "feature.md": {"feature_ids": list(descriptor["features"])}
        }
        artifacts = load_program_import().build_import_artifacts(
            self.repo / "import-source", metadata_by_path=metadata
        )
        return controller.import_program(
            descriptor,
            source_git_sha=self.base_sha,
            source_root=self.repo / "import-source",
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )

    def _doctor_with_inventory(self, controller, inventory):
        original = controller._inventory_scheduled_jobs
        controller._inventory_scheduled_jobs = lambda *_args, **_kwargs: inventory
        try:
            return controller.doctor()
        finally:
            controller._inventory_scheduled_jobs = original

    def _feature(self, feature_id: str) -> dict[str, object]:
        return {
            "schema": "x9-loop-feature-v1",
            "owner_requirement": "implement the selected bounded feature",
            "attachment_hashes": [],
            "feature_id": feature_id,
            "subfeature_ids": [],
            "accepted": [], "rejected": [], "paused": [], "unknown": [], "out_of_scope": [],
            "source_references": [], "implementation_evidence": [],
            "worktree_id": "core-x9", "worktree_path": str(self.repo), "branch": "main",
            "base_sha": self.base_sha, "local_work": {},
            "claims": [{"path": "src/a.py", "kind": "file"}],
            "resources": ["integration:default"], "dependencies": [],
            "known_decisions": [], "tool_lessons": [], "prior_failed_attempts": [],
            "finish_line": "bounded proof passes", "tests": ["unit"], "security_checks": ["secret scan"],
            "commit_rules": ["C1 then C2"], "deploy_gate": "none", "browser_acceptance": "none",
            "allowed_autonomy": ["local edits"], "owner_decision_boundaries": ["external state"],
            "worker_id": "worker",
        }

    def _stop(self):
        return {
            "schema": "x9-loop-stop-contract-v1", "success_predicate": "proof passes",
            "max_attempts": 3, "max_wall_seconds": 3600, "max_model_calls": 10, "max_tokens": None,
        }

    def test_controller_creates_immutable_order_and_minimal_action_transactionally(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        program = {"schema": "x9-loop-program-v1", "program_id": "program-a", "features": ["feature-a", "feature-b"]}
        imported = self._import_program(controller, program)
        first = controller.create_work_order(
            program_id="program-a", stop=self._stop(),
            linx_id="linx", action_class="implementation",
        )
        self.assertEqual("CREATED", first["status"])
        raw = (self.repo / first["work_order_path"]).read_bytes()
        self.assertEqual(first["work_order_sha256"], hashlib.sha256(raw).hexdigest())
        action = json.loads(controller.action_path.read_text(encoding="utf-8"))
        self.assertEqual("x9-loop-action-v2", action["schema"])
        self.assertEqual("SEND_WORK_ORDER", action["action"])
        self.assertTrue(action["must_record_transport"])
        self.assertNotIn("packet", action)
        self.assertLessEqual(len(controller.action_path.read_bytes()), 4 * 1024)
        reused = controller.create_work_order(
            program_id="program-a", stop=self._stop(),
            linx_id="linx", action_class="implementation",
        )
        self.assertEqual("ACTIVE_WORK_ORDER_REUSED", reused["status"])
        self.assertEqual(first["work_order_id"], reused["work_order_id"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(1, connection.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0])
        finally:
            connection.close()
        controller._transition_task_state(first["task_id"], "COMPLETE")
        second = controller.create_work_order(
            program_id="program-a", stop=self._stop(),
            linx_id="linx", action_class="implementation",
        )
        self.assertEqual("CREATED", second["status"])

    def test_active_work_order_resource_keys_are_canonical_without_packet_rewrite(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        resource = "Dokploy-Application-DrW76PN2WwBGybgUPKkOe"
        feature = self._feature("feature-a")
        feature["resources"] = [resource]
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-mixed-resource",
                "features": ["feature-a"],
                "feature_packets": [feature],
            },
        )
        order = controller.create_work_order(
            program_id="program-mixed-resource",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        packet_path = self.repo / order["work_order_path"]
        original = packet_path.read_bytes()

        self.assertEqual(order["work_order_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(order["work_order_id"], controller.verify_work_order(order["work_order_id"])["work_order_id"])
        available = {
            "jobs": [],
            "providers": {"codex": "AVAILABLE", "windows-task-scheduler": "AVAILABLE"},
        }
        doctor = self._doctor_with_inventory(controller, available)
        self.assertEqual("PASS", doctor["status"])
        self.assertEqual([], doctor["checks"]["work_orders"])
        connection = controller._connect()
        try:
            self.assertEqual(
                [(resource.casefold(),)],
                [tuple(row) for row in connection.execute("SELECT resource FROM resources")],
            )
        finally:
            connection.close()
        self.assertEqual(original, packet_path.read_bytes())

        def substitute_resource(connection):
            connection.execute(
                "UPDATE resources SET resource='different-resource' WHERE task_id=?",
                (order["task_id"],),
            )

        controller._mutate(substitute_resource)
        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "WORK_ORDER_DRIFT:resources"
        ):
            controller.verify_work_order(order["work_order_id"])
        self.assertEqual(original, packet_path.read_bytes())

    def test_register_task_rejects_casefold_resource_collision_zero_delta(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        connection = controller._connect()
        try:
            before = tuple(
                connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("tasks", "resources")
            )
        finally:
            connection.close()

        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "TASK_RESOURCES_INVALID"
        ):
            controller.register_task(
                "legacy-resource-casefold-collision",
                "worker",
                "core-x9",
                self.base_sha,
                [{"path": "src/legacy-resource.py", "kind": "file"}],
                ["Resource-A", "resource-a"],
                [],
                "legacy resource validation",
                owner_packet_path="owner.json",
                owner_packet_sha256="0" * 64,
            )

        connection = controller._connect()
        try:
            after = tuple(
                connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("tasks", "resources")
            )
        finally:
            connection.close()
        self.assertEqual(before, after)

    def test_active_resource_conflict_uses_canonical_resource_key(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        resource = "Dokploy-Postgres-2SJ-Jaw6opsfZcwHAKspe"
        first_feature = self._feature("feature-a")
        first_feature["resources"] = [resource]
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-first-resource",
                "features": ["feature-a"],
                "feature_packets": [first_feature],
            },
        )
        controller.create_work_order(
            program_id="program-first-resource",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        controller.register_actor("worker-2", "WORKER", "AI - WORKER 2", "Unknown")
        controller.register_worktree("core-x9-2", self.repo, "core")
        second_feature = self._feature("feature-b")
        second_feature.update(
            {
                "claims": [{"path": "src/b.py", "kind": "file"}],
                "resources": [resource.casefold()],
                "worker_id": "worker-2",
                "worktree_id": "core-x9-2",
            }
        )
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-second-resource",
                "features": ["feature-b"],
                "feature_packets": [second_feature],
            },
        )
        with self.assertRaisesRegex(
            self.loopctl.ResourceConflictError, "RESOURCE_CONFLICT"
        ):
            controller.create_work_order(
                program_id="program-second-resource",
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )

    def test_snapshot_omits_recoverable_default_receipt_metrics_under_active_order_cap(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-a",
                "features": ["feature-a"],
            },
        )
        default_root = self.loopctl._sha([])
        def add_metrics(connection):
            for index in range(60):
                scope = f"default-{index:02d}"
                connection.executemany(
                    "INSERT INTO metrics(key,value) VALUES(?,?)",
                    (
                        (f"historical-receipts:{scope}", "{}"),
                        (f"receipt-count:{scope}", "0"),
                        (f"receipt-root:{scope}", default_root),
                    ),
                )
            connection.executemany(
                "INSERT INTO metrics(key,value) VALUES(?,?)",
                (
                    ("historical-receipts:nondefault", '{"receipt.json":"' + "a" * 64 + '"}'),
                    ("receipt-count:nondefault", "1"),
                    ("receipt-root:nondefault", "b" * 64),
                ),
            )

        controller._mutate(add_metrics)

        order = controller.create_work_order(
            program_id="program-a",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        self.assertEqual("CREATED", order["status"])
        snapshot = self._decode_v3_snapshot(controller)
        metric_keys = {row["key"] for row in snapshot["tables"]["metrics"]}
        self.assertFalse(any("default-" in key for key in metric_keys))
        self.assertTrue(
            {
                "historical-receipts:nondefault",
                "receipt-count:nondefault",
                "receipt-root:nondefault",
            }.issubset(metric_keys)
        )
        self.assertLessEqual(controller.snapshot_path.stat().st_size, 8192)

        controller.rebuild()
        rebuilt = controller._connect()
        try:
            self.assertEqual(
                0,
                rebuilt.execute(
                    "SELECT COUNT(*) FROM metrics WHERE key LIKE '%:default-%'"
                ).fetchone()[0],
            )
            self.assertEqual(
                3,
                rebuilt.execute(
                    "SELECT COUNT(*) FROM metrics WHERE key LIKE '%:nondefault'"
                ).fetchone()[0],
            )
        finally:
            rebuilt.close()

    def test_v3_capacity_supports_current_registry_and_three_active_orders(self):
        controller = self.controller()
        controller.init()
        controller.register_actor("linx", "LINX", "AI - LINX v7", "Unknown")
        for index in range(4):
            controller.register_actor(
                f"worker-{index}", "WORKER", f"AI - WORKER {index}", "Unknown"
            )
        for index in range(18):
            controller.register_worktree(f"core-{index:02d}", self.repo, "core")

        for index in range(4):
            feature = self._feature(f"feature-{index}")
            feature.update(
                {
                    "claims": [{"path": f"src/slot-{index}.py", "kind": "file"}],
                    "resources": [f"integration:slot-{index}"],
                    "worker_id": f"worker-{index}",
                    "worktree_id": f"core-{index:02d}",
                }
            )
            self._import_program(
                controller,
                {
                    "schema": "x9-loop-program-v1",
                    "program_id": f"program-{index}",
                    "features": [f"feature-{index}"],
                    "feature_packets": [feature],
                },
            )

        orders = [
            controller.create_work_order(
                program_id=f"program-{index}",
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )
            for index in range(3)
        ]
        self.assertTrue(all(order["status"] == "CREATED" for order in orders))
        self.assertLessEqual(controller.snapshot_path.stat().st_size, 8192)
        decoded = self._decode_v3_snapshot(controller)
        self.assertEqual(18, len(decoded["tables"]["worktrees"]))
        self.assertEqual(4, len(decoded["tables"]["programs"]))
        self.assertEqual(3, len(decoded["tables"]["work_orders"]))

        before_action = controller.action_path.read_bytes()
        before_files = sorted(
            path.relative_to(self.repo).as_posix()
            for path in (controller.root / "runtime" / "work-orders").glob(
                "*/WORK_ORDER.json"
            )
        )
        with self.assertRaisesRegex(
            self.loopctl.TaskNotReadyError, "ACTIVE_ORDER_CAPACITY"
        ):
            controller.create_work_order(
                program_id="program-3",
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )
        self.assertEqual(before_action, controller.action_path.read_bytes())
        self.assertEqual(
            before_files,
            sorted(
                path.relative_to(self.repo).as_posix()
                for path in (controller.root / "runtime" / "work-orders").glob(
                    "*/WORK_ORDER.json"
                )
            ),
        )

        self.assertEqual("PASS", controller.rebuild()["status"])
        connection = controller._connect()
        try:
            self.assertEqual(18, connection.execute("SELECT COUNT(*) FROM worktrees").fetchone()[0])
            self.assertEqual(4, connection.execute("SELECT COUNT(*) FROM programs").fetchone()[0])
            self.assertEqual(3, connection.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0])
        finally:
            connection.close()

    def test_realistic_brand_order_and_two_reservations_fit_root_cap(self):
        capacity = load_snapshot_capacity()
        controller = self.controller()
        controller.init()
        linx_id = "019f61ba-2f9e-77c1-839b-cb8eb472f818"
        worker_id = "019f2ad8-c1f7-73e1-9454-7a6c020f2fd2"
        controller.register_actor(
            linx_id, "LINX", "Devad X9 Loop Pro", "gpt-5.6-sol high"
        )
        controller.register_actor(
            worker_id, "WORKER", "POST Brand Voice Worker", "Unknown"
        )
        controller.register_worktree("x9w-pbvri", self.repo, "recovery")
        claim_paths = [
            "app/Ai/Blog/AiBlogScrapingSidecarClient.php",
            "app/Ai/Blog/AiBlogSourceResolver.php",
            "app/Ai/Services/AiContentTaskRepository.php",
            "app/Http/Controllers/Ai/AiTaskSourceResearchController.php",
            "app/Services/PlanLimitService.php",
            "config/billing.php",
            "resources/js/pages/ai/components/AgenticWorkflowBuilder.tsx",
            "resources/js/pages/ai/components/ArticleRowsSpreadsheet.tsx",
            "resources/js/pages/ai/components/TaskWorkspaceModal.tsx",
            "resources/js/pages/ai/hooks/useArticleRowGrid.ts",
            "resources/js/pages/ai/spreadsheet-import.ts",
            "resources/js/pages/ai/types.ts",
            "routes/web.php",
            "tests/Feature/Ai/AiBlogSourceResearchTest.php",
            "tests/Feature/Ai/AiBlogWorkflowRunTest.php",
            "tests/Feature/Ai/AiSpreadsheetPersistenceTest.php",
        ]
        resources = [
            "ai-blog-source-mode-research",
            "ai-blog-spreadsheet-import",
            "worktree:x9w-pbvri",
        ]
        feature = self._feature("brand-source-mode-implementation")
        feature.update(
            {
                "claims": [
                    {"path": path, "kind": "file"} for path in claim_paths
                ],
                "finish_line": (
                    "Focused backend, workflow, parser max/max+1, type/build, "
                    "security precommit, and local real Chrome desktop/mobile "
                    "proof pass; workflow consumes the same canonical "
                    "source_type/n8n_input_picker mapping; no forbidden side "
                    "effect occurs; Worker returns a canonical honest PASS or "
                    "PARTIAL result with change map and rollback."
                ),
                "resources": resources,
                "worker_id": worker_id,
                "worktree_id": "x9w-pbvri",
            }
        )
        program_id = "brand-source-mode-implementation-20260715-1"
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": program_id,
                "features": [feature["feature_id"]],
                "feature_packets": [feature],
            },
        )
        stop = {
            "schema": "x9-loop-stop-contract-v1",
            "success_predicate": "proof passes",
            "max_attempts": 3,
            "max_wall_seconds": 10800,
            "max_model_calls": 18,
            "max_tokens": None,
        }
        observed = {}
        original_admit = controller._admit_active_order_capacity

        def measure_admission(connection, baseline_root_size):
            active_count = connection.execute(
                "SELECT COUNT(*) FROM work_orders wo "
                "JOIN tasks t ON t.task_id=wo.task_id "
                "WHERE t.status NOT IN ('COMPLETE','SUPERSEDED') "
                "AND wo.status NOT IN ('COMPLETE','EXPIRED','SUPERSEDED')"
            ).fetchone()[0]
            root_bytes = len(
                controller._snapshot_bundle(
                    connection,
                    generation=controller._generation(connection) + 1,
                )["root_raw"]
            )
            reservation_bytes = (
                capacity.ACTIVE_ORDER_CAP - active_count
            ) * capacity.ACTIVE_ORDER_RESERVATION_BYTES
            observed.update(
                {
                    "baseline_root_bytes": baseline_root_size,
                    "canonical_root_bytes": root_bytes,
                    "reservation_bytes": reservation_bytes,
                    "root_plus_reservation_bytes": root_bytes
                    + reservation_bytes,
                }
            )
            return original_admit(connection, baseline_root_size)

        controller._admit_active_order_capacity = measure_admission
        try:
            try:
                created = controller.create_work_order(
                    program_id=program_id,
                    stop=stop,
                    linx_id=linx_id,
                    action_class="Brand",
                )
            except self.loopctl.TaskNotReadyError as exc:
                self.fail(f"{exc}; {observed}")
        finally:
            controller._admit_active_order_capacity = original_admit

        self.assertEqual("CREATED", created["status"])
        root_raw = controller.snapshot_path.read_bytes()
        self.assertEqual(capacity.canonical_bytes(json.loads(root_raw)), root_raw)
        self.assertEqual(len(root_raw), observed["canonical_root_bytes"])
        self.assertEqual(
            2 * capacity.ACTIVE_ORDER_RESERVATION_BYTES,
            observed["reservation_bytes"],
        )
        self.assertLessEqual(
            observed["root_plus_reservation_bytes"], capacity.ROOT_CAP_BYTES
        )
    def test_live_brand_order_fits_and_preserves_remaining_active_capacity(self):
        capacity = load_snapshot_capacity()
        self.assertEqual(3, capacity.ACTIVE_ORDER_CAP)
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        brand_claim_paths = [
            "app/Ai/Blog/AiBlogScrapingSidecarClient.php",
            "app/Ai/Blog/AiBlogSourceResolver.php",
            "app/Ai/Services/AiContentTaskRepository.php",
            "app/Http/Controllers/Ai/AiTaskSourceResearchController.php",
            "app/Services/PlanLimitService.php",
            "config/billing.php",
            "resources/js/pages/ai/components/AgenticWorkflowBuilder.tsx",
            "resources/js/pages/ai/components/ArticleRowsSpreadsheet.tsx",
            "resources/js/pages/ai/components/TaskWorkspaceModal.tsx",
            "resources/js/pages/ai/hooks/useArticleRowGrid.ts",
            "resources/js/pages/ai/spreadsheet-import.ts",
            "resources/js/pages/ai/types.ts",
            "routes/web.php",
            "tests/Feature/Ai/AiBlogSourceResearchTest.php",
            "tests/Feature/Ai/AiBlogWorkflowRunTest.php",
            "tests/Feature/Ai/AiSpreadsheetPersistenceTest.php",
        ]
        brand_resources = [
            "ai-blog-source-mode-research",
            "ai-blog-spreadsheet-import",
            "worktree:x9w-pbvri",
        ]
        feature = self._feature("brand-source-mode-implementation")
        feature.update(
            {
                "claims": [
                    {"path": path, "kind": "file"}
                    for path in brand_claim_paths
                ],
                "resources": brand_resources,
            }
        )
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "brand-source-mode-implementation-20260715-1",
                "features": [feature["feature_id"]],
                "feature_packets": [feature],
            },
        )
        self.assertLessEqual(controller.snapshot_path.stat().st_size, 1400)

        created = controller.create_work_order(
            program_id="brand-source-mode-implementation-20260715-1",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        self.assertEqual("CREATED", created["status"])
        root_size = controller.snapshot_path.stat().st_size
        self.assertLessEqual(root_size, capacity.ROOT_CAP_BYTES)
        self.assertLessEqual(
            root_size
            + (capacity.ACTIVE_ORDER_CAP - 1)
            * capacity.ACTIVE_ORDER_RESERVATION_BYTES,
            capacity.ROOT_CAP_BYTES,
        )

        decoded = self._decode_v3_snapshot(controller)
        self.assertEqual(
            sorted((path, "file") for path in brand_claim_paths),
            sorted(
                (row["path"], row["kind"])
                for row in decoded["tables"]["claims"]
            ),
        )
        self.assertEqual(
            sorted(brand_resources),
            sorted(row["resource"] for row in decoded["tables"]["resources"]),
        )

        original_root_raw = controller.snapshot_path.read_bytes()
        original_root = json.loads(original_root_raw)
        active_reference = original_root["active_shards"][0]
        active_path = self.repo / Path(
            *PurePosixPath(active_reference["path"]).parts
        )
        active_raw = active_path.read_bytes()
        try:
            active_path.write_bytes(b"{}\n")
            with self.assertRaisesRegex(
                self.loopctl.SnapshotExportError,
                "SNAPSHOT_SHARD_HASH_MISMATCH",
            ):
                controller._decode_snapshot(original_root_raw)
        finally:
            active_path.write_bytes(active_raw)

        forged_root = json.loads(original_root_raw)
        claims_summary = next(
            item
            for item in forged_root["active_detail_summaries"]["counts"]
            if item[0] == "claims"
        )
        claims_summary[1] += 1
        with self.assertRaisesRegex(
            capacity.SnapshotCapacityError,
            "SNAPSHOT_ACTIVE_DETAIL_INVALID",
        ):
            capacity.decode_v3(
                snapshot=forged_root,
                snapshot_raw=capacity.canonical_bytes(forged_root),
                columns=self.loopctl.SNAPSHOT_COLUMNS,
                read_reference=lambda relative: (
                    self.repo / Path(*PurePosixPath(relative).parts)
                ).read_bytes(),
                list_generation_shards=controller._list_generation_shards,
            )
        self.assertEqual("PASS", controller.rebuild()["status"])
        connection = controller._connect()
        try:
            self.assertEqual(
                sorted((path, "file") for path in brand_claim_paths),
                sorted(
                    tuple(row)
                    for row in connection.execute(
                        "SELECT path,kind FROM claims WHERE task_id=?",
                        (created["task_id"],),
                    )
                ),
            )
            self.assertEqual(
                sorted(brand_resources),
                sorted(
                    row[0]
                    for row in connection.execute(
                        "SELECT resource FROM resources WHERE task_id=?",
                        (created["task_id"],),
                    )
                ),
            )
        finally:
            connection.close()
    def test_v2_rebuild_upgrades_to_v3_and_retains_exact_previous_root(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        decoded = self._decode_v3_snapshot(controller)
        capacity = load_snapshot_capacity()
        v2 = {
            "call_receipt_archive": decoded["call_receipt_archive"],
            "completed_task_ids": decoded["completed_task_ids"],
            "dispatch_attempts": decoded["dispatch_attempts"],
            "generation": decoded["generation"],
            "recovery_worktrees": decoded["recovery_worktrees"],
            "schema": "x9-loop-lite-snapshot-v2",
            "tables": {
                table: decoded["tables"][table]
                for table in self.loopctl.V2_SNAPSHOT_TABLES
            },
        }
        v2_raw = capacity.canonical_bytes(v2)
        controller.snapshot_path.write_bytes(v2_raw)

        rebuilt = controller.rebuild()
        self.assertEqual("PASS", rebuilt["status"])

        root_raw = controller.snapshot_path.read_bytes()
        root = json.loads(root_raw)
        self.assertEqual("x9-loop-lite-snapshot-v3", root["schema"])
        previous = root["previous_generation"]
        self.assertEqual("x9-loop-lite-snapshot-v2", previous["schema"])
        self.assertEqual(hashlib.sha256(v2_raw).hexdigest(), previous["sha256"])
        previous_path = self.repo / Path(*PurePosixPath(previous["path"]).parts)
        self.assertEqual(v2_raw, previous_path.read_bytes())
        self.assertEqual(decoded["tables"], self._decode_v3_snapshot(controller)["tables"])

        self.assertEqual("PASS", controller.rebuild()["status"])
        again = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(previous, again["previous_generation"])
        self.assertEqual(v2_raw, previous_path.read_bytes())

        def reject_previous(document, raw):
            mutated = json.loads(json.dumps(again))
            digest = hashlib.sha256(raw).hexdigest()
            relative = (
                ".devad/manager/loop-lite/snapshots/roots/"
                f"{digest}.json"
            )
            mutated["previous_generation"] = {
                "byte_size": len(raw),
                "generation": document["generation"],
                "path": relative,
                "schema": document["schema"],
                "sha256": digest,
            }
            shard_paths = {
                reference["path"] for reference in mutated["terminal_shards"]
            }
            with self.assertRaisesRegex(
                capacity.SnapshotCapacityError, "SNAPSHOT_PREVIOUS_INVALID"
            ):
                capacity.decode_v3(
                    snapshot=mutated,
                    snapshot_raw=capacity.canonical_bytes(mutated),
                    columns=self.loopctl.SNAPSHOT_COLUMNS,
                    read_reference=lambda path: (
                        raw
                        if path == relative
                        else (
                            self.repo / Path(*PurePosixPath(path).parts)
                        ).read_bytes()
                    ),
                    list_generation_shards=lambda _generation: shard_paths,
                )

        noncanonical = json.dumps(v2, indent=2).encode("utf-8")
        reject_previous(v2, noncanonical)
        future_v2 = {**v2, "generation": again["generation"]}
        reject_previous(future_v2, capacity.canonical_bytes(future_v2))

    def test_v7_success_accepts_feature_bound_c2_outputs(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        attestation = ".devad/features/pro-bootstrap/VALIDATION.json"
        c1_outputs = ["src/a.py", "SOURCE_MANIFEST.sha256"]
        c2_outputs = [attestation, "SOURCE_MANIFEST.sha256"]
        feature = self._feature("feature-a")
        feature["claims"] = [
            {"path": ".devad/features/pro-bootstrap", "kind": "dir"},
            {"path": "SOURCE_MANIFEST.sha256", "kind": "file"},
            {"path": "src/a.py", "kind": "file"},
        ]
        feature["local_work"] = {
            "c1_outputs": c1_outputs,
            "c2_outputs": c2_outputs,
        }
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-a",
                "features": ["feature-a"],
                "feature_packets": [feature],
            },
        )
        order = controller.create_work_order(
            program_id="program-a", stop=self._stop(),
            linx_id="linx", action_class="implementation",
        )
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        (self.repo / "src/a.py").write_text("A = 2\n", encoding="utf-8")
        (self.repo / "SOURCE_MANIFEST.sha256").write_bytes(b"c1 manifest\n")
        run("git", "add", *c1_outputs, cwd=self.repo)
        run("git", "commit", "-m", "C1", cwd=self.repo)
        c1 = run("git", "rev-parse", "HEAD", cwd=self.repo)

        attestation_path = self.repo / Path(*PurePosixPath(attestation).parts)
        attestation_path.parent.mkdir(parents=True, exist_ok=True)
        (self.repo / ".git/info/attributes").write_text(
            f"{attestation} -text\n", encoding="utf-8"
        )
        attestation_path.write_bytes(
            (
                json.dumps({"c1": c1}, separators=(",", ":"), sort_keys=True)
                + "\r\n"
            ).encode("utf-8")
        )
        (self.repo / "SOURCE_MANIFEST.sha256").write_bytes(b"c2 manifest\n")
        run("git", "add", *c2_outputs, cwd=self.repo)
        run("git", "commit", "-m", "C2", cwd=self.repo)
        c2 = run("git", "rev-parse", "HEAD", cwd=self.repo)
        event = self._write_v7_worker_event(
            controller, order, changed_files=c1_outputs, outcome="SUCCESS",
            event_id="event-feature-bound-c2",
        )
        contract = self.loopctl._load_v7_contract()
        result_path = self.repo / Path(*PurePosixPath(event["result_path"]).parts)
        result = json.loads(result_path.read_bytes())
        result.update({"attestation_path": attestation, "c1": c1, "c2": c2})
        result_raw = contract.canonical_json_bytes(result)
        result_path.write_bytes(result_raw)
        event["result_sha256"] = hashlib.sha256(result_raw).hexdigest()

        self.assertEqual("FEATURE_DONE", controller.consume_event(event)["status"])

    def test_v7_changed_success_preserves_legacy_c2_attestation(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature = self._feature("feature-a")
        feature["local_work"] = []
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-a",
                "features": ["feature-a"],
                "feature_packets": [feature],
            },
        )
        order = controller.create_work_order(
            program_id="program-a", stop=self._stop(),
            linx_id="linx", action_class="implementation",
        )
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        (self.repo / "src/a.py").write_bytes(b"A = 2\n")
        run("git", "add", "src/a.py", cwd=self.repo)
        run("git", "commit", "-m", "C1", cwd=self.repo)
        c1 = run("git", "rev-parse", "HEAD", cwd=self.repo)

        attestation = f".devad/docs/commits/{c1}.md"
        attestation_path = self.repo / Path(*PurePosixPath(attestation).parts)
        attestation_path.parent.mkdir(parents=True, exist_ok=True)
        attestation_path.write_bytes(f"C1: {c1}\n".encode("utf-8"))
        run("git", "add", attestation, cwd=self.repo)
        run("git", "commit", "-m", "C2", cwd=self.repo)
        c2 = run("git", "rev-parse", "HEAD", cwd=self.repo)
        event = self._write_v7_worker_event(
            controller, order, changed_files=["src/a.py"], outcome="SUCCESS",
            event_id="event-legacy-c2",
        )
        contract = self.loopctl._load_v7_contract()
        result_path = self.repo / Path(*PurePosixPath(event["result_path"]).parts)
        result = json.loads(result_path.read_bytes())
        result.update({"attestation_path": attestation, "c1": c1, "c2": c2})
        result_raw = contract.canonical_json_bytes(result)
        result_path.write_bytes(result_raw)
        event["result_sha256"] = hashlib.sha256(result_raw).hexdigest()

        self.assertEqual("FEATURE_DONE", controller.consume_event(event)["status"])

    def test_v3_preserves_legacy_layouts_and_upgrades_on_new_generation(self):
        capacity = load_snapshot_capacity()
        controller = self.controller()
        self._create_order(controller)
        decoded = self._decode_v3_snapshot(controller)
        current_root = json.loads(controller.snapshot_path.read_bytes())

        def build(current_raw, generation=None):
            return capacity.build_bundle(
                generation=(
                    decoded["generation"] if generation is None else generation
                ),
                columns=self.loopctl.SNAPSHOT_COLUMNS,
                tables=decoded["tables"],
                recovery_worktrees=decoded["recovery_worktrees"],
                completed_task_ids=decoded["completed_task_ids"],
                dispatch_attempts=decoded["dispatch_attempts"],
                call_receipt_archive=decoded["call_receipt_archive"],
                current_snapshot_raw=current_raw,
            )

        def decode(bundle):
            shard_files = {
                item["reference"]["path"]: item["raw"]
                for item in bundle["shards"]
            }
            extra_files = dict(shard_files)
            if bundle["previous_archive"] is not None:
                path, raw = bundle["previous_archive"]
                extra_files[path] = raw

            def read_reference(path):
                if path in extra_files:
                    return extra_files[path]
                return (
                    self.repo / Path(*PurePosixPath(path).parts)
                ).read_bytes()

            return capacity.decode_v3(
                snapshot=bundle["root"],
                snapshot_raw=bundle["root_raw"],
                columns=self.loopctl.SNAPSHOT_COLUMNS,
                read_reference=read_reference,
                list_generation_shards=lambda _generation: set(shard_files),
            )

        def shard_bytes(bundle):
            return {
                item["reference"]["path"]: item["raw"]
                for item in bundle["shards"]
            }

        legacy_tables = json.loads(json.dumps(decoded["tables"]))
        legacy_tables["outbox"] = []
        inline_seed = json.loads(json.dumps(current_root))
        inline_seed.pop("active_layout")
        inline_seed.pop("active_detail_summaries")
        inline_seed.pop("active_shards")
        inline = build(capacity.canonical_bytes(inline_seed))
        self.assertNotIn("active_shards", inline["root"])
        self.assertEqual(legacy_tables, decode(inline)["tables"])
        inline_again = build(inline["root_raw"])
        self.assertEqual(inline["root_raw"], inline_again["root_raw"])
        self.assertEqual(shard_bytes(inline), shard_bytes(inline_again))

        legacy_seed = json.loads(json.dumps(current_root))
        legacy_seed.pop("active_layout")
        legacy = build(capacity.canonical_bytes(legacy_seed))
        self.assertNotIn("active_layout", legacy["root"])
        self.assertEqual(
            {"claims", "resources"},
            set(legacy["root"]["active_detail_summaries"]),
        )
        self.assertEqual(legacy_tables, decode(legacy)["tables"])
        legacy_again = build(legacy["root_raw"])
        self.assertEqual(legacy["root_raw"], legacy_again["root_raw"])
        self.assertEqual(shard_bytes(legacy), shard_bytes(legacy_again))

        upgraded = build(
            legacy["root_raw"], generation=decoded["generation"] + 1
        )
        self.assertEqual(
            capacity.ACTIVE_LAYOUT, upgraded["root"]["active_layout"]
        )
        self.assertLessEqual(len(upgraded["root_raw"]), capacity.ROOT_CAP_BYTES)
        self.assertEqual(decoded["tables"], decode(upgraded)["tables"])

    def test_rebuild_snapshot_hold_failure_restores_exact_active_recovery_set(self):
        controller = self.controller()
        controller.init()
        wal_path = Path(str(controller.db_path) + "-wal")
        shm_path = Path(str(controller.db_path) + "-shm")
        wal_path.write_bytes(b"active-wal-recovery-bytes")
        shm_path.write_bytes(b"active-shm-recovery-bytes")
        active_paths = (
            controller.db_path,
            wal_path,
            shm_path,
            controller.snapshot_path,
        )
        before = {path: path.read_bytes() for path in active_paths}
        original_replace = self.loopctl.os.replace

        def fail_snapshot_hold(source, destination):
            source_path = Path(source)
            destination_path = Path(destination)
            if (
                source_path == controller.snapshot_path
                and ".corrupt-" in destination_path.name
            ):
                raise OSError("injected snapshot hold failure")
            return original_replace(source, destination)

        self.loopctl.os.replace = fail_snapshot_hold
        try:
            with self.assertRaisesRegex(
                self.loopctl.SnapshotExportError, "REBUILD_REPLACE_FAILED"
            ):
                controller.rebuild()
        finally:
            self.loopctl.os.replace = original_replace

        for path, raw in before.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(raw, path.read_bytes(), path)
    def test_v3_rejects_active_claim_moved_into_terminal_shard(self):
        capacity = load_snapshot_capacity()
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature = self._feature("feature-active-claim-placement")
        feature["claims"] = [
            {"path": "src/active-a.py", "kind": "file"},
            {"path": "src/active-b.py", "kind": "file"},
        ]
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-active-claim-placement",
                "features": [feature["feature_id"]],
                "feature_packets": [feature],
            },
        )
        order = controller.create_work_order(
            program_id="program-active-claim-placement",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        root = json.loads(controller.snapshot_path.read_bytes())
        references = [*root["terminal_shards"], *root["active_shards"]]
        files = {
            reference["path"]: (
                self.repo / Path(*PurePosixPath(reference["path"]).parts)
            ).read_bytes()
            for reference in references
        }
        terminal_reference = root["terminal_shards"][0]
        active_reference = root["active_shards"][0]
        terminal_payload = json.loads(files[terminal_reference["path"]])
        active_payload = json.loads(files[active_reference["path"]])
        claim_record = next(
            record
            for record in active_payload["records"]
            if record[0] == "table"
            and record[1] == "claims"
            and record[2][0] == order["task_id"]
        )
        active_payload["records"].remove(claim_record)
        terminal_payload["records"].append(claim_record)
        terminal_payload["records"].sort(key=capacity.canonical_bytes)

        def replace_shard(reference, payload):
            old_path = reference["path"]
            raw = capacity.canonical_bytes(payload)
            digest = hashlib.sha256(raw).hexdigest()
            new_path = (
                old_path.rsplit("/", 1)[0]
                + "/"
                + digest
                + ".json"
            )
            files.pop(old_path)
            files[new_path] = raw
            reference.update(
                {
                    "byte_size": len(raw),
                    "count": len(payload["records"]),
                    "path": new_path,
                    "sha256": digest,
                }
            )

        replace_shard(terminal_reference, terminal_payload)
        replace_shard(active_reference, active_payload)
        claims_summary = next(
            item
            for item in root["active_detail_summaries"]["counts"]
            if item[0] == "claims"
        )
        claims_summary[1] -= 1
        self.assertGreaterEqual(claims_summary[1], 1)

        with self.assertRaisesRegex(
            capacity.SnapshotCapacityError,
            "SNAPSHOT_ACTIVE_DETAIL_INVALID",
        ):
            capacity.decode_v3(
                snapshot=root,
                snapshot_raw=capacity.canonical_bytes(root),
                columns=self.loopctl.SNAPSHOT_COLUMNS,
                read_reference=lambda path: (
                    files[path]
                    if path in files
                    else (
                        self.repo / Path(*PurePosixPath(path).parts)
                    ).read_bytes()
                ),
                list_generation_shards=lambda _generation: set(files),
            )
    def test_v3_shards_fail_closed_for_all_integrity_faults(self):
        controller = self.controller()
        controller.init()
        controller.register_worktree("core-x9", self.repo, "core")
        capacity = load_snapshot_capacity()
        root_raw = controller.snapshot_path.read_bytes()
        base_root = json.loads(root_raw)
        base_files = {
            reference["path"]: (
                self.repo / Path(*PurePosixPath(reference["path"]).parts)
            ).read_bytes()
            for reference in base_root["terminal_shards"]
        }
        if base_root["previous_generation"] is not None:
            previous = base_root["previous_generation"]
            base_files[previous["path"]] = (
                self.repo / Path(*PurePosixPath(previous["path"]).parts)
            ).read_bytes()

        def clone(value):
            return json.loads(json.dumps(value))

        def decode(root, files, actual_paths=None):
            paths = {
                reference["path"] for reference in root["terminal_shards"]
            }
            return capacity.decode_v3(
                snapshot=root,
                snapshot_raw=capacity.canonical_bytes(root),
                columns=self.loopctl.SNAPSHOT_COLUMNS,
                read_reference=lambda relative: files[relative],
                list_generation_shards=lambda _generation: (
                    paths if actual_paths is None else actual_paths
                ),
            )

        def replace_first_shard(root, files, shard):
            raw = capacity.canonical_bytes(shard)
            digest = hashlib.sha256(raw).hexdigest()
            old = root["terminal_shards"][0]
            prefix = old["path"].rsplit("/", 1)[0]
            path = f"{prefix}/{digest}.json"
            root["terminal_shards"][0] = {
                **old,
                "byte_size": len(raw),
                "count": len(shard["records"]),
                "path": path,
                "sha256": digest,
            }
            files[path] = raw
            return path

        first_path = base_root["terminal_shards"][0]["path"]
        cases = []

        root, files = clone(base_root), dict(base_files)
        cases.append(("missing", root, files, set(), "SNAPSHOT_SHARD_EXTRA_OR_MISSING"))

        root, files = clone(base_root), dict(base_files)
        cases.append(
            (
                "extra",
                root,
                files,
                {first_path, first_path + ".extra"},
                "SNAPSHOT_SHARD_EXTRA_OR_MISSING",
            )
        )

        root, files = clone(base_root), dict(base_files)
        malformed = json.loads(files[first_path])
        malformed["records"] = [["unsupported", "record"]]
        malformed_path = replace_first_shard(root, files, malformed)
        cases.append(("malformed", root, files, {malformed_path}, "SNAPSHOT_SHARD_INVALID"))

        root, files = clone(base_root), dict(base_files)
        root["terminal_shards"][0]["byte_size"] = 65537
        cases.append(("oversized", root, files, {first_path}, "SNAPSHOT_SHARD_INVALID"))

        root, files = clone(base_root), dict(base_files)
        root["terminal_shards"][0]["path"] = (
            root["terminal_shards"][0]["path"].rsplit("/", 1)[0]
            + "/../escape.json"
        )
        cases.append(("path-escape", root, files, set(), "SNAPSHOT_SHARD_PATH_INVALID"))

        root, files = clone(base_root), dict(base_files)
        duplicate = json.loads(files[first_path])
        duplicate["records"].append(clone(duplicate["records"][0]))
        duplicate_path = replace_first_shard(root, files, duplicate)
        cases.append(("duplicate", root, files, {duplicate_path}, "SNAPSHOT_SHARD_DUPLICATE"))

        root, files = clone(base_root), dict(base_files)
        files[first_path] = b"{}\n"
        cases.append(("hash-mismatch", root, files, {first_path}, "SNAPSHOT_SHARD_HASH_MISMATCH"))

        for name, root, files, actual_paths, code in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(capacity.SnapshotCapacityError, code):
                    decode(root, files, actual_paths)

    def test_work_order_preflight_rejects_wrong_base_and_dirty_tree_without_side_effects(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)

        def import_feature(program_id, feature_id, base_sha):
            feature = self._feature(feature_id)
            feature["base_sha"] = base_sha
            self._import_program(
                controller,
                {
                    "schema": "x9-loop-program-v1",
                    "program_id": program_id,
                    "features": [feature_id],
                    "feature_packets": [feature],
                },
            )

        def state():
            connection = controller._connect()
            try:
                counts = tuple(
                    connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in ("tasks", "work_orders", "dispatches")
                )
            finally:
                connection.close()
            files = sorted(
                path.relative_to(self.repo).as_posix()
                for path in (controller.root / "runtime" / "work-orders").glob(
                    "*/WORK_ORDER.json"
                )
            )
            return counts, files, controller.action_path.read_bytes()

        import_feature("wrong-base", "feature-wrong-base", "f" * 40)
        before = state()
        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "WORKTREE_BASE_SHA_MISMATCH"
        ):
            controller.create_work_order(
                program_id="wrong-base",
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )
        self.assertEqual(before, state())

        import_feature("dirty-tree", "feature-dirty-tree", self.base_sha)
        (self.repo / "src" / "a.py").write_text("A = 2\n", encoding="utf-8")
        before = state()
        with self.assertRaisesRegex(
            self.loopctl.TaskNotReadyError, "WORKTREE_NOT_CLEAN"
        ):
            controller.create_work_order(
                program_id="dirty-tree",
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )
        self.assertEqual(before, state())

    def test_capacity_reservation_admits_large_order_and_preserves_slots(self):
        capacity = load_snapshot_capacity()
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        controller.register_actor(
            "worker-normal", "WORKER", "AI - WORKER NORMAL", "Unknown"
        )
        controller.register_worktree("core-x9-normal", self.repo, "core")
        oversized = self._feature("feature-oversized")
        oversized.update(
            {
                "claims": [
                    {"path": f"src/capacity-{index:02d}.py", "kind": "file"}
                    for index in range(8)
                ],
                "finish_line": "bounded proof " + "x" * 3000,
                "resources": [
                    f"integration:capacity-{index:02d}" for index in range(8)
                ],
            }
        )
        normal = self._feature("feature-normal")
        normal.update(
            {
                "claims": [{"path": "src/normal.py", "kind": "file"}],
                "resources": ["integration:normal"],
                "worker_id": "worker-normal",
                "worktree_id": "core-x9-normal",
            }
        )
        for program_id, feature in (
            ("program-oversized", oversized),
            ("program-normal", normal),
        ):
            self._import_program(
                controller,
                {
                    "schema": "x9-loop-program-v1",
                    "program_id": program_id,
                    "features": [feature["feature_id"]],
                    "feature_packets": [feature],
                },
            )

        oversized_order = controller.create_work_order(
            program_id="program-oversized",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        self.assertEqual("CREATED", oversized_order["status"])
        first_root_size = controller.snapshot_path.stat().st_size
        self.assertLessEqual(
            first_root_size
            + 2 * capacity.ACTIVE_ORDER_RESERVATION_BYTES,
            capacity.ROOT_CAP_BYTES,
        )

        normal_order = controller.create_work_order(
            program_id="program-normal",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        self.assertEqual("CREATED", normal_order["status"])
        second_root_size = controller.snapshot_path.stat().st_size
        self.assertLessEqual(
            second_root_size + capacity.ACTIVE_ORDER_RESERVATION_BYTES,
            capacity.ROOT_CAP_BYTES,
        )
        connection = controller._connect()
        try:
            self.assertEqual(
                (2, 2, 2),
                tuple(
                    connection.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    ).fetchone()[0]
                    for table in ("tasks", "work_orders", "dispatches")
                ),
            )
        finally:
            connection.close()
    def test_context_failure_creates_no_task_or_order(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature = self._feature("feature-a")
        feature.pop("owner_requirement")
        with self.assertRaisesRegex(self.loopctl.IdentityError, "CONTEXT_INCOMPLETE:owner_requirement"):
            self._import_program(
                controller,
                {
                    "schema": "x9-loop-program-v1",
                    "program_id": "program-a",
                    "features": ["feature-a"],
                    "feature_packets": [feature],
                },
            )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0])
        finally:
            connection.close()

    def test_controller_import_binds_mechanical_inventory_coverage_and_live_root(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        importer = load_program_import()
        source_root = self.repo / "import-source"
        metadata = {"feature.md": {"feature_ids": ["feature-a"]}}
        artifacts = importer.build_import_artifacts(source_root, metadata_by_path=metadata)
        program = {
            "schema": "x9-loop-program-v1",
            "program_id": "program-a",
            "features": ["feature-a"],
            "feature_packets": [self._feature("feature-a")],
        }
        with self.assertRaisesRegex(self.loopctl.IdentityError, "PROGRAM_ROOT_HASH_MISMATCH"):
            controller.import_program(
                program,
                source_git_sha=self.base_sha,
                source_root=source_root,
                source_root_sha256="1" * 64,
                metadata_by_path=metadata,
            )
        imported = controller.import_program(
            program,
            source_git_sha=self.base_sha,
            source_root=source_root,
            source_root_sha256=artifacts["inventory_root_sha256"],
            metadata_by_path=metadata,
        )
        program_packet = json.loads(
            (self.repo / imported["packet_path"]).read_text(encoding="utf-8")
        )
        for field in ("inventory_ref", "coverage_summary_ref", "coverage_shard_refs"):
            self.assertIn(field, program_packet)
        self.assertNotIn("feature_packets", program_packet)
        self.assertEqual(["feature-a"], program_packet["features"])
        self.assertEqual(["feature-a"], [row["feature_id"] for row in program_packet["feature_index"]])
        feature_ref = program_packet["feature_index"][0]
        feature_raw = (
            self.repo / feature_ref["feature_packet_path"]
        ).read_bytes()
        self.assertEqual(
            feature_ref["feature_packet_sha256"], hashlib.sha256(feature_raw).hexdigest()
        )
        (source_root / "feature.md").write_text("drifted\n", encoding="utf-8")
        with self.assertRaisesRegex(self.loopctl.IdentityError, "PROGRAM_SOURCE_ROOT_DRIFT"):
            controller.create_work_order(
                program_id="program-a",
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )

    def test_import_rejects_dependency_outside_authoritative_dag(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature = self._feature("feature-a")
        feature["dependencies"] = ["missing-feature"]
        with self.assertRaisesRegex(self.loopctl.IdentityError, "PROGRAM_FEATURE_DAG_INVALID"):
            self._import_program(
                controller,
                {
                    "schema": "x9-loop-program-v1",
                    "program_id": "program-a",
                    "features": ["feature-a"],
                    "feature_packets": [feature],
                },
            )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0])
        finally:
            connection.close()

    def test_import_rejects_dot_segment_program_id_without_writes(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        before = sorted(
            path.relative_to(controller.root).as_posix()
            for path in controller.root.rglob("*")
        )
        with self.assertRaisesRegex(self.loopctl.IdentityError, "PROGRAM_ID_INVALID"):
            self._import_program(
                controller,
                {
                    "schema": "x9-loop-program-v1",
                    "program_id": "..",
                    "features": ["feature-a"],
                    "feature_packets": [self._feature("feature-a")],
                },
            )
        after = sorted(
            path.relative_to(controller.root).as_posix()
            for path in controller.root.rglob("*")
        )
        self.assertEqual(before, after)
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                0, connection.execute("SELECT COUNT(*) FROM programs").fetchone()[0]
            )
        finally:
            connection.close()

    def test_controller_selects_from_immutable_feature_dag_not_caller_packet(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature_a = self._feature("feature-a")
        feature_b = self._feature("feature-b")
        feature_b["dependencies"] = ["feature-a"]
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-a",
                "features": ["feature-a", "feature-b"],
                "feature_packets": [feature_a, feature_b],
            },
        )
        forged_b = self._feature("feature-b")
        forged_b["dependencies"] = []
        with self.assertRaisesRegex(TypeError, "unexpected keyword argument 'features'"):
            controller.create_work_order(
                program_id="program-a",
                features=[forged_b],
                stop=self._stop(),
                linx_id="linx",
                action_class="implementation",
            )

        first = controller.create_work_order(
            program_id="program-a",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        first_order = json.loads(
            (self.repo / first["work_order_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            ["feature-a"],
            [ref["feature_id"] for ref in first_order["feature_packet_refs"]],
        )
        controller._transition_task_state(first["task_id"], "COMPLETE")
        second = controller.create_work_order(
            program_id="program-a",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        second_order = json.loads(
            (self.repo / second["work_order_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            ["feature-b"],
            [ref["feature_id"] for ref in second_order["feature_packet_refs"]],
        )

    def test_register_and_record_call_receipt_cli_dispatch_are_disjoint(self):
        controller = self.controller()
        controller.init()
        actor_path = Path(self.temp.name) / "actor.json"
        actor_path.write_text(
            json.dumps(
                {
                    "actor_id": "reviewer",
                    "kind": "actor",
                    "model": "Unknown",
                    "role": "THINX",
                    "title": "AI - THINX v3",
                }
            ),
            encoding="utf-8",
        )
        registered = subprocess.run(
            [
                sys.executable,
                str(LOOPCTL),
                "--repo",
                str(self.repo),
                "register",
                "--file",
                str(actor_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, registered.returncode, registered.stderr)
        self.assertEqual("REGISTERED", json.loads(registered.stdout)["status"])

        order = self._create_order(controller)
        controller.check_model_call(order["work_order_id"], self._call_telemetry("call-cli"))
        receipt_path = Path(self.temp.name) / "receipt.json"
        receipt_path.write_text(
            json.dumps(self._receipt_for(order, "call-cli")), encoding="utf-8"
        )
        recorded = subprocess.run(
            [
                sys.executable,
                str(LOOPCTL),
                "--repo",
                str(self.repo),
                "record-call-receipt",
                "--work-order",
                order["work_order_id"],
                "--file",
                str(receipt_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, recorded.returncode, recorded.stdout + recorded.stderr)
        self.assertEqual("RECORDED", json.loads(recorded.stdout)["status"])

    def _create_order(self, controller, feature_id="feature-a", stop=None):
        controller.init()
        self._register_v7_actors(controller)
        self._import_program(
            controller,
            {"schema": "x9-loop-program-v1", "program_id": "program-a", "features": [feature_id]},
        )
        return controller.create_work_order(
            program_id="program-a",
            stop=stop or self._stop(),
            linx_id="linx",
            action_class="implementation",
        )

    def _write_v7_worker_event(
        self,
        controller,
        order,
        *,
        changed_files=(),
        outcome,
        failed_verified_approaches=0,
        budget_remaining=True,
        include_proofs=True,
        event_id="event-v7-worker",
    ):
        contract = self.loopctl._load_v7_contract()
        proof = []
        if include_proofs and outcome in {"SUCCESS", "SUCCESS_CANDIDATE"}:
            for kind in ("security", "tests"):
                proof_path = (
                    f".devad/workers/worker/proof/{event_id}/{kind}.json"
                )
                proof_document = {
                    "dispatch_id": order["dispatch_id"],
                    "event_id": event_id,
                    "kind": kind,
                    "schema": "x9-loop-proof-v2",
                    "status": "PASS",
                    "task_id": order["task_id"],
                    "work_order_id": order["work_order_id"],
                    "worker_id": "worker",
                }
                proof_raw = contract.canonical_json_bytes(proof_document)
                absolute = self.repo / Path(
                    *PurePosixPath(proof_path).parts
                )
                absolute.parent.mkdir(parents=True, exist_ok=True)
                absolute.write_bytes(proof_raw)
                proof.append(
                    {
                        "kind": kind,
                        "path": proof_path,
                        "sha256": hashlib.sha256(proof_raw).hexdigest(),
                    }
                )
        proof_paths = [item["path"] for item in proof]
        result = {
            "attestation_path": None,
            "blocker": (
                None if outcome in {"SUCCESS", "SUCCESS_CANDIDATE"} else "bounded blocker"
            ),
            "budget_remaining": budget_remaining,
            "c1": None,
            "c2": None,
            "change_map": {
                "changed_surface": list(changed_files),
                "proof_refs": proof_paths,
                "reason": "bounded worker result",
                "remaining_risk": "none known",
                "rollback": "no source changes",
            },
            "changed_files": list(changed_files),
            "dispatch_id": order["dispatch_id"],
            "event_id": event_id,
            "failed_verified_approaches": failed_verified_approaches,
            "outcome": outcome,
            "packet_sha256": order["work_order_sha256"],
            "proof": proof,
            "role": "WORKER",
            "schema": "x9-loop-result-v2",
            "task_id": order["task_id"],
            "work_order_id": order["work_order_id"],
            "work_order_sha256": order["work_order_sha256"],
            "worker_id": "worker",
        }
        if outcome == "VERIFIED_FAILURE":
            approaches = []
            for index in range(failed_verified_approaches):
                evidence_path = (
                    f".devad/workers/worker/proof/{event_id}/approaches/"
                    f"approach-{index}.json"
                )
                source_hashes = {
                    "src/a.py": hashlib.sha256(
                        (self.repo / "src" / "a.py").read_bytes()
                    ).hexdigest(),
                }
                evidence = {
                    "action_class": "implementation",
                    "approach_id": f"approach-{index}",
                    "event_id": event_id,
                    "failure_code": "LOCAL_FAILURE",
                    "hypothesis": "fixture hypothesis",
                    "next_route": "fixture next route",
                    "progress": False,
                    "route": f"fixture-route-{index}",
                    "schema": "x9-loop-approach-proof-v1",
                    "source_hashes": source_hashes,
                    "task_id": order["task_id"],
                    "work_order_id": order["work_order_id"],
                    "worker_id": "worker",
                }
                evidence_raw = contract.canonical_json_bytes(evidence)
                evidence_absolute = self.repo / Path(
                    *PurePosixPath(evidence_path).parts
                )
                evidence_absolute.parent.mkdir(parents=True, exist_ok=True)
                evidence_absolute.write_bytes(evidence_raw)
                unsigned = {
                    "action_class": "implementation",
                    "approach_id": f"approach-{index}",
                    "evidence_path": evidence_path,
                    "evidence_sha256": hashlib.sha256(evidence_raw).hexdigest(),
                    "failure_code": "LOCAL_FAILURE",
                    "hypothesis": "fixture hypothesis",
                    "next_route": "fixture next route",
                    "progress": False,
                    "route": f"fixture-route-{index}",
                    "schema": contract.APPROACH_RECEIPT_SCHEMA,
                    "source_hashes": source_hashes,
                }
                approach = {
                    **unsigned,
                    "approach_sha256": contract.sha256_bytes(
                        contract.canonical_json_bytes(unsigned)
                    ),
                }
                approaches.append(approach)
            result["approach_receipts"] = approaches
            result["autonomy_proxy"] = {
                "consultation_count": 0,
                "distinct_failed_approaches": len(approaches),
                "duplicate_reviews_suppressed": 0,
                "repeated_context_bytes_avoided": "Unknown",
                "subagent_count": 0,
                "subagent_profile": None,
                "token_usage": "Unknown",
                "work_order_count": 1,
            }
        raw = contract.canonical_json_bytes(result)
        result_path = (
            f".devad/workers/worker/receipts/{event_id}.json"
        )
        absolute = self.repo / Path(*PurePosixPath(result_path).parts)
        absolute.parent.mkdir(parents=True, exist_ok=True)
        absolute.write_bytes(raw)
        return {
            "actor_id": "worker",
            "dispatch_id": order["dispatch_id"],
            "event_id": event_id,
            "event_type": "WORKER_RESULT",
            "packet_sha256": order["work_order_sha256"],
            "result_path": result_path,
            "result_sha256": hashlib.sha256(raw).hexdigest(),
            "role": "WORKER",
            "task_id": order["task_id"],
        }

    def _write_v7_worker_outbox_event(self, controller, event):
        contract = self.loopctl._load_v7_contract()
        envelope = {
            "event_id": event["event_id"],
            "event_type": "WORKER_RESULT",
            "payload_ref": {
                "path": event["result_path"],
                "sha256": event["result_sha256"],
            },
            "project_profile_id": json.loads(
                controller.project_profile_path.read_bytes()
            )["project_profile_id"],
            "schema": "x9-loop-inbox-event-v1",
            "source_actor_id": event["actor_id"],
            "source_role": event["role"],
        }
        raw = contract.canonical_json_bytes(envelope)
        outbox = (
            self.repo
            / ".devad"
            / "workers"
            / event["actor_id"]
            / "outbox"
            / event["event_id"]
            / "INBOX_EVENT.json"
        )
        outbox.parent.mkdir(parents=True, exist_ok=True)
        outbox.write_bytes(raw)
        inbox = (
            controller.root
            / "runtime"
            / "inbox"
            / event["event_id"]
            / "INBOX_EVENT.json"
        )
        inbox.parent.mkdir(parents=True, exist_ok=True)
        inbox.write_bytes(raw)
        return inbox

    def _write_v7_worker_result_ready(self, controller, event):
        emitted = controller.emit_result_ready(event["event_id"])
        source = self.repo / Path(*PurePosixPath(emitted["path"]).parts)
        path = (
            self.repo / ".devad" / "workers" / event["actor_id"]
            / "outbox" / event["event_id"] / "RESULT_READY.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.read_bytes())
        return path, emitted

    def _add_prior_program_assignment(
        self, controller, current_order, status
    ):
        contract = self.loopctl._load_v7_contract()
        current_path = self.repo / Path(
            *PurePosixPath(current_order["work_order_path"]).parts
        )
        prior = json.loads(current_path.read_bytes())
        suffix = status.lower()
        prior_order_id = f"wo-prior-{suffix}"
        prior_task_id = f"task-prior-{suffix}"
        prior_dispatch_id = f"dsp-prior-{suffix}"
        prior_relative = (
            ".devad/manager/loop-lite/runtime/work-orders/"
            f"{prior_order_id}/WORK_ORDER.json"
        )
        prior.update(
            {
                "created_at": "2026-07-14T11:59:59Z",
                "task_id": prior_task_id,
                "work_order_id": prior_order_id,
            }
        )
        raw = contract.canonical_json_bytes(prior)
        digest = contract.sha256_bytes(raw)
        prior_path = self.repo / Path(*PurePosixPath(prior_relative).parts)
        prior_path.parent.mkdir(parents=True, exist_ok=True)
        prior_path.write_bytes(raw)

        def add_prior(connection):
            source = connection.execute(
                "SELECT t.dependencies,t.finish_line,wo.program_id "
                "FROM tasks t JOIN work_orders wo ON wo.task_id=t.task_id "
                "WHERE t.task_id=?",
                (current_order["task_id"],),
            ).fetchone()
            connection.execute(
                "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    prior_task_id,
                    prior["worker_id"],
                    prior["worktree_id"],
                    prior["base_sha"],
                    prior_relative,
                    digest,
                    source["dependencies"],
                    source["finish_line"],
                    status,
                ),
            )
            connection.execute(
                "INSERT INTO claims SELECT ?,path,kind FROM claims "
                "WHERE task_id=?",
                (prior_task_id, current_order["task_id"]),
            )
            connection.execute(
                "INSERT INTO resources SELECT ?,resource FROM resources "
                "WHERE task_id=?",
                (prior_task_id, current_order["task_id"]),
            )
            connection.execute(
                "INSERT INTO work_orders VALUES(?,?,?,?,?,?,?,?)",
                (
                    prior_order_id,
                    prior_task_id,
                    prior["worker_id"],
                    prior_relative,
                    digest,
                    source["program_id"],
                    status,
                    prior["created_at"],
                ),
            )
            connection.execute(
                "INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    prior_dispatch_id,
                    prior_task_id,
                    "linx",
                    prior["worker_id"],
                    digest,
                    self.loopctl._json(
                        {
                            "schema": "x9-loop-work-order-dispatch-v1",
                            "task_id": prior_task_id,
                            "work_order_path": prior_relative,
                            "work_order_sha256": digest,
                        }
                    ),
                    None,
                    status,
                    prior["created_at"],
                ),
            )
            if status == "COMPLETE":
                controller._remember_completed_task(
                    connection, prior_task_id
                )

        controller._mutate(add_prior)

    def _program_assignment_result_scenario(self, status):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature_a = self._feature("feature-a")
        feature_b = self._feature("feature-b")
        feature_b["dependencies"] = ["feature-a"]
        program_id = f"program-assignment-{status.lower()}"
        self._import_program(
            controller,
            {
                "feature_packets": [feature_a, feature_b],
                "features": ["feature-a", "feature-b"],
                "program_id": program_id,
                "schema": "x9-loop-program-v1",
            },
        )
        current = controller.create_work_order(
            program_id=program_id,
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        self._add_prior_program_assignment(controller, current, status)
        controller.record_delivery(
            current["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            current,
            outcome="SUCCESS",
            event_id=f"event-assignment-{status.lower()}",
        )
        return (
            controller,
            self._write_v7_worker_outbox_event(controller, event),
        )
    def _controller_durable_state(self, controller):
        return (
            controller.snapshot_path.read_bytes(),
            controller.action_path.read_bytes(),
            self.loopctl._json(self._decode_v3_snapshot(controller)),
            tuple(
                sorted(
                    path.relative_to(self.repo).as_posix()
                    for path in (
                        controller.root / "runtime" / "work-orders"
                    ).rglob("WORK_ORDER.json")
                )
            ),
        )
    def _write_v7_thinx_event(
        self,
        controller,
        order,
        worker_event,
        *,
        decision="PASS",
        event_id="event-v7-thinx",
    ):
        contract = self.loopctl._load_v7_contract()
        result = {
            "actor_id": "thinx",
            "decision": decision,
            "dispatch_id": order["dispatch_id"],
            "event_id": event_id,
            "packet_sha256": order["work_order_sha256"],
            "reason": "silent conditional review",
            "role": "THINX",
            "schema": "x9-loop-thinx-decision-v2",
            "task_id": order["task_id"],
            "worker_event_id": worker_event["event_id"],
            "worker_result_sha256": worker_event["result_sha256"],
            "work_order_id": order["work_order_id"],
            "work_order_sha256": order["work_order_sha256"],
        }
        raw = contract.canonical_json_bytes(result)
        result_path = f".devad/workers/thinx/receipts/{event_id}.json"
        absolute = self.repo / Path(*PurePosixPath(result_path).parts)
        absolute.parent.mkdir(parents=True, exist_ok=True)
        absolute.write_bytes(raw)
        return {
            "actor_id": "thinx",
            "dispatch_id": order["dispatch_id"],
            "event_id": event_id,
            "event_type": "THINX_DECISION",
            "packet_sha256": order["work_order_sha256"],
            "result_path": result_path,
            "result_sha256": hashlib.sha256(raw).hexdigest(),
            "role": "THINX",
            "task_id": order["task_id"],
        }
    def test_v7_no_change_success_consumes_idempotently_and_syncs_order(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller, order, outcome="SUCCESS"
        )
        consumed = controller.consume_event(event)
        self.assertEqual("FEATURE_DONE", consumed["status"])
        self.assertEqual(
            "DUPLICATE_EVENT", controller.consume_event(event)["status"]
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("COMPLETE", "COMPLETE", "COMPLETE"),
                connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone(),
            )
        finally:
            connection.close()
        rebuilt = controller.rebuild()
        self.assertEqual("PASS", rebuilt["status"])

    def test_v7_hard_external_and_two_proof_results_map_exactly(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        hard = self._write_v7_worker_event(
            controller, order, outcome="HARD_EXTERNAL"
        )
        self.assertEqual(
            "OWNER_DECISION_REQUIRED",
            controller.consume_event(hard)["status"],
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("OWNER_DECISION_REQUIRED", "OWNER_DECISION_REQUIRED"),
                connection.execute(
                    "SELECT t.status,wo.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone(),
            )
        finally:
            connection.close()

        other_temp = tempfile.TemporaryDirectory()
        self.addCleanup(other_temp.cleanup)
        other_repo = Path(other_temp.name) / "repo"
        other_base = git_repo(other_repo)
        old_repo, old_base = self.repo, self.base_sha
        self.repo, self.base_sha = other_repo, other_base
        try:
            other = self.controller()
            other_order = self._create_order(other)
            other.record_delivery(
                other_order["dispatch_id"], "DISPATCH", "task", "ack"
            )
            blocked = self._write_v7_worker_event(
                other,
                other_order,
                outcome="VERIFIED_FAILURE",
                failed_verified_approaches=3,
                budget_remaining=True,
            )
            self.assertEqual(
                "HARD_BLOCKER_AFTER_2_PROOFS",
                other.consume_event(blocked)["status"],
            )
            connection = sqlite3.connect(other.db_path)
            try:
                self.assertEqual(
                    ("THINX_REVIEW_REQUIRED", "THINX_REVIEW_REQUIRED"),
                    connection.execute(
                        "SELECT t.status,wo.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (other_order["task_id"],),
                    ).fetchone(),
                )
            finally:
                connection.close()
        finally:
            self.repo, self.base_sha = old_repo, old_base

    def test_v3_thinx_review_uses_latest_dispatch_rowid_when_timestamps_tie(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(order["dispatch_id"], "DISPATCH", "task", "ack")
        blocked = self._write_v7_worker_event(
            controller,
            order,
            outcome="VERIFIED_FAILURE",
            failed_verified_approaches=3,
            budget_remaining=True,
            event_id="event-tied-dispatch-review",
        )
        self.assertEqual(
            "HARD_BLOCKER_AFTER_2_PROOFS", controller.consume_event(blocked)["status"]
        )

        latest_id = "000-latest-dispatch"

        def add_tied_dispatch(connection):
            original = connection.execute(
                "SELECT * FROM dispatches WHERE dispatch_id=?", (order["dispatch_id"],)
            ).fetchone()
            connection.execute(
                "INSERT INTO dispatches VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    latest_id,
                    original["task_id"],
                    original["sender_id"],
                    original["target_id"],
                    original["packet_sha256"],
                    original["packet"],
                    original["dispatch_id"],
                    "COMPLETE",
                    original["created_at"],
                ),
            )

        controller._mutate(add_tied_dispatch)
        self.assertLess(latest_id, order["dispatch_id"])

        decoded = self._decode_v3_snapshot(controller)
        self.assertEqual(
            latest_id,
            decoded["tables"]["dispatches"][-1]["dispatch_id"],
        )
        self.assertEqual("PASS", controller.rebuild()["status"])
        rebuilt = self._decode_v3_snapshot(controller)
        self.assertEqual(
            latest_id,
            rebuilt["tables"]["dispatches"][-1]["dispatch_id"],
        )
    def test_v7_thinx_pass_creates_fresh_retry_dispatch(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.register_actor("thinx", "THINX", "AI - THINX v3", "Unknown")
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        blocked = self._write_v7_worker_event(
            controller,
            order,
            outcome="VERIFIED_FAILURE",
            failed_verified_approaches=2,
            budget_remaining=True,
            event_id="event-worker-two",
        )
        self.assertEqual(
            "HARD_BLOCKER_AFTER_2_PROOFS",
            controller.consume_event(blocked)["status"],
        )
        controller.record_delivery(
            order["dispatch_id"], "REVIEW", "task", "ack"
        )
        decision = self._write_v7_thinx_event(
            controller, order, blocked
        )
        self.assertEqual(
            "RETRY_READY", controller.consume_event(decision)["status"]
        )
        self.assertEqual(
            "DUPLICATE_EVENT",
            controller.consume_event(decision)["status"],
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            state = connection.execute(
                "SELECT t.status,wo.status FROM tasks t "
                "JOIN work_orders wo ON wo.task_id=t.task_id "
                "WHERE t.task_id=?",
                (order["task_id"],),
            ).fetchone()
            latest = connection.execute(
                "SELECT dispatch_id,status,supersedes FROM dispatches "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 1",
                (order["task_id"],),
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(("RETRY_READY", "CREATED"), state)
        self.assertNotEqual(order["dispatch_id"], latest[0])
        self.assertEqual(("PREPARED", order["dispatch_id"]), latest[1:])
        action = json.loads(controller.action_path.read_text(encoding="utf-8"))
        self.assertEqual("SEND_WORK_ORDER", action["action"])
        self.assertEqual(latest[0], action["dispatch_id"])

    def test_terminal_stop_retires_dispatch_and_rejects_late_success(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        telemetry = self._call_telemetry("terminal-stop")
        telemetry["attempt"] = 3
        stopped = controller.check_model_call(order["work_order_id"], telemetry)
        self.assertEqual("MAX_ATTEMPTS", stopped["reason"])
        action = json.loads(controller.action_path.read_text(encoding="utf-8"))
        self.assertEqual("NOOP", action["action"])
        with self.assertRaisesRegex(
            self.loopctl.DeliveryError, "DISPATCH_INACTIVE"
        ):
            controller.record_delivery(
                order["dispatch_id"], "CALLBACK", "task", "ack"
            )
        late = self._write_v7_worker_event(
            controller,
            order,
            outcome="SUCCESS",
            event_id="event-late-after-stop",
        )
        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError, "STALE_COMPLETION"
        ):
            controller.consume_event(late)
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                (
                    "OWNER_DECISION_REQUIRED",
                    "OWNER_DECISION_REQUIRED",
                    "SUPERSEDED",
                ),
                connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone(),
            )
        finally:
            connection.close()
    def test_v7_soft_local_result_stays_worker_local(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller, order, outcome="SOFT_LOCAL"
        )
        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError,
            "WORKER_LOCAL_CHECKPOINT_REQUIRED",
        ):
            controller.consume_event(event)
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("REGISTERED", "CREATED", "DISPATCHED"),
                connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone(),
            )
        finally:
            connection.close()

    def test_reconcile_uses_work_order_evidence_for_v7_task(self):
        controller = self.controller()
        order = self._create_order(controller)
        reconciled = controller.reconcile(order["task_id"])
        self.assertEqual([], reconciled["scope_breach"])
        self.assertEqual([], reconciled["controller_tamper"])

    def test_reconcile_quarantines_expired_scope_breach_without_touching_worker_bytes(self):
        clock = ["2026-07-14T12:00:00Z"]
        controller = self.loopctl.Controller(self.repo, now_fn=lambda: clock[0])
        order = self._create_order(
            controller, stop=dict(self._stop(), max_wall_seconds=60)
        )
        controller.record_delivery(order["dispatch_id"], "DISPATCH", "task", "ack")
        unclaimed = self.repo / "unclaimed.php"
        unclaimed.write_bytes(b"preserve\n")
        clock[0] = "2026-07-14T12:02:00Z"

        result = controller.reconcile(order["task_id"])

        self.assertEqual("CONTROLLER_VIOLATION_DETECTED", result.get("status"))
        self.assertEqual("OWNER_DECISION_REQUIRED", result.get("event"))
        self.assertEqual(["MAX_WALL_SECONDS", "SCOPE_BREACH"], result.get("violations"))
        self.assertEqual(b"preserve\n", unclaimed.read_bytes())
        action_before = controller.action_path.read_bytes()
        action = json.loads(action_before)
        self.assertEqual("NOOP", action["action"])
        self.assertEqual(
            "owner-decision-required:MAX_WALL_SECONDS+SCOPE_BREACH",
            action["reason"],
        )
        connection = controller._connect()
        try:
            self.assertEqual(
                ("OWNER_DECISION_REQUIRED", "OWNER_DECISION_REQUIRED", "SUPERSEDED"),
                tuple(connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone()),
            )
            self.assertEqual(
                (
                    "BLOCKED",
                    "CONTROLLER_VIOLATION_DETECTED:MAX_WALL_SECONDS+SCOPE_BREACH",
                ),
                tuple(connection.execute(
                    "SELECT status,note FROM gates WHERE task_id=? "
                    "AND name='controller:violation'",
                    (order["task_id"],),
                ).fetchone()),
            )
            counts = tuple(connection.execute(
                "SELECT (SELECT COUNT(*) FROM outbox o JOIN dispatches d "
                "ON d.dispatch_id=o.dispatch_id WHERE o.dispatch_id=? "
                "AND d.status IN ('PREPARED','DISPATCHED')) ,"
                "(SELECT COUNT(*) FROM call_reservations WHERE work_order_id=?),"
                "(SELECT COUNT(*) FROM claims WHERE task_id=?),"
                "(SELECT COUNT(*) FROM resources WHERE task_id=?)",
                (order["dispatch_id"], order["work_order_id"], order["task_id"], order["task_id"]),
            ).fetchone())
            generation = controller._generation(connection)
        finally:
            connection.close()
        self.assertEqual((0, 0, 1, 1), counts)

        blocked_call = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("call-after-quarantine")
        )
        self.assertFalse(blocked_call["allow_call"])
        self.assertEqual("WORK_ORDER_NOT_ACTIVE", blocked_call["reason"])
        self.assertEqual(action_before, controller.action_path.read_bytes())
        self.assertEqual(b"preserve\n", unclaimed.read_bytes())
        connection = controller._connect()
        try:
            self.assertEqual(
                0,
                connection.execute(
                    "SELECT COUNT(*) FROM call_reservations "
                    "WHERE work_order_id=?",
                    (order["work_order_id"],),
                ).fetchone()[0],
            )
        finally:
            connection.close()

        replay = controller.reconcile(order["task_id"])
        self.assertEqual("CONTROLLER_VIOLATION_DETECTED", replay.get("status"))
        self.assertEqual(action_before, controller.action_path.read_bytes())
        connection = controller._connect()
        try:
            self.assertEqual(generation, controller._generation(connection))
        finally:
            connection.close()

    def test_reconcile_crash_cannot_leave_prepared_send_transportable(self):
        clock = ["2026-07-14T12:00:00Z"]
        controller = self.loopctl.Controller(self.repo, now_fn=lambda: clock[0])
        order = self._create_order(
            controller, stop=dict(self._stop(), max_wall_seconds=60)
        )
        self.assertEqual(
            "SEND_WORK_ORDER",
            json.loads(controller.action_path.read_bytes())["action"],
        )
        clock[0] = "2026-07-14T12:02:00Z"
        original_write_action = controller._write_action

        def crash_before_specific_owner_action(action):
            if str(action.get("reason", "")).startswith(
                "owner-decision-required:"
            ):
                raise RuntimeError("CRASH_BEFORE_SPECIFIC_OWNER_ACTION")
            original_write_action(action)

        with mock.patch.object(
            controller, "_write_action", side_effect=crash_before_specific_owner_action
        ):
            with self.assertRaisesRegex(
                RuntimeError, "CRASH_BEFORE_SPECIFIC_OWNER_ACTION"
            ):
                controller.reconcile(order["task_id"])

        fail_closed_action = json.loads(controller.action_path.read_bytes())
        self.assertEqual("NOOP", fail_closed_action["action"])
        self.assertEqual(
            "controller-violation-quarantine-pending",
            fail_closed_action["reason"],
        )
        linker = load_linker_once()
        drop = self.repo / "runtime" / "unexpected-delivery.json"
        transport = linker.link_once(
            controller.action_path,
            self.repo / "runtime" / "unexpected-ack.json",
            linker.LocalFileAdapter(drop),
        )
        self.assertEqual("NO_ACTION", transport["status"])
        self.assertFalse(drop.exists())

        connection = controller._connect()
        try:
            self.assertEqual(
                ("OWNER_DECISION_REQUIRED", "OWNER_DECISION_REQUIRED", "SUPERSEDED"),
                tuple(connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone()),
            )
            self.assertEqual(
                (1, 1, 1),
                tuple(connection.execute(
                    "SELECT (SELECT COUNT(*) FROM outbox WHERE dispatch_id=?),"
                    "(SELECT COUNT(*) FROM claims WHERE task_id=?),"
                    "(SELECT COUNT(*) FROM resources WHERE task_id=?)",
                    (order["dispatch_id"], order["task_id"], order["task_id"]),
                ).fetchone()),
            )
        finally:
            connection.close()

        restarted = self.loopctl.Controller(self.repo, now_fn=lambda: clock[0])
        replay = restarted.reconcile(order["task_id"])
        self.assertEqual("CONTROLLER_VIOLATION_DETECTED", replay["status"])
        final_action = json.loads(restarted.action_path.read_bytes())
        self.assertEqual("NOOP", final_action["action"])
        self.assertEqual(
            "owner-decision-required:MAX_WALL_SECONDS", final_action["reason"]
        )

    def test_reconcile_does_not_escalate_completed_task_after_old_wall_limit(self):
        clock = ["2026-07-14T12:00:00Z"]
        controller = self.loopctl.Controller(self.repo, now_fn=lambda: clock[0])
        order = self._create_order(
            controller, stop=dict(self._stop(), max_wall_seconds=60)
        )
        controller.record_delivery(order["dispatch_id"], "DISPATCH", "task", "ack")
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SUCCESS",
            event_id="event-complete-before-old-wall-limit",
        )
        self.assertEqual("FEATURE_DONE", controller.consume_event(event)["status"])
        clock[0] = "2026-07-14T12:02:00Z"

        result = controller.reconcile(order["task_id"])

        self.assertNotIn("status", result)
        self.assertNotIn("event", result)
        self.assertNotIn("violations", result)
        connection = controller._connect()
        try:
            self.assertEqual(
                ("COMPLETE", "COMPLETE", "COMPLETE"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status,d.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (order["task_id"],),
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

    def test_hard_stop_is_durable_and_forbids_every_later_call(self):
        controller = self.controller()
        order = self._create_order(controller)
        telemetry = {
            "action_class": "implementation",
            "attempt": 3,
            "call_id": "call-stop-1",
            "elapsed_seconds": 1,
            "model_calls": 0,
            "objective_satisfied": False,
            "prompt_prefix_sha256": "a" * 64,
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        }
        stopped = controller.check_model_call(order["work_order_id"], telemetry)
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("MAX_ATTEMPTS", stopped["reason"])
        telemetry["attempt"] = 0
        later = controller.check_model_call(order["work_order_id"], telemetry)
        self.assertFalse(later["allow_call"])
        self.assertEqual("WORK_ORDER_NOT_ACTIVE", later["reason"])

    def test_duplicate_call_receipt_restores_missing_evidence_and_rejects_tamper(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.check_model_call(
            order["work_order_id"], self._call_telemetry("durable-duplicate")
        )
        receipt = self._receipt_for(order, "durable-duplicate")
        recorded = controller.record_call_receipt(
            order["work_order_id"], receipt
        )
        evidence = self.repo / Path(
            *PurePosixPath(recorded["evidence_path"]).parts
        )
        evidence.unlink()
        replay = controller.record_call_receipt(
            order["work_order_id"], receipt
        )
        self.assertEqual("RECORDED", replay["status"])
        self.assertTrue(evidence.is_file())
        evidence.write_bytes(b"{}\n")
        with self.assertRaisesRegex(
            self.loopctl.IdentityError, "CALL_RECEIPT_EVIDENCE_DRIFT"
        ):
            controller.record_call_receipt(order["work_order_id"], receipt)

    def test_unresolved_call_reservation_is_visible_and_requires_owner(self):
        controller = self.controller()
        order = self._create_order(controller)
        first = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("orphan-call")
        )
        self.assertTrue(first["allow_call"])
        exact = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("orphan-call")
        )
        self.assertEqual("CALL_IN_FLIGHT", exact["reason"])
        available = {
            "jobs": [],
            "providers": {
                "codex": "AVAILABLE",
                "windows-task-scheduler": "AVAILABLE",
            },
        }
        checked = self._doctor_with_inventory(controller, available)
        self.assertEqual("FAIL", checked["status"])
        self.assertTrue(
            any(
                item.startswith("CALL_RESERVATION_IN_FLIGHT:")
                for item in checked["checks"]["call_ledger"]
            )
        )
        controller.now_fn = lambda: "2026-07-14T14:00:00Z"
        different = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("next-call")
        )
        self.assertEqual("OWNER_DECISION_REQUIRED", different["event"])
        self.assertEqual("MAX_WALL_SECONDS", different["reason"])

    def test_completed_call_archive_survives_rebuild_and_detects_deletion(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.check_model_call(
            order["work_order_id"], self._call_telemetry("archived-call")
        )
        recorded = controller.record_call_receipt(
            order["work_order_id"], self._receipt_for(order, "archived-call")
        )
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SUCCESS",
            event_id="event-complete-call-archive",
        )
        self.assertEqual("FEATURE_DONE", controller.consume_event(event)["status"])
        before = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(1, before["call_receipt_archive"]["count"])
        self.assertEqual("PASS", controller.rebuild()["status"])
        after = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(
            before["call_receipt_archive"], after["call_receipt_archive"]
        )
        evidence = self.repo / Path(
            *PurePosixPath(recorded["evidence_path"]).parts
        )
        evidence.unlink()
        available = {
            "jobs": [],
            "providers": {
                "codex": "AVAILABLE",
                "windows-task-scheduler": "AVAILABLE",
            },
        }
        self.assertEqual(
            "FAIL", self._doctor_with_inventory(controller, available)["status"]
        )
    def test_call_receipt_is_validated_and_cache_drift_blocks_replay(self):
        controller = self.controller()
        order = self._create_order(controller)
        work_order = controller.verify_work_order(order["work_order_id"])
        contract = self.loopctl._load_v7_contract()
        initial = controller.check_model_call(order["work_order_id"], {
            "action_class": work_order["action_class"],
            "attempt": 0,
            "call_id": "call-1",
            "elapsed_seconds": 0,
            "model_calls": 0,
            "objective_satisfied": False,
            "prompt_prefix_sha256": "a" * 64,
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        })
        self.assertTrue(initial["allow_call"])
        self.assertEqual("RESERVED", initial["reservation_status"])
        receipt = contract.build_call_receipt(
            action_class="implementation",
            attempt=0,
            call_id="call-1",
            compaction_generation=0,
            sequence=1,
            token_usage="Unknown",
            work_order_sha256=order["work_order_sha256"],
            pre_prompt_prefix_sha256="a" * 64,
            post_prompt_prefix_sha256="a" * 64,
            pre_tool_schema_sha256="b" * 64,
            post_tool_schema_sha256="b" * 64,
        )
        recorded = controller.record_call_receipt(order["work_order_id"], receipt)
        self.assertEqual("RECORDED", recorded["status"])
        gate = controller.check_model_call(order["work_order_id"], {
            "action_class": work_order["action_class"],
            "attempt": 1,
            "call_id": "call-2",
            "elapsed_seconds": 2,
            "model_calls": 1,
            "objective_satisfied": False,
            "prompt_prefix_sha256": "c" * 64,
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        })
        self.assertFalse(gate["allow_call"])
        self.assertEqual("CACHE_PREFIX_CHANGED", gate["event"])
        later = controller.check_model_call(order["work_order_id"], {
            "action_class": work_order["action_class"],
            "attempt": 1,
            "call_id": "call-3",
            "elapsed_seconds": 2,
            "model_calls": 1,
            "objective_satisfied": False,
            "prompt_prefix_sha256": "a" * 64,
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        })
        self.assertFalse(later["allow_call"])
        self.assertEqual("WORK_ORDER_NOT_ACTIVE", later["reason"])
        malformed = dict(receipt)
        malformed["call_id"] = "call-2"
        malformed["prompt_prefix_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(self.loopctl.IdentityError, "CALL_RECEIPT_INVALID"):
            controller.record_call_receipt(order["work_order_id"], malformed)

    def test_worker_free_text_cannot_authorize_cache_contract_drift(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.check_model_call(order["work_order_id"], self._call_telemetry("call-stable"))
        controller.record_call_receipt(
            order["work_order_id"], self._receipt_for(order, "call-stable")
        )
        changed = self._call_telemetry("call-changed")
        changed.update(
            {
                "attempt": 1,
                "intentional_change_reason": "worker says this was reviewed",
                "prompt_prefix_sha256": "c" * 64,
            }
        )
        stopped = controller.check_model_call(order["work_order_id"], changed)
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("CACHE_PREFIX_CHANGED", stopped["event"])

    def test_drifted_call_receipt_records_pre_call_reservation_and_stops_replay(self):
        controller = self.controller()
        order = self._create_order(controller)
        gate = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("call-drifted")
        )
        self.assertTrue(gate["allow_call"])
        receipt = self.loopctl._load_v7_contract().build_call_receipt(
            action_class="implementation",
            attempt=0,
            call_id="call-drifted",
            compaction_generation=1,
            sequence=1,
            token_usage="Unknown",
            work_order_sha256=order["work_order_sha256"],
            pre_prompt_prefix_sha256="a" * 64,
            post_prompt_prefix_sha256="c" * 64,
            pre_tool_schema_sha256="b" * 64,
            post_tool_schema_sha256="b" * 64,
        )
        recorded = controller.record_call_receipt(order["work_order_id"], receipt)
        self.assertEqual("RECORDED", recorded["status"])
        replay = self._call_telemetry("call-after-drift")
        replay["attempt"] = 1
        replay["prompt_prefix_sha256"] = "c" * 64
        stopped = controller.check_model_call(order["work_order_id"], replay)
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("OWNER_DECISION_REQUIRED", stopped["event"])
        self.assertEqual("WORK_ORDER_NOT_ACTIVE", stopped["reason"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                "RECORDED",
                connection.execute(
                    "SELECT status FROM call_reservations WHERE call_id='call-drifted'"
                ).fetchone()[0],
            )
        finally:
            connection.close()

    def _call_telemetry(self, call_id, model_calls=0):
        return {
            "action_class": "implementation",
            "attempt": 0,
            "call_id": call_id,
            "elapsed_seconds": 0,
            "model_calls": model_calls,
            "objective_satisfied": False,
            "prompt_prefix_sha256": "a" * 64,
            "token_usage": "Unknown",
            "tool_schema_sha256": "b" * 64,
        }

    def _receipt_for(self, order, call_id, *, attempt=0, sequence=1):
        return self.loopctl._load_v7_contract().build_call_receipt(
            action_class="implementation",
            attempt=attempt,
            call_id=call_id,
            compaction_generation=0,
            sequence=sequence,
            token_usage="Unknown",
            work_order_sha256=order["work_order_sha256"],
            pre_prompt_prefix_sha256="a" * 64,
            post_prompt_prefix_sha256="a" * 64,
            pre_tool_schema_sha256="b" * 64,
            post_tool_schema_sha256="b" * 64,
        )

    def test_call_ledger_derives_limits_and_keeps_ten_receipts_under_snapshot_cap(self):
        controller = self.controller()
        order = self._create_order(controller)
        for index in range(10):
            call_id = f"call-{index}"
            gate = controller.check_model_call(
                order["work_order_id"],
                self._call_telemetry(call_id, model_calls=0),
            )
            self.assertTrue(gate["allow_call"])
            self.assertEqual(index, gate["authoritative_model_calls"])
            controller.record_call_receipt(
                order["work_order_id"],
                self._receipt_for(order, call_id, sequence=index + 1),
            )
            self.assertLessEqual(controller.snapshot_path.stat().st_size, 8192)
        exhausted = controller.check_model_call(
            order["work_order_id"],
            self._call_telemetry("call-10", model_calls=0),
        )
        self.assertFalse(exhausted["allow_call"])
        self.assertEqual("MAX_MODEL_CALLS", exhausted["reason"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                10,
                connection.execute(
                    "SELECT COUNT(*) FROM call_receipts WHERE work_order_id=?",
                    (order["work_order_id"],),
                ).fetchone()[0],
            )
        finally:
            connection.close()

    def test_call_sequence_is_authoritative_and_latest_metric_cannot_rewind(self):
        controller = self.controller()
        order = self._create_order(controller)
        first_gate = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("ordered-1")
        )
        self.assertEqual(1, first_gate["call_sequence"])
        first_receipt = self._receipt_for(order, "ordered-1", sequence=1)
        controller.record_call_receipt(order["work_order_id"], first_receipt)

        second_telemetry = self._call_telemetry("ordered-2")
        second_telemetry["attempt"] = 2
        second_gate = controller.check_model_call(
            order["work_order_id"], second_telemetry
        )
        self.assertEqual(2, second_gate["call_sequence"])
        second_receipt = self._receipt_for(
            order, "ordered-2", attempt=2, sequence=2
        )
        controller.record_call_receipt(order["work_order_id"], second_receipt)

        rewound = self._call_telemetry("ordered-3")
        rewound["attempt"] = 1
        stopped = controller.check_model_call(order["work_order_id"], rewound)
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("STOP_TELEMETRY_REWIND:attempt", stopped["reason"])

        def rewind_latest_metric(connection):
            connection.execute(
                "UPDATE metrics SET value=? WHERE key=?",
                (
                    json.dumps(first_receipt, sort_keys=True, separators=(",", ":")),
                    f"call-latest:{order['work_order_id']}",
                ),
            )

        controller._mutate(rewind_latest_metric)
        available = {
            "jobs": [],
            "providers": {
                "codex": "AVAILABLE",
                "windows-task-scheduler": "AVAILABLE",
            },
        }
        self.assertEqual("FAIL", self._doctor_with_inventory(controller, available)["status"])

    def test_call_reservation_is_single_inflight_and_concurrency_safe(self):
        controller = self.controller()
        order = self._create_order(controller)
        work_order_id = order["work_order_id"]

        def reserve(call_id):
            return controller.check_model_call(
                work_order_id, self._call_telemetry(call_id)
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(reserve, ("race-a", "race-b")))
        self.assertEqual(1, sum(result["allow_call"] for result in results))
        denied = next(result for result in results if not result["allow_call"])
        self.assertEqual("CALL_IN_FLIGHT", denied["reason"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM call_reservations "
                    "WHERE work_order_id=? AND status='RESERVED'",
                    (work_order_id,),
                ).fetchone()[0],
            )
            self.assertEqual(
                ("CREATED", "REGISTERED"),
                connection.execute(
                    "SELECT wo.status,t.status FROM work_orders wo "
                    "JOIN tasks t ON t.task_id=wo.task_id "
                    "WHERE wo.work_order_id=?",
                    (work_order_id,),
                ).fetchone(),
            )
        finally:
            connection.close()

    def test_max_one_call_cannot_be_bypassed_by_rewound_telemetry(self):
        controller = self.controller()
        stop = self._stop()
        stop["max_model_calls"] = 1
        order = self._create_order(controller, stop=stop)
        allowed = controller.check_model_call(
            order["work_order_id"], self._call_telemetry("only-call")
        )
        self.assertTrue(allowed["allow_call"])
        controller.record_call_receipt(
            order["work_order_id"], self._receipt_for(order, "only-call")
        )
        stopped = controller.check_model_call(
            order["work_order_id"],
            self._call_telemetry("forbidden-call", model_calls=0),
        )
        self.assertFalse(stopped["allow_call"])
        self.assertEqual("MAX_MODEL_CALLS", stopped["reason"])
        self.assertEqual(1, stopped["authoritative_model_calls"])

    def test_v7_rebuild_preserves_pending_action_bytes_and_identity(self):
        controller = self.controller()
        order = self._create_order(controller)
        before = controller.action_path.read_bytes()
        before_action = json.loads(before)

        rebuilt = controller.rebuild()

        self.assertEqual("PASS", rebuilt["status"])
        after = controller.action_path.read_bytes()
        self.assertEqual(before, after)
        self.assertEqual(
            before_action["action_id"],
            json.loads(after)["action_id"],
        )
        self.assertEqual(
            order["dispatch_id"],
            json.loads(after)["dispatch_id"],
        )

    def test_v7_rebuild_upgrades_legacy_mixed_outbox_and_keeps_pending_action(self):
        capacity = load_snapshot_capacity()
        controller = self.controller()
        completed = self._create_order(controller)
        controller.record_delivery(
            completed["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            completed,
            outcome="SUCCESS",
            event_id="event-legacy-mixed-outbox-complete",
        )
        self.assertEqual("FEATURE_DONE", controller.consume_event(event)["status"])
        run("git", "add", ".devad/workers", cwd=self.repo)
        run("git", "commit", "-m", "complete first fixture", cwd=self.repo)
        self.base_sha = run("git", "rev-parse", "HEAD", cwd=self.repo)

        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-b",
                "features": ["feature-b"],
            },
        )
        pending = controller.create_work_order(
            program_id="program-b",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        decoded = self._decode_v3_snapshot(controller)
        tables = json.loads(json.dumps(decoded["tables"]))
        tables["outbox"] = [
            row
            for row in tables["outbox"]
            if row["dispatch_id"] != pending["dispatch_id"]
        ]
        self.assertEqual(1, len(tables["outbox"]))

        current_root = json.loads(controller.snapshot_path.read_bytes())
        legacy_seed = json.loads(json.dumps(current_root))
        legacy_seed.pop("active_layout")
        legacy_bundle = capacity.build_bundle(
            generation=decoded["generation"],
            columns=self.loopctl.SNAPSHOT_COLUMNS,
            tables=tables,
            recovery_worktrees=decoded["recovery_worktrees"],
            completed_task_ids=decoded["completed_task_ids"],
            dispatch_attempts=decoded["dispatch_attempts"],
            call_receipt_archive=decoded["call_receipt_archive"],
            current_snapshot_raw=capacity.canonical_bytes(legacy_seed),
        )
        generation_dir = (
            controller.root
            / "snapshots"
            / "generations"
            / str(decoded["generation"])
        )
        preserved_generation = generation_dir.with_name(
            generation_dir.name + "-pre-legacy-fixture"
        )
        os.replace(generation_dir, preserved_generation)
        controller._write_snapshot_bundle(legacy_bundle)

        connection = controller._connect()
        try:
            self.assertTrue(
                controller._snapshot_matches_connection(
                    connection, legacy_bundle["root_raw"]
                )
            )
        finally:
            connection.close()

        self.assertEqual("PASS", controller.rebuild()["status"])
        upgraded = json.loads(controller.snapshot_path.read_bytes())
        self.assertEqual(capacity.ACTIVE_LAYOUT, upgraded["active_layout"])
        self.assertEqual(decoded["generation"] + 1, upgraded["generation"])
        first_action = controller.action_path.read_bytes()
        self.assertEqual(
            pending["dispatch_id"],
            json.loads(first_action)["dispatch_id"],
        )
        self.assertEqual("PASS", controller.rebuild()["status"])
        self.assertEqual(first_action, controller.action_path.read_bytes())

    def test_v7_rebuild_restores_action_ledger_and_post_rebuild_calls(self):
        controller = self.controller()
        order = self._create_order(controller)
        first_rebuild = controller.rebuild()
        self.assertEqual("PASS", first_rebuild["status"])
        self.assertEqual(
            "x9-loop-action-v2",
            json.loads(controller.action_path.read_text(encoding="utf-8"))["schema"],
        )
        controller.check_model_call(
            order["work_order_id"], self._call_telemetry("before-rebuild")
        )
        controller.record_call_receipt(
            order["work_order_id"],
            self._receipt_for(order, "before-rebuild"),
        )
        second_rebuild = controller.rebuild()
        self.assertEqual("PASS", second_rebuild["status"])
        next_gate = controller.check_model_call(
            order["work_order_id"],
            self._call_telemetry("after-rebuild", model_calls=0),
        )
        self.assertTrue(next_gate["allow_call"])
        self.assertEqual(1, next_gate["authoritative_model_calls"])
        controller.record_call_receipt(
            order["work_order_id"],
            self._receipt_for(order, "after-rebuild", sequence=2),
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                2,
                connection.execute(
                    "SELECT COUNT(*) FROM call_receipts WHERE work_order_id=?",
                    (order["work_order_id"],),
                ).fetchone()[0],
            )
        finally:
            connection.close()

    def test_doctor_core_is_scheduler_independent_and_external_gate_is_separate(self):
        controller = self.controller()
        controller.init()
        before = {
            "db": controller.db_path.read_bytes(),
            "snapshot": controller.snapshot_path.read_bytes(),
            "approved": controller.approved_jobs_path.read_bytes(),
        }
        available = {
            "jobs": [],
            "providers": {"codex": "AVAILABLE", "windows-task-scheduler": "AVAILABLE"},
        }
        healthy = self._doctor_with_inventory(controller, available)
        self.assertEqual("PASS", healthy["status"])
        self.assertTrue(healthy["checks"]["jobs"]["core_loop_ready"])
        self.assertIsNone(healthy["checks"]["jobs"]["external_wake_ready"])
        unknown = self._doctor_with_inventory(
            controller,
            {
                "jobs": [],
                "providers": {
                    "codex": "UNKNOWN",
                    "windows-task-scheduler": "UNKNOWN",
                },
            },
        )
        self.assertEqual("PASS", unknown["status"])
        unexpected = {
            "jobs": [{
                "provider": "codex",
                "job_id": "sk-secret-job",
                "command_hash": "c" * 64,
                "schedule_hash": "d" * 64,
                "relevance": "CURRENT_PROJECT_MONITOR",
            }],
            "providers": available["providers"],
        }
        disabled = self._doctor_with_inventory(controller, unexpected)
        self.assertEqual("PASS", disabled["status"])
        self.assertIsNone(disabled["checks"]["jobs"]["external_wake_ready"])
        self.assertNotIn("sk-secret-job", json.dumps(disabled))
        self.assertEqual(before["db"], controller.db_path.read_bytes())
        self.assertEqual(before["snapshot"], controller.snapshot_path.read_bytes())
        self.assertEqual(before["approved"], controller.approved_jobs_path.read_bytes())

        unrelated = self._doctor_with_inventory(
            controller,
            {
                "jobs": [{
                    "provider": "windows-task-scheduler",
                    "job_id": "windows-maintenance",
                    "command_hash": "e" * 64,
                    "schedule_hash": "f" * 64,
                    "relevance": "UNRELATED_OS_JOB",
                }],
                "providers": available["providers"],
            },
        )
        self.assertEqual("PASS", unrelated["status"])
        self.assertEqual(
            "UNRELATED_OS_JOB",
            unrelated["checks"]["jobs"]["job_findings"][0]["status"],
        )

        profile_id = json.loads(controller.project_profile_path.read_bytes())[
            "project_profile_id"
        ]
        external_manifest = {
            "jobs": [{
                "provider": "codex",
                "job_id": "approved-monitor",
                "command_hash": "a" * 64,
                "schedule_hash": "b" * 64,
            }],
            "monitor_mode": "EXTERNAL",
            "project_profile_id": profile_id,
            "schema": "x9-loop-approved-jobs-v1",
        }
        controller.approved_jobs_path.write_bytes(
            self.loopctl._load_v7_contract().canonical_json_bytes(external_manifest)
        )
        external_drift = self._doctor_with_inventory(
            controller,
            {
                "jobs": [{
                    **external_manifest["jobs"][0],
                    "command_hash": "c" * 64,
                    "relevance": "CURRENT_PROJECT_MONITOR",
                }],
                "providers": {"codex": "AVAILABLE"},
            },
        )
        self.assertEqual("PASS", external_drift["status"])
        self.assertTrue(external_drift["checks"]["jobs"]["core_loop_ready"])
        self.assertFalse(external_drift["checks"]["jobs"]["external_wake_ready"])
        self.assertEqual(
            "COMMAND_DRIFT",
            external_drift["checks"]["jobs"]["unauthorized_jobs"][0]["status"],
        )

    def test_doctor_rejects_caller_supplied_job_inventory(self):
        controller = self.controller()
        codex_home = Path(self.temp.name) / "codex-home"
        automations = codex_home / "automations"
        automations.mkdir(parents=True)
        (automations / ".run-jitter-salt").write_text(
            "test salt\n", encoding="utf-8"
        )
        previous_home = os.environ.get("CODEX_HOME")
        os.environ["CODEX_HOME"] = str(codex_home)
        try:
            jobs, status = controller._inventory_codex_recurring_jobs()
        finally:
            if previous_home is None:
                os.environ.pop("CODEX_HOME", None)
            else:
                os.environ["CODEX_HOME"] = previous_home
        self.assertEqual("AVAILABLE", status)
        self.assertEqual([], jobs)

        controller.init()
        fabricated = {
            "jobs": [],
            "providers": {
                "codex": "AVAILABLE",
                "windows-task-scheduler": "AVAILABLE",
            },
        }
        with self.assertRaises(TypeError):
            controller.doctor(job_inventory=fabricated)

    def test_doctor_preserves_precise_historical_missing_classification(self):
        write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        result = self._doctor_with_inventory(
            controller,
            {
                "jobs": [],
                "providers": {
                    "codex": "AVAILABLE",
                    "windows-task-scheduler": "AVAILABLE",
                },
            },
        )
        self.assertEqual("PASS", result["status"])
        self.assertEqual(["core-legacy"], result["checks"]["historical_missing"])
        self.assertEqual([], result["checks"]["worktrees"])

    def test_v6_status_only_handover_receipt_is_historical_not_v7_completion(self):
        write_v1_state(self.repo, self.base_sha)
        receipt_dir = (
            self.repo / ".devad" / "workers" / "worker" / "receipts"
        )
        receipt_dir.mkdir(parents=True)
        receipt_path = receipt_dir / "hsr-current-worker.json"
        legacy_receipt = {
            "schema": "x9-v6-status-only-handover-receipt-v1",
            "status_request_id": "hsr-current-worker",
            "mode": "STATUS_ONLY_HANDOVER",
            "worker_thread_actor_id": "worker",
            "real_role": "WORKER",
        }
        receipt_path.write_text(
            json.dumps(legacy_receipt, indent=2), encoding="utf-8"
        )
        nested_receipt = {
            "schema": "x9-v6-status-only-handover-receipt-v1",
            "status_request_id": "hsr-nested-worker",
            "mode": "STATUS_ONLY_HANDOVER",
            "worker": {"thread_actor_id": "worker", "real_role": "WORKER"},
        }
        (receipt_dir / "hsr-nested-worker.json").write_text(
            json.dumps(nested_receipt, indent=2),
            encoding="utf-8",
        )

        controller = self.controller()
        controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        inventory = {
            "jobs": [],
            "providers": {
                "codex": "AVAILABLE",
                "windows-task-scheduler": "AVAILABLE",
            },
        }

        result = self._doctor_with_inventory(controller, inventory)
        self.assertEqual("PASS", result["status"])
        self.assertEqual([], result["checks"]["receipts"])
        self.assertEqual([], result["checks"]["recovery"])

        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        forged_path = receipt_dir / "hsr-forged-after-dispatch.json"
        forged_path.write_text(
            json.dumps(
                {
                    "schema": "x9-v6-status-only-handover-receipt-v1",
                    "status_request_id": "hsr-forged-after-dispatch",
                    "mode": "STATUS_ONLY_HANDOVER",
                    "worker_thread_actor_id": "worker",
                    "real_role": "WORKER",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SUCCESS",
            event_id="event-after-v6-handover",
        )
        with self.assertRaisesRegex(
            self.loopctl.StateNotDurableError, "RECEIPT_SET_MISMATCH"
        ):
            controller.consume_event(event)
        forged_path.unlink()
        self.assertEqual("FEATURE_DONE", controller.consume_event(event)["status"])
        after_event = self._doctor_with_inventory(controller, inventory)
        self.assertEqual("PASS", after_event["status"])
        self.assertEqual([], after_event["checks"]["receipts"])

        legacy_receipt["schema"] = "unknown-receipt-v1"
        receipt_path.write_text(
            json.dumps(legacy_receipt, indent=2), encoding="utf-8"
        )
        rejected = self._doctor_with_inventory(controller, inventory)
        self.assertEqual("FAIL", rejected["status"])
        self.assertTrue(rejected["checks"]["receipts"])
        self.assertTrue(rejected["checks"]["recovery"])

    def test_verify_work_order_rejects_cross_order_packet_substitution(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-a",
                "features": ["feature-a", "feature-b"],
            },
        )
        first = controller.create_work_order(
            program_id="program-a",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        controller._transition_task_state(first["task_id"], "COMPLETE")
        second = controller.create_work_order(
            program_id="program-a",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            connection.execute(
                "UPDATE work_orders SET packet_path=?,packet_sha256=? WHERE work_order_id=?",
                (
                    second["work_order_path"],
                    second["work_order_sha256"],
                    first["work_order_id"],
                ),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaisesRegex(
            self.loopctl.IdentityError,
            "WORK_ORDER_DRIFT:(work_order_id|task_id)",
        ):
            controller.verify_work_order(first["work_order_id"])

    def test_doctor_rejects_snapshot_drift_and_missing_active_action(self):
        controller = self.controller()
        self._create_order(controller)
        available = {
            "jobs": [],
            "providers": {"codex": "AVAILABLE", "windows-task-scheduler": "AVAILABLE"},
        }
        original_snapshot = controller.snapshot_path.read_bytes()
        snapshot = json.loads(original_snapshot)
        snapshot["active_detail_summaries"]["work_orders"] = []
        controller.snapshot_path.write_bytes(
            self.loopctl._load_v7_contract().canonical_json_bytes(snapshot)
        )
        drifted = self._doctor_with_inventory(controller, available)
        self.assertEqual("FAIL", drifted["status"])
        self.assertEqual("FAIL", drifted["checks"]["snapshot"])
        controller.snapshot_path.write_bytes(original_snapshot)
        controller.action_path.unlink()
        missing_action = self._doctor_with_inventory(controller, available)
        self.assertEqual("FAIL", missing_action["status"])
        self.assertEqual("FAIL", missing_action["checks"]["action"])
        self.assertFalse(controller.action_path.exists())
        controller._write_action(controller._current_action())
        action = json.loads(controller.action_path.read_text(encoding="utf-8"))
        action["dispatch_id"] = "dsp-bogus"
        controller.action_path.write_bytes(
            self.loopctl._load_v7_contract().canonical_json_bytes(action)
        )
        tampered_action = self._doctor_with_inventory(controller, available)
        self.assertEqual("FAIL", tampered_action["status"])
        self.assertEqual("FAIL", tampered_action["checks"]["action"])

    def test_doctor_accepts_acknowledged_delivery_wait_action(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        action = json.loads(controller.action_path.read_text(encoding="utf-8"))
        self.assertEqual("WAIT", action["action"])
        self.assertEqual("delivery-acknowledged", action["reason"])

        available = {
            "jobs": [],
            "providers": {
                "codex": "AVAILABLE",
                "windows-task-scheduler": "AVAILABLE",
            },
        }
        result = self._doctor_with_inventory(controller, available)
        self.assertEqual("PASS", result["status"])
        self.assertEqual("PASS", result["checks"]["action"])

    def test_doctor_validates_work_order_dispatch_and_call_ledger_semantics(self):
        available = {
            "jobs": [],
            "providers": {"codex": "AVAILABLE", "windows-task-scheduler": "AVAILABLE"},
        }

        controller = self.controller()
        order = self._create_order(controller)
        (self.repo / order["work_order_path"]).unlink()
        missing_order = self._doctor_with_inventory(controller, available)
        self.assertEqual("FAIL", missing_order["status"])
        self.assertTrue(missing_order["checks"]["work_orders"])

        with self.subTest("forged outbox"):
            other_temp = tempfile.TemporaryDirectory()
            self.addCleanup(other_temp.cleanup)
            other_repo = Path(other_temp.name) / "repo"
            other_base = git_repo(other_repo)
            old_repo, old_base = self.repo, self.base_sha
            self.repo, self.base_sha = other_repo, other_base
            try:
                forged_controller = self.controller()
                forged_order = self._create_order(forged_controller)
                forged = json.loads(
                    forged_controller.action_path.read_text(encoding="utf-8")
                )
                forged["target_actor_id"] = "bogus"
                forged["target_role"] = "THINX"

                def forge_outbox(connection):
                    connection.execute(
                        "UPDATE outbox SET payload=? WHERE dispatch_id=?",
                        (
                            json.dumps(
                                forged, sort_keys=True, separators=(",", ":")
                            ),
                            forged_order["dispatch_id"],
                        ),
                    )

                forged_controller._mutate(forge_outbox)
                forged_controller._write_action(forged)
                forged_result = self._doctor_with_inventory(
                    forged_controller, available
                )
                self.assertEqual("FAIL", forged_result["status"])
                self.assertTrue(
                    forged_result["checks"]["dispatch_identity"]
                )
            finally:
                self.repo, self.base_sha = old_repo, old_base

        with self.subTest("tampered call row"):
            other_temp = tempfile.TemporaryDirectory()
            self.addCleanup(other_temp.cleanup)
            other_repo = Path(other_temp.name) / "repo"
            other_base = git_repo(other_repo)
            old_repo, old_base = self.repo, self.base_sha
            self.repo, self.base_sha = other_repo, other_base
            try:
                call_controller = self.controller()
                call_order = self._create_order(call_controller)
                call_controller.check_model_call(
                    call_order["work_order_id"],
                    self._call_telemetry("doctor-call"),
                )
                call_controller.record_call_receipt(
                    call_order["work_order_id"],
                    self._receipt_for(call_order, "doctor-call"),
                )
                connection = sqlite3.connect(call_controller.db_path)
                try:
                    connection.execute(
                        "UPDATE call_receipts SET receipt=?,receipt_sha256=? "
                        "WHERE call_id='doctor-call'",
                        ("{}", hashlib.sha256(b"{}\n").hexdigest()),
                    )
                    connection.commit()
                finally:
                    connection.close()
                tampered = self._doctor_with_inventory(call_controller, available)
                self.assertEqual("FAIL", tampered["status"])
                self.assertTrue(tampered["checks"]["call_ledger"])
            finally:
                self.repo, self.base_sha = old_repo, old_base

    def test_migration_rejects_unknown_sqlite_objects(self):
        write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        connection = sqlite3.connect(controller.db_path)
        try:
            connection.execute("CREATE TABLE shadow_state(secret TEXT)")
            connection.execute("INSERT INTO shadow_state VALUES('kept')")
            connection.commit()
        finally:
            connection.close()
        with self.assertRaisesRegex(
            self.loopctl.StateNotDurableError, "V6_DATABASE_INVALID"
        ):
            controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("kept",),
                connection.execute("SELECT secret FROM shadow_state").fetchone(),
            )
        finally:
            connection.close()
        self.assertFalse(controller.migration_state_path.exists())

    def test_v7_database_fences_legacy_insert_and_update_writers(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        migrated = controller.migrate_v1_to_v2(
            {"core-legacy": "a" * 64}
        )

        for statement in (
            "INSERT OR IGNORE INTO meta(key,value) "
            "VALUES('generation','0')",
            "UPDATE meta SET value='99' WHERE key='generation'",
        ):
            connection = sqlite3.connect(
                controller.db_path, isolation_level=None
            )
            try:
                connection.execute("BEGIN IMMEDIATE")
                with self.assertRaises(sqlite3.OperationalError):
                    connection.execute(statement)
                connection.rollback()
            finally:
                connection.close()

        controller.register_actor(
            "worker-fenced", "WORKER", "AI - WORKER Fenced", "Unknown"
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("WORKER",),
                connection.execute(
                    "SELECT role FROM actors WHERE actor_id='worker-fenced'"
                ).fetchone(),
            )
            self.assertEqual(
                {
                    "x9_v7_write_fence_insert",
                    "x9_v7_write_fence_update",
                },
                {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='trigger'"
                    )
                },
            )
        finally:
            connection.close()

        controller.rollback_to_v6(migrated["recovery_id"])
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(
            original["SNAPSHOT.json"], controller.snapshot_path.read_bytes()
        )
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                [],
                connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger'"
                ).fetchall(),
            )
        finally:
            connection.close()

    def test_prepared_crash_preserves_coherent_newer_active_v6(self):
        write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        code = f"""
import importlib.util
import json
import os
import sqlite3
import sys
from pathlib import Path, PurePosixPath
spec = importlib.util.spec_from_file_location("loopctl_prepared_crash", r"{LOOPCTL}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
controller = module.Controller(Path(r"{self.repo}"))
def crash_before_fence(expected_snapshot):
    connection = sqlite3.connect(controller.db_path)
    try:
        connection.execute(
            "UPDATE actors SET title='AI - LINX v7' WHERE actor_id='linx'"
        )
        connection.execute(
            "UPDATE meta SET value='8' WHERE key='generation'"
        )
        connection.commit()
    finally:
        connection.close()
    snapshot = json.loads(
        controller.snapshot_path.read_text(encoding="utf-8")
    )
    snapshot["generation"] = 8
    snapshot["tables"]["actors"][0]["title"] = "AI - LINX v7"
    controller.snapshot_path.write_text(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    os._exit(93)
controller._install_v6_write_fence = crash_before_fence
controller.migrate_v1_to_v2({{"core-legacy": "a" * 64}})
"""
        crashed = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(93, crashed.returncode, crashed.stderr)
        self.assertTrue(controller.migration_state_path.is_file())
        recovered = controller.recover_interrupted_migration()
        self.assertEqual("PRESERVED_ACTIVE_V6", recovered["status"])
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("AI - LINX v7",),
                connection.execute(
                    "SELECT title FROM actors WHERE actor_id='linx'"
                ).fetchone(),
            )
            self.assertEqual(
                "8",
                connection.execute(
                    "SELECT value FROM meta WHERE key='generation'"
                ).fetchone()[0],
            )
        finally:
            connection.close()
        self.assertEqual(
            8,
            json.loads(
                controller.snapshot_path.read_text(encoding="utf-8")
            )["generation"],
        )
        self.assertFalse(controller.migration_state_path.exists())
    def test_migration_failure_before_jobs_gate_preserves_exact_v1_state(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        controller.approved_jobs_path.write_bytes(b"{")
        with self.assertRaisesRegex(self.loopctl.StateNotDurableError, "APPROVED_JOBS_INVALID"):
            controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(original["SNAPSHOT.json"], controller.snapshot_path.read_bytes())
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(0, connection.execute("PRAGMA user_version").fetchone()[0])
        finally:
            connection.close()

    def test_migration_rejects_corrupt_v1_snapshot_and_concurrent_source_drift(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        snapshot = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
        snapshot["tables"] = {"tampered": []}
        controller.snapshot_path.write_text(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(self.loopctl.StateNotDurableError, "V6_SNAPSHOT_INVALID"):
            controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())

        controller.snapshot_path.write_bytes(original["SNAPSHOT.json"])
        original_manifest = controller._write_recovery_manifest

        def mutate_after_manifest(*args, **kwargs):
            original_manifest(*args, **kwargs)
            connection = sqlite3.connect(controller.db_path)
            try:
                connection.execute("INSERT INTO metrics VALUES('late-write','1')")
                connection.execute("UPDATE meta SET value='8' WHERE key='generation'")
                connection.commit()
            finally:
                connection.close()
            current = json.loads(controller.snapshot_path.read_text(encoding="utf-8"))
            current["generation"] = 8
            current["tables"]["metrics"].append({"key": "late-write", "value": "1"})
            controller.snapshot_path.write_text(
                json.dumps(current, sort_keys=True, separators=(",", ":")),
                encoding="utf-8",
            )

        controller._write_recovery_manifest = mutate_after_manifest
        try:
            with self.assertRaisesRegex(self.loopctl.StateNotDurableError, "V6_SOURCE_DRIFT"):
                controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        finally:
            controller._write_recovery_manifest = original_manifest
        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                "1",
                connection.execute(
                    "SELECT value FROM metrics WHERE key='late-write'"
                ).fetchone()[0],
            )
        finally:
            connection.close()
        self.assertFalse(controller.migration_state_path.exists())
        self.assertEqual("NONE", controller.recover_interrupted_migration()["status"])
        self.assertTrue(controller.db_path.exists())

    def test_migration_interrupt_restores_complete_v1_set(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        original_replace = self.loopctl.os.replace

        def interrupt_snapshot_move(source, destination):
            if (
                Path(source) == controller.snapshot_path
                and Path(destination).name == "active-SNAPSHOT.json"
            ):
                raise KeyboardInterrupt()
            return original_replace(source, destination)

        self.loopctl.os.replace = interrupt_snapshot_move
        try:
            with self.assertRaises(KeyboardInterrupt):
                controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        finally:
            self.loopctl.os.replace = original_replace
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(original["SNAPSHOT.json"], controller.snapshot_path.read_bytes())

    def _run_crash_child(self, controller, operation, recovery_id=None):
        code = f"""
import importlib.util
import os
import sys
from pathlib import Path, PurePosixPath
spec = importlib.util.spec_from_file_location("loopctl_crash_child", r"{LOOPCTL}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
controller = module.Controller(Path(r"{self.repo}"))
original = module.os.replace
def crash(source, destination):
    source = Path(source)
    destination = Path(destination)
    if {operation!r} == "migrate":
        hit = source == controller.snapshot_path and destination.name == "active-SNAPSHOT.json"
    else:
        hit = source == controller.snapshot_path and destination.name == "SNAPSHOT.json" and "v7-failed-" in str(destination.parent)
    if hit:
        os._exit(91)
    return original(source, destination)
module.os.replace = crash
if {operation!r} == "migrate":
    controller.migrate_v1_to_v2({{"core-legacy": "a" * 64}})
else:
    controller.rollback_to_v6({recovery_id!r})
"""
        return subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_process_death_during_migration_recovers_exact_v1_on_next_entry(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        crashed = self._run_crash_child(controller, "migrate")
        self.assertEqual(91, crashed.returncode, crashed.stderr)
        self.assertTrue(controller.migration_state_path.is_file())
        recovered = controller.recover_interrupted_migration()
        self.assertEqual("RECOVERED", recovered["status"])
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(original["SNAPSHOT.json"], controller.snapshot_path.read_bytes())
        self.assertFalse(controller.migration_state_path.exists())

    def test_process_death_during_rollback_recovers_exact_v1_on_next_entry(self):
        original = write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        migrated = controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        crashed = self._run_crash_child(
            controller, "rollback", migrated["recovery_id"]
        )
        self.assertEqual(91, crashed.returncode, crashed.stderr)
        self.assertTrue(controller.migration_state_path.is_file())
        recovered = controller.recover_interrupted_migration()
        self.assertEqual("RECOVERED", recovered["status"])
        self.assertEqual(original["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(original["SNAPSHOT.json"], controller.snapshot_path.read_bytes())
        self.assertFalse(controller.migration_state_path.exists())

    def test_rollback_rejects_incomplete_manifest_without_touching_v7(self):
        write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        migrated = controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        active = {
            "loop.db": controller.db_path.read_bytes(),
            "SNAPSHOT.json": controller.snapshot_path.read_bytes(),
        }
        recovery = controller.root / "recovery" / migrated["recovery_id"]
        manifest_path = recovery / "RECOVERY.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = [row for row in manifest["files"] if row["name"] == "SNAPSHOT.json"]
        manifest_path.write_bytes(
            self.loopctl._load_v7_contract().canonical_json_bytes(manifest)
        )
        with self.assertRaisesRegex(self.loopctl.StateNotDurableError, "RECOVERY_MANIFEST_INVALID"):
            controller.rollback_to_v6(migrated["recovery_id"])
        self.assertEqual(active["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(active["SNAPSHOT.json"], controller.snapshot_path.read_bytes())

    def test_rollback_write_failure_restores_complete_v7_set(self):
        write_v1_state(self.repo, self.base_sha)
        controller = self.controller()
        migrated = controller.migrate_v1_to_v2({"core-legacy": "a" * 64})
        active = {
            "loop.db": controller.db_path.read_bytes(),
            "SNAPSHOT.json": controller.snapshot_path.read_bytes(),
            "APPROVED_JOBS.json": controller.approved_jobs_path.read_bytes(),
        }
        original_write = controller._atomic_state_write
        calls = {"count": 0}

        def fail_second_write(path, data):
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("injected rollback failure")
            return original_write(path, data)

        controller._atomic_state_write = fail_second_write
        try:
            with self.assertRaises(self.loopctl.StateNotDurableError):
                controller.rollback_to_v6(migrated["recovery_id"])
        finally:
            controller._atomic_state_write = original_write
        self.assertEqual(active["loop.db"], controller.db_path.read_bytes())
        self.assertEqual(active["SNAPSHOT.json"], controller.snapshot_path.read_bytes())
        self.assertEqual(active["APPROVED_JOBS.json"], controller.approved_jobs_path.read_bytes())

    def test_success_candidate_creates_receipt_bound_dirty_successor(self):
        controller = self.controller()
        controller.init()
        self._register_v7_actors(controller)
        feature_a = self._feature("feature-a")
        feature_b = self._feature("feature-b")
        feature_b["dependencies"] = ["feature-a"]
        self._import_program(
            controller,
            {
                "feature_packets": [feature_a, feature_b],
                "features": ["feature-a", "feature-b"],
                "program_id": "program-candidate",
                "schema": "x9-loop-program-v1",
            },
        )
        first = controller.create_work_order(
            program_id="program-candidate",
            stop=self._stop(),
            linx_id="linx",
            action_class="implementation",
        )
        controller.record_delivery(
            first["dispatch_id"], "DISPATCH", "task", "ack"
        )
        source = self.repo / "src" / "a.py"
        source.write_text("A = 2\n", encoding="utf-8")
        source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        event = self._write_v7_worker_event(
            controller,
            first,
            changed_files=("src/a.py",),
            outcome="SUCCESS_CANDIDATE",
            event_id="event-success-candidate",
        )
        consumed = controller.run_once(
            self._write_v7_worker_outbox_event(controller, event)
        )

        self.assertEqual("FEATURE_DONE", consumed["status"])
        self.assertEqual("CREATED", consumed["continuation"]["status"])
        result_ready_path, emitted = self._write_v7_worker_result_ready(
            controller, event
        )
        result_ready_raw = result_ready_path.read_bytes()
        signal = json.loads(result_ready_raw)
        connection = controller._connect()
        try:
            sender_id = connection.execute(
                "SELECT sender_id FROM dispatches WHERE dispatch_id=?",
                (first["dispatch_id"],),
            ).fetchone()[0]
            self.assertEqual("CONSUMED", connection.execute(
                "SELECT status FROM inbox WHERE event_id=?", (event["event_id"],)
            ).fetchone()[0])
        finally:
            connection.close()
        self.assertEqual(sender_id, signal["return_to_task_id"])
        self.assertEqual(
            controller._result_ready_callback_id(
                signal["expected_result_identity"], sender_id
            ),
            signal["callback_id"],
        )
        action = json.loads(controller.action_path.read_bytes())
        successor_path = self.repo / Path(
            *PurePosixPath(action["work_order_path"]).parts
        )
        successor = json.loads(successor_path.read_bytes())
        self.assertEqual(
            {
                "files": [
                    {
                        "path": "src/a.py",
                        "sha256": source_sha256,
                        "state": "PRESENT",
                    }
                ],
                "schema": "x9-loop-candidate-handoff-v1",
                "source_base_sha": self.base_sha,
                "source_event_id": event["event_id"],
                "source_result_sha256": event["result_sha256"],
                "source_task_id": first["task_id"],
                "source_worker_id": "worker",
                "source_work_order_id": first["work_order_id"],
                "source_worktree_id": "core-x9",
                "source_worktree_path": str(self.repo),
            },
            successor["candidate_handoff"],
        )
        self.assertEqual(
            source_sha256,
            hashlib.sha256(source.read_bytes()).hexdigest(),
        )
        connection = controller._connect()
        try:
            controller._assert_v7_dispatch_preflight(
                connection, consumed["continuation"]["task_id"]
            )
        finally:
            connection.close()
        self.assertIn(
            ".devad/workers/worker/outbox/event-success-candidate/result_ready.json",
            controller._git_state("HEAD", self.repo)["untracked"],
        )
        tampered = json.loads(result_ready_raw)
        tampered["return_to_task_id"] = "wrong-requester"
        result_ready_path.write_bytes(
            self.loopctl._load_v7_contract().canonical_json_bytes(tampered)
        )
        before = self._controller_durable_state(controller)
        connection = controller._connect()
        try:
            with self.assertRaisesRegex(
                self.loopctl.StaleCompletionError, "RESULT_GIT_INVALID"
            ):
                controller._assert_v7_dispatch_preflight(
                    connection, consumed["continuation"]["task_id"]
                )
        finally:
            connection.close()
        self.assertEqual(before, self._controller_durable_state(controller))
        result_ready_path.write_bytes(result_ready_raw)
        connection = controller._connect()
        try:
            controller._assert_v7_dispatch_preflight(
                connection, consumed["continuation"]["task_id"]
            )
        finally:
            connection.close()
        unrelated = self.repo / "src" / "unrelated.py"
        unrelated.write_text("UNRELATED = True\n", encoding="utf-8")
        connection = controller._connect()
        try:
            with self.assertRaisesRegex(
                self.loopctl.TaskNotReadyError,
                "WORKTREE_NOT_CLEAN",
            ):
                controller._assert_v7_dispatch_preflight(
                    connection,
                    consumed["continuation"]["task_id"],
                )
        finally:
            connection.close()

    def test_result_consumption_ignores_superseded_prior_assignment(self):
        controller, inbox = self._program_assignment_result_scenario(
            "SUPERSEDED"
        )

        consumed = controller.run_once(inbox)

        self.assertEqual("FEATURE_DONE", consumed["status"])
        self.assertEqual("CREATED", consumed["continuation"]["status"])
        action = json.loads(controller.action_path.read_bytes())
        self.assertEqual("SEND_WORK_ORDER", action["action"])
        successor = json.loads(
            (
                self.repo
                / Path(*PurePosixPath(action["work_order_path"]).parts)
            ).read_bytes()
        )
        self.assertEqual(
            ["feature-b"],
            [
                ref["feature_id"]
                for ref in successor["feature_packet_refs"]
            ],
        )
        after = self._controller_durable_state(controller)
        self.assertEqual(
            "ALREADY_CONSUMED", controller.run_once(inbox)["status"]
        )
        self.assertEqual(after, self._controller_durable_state(controller))

    def test_two_non_superseded_assignments_fail_with_zero_state_delta(self):
        controller, inbox = self._program_assignment_result_scenario(
            "COMPLETE"
        )
        before = self._controller_durable_state(controller)

        with self.assertRaisesRegex(
            self.loopctl.IdentityError,
            "PROGRAM_FEATURE_ASSIGNMENT_INVALID",
        ):
            controller.run_once(inbox)

        self.assertEqual(before, self._controller_durable_state(controller))
    def test_success_candidate_requires_security_and_test_proofs(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        (self.repo / "src" / "a.py").write_text("A = 2\n", encoding="utf-8")
        event = self._write_v7_worker_event(
            controller,
            order,
            changed_files=("src/a.py",),
            outcome="SUCCESS_CANDIDATE",
            include_proofs=False,
            event_id="event-proofless-candidate",
        )

        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError, "RESULT_CANDIDATE_INVALID"
        ):
            controller.consume_event(event)

    def test_oversized_result_is_rejected_before_read(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SUCCESS",
            event_id="event-oversized-result",
        )
        result_path = self.repo / Path(
            *PurePosixPath(event["result_path"]).parts
        )
        oversized = b"x" * (
            self.loopctl._load_v7_contract().PACKET_CAPS["RESULT.json"] + 1
        )
        result_path.write_bytes(oversized)
        event["result_sha256"] = hashlib.sha256(oversized).hexdigest()
        original_read_bytes = Path.read_bytes

        def guarded_read_bytes(path):
            if path == result_path:
                raise AssertionError("oversized result must not be read")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
            with self.assertRaisesRegex(
                self.loopctl.StaleCompletionError, "RESULT_INVALID"
            ):
                controller.consume_event(event)

    def test_supersede_paused_is_receipt_bound_and_preserves_dirty_bytes(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        source = self.repo / "src" / "a.py"
        source.write_text("A = 2\n", encoding="utf-8")
        expected_bytes = source.read_bytes()
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SCOPE_CONFLICT",
            event_id="event-paused-dirty",
            changed_files=("src/a.py",),
        )
        self.assertEqual(
            "TASK_SCOPE_PAUSED", controller.consume_event(event)["status"]
        )

        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError,
            "SUPERSEDE_RECEIPT_MISMATCH",
        ):
            controller.supersede_paused(order["task_id"], "0" * 64)

        retired = controller.supersede_paused(
            order["task_id"], event["result_sha256"]
        )
        self.assertEqual("SUPERSEDED", retired["status"])
        self.assertEqual(
            "ALREADY_SUPERSEDED",
            controller.supersede_paused(
                order["task_id"], event["result_sha256"]
            )["status"],
        )
        self.assertEqual(expected_bytes, source.read_bytes())

        connection = sqlite3.connect(controller.db_path)
        try:
            self.assertEqual(
                ("SUPERSEDED", "SUPERSEDED", "COMPLETE"),
                connection.execute(
                    "SELECT t.status,wo.status,d.status FROM tasks t "
                    "JOIN work_orders wo ON wo.task_id=t.task_id "
                    "JOIN dispatches d ON d.task_id=t.task_id "
                    "WHERE t.task_id=?",
                    (order["task_id"],),
                ).fetchone(),
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM claims WHERE task_id=?",
                    (order["task_id"],),
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM resources WHERE task_id=?",
                    (order["task_id"],),
                ).fetchone()[0],
            )
        finally:
            connection.close()

        connection = controller._connect()
        try:
            active = load_snapshot_capacity()._active_sets(
                controller._snapshot_tables(connection)
            )
        finally:
            connection.close()
        self.assertNotIn(order["task_id"], active["tasks"])

    def test_supersede_paused_releases_claim_and_resource_for_successor(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SCOPE_CONFLICT",
            event_id="event-paused-clean",
        )
        self.assertEqual(
            "TASK_SCOPE_PAUSED", controller.consume_event(event)["status"]
        )
        def expire_order(connection):
            connection.execute(
                "UPDATE work_orders SET status='EXPIRED' WHERE task_id=?",
                (order["task_id"],),
            )
            return {"status": "EXPIRED"}

        controller._mutate(expire_order)
        completed = subprocess.run(
            [
                sys.executable,
                str(LOOPCTL),
                "--repo",
                str(self.repo),
                "supersede-paused",
                "--task",
                order["task_id"],
                "--result-sha256",
                event["result_sha256"],
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(
            "SUPERSEDED", json.loads(completed.stdout)["status"]
        )
        self._import_program(
            controller,
            {
                "schema": "x9-loop-program-v1",
                "program_id": "program-successor",
                "features": ["feature-successor"],
            },
        )
        successor = controller.create_work_order(
            program_id="program-successor",
            stop=self._stop(),
            linx_id="linx",
            action_class="successor",
        )
        self.assertEqual("CREATED", successor["status"])
        self.assertNotEqual(order["task_id"], successor["task_id"])

    def test_supersede_paused_rejects_deleted_receipt(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SCOPE_CONFLICT",
            event_id="event-paused-receipt-deleted",
        )
        self.assertEqual(
            "TASK_SCOPE_PAUSED", controller.consume_event(event)["status"]
        )

        receipt = self.repo / Path(*PurePosixPath(event["result_path"]).parts)
        receipt.unlink()

        with self.assertRaisesRegex(
            self.loopctl.StateNotDurableError,
            "RECEIPT_SET_MISMATCH",
        ):
            controller.supersede_paused(
                order["task_id"], event["result_sha256"]
            )

        connection = controller._connect()
        try:
            self.assertEqual(
                ("TASK_SCOPE_PAUSED", "TASK_SCOPE_PAUSED"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (order["task_id"],),
                    ).fetchone()
                ),
            )
        finally:
            connection.close()

    def test_supersede_owner_decision_cli_is_receipt_bound_and_idempotent(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="HARD_EXTERNAL",
            event_id="event-owner-decision-retire",
        )
        self.assertEqual(
            "OWNER_DECISION_REQUIRED", controller.consume_event(event)["status"]
        )

        completed = subprocess.run(
            [
                sys.executable,
                str(LOOPCTL),
                "--repo",
                str(self.repo),
                "supersede-owner-decision",
                "--task",
                order["task_id"],
                "--result-sha256",
                event["result_sha256"],
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("SUPERSEDED", json.loads(completed.stdout)["status"])
        before_retry = (
            self._controller_durable_state(controller),
            (controller.root / "runtime" / "STATUS.md").read_bytes(),
            (controller.root / "runtime" / "HANDOFFS.md").read_bytes(),
        )
        self.assertEqual(
            "ALREADY_SUPERSEDED",
            controller.supersede_owner_decision(
                order["task_id"], event["result_sha256"]
            )["status"],
        )
        self.assertEqual(
            before_retry,
            (
                self._controller_durable_state(controller),
                (controller.root / "runtime" / "STATUS.md").read_bytes(),
                (controller.root / "runtime" / "HANDOFFS.md").read_bytes(),
            ),
        )
        connection = controller._connect()
        try:
            self.assertEqual(
                ("SUPERSEDED", "SUPERSEDED", "COMPLETE"),
                tuple(
                    connection.execute(
                        "SELECT t.status,wo.status,d.status FROM tasks t "
                        "JOIN work_orders wo ON wo.task_id=t.task_id "
                        "JOIN dispatches d ON d.task_id=t.task_id "
                        "WHERE t.task_id=?",
                        (order["task_id"],),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                ("PASS", f"result_sha256={event['result_sha256']}"),
                tuple(
                    connection.execute(
                        "SELECT status,note FROM gates WHERE task_id=? "
                        "AND name='lifecycle:owner-decision-superseded'",
                        (order["task_id"],),
                    ).fetchone()
                ),
            )
            self.assertEqual(
                1,
                connection.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0],
            )
        finally:
            connection.close()
        self.assertEqual(
            "NOOP", json.loads(controller.action_path.read_bytes())["action"]
        )

    def test_supersede_owner_decision_wrong_hash_has_zero_state_delta(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="HARD_EXTERNAL",
            event_id="event-owner-decision-wrong-hash",
        )
        self.assertEqual(
            "OWNER_DECISION_REQUIRED", controller.consume_event(event)["status"]
        )
        before = self._controller_durable_state(controller)

        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError,
            "OWNER_DECISION_RECEIPT_MISMATCH",
        ):
            controller.supersede_owner_decision(order["task_id"], "0" * 64)

        self.assertEqual(before, self._controller_durable_state(controller))

    def test_supersede_owner_decision_rejects_second_receipt_read_drift(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="HARD_EXTERNAL",
            event_id="event-owner-decision-second-read-drift",
        )
        controller.consume_event(event)
        before = self._controller_durable_state(controller)
        original_read = controller._read_capped_packet
        reads = {"count": 0}

        def drift_on_second_read(path, packet_name):
            data = original_read(path, packet_name)
            reads["count"] += 1
            return data if reads["count"] == 1 else data + b" "

        with mock.patch.object(
            controller,
            "_read_capped_packet",
            side_effect=drift_on_second_read,
        ):
            with self.assertRaisesRegex(
                self.loopctl.StaleCompletionError,
                "OWNER_DECISION_RECEIPT_MISMATCH",
            ):
                controller.supersede_owner_decision(
                    order["task_id"], event["result_sha256"]
                )

        self.assertEqual(2, reads["count"])
        self.assertEqual(before, self._controller_durable_state(controller))

    def test_supersede_owner_decision_rejects_wrong_status_and_active_dispatch(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="HARD_EXTERNAL",
            event_id="event-owner-decision-state-guards",
        )
        controller.consume_event(event)

        def set_statuses(connection, task_status, dispatch_status):
            connection.execute(
                "UPDATE tasks SET status=? WHERE task_id=?",
                (task_status, order["task_id"]),
            )
            connection.execute(
                "UPDATE dispatches SET status=? WHERE dispatch_id=?",
                (dispatch_status, order["dispatch_id"]),
            )
            return {"status": "TEST_SETUP"}

        controller._mutate(
            lambda connection: set_statuses(
                connection, "REGISTERED", "COMPLETE"
            )
        )
        before = self._controller_durable_state(controller)
        with self.assertRaisesRegex(
            self.loopctl.TaskNotReadyError,
            "TASK_NOT_OWNER_DECISION_REQUIRED",
        ):
            controller.supersede_owner_decision(
                order["task_id"], event["result_sha256"]
            )
        self.assertEqual(before, self._controller_durable_state(controller))

        controller._mutate(
            lambda connection: set_statuses(
                connection, "OWNER_DECISION_REQUIRED", "DISPATCHED"
            )
        )
        before = self._controller_durable_state(controller)
        with self.assertRaisesRegex(
            self.loopctl.TaskNotReadyError,
            "TASK_NOT_OWNER_DECISION_REQUIRED",
        ):
            controller.supersede_owner_decision(
                order["task_id"], event["result_sha256"]
            )
        self.assertEqual(before, self._controller_durable_state(controller))

    def test_supersede_owner_decision_revalidates_receipt_and_worker_identity(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="HARD_EXTERNAL",
            event_id="event-owner-decision-revalidate",
        )
        controller.consume_event(event)
        receipt_path = self.repo / Path(
            *PurePosixPath(event["result_path"]).parts
        )
        contract = self.loopctl._load_v7_contract()
        receipt = json.loads(receipt_path.read_bytes())

        def bind_receipt(document):
            raw = contract.canonical_json_bytes(document)
            receipt_path.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()

            def operation(connection):
                connection.execute(
                    "UPDATE events SET event_sha256=? WHERE event_id=?",
                    (digest, event["event_id"]),
                )
                controller._set_receipt_state(
                    connection, "core-x9", [digest]
                )
                return {"status": "TEST_SETUP"}

            controller._mutate(operation)
            return digest

        wrong_outcome = dict(receipt, outcome="SCOPE_CONFLICT")
        digest = bind_receipt(wrong_outcome)
        before = self._controller_durable_state(controller)
        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError,
            "OWNER_DECISION_RECEIPT_MISMATCH",
        ):
            controller.supersede_owner_decision(order["task_id"], digest)
        self.assertEqual(before, self._controller_durable_state(controller))

        digest = bind_receipt(receipt)

        def break_worker_binding(connection):
            connection.execute(
                "UPDATE work_orders SET worker_id='linx' WHERE task_id=?",
                (order["task_id"],),
            )
            connection.execute(
                "UPDATE dispatches SET target_id='linx' WHERE dispatch_id=?",
                (order["dispatch_id"],),
            )
            return {"status": "TEST_SETUP"}

        controller._mutate(break_worker_binding)
        before = self._controller_durable_state(controller)
        with self.assertRaisesRegex(
            self.loopctl.StaleCompletionError,
            "OWNER_DECISION_RECEIPT_MISMATCH",
        ):
            controller.supersede_owner_decision(order["task_id"], digest)
        self.assertEqual(before, self._controller_durable_state(controller))

    def test_rebuild_treats_superseded_historical_missing_task_as_terminal(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(
            order["dispatch_id"], "DISPATCH", "task", "ack"
        )
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="SCOPE_CONFLICT",
            event_id="event-paused-historical",
        )
        self.assertEqual(
            "TASK_SCOPE_PAUSED", controller.consume_event(event)["status"]
        )
        self.assertEqual(
            "SUPERSEDED",
            controller.supersede_paused(
                order["task_id"], event["result_sha256"]
            )["status"],
        )

        missing = self.repo.parent / "missing-core"

        def classify_historical_missing(connection):
            connection.execute(
                "INSERT INTO worktrees(worktree_id,path,repository_id) "
                "VALUES(?,?,?)",
                ("core-legacy", str(missing), "core"),
            )
            connection.execute(
                "INSERT INTO worktree_classifications("
                "worktree_id,classification,owner_decision_sha256"
                ") VALUES(?,?,?)",
                ("core-legacy", "HISTORICAL_MISSING", "a" * 64),
            )
            connection.execute(
                "UPDATE tasks SET worktree_id='core-legacy' WHERE task_id=?",
                (order["task_id"],),
            )
            return {"status": "PASS"}

        controller._mutate(classify_historical_missing)

        self.assertFalse(missing.exists())
        self.assertEqual("PASS", controller.rebuild()["status"])

    def test_active_mission_reuses_order_and_thinker_review_reuses_verdict(self):
        controller = self.controller()
        order = self._create_order(controller)
        reused = self._create_order(controller)
        self.assertEqual("ACTIVE_WORK_ORDER_REUSED", reused["status"])
        self.assertEqual(order["work_order_id"], reused["work_order_id"])
        controller.register_actor("thinx", "THINX", "fixture thinker", "Unknown")
        controller.register_actor("thinx-two", "THINKER", "second thinker", "Unknown")
        request = {
            "action_class": "implementation",
            "evidence_sha256": "a" * 64,
            "question_sha256": "b" * 64,
            "review_class": "STAGED_DIFF",
            "staged_tree_sha256": "c" * 64,
            "thinker_id": "thinx",
        }
        self.assertEqual(
            "CONTINUE_LOCAL",
            controller.admit_thinker_review(order["work_order_id"], request)["status"],
        )
        (self.repo / "src" / "a.py").write_text("A = 2\n", encoding="utf-8")
        run("git", "add", "src/a.py", cwd=self.repo)
        staged_sha256 = hashlib.sha256(
            subprocess.run(
                ["git", "diff", "--cached", "--binary"], cwd=self.repo,
                check=True, capture_output=True,
            ).stdout
        ).hexdigest()
        request = {
            **request,
            "evidence_sha256": staged_sha256,
            "staged_tree_sha256": staged_sha256,
        }
        admission = {
            "architecture_security_boundary": False,
            "distinct_failed_approaches": 0,
            "owner_boundary": False,
            "schema": "x9-loop-question-admission-v1",
            "single_route_failed": False,
            "stable_material_diff": True,
            "subagent_available": False,
        }
        request = {**request, "admission": admission}
        self.assertEqual(
            "CONTINUE_LOCAL",
            controller.admit_thinker_review(
                order["work_order_id"],
                {
                    **request,
                    "admission": {
                        **admission,
                        "architecture_security_boundary": True,
                        "stable_material_diff": False,
                    },
                },
            )["status"],
        )
        first = controller.admit_thinker_review(order["work_order_id"], request)
        self.assertEqual("THINKER_REVIEW_REQUIRED", first["status"])
        duplicate = controller.admit_thinker_review(order["work_order_id"], request)
        self.assertEqual("THINKER_REVIEW_REUSED", duplicate["status"])
        self.assertIsNone(duplicate["verdict"])
        with self.assertRaises(self.loopctl.IdentityError):
            controller.admit_thinker_review(
                order["work_order_id"], {**request, "thinker_id": "missing"}
            )
        verdict_sha256 = self.loopctl._sha({
            "consultation_key": first["consultation_key"],
            "thinker_id": "thinx", "verdict": "PASS",
        })
        with self.assertRaises(self.loopctl.IdentityError):
            controller.record_thinker_verdict(
                order["work_order_id"], first["consultation_key"], "PASS",
                "thinx", "0" * 64,
            )
        self.assertEqual(
            "PASS", controller.record_thinker_verdict(
                order["work_order_id"], first["consultation_key"], "PASS",
                "thinx", verdict_sha256,
            )["status"],
        )
        connection = controller._connect()
        try:
            generation_before_replay = int(
                connection.execute(
                    "SELECT value FROM meta WHERE key='generation'"
                ).fetchone()[0]
            )
        finally:
            connection.close()
        self.assertEqual(
            "PASS", controller.record_thinker_verdict(
                order["work_order_id"], first["consultation_key"], "PASS",
                "thinx", verdict_sha256,
            )["status"],
        )
        connection = controller._connect()
        try:
            self.assertEqual(
                generation_before_replay,
                int(connection.execute(
                    "SELECT value FROM meta WHERE key='generation'"
                ).fetchone()[0]),
            )
        finally:
            connection.close()
        with self.assertRaises(self.loopctl.IdentityError):
            controller.record_thinker_verdict(
                order["work_order_id"], first["consultation_key"], "BLOCK",
                "thinx", self.loopctl._sha({
                    "consultation_key": first["consultation_key"],
                    "thinker_id": "thinx", "verdict": "BLOCK",
                }),
            )
        self.assertEqual(
            "PASS", controller.admit_thinker_review(
                order["work_order_id"], request
            )["verdict"],
        )
        (self.repo / "src" / "a.py").write_text("A = 3\n", encoding="utf-8")
        run("git", "add", "src/a.py", cwd=self.repo)
        changed_sha256 = hashlib.sha256(
            subprocess.run(
                ["git", "diff", "--cached", "--binary"], cwd=self.repo,
                check=True, capture_output=True,
            ).stdout
        ).hexdigest()
        changed_request = {
            **request,
            "evidence_sha256": changed_sha256,
            "staged_tree_sha256": changed_sha256,
        }
        changed_evidence = controller.admit_thinker_review(
            order["work_order_id"], changed_request
        )
        self.assertEqual("THINKER_REVIEW_REQUIRED", changed_evidence["status"])
        self.assertNotEqual(
            first["consultation_key"], changed_evidence["consultation_key"]
        )
        changed_reviewer = controller.admit_thinker_review(
            order["work_order_id"], {**changed_request, "thinker_id": "thinx-two"}
        )
        self.assertEqual("THINKER_REVIEW_REQUIRED", changed_reviewer["status"])
        self.assertNotEqual(
            first["consultation_key"], changed_reviewer["consultation_key"]
        )

    def test_autonomy_rejects_tampered_approach_evidence_before_consume(self):
        controller = self.controller()
        order = self._create_order(controller)
        controller.record_delivery(order["dispatch_id"], "DISPATCH", "task", "ack")
        event = self._write_v7_worker_event(
            controller,
            order,
            outcome="VERIFIED_FAILURE",
            failed_verified_approaches=2,
            event_id="event-v7-tampered-approach",
        )
        proof = self.repo / ".devad" / "workers" / "worker" / "proof" / (
            f"{event['event_id']}/approaches/approach-0.json"
        )
        proof.write_bytes(b"{\"tampered\":true}\n")
        with self.assertRaises(self.loopctl.StaleCompletionError) as failure:
            controller.consume_event(event)
        self.assertEqual("APPROACH_EVIDENCE_INVALID", str(failure.exception))
        connection = controller._connect()
        try:
            self.assertEqual(
                0,
                connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            )
        finally:
            connection.close()

if __name__ == "__main__":
    unittest.main()
