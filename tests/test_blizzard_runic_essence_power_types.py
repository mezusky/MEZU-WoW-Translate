"""Official counted Runic Power / Essence mappings remain locale-scoped and ID-based.

Examples are short snippets, not copied guide passages. The source/target
quantity gate protects semantic resource identity, not browser translation.
"""
import unittest

from scripts.build_blizzard_memory import numeric_semantics_match, resource_count_facts


class CountedRunicPowerEssenceTests(unittest.TestCase):
    def test_blood_and_unholy_death_knight_runic_power(self):
        self.assertEqual(resource_count_facts("Gain 10 Runic Power.", "en-US"), [("10", "6")])
        self.assertEqual(resource_count_facts("Gagne 10 points de puissance runique.", "fr-FR"),
                         [("10", "6")])
        self.assertTrue(numeric_semantics_match(
            "Gain 10 Runic Power.", "Gagne 10 points de puissance runique."))
        self.assertTrue(numeric_semantics_match(
            "Costs 1 Runic Power.", "Coûte 1 point de puissance runique."))

    def test_preservation_and_devastation_evoker_essence(self):
        self.assertEqual(resource_count_facts("Gain 2 Essence.", "en-US"), [("2", "19")])
        self.assertEqual(resource_count_facts("Gagne 2 points d’essence.", "fr-FR"),
                         [("2", "19")])
        self.assertTrue(numeric_semantics_match(
            "Gain 2 Essence.", "Gagne 2 points d’essence."))
        self.assertTrue(numeric_semantics_match(
            "Spend 1 Essence.", "Dépense 1 point d'essence."))

    def test_cross_class_resource_swaps_rejected(self):
        self.assertFalse(numeric_semantics_match(
            "Gain 10 Runic Power.", "Gagne 10 points d’essence."))
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Essence.", "Gagne 2 points de puissance runique."))
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Essence.", "Gagne 2 points de focalisation."))

    def test_quantity_and_order_still_matter(self):
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Essence.", "Gagne 3 points d’essence."))
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Essence and 10 Runic Power.",
            "Gagne 10 points de puissance runique et 2 points d’essence."))

    def test_uncounted_essence_is_not_assumed_to_be_resource(self):
        self.assertEqual(resource_count_facts("The essence of dragons.", "en-US"), [])
        self.assertEqual(resource_count_facts("L’essence des dragons.", "fr-FR"), [])

    def test_unknown_locale_never_borrows_french_forms(self):
        self.assertEqual(resource_count_facts("2 points d’essence", "fr-CA"), [])
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Essence.", "Gagne 2 points d’essence.", "en-US", "fr-CA"))


if __name__ == "__main__":
    unittest.main()
