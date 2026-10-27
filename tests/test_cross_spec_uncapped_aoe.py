"""Uncapped AoE is a shared concept, not a guide-specific override.

Source-only examples: Devastation Evoker Mythic+ and Enhancement Shaman
rotation, both on retail Wowhead. Browser output is not asserted here.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class UncappedAoeTests(unittest.TestCase):
    def test_cross_spec_jargon_and_cap_distinction(self):
        player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        jargon = select_jargon(player, "en-US", "fr-FR")
        self.assertEqual(jargon["uncapped AoE"], "AoE sans limite de cibles")
        self.assertEqual(jargon["hard-capped AoE"], "AoE limitée à un nombre fixe de cibles")
        self.assertNotIn("uncapped", jargon)
        self.assertNotIn("AoE", jargon)
        self.assertNotIn("uncapped AoE", manual.get("exact", {}))
        self.assertNotIn("uncapped AoE", manual.get("jargon", {}))

    def test_locale_direction_and_same_language_noop(self):
        player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(player, "en", "en"), {})
        self.assertEqual(select_jargon(player, "en-US", "fr-CA")["uncapped AoE"],
                         "AoE sans limite de cibles")
        with self.assertRaises(ValueError):
            select_jargon(player, "fr", "en")


if __name__ == "__main__":
    unittest.main()
