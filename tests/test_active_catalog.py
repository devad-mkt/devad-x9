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
        self.assertTrue((ROOT / "compat" / "seo-content-engine" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
