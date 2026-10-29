"""Official Apex-talent terminology is reusable across unrelated Wowhead guides.

Source-only evidence: Blood DK, Vengeance DH and Protection Paladin tank
leveling; Discipline Priest overview (healer); Arcane Mage leveling (DPS).
Blizzard's French Midnight announcement calls these "talents de prestige".
This does not assert Chrome Translator API or DOM reconstruction success.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class ApexOfficialCrossRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
            encoding="utf-8"))
        cls.manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        cls.pages = {entry["url"] for entry in json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(
                encoding="utf-8"))["pages"]}

    def test_official_french_terms_and_case(self):
        terms = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "Apex Talent": "Talent de prestige",
            "Apex Talents": "Talents de prestige",
            "Apex talent": "talent de prestige",
            "Apex talents": "talents de prestige",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
                self.assertNotIn(source, self.manual.get("exact", {}))
                self.assertNotIn(source, self.manual.get("jargon", {}))
        # "Apex" by itself may refer to an unrelated WoW name or adjective.
        self.assertNotIn("Apex", terms)
        self.assertNotIn("apex", terms)

    def test_language_pair_isolation(self):
        self.assertEqual(select_jargon(self.player, "fr", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de", "fr")
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en", "de")

    def test_tank_leveling_heldouts_and_unrelated_roles(self):
        urls = (
            "https://www.wowhead.com/guide/classes/death-knight/blood/tank-leveling-tips",
            "https://www.wowhead.com/guide/classes/demon-hunter/vengeance/tank-leveling-tips",
            "https://www.wowhead.com/guide/classes/paladin/protection/tank-leveling-tips",
            "https://www.wowhead.com/guide/classes/priest/discipline/overview-pve-healer",
            "https://www.wowhead.com/guide/classes/mage/arcane/dps-leveling-tips",
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertIn(url, self.pages)


if __name__ == "__main__":
    unittest.main()
