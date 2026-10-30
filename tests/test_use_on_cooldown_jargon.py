"""Cross-class French terminology contract for imperative cooldown advice.

Source-only evidence: Protection Warrior leveling/rotation and Devastation
Evoker leveling (Wowhead, indexed 2026-10-30). This does not assert a Chrome
Translator API result or DOM rendering behavior.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))


class ImperativeCooldownJargonTests(unittest.TestCase):
    def test_unambiguous_imperative_is_reusable_across_specs(self):
        terms = GLOSSARY["jargon"]
        # Warrior: "Use on cooldown." Evoker: "Use on cooldown, unless ..."
        for phrase in ("Use on cooldown", "Use on Cooldown"):
            with self.subTest(phrase=phrase):
                self.assertEqual(terms[phrase], "À utiliser dès que disponible")
                self.assertNotIn(phrase, MANUAL.get("exact", {}))
                self.assertNotIn(phrase, MANUAL.get("jargon", {}))

    def test_ability_state_must_not_be_rewritten_as_an_instruction(self):
        # "While Shield Slam is on cooldown" means the ability is recharging.
        # Never introduce a bare "on cooldown" rule in the locale glossary.
        terms = GLOSSARY["jargon"]
        for unsafe in ("on cooldown", "On Cooldown", "cooldown"):
            self.assertNotIn(unsafe, terms)
        self.assertEqual(select_jargon(GLOSSARY, "en-US", "fr-FR")["Use on cooldown"],
                         "À utiliser dès que disponible")
        self.assertEqual(select_jargon(GLOSSARY, "fr", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")


if __name__ == "__main__":
    unittest.main()
