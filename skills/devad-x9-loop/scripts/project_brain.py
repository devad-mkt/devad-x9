"""Derived, profile-local project context helpers for X9 Loop Lite."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

CAPSULE_SCHEMA = "x9-loop-context-capsule-v1"
CAPSULE_CAP = 16 * 1024
SHARD_CAP = 64 * 1024
PROFILE_SCHEMA = "x9-project-memory-v1"
OWNERSHIP_FIELDS = (
    "EXISTING_FEATURE", "UI_SETTINGS", "SERVER_AUTHORITY", "PLAN_ENTITLEMENT",
    "REFERENCE_REUSE", "PERSISTENCE_CONSUMPTION", "INTEGRATED_HISTORY",
    "TEST_PROOF", "GAP", "CHANGE_MODE",
)
FAILURE_FIELDS = ("class", "code", "signature", "progress")
CHANGE_MODES = {"REUSE", "EXTEND", "NEW", "REPLACE_AUTHORIZED"}


class ProjectBrainError(ValueError):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False,
                          sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ProjectBrainError("PROJECT_BRAIN_CANONICAL_JSON_INVALID") from exc


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _profile_hash(profile_id: str) -> str:
    if not isinstance(profile_id, str) or not profile_id.strip() or any(c in profile_id for c in "\x00\r\n"):
        raise ProjectBrainError("PROJECT_PROFILE_ID_INVALID")
    return hashlib.sha256(profile_id.encode("utf-8")).hexdigest()[:32]


def profile_root(repo_root: str | os.PathLike[str], profile_id: str) -> Path:
    return Path(repo_root).resolve() / ".devad" / "profiles" / f"profile-{_profile_hash(profile_id)}"


derive_profile_root = profile_root


def canonical_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ProjectBrainError("PROJECT_SOURCE_PATH_INVALID")
    if "\\" in value or value.startswith("/") or ":" in value:
        raise ProjectBrainError("PROJECT_SOURCE_PATH_INVALID")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ProjectBrainError("PROJECT_SOURCE_PATH_INVALID")
    if any(part.upper() in {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1"} for part in path.parts):
        raise ProjectBrainError("PROJECT_SOURCE_PATH_INVALID")
    return path.as_posix()


def _reparse(path: Path) -> bool:
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except OSError:
        return False


def _safe_file(repo: Path, relative: str) -> Path:
    relative = canonical_repo_path(relative)
    candidate = repo.joinpath(*PurePosixPath(relative).parts)
    current = repo
    for part in candidate.relative_to(repo).parts:
        current /= part
        if current.exists() and _reparse(current):
            raise ProjectBrainError("PROJECT_SOURCE_REPARSE_FORBIDDEN")
    try:
        candidate.resolve(strict=False).relative_to(repo.resolve())
    except ValueError as exc:
        raise ProjectBrainError("PROJECT_SOURCE_PATH_INVALID") from exc
    return candidate


def _read_hash(path: Path) -> tuple[bytes, str]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ProjectBrainError("PROJECT_SOURCE_FILE_UNREADABLE") from exc
    return data, sha256_bytes(data)


def _head(repo: Path) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def validate_source_ref(repo_root: str | os.PathLike[str], source_ref: Mapping[str, Any], *,
                        expected_git_sha: str | None = None,
                        inventory: Mapping[str, Any] | None = None) -> dict[str, Any]:
    required = {"ref_id", "path", "file_sha256", "byte_start", "byte_end", "span_sha256"}
    if not isinstance(source_ref, Mapping) or not required.issubset(source_ref):
        raise ProjectBrainError("PROJECT_SOURCE_REF_INVALID")
    path_text = canonical_repo_path(source_ref["path"])
    start, end = source_ref["byte_start"], source_ref["byte_end"]
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < start:
        raise ProjectBrainError("PROJECT_SOURCE_SPAN_INVALID")
    if not _is_sha(source_ref["file_sha256"]) or not _is_sha(source_ref["span_sha256"]):
        raise ProjectBrainError("PROJECT_SOURCE_HASH_INVALID")
    repo = Path(repo_root).resolve()
    path = _safe_file(repo, path_text)
    data, digest = _read_hash(path)
    if digest != source_ref["file_sha256"]:
        raise ProjectBrainError("PROJECT_SOURCE_FILE_DRIFT")
    if end > len(data) or sha256_bytes(data[start:end]) != source_ref["span_sha256"]:
        raise ProjectBrainError("PROJECT_SOURCE_SPAN_DRIFT")
    if inventory is not None:
        expected = inventory.get(path_text)
        if isinstance(expected, Mapping):
            expected = expected.get("sha256", expected.get("file_sha256"))
        if expected != digest:
            raise ProjectBrainError("PROJECT_SOURCE_INVENTORY_DRIFT")
    if expected_git_sha and _head(repo) not in (None, expected_git_sha):
        raise ProjectBrainError("PROJECT_CONTEXT_GIT_DRIFT")
    result = copy.deepcopy(dict(source_ref))
    result["path"] = path_text
    return result


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Mapping):
        return " ".join(f"{k} {_text(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_text(v) for v in value)
    return str(value)


def validate_ownership(ownership: Any) -> list[dict[str, Any]]:
    if ownership in (None, [], {}):
        return []
    rows = ownership if isinstance(ownership, list) else [ownership]
    output = []
    for row in rows:
        if not isinstance(row, Mapping) or any(field not in row for field in OWNERSHIP_FIELDS):
            raise ProjectBrainError("PROJECT_OWNERSHIP_FIELDS_INVALID")
        mode = row["CHANGE_MODE"]
        if mode not in CHANGE_MODES:
            raise ProjectBrainError("PROJECT_OWNERSHIP_CHANGE_MODE_INVALID")
        owner_text = " ".join(_text(row[field]).lower() for field in (
            "EXISTING_FEATURE", "SERVER_AUTHORITY", "PERSISTENCE_CONSUMPTION",
            "INTEGRATED_HISTORY", "REFERENCE_REUSE"))
        empty_markers = ("none", "unknown", "missing", "not applicable", "no owner", "gap")
        has_owner = bool(owner_text.strip()) and not any(mark in owner_text for mark in empty_markers)
        if mode == "NEW" and has_owner:
            raise ProjectBrainError("PROJECT_OWNERSHIP_NEW_CONFLICT")
        if mode == "REPLACE_AUTHORIZED":
            decision = _text(row["PLAN_ENTITLEMENT"]) + " " + _text(row["GAP"])
            if not re.search(r"authorized|approved|owner decision|replace", decision, re.I):
                raise ProjectBrainError("PROJECT_OWNERSHIP_REPLACEMENT_UNAUTHORIZED")
        advisory = _text(row["EXISTING_FEATURE"]).lower()
        authoritative = " ".join(_text(row[field]).lower() for field in (
            "SERVER_AUTHORITY", "PERSISTENCE_CONSUMPTION", "INTEGRATED_HISTORY", "TEST_PROOF"))
        if ("dom" in advisory or "advisory" in advisory) and not authoritative.strip():
            raise ProjectBrainError("PROJECT_OWNERSHIP_ADVISORY_ONLY")
        if mode in {"REUSE", "EXTEND"} and not has_owner:
            raise ProjectBrainError("PROJECT_OWNERSHIP_SEAM_MISSING")
        output.append(copy.deepcopy(dict(row)))
    return output

def validate_sitemap(sitemap_path: str | os.PathLike[str], *,
                     manifest_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    path = Path(sitemap_path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProjectBrainError("PROJECT_DOCS_SITEMAP_UNREADABLE") from exc
    links = re.findall(r"!?(?:\[[^\]]*\])\(([^)\s]+)(?:\s+[^)]*)?\)", text)
    if not links:
        raise ProjectBrainError("PROJECT_DOCS_SITEMAP_LINKS_MISSING")
    targets = []
    for link in links:
        if link.startswith(("http:", "https:", "#", "/")) or "\\" in link:
            raise ProjectBrainError("PROJECT_DOCS_SITEMAP_LINK_INVALID")
        target = (path.parent / link).resolve()
        try:
            target.relative_to(path.parent.resolve())
        except ValueError as exc:
            raise ProjectBrainError("PROJECT_DOCS_SITEMAP_LINK_INVALID") from exc
        if not target.is_file():
            raise ProjectBrainError("PROJECT_DOCS_SITEMAP_LINK_MISSING")
        targets.append(target.relative_to(path.parent.resolve()).as_posix())
    if manifest_path is not None:
        entries = {}
        try:
            manifest = Path(manifest_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise ProjectBrainError("PROJECT_DOCS_MANIFEST_UNREADABLE") from exc
        for line in manifest.splitlines():
            if not line.strip():
                continue
            match = re.fullmatch(r"([0-9a-f]{64})\s+[* ](.+)", line.strip())
            if not match:
                raise ProjectBrainError("PROJECT_DOCS_MANIFEST_INVALID")
            entries[match.group(2)] = match.group(1)
        for target in targets:
            if target not in entries:
                raise ProjectBrainError("PROJECT_DOCS_MANIFEST_MISSING_LINK")
            if sha256_bytes((path.parent / target).read_bytes()) != entries[target]:
                raise ProjectBrainError("PROJECT_DOCS_MANIFEST_DRIFT")
    return {"status": "PASS", "path": str(path), "links": targets, "bytes": len(text.encode("utf-8"))}


EXECUTION_SITEMAP_HEADINGS = (
    "Owner Goal", "Current State", "Scope", "Implementation", "Acceptance",
    "Gates", "Rollback", "Next Action",
)


def validate_execution_sitemap(sitemap_path: str | os.PathLike[str], *,
                               manifest_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Validate the compact, source-backed transfer view used after a wake."""
    result = validate_sitemap(sitemap_path, manifest_path=manifest_path)
    path = Path(sitemap_path)
    text = path.read_text(encoding="utf-8")
    if result["bytes"] > CAPSULE_CAP:
        raise ProjectBrainError("PROJECT_EXECUTION_SITEMAP_TOO_LARGE")
    missing = [heading for heading in EXECUTION_SITEMAP_HEADINGS if f"## {heading}" not in text]
    if missing:
        raise ProjectBrainError(f"PROJECT_EXECUTION_SITEMAP_INCOMPLETE:{missing[0]}")
    return {**result, "execution_sitemap": True}


