"""Offline contract tests for locale-specific, reusable player terminology."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))


class PlayerGlossaryTests(unittest.TestCase):
    def test_locale_is_explicit(self):
        self.assertEqual(GLOSSARY["sourceLanguage"], "en")
        self.assertEqual(GLOSSARY["targetLanguage"], "fr")
        self.assertNotEqual(GLOSSARY["sourceLanguage"], GLOSSARY["targetLanguage"])

    def test_jargon_entries_are_valid(self):
        jargon = GLOSSARY["jargon"]
        self.assertIsInstance(jargon, dict)
        for source, target in jargon.items():
            with self.subTest(source=source):
                self.assertIsInstance(source, str)
                self.assertIsInstance(target, str)
                self.assertTrue(source.strip())
                self.assertTrue(target.strip())

    def test_tier_terms_generalize_across_labels(self):
        jargon = GLOSSARY["jargon"]
        for source, target in {
            "tier set": "set de classe",
            "tier sets": "sets de classe",
            "set bonus": "bonus de set",
            "set bonuses": "bonus de set",
            "2-Set Bonus": "Bonus 2 pièces",
            "4-Set Bonus": "Bonus 4 pièces",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)


    def test_offpiece_variants_share_one_locale_specific_translation(self):
        # Seen across Preservation Evoker and unrelated Rogue/Monk gear guides.
        jargon = GLOSSARY["jargon"]
        for source in ("off-piece", "offpiece", "off piece"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "pièce hors set")
        for source in ("off-pieces", "offpieces", "off pieces"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "pièces hors set")


    def test_stat_threshold_terms_generalize_across_specs(self):
        # Blood DK, Arcane Mage and Brewmaster guides use the same stat section.
        jargon = GLOSSARY["jargon"]
        self.assertEqual(jargon["diminishing returns"], "rendements décroissants")
        self.assertEqual(jargon["diminishing return"], "rendement décroissant")
        self.assertEqual(jargon["breakpoint"], "seuil")
        self.assertEqual(jargon["breakpoints"], "seuils")


    def test_crafting_terms_shared_across_unrelated_specs(self):
        # Discipline Priest, Preservation Evoker, Fire Mage and Demonology
        # Warlock gear guides use these common crafting/equipment terms.
        jargon = GLOSSARY["jargon"]
        self.assertEqual(jargon["crafting order"], "ordre de craft")
        for spelling in ("off-hand", "offhand"):
            with self.subTest(spelling=spelling):
                self.assertEqual(jargon[spelling], "main gauche")
        for spelling in ("off-hands", "offhands"):
            with self.subTest(spelling=spelling):
                self.assertEqual(jargon[spelling], "mains gauches")
        self.assertEqual(jargon["embellishment"], "embellissement")
        self.assertEqual(jargon["embellishments"], "embellissements")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        self.assertNotIn("crafting order", manual.get("exact", {}))
        # "off-piece" means non-set armor, not an off-hand weapon.
        self.assertEqual(jargon["off-piece"], "pièce hors set")


    def test_locale_glossary_has_no_duplicate_legacy_jargon(self):
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        overlapping = set(GLOSSARY["jargon"]) & set(manual.get("jargon", {}))
        self.assertEqual(overlapping, set(), "Move terms to one locale-scoped source")


if __name__ == "__main__":
    unittest.main()
