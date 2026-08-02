from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "devad-x9-loop" / "scripts" / "program_import.py"


def load_program_import(testcase: unittest.TestCase):
    testcase.assertTrue(
        MODULE_PATH.is_file(),
        "program_import.py must exist before the V7 importer contract can pass",
    )
    name = "program_import_v7_under_test"
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    testcase.assertIsNotNone(spec)
    testcase.assertIsNotNone(spec.loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def inventory_row(path: str, sha256: str = "0" * 64, **overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "path": path,
        "sha256": sha256,
        "size": 1,
        "source_class": "CURRENT_GIT",
        "classification": "IMPORTED",
        "feature_ids": [],
        "chosen_fact_owner": "git",
        "reason": "current durable source",
    }
    row.update(overrides)
    return row


class CanonicalEncodingTests(unittest.TestCase):
    def test_canonical_json_and_jsonl_are_compact_utf8_integer_only_with_one_lf(self):
        program_import = load_program_import(self)
        self.assertEqual(
            b'{"a":"caf\xc3\xa9","z":1}\n',
            program_import.canonical_json_bytes({"z": 1, "a": "caf\u00e9"}),
        )
        self.assertEqual(
            b'{"a":1}\n{"b":2}\n',
            program_import.canonical_jsonl_bytes([{"a": 1}, {"b": 2}]),
        )
        for value in (1.5, float("nan"), float("inf"), {"nested": [2.0]}):
            with self.subTest(value=repr(value)):
                with self.assertRaises(program_import.CanonicalEncodingError):
                    program_import.canonical_json_bytes(value)

    def test_paths_are_repo_relative_nfc_forward_slash_and_escape_safe(self):
        program_import = load_program_import(self)
        decomposed = "Cafe\u0301\\notes.txt"
        self.assertEqual(
            unicodedata.normalize("NFC", decomposed).replace("\\", "/"),
            program_import.canonical_repo_path(decomposed),
        )
        for bad in (
            "/absolute.txt",
            "C:\\absolute.txt",
            "\\\\server\\share\\file.txt",
            "../escape.txt",
            "safe/../escape.txt",
        ):
            with self.subTest(path=bad):
                with self.assertRaises(program_import.PathSafetyError):
                    program_import.canonical_repo_path(bad)

    def test_casefold_collisions_and_conflicting_duplicate_rows_are_rejected(self):
        program_import = load_program_import(self)
        with self.assertRaises(program_import.PathCollisionError):
            program_import.validate_inventory_rows(
                [inventory_row("Docs/Readme.md"), inventory_row("docs/README.md")]
            )
        with self.assertRaises(program_import.InventoryConflictError):
            program_import.validate_inventory_rows(
                [inventory_row("same.txt"), inventory_row("same.txt", "1" * 64)]
            )

    def test_symlink_and_windows_reparse_escapes_are_detectable(self):
        program_import = load_program_import(self)
        fake_reparse = SimpleNamespace(
            st_mode=stat.S_IFDIR,
            st_file_attributes=getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400),
        )
        with mock.patch.object(program_import.os, "lstat", return_value=fake_reparse):
            self.assertTrue(program_import.is_reparse_point(Path("ignored")))

        with tempfile.TemporaryDirectory() as root_name, tempfile.TemporaryDirectory() as outside_name:
            root = Path(root_name)
            outside = Path(outside_name) / "secret.txt"
            outside.write_text("secret", encoding="utf-8")
            link = root / "escape.txt"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable on this host: {exc}")
            with self.assertRaises(program_import.PathEscapeError):
                program_import.inventory_durable_files(root)