def validate_context_capsule(capsule: Mapping[str, Any], *,
                             repo_root: str | os.PathLike[str] | None = None,
                             expected_profile_id: str | None = None,
                             expected_git_sha: str | None = None,
                             inventory: Mapping[str, Any] | None = None,
                             allow_legacy: bool = False) -> dict[str, Any]:
    required = {"schema", "capsule_id", "repository_id", "source_git_sha", "source_root_sha256",
                "requirements", "facts", "relations", "source_refs"}
    if not isinstance(capsule, Mapping) or capsule.get("schema") != CAPSULE_SCHEMA or not required.issubset(capsule):
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_FIELDS_INVALID")
    strict = {"profile_id", "docs_sitemap_ref", "retrieval_budget"}
    if not allow_legacy and not strict.issubset(capsule):
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_FIELDS_INVALID")
    if expected_profile_id is not None and capsule.get("profile_id") not in (None, expected_profile_id):
        raise ProjectBrainError("PROJECT_CONTEXT_PROFILE_DRIFT")
    if expected_git_sha and capsule.get("source_git_sha") != expected_git_sha:
        raise ProjectBrainError("PROJECT_CONTEXT_GIT_DRIFT")
    for key in ("source_git_sha", "source_root_sha256"):
        if not isinstance(capsule[key], str) or not re.fullmatch(r"[0-9a-f]{40,64}", capsule[key]):
            raise ProjectBrainError("PROJECT_CONTEXT_IDENTITY_INVALID")
    if any(not isinstance(capsule[key], list) for key in ("requirements", "facts", "relations", "source_refs")):
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_LIST_INVALID")
    budget = capsule.get("retrieval_budget")
    if budget is not None and (not isinstance(budget, Mapping) or budget.get("max_bytes") != CAPSULE_CAP or budget.get("model_calls") != 0):
        raise ProjectBrainError("PROJECT_CONTEXT_RETRIEVAL_BUDGET_INVALID")
    if budget is not None and any(not isinstance(budget.get(key), int) for key in ("max_facts", "max_source_refs")):
        raise ProjectBrainError("PROJECT_CONTEXT_RETRIEVAL_BUDGET_INVALID")
    validate_ownership(capsule.get("ownership", capsule.get("ownership_relations")))
    refs = []
    for item in capsule["source_refs"]:
        refs.append(validate_source_ref(repo_root, item, expected_git_sha=expected_git_sha, inventory=inventory)
                    if repo_root is not None else copy.deepcopy(item))
    sitemap = capsule.get("docs_sitemap_ref")
    if sitemap is not None:
        if not isinstance(sitemap, Mapping) or set(sitemap) != {"path", "sha256", "bytes"} or not _is_sha(sitemap["sha256"]):
            raise ProjectBrainError("PROJECT_CONTEXT_SITEMAP_REF_INVALID")
        if repo_root is not None:
            sitemap_path = _safe_file(Path(repo_root).resolve(), sitemap["path"])
            data, digest = _read_hash(sitemap_path)
            if digest != sitemap["sha256"] or len(data) != sitemap["bytes"]:
                raise ProjectBrainError("PROJECT_CONTEXT_SITEMAP_DRIFT")
            validate_sitemap(sitemap_path)
    result = copy.deepcopy(dict(capsule))
    result["source_refs"] = refs
    if len(canonical_json_bytes(result)) > CAPSULE_CAP:
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_TOO_LARGE")
    return result


def build_context_capsule(*, capsule_id: str, profile_id: str, repository_id: str,
                          source_git_sha: str, source_root_sha256: str,
                          docs_sitemap_ref: Mapping[str, Any], requirements: Sequence[Any] = (),
                          source_refs: Sequence[Mapping[str, Any]] = (), facts: Sequence[Any] = (),
                          relations: Sequence[Any] = (), contradictions: Sequence[Any] = (),
                          must_reuse_fact_ids: Sequence[str] = (),
                          forbidden_authority_locations: Sequence[str] = (),
                          advisory_refs: Sequence[Any] = (),
                          ownership: Sequence[Mapping[str, Any]] | Mapping[str, Any] = ()) -> dict[str, Any]:
    capsule = {
        "schema": CAPSULE_SCHEMA, "capsule_id": capsule_id, "profile_id": profile_id,
        "repository_id": repository_id, "source_git_sha": source_git_sha,
        "source_root_sha256": source_root_sha256, "docs_sitemap_ref": dict(docs_sitemap_ref),
        "requirements": list(requirements), "source_refs": [dict(v) for v in source_refs],
        "facts": list(facts), "relations": list(relations), "contradictions": list(contradictions),
        "must_reuse_fact_ids": list(must_reuse_fact_ids),
        "forbidden_authority_locations": list(forbidden_authority_locations),
        "advisory_refs": list(advisory_refs),
        "retrieval_budget": {"max_bytes": CAPSULE_CAP, "max_facts": 40, "max_source_refs": 60, "model_calls": 0},
    }
    if ownership:
        capsule["ownership"] = list(ownership) if isinstance(ownership, (list, tuple)) else dict(ownership)
    return validate_context_capsule(capsule)


