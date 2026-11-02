"""Guard WoW spellcasting pushback terminology across unrelated guide roles.

Forever Protection Paladin: damage pushback during Holy Wrath casts.
Forever Holy Priest: Power Word: Shield prevents cast pushback.
Forever Druid/Priest: cast time pushback from damage.
A generic "pushback" rule would corrupt non-spell contexts such as
"push back the Lich King's army" in dungeon guides.
"""
import unittest
from pathlib import Path

from scripts.locale_glossary import parse_json_unique_keys, select_jargon


class PushbackContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "data" / "mezu_player_glossary.json"
        cls.glossary = parse_json_unique_keys(path.read_text(encoding="utf-8"))

    def test_cast_damage_and_protection_phrases(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["cast time pushback"], "retard d’incantation causé par les dégâts")
        self.assertEqual(terms["damage pushback"], "retard d’incantation dû aux dégâts")
        self.assertEqual(terms["pushback protection"], "protection contre le retard d’incantation")
        # Full raid-buff table label must not leave a stray English "Spell".
        # Observed on SoD Paladin Healer and Cata Holy/Shadow Priests.
        self.assertEqual(terms["spell pushback protection"], "protection contre le retard d’incantation")

    def test_no_ambiguous_generic_pushback_replacement(self):
        terms = select_jargon(self.glossary, "en", "fr")
        for unsafe in ("pushback", "push-back", "push back"):
            self.assertNotIn(unsafe, terms)

    def test_language_direction_isolated(self):
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
