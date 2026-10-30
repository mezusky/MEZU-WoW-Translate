"""Source-grounded cross-guide jargon guardrails.

English Wowhead sources: Holy Priest spot-healing, Protection Paladin's
squishy Prophet Velen, and Brewmaster Stagger vs ordinary 'stagger' verbs.
These assertions protect data choices; they do not simulate Chrome's
browser-local Translator API or certify rendered translations.
"""
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


class CrossGuideAmbiguityTests(unittest.TestCase):
    def test_squishy_is_fragility_not_low_hit_points(self):
        data = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(data["targetLanguage"], "fr")
        self.assertEqual(data["jargon"]["squishy"], "fragile")
        self.assertEqual(data["jargon"]["squishy targets"], "cibles fragiles")

    def test_stagger_is_not_an_unqualified_prose_override(self):
        # Brewmaster Stagger is an official ID-backed mechanic (Report in FR).
        # 'stagger the deaths' in a Windwalker guide is an ordinary verb.
        glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in (glossary["jargon"], manual.get("exact", {}), manual.get("jargon", {})):
            self.assertNotIn("stagger", {key.casefold() for key in layer})

    def test_spot_healing_is_contextual_player_jargon(self):
        data = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(data["jargon"]["spot-healing"], "soin ciblé")
        self.assertEqual(data["jargon"]["spot-heal"], "faire du soin ciblé")


if __name__ == "__main__":
    unittest.main()
