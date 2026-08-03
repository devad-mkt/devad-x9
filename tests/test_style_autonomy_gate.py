from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "skills" / "x9-loop-style" / "scripts" / "style_autonomy_gate.py"


def load_gate():
    spec = importlib.util.spec_from_file_location("style_autonomy_gate", PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StyleAutonomyGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = load_gate()

    def admission(self, **changes):
        return {
            "schema": self.gate.SCHEMA,
            "architecture_security_boundary": False,
            "distinct_failed_approaches": 0,
            "judgment_needed": False,
            "owner_boundary": False,
            "same_root_cause_cycles": 0,
            "single_route_failed": False,
            "stable_material_diff": False,
            "subagent_available": False,
            **changes,
        }

    def receipt(self, **changes):
        return {
            "schema": self.gate.RECEIPT_SCHEMA,
            "already_consumed": False,
            "expected_event": "LEASE_READY",
            "expected_receipt_sha256": "A" * 64,
            "expired": False,
            "receipt_present": True,
            "received_event": "LEASE_READY",
            "received_receipt_sha256": "a" * 64,
            **changes,
        }

    def test_ordinary_and_invalid_admission_continue_locally(self):
        for value in (None, {}, self.admission()):
            self.assertEqual("CONTINUE_LOCAL", self.gate.classify(value)["classification"])

    def test_same_root_cycles_one_to_three_stay_local(self):
        for cycles in (1, 2, 3):
            result = self.gate.classify(self.admission(same_root_cause_cycles=cycles))
            self.assertEqual("LOCAL_FALLBACK", result["classification"])

    def test_two_distinct_failures_need_explicit_judgment(self):
        self.assertEqual(
            "CONTINUE_LOCAL",
            self.gate.classify(self.admission(distinct_failed_approaches=2))["classification"],
        )
        self.assertEqual(
            "THINKER_ALLOWED",
            self.gate.classify(self.admission(distinct_failed_approaches=2, judgment_needed=True))["classification"],
        )

    def test_real_owner_boundary_escalates(self):
        self.assertEqual(
            "OWNER_REQUIRED",
            self.gate.classify(self.admission(owner_boundary=True))["classification"],
        )

    def test_missing_matching_and_zero_delta_receipts(self):
        self.assertEqual(
            "DEPENDENCY_WAIT",
            self.gate.classify_receipt(
                self.receipt(receipt_present=False, received_event=None, received_receipt_sha256=None)
            )["state"],
        )
        self.assertEqual("RESUME_READY", self.gate.classify_receipt(self.receipt())["state"])
        for value in (
            self.receipt(already_consumed=True),
            self.receipt(expired=True),
            self.receipt(received_event="WRONG"),
            self.receipt(received_receipt_sha256="b" * 64),
        ):
            self.assertEqual("ZERO_DELTA", self.gate.classify_receipt(value)["state"])

    def test_cli_receipt_case_has_no_runtime_side_effect(self):
        result = self.gate.main(["--receipt-case", json.dumps(self.receipt())])
        self.assertEqual(0, result)


if __name__ == "__main__":
    unittest.main()
