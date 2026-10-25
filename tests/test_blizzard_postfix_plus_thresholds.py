"""Preserve inclusive postfix thresholds found in unrelated Wowhead class guides.

Synthetic safety tests for official phrase-memory collection, not browser translation.
"""
import unittest

from scripts.build_blizzard_memory import good_pair, numeric_facts, numeric_semantics_match


class PostfixPlusThresholdTests(unittest.TestCase):
    def test_enhancement_maelstrom_weapon_stack_threshold(self):
        self.assertEqual(numeric_facts("Cast at 5+ stacks.", "en-US"), [("5+", "stack")])
        self.assertFalse(numeric_semantics_match(
            "Cast at 5+ stacks.", "Lancez à 5 cumuls."))
        self.assertTrue(numeric_semantics_match(
            "Cast at 5+ stacks.", "Lancez à 5+ cumuls."))

    def test_other_spec_stack_threshold_is_not_exact_count(self):
        self.assertEqual(numeric_facts("At ~6+ stacks", "en-US"), [("6+", "stack")])
        self.assertFalse(numeric_semantics_match(
            "At ~6+ stacks", "À environ 6 cumuls"))

    def test_postfix_plus_on_targets_and_percent(self):
        self.assertEqual(numeric_facts("Hit 10+ targets.", "en-US"), [("10+", "target")])
        self.assertFalse(numeric_semantics_match(
            "Hit 10+ targets.", "Touchez 10 cibles."))
        self.assertEqual(numeric_facts("Gain 5+%.", "en-US"), [("5+", "%")])

    def test_existing_signed_numbers_and_ranges_remain_stable(self):
        self.assertEqual(numeric_facts("From 10 to -5%.", "en-US"), [("10", ""), ("-5", "%")])
        self.assertEqual(numeric_facts("10-20%.", "en-US"), [("10", ""), ("20", "%")])
        self.assertTrue(numeric_semantics_match(
            "Gain +5% for 10-20 seconds.", "Gagnez 5 % pendant 10 à 20 secondes."))

    def test_unsafe_pair_rejected_before_memory_publication(self):
        self.assertFalse(good_pair(
            "Spend at 9+ stacks for maximum damage.",
            "Dépensez à 9 cumuls pour maximiser les dégâts.", 7.0))
        self.assertTrue(good_pair(
            "Spend at 9+ stacks for maximum damage.",
            "Dépensez à 9+ cumuls pour maximiser les dégâts.", 7.0))


if __name__ == "__main__":
    unittest.main()
