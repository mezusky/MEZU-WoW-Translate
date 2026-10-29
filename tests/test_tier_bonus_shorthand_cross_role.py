"""Locale-scoped tier-bonus shorthand across independent Wowhead specs.

Preservation Evoker Season 1 tier guide uses "2pc bonus" in prose;
Blood Death Knight and Survival Hunter tier guides use 2pc/4pc as
structured class-set labels. Only the prose phrases are mapped here:
bare "2pc"/"4pc" and canonical item/spell identifiers stay untouched.
Source-only evidence, not a browser Translator API assertion.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class TierBonusShorthandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))

    def test_short_forms_extend_existing_set_bonus_family(self):
        terms = select_jargon(self.player, "en-US", "fr-FR")
        for source, target in {
            "2pc bonus": "bonus 2 pièces",
            "4pc bonus": "bonus 4 pièces",
            "2-piece bonus": "bonus 2 pièces",
            "4-piece bonus": "bonus 4 pièces",
            "2-set bonus": "bonus 2 pièces",
            "4-set bonus": "bonus 4 pièces",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
        # Bare numeric labels occur inside structured official set effects.
        for label in ("2pc", "4pc", "Class Set 2pc", "Class Set 4pc"):
            self.assertNotIn(label, terms)

    def test_no_manual_duplication_or_cross_locale_leakage(self):
        for phrase in ("2pc bonus", "4pc bonus"):
            self.assertNotIn(phrase, self.manual.get("exact", {}))
            self.assertNotIn(phrase, self.manual.get("jargon", {}))
        self.assertEqual(select_jargon(self.player, "en-US", "en-GB"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de-DE", "fr-FR")
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
