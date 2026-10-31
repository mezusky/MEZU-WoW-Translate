"""Source-only cross-role regression for SimulationCraft/Raidbots terminology.

Indexed Wowhead pages use "sim your own character" in DPS gearing and
"sim your gear" in healer stat guides. This checks data isolation and corpus
coverage, not the browser Translator API or rich-text reconstruction.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class SimulationJargonCrossRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_contextual_simulation_phrases(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["sim your own character"], "simuler votre personnage")
        self.assertEqual(terms["sim your character"], "simuler votre personnage")
        self.assertEqual(terms["sim your gear"], "simuler votre équipement")
        # "sim" alone is ambiguous (verb, noun, proper name); leave it to prose fallback.
        self.assertNotIn("sim", terms)
        self.assertNotIn("simulation", terms)
        for layer in ("jargon", "exact"):
            legacy = {key.casefold() for key in self.manual.get(layer, {})}
            for phrase in ("sim your own character", "sim your character", "sim your gear"):
                self.assertNotIn(phrase, legacy)

    def test_locale_isolation(self):
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en-US", "de-DE")

    def test_cross_role_and_class_heldouts_already_in_corpus(self):
        urls = {p["url"] for p in self.pages}
        for suffix in (
            "hunter/beast-mastery/stat-priority-pve-dps",
            "mage/arcane/stat-priority-pve-dps",
            "warrior/protection/stat-priority-pve-tank",
            "priest/discipline/bis-gear",
            "shaman/restoration/stat-priority-pve-healer",
        ):
            with self.subTest(suffix=suffix):
                self.assertIn("https://www.wowhead.com/guide/classes/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
