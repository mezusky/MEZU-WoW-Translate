"""Canonical power-type counts must remain stable across independent WoW specs.

IDs follow Enum.PowerType (4 combo points, 7 soul shards, 9 holy power).
The locale files contain official surface forms; the collector only compares IDs.
"""
import unittest

from scripts.build_blizzard_memory import numeric_semantics_match, resource_count_facts


class CanonicalPowerTypeCountTests(unittest.TestCase):
    def test_rogue_and_feral_combo_points(self):
        self.assertEqual(resource_count_facts("Spend 6 Combo Points.", "en-US"), [("6", "4")])
        self.assertEqual(resource_count_facts("Utilisez 6 points de combo.", "fr-FR"), [("6", "4")])
        self.assertTrue(numeric_semantics_match(
            "Spend 6 Combo Points.", "Utilisez 6 points de combo."))
        self.assertTrue(numeric_semantics_match(
            "Gain 1 Combo Point.", "Gagnez 1 point de combo."))

    def test_holy_and_protection_paladin_holy_power(self):
        self.assertEqual(resource_count_facts("Spend 3 Holy Power.", "en-US"), [("3", "9")])
        for translation in ("Dépensez 3 charges de puissance sacrée.",
                            "Dépensez 3 points de puissance sacrée."):
            with self.subTest(translation=translation):
                self.assertEqual(resource_count_facts(translation, "fr-FR"), [("3", "9")])
                self.assertTrue(numeric_semantics_match("Spend 3 Holy Power.", translation))
        self.assertTrue(numeric_semantics_match(
            "Gain 1 Holy Power.", "Gagnez 1 charge de puissance sacrée."))

    def test_resource_swap_and_wrong_quantity_are_rejected(self):
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Holy Power.", "Dépensez 3 points de combo."))
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Combo Points.", "Dépensez 3 charges de puissance sacrée."))
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Holy Power.", "Dépensez 4 charges de puissance sacrée."))
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Soul Shards.", "Dépensez 3 points de combo."))

    def test_locale_isolation_and_unrelated_numbers(self):
        self.assertEqual(resource_count_facts("3 Holy Power", "fr-CA"), [])
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Holy Power.", "Dépensez 3 charges de puissance sacrée.",
            "en-US", "fr-CA"))
        self.assertTrue(numeric_semantics_match(
            "Increase damage by 5%.", "Augmente les dégâts de 5 %.",
            "en-US", "fr-CA"))


if __name__ == "__main__":
    unittest.main()
