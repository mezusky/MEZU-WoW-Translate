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


if __name__ == "__main__":
    unittest.main()
