"""Cross-role source-only evidence for ranged interrupt jargon.

Indexed Wowhead Blood DK and Arms/Fury Warrior Mythic+ guides use
"ranged kick" or "ranged interrupt". This does not validate browser output.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class RangedInterruptCrossClassTests(unittest.TestCase):
    def test_fr_terms_and_language_isolation(self):
        glossary = json.loads(
            (ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8")
        )
        terms = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(terms["ranged kick"], "kick à distance")
        self.assertEqual(terms["ranged interrupt"], "interruption à distance")
        self.assertNotIn("ranged", terms)
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "de-DE")

    def test_no_manual_overrides_or_duplicate_spell_names(self):
        manual = json.loads(
            (ROOT / "data/manual_overrides.json").read_text(encoding="utf-8")
        )
        for layer in ("exact", "jargon", "protected_names"):
            for phrase in ("ranged kick", "ranged interrupt"):
                with self.subTest(layer=layer, phrase=phrase):
                    self.assertNotIn(phrase, manual.get(layer, {}))

    def test_independent_tank_and_dps_guides_in_corpus(self):
        pages = json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]
        urls = {page["url"] for page in pages}
        for spec in (
            "death-knight/blood/mythic-plus-dungeon-tips",
            "warrior/arms/mythic-plus-dungeon-tips",
            "warrior/fury/mythic-plus-dungeon-tips",
        ):
            with self.subTest(spec=spec):
                self.assertIn("https://www.wowhead.com/guide/classes/" + spec, urls)


if __name__ == "__main__":
    unittest.main()
