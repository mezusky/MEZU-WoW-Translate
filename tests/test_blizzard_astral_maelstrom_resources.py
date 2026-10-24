"""Cross-class canonical resource count safety for Balance Druid and Elemental Shaman.

Synthetic collector tests; do not claim browser Translator API verification.
"""
import unittest

from scripts.build_blizzard_memory import numeric_semantics_match, resource_count_facts


class AstralAndMaelstromResourceTests(unittest.TestCase):
    def test_astral_power_uses_canonical_id_in_both_locales(self):
        self.assertEqual(resource_count_facts("Generate 20 Astral Power.", "en-US"), [("20", "8")])
        self.assertEqual(resource_count_facts("Générez 20 points de puissance astrale.", "fr-FR"), [("20", "8")])
        self.assertTrue(numeric_semantics_match(
            "Generate 20 Astral Power.", "Générez 20 points de puissance astrale."))

    def test_maelstrom_uses_distinct_canonical_id(self):
        self.assertEqual(resource_count_facts("Gain 15 Maelstrom.", "en-US"), [("15", "11")])
        self.assertEqual(resource_count_facts("Gagnez 15 points de Maelström.", "fr-FR"), [("15", "11")])
        self.assertTrue(numeric_semantics_match(
            "Gain 15 Maelstrom.", "Gagnez 15 points de maelström."))

    def test_cross_resource_substitution_is_rejected(self):
        self.assertFalse(numeric_semantics_match(
            "Gain 20 Astral Power.", "Gagnez 20 points de maelström."))
        self.assertFalse(numeric_semantics_match(
            "Gain 15 Maelstrom.", "Gagnez 15 points de puissance astrale."))

    def test_maelstrom_weapon_is_a_spell_not_power_type_11(self):
        self.assertEqual(resource_count_facts("10 Maelstrom Weapon stacks", "en-US"), [])
        self.assertEqual(resource_count_facts("10 Maelstrom stacks", "en-US"), [("10", "11")])
        self.assertEqual(resource_count_facts("20 Astral Power. Spend it.", "en-US"), [("20", "8")])

    def test_unrecognized_locales_do_not_borrow_french_aliases(self):
        self.assertEqual(resource_count_facts("20 points de puissance astrale", "de-DE"), [])
        self.assertEqual(resource_count_facts("15 points de maelström", "de-DE"), [])


if __name__ == "__main__":
    unittest.main()
