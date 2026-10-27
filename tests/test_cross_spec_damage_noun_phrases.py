"""Cross-spec damage noun phrases are locale-scoped, not sentence overrides.

Source-only examples were sampled from Assassination Rogue, Frost Death Knight
and Mistweaver Monk Wowhead guides. No browser output is asserted here.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"
PLAYER = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))


class CrossSpecDamageNounTests(unittest.TestCase):
    def test_reusable_damage_phrases(self):
        jargon = select_jargon(PLAYER, "en-US", "fr-FR")
        expected = {
            "single-target damage": "dégâts monocibles",
            "single target damage": "dégâts monocibles",
            "cleave damage": "dégâts de cleave",
        }
        for source, french in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], french)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_do_not_conflate_incoming_damage_or_healing(self):
        jargon = PLAYER["jargon"]
        # Mistweaver raid tips discuss incoming single-target damage, while
        # other guides discuss outgoing DPS; the noun stays neutral.
        self.assertNotIn("single-target healing", jargon)
        self.assertNotIn("single target healing", jargon)
        self.assertNotIn("damage", jargon)
        self.assertEqual(jargon["damage intake"], "dégâts subis")
        self.assertEqual(jargon["damage profile"], "profil de dégâts")

    def test_direction_is_explicit_and_same_language_is_noop(self):
        self.assertEqual(select_jargon(PLAYER, "en", "en"), {})
        with self.assertRaises(ValueError):
            select_jargon(PLAYER, "fr", "en")
        self.assertEqual(select_jargon(PLAYER, "en", "fr-CA")["cleave damage"],
                         "dégâts de cleave")


if __name__ == "__main__":
    unittest.main()
