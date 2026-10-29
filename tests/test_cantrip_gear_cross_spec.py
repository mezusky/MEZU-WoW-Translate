"""Cross-spec French gear jargon, grounded in live Wowhead Season 2 guides.

Arcane Mage: 'cantrip weapon effect'; Frost Mage: 'cantrip item';
Fire Mage: 'cantrip gear'. These are descriptions of item effects, not
Blizzard spell or item names. This does not assert browser output.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CantripGearGlossaryTests(unittest.TestCase):
    def test_contextual_gear_phrases_share_locale_specific_meaning(self):
        payload = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
            encoding="utf-8"))
        self.assertEqual(payload["sourceLanguage"], "en")
        self.assertEqual(payload["targetLanguage"], "fr")
        expected = {
            "cantrip item": "objet à effet spécial",
            "cantrip items": "objets à effet spécial",
            "cantrip gear": "équipement à effet spécial",
            "cantrip weapon effect": "effet spécial de l’arme",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(payload["jargon"][source], target)
        # A bare 'cantrip' may refer to something other than an item effect.
        self.assertNotIn("cantrip", payload["jargon"])

    def test_no_legacy_duplicate_or_full_sentence_override(self):
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for term in ("cantrip item", "cantrip items", "cantrip gear",
                     "cantrip weapon effect"):
            with self.subTest(term=term):
                self.assertNotIn(term, manual.get("jargon", {}))
                self.assertNotIn(term, manual.get("exact", {}))


if __name__ == "__main__":
    unittest.main()
