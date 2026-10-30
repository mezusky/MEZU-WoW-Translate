"""Protect WoW execute-phase prose without overriding the Execute spell.

Source-only examples: Arms Warrior Midnight rotation (Execute Priority),
Warlock Affliction WotLK rotation, Hunter Survival WotLK rotation.
Historical guides are linguistic heldouts, not current gameplay advice.
This test does not validate Chrome's browser-local translation or DOM.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExecutePhaseGlossaryTests(unittest.TestCase):
    def test_locale_scoped_phrase_does_not_override_spell(self):
        data = json.loads(
            (ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            (data["sourceLanguage"], data["targetLanguage"]), ("en", "fr")
        )
        jargon = data["jargon"]
        for source, target in (
            ("execute phase", "phase d’exécution"),
            ("Execute phase", "Phase d’exécution"),
            ("Execute Phase", "Phase d’exécution"),
        ):
            self.assertEqual(jargon[source], target)

        # "Execute" is an official spell name in some specs, whereas the
        # execute phase is a generic low-health combat window. Do not
        # globally rewrite the spell or every occurrence of "execute".
        self.assertFalse(
            any(key.casefold() in {"execute", "execution"} for key in jargon)
        )
        manual = json.loads(
            (ROOT / "data/manual_overrides.json").read_text(encoding="utf-8")
        )
        for layer in ("jargon", "exact"):
            old = {key.casefold() for key in manual.get(layer, {})}
            self.assertNotIn("execute phase", old)
            self.assertNotIn("execute", old)


if __name__ == "__main__":
    unittest.main()
