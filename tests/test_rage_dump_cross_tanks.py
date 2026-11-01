"""Source-only Rage spending jargon across Guardian Druid and Protection Warrior.

The indexed Wowhead rotation pages show both imperative 'Dump rage' and
prose about dumping excess Rage. This tests locale-scoped terminology,
not the Chrome Translator API or rendered browser translation.
"""
import json
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class RageDumpCrossTankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((ROOT / "data/mezu_player_glossary.json")
                                  .read_text(encoding="utf-8"))

    def test_locale_scoped_meaning_and_capitalization(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["Dump rage"], "Dépenser la rage")
        self.assertEqual(terms["dump rage"], "dépenser la rage")
        self.assertEqual(terms["dump excess rage"], "dépenser l’excès de rage")
        self.assertNotIn("dump", terms)  # avoid ordinary non-WoW uses
        self.assertNotIn("Rage", terms)  # official resource names are ID-backed
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en-US", "de-DE")

    def test_source_only_matcher_favors_specific_spending_phrase(self):
        coverage = JargonCoverage(select_jargon(self.glossary, "en", "fr"))
        self.assertEqual(coverage.hits("Dump rage"), ["Dump rage"])
        self.assertEqual(coverage.hits("You should dump excess rage now."),
                         ["dump excess rage"])
        self.assertEqual(coverage.hits("Dump rage. Then dump excess rage."),
                         ["Dump rage", "dump excess rage"])
        self.assertEqual(coverage.hits("Dump the items into a bag."), [])

    def test_independent_current_tank_rotations_in_corpus(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json")
                           .read_text(encoding="utf-8"))["pages"]
        urls = {page["url"] for page in pages}
        for suffix in ("druid/guardian/rotation-cooldowns-pve-tank",
                       "warrior/protection/rotation-cooldowns-pve-tank"):
            with self.subTest(spec=suffix):
                self.assertIn("https://www.wowhead.com/guide/classes/" + suffix,
                              urls)

    def test_no_duplicate_legacy_rule(self):
        manual = json.loads((ROOT / "data/manual_overrides.json")
                            .read_text(encoding="utf-8"))
        for layer in ("jargon", "exact"):
            for term in ("Dump rage", "dump rage", "dump excess rage"):
                self.assertNotIn(term, manual.get(layer, {}))


if __name__ == "__main__":
    unittest.main()
