"""Locale-aware bounded ranges seen in independent Wowhead rotation/talent guides.

Retail Assassination Rogue talent builds: "between 2 and 3 targets".
MoP Classic Frost Mage rotation: "between 3 and 5 targets".
The French strings are expected synthetic translations, not browser output.
"""
import unittest

from scripts.build_blizzard_memory import (
    good_pair, numeric_semantics_match, range_facts,
)


class BoundedRangePhraseTests(unittest.TestCase):
    def test_rogue_retail_targets(self):
        source = "The breakpoint is between 2 and 3 targets."
        french = "Le seuil se situe entre 2 et 3 cibles."
        self.assertEqual(range_facts(source, "en-US"), [("2", "3")])
        self.assertEqual(range_facts(french, "fr-FR"), [("2", "3")])
        self.assertTrue(numeric_semantics_match(source, french))
        self.assertTrue(good_pair(source, french, 8.0))

    def test_mage_classic_targets_cross_page(self):
        source = "Nether Tempest is preferable between 3 and 5 targets."
        french = "Tempête du Néant est préférable de 3 à 5 cibles."
        self.assertTrue(numeric_semantics_match(source, french))
        self.assertEqual(range_facts(source, "en-US"), [("3", "5")])

    def test_conjunction_does_not_mean_range_without_prefix(self):
        self.assertEqual(range_facts("Use 2 and 3 charges.", "en-US"), [])
        self.assertEqual(range_facts("Utilisez 2 et 3 charges.", "fr-FR"), [])
        self.assertFalse(numeric_semantics_match(
            "Use between 2 and 3 charges.",
            "Utilisez 2 et 3 charges.",
        ))

    def test_reversed_and_missing_interval_are_rejected(self):
        source = "Choose between 2 and 3 targets."
        self.assertFalse(numeric_semantics_match(
            source, "Choisissez entre 3 et 2 cibles."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Choisissez 2 ou 3 cibles."
        ))

    def test_dash_and_between_are_equivalent_but_not_alternatives(self):
        self.assertTrue(numeric_semantics_match(
            "Between 2 and 3 targets are ideal.",
            "2-3 cibles sont idéales.",
        ))
        self.assertFalse(numeric_semantics_match(
            "Between 2 and 3 targets are ideal.",
            "2 cibles ou 3 cibles sont idéales.",
        ))

    def test_unknown_locale_does_not_borrow_english_or_french(self):
        self.assertEqual(range_facts("between 2 and 3 targets", "de-DE"), [])
        self.assertEqual(range_facts("entre 2 et 3 cibles", "en-US"), [])
        self.assertEqual(range_facts("between 2 and 3 targets", "fr-FR"), [])
        self.assertEqual(range_facts("2-3 targets", "de-DE"), [("2", "3")])


if __name__ == "__main__":
    unittest.main()
