"""Source-grounded cross-role count-word safety checks, not Chrome translations.

Indexed Wowhead guides: Preservation Evoker (Stasis/target caps), Subtlety
Rogue (AoE threshold), and Brewmaster Monk (major cooldown count).
"""
import unittest

from scripts.locale_number_words import normalize_count_words
from scripts.build_blizzard_memory import numeric_semantics_match, good_pair


class LocaleNumberWordTests(unittest.TestCase):
    def test_locale_specific_normalization(self):
        self.assertEqual(normalize_count_words("three spells and five targets", "en-US"),
                         "3 spells and 5 targets")
        self.assertEqual(normalize_count_words("trois sorts et cinq cibles", "fr-FR"),
                         "3 sorts et 5 cibles")

    def test_unknown_locale_and_proper_names_remain_untouched(self):
        self.assertEqual(normalize_count_words("three spells", "de-DE"), "three spells")
        self.assertEqual(normalize_count_words("Three Kings and two-piece sets", "en-US"),
                         "Three Kings and two-piece sets")
        self.assertEqual(normalize_count_words("one target and un sort", "en-US"),
                         "one target and un sort")

    def test_evoker_stasis_rejects_wrong_spelled_count(self):
        source = "Stasis stores three healing spells for later use."
        self.assertTrue(numeric_semantics_match(source,
                         "Stase stocke trois sorts de soin pour plus tard."))
        self.assertFalse(numeric_semantics_match(source,
                          "Stase stocke deux sorts de soin pour plus tard."))
        self.assertFalse(good_pair(source, "Stase stocke deux sorts de soin pour plus tard.", 8.0))

    def test_spelled_and_digit_counts_are_equivalent(self):
        self.assertTrue(numeric_semantics_match(
            "Stasis stores three spells for 30 seconds.",
            "Stase stocke 3 sorts pendant 30 secondes."
        ))
        self.assertFalse(numeric_semantics_match(
            "Stasis stores three spells for 30 seconds.",
            "Stase stocke 3 sorts pendant 20 secondes."
        ))

    def test_rogue_aoe_inclusive_threshold(self):
        source = "Subtlety switches to AoE with two or more targets."
        self.assertTrue(numeric_semantics_match(
            source, "La Finesse passe en zone avec 2 cibles ou plus."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "La Finesse passe en zone avec 3 cibles ou plus."
        ))

    def test_evoker_up_to_five_targets(self):
        source = "Life-Giver's Flame heals up to five targets."
        self.assertTrue(numeric_semantics_match(
            source, "La Flamme du don de vie soigne jusqu'à cinq cibles."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "La Flamme du don de vie soigne jusqu'à quatre cibles."
        ))

    def test_brewmaster_major_cooldowns(self):
        source = "Brewmaster Monks have access to four major cooldown abilities."
        self.assertTrue(numeric_semantics_match(
            source, "Les moines Maîtres brasseurs ont quatre temps de recharge majeurs."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Les moines Maîtres brasseurs ont trois temps de recharge majeurs."
        ))

    def test_spell_name_and_single_quantity_not_guessed(self):
        self.assertEqual(normalize_count_words("The Four Horsemen", "en-US"),
                         "The Four Horsemen")
        self.assertEqual(normalize_count_words("one Essence Burst", "en-US"),
                         "one Essence Burst")
        self.assertTrue(numeric_semantics_match("Cast one spell.", "Lancez un sort."))


if __name__ == "__main__":
    unittest.main()
