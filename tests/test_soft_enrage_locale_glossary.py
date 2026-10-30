"""Keep WoW raid soft-enrage jargon distinct from unrelated enrage/cap terms.

English Wowhead source checks: Affliction and Demonology Warlock Manaforge
Omega raid guides; Protection Paladin Manaforge Omega raid tips; Devastation
Evoker Vault of the Incarnates raid tips (legacy heldout).
This is an offline data contract, not proof of browser-rendered translation.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SoftEnrageLocaleTests(unittest.TestCase):
    def test_soft_enrage_is_locale_scoped_and_reusable(self):
        glossary = json.loads(
            (ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            (glossary["sourceLanguage"], glossary["targetLanguage"]),
            ("en", "fr"),
        )
        terms = glossary["jargon"]
        self.assertEqual(terms["soft enrage"], "enrage progressif")
        self.assertEqual(terms["soft-enrage"], "enrage progressif")
        self.assertEqual(
            terms["soft enrage timer"], "timer d’enrage progressif"
        )

        # "enrage" alone can be a Blizzard mechanic, a boss ability or
        # a different hard-enrage deadline. "soft cap" concerns stats.
        for unsafe in ("enrage", "soft", "soft cap", "hard enrage"):
            self.assertNotIn(unsafe, terms)
        self.assertEqual(terms["enrage timer"], "timer d’enrage")

        manual = json.loads(
            (ROOT / "data/manual_overrides.json").read_text(encoding="utf-8")
        )
        for layer in ("jargon", "exact"):
            legacy = {key.casefold() for key in manual.get(layer, {})}
            for key in ("soft enrage", "soft-enrage", "soft enrage timer"):
                self.assertNotIn(key.casefold(), legacy)


if __name__ == "__main__":
    unittest.main()
