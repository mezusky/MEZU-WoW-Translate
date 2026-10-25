"""Locale-aware numeric facts on independent Wowhead tank/DPS source patterns.

Synthetic memory safety tests; these do not verify Chrome's Translator API.
"""
import unittest

from scripts.build_blizzard_memory import numeric_facts, numeric_semantics_match, good_pair


class LocaleGroupedNumbersTests(unittest.TestCase):
    def test_brewmaster_damage_example_grouped_thousands(self):
        source = "You take 25,000 damage and then 12,500 damage."
        target = "Vous subissez 25\u202f000 points de dégâts, puis 12 500 points de dégâts."
        self.assertEqual(numeric_facts(source, "en-US"), [("25000", ""), ("12500", "")])
        self.assertEqual(numeric_facts(target, "fr-FR"), [("25000", ""), ("12500", "")])
        self.assertTrue(numeric_semantics_match(source, target))

    def test_changed_damage_is_not_accepted(self):
        self.assertFalse(numeric_semantics_match(
            "The hit deals 25,000 damage.",
            "Le coup inflige 25 001 points de dégâts."
        ))

    def test_fractional_thousands_and_signed_modifiers(self):
        self.assertTrue(numeric_semantics_match(
            "Damage increases by +1,234.5 points and -5%.",
            "Les dégâts augmentent de 1 234,5 points et de -5 %."
        ))
        self.assertFalse(numeric_semantics_match(
            "Damage increases by +1,234.5 points.",
            "Les dégâts augmentent de 1 234,6 points."
        ))

    def test_same_comma_number_is_not_same_value_in_different_locales(self):
        self.assertFalse(numeric_semantics_match(
            "Deal 1,000 damage.", "Inflige 1,000 points de dégâts."
        ))
        self.assertTrue(numeric_semantics_match(
            "Deal 1,000 damage.", "Inflige 1 000 points de dégâts."
        ))

    def test_existing_thresholds_and_wow_resource_counts(self):
        self.assertTrue(numeric_semantics_match(
            "Spend 5+ Soul Shards and hit 3+ targets.",
            "Dépensez 5+ éclats d’âme et touchez 3+ cibles."
        ))
        self.assertFalse(numeric_semantics_match(
            "Spend 5+ Soul Shards and hit 3+ targets.",
            "Dépensez 5 éclats d’âme et touchez 3 cibles."
        ))

    def test_memory_pair_acceptance_does_not_ignore_numeric_changes(self):
        self.assertTrue(good_pair(
            "You take 25,000 damage and then 12,500 damage.",
            "Vous subissez 25 000 points de dégâts puis 12 500 points de dégâts.", 8.0
        ))
        self.assertFalse(good_pair(
            "You take 25,000 damage and then 12,500 damage.",
            "Vous subissez 25 000 points de dégâts puis 12 501 points de dégâts.", 8.0
        ))


if __name__ == "__main__":
    unittest.main()
