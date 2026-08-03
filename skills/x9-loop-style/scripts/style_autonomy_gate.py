#!/usr/bin/env python3
"""Classify one Style escalation or receipt without starting a runtime loop."""

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping


SCHEMA = "x9-style-autonomy-admission-v1"
RECEIPT_SCHEMA = "x9-style-receipt-admission-v1"
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
        label = "SUBAGENT_ONCE" if value["subagent_available"] else "LOCAL_FALLBACK"
        return _result(label, "ONE_ROUTE_FAILED")
    return _result("CONTINUE_LOCAL", "ROUTINE_OR_KNOWN_NEXT_ACTION")


def _result(classification: str, reason: str) -> dict[str, Any]:
    next_actions = {
        "CONTINUE_LOCAL": "continue the safe local action; do not send an outbound question",
        "LOCAL_FALLBACK": "try one materially different safe local route",
        "SUBAGENT_ONCE": "use at most one bounded same-authority advisory helper",
        "THINKER_ALLOWED": "request one review bound to current stable evidence",
        "OWNER_REQUIRED": "request the owner-bound decision and continue disjoint safe work",
    }
    return {
        "schema": SCHEMA,
        "classification": classification,
        "reason": reason,
        "outbound_question_allowed": classification in {"THINKER_ALLOWED", "OWNER_REQUIRED"},
        "next_action": next_actions[classification],
    }


def classify_receipt(value: Any) -> dict[str, Any]:
    """Classify one receipt without storing state, waking tasks, or retrying."""
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
        or (value.get("received_event") is not None and not isinstance(value.get("received_event"), str))
        or (value.get("received_receipt_sha256") is not None and not _is_sha256(value.get("received_receipt_sha256")))
    )
    if invalid or not value.get("receipt_present"):
        return _receipt_result("DEPENDENCY_WAIT", "MISSING_OR_INVALID_RECEIPT")
    if value["received_event"] != value["expected_event"]:
        return _receipt_result("ZERO_DELTA", "EVENT_MISMATCH")
    if value["received_receipt_sha256"].casefold() != value["expected_receipt_sha256"].casefold():
        return _receipt_result("ZERO_DELTA", "RECEIPT_HASH_MISMATCH")
    if value["expired"]:
        return _receipt_result("ZERO_DELTA", "RECEIPT_EXPIRED")
    if value["already_consumed"]:
        return _receipt_result("ZERO_DELTA", "DUPLICATE_RECEIPT")
    return _receipt_result("RESUME_READY", "MATCHING_FRESH_RECEIPT")


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())


def _receipt_result(state: str, reason: str) -> dict[str, Any]:
    return {"schema": RECEIPT_SCHEMA, "state": state, "reason": reason, "should_resume": state == "RESUME_READY"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--case", help="one JSON admission object")
    command.add_argument("--receipt-case", help="one JSON receipt object")
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.case if args.case is not None else args.receipt_case)
    except json.JSONDecodeError:
        value = None
    print(json.dumps(classify(value) if args.case is not None else classify_receipt(value), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
