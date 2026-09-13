from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ActiveCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = json.loads(
            (ROOT / "active" / "catalog.json").read_text(encoding="utf-8-sig")
        )

    def test_catalog_has_unique_entrypoints_and_required_z_names(self) -> None:
        names = [entry["name"] for entry in self.catalog["entries"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("z-content", names)
        self.assertIn("z-evidence-v2", names)
        self.assertNotIn("seo-content-engine", names)

    def test_nested_agent_router_is_installable(self) -> None:
        entry = next(item for item in self.catalog["entries"] if item["name"] == "a0-plugin-router")
        self.assertTrue((ROOT / "active" / entry["path"] / "SKILL.md").is_file())

    def test_legacy_style_package_remains_present(self) -> None:
        self.assertTrue((ROOT / "skills" / "x9-loop-style" / "SKILL.md").is_file())

    def test_compact_catalog_reuses_duplicates_and_keeps_s3_addon(self) -> None:
        compact = json.loads(
            (ROOT / "skills" / "compact-catalog.json").read_text(encoding="utf-8-sig")
        )
        entries = compact["entries"]
        self.assertEqual(compact["local_entrypoint_count"], len(self.catalog["entries"]))
        self.assertEqual(compact["compact_card_count"], 57)
        self.assertEqual(compact["reused_alias_count"], 18)
        self.assertTrue((ROOT / "skills" / "z-content" / "SKILL.md").is_file())
        self.assertTrue((ROOT / "skills" / "x9-s3-continuity" / "protocol.py").is_file())
        self.assertFalse((ROOT / "compat" / "seo-content-engine" / "SKILL.md").exists())
        self.assertEqual(
            {item["local_name"] for item in entries if item["local_name"] != "x9-s3-continuity"},
            {item["name"] for item in self.catalog["entries"]},
        )


if __name__ == "__main__":
    unittest.main()
