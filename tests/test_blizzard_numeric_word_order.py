"""Cross-role numeric word-order safety, based on live-indexed Wowhead sources.

Preservation Evoker (Rewind percentages/durations), Restoration Shaman
(Healing Tide Totem distance/targets), Windwalker Monk (Chi and cooldowns).
Sentences below are synthetic translation fixtures, not captured Chrome output.
"""
import unittest

from scripts.build_blizzard_memory import (
    _alignment_number_tokens,
    _numeric_fact_sequences_match,
    numeric_semantics_match,
    structural_score,
)


class NumericWordOrderTests(unittest.TestCase):
    def test_healer_distance_and_target_count_may_reorder(self):
        en = "Healing Tide Totem heals 5 targets within 40 yards."
        fr = "À 40 mètres, le Totem de marée de soins soigne 5 cibles."
        self.assertTrue(numeric_semantics_match(en, fr))
        self.assertTrue(_numeric_fact_sequences_match(
            _alignment_number_tokens(en, "en-US"),
            _alignment_number_tokens(fr, "fr-FR"),
        ))

    def test_healer_duration_and_percent_may_reorder(self):
        self.assertTrue(numeric_semantics_match(
            "Rewind restores 33% of damage taken for 5 seconds.",
            "Pendant 5 secondes, Rembobinage rend 33 % des dégâts subis.",
        ))

    def test_ambiguous_over_duration_stays_conservative(self):
        # English "over 5 seconds" can describe elapsed time or a strict
        # greater-than threshold. Do not infer its meaning from unit alone.
        # A false negative is safer than teaching Blizzard memory a false pair.
        self.assertFalse(numeric_semantics_match(
            "Rewind restores 33% of damage taken over 5 seconds.",
            "Pendant 5 secondes, Rembobinage rend 33 % des dégâts subis.",
        ))

    def test_monk_resource_and_duration_may_reorder(self):
        self.assertTrue(numeric_semantics_match(
            "Spend 2 Chi during a 6-second window.",
            "Pendant 6 secondes, dépensez 2 points de chi.",
        ))

    def test_inclusive_threshold_remains_mandatory(self):
        en = "Healing Tide Totem heals up to 5 targets within 40 yards."
        self.assertTrue(numeric_semantics_match(
            en, "Dans un rayon de 40 mètres, soigne jusqu'à 5 cibles."
        ))
        self.assertFalse(numeric_semantics_match(
            en, "Dans un rayon de 40 mètres, soigne 5 cibles."
        ))

    def test_same_unit_value_order_must_not_swap(self):
        self.assertFalse(numeric_semantics_match(
            "Damage increases by 10% and healing increases by 20%.",
            "Les soins augmentent de 20 % et les dégâts de 10 %.",
        ))

    def test_untyped_values_remain_ordered(self):
        self.assertFalse(numeric_semantics_match(
            "Use 3 spells then 5 abilities.",
            "Utilisez 5 capacités puis 3 sorts.",
        ))

    def test_cross_unit_magnitude_change_is_rejected(self):
        self.assertFalse(numeric_semantics_match(
            "Heal 5 targets within 40 yards.",
            "Soignez 5 cibles dans un rayon de 30 mètres.",
        ))

    def test_alignment_rewards_safe_reordering(self):
        en = ("li", "Heal 5 targets within 40 yards.")
        good = ("li", "Dans un rayon de 40 mètres, soignez 5 cibles.")
        bad = ("li", "Dans un rayon de 30 mètres, soignez 5 cibles.")
        self.assertGreater(structural_score(en, good), structural_score(en, bad))


if __name__ == "__main__":
    unittest.main()
