from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence
import ntpath
import re
import unicodedata
from pathlib import Path, PurePosixPath


PACKET_CAPS = {
    "ACTION.json": 4 * 1024,
    "CALL_RECEIPT.json": 16 * 1024,
    "FEATURE_PACKET.json": 32 * 1024,
    "IMPORT_COVERAGE_SUMMARY.json": 16 * 1024,
    "INBOX_EVENT.json": 4 * 1024,
    "PROGRAM_PACKET.json": 16 * 1024,
    "RESULT.json": 4 * 1024,
    "RESULT_READY.json": 4 * 1024,
    "SNAPSHOT.json": 8 * 1024,
    "THINX_DECISION.json": 4 * 1024,
    "WORKER_CHECKPOINT.json": 16 * 1024,
    "WORK_ORDER.json": 16 * 1024,
    "TRANSPORT_ACK.json": 4 * 1024,
    "LOOP_INCIDENT.json": 8 * 1024,
}

REQUIRED_CONTEXT_FIELDS = (
    "schema",
    "owner_requirement",
    "attachment_hashes",
    "feature_id",
    "subfeature_ids",
    "accepted",
    "rejected",
    "paused",
    "unknown",
    "out_of_scope",
    "source_references",
    "implementation_evidence",
    "worktree_id",
    "worktree_path",
    "branch",
    "base_sha",
    "local_work",
    "claims",
    "resources",
    "dependencies",
    "known_decisions",
    "tool_lessons",
    "prior_failed_attempts",
    "finish_line",
    "tests",
    "security_checks",
    "commit_rules",
    "deploy_gate",
    "browser_acceptance",
    "allowed_autonomy",
    "owner_decision_boundaries",
)

WORK_ORDER_BINDINGS = (
    "base_sha",
    "claims",
    "feature_packet_refs",
    "program_packet_path",
    "program_packet_sha256",
    "resources",
    "source_git_sha",
    "source_root_sha256",
    "stop_contract",
    "task_id",
    "work_order_id",
    "worker_id",
    "worktree_id",
    "worktree_path",
)

WORKER_RESULT_VALIDATOR_PATH = (
    "skills/devad-x9-loop/scripts/v7_contract.py"
)

AUTONOMY_CONTRACT_SCHEMA = "x9-loop-autonomy-v1"
APPROACH_RECEIPT_SCHEMA = "x9-loop-approach-receipt-v1"
QUESTION_ADMISSION_SCHEMA = "x9-loop-question-admission-v1"


def _canonical_hash(value: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(value)))


def mission_identity(
    *, action_class: str, features: Sequence[Mapping[str, Any]],
    program_packet_ref: Mapping[str, Any], stop: Mapping[str, Any],
) -> str:
    """Hash the independently accepted outcome, never its generated IDs."""
    if not isinstance(action_class, str) or not action_class.strip():
        raise ContractError("MISSION_IDENTITY_INVALID")
    if not 1 <= len(features) <= 2 or set(program_packet_ref) != {"path", "sha256"}:
        raise ContractError("MISSION_IDENTITY_INVALID")
    selected = []
    for feature in sorted(features, key=lambda item: str(item.get("feature_id", ""))):
        _validate_feature_assignment(feature)
        selected.append({
            "feature_id": feature["feature_id"],
            "path": canonical_repo_path(feature["path"]),
            "sha256": _require_sha256(feature["sha256"], "MISSION_IDENTITY_INVALID"),
            "claims": _normalized_claims(feature["claims"]),
            "resources": _normalized_resources(feature["resources"]),
            "finish_line": feature["finish_line"],
        })
    return _canonical_hash({
        "action_class": action_class,
        "features": selected,
        "program_packet_path": canonical_repo_path(program_packet_ref["path"]),
        "program_packet_sha256": _require_sha256(program_packet_ref["sha256"], "MISSION_IDENTITY_INVALID"),
        "stop_contract": _validate_stop(stop),
    })


def build_autonomy_contract(mission_sha256: str) -> dict[str, Any]:
    _require_sha256(mission_sha256, "AUTONOMY_CONTRACT_INVALID")
    return {
        "escalation": "TWO_DISTINCT_PROOF_BOUND_APPROACHES",
        "mission_sha256": mission_sha256,
        "safe_action": "EXECUTE_NOW_WITHIN_PACKET",
        "schema": AUTONOMY_CONTRACT_SCHEMA,
    }


def validate_autonomy_contract(value: Any) -> dict[str, Any]:
    required = {"escalation", "mission_sha256", "safe_action", "schema"}
    if (
        not isinstance(value, Mapping) or set(value) != required
        or value.get("schema") != AUTONOMY_CONTRACT_SCHEMA
        or value.get("safe_action") != "EXECUTE_NOW_WITHIN_PACKET"
        or value.get("escalation") != "TWO_DISTINCT_PROOF_BOUND_APPROACHES"
    ):
        raise ContractError("AUTONOMY_CONTRACT_INVALID")
    _require_sha256(value["mission_sha256"], "AUTONOMY_CONTRACT_INVALID")
    return copy.deepcopy(dict(value))


def classify_autonomy_action(
    *, local: bool, reversible: bool, in_scope: bool,
    external_effect: bool, destructive: bool, owner_boundary: bool,
    failed_approaches: int = 0,
) -> str:
    """Classify an action without using model judgment or mutable counters."""
    if any(not isinstance(value, bool) for value in (
        local, reversible, in_scope, external_effect, destructive, owner_boundary,
    )) or isinstance(failed_approaches, bool) or not isinstance(failed_approaches, int) or failed_approaches < 0:
        raise ContractError("AUTONOMY_ACTION_INVALID")
    if destructive or external_effect or owner_boundary or not in_scope:
        return "OWNER_ACTION"
    if local and reversible:
        return "EXECUTE_NOW"
    if failed_approaches >= 2:
        return "THINKER_REVIEW"
    return "WORKER_LOCAL_REPAIR"


