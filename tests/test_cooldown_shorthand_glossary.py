"""Cooldown-state ambiguity regression from independent Wowhead guides.

Source-only tests: these do not simulate Chrome Translator API output.
A flat glossary cannot distinguish an instruction to cast when ready from
a statement that an ability is currently unavailable.
"""
import json
import re
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class CooldownShorthandTests(unittest.TestCase):
    def test_ambiguous_shorthand_is_not_a_context_free_replacement(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        for phrase in ("on cooldown", "on cd", "On CD"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, terms)
                self.assertNotIn(phrase, MANUAL.get("jargon", {}))
                self.assertNotIn(phrase, MANUAL.get("exact", {}))
        # Unlike "on cooldown", "off cooldown" consistently means ready.
        self.assertEqual(terms["off cooldown"], "disponible")
        self.assertNotIn("cd", terms)

    def test_same_words_have_opposite_meanings_across_guides(self):
        # Brief English source fixtures, not observed French output.
        # The Priest guide itself uses "on cd" for BOTH instructions and
        # the unavailable state, so matching solely by substring is unsafe.
        examples = (
            ("discipline-priest-rotation", "Cast Mind Blast on cd", "cast_when_ready"),
            ("discipline-priest-rotation", "if Evang is on cd", "currently_unavailable"),
            ("frost-mage-rotation", "Keep it on cooldown", "cast_when_ready"),
            ("brewmaster-monk-rotation", "using them on cooldown", "cast_when_ready"),
        )
        ids = {page["id"] for page in PAGES}
        observed = set()
        for guide, sample, sense in examples:
            with self.subTest(guide=guide, sense=sense):
                self.assertIn(guide, ids)
                self.assertRegex(sample.lower(), r"\bon (?:cd|cooldown)\b")
                self.assertNotIn(sample, MANUAL.get("exact", {}))
                observed.add(sense)
        self.assertEqual(observed, {"cast_when_ready", "currently_unavailable"})

    def test_locale_isolation(self):
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        for source, target in (("fr-FR", "en-US"), ("en-US", "de-DE")):
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    select_jargon(GLOSSARY, source, target)


if __name__ == "__main__":
    unittest.main()
