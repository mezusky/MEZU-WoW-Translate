"""Source-only regression for CDR jargon across unrelated class guides.

This validates data selection, not browser Translator API or DOM output.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class CdrCrossRoleTests(unittest.TestCase):
    def test_abbreviation_is_locale_scoped_and_not_a_spell_override(self):
        glossary = json.loads(
            (ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8")
        )
        terms = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(terms["CDR"], "réduction de CD")
        self.assertEqual(terms["cdr"], "réduction de CD")
        self.assertNotIn("Cull the Weak", terms)
        self.assertNotIn("Ashen Catalyst", terms)
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "de-DE")

    def test_abbreviation_is_not_duplicated_in_legacy_overrides(self):
        manual = json.loads(
            (ROOT / "data/manual_overrides.json").read_text(encoding="utf-8")
        )
        for layer in ("jargon", "exact", "protected_names"):
            for term in ("CDR", "cdr"):
                with self.subTest(layer=layer, term=term):
                    self.assertNotIn(term, manual.get(layer, {}))

    def test_independent_class_sources_are_already_in_corpus(self):
        pages = json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]
        urls = {page["url"] for page in pages}
        for spec in (
            "warrior/protection/rotation-cooldowns-pve-tank",
            "warlock/affliction/rotation-cooldowns-pve-dps",
            "shaman/enhancement/rotation-cooldowns-pve-dps",
            "druid/balance/rotation-cooldowns-pve-dps",
        ):
            with self.subTest(spec=spec):
                self.assertIn("https://www.wowhead.com/guide/classes/" + spec, urls)


if __name__ == "__main__":
    unittest.main()
