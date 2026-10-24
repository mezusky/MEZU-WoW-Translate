"""Signed numeric modifiers must not be inverted in official phrase memory."""
import unittest

from scripts.build_blizzard_memory import good_pair, numeric_facts


class SignedNumericMemoryTests(unittest.TestCase):
    def test_negative_percent_is_not_unsigned_positive(self):
        self.assertEqual(numeric_facts("Damage reduced by -5%."), [("-5", "%")])
        self.assertEqual(numeric_facts("Dégâts réduits de 5 %."), [("5", "%")])
        self.assertFalse(good_pair("Damage reduced by -5%.",
                                   "Dégâts réduits de 5 %.", 6.0))

    def test_unicode_minus_is_normalized(self):
        self.assertEqual(numeric_facts("Damage reduced by −5%."), [("-5", "%")])
        self.assertTrue(good_pair("Damage reduced by -5%.",
                                  "Dégâts réduits de −5 %.", 6.0))

    def test_explicit_plus_is_equivalent_to_positive(self):
        self.assertEqual(numeric_facts("Damage increased by +5%."),
                         numeric_facts("Dégâts augmentés de 5 %."))
        self.assertTrue(good_pair("Damage increased by +5%.",
                                  "Dégâts augmentés de 5 %.", 6.0))


    def test_swapped_percentages_are_not_an_exact_translation(self):
        en = "Health increases by 5%, while damage increases by 10%."
        fr = "Les points de vie augmentent de 10 %, tandis que les dégâts augmentent de 5 %."
        self.assertEqual(numeric_facts(en), [("5", "%"), ("10", "%")])
        self.assertEqual(numeric_facts(fr), [("10", "%"), ("5", "%")])
        self.assertFalse(good_pair(en, fr, 7.0))

    def test_correctly_ordered_percentages_remain_eligible(self):
        en = "Health increases by 5%, while damage increases by 10%."
        fr = "Les points de vie augmentent de 5 %, tandis que les dégâts augmentent de 10 %."
        self.assertTrue(good_pair(en, fr, 7.0))


    def test_compact_range_is_not_a_negative_modifier(self):
        self.assertEqual(numeric_facts("Your damage rises by 10-20%."),
                         [("10", ""), ("20", "%")])
        self.assertEqual(numeric_facts("Your damage rises by 10–20%."),
                         [("10", ""), ("20", "%")])
        self.assertEqual(numeric_facts("Your damage rises by 10—20%."),
                         [("10", ""), ("20", "%")])
        self.assertTrue(good_pair("Your damage rises by 10-20%.",
                                  "Vos dégâts augmentent de 10 à 20 %.", 6.0))

    def test_real_negative_modifier_after_a_word_is_preserved(self):
        self.assertEqual(numeric_facts("From 10 to -5% damage."),
                         [("10", ""), ("-5", "%")])
        self.assertFalse(good_pair("From 10 to -5% damage.",
                                   "De 10 à 5 % de dégâts.", 6.0))

    def test_range_endpoints_must_remain_in_order(self):
        self.assertFalse(good_pair("Damage increases by 10-20%.",
                                   "Les dégâts augmentent de 20 à 10 %.", 6.0))


if __name__ == "__main__":
    unittest.main()