def classify_question_admission(value: Any) -> str:
    """Return the only permitted next route for an outbound question."""
    required = {
        "architecture_security_boundary", "distinct_failed_approaches",
        "owner_boundary", "schema", "single_route_failed",
        "stable_material_diff", "subagent_available",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        return "CONTINUE_LOCAL"
    if (
        value.get("schema") != QUESTION_ADMISSION_SCHEMA
        or any(
            not isinstance(value.get(name), bool)
            for name in required - {"schema", "distinct_failed_approaches"}
        )
        or isinstance(value.get("distinct_failed_approaches"), bool)
        or not isinstance(value.get("distinct_failed_approaches"), int)
        or value["distinct_failed_approaches"] < 0
    ):
        return "CONTINUE_LOCAL"
    if value["owner_boundary"]:
        return "OWNER_REQUIRED"
    if (
        value["stable_material_diff"]
        or value["architecture_security_boundary"]
        or value["distinct_failed_approaches"] >= 2
    ):
        return "THINKER_ALLOWED"
    if value["single_route_failed"]:
        return "SUBAGENT_ONCE" if value["subagent_available"] else "LOCAL_FALLBACK"
    return "CONTINUE_LOCAL"


def validate_approach_receipts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ContractError("APPROACH_RECEIPTS_INVALID")
    output: list[dict[str, Any]] = []
    identities: set[str] = set()
    required = {
        "action_class", "approach_id", "approach_sha256", "evidence_path",
        "evidence_sha256", "failure_code", "hypothesis", "next_route",
        "progress", "route", "source_hashes", "schema",
    }
    for item in value:
        if not isinstance(item, Mapping) or set(item) != required or item.get("schema") != APPROACH_RECEIPT_SCHEMA:
            raise ContractError("APPROACH_RECEIPTS_INVALID")
        for field in ("action_class", "approach_id", "failure_code", "hypothesis", "next_route", "route"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ContractError("APPROACH_RECEIPTS_INVALID")
        if not isinstance(item.get("progress"), bool):
            raise ContractError("APPROACH_RECEIPTS_INVALID")
        canonical_repo_path(item["evidence_path"])
        _require_sha256(item["evidence_sha256"], "APPROACH_RECEIPTS_INVALID")
        sources = item["source_hashes"]
        if not isinstance(sources, Mapping) or not sources or any(
            not isinstance(path, str) or canonical_repo_path(path) != path
            or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            for path, digest in sources.items()
        ):
            raise ContractError("APPROACH_RECEIPTS_INVALID")
        unsigned = {key: copy.deepcopy(item[key]) for key in required - {"approach_sha256"}}
        digest = _canonical_hash(unsigned)
        if item["approach_sha256"] != digest:
            raise ContractError("APPROACH_RECEIPT_HASH_INVALID")
        identity = _canonical_hash({
            "route": item["route"], "evidence_sha256": item["evidence_sha256"],
            "failure_code": item["failure_code"], "progress": item["progress"],
        })
        if identity in identities:
            continue
        identities.add(identity)
        output.append(copy.deepcopy(dict(item)))
    return output


def consultation_key(
    *, work_order_id: str, action_class: str, review_class: str,
    evidence_sha256: str, question_sha256: str, staged_tree_sha256: str,
    thinker_id: str,
) -> str:
    for value in (work_order_id, action_class, review_class, thinker_id):
        if not isinstance(value, str) or not value.strip():
            raise ContractError("CONSULTATION_KEY_INVALID")
    _require_sha256(evidence_sha256, "CONSULTATION_KEY_INVALID")
    _require_sha256(question_sha256, "CONSULTATION_KEY_INVALID")
    _require_sha256(staged_tree_sha256, "CONSULTATION_KEY_INVALID")
    return _canonical_hash({
        "action_class": action_class, "evidence_sha256": evidence_sha256,
        "question_sha256": question_sha256,
        "review_class": review_class, "staged_tree_sha256": staged_tree_sha256,
        "thinker_id": thinker_id, "work_order_id": work_order_id,
    })


def validate_autonomy_proxy(value: Any) -> dict[str, Any]:
    required = {
        "consultation_count", "distinct_failed_approaches", "duplicate_reviews_suppressed",
        "repeated_context_bytes_avoided", "subagent_count", "subagent_profile", "token_usage",
        "work_order_count",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        raise ContractError("AUTONOMY_PROXY_INVALID")
    for field in required - {"subagent_profile", "token_usage", "repeated_context_bytes_avoided"}:
        item = value[field]
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            raise ContractError("AUTONOMY_PROXY_INVALID")
    if value["repeated_context_bytes_avoided"] != "Unknown" and (
        isinstance(value["repeated_context_bytes_avoided"], bool)
        or not isinstance(value["repeated_context_bytes_avoided"], int)
        or value["repeated_context_bytes_avoided"] < 0
    ):
        raise ContractError("AUTONOMY_PROXY_INVALID")
    if value["token_usage"] != "Unknown" and (
        isinstance(value["token_usage"], bool) or not isinstance(value["token_usage"], int)
        or value["token_usage"] < 0
    ):
        raise ContractError("AUTONOMY_PROXY_INVALID")
    if value["subagent_profile"] is not None and (
        not isinstance(value["subagent_profile"], str) or not value["subagent_profile"].strip()
    ):
        raise ContractError("AUTONOMY_PROXY_INVALID")
    if value["subagent_count"] > 1:
        raise ContractError("AUTONOMY_SUBAGENT_LIMIT")
    return copy.deepcopy(dict(value))


def worker_result_contract_binding() -> dict[str, str]:
    try:
        validator_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except OSError as exc:
        raise ContractError("WORKER_RESULT_VALIDATOR_UNAVAILABLE") from exc
    return {
        "proof_schema": "x9-loop-proof-v2",
        "result_schema": "x9-loop-result-v2",
        "validator_path": WORKER_RESULT_VALIDATOR_PATH,
        "validator_sha256": validator_sha256,
    }


def _validate_worker_result_contract(value: Any) -> dict[str, str]:
    if (
        not isinstance(value, Mapping)
        or set(value)
        != {
            "proof_schema", "result_schema", "validator_path",
            "validator_sha256",
        }
        or value.get("proof_schema") != "x9-loop-proof-v2"
        or value.get("result_schema") != "x9-loop-result-v2"
        or value.get("validator_path") != WORKER_RESULT_VALIDATOR_PATH
    ):
        raise ContractError("WORKER_RESULT_CONTRACT_INVALID")
    canonical_repo_path(value["validator_path"])
    _require_sha256(value["validator_sha256"], "WORKER_RESULT_CONTRACT_INVALID")
    return copy.deepcopy(dict(value))


def validate_candidate_handoff(value: Any) -> dict[str, Any]:
    required = {
        "files",
        "schema",
        "source_base_sha",
        "source_event_id",
        "source_result_sha256",
        "source_task_id",
        "source_worker_id",
        "source_work_order_id",
        "source_worktree_id",
        "source_worktree_path",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        raise ContractError("CANDIDATE_HANDOFF_FIELDS_INVALID")
    if value["schema"] != "x9-loop-candidate-handoff-v1":
        raise ContractError("CANDIDATE_HANDOFF_SCHEMA_INVALID")
    _require_git_sha(value["source_base_sha"], "CANDIDATE_HANDOFF_BASE_INVALID")
    _require_sha256(
        value["source_result_sha256"],
        "CANDIDATE_HANDOFF_RESULT_INVALID",
    )
    for field in (
        "source_event_id",
        "source_task_id",
        "source_worker_id",
        "source_work_order_id",
        "source_worktree_id",
        "source_worktree_path",
    ):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ContractError(f"CANDIDATE_HANDOFF_IDENTITY_INVALID:{field}")
    files = value["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= 256:
        raise ContractError("CANDIDATE_HANDOFF_FILES_INVALID")
    paths: list[str] = []
    for item in files:
        if (
            not isinstance(item, Mapping)
            or set(item) != {"path", "sha256", "state"}
            or item["state"] not in {"DELETED", "PRESENT"}
        ):
            raise ContractError("CANDIDATE_HANDOFF_FILE_INVALID")
        paths.append(canonical_repo_path(item["path"]))
        if item["state"] == "PRESENT":
            _require_sha256(
                item["sha256"], "CANDIDATE_HANDOFF_FILE_INVALID"
            )
        elif item["sha256"] is not None:
            raise ContractError("CANDIDATE_HANDOFF_FILE_INVALID")
    _canonical_paths_unique(paths)
    validated = copy.deepcopy(dict(value))
    if len(canonical_json_bytes(validated)) > 12 * 1024:
        raise ContractError("CANDIDATE_HANDOFF_TOO_LARGE")
    return validated


class ContractError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _reject_floats(value: Any, seen: set[int] | None = None) -> None:
    if isinstance(value, float):
        raise ContractError("CANONICAL_FLOAT_FORBIDDEN")
    if isinstance(value, Mapping):
        identity = id(value)
        seen = set() if seen is None else seen
        if identity in seen:
            raise ContractError("CANONICAL_JSON_CYCLIC")
        seen.add(identity)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ContractError("CANONICAL_KEY_INVALID")
                _reject_floats(item, seen)
        finally:
            seen.remove(identity)
    elif isinstance(value, (list, tuple)):
        identity = id(value)
        seen = set() if seen is None else seen
        if identity in seen:
            raise ContractError("CANONICAL_JSON_CYCLIC")
        seen.add(identity)
        try:
            for item in value:
                _reject_floats(item, seen)
        finally:
            seen.remove(identity)


def canonical_json_bytes(payload: Any) -> bytes:
    try:
        _reject_floats(payload)
    except RecursionError as exc:
        raise ContractError("CANONICAL_JSON_RECURSION") from exc
    try:
        text = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except RecursionError as exc:
        raise ContractError("CANONICAL_JSON_RECURSION") from exc
    except (TypeError, ValueError) as exc:
        raise ContractError("CANONICAL_JSON_INVALID") from exc
    return (text + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require_sha256(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ContractError(code)
    return value


def _require_git_sha(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        raise ContractError(code)
    return value


def _require_bounded_id(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value
    ):
        raise ContractError(code)
    return value


def canonical_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ContractError("CANONICAL_PATH_INVALID")
    normalized = unicodedata.normalize("NFC", value).replace("\\", "/")
    drive, _ = ntpath.splitdrive(normalized)
    if drive or normalized.startswith("/"):
        raise ContractError("CANONICAL_PATH_INVALID")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ContractError("CANONICAL_PATH_INVALID")
    canonical = str(PurePosixPath(*parts))
    if canonical != normalized:
        raise ContractError("CANONICAL_PATH_INVALID")
    return canonical


def _canonical_paths_unique(values: Sequence[str]) -> list[str]:
    canonical = [canonical_repo_path(value) for value in values]
    folded: dict[str, str] = {}
    for path in canonical:
        key = path.casefold()
        if key in folded:
            raise ContractError("CANONICAL_PATH_COLLISION")
        folded[key] = path
    return sorted(canonical, key=lambda item: item.encode("utf-8"))


def validate_packet_cap(name: str, payload: bytes) -> None:
    maximum = PACKET_CAPS.get(name)
    if maximum is None:
        raise ContractError(f"PACKET_CAP_UNKNOWN:{name}")
    if len(payload) > maximum:
        raise ContractError(f"PACKET_CAP_EXCEEDED:{name}")


def _load_canonical_packet(
    raw: bytes,
    expected_sha256: str,
    packet_name: str,
    error_prefix: str,
) -> dict[str, Any]:
    _require_sha256(expected_sha256, f"{error_prefix}_HASH_INVALID")
    if not isinstance(raw, bytes) or sha256_bytes(raw) != expected_sha256:
        raise ContractError(f"{error_prefix}_HASH_MISMATCH")
    validate_packet_cap(packet_name, raw)
    try:
        packet = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{error_prefix}_JSON_INVALID") from exc
    if not isinstance(packet, dict):
        raise ContractError(f"{error_prefix}_JSON_INVALID")
    if canonical_json_bytes(packet) != raw:
        raise ContractError(f"{error_prefix}_BYTES_NONCANONICAL")
    return packet


def validate_inbox_event(
    raw: bytes,
    expected_sha256: str,
    expected_profile_id: str,
) -> dict[str, Any]:
    event = _load_canonical_packet(
        raw, expected_sha256, "INBOX_EVENT.json", "INBOX_EVENT"
    )
    required = {
        "event_id",
        "event_type",
        "payload_ref",
        "project_profile_id",
        "schema",
        "source_actor_id",
        "source_role",
    }
    if set(event) != required:
        raise ContractError("INBOX_EVENT_FIELDS_INVALID")
    if event["schema"] != "x9-loop-inbox-event-v1":
        raise ContractError("INBOX_EVENT_SCHEMA_INVALID")

    role_by_type = {
        "THINX_RESULT": "THINKER",
        "TRANSPORT_ACK": "LINKER",
        "WORKER_RESULT": "WORKER",
    }
    if event["event_type"] not in role_by_type:
        raise ContractError("INBOX_EVENT_TYPE_INVALID")
    if event["source_role"] != role_by_type[event["event_type"]]:
        raise ContractError("INBOX_EVENT_ROLE_MISMATCH")
    _require_bounded_id(event["event_id"], "INBOX_EVENT_ID_INVALID")
    _require_bounded_id(event["source_actor_id"], "INBOX_EVENT_ACTOR_INVALID")
    _require_bounded_id(
        event["project_profile_id"], "INBOX_EVENT_PROFILE_INVALID"
    )
    _require_bounded_id(expected_profile_id, "INBOX_EVENT_PROFILE_INVALID")
    if event["project_profile_id"] != expected_profile_id:
        raise ContractError("INBOX_EVENT_PROFILE_MISMATCH")

    payload_ref = event["payload_ref"]
    if not isinstance(payload_ref, Mapping) or set(payload_ref) != {"path", "sha256"}:
        raise ContractError("INBOX_PAYLOAD_REF_INVALID")
    path = canonical_repo_path(payload_ref["path"])
    if not path.endswith(".json"):
        raise ContractError("INBOX_PAYLOAD_REF_INVALID")
    _require_sha256(payload_ref["sha256"], "INBOX_PAYLOAD_REF_INVALID")
    return copy.deepcopy(event)


RESULT_READY_IDENTITY_FIELDS = {
    "dispatch_id",
    "event_id",
    "packet_sha256",
    "result_path",
    "result_sha256",
    "task_id",
    "work_order_id",
    "work_order_sha256",
    "worker_id",
}


def _validate_result_ready_identity(value: Any) -> dict[str, str]:
    if (
        not isinstance(value, Mapping)
        or set(value) != RESULT_READY_IDENTITY_FIELDS
    ):
        raise ContractError("RESULT_READY_IDENTITY_INVALID")
    for field in (
        "dispatch_id",
        "event_id",
        "task_id",
        "work_order_id",
        "worker_id",
    ):
        _require_bounded_id(value[field], "RESULT_READY_IDENTITY_INVALID")
    for field in ("packet_sha256", "result_sha256", "work_order_sha256"):
        _require_sha256(value[field], "RESULT_READY_IDENTITY_INVALID")
    canonical_repo_path(value["result_path"])
    return copy.deepcopy(dict(value))


def build_result_ready(
    *,
    callback_id: str,
    expected_result_identity: Mapping[str, Any],
    expires_at: str,
    project_profile_id: str,
    return_to_task_id: str,
) -> dict[str, Any]:
    signal = {
        "callback_id": callback_id,
        "expected_result_identity": _validate_result_ready_identity(
            expected_result_identity
        ),
        "expires_at": expires_at,
        "project_profile_id": project_profile_id,
        "return_to_task_id": return_to_task_id,
        "schema": "x9-loop-result-ready-v1",
        "source_role": "WORKER",
        "status": "READY",
    }
    _require_bounded_id(signal["callback_id"], "RESULT_READY_ID_INVALID")
    _require_bounded_id(signal["expires_at"], "RESULT_READY_EXPIRY_INVALID")
    _require_bounded_id(
        signal["project_profile_id"], "RESULT_READY_PROFILE_INVALID"
    )
    _require_bounded_id(
        signal["return_to_task_id"], "RESULT_READY_REQUESTER_INVALID"
    )
    return signal


def validate_result_ready(
    raw: bytes,
    expected_sha256: str,
    expected_profile_id: str,
    *,
    expected_identity: Mapping[str, Any] | None = None,
    expected_requester: str | None = None,
) -> dict[str, Any]:
    signal = _load_canonical_packet(
        raw, expected_sha256, "RESULT_READY.json", "RESULT_READY"
    )
    required = {
        "callback_id",
        "expected_result_identity",
        "expires_at",
        "project_profile_id",
        "return_to_task_id",
        "schema",
        "source_role",
        "status",
    }
    if set(signal) != required:
        raise ContractError("RESULT_READY_FIELDS_INVALID")
    if signal["schema"] != "x9-loop-result-ready-v1":
        raise ContractError("RESULT_READY_SCHEMA_INVALID")
    if signal["status"] != "READY" or signal["source_role"] != "WORKER":
        raise ContractError("RESULT_READY_STATE_INVALID")
    _require_bounded_id(signal["callback_id"], "RESULT_READY_ID_INVALID")
    _require_bounded_id(signal["expires_at"], "RESULT_READY_EXPIRY_INVALID")
    _require_bounded_id(
        signal["project_profile_id"], "RESULT_READY_PROFILE_INVALID"
    )
    _require_bounded_id(
        expected_profile_id, "RESULT_READY_PROFILE_INVALID"
    )
    if signal["project_profile_id"] != expected_profile_id:
        raise ContractError("RESULT_READY_PROFILE_MISMATCH")
    _require_bounded_id(
        signal["return_to_task_id"], "RESULT_READY_REQUESTER_INVALID"
    )
    if expected_requester is not None:
        _require_bounded_id(
            expected_requester, "RESULT_READY_REQUESTER_INVALID"
        )
        if signal["return_to_task_id"] != expected_requester:
            raise ContractError("RESULT_READY_REQUESTER_MISMATCH")
    identity = _validate_result_ready_identity(
        signal["expected_result_identity"]
    )
    if expected_identity is not None:
        if _validate_result_ready_identity(expected_identity) != identity:
            raise ContractError("RESULT_READY_IDENTITY_MISMATCH")
    return copy.deepcopy(signal)


def validate_loop_incident(
    raw: bytes,
    expected_sha256: str,
    *,
    expected_identity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    incident = _load_canonical_packet(
        raw, expected_sha256, "LOOP_INCIDENT.json", "LOOP_INCIDENT"
    )
    required = {
        "actual_transition",
        "circuit",
        "claims_sha256",
        "dispatch_id",
        "event_id",
        "evidence_hashes",
        "expected_result_identity",
        "expected_transition",
        "host_enforcement",
        "incident_id",
        "proposed_regression",
        "repair_outcome",
        "reproducer",
        "return_to_task_id",
        "schema",
        "task_id",
        "worker_id",
        "work_order_id",
        "worktree_id",
        "worktree_path",
    }
    if set(incident) != required:
        raise ContractError("LOOP_INCIDENT_FIELDS_INVALID")
    if incident["schema"] != "x9-loop-incident-v1":
        raise ContractError("LOOP_INCIDENT_SCHEMA_INVALID")
    if incident["circuit"] != "OPEN":
        raise ContractError("LOOP_INCIDENT_STATE_INVALID")
    for field in (
        "dispatch_id",
        "event_id",
        "incident_id",
        "return_to_task_id",
        "task_id",
        "worker_id",
        "work_order_id",
        "worktree_id",
    ):
        _require_bounded_id(incident[field], "LOOP_INCIDENT_ID_INVALID")
    _require_sha256(incident["claims_sha256"], "LOOP_INCIDENT_HASH_INVALID")
    evidence = incident["evidence_hashes"]
    if (
        not isinstance(evidence, Mapping)
        or set(evidence)
        != {"expected_signal_sha256", "result_sha256", "state_sha256"}
    ):
        raise ContractError("LOOP_INCIDENT_EVIDENCE_INVALID")
    for value in evidence.values():
        _require_sha256(value, "LOOP_INCIDENT_EVIDENCE_INVALID")
    _validate_result_ready_identity(incident["expected_result_identity"])
    if (
        expected_identity is not None
        and incident["expected_result_identity"]
        != _validate_result_ready_identity(expected_identity)
    ):
        raise ContractError("LOOP_INCIDENT_IDENTITY_MISMATCH")
    for field in (
        "actual_transition",
        "expected_transition",
        "host_enforcement",
        "proposed_regression",
        "repair_outcome",
        "reproducer",
        "worktree_path",
    ):
        if not isinstance(incident[field], str) or not incident[field].strip():
            raise ContractError("LOOP_INCIDENT_FIELDS_INVALID")
    return copy.deepcopy(incident)


def validate_transport_ack(
    raw: bytes,
    expected_sha256: str,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    ack = _load_canonical_packet(
        raw, expected_sha256, "TRANSPORT_ACK.json", "TRANSPORT_ACK"
    )
    required = {
        "ack_id",
        "action",
        "action_id",
        "action_sha256",
        "dispatch_id",
        "project_profile_id",
        "schema",
        "status",
        "work_order_id",
        "work_order_sha256",
        "worker_id",
    }
    identity_fields = {
        "action_id",
        "action_sha256",
        "dispatch_id",
        "project_profile_id",
        "work_order_id",
        "work_order_sha256",
        "worker_id",
    }
    if set(ack) != required:
        raise ContractError("TRANSPORT_ACK_FIELDS_INVALID")
    if not isinstance(expected, Mapping) or set(expected) != identity_fields:
        raise ContractError("TRANSPORT_ACK_EXPECTED_INVALID")
    if (
        ack["schema"] != "x9-loop-transport-ack-v1"
        or ack["action"] not in {"SEND_WORK_ORDER", "RESULT_SCHEMA_REPAIR"}
        or ack["status"] != "DELIVERED"
    ):
        raise ContractError("TRANSPORT_ACK_SCHEMA_INVALID")

    for field in (
        "ack_id", "action_id", "dispatch_id", "project_profile_id",
        "work_order_id", "worker_id",
    ):
        _require_bounded_id(ack[field], "TRANSPORT_ACK_ID_INVALID")
    for field in ("action_sha256", "work_order_sha256"):
        _require_sha256(ack[field], "TRANSPORT_ACK_HASH_INVALID")
    for field in identity_fields:
        if ack[field] != expected[field]:
            raise ContractError(f"TRANSPORT_ACK_IDENTITY_MISMATCH:{field}")
    return copy.deepcopy(ack)


def validate_context_complete(feature_packet: Mapping[str, Any]) -> None:
    for field in REQUIRED_CONTEXT_FIELDS:
        if field not in feature_packet or feature_packet[field] is None:
            raise ContractError(f"CONTEXT_INCOMPLETE:{field}")
    if feature_packet.get("schema") != "x9-loop-feature-v1":
        raise ContractError("CONTEXT_INCOMPLETE:schema")
    for field in ("feature_id", "owner_requirement", "worktree_id", "worktree_path", "base_sha"):
        if not isinstance(feature_packet.get(field), str) or not feature_packet[field].strip():
            raise ContractError(f"CONTEXT_INCOMPLETE:{field}")
    capsule_ref = feature_packet.get("context_capsule_ref")
    if capsule_ref is not None:
        required = {"bytes", "capsule_id", "path", "sha256"}
        if not isinstance(capsule_ref, Mapping) or set(capsule_ref) != required:
            raise ContractError("CONTEXT_CAPSULE_REF_INVALID")
        if (isinstance(capsule_ref["bytes"], bool)
                or not isinstance(capsule_ref["bytes"], int)
                or not 1 <= capsule_ref["bytes"] <= 16 * 1024):
            raise ContractError("CONTEXT_CAPSULE_REF_INVALID")
        if not isinstance(capsule_ref["capsule_id"], str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", capsule_ref["capsule_id"]):
            raise ContractError("CONTEXT_CAPSULE_REF_INVALID")
        canonical_repo_path(capsule_ref["path"])
        _require_sha256(capsule_ref["sha256"], "CONTEXT_CAPSULE_REF_INVALID")


def _validate_stop(stop: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "schema",
        "success_predicate",
        "max_attempts",
        "max_wall_seconds",
        "max_model_calls",
        "max_tokens",
    )
    for field in required:
        if field not in stop:
            raise ContractError(f"STOP_CONTRACT_INCOMPLETE:{field}")
    if stop["schema"] != "x9-loop-stop-contract-v1":
        raise ContractError("STOP_CONTRACT_SCHEMA_INVALID")
    for field in ("max_attempts", "max_wall_seconds", "max_model_calls"):
        value = stop[field]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ContractError(f"STOP_CONTRACT_INVALID:{field}")
    tokens = stop["max_tokens"]
    if tokens is not None and (isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0):
        raise ContractError("STOP_CONTRACT_INVALID:max_tokens")
    if not isinstance(stop["success_predicate"], str) or not stop["success_predicate"].strip():
        raise ContractError("STOP_CONTRACT_INVALID:success_predicate")
    return copy.deepcopy(dict(stop))


def _ordered_unique(values: Sequence[Any]) -> list[Any]:
    ordered: dict[bytes, Any] = {}
    for value in values:
        encoded = canonical_json_bytes(value)
        if encoded in ordered:
            raise ContractError("CANONICAL_DUPLICATE_VALUE")
        ordered[encoded] = copy.deepcopy(value)
    return [ordered[key] for key in sorted(ordered)]


def _normalized_claims(values: Any) -> list[dict[str, str]]:
    if not isinstance(values, (list, tuple)):
        raise ContractError("CLAIMS_INVALID")
    claims: list[dict[str, str]] = []
    folded: set[str] = set()
    for value in values:
        if isinstance(value, str):
            path, kind = canonical_repo_path(value), "file"
        elif isinstance(value, Mapping) and set(value) == {"path", "kind"}:
            path, kind = canonical_repo_path(value["path"]), value["kind"]
        else:
            raise ContractError("CLAIMS_INVALID")
        if kind not in {"file", "dir"}:
            raise ContractError("CLAIMS_INVALID")
        key = path.casefold()
        if key in folded:
            raise ContractError("CANONICAL_PATH_COLLISION")
        folded.add(key)
        claims.append({"kind": kind, "path": path})
    return sorted(claims, key=lambda item: (item["path"].encode("utf-8"), item["kind"]))


def canonical_resource_keys(values: Any) -> list[str]:
    """Return the Controller storage/comparison keys for declared resources."""
    if not isinstance(values, (list, tuple)) or any(
        not isinstance(item, str) or not item.strip() for item in values
    ):
        raise ContractError("RESOURCES_INVALID")
    keys = [item.casefold() for item in values]
    if len(keys) != len(set(keys)):
        raise ContractError("CANONICAL_RESOURCE_COLLISION")
    return sorted(keys)


def _normalized_resources(values: Any) -> list[str]:
    canonical_resource_keys(values)
    return _ordered_unique(list(values))


def _validate_feature_assignment(feature: Mapping[str, Any]) -> None:
    required = (
        "base_sha",
        "claims",
        "dependencies",
        "feature_id",
        "finish_line",
        "path",
        "resources",
        "sha256",
        "worker_id",
        "worktree_id",
        "worktree_path",
    )
    for field in required:
        if field not in feature:
            raise ContractError(f"FEATURE_ASSIGNMENT_INCOMPLETE:{field}")
    _require_git_sha(feature["base_sha"], "FEATURE_BASE_SHA_INVALID")
    _require_sha256(feature["sha256"], "FEATURE_PACKET_SHA_INVALID")
    canonical_repo_path(feature["path"])
    _normalized_claims(feature["claims"])
    _normalized_resources(feature["resources"])
    dependencies = feature["dependencies"]
    if (
        not isinstance(dependencies, (list, tuple))
        or any(not isinstance(item, str) or not item.strip() for item in dependencies)
        or len(dependencies) != len(set(dependencies))
    ):
        raise ContractError("FEATURE_DEPENDENCIES_INVALID")
    finish_line = feature["finish_line"]
    if not (
        (isinstance(finish_line, str) and finish_line.strip())
        or (isinstance(finish_line, (list, tuple)) and finish_line and all(isinstance(item, str) and item.strip() for item in finish_line))
    ):
        raise ContractError("FEATURE_FINISH_LINE_INVALID")
    for field in ("feature_id", "worker_id", "worktree_id", "worktree_path"):
        if not isinstance(feature[field], str) or not feature[field].strip():
            raise ContractError(f"FEATURE_ASSIGNMENT_INVALID:{field}")


def _validate_two_feature_atomicity(features: Sequence[Mapping[str, Any]]) -> None:
    if len(features) != 2:
        return
    for feature in features:
        if feature.get("atomic_compatible") is not True:
            raise ContractError("TWO_FEATURE_NOT_ATOMIC")
        _require_sha256(feature.get("compatibility_hash"), "TWO_FEATURE_NOT_ATOMIC")
    matching = (
        "atomic_bundle",
        "base_sha",
        "claims",
        "compatibility_hash",
        "dependencies",
        "finish_line",
        "resources",
        "worker_id",
        "worktree_id",
        "worktree_path",
    )
    for field in matching:
        values = {canonical_json_bytes(feature.get(field)) for feature in features}
        if len(values) != 1 or next(iter(values)) in {b"null\n", b'""\n'}:
            raise ContractError("TWO_FEATURE_NOT_ATOMIC")


def build_work_order(
    *,
    action_class: str,
    created_at: str,
    features: Sequence[Mapping[str, Any]],
    program_packet_ref: Mapping[str, str],
    source_git_sha: str,
    source_root_sha256: str,
    stop: Mapping[str, Any],
    task_id: str,
    work_order_id: str,
    candidate_handoff: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bytes, str]:
    if not 1 <= len(features) <= 2:
        raise ContractError("WORK_ORDER_FEATURE_LIMIT")
    if not all(isinstance(value, str) and value.strip() for value in (action_class, created_at, task_id, work_order_id)):
        raise ContractError("WORK_ORDER_IDENTITY_INVALID")
    _require_git_sha(source_git_sha, "SOURCE_GIT_SHA_INVALID")
    _require_sha256(source_root_sha256, "SOURCE_ROOT_SHA_INVALID")
    for feature in features:
        _validate_feature_assignment(feature)
    _validate_two_feature_atomicity(features)
    if set(program_packet_ref) != {"path", "sha256"}:
        raise ContractError("PROGRAM_PACKET_REF_INVALID")
    program_path = canonical_repo_path(program_packet_ref["path"])
    program_sha256 = _require_sha256(program_packet_ref["sha256"], "PROGRAM_PACKET_SHA_INVALID")
    ordered = sorted(features, key=lambda item: str(item["feature_id"]))
    if len({str(feature["feature_id"]).casefold() for feature in ordered}) != len(ordered):
        raise ContractError("FEATURE_ID_COLLISION")
    first = ordered[0]
    refs = [
        {
            "feature_id": feature["feature_id"],
            "path": canonical_repo_path(feature["path"]),
            "sha256": _require_sha256(feature["sha256"], "FEATURE_PACKET_SHA_INVALID"),
        }
        for feature in ordered
    ]
    _canonical_paths_unique([ref["path"] for ref in refs])
    order = {
        "action_class": action_class,
        "base_sha": first["base_sha"],
        "claims": _normalized_claims(first["claims"]),
        "created_at": created_at,
        "feature_packet_refs": refs,
        "linx_read_scope": "ACTION_ONLY",
        "program_packet_path": program_path,
        "program_packet_sha256": program_sha256,
        "resources": _normalized_resources(first["resources"]),
        "schema": "x9-loop-work-order-v1",
        "source_git_sha": source_git_sha,
        "source_root_sha256": source_root_sha256,
        "state": "CREATED",
        "stop_contract": _validate_stop(stop),
        "task_id": task_id,
        "work_order_id": work_order_id,
        "worker_id": first["worker_id"],
        "worktree_id": first["worktree_id"],
        "worktree_path": first["worktree_path"],
        "worker_result_contract": worker_result_contract_binding(),
        "writer": "Controller",
    }
    mission_sha256 = mission_identity(
        action_class=action_class,
        features=ordered,
        program_packet_ref=program_packet_ref,
        stop=stop,
    )
    order["autonomy_contract"] = build_autonomy_contract(mission_sha256)
    if candidate_handoff is not None:
        order["candidate_handoff"] = validate_candidate_handoff(candidate_handoff)
    raw = canonical_json_bytes(order)
    validate_packet_cap("WORK_ORDER.json", raw)
    return order, raw, sha256_bytes(raw)


def bound_work_order_context(order: Mapping[str, Any]) -> dict[str, Any]:
    bound = {field: copy.deepcopy(order.get(field)) for field in WORK_ORDER_BINDINGS}
    if "worker_result_contract" in order:
        bound["worker_result_contract"] = copy.deepcopy(order["worker_result_contract"])
    if "candidate_handoff" in order:
        bound["candidate_handoff"] = copy.deepcopy(order["candidate_handoff"])
    return bound


def validate_work_order_identity(
    raw: bytes,
    expected_sha256: str,
    current_context: Mapping[str, Any],
) -> dict[str, Any]:
    _require_sha256(expected_sha256, "WORK_ORDER_HASH_INVALID")
    if not isinstance(raw, bytes) or sha256_bytes(raw) != expected_sha256:
        raise ContractError("WORK_ORDER_HASH_MISMATCH")
    try:
        order = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("WORK_ORDER_JSON_INVALID") from exc
    if not isinstance(order, dict):
        raise ContractError("WORK_ORDER_JSON_INVALID")
    if canonical_json_bytes(order) != raw:
        raise ContractError("WORK_ORDER_BYTES_NONCANONICAL")
    validate_packet_cap("WORK_ORDER.json", raw)
    required = {
        "action_class", "base_sha", "claims", "created_at", "feature_packet_refs",
        "linx_read_scope", "program_packet_path", "program_packet_sha256", "resources",
        "schema", "source_git_sha", "source_root_sha256", "state", "stop_contract",
        "task_id", "work_order_id", "worker_id", "worktree_id", "worktree_path", "writer",
    }
    optional = {"autonomy_contract", "candidate_handoff", "worker_result_contract"}
    if not required.issubset(order) or set(order) - required - optional:
        raise ContractError("WORK_ORDER_FIELDS_INVALID")
    if "worker_result_contract" in order:
        _validate_worker_result_contract(order["worker_result_contract"])
    if "autonomy_contract" in order:
        validate_autonomy_contract(order["autonomy_contract"])
    if "candidate_handoff" in order:
        validate_candidate_handoff(order["candidate_handoff"])
    if order["schema"] != "x9-loop-work-order-v1" or order["state"] != "CREATED":
        raise ContractError("WORK_ORDER_SCHEMA_INVALID")
    if order["writer"] != "Controller" or order["linx_read_scope"] != "ACTION_ONLY":
        raise ContractError("WORK_ORDER_AUTHORITY_INVALID")
    _require_git_sha(order["base_sha"], "WORK_ORDER_BASE_SHA_INVALID")
    _require_git_sha(order["source_git_sha"], "SOURCE_GIT_SHA_INVALID")
    _require_sha256(order["source_root_sha256"], "SOURCE_ROOT_SHA_INVALID")
    _require_sha256(order["program_packet_sha256"], "PROGRAM_PACKET_SHA_INVALID")
    canonical_repo_path(order["program_packet_path"])
    _normalized_claims(order["claims"])
    _normalized_resources(order["resources"])
    _validate_stop(order["stop_contract"])
    for field in ("action_class", "created_at", "task_id", "work_order_id", "worker_id", "worktree_id", "worktree_path"):
        if not isinstance(order[field], str) or not order[field].strip():
            raise ContractError(f"WORK_ORDER_FIELD_INVALID:{field}")
    refs = order["feature_packet_refs"]
    if not isinstance(refs, list) or not 1 <= len(refs) <= 2:
        raise ContractError("WORK_ORDER_FEATURE_LIMIT")
    ref_paths: list[str] = []
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"feature_id", "path", "sha256"}:
            raise ContractError("FEATURE_PACKET_REF_INVALID")
        if not isinstance(ref["feature_id"], str) or not ref["feature_id"].strip():
            raise ContractError("FEATURE_PACKET_REF_INVALID")
        ref_paths.append(canonical_repo_path(ref["path"]))
        _require_sha256(ref["sha256"], "FEATURE_PACKET_SHA_INVALID")
    _canonical_paths_unique(ref_paths)
    if not isinstance(current_context, Mapping):
        raise ContractError("WORK_ORDER_CONTEXT_INVALID")
    for field in WORK_ORDER_BINDINGS:
        if field not in current_context or current_context[field] is None:
            raise ContractError(f"WORK_ORDER_DRIFT:{field}")
        if field == "resources":
            matches = canonical_resource_keys(order[field]) == canonical_resource_keys(
                current_context[field]
            )
        else:
            matches = copy.deepcopy(order[field]) == copy.deepcopy(current_context[field])
        if not matches:
            raise ContractError(f"WORK_ORDER_DRIFT:{field}")
    if "worker_result_contract" in order:
        if copy.deepcopy(current_context.get("worker_result_contract")) != copy.deepcopy(
            order["worker_result_contract"]
        ):
            raise ContractError("WORK_ORDER_DRIFT:worker_result_contract")
    if "candidate_handoff" in order:
        if copy.deepcopy(current_context.get("candidate_handoff")) != copy.deepcopy(
            order["candidate_handoff"]
        ):
            raise ContractError("WORK_ORDER_DRIFT:candidate_handoff")
    return order


def _stop_result(reason: str) -> dict[str, Any]:
    return {
        "action_class": None,
        "allow_call": False,
        "event": "OWNER_DECISION_REQUIRED",
        "reason": reason,
    }


def pre_model_call_gate(
    *,
    action_class: str,
    attempt: int,
    elapsed_seconds: int,
    model_calls: int,
    objective_satisfied: bool,
    prior_receipt: Mapping[str, Any] | None,
    prompt_prefix_sha256: str,
    stop: Mapping[str, Any],
    token_usage: int | str,
    tool_schema_sha256: str,
) -> dict[str, Any]:
    limits = _validate_stop(stop)
    if not isinstance(action_class, str) or not action_class.strip():
        raise ContractError("ACTION_CLASS_INVALID")
    for name, value in (
        ("attempt", attempt),
        ("elapsed_seconds", elapsed_seconds),
        ("model_calls", model_calls),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ContractError(f"STOP_TELEMETRY_INVALID:{name}")
    if not isinstance(objective_satisfied, bool):
        raise ContractError("STOP_TELEMETRY_INVALID:objective_satisfied")
    _require_sha256(prompt_prefix_sha256, "PROMPT_PREFIX_HASH_INVALID")
    _require_sha256(tool_schema_sha256, "TOOL_SCHEMA_HASH_INVALID")
    if objective_satisfied:
        return {
            "action_class": action_class,
            "allow_call": False,
            "event": "FEATURE_DONE",
            "reason": "SUCCESS_PREDICATE_SATISFIED",
        }
    if attempt >= limits["max_attempts"]:
        return _stop_result("MAX_ATTEMPTS")
    if elapsed_seconds >= limits["max_wall_seconds"]:
        return _stop_result("MAX_WALL_SECONDS")
    if model_calls >= limits["max_model_calls"]:
        return _stop_result("MAX_MODEL_CALLS")
    max_tokens = limits["max_tokens"]
    if max_tokens is not None:
        if token_usage == "Unknown":
            return _stop_result("TOKEN_USAGE_UNKNOWN")
        if isinstance(token_usage, bool) or not isinstance(token_usage, int) or token_usage < 0:
            raise ContractError("TOKEN_USAGE_INVALID")
        if token_usage >= max_tokens:
            return _stop_result("MAX_TOKENS")
    elif token_usage != "Unknown" and (
        isinstance(token_usage, bool) or not isinstance(token_usage, int) or token_usage < 0
    ):
        raise ContractError("TOKEN_USAGE_INVALID")

    if prior_receipt is not None:
        if not isinstance(prior_receipt, Mapping):
            raise ContractError("PRIOR_CALL_RECEIPT_INVALID")
        if prior_receipt.get("stability", "STABLE") != "STABLE":
            return {
                "action_class": action_class,
                "allow_call": False,
                "event": "CACHE_PREFIX_CHANGED",
                "reason": "UNRESOLVED_PRIOR_CACHE_DRIFT",
            }
        old_action = prior_receipt.get("action_class")
        old_prompt = prior_receipt.get("prompt_prefix_sha256")
        old_tools = prior_receipt.get("tool_schema_sha256")
        changed = (
            old_action != action_class
            or old_prompt != prompt_prefix_sha256
            or old_tools != tool_schema_sha256
        )
        if changed:
            return {
                "action_class": action_class,
                "allow_call": False,
                "event": "CACHE_PREFIX_CHANGED",
                "reason": "UNEXPLAINED_PROMPT_TOOL_OR_ACTION_DRIFT",
            }
    return {
        "action_class": action_class,
        "allow_call": True,
        "event": None,
        "reason": "WITHIN_STOP_CONTRACT",
    }

def build_call_receipt(
    *,
    action_class: str,
    attempt: int,
    call_id: str,
    compaction_generation: int,
    sequence: int,
    token_usage: int | str,
    work_order_sha256: str,
    pre_prompt_prefix_sha256: str | None = None,
    post_prompt_prefix_sha256: str | None = None,
    pre_tool_schema_sha256: str | None = None,
    post_tool_schema_sha256: str | None = None,
    pre_compaction_prompt_prefix_sha256: str | None = None,
    post_compaction_prompt_prefix_sha256: str | None = None,
    pre_compaction_tool_schema_sha256: str | None = None,
    post_compaction_tool_schema_sha256: str | None = None,
    failure: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pre_prompt = pre_prompt_prefix_sha256 or pre_compaction_prompt_prefix_sha256
    post_prompt = post_prompt_prefix_sha256 or post_compaction_prompt_prefix_sha256
    pre_tools = pre_tool_schema_sha256 or pre_compaction_tool_schema_sha256
    post_tools = post_tool_schema_sha256 or post_compaction_tool_schema_sha256
    if not all(isinstance(value, str) and value for value in (pre_prompt, post_prompt, pre_tools, post_tools)):
        raise ContractError("CALL_RECEIPT_HASH_INCOMPLETE")
    if token_usage != "Unknown" and (
        isinstance(token_usage, bool) or not isinstance(token_usage, int) or token_usage < 0
    ):
        raise ContractError("TOKEN_USAGE_INVALID")
    stable = pre_prompt == post_prompt and pre_tools == post_tools
    receipt = {
        "action_class": action_class,
        "attempt": attempt,
        "call_id": call_id,
        "sequence": sequence,
        "compaction_generation": compaction_generation,
        "drift_reason": "" if stable else "UNEXPLAINED_PROMPT_OR_TOOL_DRIFT",
        "post_compaction_prompt_prefix_sha256": post_prompt,
        "post_compaction_tool_schema_sha256": post_tools,
        "pre_compaction_prompt_prefix_sha256": pre_prompt,
        "pre_compaction_tool_schema_sha256": pre_tools,
        "prompt_prefix_sha256": post_prompt,
        "schema": "x9-loop-call-receipt-v1",
        "stability": "STABLE" if stable else "DRIFTED",
        "token_usage": token_usage,
        "tool_schema_sha256": post_tools,
        "work_order_sha256": work_order_sha256,
    }
    if failure is not None:
        receipt["failure"] = copy.deepcopy(dict(failure))
    validate_call_receipt(receipt)
    return receipt


def validate_call_receipt(
    receipt: Mapping[str, Any],
    expected_work_order_sha256: str | None = None,
) -> dict[str, Any]:
    required = {
        "action_class", "attempt", "call_id", "compaction_generation", "drift_reason",
        "post_compaction_prompt_prefix_sha256", "post_compaction_tool_schema_sha256",
        "pre_compaction_prompt_prefix_sha256", "pre_compaction_tool_schema_sha256",
        "prompt_prefix_sha256", "schema", "sequence", "stability", "token_usage",
        "tool_schema_sha256", "work_order_sha256",
    }
    if (not isinstance(receipt, Mapping)
            or not required.issubset(receipt)
            or set(receipt) - required not in (set(), {"failure"})):
        raise ContractError("CALL_RECEIPT_INVALID")
    if "failure" in receipt:
        failure = receipt["failure"]
        if (not isinstance(failure, Mapping)
                or set(failure) != {"class", "code", "signature", "progress"}
                or failure["class"] not in {"PRODUCT", "INFRASTRUCTURE"}
                or not isinstance(failure["code"], str)
                or not re.fullmatch(r"[A-Z][A-Z0-9_.:-]{0,95}", failure["code"])
                or not isinstance(failure["progress"], bool)):
            raise ContractError("CALL_RECEIPT_FAILURE_INVALID")
        _require_sha256(failure["signature"], "CALL_RECEIPT_FAILURE_INVALID")
    if receipt["schema"] != "x9-loop-call-receipt-v1":
        raise ContractError("CALL_RECEIPT_INVALID")
    if (
        not isinstance(receipt["action_class"], str)
        or not receipt["action_class"].strip()
        or not isinstance(receipt["call_id"], str)
        or not re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", receipt["call_id"])
    ):
        raise ContractError("CALL_RECEIPT_INVALID")
    for field in ("attempt", "compaction_generation", "sequence"):
        value = receipt[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < (1 if field == "sequence" else 0):
            raise ContractError("CALL_RECEIPT_INVALID")
    hash_fields = (
        "post_compaction_prompt_prefix_sha256",
        "post_compaction_tool_schema_sha256",
        "pre_compaction_prompt_prefix_sha256",
        "pre_compaction_tool_schema_sha256",
        "prompt_prefix_sha256",
        "tool_schema_sha256",
        "work_order_sha256",
    )
    for field in hash_fields:
        _require_sha256(receipt[field], "CALL_RECEIPT_INVALID")
    token_usage = receipt["token_usage"]
    if token_usage != "Unknown" and (
        isinstance(token_usage, bool) or not isinstance(token_usage, int) or token_usage < 0
    ):
        raise ContractError("CALL_RECEIPT_INVALID")
    prompt_stable = (
        receipt["pre_compaction_prompt_prefix_sha256"]
        == receipt["post_compaction_prompt_prefix_sha256"]
    )
    tools_stable = (
        receipt["pre_compaction_tool_schema_sha256"]
        == receipt["post_compaction_tool_schema_sha256"]
    )
    expected_stability = "STABLE" if prompt_stable and tools_stable else "DRIFTED"
    expected_reason = "" if expected_stability == "STABLE" else "UNEXPLAINED_PROMPT_OR_TOOL_DRIFT"
    if (
        receipt["stability"] != expected_stability
        or receipt["drift_reason"] != expected_reason
        or receipt["prompt_prefix_sha256"] != receipt["post_compaction_prompt_prefix_sha256"]
        or receipt["tool_schema_sha256"] != receipt["post_compaction_tool_schema_sha256"]
    ):
        raise ContractError("CALL_RECEIPT_INVALID")
    if (
        expected_work_order_sha256 is not None
        and receipt["work_order_sha256"] != _require_sha256(
            expected_work_order_sha256, "CALL_RECEIPT_INVALID"
        )
    ):
        raise ContractError("CALL_RECEIPT_WORK_ORDER_MISMATCH")
    validate_packet_cap("CALL_RECEIPT.json", canonical_json_bytes(dict(receipt)))
    return copy.deepcopy(dict(receipt))


def map_worker_event(
    outcome: str,
    *,
    failed_verified_approaches: int = 0,
    budget_remaining: bool = True,
    approach_receipts: Sequence[Mapping[str, Any]] | None = None,
) -> str | None:
    if (
        isinstance(failed_verified_approaches, bool)
        or not isinstance(failed_verified_approaches, int)
        or failed_verified_approaches < 0
        or not isinstance(budget_remaining, bool)
    ):
        raise ContractError("WORKER_EVENT_TELEMETRY_INVALID")
    if outcome in {"SUCCESS", "SUCCESS_CANDIDATE"}:
        return "FEATURE_DONE"
    if outcome in {
        "HARD_EXTERNAL",
        "OWNER_CONFLICT",
        "STOP_EXHAUSTED",
        "CACHE_DRIFT_UNRESOLVED",
    }:
        return "OWNER_DECISION_REQUIRED"
    if outcome == "VERIFIED_FAILURE":
        threshold = 3
        if approach_receipts is not None:
            threshold = 2
            if failed_verified_approaches != len(approach_receipts):
                raise ContractError("APPROACH_RECEIPT_COUNT_MISMATCH")
        if failed_verified_approaches >= threshold and budget_remaining:
            return "HARD_BLOCKER_AFTER_2_PROOFS" if threshold == 2 else "HARD_BLOCKER_AFTER_3_PROOFS"
        if failed_verified_approaches >= threshold and not budget_remaining:
            return "OWNER_DECISION_REQUIRED"
        return None
    if outcome == "SCOPE_CONFLICT":
        return "TASK_SCOPE_PAUSED"
    if outcome == "SOFT_LOCAL":
        return None
    raise ContractError(f"WORKER_OUTCOME_UNKNOWN:{outcome}")

JOB_RELEVANCE = {
    "CURRENT_PROJECT_MONITOR",
    "OTHER_PROJECT_JOB",
    "UNRELATED_OS_JOB",
    "UNKNOWN_PROJECT_BINDING",
}


def _validate_job_row(row: Mapping[str, Any], *, observed: bool = False) -> None:
    if not isinstance(row, Mapping):
        raise ContractError("JOB_IDENTITY_INVALID")
    forbidden = {"command", "raw_command", "raw_schedule", "schedule"}
    if forbidden.intersection(row):
        raise ContractError("JOB_RAW_COMMAND_FORBIDDEN")
    required = {"provider", "job_id", "command_hash", "schedule_hash"}
    allowed = required | ({"relevance"} if observed else set())
    if not required.issubset(row) or not set(row).issubset(allowed):
        missing = sorted(required - set(row))
        raise ContractError(f"JOB_IDENTITY_INCOMPLETE:{missing[0] if missing else 'extra'}")
    provider = row["provider"]
    if not isinstance(provider, str) or not (
        provider in {"codex", "windows-task-scheduler"}
        or re.fullmatch(r"platform:[A-Za-z0-9._-]{1,64}", provider)
    ):
        raise ContractError("JOB_PROVIDER_INVALID")
    if not isinstance(row["job_id"], str) or not re.fullmatch(r"[A-Za-z0-9._:/-]{1,128}", row["job_id"]):
        raise ContractError("JOB_ID_INVALID")
    _require_sha256(row["command_hash"], "JOB_COMMAND_HASH_INVALID")
    _require_sha256(row["schedule_hash"], "JOB_SCHEDULE_HASH_INVALID")
    if observed and row.get("relevance", "UNKNOWN_RELEVANCE") not in JOB_RELEVANCE:
        raise ContractError("JOB_RELEVANCE_INVALID")


def _job_index(
    rows: Sequence[Mapping[str, Any]], *, observed: bool = False
) -> dict[tuple[str, str], tuple[str, str, str]]:
    result: dict[tuple[str, str], tuple[str, str, str]] = {}
    for row in rows:
        _validate_job_row(row, observed=observed)
        key = (row["provider"], row["job_id"])
        if key in result:
            raise ContractError("JOB_ID_DUPLICATE")
        result[key] = (
            row["command_hash"],
            row["schedule_hash"],
            row.get("relevance", "UNKNOWN_RELEVANCE") if observed else "APPROVED",
        )
    return result


def compare_scheduled_jobs(
    approved_manifest: Mapping[str, Any],
    observed_jobs: Sequence[Mapping[str, Any]],
    provider_status: Mapping[str, str],
    *,
    project_profile_id: str | None = None,
) -> dict[str, Any]:
    if approved_manifest.get("schema") != "x9-loop-approved-jobs-v1":
        raise ContractError("APPROVED_JOBS_SCHEMA_INVALID")
    monitor_mode = approved_manifest.get("monitor_mode", "DISABLED")
    if monitor_mode not in {"DISABLED", "EXTERNAL"}:
        raise ContractError("MONITOR_MODE_INVALID")
    approved_rows = approved_manifest.get("jobs")
    if not isinstance(approved_rows, list) or not isinstance(observed_jobs, Sequence):
        raise ContractError("APPROVED_JOBS_INVALID")
    if not isinstance(provider_status, Mapping):
        raise ContractError("JOB_PROVIDER_STATUS_INVALID")
    if monitor_mode == "DISABLED":
        if approved_rows:
            raise ContractError("DISABLED_MONITOR_HAS_APPROVALS")
        allowed_keys = {"jobs", "monitor_mode", "schema"}
    else:
        allowed_keys = {"jobs", "monitor_mode", "project_profile_id", "schema"}
        bound_profile = approved_manifest.get("project_profile_id")
        if (
            not isinstance(bound_profile, str)
            or re.fullmatch(r"[A-Za-z0-9._:-]{16,128}", bound_profile) is None
            or not approved_rows
            or (project_profile_id is not None and bound_profile != project_profile_id)
        ):
            raise ContractError("EXTERNAL_MONITOR_PROJECT_BINDING_INVALID")
    if not set(approved_manifest).issubset(allowed_keys):
        raise ContractError("APPROVED_JOBS_INVALID")
    approved = _job_index(copy.deepcopy(approved_rows))
    observed = _job_index(copy.deepcopy(list(observed_jobs)), observed=True)
    required_providers = {key[0] for key in approved} if monitor_mode == "EXTERNAL" else set()
    unavailable = sorted(
        provider
        for provider in required_providers
        if provider_status.get(provider) != "AVAILABLE"
    )
    findings = []
    blockers = []
    for key, actual in observed.items():
        provider, job_id = key
        redacted = {
            "job_id_sha256": sha256_bytes(job_id.encode("utf-8"))[:16],
            "provider": provider,
        }
        relevance = "CURRENT_PROJECT_MONITOR" if key in approved else actual[2]
        statuses: list[str] = []
        if relevance in {"OTHER_PROJECT_JOB", "UNRELATED_OS_JOB"}:
            statuses = [relevance]
        elif relevance == "UNKNOWN_PROJECT_BINDING":
            statuses = ["UNKNOWN_PROJECT_BINDING"]
        elif key not in approved:
            statuses = ["NEW_JOB"]
        else:
            expected = approved[key]
            if expected[0] != actual[0]:
                statuses.append("COMMAND_DRIFT")
            if expected[1] != actual[1]:
                statuses.append("SCHEDULE_DRIFT")
        for status in statuses:
            finding = {**redacted, "status": status}
            findings.append(finding)
            if monitor_mode == "EXTERNAL" and status not in {
                "OTHER_PROJECT_JOB", "UNRELATED_OS_JOB"
            }:
                blockers.append(finding)
    if monitor_mode == "EXTERNAL":
        for key in sorted(set(approved) - set(observed)):
            provider, job_id = key
            finding = {
                "job_id_sha256": sha256_bytes(job_id.encode("utf-8"))[:16],
                "provider": provider,
                "status": "APPROVED_JOB_MISSING",
            }
            findings.append(finding)
            blockers.append(finding)
    ordering = lambda row: (row["provider"], row["job_id_sha256"], row["status"])
    external_ready = None if monitor_mode == "DISABLED" else not blockers and not unavailable
    return {
        "activation_allowed": True,
        "core_loop_ready": True,
        "external_wake_ready": external_ready,
        "job_findings": sorted(findings, key=ordering),
        "monitor_mode": monitor_mode,
        "unauthorized_jobs": sorted(blockers, key=ordering),
        "unrelated_jobs": sorted(
            (
                row
                for row in findings
                if row["status"] in {"OTHER_PROJECT_JOB", "UNRELATED_OS_JOB"}
            ),
            key=ordering,
        ),
        "unavailable_providers": unavailable,
    }

def build_worker_checkpoint(
    *,
    attempt: int,
    proof_refs: Sequence[str],
    state: str,
    worker_id: str,
    work_order_id: str,
    work_order_sha256: str,
) -> tuple[dict[str, Any], bytes, str]:
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 0:
        raise ContractError("CHECKPOINT_ATTEMPT_INVALID")
    if not isinstance(proof_refs, (list, tuple)) or any(
        not isinstance(item, str) or not item for item in proof_refs
    ):
        raise ContractError("CHECKPOINT_PROOF_REFS_INVALID")
    for name, value in (("state", state), ("worker_id", worker_id), ("work_order_id", work_order_id)):
        if not isinstance(value, str) or not value.strip():
            raise ContractError(f"CHECKPOINT_FIELD_INVALID:{name}")
    _require_sha256(work_order_sha256, "CHECKPOINT_WORK_ORDER_HASH_INVALID")
    checkpoint = {
        "attempt": attempt,
        "authoritative": False,
        "expires_with_work_order": True,
        "local_only": True,
        "proof_refs": list(proof_refs),
        "schema": "x9-loop-worker-checkpoint-v1",
        "state": state,
        "work_order_id": work_order_id,
        "work_order_sha256": work_order_sha256,
        "worker_id": worker_id,
    }
    raw = canonical_json_bytes(checkpoint)
    validate_packet_cap("WORKER_CHECKPOINT.json", raw)
    return checkpoint, raw, sha256_bytes(raw)


def validate_worker_checkpoint(
    raw: bytes,
    expected_sha256: str,
    work_order_id: str,
    work_order_sha256: str,
    worker_id: str,
    work_order_active: bool,
) -> dict[str, Any]:
    _require_sha256(expected_sha256, "CHECKPOINT_HASH_INVALID")
    _require_sha256(work_order_sha256, "CHECKPOINT_WORK_ORDER_HASH_INVALID")
    if not isinstance(worker_id, str) or not worker_id.strip():
        raise ContractError("CHECKPOINT_WORKER_INVALID")
    if not isinstance(work_order_active, bool):
        raise ContractError("CHECKPOINT_ACTIVE_STATE_INVALID")
    validate_packet_cap("WORKER_CHECKPOINT.json", raw)
    if not isinstance(raw, bytes) or sha256_bytes(raw) != expected_sha256:
        raise ContractError("CHECKPOINT_TAMPERED")
    try:
        checkpoint = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("CHECKPOINT_TAMPERED") from exc
    if not isinstance(checkpoint, dict) or canonical_json_bytes(checkpoint) != raw:
        raise ContractError("CHECKPOINT_TAMPERED")
    required = {
        "attempt", "authoritative", "expires_with_work_order", "local_only", "proof_refs",
        "schema", "state", "work_order_id", "work_order_sha256", "worker_id",
    }
    if set(checkpoint) != required or checkpoint["schema"] != "x9-loop-worker-checkpoint-v1":
        raise ContractError("CHECKPOINT_SCHEMA_INVALID")
    if not work_order_active:
        raise ContractError("CHECKPOINT_EXPIRED")
    if (
        checkpoint["authoritative"] is not False
        or checkpoint["local_only"] is not True
        or checkpoint["expires_with_work_order"] is not True
    ):
        raise ContractError("CHECKPOINT_AUTHORITY_INVALID")
    if checkpoint["work_order_id"] != work_order_id:
        raise ContractError("CHECKPOINT_WORK_ORDER_MISMATCH")
    if checkpoint["work_order_sha256"] != work_order_sha256:
        raise ContractError("CHECKPOINT_WORK_ORDER_HASH_MISMATCH")
    if checkpoint["worker_id"] != worker_id:
        raise ContractError("CHECKPOINT_WORKER_MISMATCH")
    if (
        isinstance(checkpoint["attempt"], bool)
        or not isinstance(checkpoint["attempt"], int)
        or checkpoint["attempt"] < 0
        or not isinstance(checkpoint["state"], str)
        or not checkpoint["state"].strip()
        or not isinstance(checkpoint["proof_refs"], list)
        or any(not isinstance(item, str) or not item for item in checkpoint["proof_refs"])
    ):
        raise ContractError("CHECKPOINT_FIELDS_INVALID")
    return checkpoint

def validate_change_map(change_map: Mapping[str, Any]) -> None:
    required = {
        "changed_surface", "proof_refs", "reason", "remaining_risk", "rollback",
    }
    if not isinstance(change_map, Mapping) or set(change_map) != required:
        missing = sorted(required - set(change_map)) if isinstance(change_map, Mapping) else []
        raise ContractError(
            f"RESULT_CHANGE_MAP_INCOMPLETE:{missing[0] if missing else 'fields'}"
        )
    if (
        not isinstance(change_map["changed_surface"], list)
        or any(
            not isinstance(item, str) or canonical_repo_path(item) != item
            for item in change_map["changed_surface"]
        )
        or len(change_map["changed_surface"])
        != len(set(change_map["changed_surface"]))
    ):
        raise ContractError("RESULT_CHANGE_MAP_INVALID:changed_surface")
    if (
        not isinstance(change_map["proof_refs"], list)
        or any(
            not isinstance(item, str) or canonical_repo_path(item) != item
            for item in change_map["proof_refs"]
        )
        or len(change_map["proof_refs"]) != len(set(change_map["proof_refs"]))
    ):
        raise ContractError("RESULT_CHANGE_MAP_INVALID:proof_refs")
    for field in ("reason", "remaining_risk", "rollback"):
        if not isinstance(change_map[field], str) or not change_map[field].strip():
            raise ContractError(f"RESULT_CHANGE_MAP_INVALID:{field}")
    raw = canonical_json_bytes(dict(change_map))
    if len(raw) > 8 * 1024:
        raise ContractError("RESULT_CHANGE_MAP_TOO_LARGE")


def validate_worker_result(
    result: Mapping[str, Any],
    expected: Mapping[str, str],
    *,
    require_proof_bound_approaches: bool = False,
) -> tuple[dict[str, Any], str]:
    required = {
        "attestation_path", "blocker", "budget_remaining", "c1", "c2",
        "change_map", "changed_files", "dispatch_id", "event_id",
        "failed_verified_approaches", "outcome", "packet_sha256", "proof",
        "role", "schema", "task_id", "work_order_id", "work_order_sha256",
        "worker_id",
    }
    expected_fields = {
        "dispatch_id", "event_id", "packet_sha256", "task_id",
        "work_order_id", "work_order_sha256", "worker_id",
    }
    if (
        not isinstance(result, Mapping)
        or not required.issubset(result)
        or set(result) - required - {"approach_receipts", "autonomy_proxy"}
        or not isinstance(expected, Mapping)
        or set(expected) != expected_fields
    ):
        raise ContractError("RESULT_FIELDS_INVALID")
    approaches: list[dict[str, Any]] | None = None
    if "approach_receipts" in result:
        approaches = validate_approach_receipts(result["approach_receipts"])
        if len(approaches) != len(result["approach_receipts"]):
            raise ContractError("APPROACH_RECEIPT_DUPLICATE")
    if "autonomy_proxy" in result:
        proxy = validate_autonomy_proxy(result["autonomy_proxy"])
        if approaches is not None and proxy["distinct_failed_approaches"] != len(approaches):
            raise ContractError("AUTONOMY_PROXY_APPROACH_MISMATCH")
    elif approaches is not None:
        raise ContractError("AUTONOMY_PROXY_REQUIRED")
    if require_proof_bound_approaches and result["outcome"] == "VERIFIED_FAILURE" and approaches is None:
        raise ContractError("APPROACH_RECEIPTS_REQUIRED")
    if result["schema"] != "x9-loop-result-v2" or result["role"] != "WORKER":
        raise ContractError("RESULT_SCHEMA_INVALID")
    for field in expected_fields:
        if result[field] != expected[field]:
            raise ContractError(f"RESULT_IDENTITY_MISMATCH:{field}")
    _require_sha256(result["packet_sha256"], "RESULT_HASH_INVALID")
    _require_sha256(result["work_order_sha256"], "RESULT_HASH_INVALID")
    changed = result["changed_files"]
    if (
        not isinstance(changed, list)
        or any(not isinstance(item, str) or canonical_repo_path(item) != item for item in changed)
        or len(changed) != len(set(changed))
    ):
        raise ContractError("RESULT_CHANGED_FILES_INVALID")
    proof = result["proof"]
    if not isinstance(proof, list):
        raise ContractError("RESULT_PROOF_INVALID")
    proof_paths: list[str] = []
    proof_kinds: set[str] = set()
    for item in proof:
        if (
            not isinstance(item, Mapping)
            or set(item) != {"kind", "path", "sha256"}
            or item["kind"] not in {"security", "tests"}
            or item["kind"] in proof_kinds
        ):
            raise ContractError("RESULT_PROOF_INVALID")
        proof_kinds.add(item["kind"])
        proof_paths.append(canonical_repo_path(item["path"]))
        _require_sha256(item["sha256"], "RESULT_PROOF_INVALID")
    _canonical_paths_unique(proof_paths)
    validate_change_map(result["change_map"])
    if result["change_map"]["changed_surface"] != changed:
        raise ContractError("RESULT_CHANGE_MAP_MISMATCH")
    if result["change_map"]["proof_refs"] != proof_paths:
        raise ContractError("RESULT_CHANGE_MAP_MISMATCH")
    disposition = map_worker_event(
        result["outcome"],
        failed_verified_approaches=result["failed_verified_approaches"],
        budget_remaining=result["budget_remaining"],
        approach_receipts=(
            approaches if require_proof_bound_approaches else None
        ),
    )
    if disposition is None:
        raise ContractError("WORKER_LOCAL_CHECKPOINT_REQUIRED")
    if result["outcome"] == "SUCCESS":
        if proof_kinds != {"security", "tests"} or result["blocker"] is not None:
            raise ContractError("RESULT_PROOF_INVALID")
        if changed:
            _require_git_sha(result["c1"], "RESULT_COMMIT_INVALID")
            _require_git_sha(result["c2"], "RESULT_COMMIT_INVALID")
            canonical_repo_path(result["attestation_path"])
        elif any(
            result[field] is not None
            for field in ("attestation_path", "c1", "c2")
        ):
            raise ContractError("RESULT_COMMIT_INVALID")
    elif result["outcome"] == "SUCCESS_CANDIDATE":
        if (
            not changed
            or proof_kinds != {"security", "tests"}
            or result["blocker"] is not None
            or any(
                result[field] is not None
                for field in ("attestation_path", "c1", "c2")
            )
        ):
            raise ContractError("RESULT_CANDIDATE_INVALID")
    else:
        if (
            any(
                result[field] is not None
                for field in ("attestation_path", "c1", "c2")
            )
            or not isinstance(result["blocker"], str)
            or not result["blocker"].strip()
        ):
            raise ContractError("RESULT_BLOCKER_INVALID")
    return copy.deepcopy(dict(result)), disposition

def validate_thinx_decision(
    result: Mapping[str, Any],
    expected: Mapping[str, str],
) -> dict[str, Any]:
    required = {
        "actor_id",
        "decision",
        "dispatch_id",
        "event_id",
        "packet_sha256",
        "reason",
        "role",
        "schema",
        "task_id",
        "worker_event_id",
        "worker_result_sha256",
        "work_order_id",
        "work_order_sha256",
    }
    expected_fields = required - {"decision", "reason", "role", "schema"}
    if (
        not isinstance(result, Mapping)
        or set(result) != required
        or not isinstance(expected, Mapping)
        or set(expected) != expected_fields
    ):
        raise ContractError("THINX_DECISION_FIELDS_INVALID")
    if (
        result["schema"] != "x9-loop-thinx-decision-v2"
        or result["role"] != "THINX"
        or result["decision"] not in {"PASS", "BLOCKED", "FAIL"}
        or not isinstance(result["reason"], str)
        or not result["reason"].strip()
    ):
        raise ContractError("THINX_DECISION_INVALID")
    for field in expected_fields:
        if result[field] != expected[field]:
            raise ContractError(
                f"THINX_DECISION_IDENTITY_MISMATCH:{field}"
            )
    for field in (
        "packet_sha256",
        "worker_result_sha256",
        "work_order_sha256",
    ):
        _require_sha256(result[field], "THINX_DECISION_HASH_INVALID")
    validate_packet_cap(
        "THINX_DECISION.json",
        canonical_json_bytes(dict(result)),
    )
    return copy.deepcopy(dict(result))
