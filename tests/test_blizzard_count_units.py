"""Keep WoW count nouns distinct in high-confidence official phrase memory."""
import unittest

from scripts.build_blizzard_memory import good_pair, numeric_facts, numeric_semantics_match


class BlizzardCountUnitTests(unittest.TestCase):
    def test_target_counts_are_language_neutral(self):
        self.assertEqual(numeric_facts("Hits up to 4 targets.", "en-US"), [("4", "target")])
        self.assertEqual(numeric_facts("Touche jusqu'à 4 cibles.", "fr-FR"), [("4", "target")])
        self.assertTrue(good_pair("Hits up to 4 targets.",
                                  "Touche jusqu'à 4 cibles.", 6.0))

    def test_stack_counts_are_language_neutral(self):
        self.assertEqual(numeric_facts("Grants 3 stacks.", "en-US"), [("3", "stack")])
        self.assertEqual(numeric_facts("Confère 3 cumuls.", "fr-FR"), [("3", "stack")])
        self.assertTrue(numeric_semantics_match("Grants 3 stacks.",
                                                "Confère 3 cumuls."))

    def test_target_stack_swaps_are_rejected(self):
        self.assertFalse(numeric_semantics_match("Hits 4 targets.",
                                                 "Touche 4 cumuls."))
        self.assertFalse(good_pair("Hits up to 4 targets.",
                                   "Applique jusqu'à 4 cumuls.", 6.0))
        self.assertFalse(numeric_semantics_match("Grants 3 stacks.",
                                                 "Confère 3 cibles."))

    def test_ambiguous_spell_charges_are_not_equated_to_stacks(self):
        self.assertEqual(numeric_facts("Grants 2 charges.", "en-US"), [("2", "wow_ability_charge")])
        self.assertTrue(numeric_semantics_match("Grants 2 charges.",
                                                "Confère 2 charges."))
        self.assertFalse(numeric_semantics_match("Grants 2 stacks.",
                                                 "Confère 2 charges."))
        self.assertTrue(numeric_semantics_match("Damage increased by 10-20%.",
                                                "Dégâts augmentés de 10 à 20 %."))


if __name__ == "__main__":
    unittest.main()