def write_context_capsule(path: str | os.PathLike[str], capsule: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_context_capsule(capsule)
    data = canonical_json_bytes(validated) + b"\n"
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != data:
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_IMMUTABLE")
    if not target.exists():
        target.write_bytes(data)
    return {"path": str(target), "bytes": len(data), "sha256": sha256_bytes(data), "capsule": validated}


def validate_capsule_ref(repo_root: str | os.PathLike[str], reference: Mapping[str, Any], *,
                         expected_profile_id: str | None = None,
                         expected_git_sha: str | None = None,
                         inventory: Mapping[str, Any] | None = None,
                         allow_legacy: bool = False) -> dict[str, Any]:
    if not isinstance(reference, Mapping) or set(reference) != {"bytes", "capsule_id", "path", "sha256"}:
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_REF_INVALID")
    path = _safe_file(Path(repo_root).resolve(), reference["path"])
    data, digest = _read_hash(path)
    if len(data) != reference["bytes"] or digest != reference["sha256"]:
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_REF_DRIFT")
    try:
        capsule = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_JSON_INVALID") from exc
    if capsule.get("capsule_id") != reference["capsule_id"]:
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_ID_DRIFT")
    checked = validate_context_capsule(capsule, repo_root=repo_root, expected_profile_id=expected_profile_id,
                                       expected_git_sha=expected_git_sha, inventory=inventory,
                                       allow_legacy=allow_legacy)
    return {"reference": copy.deepcopy(dict(reference)), "capsule": checked, "path": str(path),
            "bytes": len(data), "sha256": digest}


def validate_feature_packet_context(repo_root: str | os.PathLike[str], feature_packet: Mapping[str, Any], *,
                                    profile_id: str | None = None, phase: str = "pre-plan",
                                    allow_legacy: bool = False,
                                    inventory: Mapping[str, Any] | None = None) -> dict[str, Any]:
    reference = feature_packet.get("context_capsule_ref") if isinstance(feature_packet, Mapping) else None
    if reference is None:
        if allow_legacy:
            return {"status": "LEGACY_CONTEXT", "phase": phase}
        raise ProjectBrainError("PROJECT_CONTEXT_CAPSULE_REQUIRED")
    expected_git = feature_packet.get("base_sha") if isinstance(feature_packet.get("base_sha"), str) else None
    return validate_capsule_ref(repo_root, reference, expected_profile_id=profile_id,
                                expected_git_sha=expected_git, inventory=inventory,
                                allow_legacy=allow_legacy)

class _ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()

class ProjectMemory:
    """Profile-isolated derived memory; Controller state is never stored here."""

    def __init__(self, repo_root: str | os.PathLike[str], profile_id: str, repository_id: str | None = None):
        self.repo_root = Path(repo_root).resolve()
        self.profile_id = profile_id
        self.repository_id = repository_id or self.repo_root.name
        self.profile_root = profile_root(self.repo_root, profile_id)
        self.memory_root = self.profile_root / "memory"
        self.database_path = self.memory_root / "project-memory.sqlite"
        self.root_manifest_path = self.memory_root / "PROJECT_MEMORY_ROOT.json"

    def _manifest_payload(self) -> dict[str, Any]:
        return {
            "schema": PROFILE_SCHEMA,
            "schema_version": 1,
            "profile_id": self.profile_id,
            "profile_hash": self.profile_root.name.removeprefix("profile-"),
            "repository_id": self.repository_id,
            "database": "project-memory.sqlite",
        }

    def _validate_root_manifest(self) -> None:
        expected = canonical_json_bytes(self._manifest_payload()) + b"\n"
        if not self.root_manifest_path.is_file() or self.root_manifest_path.read_bytes() != expected:
            raise ProjectBrainError("PROJECT_MEMORY_ROOT_DRIFT")

    def _validate_database(self, database_path: str | os.PathLike[str] | None = None) -> str:
        path = Path(database_path or self.database_path).resolve()
        if not path.is_file() or _reparse(path):
            raise ProjectBrainError("PROJECT_MEMORY_DATABASE_INVALID")
        try:
            with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True, factory=_ClosingConnection) as connection:
                connection.row_factory = sqlite3.Row
                if connection.execute("PRAGMA user_version").fetchone()[0] != 1:
                    raise ProjectBrainError("PROJECT_MEMORY_SCHEMA_INVALID")
                if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ProjectBrainError("PROJECT_MEMORY_CORRUPT")
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                required = {"meta", "sources", "facts", "relations", "decisions", "contradictions", "episodes", "incidents", "documents", "facts_fts", "decisions_fts", "episodes_fts", "document_titles_fts"}
                if not required.issubset(tables):
                    raise ProjectBrainError("PROJECT_MEMORY_SCHEMA_INVALID")
                meta = {row["key"]: row["value"] for row in connection.execute("SELECT key,value FROM meta")}
                if meta.get("schema") != PROFILE_SCHEMA or meta.get("profile_id") != self.profile_id or meta.get("repository_id") != self.repository_id:
                    raise ProjectBrainError("PROJECT_MEMORY_PROFILE_DRIFT")
                facts = [tuple(row) for row in connection.execute("SELECT fact_id,semantic_key,value FROM facts ORDER BY fact_id")]
                indexed_facts = [tuple(row) for row in connection.execute("SELECT fact_id,semantic_key,value FROM facts_fts ORDER BY fact_id")]
                if facts != indexed_facts:
                    raise ProjectBrainError("PROJECT_MEMORY_FTS_DRIFT")
                episodes = [tuple(row) for row in connection.execute("SELECT episode_id,feature_id,summary FROM episodes ORDER BY episode_id")]
                indexed_episodes = [tuple(row) for row in connection.execute("SELECT episode_id,feature_id,summary FROM episodes_fts ORDER BY episode_id")]
                if episodes != indexed_episodes:
                    raise ProjectBrainError("PROJECT_MEMORY_FTS_DRIFT")
                decisions = [tuple(row) for row in connection.execute("SELECT decision_id,owner,scope,status,evidence FROM decisions ORDER BY decision_id")]
                indexed_decisions = [tuple(row) for row in connection.execute("SELECT decision_id,owner,scope,status,evidence FROM decisions_fts ORDER BY decision_id")]
                if decisions != indexed_decisions:
                    raise ProjectBrainError("PROJECT_MEMORY_FTS_DRIFT")
                documents = [tuple(row) for row in connection.execute("SELECT document_id,title,path FROM documents ORDER BY document_id")]
                indexed_documents = [tuple(row) for row in connection.execute("SELECT document_id,title,path FROM document_titles_fts ORDER BY document_id")]
                if documents != indexed_documents:
                    raise ProjectBrainError("PROJECT_MEMORY_FTS_DRIFT")
        except ProjectBrainError:
            raise
        except (OSError, sqlite3.Error) as exc:
            raise ProjectBrainError("PROJECT_MEMORY_DATABASE_INVALID") from exc
        return "PASS"

    def _guard(self) -> None:
        for path in (self.repo_root / ".devad", self.repo_root / ".devad" / "profiles", self.profile_root, self.memory_root):
            if path.exists() and _reparse(path):
                raise ProjectBrainError("PROJECT_MEMORY_REPARSE_FORBIDDEN")

    def probe_fts5(self) -> str:
        try:
            with sqlite3.connect(":memory:", factory=_ClosingConnection) as connection:
                connection.execute("CREATE VIRTUAL TABLE probe USING fts5(value)")
        except sqlite3.Error as exc:
            raise ProjectBrainError("PROJECT_MEMORY_FTS5_UNAVAILABLE") from exc
        return "PASS"

    def _connect(self) -> sqlite3.Connection:
        self._guard()
        self._validate_root_manifest()
        if not self.database_path.exists():
            raise ProjectBrainError("PROJECT_MEMORY_NOT_INITIALIZED")
        connection = sqlite3.connect(str(self.database_path), factory=_ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def initialize(self) -> Path:
        self._guard()
        self.probe_fts5()
        self.memory_root.mkdir(parents=True, exist_ok=True)
        manifest = self._manifest_payload()
        data = canonical_json_bytes(manifest) + b"\n"
        if self.root_manifest_path.exists() and self.root_manifest_path.read_bytes() != data:
            raise ProjectBrainError("PROJECT_MEMORY_ROOT_DRIFT")
        if not self.root_manifest_path.exists():
            self.root_manifest_path.write_bytes(data)
        with sqlite3.connect(str(self.database_path), factory=_ClosingConnection) as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")
            self._create_schema(connection)
            for key, value in (("schema", PROFILE_SCHEMA), ("profile_id", self.profile_id), ("repository_id", self.repository_id)):
                connection.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)", (key, value))
            connection.commit()
        self._validate_root_manifest()
        self._validate_database()
        return self.database_path

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.executescript("""
          PRAGMA user_version=1;
          CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS sources(source_id TEXT PRIMARY KEY,path TEXT NOT NULL,file_sha256 TEXT NOT NULL,byte_start INTEGER NOT NULL,byte_end INTEGER NOT NULL,span_sha256 TEXT NOT NULL,git_sha TEXT,captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS facts(fact_id TEXT PRIMARY KEY,semantic_key TEXT NOT NULL,value TEXT NOT NULL,tier TEXT NOT NULL,trust TEXT NOT NULL,source_ref_ids TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS relations(relation_id TEXT PRIMARY KEY,from_id TEXT NOT NULL,relation TEXT NOT NULL,to_id TEXT NOT NULL,state TEXT NOT NULL DEFAULT 'SOURCE_BACKED');
          CREATE TABLE IF NOT EXISTS decisions(decision_id TEXT PRIMARY KEY,owner TEXT NOT NULL,scope TEXT NOT NULL,status TEXT NOT NULL,evidence TEXT NOT NULL,supersedes TEXT);
          CREATE TABLE IF NOT EXISTS contradictions(contradiction_id TEXT PRIMARY KEY,left_id TEXT NOT NULL,right_id TEXT NOT NULL,precedence TEXT NOT NULL,resolution TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS episodes(episode_id TEXT PRIMARY KEY,feature_id TEXT NOT NULL,result_sha256 TEXT NOT NULL,summary TEXT NOT NULL,citations TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS documents(document_id TEXT PRIMARY KEY,title TEXT NOT NULL,path TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS incidents(signature TEXT PRIMARY KEY,failure_class TEXT NOT NULL,code TEXT NOT NULL,count INTEGER NOT NULL,progress INTEGER NOT NULL,receipt_ids TEXT NOT NULL);
          CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(fact_id UNINDEXED,semantic_key,value);
          CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(decision_id UNINDEXED,owner,scope,status,evidence);
          CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(episode_id UNINDEXED,feature_id,summary);
          CREATE VIRTUAL TABLE IF NOT EXISTS document_titles_fts USING fts5(document_id UNINDEXED,title,path UNINDEXED);
        """)

    def put_source(self, source_ref: Mapping[str, Any], *, git_sha: str | None = None) -> None:
        item = validate_source_ref(self.repo_root, source_ref, expected_git_sha=git_sha)
        with self._connect() as connection:
            connection.execute("INSERT OR REPLACE INTO sources(source_id,path,file_sha256,byte_start,byte_end,span_sha256,git_sha) VALUES(?,?,?,?,?,?,?)",
                               (item["ref_id"], item["path"], item["file_sha256"], item["byte_start"], item["byte_end"], item["span_sha256"], git_sha))

    def put_fact(self, *, fact_id: str, semantic_key: str, value: str,
                 source_ref_ids: Sequence[str], tier: str = "DURABLE",
                 trust: str = "SOURCE_BACKED") -> None:
        if not all(isinstance(v, str) and v for v in (fact_id, semantic_key, value)):
            raise ProjectBrainError("PROJECT_MEMORY_FACT_INVALID")
        source_json = json.dumps(list(source_ref_ids), ensure_ascii=False, separators=(",", ":"))
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT semantic_key,value,tier,trust,source_ref_ids FROM facts WHERE fact_id=?",
                (fact_id,),
            ).fetchone()
            if existing is not None:
                if tuple(existing) != (semantic_key, value, tier, trust, source_json):
                    raise ProjectBrainError("PROJECT_MEMORY_FACT_IMMUTABLE")
                return
            connection.execute(
                "INSERT INTO facts(fact_id,semantic_key,value,tier,trust,source_ref_ids) VALUES(?,?,?,?,?,?)",
                (fact_id, semantic_key, value, tier, trust, source_json),
            )
            connection.execute(
                "INSERT INTO facts_fts(fact_id,semantic_key,value) VALUES(?,?,?)",
                (fact_id, semantic_key, value),
            )

    def put_decision(self, *, decision_id: str, owner: str, scope: str, status: str, evidence: str, supersedes: str | None = None) -> None:
        if not all(isinstance(value, str) and value for value in (decision_id, owner, scope, status, evidence)):
            raise ProjectBrainError("PROJECT_MEMORY_DECISION_INVALID")
        with self._connect() as connection:
            values = (owner, scope, status, evidence, supersedes)
            existing = connection.execute("SELECT owner,scope,status,evidence,supersedes FROM decisions WHERE decision_id=?", (decision_id,)).fetchone()
            if existing is not None:
                if tuple(existing) != values:
                    raise ProjectBrainError("PROJECT_MEMORY_DECISION_IMMUTABLE")
                return
            connection.execute("INSERT INTO decisions(decision_id,owner,scope,status,evidence,supersedes) VALUES(?,?,?,?,?,?)",
                               (decision_id, *values))
            connection.execute("INSERT INTO decisions_fts(decision_id,owner,scope,status,evidence) VALUES(?,?,?,?,?)",
                               (decision_id, owner, scope, status, evidence))

    def put_document_title(self, *, document_id: str, title: str, path: str) -> None:
        if not all(isinstance(value, str) and value for value in (document_id, title, path)):
            raise ProjectBrainError("PROJECT_MEMORY_DOCUMENT_TITLE_INVALID")
        path = canonical_repo_path(path)
        with self._connect() as connection:
            existing = connection.execute("SELECT title,path FROM documents WHERE document_id=?", (document_id,)).fetchone()
            if existing is not None:
                if tuple(existing) != (title, path):
                    raise ProjectBrainError("PROJECT_MEMORY_DOCUMENT_TITLE_IMMUTABLE")
                return
            connection.execute("INSERT INTO documents(document_id,title,path) VALUES(?,?,?)",
                               (document_id, title, path))
            connection.execute("INSERT INTO document_titles_fts(document_id,title,path) VALUES(?,?,?)",
                               (document_id, title, path))

    def put_episode(self, *, episode_id: str, feature_id: str, result_sha256: str, summary: str, citations: str) -> None:
        if not all(isinstance(value, str) and value for value in (episode_id, feature_id, summary, citations)) or not _is_sha(result_sha256):
            raise ProjectBrainError("PROJECT_MEMORY_EPISODE_INVALID")
        with self._connect() as connection:
            values = (feature_id, result_sha256, summary, citations)
            existing = connection.execute("SELECT feature_id,result_sha256,summary,citations FROM episodes WHERE episode_id=?", (episode_id,)).fetchone()
            if existing is not None:
                if tuple(existing) != values:
                    raise ProjectBrainError("PROJECT_MEMORY_EPISODE_IMMUTABLE")
                return
            connection.execute("INSERT INTO episodes(episode_id,feature_id,result_sha256,summary,citations) VALUES(?,?,?,?,?)",
                               (episode_id, *values))
            connection.execute("INSERT INTO episodes_fts(episode_id,feature_id,summary) VALUES(?,?,?)",
                               (episode_id, feature_id, summary))

    def search_episodes(self, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            return []
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ProjectBrainError("PROJECT_MEMORY_SEARCH_LIMIT_INVALID")
        with self._connect() as connection:
            rows = connection.execute("SELECT episode_id,feature_id,summary FROM episodes_fts WHERE episodes_fts MATCH ? LIMIT ?", (query, limit)).fetchall()
        return [{"episode_id": r[0], "feature_id": r[1], "summary": r[2]} for r in rows]


    def search_decisions(self, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            return []
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ProjectBrainError("PROJECT_MEMORY_SEARCH_LIMIT_INVALID")
        with self._connect() as connection:
            rows = connection.execute("SELECT decision_id,owner,scope,status,evidence FROM decisions_fts WHERE decisions_fts MATCH ? LIMIT ?", (query, limit)).fetchall()
        return [{"decision_id": r[0], "owner": r[1], "scope": r[2], "status": r[3], "evidence": r[4]} for r in rows]

    def search_document_titles(self, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            return []
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ProjectBrainError("PROJECT_MEMORY_SEARCH_LIMIT_INVALID")
        with self._connect() as connection:
            rows = connection.execute("SELECT document_id,title,path FROM document_titles_fts WHERE document_titles_fts MATCH ? LIMIT ?", (query, limit)).fetchall()
        return [{"document_id": r[0], "title": r[1], "path": r[2]} for r in rows]


    def search(self, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            return []
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ProjectBrainError("PROJECT_MEMORY_SEARCH_LIMIT_INVALID")
        with self._connect() as connection:
            rows = connection.execute("SELECT f.fact_id,f.semantic_key,f.value,f.tier,f.trust,f.source_ref_ids FROM facts_fts JOIN facts f ON f.fact_id=facts_fts.fact_id WHERE facts_fts MATCH ? LIMIT ?", (query, limit)).fetchall()
        return [{"fact_id": r[0], "semantic_key": r[1], "value": r[2], "tier": r[3], "trust": r[4], "source_ref_ids": json.loads(r[5])} for r in rows]

    def record_incident(self, failure: Mapping[str, Any], *, receipt_id: str = "") -> None:
        item = validate_failure(failure)
        with self._connect() as connection:
            row = connection.execute("SELECT count,receipt_ids FROM incidents WHERE signature=?", (item["signature"],)).fetchone()
            count = int(row[0]) + 1 if row else 1
            ids = json.loads(row[1]) if row else []
            if receipt_id and receipt_id not in ids:
                ids.append(receipt_id)
            connection.execute("INSERT OR REPLACE INTO incidents(signature,failure_class,code,count,progress,receipt_ids) VALUES(?,?,?,?,?,?)",
                               (item["signature"], item["class"], item["code"], count, int(item["progress"]), json.dumps(ids, separators=(",", ":"))))

    def integrity_check(self) -> str:
        self._validate_root_manifest()
        return self._validate_database()

    def export(self, path: str | os.PathLike[str] | None = None) -> bytes | dict[str, Any]:
        with self._connect() as connection:
            tables = ("meta", "sources", "facts", "relations", "decisions", "contradictions", "episodes", "incidents")
            payload = {table: [dict(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()] for table in tables}
        data = canonical_json_bytes(payload) + b"\n"
        if path is None:
            return data
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != data:
            raise ProjectBrainError("PROJECT_MEMORY_EXPORT_IMMUTABLE")
        if not target.exists():
            target.write_bytes(data)
        return payload

    canonical_export = export

    def backup(self, target: str | os.PathLike[str]) -> Path:
        self.integrity_check()
        destination = Path(target)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise ProjectBrainError("PROJECT_MEMORY_BACKUP_EXISTS")
        try:
            with sqlite3.connect(str(self.database_path), factory=_ClosingConnection) as source, sqlite3.connect(str(destination), factory=_ClosingConnection) as target_connection:
                source.backup(target_connection)
        except (OSError, sqlite3.Error) as exc:
            raise ProjectBrainError("PROJECT_MEMORY_BACKUP_FAILED") from exc
        self._validate_database(destination)
        return destination

    def migrate(self) -> str:
        self._validate_root_manifest()
        self._validate_database()
        next_path = Path(str(self.database_path) + ".next")
        if next_path.exists():
            raise ProjectBrainError("PROJECT_MEMORY_MIGRATION_RESIDUE")
        original = sqlite3.connect(":memory:", factory=_ClosingConnection)
        try:
            with sqlite3.connect(str(self.database_path), factory=_ClosingConnection) as source:
                source.backup(original)
            with sqlite3.connect(str(next_path), factory=_ClosingConnection) as candidate:
                original.backup(candidate)
            self._validate_database(next_path)
            os.replace(next_path, self.database_path)
            try:
                return self._validate_database()
            except (OSError, sqlite3.Error, ProjectBrainError) as failure:
                rollback_next = Path(str(self.database_path) + ".rollback.next")
                if rollback_next.exists():
                    raise ProjectBrainError("PROJECT_MEMORY_ROLLBACK_RESIDUE") from failure
                try:
                    with sqlite3.connect(str(rollback_next), factory=_ClosingConnection) as restore:
                        original.backup(restore)
                    os.replace(rollback_next, self.database_path)
                    self._validate_database()
                except (OSError, sqlite3.Error, ProjectBrainError) as rollback_failure:
                    raise ProjectBrainError("PROJECT_MEMORY_MIGRATION_ROLLBACK_FAILED") from rollback_failure
                raise ProjectBrainError("PROJECT_MEMORY_MIGRATION_FAILED") from failure
        except ProjectBrainError:
            raise
        except (OSError, sqlite3.Error) as exc:
            raise ProjectBrainError("PROJECT_MEMORY_MIGRATION_FAILED") from exc
        finally:
            original.close()

    def rollback(self, backup_path: str | os.PathLike[str]) -> str:
        source = Path(backup_path)
        if not source.is_file():
            raise ProjectBrainError("PROJECT_MEMORY_ROLLBACK_SOURCE_MISSING")
        self._validate_root_manifest()
        self._validate_database(source)
        next_path = Path(str(self.database_path) + ".rollback.next")
        if next_path.exists():
            raise ProjectBrainError("PROJECT_MEMORY_ROLLBACK_RESIDUE")
        try:
            shutil.copy2(source, next_path)
            os.replace(next_path, self.database_path)
        except (OSError, shutil.Error) as exc:
            raise ProjectBrainError("PROJECT_MEMORY_ROLLBACK_FAILED") from exc
        return self._validate_database()

def validate_failure(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != set(FAILURE_FIELDS):
        raise ProjectBrainError("PROJECT_FAILURE_FIELDS_INVALID")
    if value["class"] not in {"PRODUCT", "INFRASTRUCTURE"}:
        raise ProjectBrainError("PROJECT_FAILURE_CLASS_INVALID")
    if not isinstance(value["code"], str) or not re.fullmatch(r"[A-Z][A-Z0-9_.:-]{0,95}", value["code"]):
        raise ProjectBrainError("PROJECT_FAILURE_CODE_INVALID")
    if not _is_sha(value["signature"]):
        raise ProjectBrainError("PROJECT_FAILURE_SIGNATURE_INVALID")
    if not isinstance(value["progress"], bool):
        raise ProjectBrainError("PROJECT_FAILURE_PROGRESS_INVALID")
    return copy.deepcopy(dict(value))


def failure_signature(failure_class: str, code: str, *, identity: Mapping[str, Any] | None = None) -> str:
    return sha256_json({"class": failure_class, "code": code, "identity": identity or {}})


def repeated_failure_gate(receipts: Iterable[Mapping[str, Any]], *, threshold: int = 3,
                          source_identity: str | None = None) -> dict[str, Any]:
    if not isinstance(threshold, int) or threshold < 1:
        raise ProjectBrainError("PROJECT_FAILURE_THRESHOLD_INVALID")
    signature = None
    count = 0
    for receipt in receipts:
        failure = receipt.get("failure") if isinstance(receipt, Mapping) else None
        if failure is None:
            continue
        item = validate_failure(failure)
        if item["class"] != "PRODUCT" or item["progress"]:
            continue
        if source_identity is not None and receipt.get("source_identity") not in (None, source_identity):
            signature, count = None, 0
            continue
        if item["signature"] == signature:
            count += 1
        else:
            signature, count = item["signature"], 1
    return {"open": count >= threshold, "count": count, "threshold": threshold,
            "signature": signature, "code": "PROJECT_MEMORY_CIRCUIT_OPEN" if count >= threshold else None}


def _load_v7_contract():
    path = Path(__file__).with_name("v7_contract.py")
    spec = importlib.util.spec_from_file_location(
        "x9_loop_v7_contract_for_project_brain", path
    )
    if spec is None or spec.loader is None:
        raise ProjectBrainError("PROJECT_DOCS_RESULT_CONTRACT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as exc:
        raise ProjectBrainError("PROJECT_DOCS_RESULT_CONTRACT_UNAVAILABLE") from exc
    return module


def _validate_accepted_result(result: Mapping[str, Any]) -> None:
    if (
        result.get("schema") != "x9-loop-result-v2"
        or result.get("role") != "WORKER"
        or result.get("outcome") != "SUCCESS"
    ):
        raise ProjectBrainError("PROJECT_DOCS_RESULT_NOT_ACCEPTED")
    try:
        contract = _load_v7_contract()
        expected = {
            field: result[field]
            for field in (
                "dispatch_id", "event_id", "packet_sha256", "task_id",
                "work_order_id", "work_order_sha256", "worker_id",
            )
        }
        validated, _disposition = contract.validate_worker_result(
            result, expected
        )
    except Exception as exc:
        raise ProjectBrainError("PROJECT_DOCS_RESULT_NOT_ACCEPTED") from exc
    if validated != dict(result):
        raise ProjectBrainError("PROJECT_DOCS_RESULT_NOT_ACCEPTED")


DOC_BINDING_FIELDS = {
    "feature_id", "feature_packet_sha256", "plan_sha256", "task_id", "work_order_id",
    "work_order_sha256", "dispatch_id", "event_id", "worker_id", "profile_id",
    "base_sha", "current_sha", "result_sha256", "source_manifest_sha256", "proof", "changed_files",
    "attestation_path", "c2_sha256", "unknown_items", "rollback", "canonical_refs",
}

STYLE_DOCS_RECEIPT_FIELDS = {
    "schema", "outcome", "feature_id", "profile_id", "base_sha", "current_sha",
    "plan_ref", "source_refs", "proof", "changed_files", "unknown_items", "rollback",
}

def _validate_docs_binding(repo_root: str | os.PathLike[str], feature_id: str,
                            result: Mapping[str, Any], binding: Mapping[str, Any],
                            profile_id: str | None = None) -> dict[str, Any]:
    if not isinstance(binding, Mapping) or set(binding) != DOC_BINDING_FIELDS:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_INVALID")
    if binding["feature_id"] != feature_id:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_INVALID")
    if profile_id is not None and binding["profile_id"] != profile_id:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_DRIFT")
    if not isinstance(binding["profile_id"], str) or not binding["profile_id"].strip():
        raise ProjectBrainError("PROJECT_DOCS_BINDING_INVALID")
    for field in ("feature_packet_sha256", "work_order_sha256", "result_sha256", "source_manifest_sha256"):
        if not _is_sha(binding[field]):
            raise ProjectBrainError("PROJECT_DOCS_BINDING_HASH_INVALID")
    if binding["plan_sha256"] is not None and not _is_sha(binding["plan_sha256"]):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_HASH_INVALID")
    if not isinstance(binding["base_sha"], str) or not re.fullmatch(r"[0-9a-f]{40}", binding["base_sha"]) or not isinstance(binding["current_sha"], str) or not re.fullmatch(r"[0-9a-f]{40}", binding["current_sha"]):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_HASH_INVALID")
    required_refs = {"feature_packet", "work_order", "result", "source_manifest"}
    optional_refs = {"dispatch", "plan", "program_packet", "result_ready", "inbox_event"}
    refs = binding["canonical_refs"]
    if not isinstance(refs, Mapping) or not required_refs.issubset(refs) or not set(refs).issubset(required_refs | optional_refs):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_INVALID")
    artifact_payloads: dict[str, Any] = {}
    for kind, reference in refs.items():
        if not isinstance(reference, Mapping) or set(reference) != {"path", "sha256"} or not _is_sha(reference["sha256"]):
            raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_INVALID")
        path = _safe_file(Path(repo_root).resolve(), reference["path"])
        data, digest = _read_hash(path)
        if digest != reference["sha256"]:
            raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_DRIFT")
        if kind in {"feature_packet", "work_order", "dispatch", "result", "program_packet", "result_ready", "inbox_event"}:
            try:
                artifact_payloads[kind] = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_INVALID") from exc
    ref_identity_checks = (
        ("feature_packet", "feature_packet_sha256"),
        ("work_order", "work_order_sha256"),
        ("source_manifest", "source_manifest_sha256"),
    )
    if any(refs[k]["sha256"] != binding[field] for k, field in ref_identity_checks):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if ("plan" in refs) != (binding["plan_sha256"] is not None):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if "plan" in refs and refs["plan"]["sha256"] != binding["plan_sha256"]:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    feature_payload = artifact_payloads["feature_packet"]
    if not isinstance(feature_payload, Mapping) or any(field not in feature_payload for field in ("feature_id", "base_sha")):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if feature_payload["feature_id"] != feature_id or feature_payload["base_sha"] != binding["base_sha"]:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if "plan_sha256" in feature_payload and feature_payload["plan_sha256"] != binding["plan_sha256"]:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    attachments = feature_payload.get("attachment_hashes")
    if attachments is not None and binding["plan_sha256"] is not None and binding["plan_sha256"] not in attachments:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    work_payload = artifact_payloads["work_order"]
    required_work = ("work_order_id", "task_id", "worker_id", "base_sha", "feature_packet_refs")
    if not isinstance(work_payload, Mapping) or any(field not in work_payload for field in required_work):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if any(work_payload[field] != binding[field] for field in ("work_order_id", "task_id", "worker_id", "base_sha")):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if "feature_id" in work_payload and work_payload["feature_id"] != feature_id:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    if "plan_sha256" in work_payload and work_payload["plan_sha256"] != binding["plan_sha256"]:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    work_refs = work_payload["feature_packet_refs"]
    if not isinstance(work_refs, list) or not any(isinstance(item, Mapping) and item.get("sha256") == binding["feature_packet_sha256"] for item in work_refs):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    dispatch_payload = artifact_payloads.get("dispatch")
    if dispatch_payload is not None and (
        not isinstance(dispatch_payload, Mapping)
        or any(field not in dispatch_payload for field in ("dispatch_id", "event_id", "worker_id"))
        or any(dispatch_payload[field] != binding[field] for field in ("dispatch_id", "event_id", "worker_id"))
    ):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    result_ready = artifact_payloads.get("result_ready")
    if result_ready is not None:
        identity = result_ready.get("expected_result_identity")
        if not isinstance(identity, Mapping) or any(identity.get(field) != binding[field] for field in ("dispatch_id", "event_id", "task_id", "work_order_id", "work_order_sha256", "worker_id")):
            raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
        if identity.get("result_sha256") != binding["result_sha256"]:
            raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    inbox_event = artifact_payloads.get("inbox_event")
    if inbox_event is not None:
        payload_ref = inbox_event.get("payload_ref")
        if (
            not isinstance(payload_ref, Mapping)
            or inbox_event.get("event_id") != binding["event_id"]
            or inbox_event.get("source_actor_id") != binding["worker_id"]
            or payload_ref.get("sha256") != binding["result_sha256"]
        ):
            raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    result_payload = artifact_payloads["result"]
    if result_payload != dict(result) or binding["result_sha256"] != refs["result"]["sha256"]:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_DRIFT")
    current_head = _head(Path(repo_root).resolve())
    if current_head is None or current_head != binding["current_sha"]:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_IDENTITY_DRIFT")
    for proof in result["proof"]:
        proof_path = _safe_file(Path(repo_root).resolve(), proof["path"])
        _proof_data, proof_digest = _read_hash(proof_path)
        if proof_digest != proof["sha256"]:
            raise ProjectBrainError("PROJECT_DOCS_BINDING_ARTIFACT_DRIFT")
    if binding["result_sha256"] != refs["result"]["sha256"] or result.get("packet_sha256") not in {binding["feature_packet_sha256"], binding["work_order_sha256"]}:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_DRIFT")
    for field in ("task_id", "work_order_id", "work_order_sha256", "dispatch_id", "event_id", "worker_id"):
        if binding[field] != result.get(field):
            raise ProjectBrainError("PROJECT_DOCS_BINDING_DRIFT")
    if binding["proof"] != result.get("proof") or binding["changed_files"] != result.get("changed_files"):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_DRIFT")
    if binding["attestation_path"] != result.get("attestation_path"):
        raise ProjectBrainError("PROJECT_DOCS_BINDING_DRIFT")
    result_c2 = result.get("c2")
    result_c2_sha = result_c2.get("sha256") if isinstance(result_c2, Mapping) else None
    if binding["c2_sha256"] != result_c2_sha or binding["unknown_items"] != []:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_DRIFT")
    if not isinstance(binding["rollback"], str) or not binding["rollback"].strip():
        raise ProjectBrainError("PROJECT_DOCS_BINDING_INVALID")
    return copy.deepcopy(dict(binding))


def _immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ProjectBrainError("PROJECT_DOCS_INPUT_CHANGED")
    if not path.exists():
        path.write_bytes(data)


def generate_feature_docs(repo_root: str | os.PathLike[str], feature_id: str, result: Mapping[str, Any], *,
                          profile_id: str | None = None, binding: Mapping[str, Any] | None = None,
                          output_root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    if not isinstance(result, Mapping):
        raise ProjectBrainError("PROJECT_DOCS_RESULT_INVALID")
    _validate_accepted_result(result)
    if not isinstance(feature_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,95}", feature_id):
        raise ProjectBrainError("PROJECT_DOCS_FEATURE_ID_INVALID")
    if binding is None:
        raise ProjectBrainError("PROJECT_DOCS_BINDING_REQUIRED")
    if output_root is not None:
        raise ProjectBrainError("PROJECT_DOCS_OUTPUT_ROOT_FORBIDDEN")
    normalized_binding = _validate_docs_binding(repo_root, feature_id, result, binding, profile_id)
    directory = (Path(repo_root).resolve() / ".devad" / "features" / feature_id).resolve()
    result_sha = normalized_binding["result_sha256"]
    docs = {
        "00-overview.md": f"# {feature_id}\n\nEvidence: VERIFIED\n\nCanonical result: `{result_sha}`.\n",
        "01-scope.md": "# Scope\n\nThis packet records only the accepted bounded feature slice.\n",
        "02-architecture.md": "# Architecture\n\nMemory is derived and profile-local; Controller packets remain authoritative.\n",
        "03-data.md": "# Data\n\nStyle keeps derived profile-local documents only; it does not require a database.\n",
        "04-runtime.md": "# Runtime\n\nGenerated documents do not grant authority or dispatch work.\n",
        "05-tests.md": "# Tests\n\nEvidence label: VERIFIED.\n",
        "06-decisions.md": "# Decisions\n\nAccepted result evidence is the sole input to this packet.\n",
    }
    task = "\n".join([f"# {feature_id} task sitemap", "", "Evidence: VERIFIED", ""] + [f"- [{name}]({name})" for name in docs]) + "\n"
    feature = {"schema": "x9-project-docs-feature-v1", "feature_id": feature_id,
               "profile_id": normalized_binding["profile_id"],
               "result_sha256": result_sha, "accepted": True,
               "binding": normalized_binding,
               "generated_files": ["TASK.md", "FEATURE.json", "MANIFEST.sha256", *docs]}
    _immutable(directory / "TASK.md", task.encode())
    _immutable(directory / "FEATURE.json", canonical_json_bytes(feature) + b"\n")
    for name, text in docs.items():
        _immutable(directory / name, text.encode())
    names = ["TASK.md", "FEATURE.json", *docs]
    manifest = "\n".join(f"{sha256_bytes((directory / name).read_bytes())}  {name}" for name in names) + "\n"
    _immutable(directory / "MANIFEST.sha256", manifest.encode())
    validate_sitemap(directory / "TASK.md", manifest_path=directory / "MANIFEST.sha256")
    return {"status": "VERIFIED", "feature_id": feature_id, "path": str(directory),
            "result_sha256": result_sha, "manifest_sha256": sha256_bytes((directory / "MANIFEST.sha256").read_bytes()),
            "files": names}


def _validate_style_docs_receipt(repo_root: str | os.PathLike[str], feature_id: str,
                                 receipt: Mapping[str, Any], profile_id: str | None = None) -> dict[str, Any]:
    if not isinstance(receipt, Mapping) or set(receipt) != STYLE_DOCS_RECEIPT_FIELDS:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    if receipt["schema"] != "x9-loop-style-result-v1" or receipt["outcome"] != "SUCCESS":
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_NOT_ACCEPTED")
    if receipt["feature_id"] != feature_id:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    if not isinstance(receipt["profile_id"], str) or not receipt["profile_id"].strip():
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    if profile_id is not None and receipt["profile_id"] != profile_id:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_DRIFT")
    for field in ("base_sha", "current_sha"):
        if not isinstance(receipt[field], str) or not re.fullmatch(r"[0-9a-f]{40}", receipt[field]):
            raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_HASH_INVALID")
    repo = Path(repo_root).resolve()
    if _head(repo) != receipt["current_sha"]:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_DRIFT")
    plan_ref = receipt["plan_ref"]
    if not isinstance(plan_ref, Mapping) or set(plan_ref) != {"path", "sha256"} or not _is_sha(plan_ref["sha256"]):
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    _plan_data, plan_digest = _read_hash(_safe_file(repo, plan_ref["path"]))
    if plan_digest != plan_ref["sha256"]:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_DRIFT")
    source_refs = receipt["source_refs"]
    if not isinstance(source_refs, list) or not source_refs:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    normalized_refs = [validate_source_ref(repo, item, expected_git_sha=receipt["current_sha"]) for item in source_refs]
    if len({item["ref_id"] for item in normalized_refs}) != len(normalized_refs):
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    proof = receipt["proof"]
    if not isinstance(proof, list) or not proof:
        raise ProjectBrainError("PROJECT_STYLE_DOCS_PROOF_INVALID")
    normalized_proof = []
    for item in proof:
        if not isinstance(item, Mapping) or set(item) != {"kind", "path", "sha256"} or not isinstance(item["kind"], str) or not item["kind"].strip() or not _is_sha(item["sha256"]):
            raise ProjectBrainError("PROJECT_STYLE_DOCS_PROOF_INVALID")
        path = _safe_file(repo, item["path"])
        _proof_data, proof_digest = _read_hash(path)
        if proof_digest != item["sha256"]:
            raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_DRIFT")
        normalized_proof.append({"kind": item["kind"], "path": canonical_repo_path(item["path"]), "sha256": item["sha256"]})
    changed = receipt["changed_files"]
    if not isinstance(changed, list) or len({canonical_repo_path(item) for item in changed}) != len(changed):
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    if receipt["unknown_items"] != [] or not isinstance(receipt["rollback"], str) or not receipt["rollback"].strip():
        raise ProjectBrainError("PROJECT_STYLE_DOCS_RECEIPT_INVALID")
    normalized = copy.deepcopy(dict(receipt))
    normalized["plan_ref"] = {"path": canonical_repo_path(plan_ref["path"]), "sha256": plan_ref["sha256"]}
    normalized["source_refs"] = normalized_refs
    normalized["proof"] = normalized_proof
    normalized["changed_files"] = [canonical_repo_path(item) for item in changed]
    return normalized


def generate_style_feature_docs(repo_root: str | os.PathLike[str], feature_id: str, receipt: Mapping[str, Any], *,
                                profile_id: str | None = None,
                                output_root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    if not isinstance(feature_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,95}", feature_id):
        raise ProjectBrainError("PROJECT_DOCS_FEATURE_ID_INVALID")
    if output_root is not None:
        raise ProjectBrainError("PROJECT_DOCS_OUTPUT_ROOT_FORBIDDEN")
    normalized = _validate_style_docs_receipt(repo_root, feature_id, receipt, profile_id)
    directory = (Path(repo_root).resolve() / ".devad" / "features" / feature_id).resolve()
    receipt_sha = sha256_json(normalized)
    docs = {
        "00-overview.md": f"# {feature_id}\n\nEvidence: VERIFIED\n\nStyle receipt: `{receipt_sha}`.\n",
        "01-scope.md": "# Scope\n\nThis packet records one accepted bounded Style slice.\n",
        "02-architecture.md": "# Architecture\n\nStyle receipt and current Git are authoritative; memory and docs are derived.\n",
        "03-data.md": "# Data\n\nThe profile-local database path is derived from the bound profile identity.\n",
        "04-runtime.md": "# Runtime\n\nGenerated documents do not create Controller state, dispatch work, or call providers.\n",
        "05-tests.md": "# Tests\n\nEvidence label: VERIFIED.\n",
        "06-decisions.md": "# Decisions\n\nThe accepted Style receipt is the sole input to this packet.\n",
    }
    task = "\n".join([f"# {feature_id} task sitemap", "", "Evidence: VERIFIED", ""] + [f"- [{name}]({name})" for name in docs]) + "\n"
    feature = {"schema": "x9-project-docs-feature-v1", "feature_id": feature_id,
               "profile_id": normalized["profile_id"], "receipt_sha256": receipt_sha,
               "accepted": True, "mode": "STYLE_ONLY", "binding": normalized,
               "generated_files": ["TASK.md", "FEATURE.json", "MANIFEST.sha256", *docs]}
    _immutable(directory / "TASK.md", task.encode())
    _immutable(directory / "FEATURE.json", canonical_json_bytes(feature) + b"\n")
    for name, text in docs.items():
        _immutable(directory / name, text.encode())
    names = ["TASK.md", "FEATURE.json", *docs]
    manifest = "\n".join(f"{sha256_bytes((directory / name).read_bytes())}  {name}" for name in names) + "\n"
    _immutable(directory / "MANIFEST.sha256", manifest.encode())
    validate_sitemap(directory / "TASK.md", manifest_path=directory / "MANIFEST.sha256")
    return {"status": "VERIFIED", "mode": "STYLE_ONLY", "feature_id": feature_id,
            "path": str(directory), "receipt_sha256": receipt_sha,
            "manifest_sha256": sha256_bytes((directory / "MANIFEST.sha256").read_bytes()), "files": names}


build_feature_docs = generate_feature_docs
build_style_feature_docs = generate_style_feature_docs


def canary_existing_capability(capsule: Mapping[str, Any], *, owner_mode: str = "REUSE") -> dict[str, Any]:
    validate_context_capsule(capsule)
    if owner_mode not in {"REUSE", "EXTEND"}:
        raise ProjectBrainError("PROJECT_CANARY_NEW_FORBIDDEN")
    return {"status": "PASS", "owner_mode": owner_mode, "dispatches": 0, "model_calls": 0}


__all__ = [
    "CAPSULE_CAP", "CAPSULE_SCHEMA", "OWNERSHIP_FIELDS", "ProjectBrainError", "ProjectMemory",
    "build_context_capsule", "build_feature_docs", "canary_existing_capability", "canonical_json_bytes",
    "canonical_repo_path", "derive_profile_root", "failure_signature", "generate_feature_docs",
    "generate_style_feature_docs", "build_style_feature_docs",
    "profile_root", "repeated_failure_gate", "sha256_bytes", "sha256_json", "validate_capsule_ref",
    "validate_context_capsule", "validate_failure", "validate_feature_packet_context", "validate_ownership",
    "validate_execution_sitemap", "validate_sitemap", "validate_source_ref", "write_context_capsule",
]
