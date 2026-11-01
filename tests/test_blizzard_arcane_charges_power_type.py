"""Arcane Mage charges must be validated by canonical PowerType ID 16.

The source is Wowhead Arcane Mage stat/rotation prose and official French
Blizzard Arcane resource terminology. This protects official phrase-memory
alignment, not browser rendering or automatic translation.
"""
import unittest

from scripts.build_blizzard_memory import (
    numeric_facts, numeric_semantics_match, resource_count_facts,
)


class ArcaneChargesPowerTypeTests(unittest.TestCase):
    def test_mage_arcane_singular_and_plural(self):
        cases = (
            ("Gain 1 Arcane Charge.", "Gagne 1 charge arcanique.", "1"),
            ("Gain 4 Arcane Charges.", "Gagne 4 charges arcaniques.", "4"),
        )
        for english, french, amount in cases:
            with self.subTest(english=english):
                self.assertEqual(resource_count_facts(english, "en-US"),
                                 [(amount, "16")])
                self.assertEqual(resource_count_facts(french, "fr-FR"),
                                 [(amount, "16")])
                self.assertTrue(numeric_semantics_match(english, french))

    def test_arcane_charges_are_not_spell_ability_charges(self):
        self.assertEqual(numeric_facts("Gagne 4 charges arcaniques.", "fr-FR"),
                         [("4", "")])
        self.assertFalse(numeric_semantics_match(
            "Gain 4 Arcane Charges.", "Gagne 4 charges disponibles."))

    def test_independent_paladin_and_rogue_resources_do_not_cross_map(self):
        self.assertFalse(numeric_semantics_match(
            "Gain 4 Arcane Charges.", "Gagne 4 charges de puissance sacrée."))
        self.assertFalse(numeric_semantics_match(
            "Gain 4 Arcane Charges.", "Gagne 4 points de combo."))
        self.assertFalse(numeric_semantics_match(
            "Gain 3 Holy Power.", "Gagne 3 charges arcaniques."))

    def test_unknown_target_locale_cannot_borrow_french_resource_names(self):
        self.assertEqual(resource_count_facts("4 charges arcaniques", "fr-CA"), [])
        self.assertFalse(numeric_semantics_match(
            "Gain 4 Arcane Charges.", "Gagne 4 charges arcaniques.",
            "en-US", "fr-CA"))


if __name__ == "__main__":
    unittest.main()
