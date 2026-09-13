#!/usr/bin/env python3
"""Classify a proposed Style-mode escalation without starting a runtime loop."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any, Mapping


SCHEMA = "x9-style-autonomy-admission-v1"
RECEIPT_SCHEMA = "x9-style-receipt-admission-v1"
WAIT_SCHEMA = "x9-style-pre-wait-admission-v3"
DISPATCH_SCHEMA = "x9-style-lane-dispatch-v1"
REQUIRED = {
    "architecture_security_boundary",
    "distinct_failed_approaches",
    "judgment_needed",
    "owner_boundary",
    "same_root_cause_cycles",
    "schema",
    "single_route_failed",
    "stable_material_diff",
    "subagent_available",
}
RECEIPT_REQUIRED = {
    "already_consumed",
    "expected_event",
    "expected_receipt_sha256",
    "expired",
    "receipt_present",
    "received_event",
    "received_receipt_sha256",
    "schema",
}
DISPATCH_REQUIRED = {
    "lane_mode",
    "local_continuation_reserve_path",
    "local_continuation_reserve_sha256",
    "packet_sha256",
    "ready_chunk_count",
    "resume_event",
    "schema",
}
WAIT_REQUIRED = {
    "authorized_candidate_count",
    "authorized_candidates",
    "authorized_candidates_sha256",
    "backlog_localization_done",
    "blocked_chunk",
    "dependency_event",
    "eligible_candidate_count",
    "eligible_candidates",
    "eligible_candidates_sha256",
    "expected_packet_sha256",
    "expansion_proposal_path",
    "expansion_proposal_sha256",
    "inspected_candidate_count",
    "inspected_candidates",
    "inspected_candidates_sha256",
    "localization_authorized_candidates_sha256",
    "localization_outcome",
    "localization_packet_sha256",
    "localization_receipt_path",
    "localization_receipt_sha256",
    "no_authorized_local_slice",
    "observed_packet_sha256",
    "packet_path",
    "schema",
    "selected_action",
    "selected_chunk_id",
}
WAIT_RESERVE_EXTENSION = {
    "expansion_within_reserve",
    "local_continuation_reserve_path",
    "local_continuation_reserve_sha256",
    "no_external_effect",
    "no_shared_resource",
    "self_admit_local_expansion",
}
WAIT_ALLOWED = WAIT_REQUIRED | WAIT_RESERVE_EXTENSION
CANDIDATE_STATES = {"READY", "COMPLETE", "WAITING_RECEIPT"}
CANDIDATE_REQUIRED = {"action", "candidate_state", "chunk_id", "record_sha256"}
INSPECTED_CANDIDATE_REQUIRED = CANDIDATE_REQUIRED | {"eligibility"}
LOCALIZATION_OUTCOMES = {"NONE_FOUND", "NOT_RUN", "PROPOSAL_CREATED"}
LANE_MODES = {"ACTIVE", "EVENT_ONLY"}


def classify(value: Any) -> dict[str, Any]:
    """Fail open to local work: malformed admissions never create a block."""
    invalid = (
        not isinstance(value, Mapping)
        or set(value) != REQUIRED
        or value.get("schema") != SCHEMA
        or any(
            not isinstance(value.get(key), bool)
            for key in REQUIRED
            - {"schema", "distinct_failed_approaches", "same_root_cause_cycles"}
        )
        or isinstance(value.get("distinct_failed_approaches"), bool)
        or not isinstance(value.get("distinct_failed_approaches"), int)
        or value.get("distinct_failed_approaches", 0) < 0
        or isinstance(value.get("same_root_cause_cycles"), bool)
        or not isinstance(value.get("same_root_cause_cycles"), int)
        or value.get("same_root_cause_cycles", 0) < 0
    )
    if invalid:
        return _result("CONTINUE_LOCAL", "MISSING_OR_INVALID_ADMISSION")
    if value["owner_boundary"]:
        return _result("OWNER_REQUIRED", "OWNER_BOUNDARY")
    if value["stable_material_diff"] or value["architecture_security_boundary"]:
        return _result("THINKER_ALLOWED", "STABLE_REVIEW_OR_HARD_BOUNDARY")
    if value["same_root_cause_cycles"]:
        return _result("LOCAL_FALLBACK", "SAME_ROOT_CAUSE_STAYS_LOCAL")
    if value["distinct_failed_approaches"] >= 2 and value["judgment_needed"]:
        return _result("THINKER_ALLOWED", "TWO_DISTINCT_FAILURES_NEED_JUDGMENT")
    if value["single_route_failed"]:
        return _result(
            "SUBAGENT_ONCE" if value["subagent_available"] else "LOCAL_FALLBACK",
            "ONE_ROUTE_FAILED",
        )
    return _result("CONTINUE_LOCAL", "ROUTINE_OR_KNOWN_NEXT_ACTION")


def _result(classification: str, reason: str) -> dict[str, Any]:
    outbound_allowed = classification in {"THINKER_ALLOWED", "OWNER_REQUIRED"}
    next_actions = {
        "CONTINUE_LOCAL": "continue the safe local action; do not send an outbound question",
        "LOCAL_FALLBACK": "try one materially different safe local route",
        "SUBAGENT_ONCE": "use at most one bounded same-authority advisory helper",
        "THINKER_ALLOWED": "request one review bound to the current stable evidence",
        "OWNER_REQUIRED": "request only the owner-bound decision and continue disjoint safe work",
    }
    return {
        "schema": SCHEMA,
        "classification": classification,
        "reason": reason,
        "outbound_question_allowed": outbound_allowed,
        "next_action": next_actions[classification],
    }


def classify_dispatch(value: Any) -> dict[str, Any]:
    """Reject an empty active lane before it strands a Worker.

    This is a stateless packet-shape check.  It does not create a task, reserve
    a resource, or wake a host thread; callers still bind the ready chunk or
    local-continuation reserve to the current authority envelope.
    """
    if (
        not isinstance(value, Mapping)
        or set(value) != DISPATCH_REQUIRED
        or value.get("schema") != DISPATCH_SCHEMA
        or value.get("lane_mode") not in LANE_MODES
        or not _is_sha256(value.get("packet_sha256"))
        or isinstance(value.get("ready_chunk_count"), bool)
        or not isinstance(value.get("ready_chunk_count"), int)
        or value.get("ready_chunk_count", -1) < 0
        or not _optional_path_hash_pair(
            value.get("local_continuation_reserve_path"),
            value.get("local_continuation_reserve_sha256"),
        )
        or not _optional_nonempty_string(value.get("resume_event"))
    ):
        return _dispatch_result("DISPATCH_REPAIR_REQUIRED", "INVALID_DISPATCH_ADMISSION")

    has_local_work = bool(value["ready_chunk_count"]) or (
        value["local_continuation_reserve_path"] is not None
    )
    if value["lane_mode"] == "ACTIVE":
        if has_local_work:
            return _dispatch_result("ACTIVE_READY", "LOCAL_WORK_BOUND")
        return _dispatch_result("EVENT_ONLY_REQUIRED", "NO_LOCAL_WORK_BOUND")
    if has_local_work or value["resume_event"] is None:
        return _dispatch_result("DISPATCH_REPAIR_REQUIRED", "INVALID_EVENT_ONLY_ADMISSION")
    return _dispatch_result("EVENT_ONLY", "EXTERNAL_RECEIPT_ONLY")


def _dispatch_result(state: str, reason: str) -> dict[str, Any]:
    return {
        "schema": DISPATCH_SCHEMA,
        "state": state,
        "reason": reason,
        "should_start": state == "ACTIVE_READY",
    }


def classify_receipt(value: Any) -> dict[str, Any]:
    """Classify one receipt without storing state, waking a task, or retrying work.

    A missing receipt requires a valid pre-wait sweep before a lane may wait.
    A stale, mismatched, or duplicate receipt is deliberately a zero-delta
    transport result rather than a reason to recreate work or ask for approval.
    """
    invalid = (
        not isinstance(value, Mapping)
        or set(value) != RECEIPT_REQUIRED
        or value.get("schema") != RECEIPT_SCHEMA
        or any(
            not isinstance(value.get(key), bool)
            for key in {"already_consumed", "expired", "receipt_present"}
        )
        or not isinstance(value.get("expected_event"), str)
        or not value.get("expected_event")
        or not _is_sha256(value.get("expected_receipt_sha256"))
        or (
            value.get("received_event") is not None
            and not isinstance(value.get("received_event"), str)
        )
        or (
            value.get("received_receipt_sha256") is not None
            and not _is_sha256(value.get("received_receipt_sha256"))
        )
    )
    if invalid or not value.get("receipt_present"):
        return _receipt_result("CONTINUE_LOCAL", "PRE_WAIT_REQUIRED_FOR_MISSING_RECEIPT")
    if value["received_event"] != value["expected_event"]:
        return _receipt_result("ZERO_DELTA", "EVENT_MISMATCH")
    if (
        value["received_receipt_sha256"].casefold()
        != value["expected_receipt_sha256"].casefold()
    ):
        return _receipt_result("ZERO_DELTA", "RECEIPT_HASH_MISMATCH")
    if value["expired"]:
        return _receipt_result("ZERO_DELTA", "RECEIPT_EXPIRED")
    if value["already_consumed"]:
        return _receipt_result("ZERO_DELTA", "DUPLICATE_RECEIPT")
    return _receipt_result("RESUME_READY", "MATCHING_FRESH_RECEIPT")


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def _receipt_result(state: str, reason: str) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "state": state,
        "reason": reason,
        "should_resume": state == "RESUME_READY",
    }


def classify_wait(value: Any) -> dict[str, Any]:
    """Admit a lane wait only after its whole current envelope is inspected.

    The caller supplies expected and observed packet/candidate-inventory
    identities. A packet-bound READY chunk can start locally without Looper
    approval; ordinary backlog prose is never execution authority. With no
    eligible authorized chunk, one read-only backlog localization is required
    before a lane may wait. This classifier stores no state and cannot create
    tasks, claims, schedules, or scope decisions.
    """
    if (
        not isinstance(value, Mapping)
        or not WAIT_REQUIRED.issubset(value)
        or not set(value).issubset(WAIT_ALLOWED)
        or value.get("schema") != WAIT_SCHEMA
        or any(
            not isinstance(value.get(key), bool)
            for key in {
                "backlog_localization_done",
                "no_authorized_local_slice",
            }
        )
        or any(
            key in value and not isinstance(value.get(key), bool)
            for key in {
                "expansion_within_reserve",
                "no_external_effect",
                "no_shared_resource",
                "self_admit_local_expansion",
            }
        )
        or any(
            not isinstance(value.get(key), str) or not value.get(key)
            for key in {"dependency_event", "blocked_chunk", "packet_path"}
        )
        or any(
            not _is_sha256(value.get(key))
            for key in {
                "expected_packet_sha256",
                "observed_packet_sha256",
                "authorized_candidates_sha256",
                "inspected_candidates_sha256",
                "eligible_candidates_sha256",
            }
        )
        or any(
            isinstance(value.get(key), bool)
            or not isinstance(value.get(key), int)
            or value.get(key, -1) < 0
            for key in {
                "authorized_candidate_count",
                "inspected_candidate_count",
                "eligible_candidate_count",
            }
        )
        or not _candidate_inventory_valid(value.get("authorized_candidates"))
        or not _inspected_inventory_valid(value.get("inspected_candidates"))
        or not _candidate_inventory_valid(value.get("eligible_candidates"))
        or not _optional_nonempty_pair(
            value.get("selected_chunk_id"), value.get("selected_action")
        )
        or not _optional_path_hash_pair(
            value.get("expansion_proposal_path"),
            value.get("expansion_proposal_sha256"),
        )
        or not _optional_path_hash_pair(
            value.get("local_continuation_reserve_path"),
            value.get("local_continuation_reserve_sha256"),
        )
        or not isinstance(value.get("localization_outcome"), str)
        or value.get("localization_outcome") not in LOCALIZATION_OUTCOMES
    ):
        return _wait_result("CONTINUE_LOCAL", "PRE_WAIT_ADMISSION_INVALID")
    if (
        value["expected_packet_sha256"].casefold()
        != value["observed_packet_sha256"].casefold()
    ):
        return _wait_result("CONTINUE_LOCAL", "PACKET_IDENTITY_MISMATCH")
    authorized = value["authorized_candidates"]
    inspected = value["inspected_candidates"]
    eligible = value["eligible_candidates"]
    if (
        value["authorized_candidate_count"] != len(authorized)
        or value["inspected_candidate_count"] != len(inspected)
        or value["eligible_candidate_count"] != len(eligible)
        or value["authorized_candidates_sha256"].casefold()
        != _inventory_sha256(authorized)
        or value["inspected_candidates_sha256"].casefold()
        != _inventory_sha256(inspected)
        or value["eligible_candidates_sha256"].casefold()
        != _inventory_sha256(eligible)
    ):
        return _wait_result("CONTINUE_LOCAL", "CANDIDATE_INVENTORY_HASH_INVALID")
    authorized_identities = {_candidate_identity(record) for record in authorized}
    inspected_identities = {
        _candidate_identity(record) for record in inspected
    }
    if authorized_identities != inspected_identities:
        return _wait_result("CONTINUE_LOCAL", "CANDIDATE_INVENTORY_INCOMPLETE")
    marked_eligible = {
        _candidate_identity(record)
        for record in inspected
        if record["eligibility"] == "ELIGIBLE"
    }
    eligible_identities = {_candidate_identity(record) for record in eligible}
    if (
        eligible_identities != marked_eligible
        or any(record["candidate_state"] != "READY" for record in eligible)
    ):
        return _wait_result("CONTINUE_LOCAL", "ELIGIBLE_INVENTORY_MISMATCH")
    if eligible:
        selected = [
            record
            for record in eligible
            if record["chunk_id"] == value["selected_chunk_id"]
            and record["action"] == value["selected_action"]
        ]
        if len(selected) != 1 or value["no_authorized_local_slice"]:
            return _wait_result("CONTINUE_LOCAL", "SELECTED_ACTION_NOT_ELIGIBLE")
        return _wait_result("CONTINUE_LOCAL", "AUTHORIZED_LOCAL_ACTION_EXISTS")
    if value["selected_chunk_id"] is not None or value["selected_action"] is not None:
        return _wait_result("CONTINUE_LOCAL", "SELECTED_ACTION_NOT_ELIGIBLE")
    if not value["no_authorized_local_slice"]:
        return _wait_result("CONTINUE_LOCAL", "NO_LOCAL_SLICE_NOT_PROVEN")
    if not value["backlog_localization_done"]:
        if (
            value["localization_outcome"] != "NOT_RUN"
            or any(
                value.get(key) is not None
                for key in {
                    "localization_authorized_candidates_sha256",
                    "localization_packet_sha256",
                    "localization_receipt_path",
                    "localization_receipt_sha256",
                    "expansion_proposal_path",
                    "expansion_proposal_sha256",
                }
            )
        ):
            return _wait_result("CONTINUE_LOCAL", "LOCALIZATION_ADMISSION_INVALID")
        return _wait_result(
            "BACKLOG_LOCALIZATION_REQUIRED", "AUTHORIZED_BACKLOG_NOT_LOCALIZED"
        )
    if (
        value["localization_outcome"] == "NOT_RUN"
        or not _localization_receipt_valid(value)
    ):
        return _wait_result("CONTINUE_LOCAL", "LOCALIZATION_ADMISSION_INVALID")
    if (
        value["localization_packet_sha256"].casefold()
        != value["expected_packet_sha256"].casefold()
    ):
        return _wait_result("CONTINUE_LOCAL", "LOCALIZATION_PACKET_MISMATCH")
    if (
        value["localization_authorized_candidates_sha256"].casefold()
        != value["authorized_candidates_sha256"].casefold()
    ):
        return _wait_result("CONTINUE_LOCAL", "LOCALIZATION_CANDIDATE_MISMATCH")
    if value["expansion_proposal_path"] is not None:
        if (
            value["localization_outcome"] != "PROPOSAL_CREATED"
            or value["expansion_proposal_path"]
            != value["localization_receipt_path"]
            or value["expansion_proposal_sha256"].casefold()
            != value["localization_receipt_sha256"].casefold()
        ):
            return _wait_result("CONTINUE_LOCAL", "EXPANSION_EVENT_REQUIRED")
        if value.get("self_admit_local_expansion", False):
            if (
                value.get("local_continuation_reserve_path") is None
                or not value.get("expansion_within_reserve", False)
                or not value.get("no_shared_resource", False)
                or not value.get("no_external_effect", False)
            ):
                return _wait_result(
                    "CONTINUE_LOCAL", "LOCAL_CONTINUATION_ADMISSION_INVALID"
                )
            return _wait_result("CONTINUE_LOCAL", "LOCAL_CONTINUATION_READY")
        if (
            value.get("local_continuation_reserve_path") is not None
            or value.get("expansion_within_reserve", False)
            or value.get("no_shared_resource", False)
            or value.get("no_external_effect", False)
            or value["dependency_event"] != "CLAIM_EXPANSION_RECEIPT"
        ):
            return _wait_result("CONTINUE_LOCAL", "EXPANSION_EVENT_REQUIRED")
        return _wait_result("DEPENDENCY_WAIT", "CLAIM_EXPANSION_RECEIPT_REQUIRED")
    if (
        value.get("self_admit_local_expansion", False)
        or value.get("local_continuation_reserve_path") is not None
        or value.get("expansion_within_reserve", False)
        or value.get("no_shared_resource", False)
        or value.get("no_external_effect", False)
    ):
        return _wait_result("CONTINUE_LOCAL", "LOCAL_CONTINUATION_ADMISSION_INVALID")
    if value["localization_outcome"] != "NONE_FOUND":
        return _wait_result("CONTINUE_LOCAL", "LOCALIZATION_OUTCOME_INVALID")
    return _wait_result("DEPENDENCY_WAIT", "NO_AUTHORIZED_LOCAL_SLICE")


def _optional_nonempty_pair(left: Any, right: Any) -> bool:
    return (left is None and right is None) or (
        isinstance(left, str)
        and bool(left)
        and isinstance(right, str)
        and bool(right)
    )


def _optional_path_hash_pair(path: Any, digest: Any) -> bool:
    return (path is None and digest is None) or (
        isinstance(path, str) and bool(path) and _is_sha256(digest)
    )


def _optional_nonempty_string(value: Any) -> bool:
    return value is None or (isinstance(value, str) and bool(value))


def _candidate_inventory_valid(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(record, Mapping)
            and set(record) == CANDIDATE_REQUIRED
            and isinstance(record.get("chunk_id"), str)
            and bool(record["chunk_id"])
            and isinstance(record.get("action"), str)
            and bool(record["action"])
            and _is_sha256(record.get("record_sha256"))
            and record.get("candidate_state") in CANDIDATE_STATES
            for record in value
        )
        and len({record["chunk_id"] for record in value}) == len(value)
    )


def _inspected_inventory_valid(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(record, Mapping)
            and set(record) == INSPECTED_CANDIDATE_REQUIRED
            and isinstance(record.get("chunk_id"), str)
            and bool(record["chunk_id"])
            and isinstance(record.get("action"), str)
            and bool(record["action"])
            and _is_sha256(record.get("record_sha256"))
            and record.get("candidate_state") in CANDIDATE_STATES
            and record.get("eligibility") in {"ELIGIBLE", "INELIGIBLE"}
            for record in value
        )
        and len({record["chunk_id"] for record in value}) == len(value)
    )


def _candidate_identity(record: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        record["chunk_id"],
        record["action"],
        record["record_sha256"].casefold(),
        record["candidate_state"],
    )


def _inventory_sha256(records: list[Mapping[str, Any]]) -> str:
    canonical = sorted(
        records,
        key=lambda record: (
            record["chunk_id"],
            record["action"],
            record["record_sha256"].casefold(),
            record["candidate_state"],
            record.get("eligibility", ""),
        ),
    )
    payload = json.dumps(
        canonical, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _localization_receipt_valid(value: Mapping[str, Any]) -> bool:
    return (
        isinstance(value.get("localization_receipt_path"), str)
        and bool(value["localization_receipt_path"])
        and _is_sha256(value.get("localization_receipt_sha256"))
        and _is_sha256(value.get("localization_packet_sha256"))
        and _is_sha256(value.get("localization_authorized_candidates_sha256"))
    )


def _wait_result(state: str, reason: str) -> dict[str, Any]:
    next_actions = {
        "CONTINUE_LOCAL": (
            "reconcile the current packet sweep or begin the selected safe "
            "authorized local chunk; do not wait"
        ),
        "BACKLOG_LOCALIZATION_REQUIRED": (
            "perform one read-only localization of the current packet-bound "
            "backlog; do not code an unbound chunk or ask for approval"
        ),
        "DEPENDENCY_WAIT": (
            "pause only the declared chunk until its named receipt arrives; "
            "do not poll or terminate the whole goal"
        ),
    }
    return {
        "schema": WAIT_SCHEMA,
        "state": state,
        "reason": reason,
        "should_wait": state == "DEPENDENCY_WAIT",
        "should_subscribe": state == "DEPENDENCY_WAIT",
        "next_action": next_actions[state],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument(
        "--case",
        help="one JSON admission object; malformed input continues locally",
    )
    command.add_argument(
        "--receipt-case",
        help="one JSON receipt object; a missing receipt requires --wait-case admission",
    )
    command.add_argument(
        "--wait-case",
        help="one JSON pre-wait object; missing sweep evidence continues locally",
    )
    command.add_argument(
        "--dispatch-case",
        help="one JSON lane-dispatch object; empty active lanes become event-only",
    )
    command.add_argument(
        "--case-stdin",
        action="store_true",
        help=(
            "read one JSON admission from standard input; schema selects the "
            "classifier. Use this instead of inline JSON from PowerShell."
        ),
    )
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.case_stdin else (
            args.case
            if args.case is not None
            else args.receipt_case
            if args.receipt_case is not None
            else args.wait_case
            if args.wait_case is not None
            else args.dispatch_case
        )
        value = json.loads(_strip_transport_bom(raw))
    except json.JSONDecodeError:
        value = None
    if args.case_stdin:
        result = _classify_schema_case(value)
    else:
        result = (
            classify(value)
            if args.case is not None
            else classify_receipt(value)
            if args.receipt_case is not None
            else classify_wait(value)
            if args.wait_case is not None
            else classify_dispatch(value)
        )
    print(json.dumps(result, sort_keys=True))
    return 0


def _classify_schema_case(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return _result("CONTINUE_LOCAL", "INVALID_CASE_SCHEMA")
    schema = value.get("schema")
    if schema == SCHEMA:
        return classify(value)
    if schema == RECEIPT_SCHEMA:
        return classify_receipt(value)
    if schema == WAIT_SCHEMA:
        return classify_wait(value)
    if schema == DISPATCH_SCHEMA:
        return classify_dispatch(value)
    return _result("CONTINUE_LOCAL", "INVALID_CASE_SCHEMA")


def _strip_transport_bom(raw: str) -> str:
    """Handle both Unicode and legacy-decoded UTF-8 BOMs from PowerShell."""
    raw = raw.lstrip("\ufeff")
    return raw[3:] if raw.startswith("\u00ef\u00bb\u00bf") else raw


if __name__ == "__main__":
    raise SystemExit(main())