class InventoryTests(unittest.TestCase):
    def test_inventory_streams_every_file_and_emits_only_required_metadata(self):
        program_import = load_program_import(self)
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            (root / "nested").mkdir()
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            payload = bytes(range(256)) * 600
            (root / "nested" / "b.bin").write_bytes(payload)
            metadata = {
                "nested/b.bin": {
                    "source_class": "OWNER_PACKET",
                    "classification": "POINTER",
                    "feature_ids": ["feature-b"],
                    "chosen_fact_owner": "owner",
                    "reason": "binary evidence stays out of model context",
                }
            }
            rows = program_import.inventory_durable_files(root, metadata_by_path=metadata)

        self.assertEqual(2, len(rows))
        self.assertEqual(["a.txt", "nested/b.bin"], [row["path"] for row in rows])
        self.assertEqual(
            {
                "path",
                "sha256",
                "size",
                "source_class",
                "classification",
                "feature_ids",
                "chosen_fact_owner",
                "reason",
            },
            set(rows[0]),
        )
        binary = rows[1]
        self.assertEqual(hashlib.sha256(payload).hexdigest(), binary["sha256"])
        self.assertEqual(len(payload), binary["size"])
        self.assertNotIn("content", binary)
        self.assertEqual("POINTER", binary["classification"])

    def test_root_hash_is_exact_concatenated_jsonl_and_shards_and_summary_obey_caps(self):
        program_import = load_program_import(self)
        rows = [
            inventory_row(
                f"evidence/{index:03d}.txt",
                hashlib.sha256(str(index).encode("ascii")).hexdigest(),
                size=index,
                classification=("IMPORTED" if index % 2 else "NOT_RELEVANT"),
                feature_ids=[f"feature-{index % 3}"],
            )
            for index in range(30)
        ]
        exact_jsonl = program_import.inventory_jsonl_bytes(rows)
        expected_root = hashlib.sha256(exact_jsonl).hexdigest()
        self.assertEqual(expected_root, program_import.inventory_root_sha256(rows))

        shards = program_import.shard_inventory(rows, max_bytes=1024)
        self.assertGreater(len(shards), 1)
        self.assertEqual(exact_jsonl, b"".join(shards))
        self.assertTrue(all(len(shard) <= 1024 for shard in shards))
        summary = program_import.build_coverage_summary(rows, shards)
        self.assertLessEqual(len(summary), program_import.COVERAGE_SUMMARY_MAX_BYTES)
        parsed = json.loads(summary)
        self.assertEqual(30, parsed["file_count"])
        self.assertEqual(expected_root, parsed["inventory_root_sha256"])
        self.assertEqual(len(shards), parsed["shard_count"])

    def test_omission_root_drift_and_expected_root_mismatch_fail_closed(self):
        program_import = load_program_import(self)
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            path = root / "durable.txt"
            path.write_text("version one", encoding="utf-8")
            rows = program_import.inventory_durable_files(root)
            expected_root = program_import.inventory_root_sha256(rows)
            self.assertEqual(expected_root, program_import.verify_inventory(root, rows))

            with self.assertRaises(program_import.InventoryOmissionError):
                program_import.verify_inventory(root, [])
            with self.assertRaises(program_import.RootDriftError):
                program_import.verify_inventory(root, rows, expected_root_sha256="f" * 64)

            path.write_text("version two", encoding="utf-8")
            with self.assertRaises(program_import.RootDriftError):
                program_import.verify_inventory(root, rows)

    def test_inventory_outputs_are_byte_identical_on_repeated_runs(self):
        program_import = load_program_import(self)
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            for index in range(7):
                (root / f"{index}.txt").write_text(f"value-{index}", encoding="utf-8")
            first = program_import.inventory_durable_files(root)
            second = program_import.inventory_durable_files(root)
        self.assertEqual(first, second)
        self.assertEqual(
            program_import.inventory_jsonl_bytes(first),
            program_import.inventory_jsonl_bytes(second),
        )
        self.assertEqual(
            program_import.build_coverage_summary(first, program_import.shard_inventory(first)),
            program_import.build_coverage_summary(second, program_import.shard_inventory(second)),
        )


class PrecedenceAndPacketTests(unittest.TestCase):
    def test_source_precedence_is_deterministic_and_equal_rank_conflicts_fail(self):
        program_import = load_program_import(self)
        historical = inventory_row(
            "fact.txt",
            "1" * 64,
            source_class="HISTORICAL_EVIDENCE",
            chosen_fact_owner="history",
        )
        current = inventory_row(
            "fact.txt",
            "2" * 64,
            source_class="CURRENT_GIT",
            chosen_fact_owner="git",
        )
        self.assertLess(
            program_import.source_precedence("CURRENT_GIT"),
            program_import.source_precedence("HISTORICAL_EVIDENCE"),
        )
        self.assertEqual(current, program_import.choose_precedent_source([historical, current]))
        with self.assertRaises(program_import.InventoryConflictError):
            program_import.choose_precedent_source(
                [current, inventory_row("fact.txt", "3" * 64, source_class="CURRENT_GIT")]
            )

    def test_packet_builders_use_canonical_bytes_and_enforce_exact_caps(self):
        program_import = load_program_import(self)
        program = program_import.build_program_packet({"mission": "import", "count": 3})
        feature = program_import.build_feature_packet({"feature_id": "feature-a", "count": 2})
        self.assertEqual("x9-loop-program-v1", json.loads(program)["schema"])
        self.assertEqual("x9-loop-feature-v1", json.loads(feature)["schema"])
        self.assertEqual(program, program_import.canonical_json_bytes(json.loads(program)))
        self.assertEqual(feature, program_import.canonical_json_bytes(json.loads(feature)))
        self.assertLessEqual(len(program), program_import.PROGRAM_PACKET_MAX_BYTES)
        self.assertLessEqual(len(feature), program_import.FEATURE_PACKET_MAX_BYTES)

        with self.assertRaises(program_import.PacketTooLargeError):
            program_import.build_program_packet({"blob": "x" * (16 * 1024)})
        with self.assertRaises(program_import.PacketTooLargeError):
            program_import.build_feature_packet({"blob": "x" * (32 * 1024)})
        with self.assertRaises(program_import.CanonicalEncodingError):
            program_import.build_program_packet({"bad": 1.25})

    def test_counts_are_derived_from_input_and_never_use_legacy_constant(self):
        program_import = load_program_import(self)
        rows = [inventory_row(f"{index}.txt") for index in range(11)]
        summary = json.loads(
            program_import.build_coverage_summary(rows, program_import.shard_inventory(rows))
        )
        self.assertEqual(len(rows), summary["file_count"])
        self.assertNotEqual(2333, summary["file_count"])


if __name__ == "__main__":
    unittest.main()
