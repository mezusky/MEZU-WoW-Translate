"""Cross-role alignment tests grounded in indexed Wowhead guide quantity patterns.

This tests Blizzard phrase-memory alignment, not Chrome Translator output.
"""
import unittest

from scripts.build_blizzard_memory import structural_score, numeric_semantics_match


class SpelledCountAlignmentTests(unittest.TestCase):
    def test_evoker_spelled_count_matches_digit_count(self):
        source = ("p", "Stasis stores three spells for 30 seconds.")
        equivalent = ("p", "Stase stocke 3 sorts pendant 30 secondes.")
        wrong = ("p", "Stase stocke 4 sorts pendant 30 secondes.")
        self.assertGreater(structural_score(source, equivalent),
                           structural_score(source, wrong))
        self.assertTrue(numeric_semantics_match(source[1], equivalent[1]))
        self.assertFalse(numeric_semantics_match(source[1], wrong[1]))

    def test_brewmaster_spelled_count_aligns_to_spelled_count(self):
        source = ("p", "Brewmaster Monks have four major cooldown abilities.")
        equivalent = ("p", "Les moines Maîtres brasseurs ont quatre gros CD.")
        wrong = ("p", "Les moines Maîtres brasseurs ont cinq gros CD.")
        self.assertGreater(structural_score(source, equivalent),
                           structural_score(source, wrong))

    def test_mage_numeric_count_aligns_to_spelled_count(self):
        source = ("li", "Use 4 abilities before the next Combustion.")
        equivalent = ("li", "Utilisez quatre capacités avant la prochaine Combustion.")
        wrong = ("li", "Utilisez cinq capacités avant la prochaine Combustion.")
        self.assertGreater(structural_score(source, equivalent),
                           structural_score(source, wrong))

    def test_proper_name_remains_unmodified(self):
        source = ("p", "The Four Horsemen require 3 players.")
        equivalent = ("p", "Les Quatre Cavaliers nécessitent 3 joueurs.")
        # Both title-cased names are left alone by the conservative lexicon.
        self.assertTrue(numeric_semantics_match(source[1], equivalent[1]))


if __name__ == "__main__":
    unittest.main()
