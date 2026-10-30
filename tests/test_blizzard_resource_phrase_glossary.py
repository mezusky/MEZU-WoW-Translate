"""Reusable official WoW terminology, not guide-specific sentence overrides."""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data" / "mezu_player_glossary.json")
                      .read_text(encoding="utf-8"))


class BlizzardResourcePhraseTests(unittest.TestCase):
    def test_rogue_finisher_and_combo_resource_forms(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["finishing move"], "coup de grâce")
        self.assertEqual(terms["finishing moves"], "coups de grâce")
        self.assertEqual(terms["combo point"], "point de combo")
        self.assertEqual(terms["combo points"], "points de combo")

    def test_destruction_warlock_fragment_forms(self):
        terms = select_jargon(GLOSSARY, "en", "fr")
        self.assertEqual(terms["soul shard fragment"], "fragment d’éclat d’âme")
        self.assertEqual(terms["soul shard fragments"], "fragments d’éclat d’âme")
        self.assertNotIn("shard", terms)  # Avoid translating unrelated jargon.

    def test_locale_data_cannot_leak_into_other_targets(self):
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "de", "fr")
        self.assertEqual(select_jargon(GLOSSARY, "fr", "fr-FR"), {})


if __name__ == "__main__":
    unittest.main()
