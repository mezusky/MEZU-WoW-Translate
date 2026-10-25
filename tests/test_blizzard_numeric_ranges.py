"""Conservative locale-aware numeric range semantics in official phrase memory.

Indexed Wowhead source examples: Devastation Evoker empower target ranges,
Destruction Warlock 1-2 targets, and Brewmaster Stagger 1-29%/30-59%.
These are offline safety checks, not Chrome Translator API verification.
"""
import unittest

from scripts.build_blizzard_memory import good_pair, numeric_semantics_match, range_facts


class NumericRangeTests(unittest.TestCase):
    def test_evoker_target_rank_ranges(self):
        self.assertEqual(range_facts("Rank 1: 1-2 Targets", "en-US"), [("1", "2")])
        self.assertTrue(numeric_semantics_match(
            "Rank 1: 1-2 Targets.", "Rang 1 : 1 à 2 cibles."
        ))
        self.assertTrue(numeric_semantics_match(
            "Rank 2: 3–4 Targets.", "Rang 2 : 3 à 4 cibles."
        ))

    def test_warlock_targets_range_vs_disjunction(self):
        source = "Cast Chaos Bolt on 1-2 targets."
        self.assertTrue(numeric_semantics_match(
            source, "Lancez Trait du chaos sur 1 à 2 cibles."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Lancez Trait du chaos sur 1 ou 2 cibles."
        ))

    def test_brewmaster_stagger_percentage_bands(self):
        self.assertTrue(numeric_semantics_match(
            "Light Stagger is 1-29% of maximum health.",
            "Le report léger représente 1 à 29 % des points de vie maximum."
        ))
        self.assertFalse(numeric_semantics_match(
            "Moderate Stagger is 30-59% of maximum health.",
            "Le report modéré représente 30 ou 59 % des points de vie maximum."
        ))

    def test_ordered_endpoints_and_multiple_ranges(self):
        self.assertEqual(range_facts("1-2 targets, 3-4 targets", "en-US"),
                         [("1", "2"), ("3", "4")])
        self.assertFalse(numeric_semantics_match(
            "Choose 1-2 targets, then 3-4 targets.",
            "Choisissez 1 à 2 cibles, puis 4 à 3 cibles."
        ))

    def test_grouped_numbers_and_decimal_endpoints(self):
        self.assertTrue(numeric_semantics_match(
            "Between 1,000-2,000 damage and 0.5-1.5 seconds.",
            "Entre 1 000 à 2 000 dégâts et 0,5 à 1,5 secondes."
        ))
        self.assertEqual(range_facts("1,000-2,000", "en-US"), [("1000", "2000")])

    def test_devourer_collapsing_star_and_soul_ranges(self):
        self.assertTrue(numeric_semantics_match(
            "Cast 4-5 Collapsing Stars per window.",
            "Lancez 4 à 5 Étoiles effondrées par fenêtre."
        ))
        self.assertFalse(numeric_semantics_match(
            "Collect 10-20 souls before the next window.",
            "Récupérez 10 ou 20 âmes avant la prochaine fenêtre."
        ))

    def test_unknown_locale_isolation(self):
        self.assertEqual(range_facts("1 to 2 targets", "de-DE"), [])
        self.assertEqual(range_facts("1 à 2 cibles", "en-US"), [])
        self.assertEqual(range_facts("1–2 targets", "de-DE"), [("1", "2")])

    def test_good_pair_filters_missing_range(self):
        source = "Use this spell against 1-2 targets."
        self.assertTrue(good_pair(
            source, "Utilisez ce sort contre 1 à 2 cibles.", 8.0
        ))
        self.assertFalse(good_pair(
            source, "Utilisez ce sort contre 1 ou 2 cibles.", 8.0
        ))


if __name__ == "__main__":
    unittest.main()
