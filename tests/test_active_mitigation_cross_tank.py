"""Blizzard-attested tank terminology reused across independent Midnight specs.

English source evidence: Guardian Druid abilities, Vengeance DH abilities,
plus Protection Paladin and Brewmaster Monk tank guides. Blizzard's French
2011 developer article explicitly uses "mitigation active"; no generic
"mitigation" replacement is introduced by this change.

Source-only test: Chrome Translator API and DOM output are not simulated.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class ActiveMitigationTests(unittest.TestCase):
    def test_official_fr_collocation(self):
        expected = {"active mitigation": "mitigation active",
                    "Active Mitigation": "Mitigation active"}
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_no_unscoped_mitigation_rule_added_to_player_glossary(self):
        self.assertNotIn("mitigation", GLOSSARY["jargon"])
        self.assertNotIn("mitigate", GLOSSARY["jargon"])

    def test_independent_tank_sources(self):
        ids = {p["id"] for p in PAGES}
        self.assertTrue({
            "guardian-druid-talents", "vengeance-demon-hunter-abilities",
            "protection-paladin-rotation", "brewmaster-monk-leveling"
        }.issubset(ids))

    def test_heldout_roles_and_sections(self):
        by_id = {p["id"]: p["url"] for p in PAGES}
        expected = {
            "protection-paladin-gear": "/paladin/protection/bis-gear",
            "brewmaster-monk-gear": "/monk/brewmaster/bis-gear",
            "vengeance-demon-hunter-mythic-plus": "/demon-hunter/vengeance/mythic-plus-dungeon-tips",
            "mistweaver-monk-gear": "/monk/mistweaver/bis-gear",
            "destruction-warlock-gear": "/warlock/destruction/bis-gear",
        }
        for key, suffix in expected.items():
            with self.subTest(page=key):
                self.assertEqual(by_id[key], "https://www.wowhead.com/guide/classes" + suffix)
        self.assertEqual(len(PAGES), len(set(by_id)))
        self.assertEqual(len(PAGES), len({p["url"] for p in PAGES}))

    def test_locale_isolation(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["active mitigation"], "mitigation active")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "es")


if __name__ == "__main__":
    unittest.main()
