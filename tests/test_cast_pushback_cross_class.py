"""Cross-class EN->FR contract for damage-induced cast-time pushback.

English guide evidence: Forever Discipline Priest abilities and Classic
Restoration Shaman PvP. Official FR spell tooltips describe casting time
being delayed by damage. This is a data-layer test, not browser rendering.
"""
import unittest
from pathlib import Path

from scripts.locale_glossary import parse_json_unique_keys, select_jargon


DATA = Path(__file__).resolve().parents[1] / "data"


class CastPushbackLocaleTests(unittest.TestCase):
    def test_cast_time_pushback_is_specific_to_damage_delays(self):
        player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        terms = select_jargon(player, "en-US", "fr-FR")

        # Priest: "prevents cast time pushback while active".
        # Shaman: "vulnerable to cast time pushback and interrupts".
        self.assertEqual(terms["cast time pushback"],
                         "retard d’incantation causé par les dégâts")
        for layer in ("exact", "jargon"):
            self.assertNotIn("cast time pushback", manual.get(layer, {}))

        # Bare pushback also covers channeled spells, whereas knockback is
        # physical displacement. Neither can safely use this casting rule.
        for ambiguous in ("pushback", "spell pushback", "knockback",
                          "interrupt", "interruption", "cast time"):
            self.assertNotIn(ambiguous, terms)

    def test_no_leakage_to_other_translation_directions(self):
        player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(player, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
