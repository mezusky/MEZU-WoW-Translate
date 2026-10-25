"""Cross-class numeric alignment checks from indexed Wowhead guide patterns.

These compare expected French equivalents, not browser Translator API output.
"""
import unittest

from scripts.build_blizzard_memory import (
    _alignment_number_tokens, numeric_semantics_match, structural_score,
)


class CanonicalNumericAlignmentTests(unittest.TestCase):
    def test_blood_dk_decimal_percent_uses_locale_separator(self):
        en = ("li", "Healing proc increased from 6% to 7.2%.")
        fr = ("li", "Le soin passe de 6 % à 7,2 %.")
        wrong = ("li", "Le soin passe de 6 % à 7,3 %.")
        self.assertEqual(_alignment_number_tokens(en[1], "en-US"),
                         _alignment_number_tokens(fr[1], "fr-FR"))
        self.assertGreater(structural_score(en, fr), structural_score(en, wrong))
        self.assertTrue(numeric_semantics_match(en[1], fr[1]))
        self.assertFalse(numeric_semantics_match(en[1], wrong[1]))

    def test_brewmaster_decimal_duration_and_percent(self):
        en = ("li", "Gain 12.5% healing and reduce cooldown by 0.5 seconds.")
        fr = ("li", "Gagne 12,5 % de soins et réduit le recharge de 0,5 seconde.")
        wrong = ("li", "Gagne 12,5 % de soins et réduit le recharge de 0,5 minute.")
        self.assertGreater(structural_score(en, fr), structural_score(en, wrong))
        self.assertTrue(numeric_semantics_match(en[1], fr[1]))
        self.assertFalse(numeric_semantics_match(en[1], wrong[1]))

    def test_distance_unit_canonicalization(self):
        en = ("p", "The ability has a range of 40 yards.")
        fr = ("p", "Cette capacité a une portée de 40 mètres.")
        wrong = ("p", "Cette capacité dure 40 secondes.")
        self.assertGreater(structural_score(en, fr), structural_score(en, wrong))

    def test_inclusive_threshold_remains_alignment_equivalent(self):
        en = ("li", "Maintain 5+ stacks for this phase.")
        fr = ("li", "Gardez au moins 5 cumuls pendant cette phase.")
        self.assertEqual(_alignment_number_tokens(en[1], "en-US"),
                         _alignment_number_tokens(fr[1], "fr-FR"))
        self.assertTrue(numeric_semantics_match(en[1], fr[1]))

    def test_thousands_grouping_respects_declared_locale(self):
        en = ("p", "The threshold is 1,000 rating.")
        fr = ("p", "Le seuil est de 1 000 points.")
        wrong = ("p", "Le seuil est de 1 100 points.")
        self.assertEqual(_alignment_number_tokens(en[1], "en-US"),
                         _alignment_number_tokens(fr[1], "fr-FR"))
        self.assertGreater(structural_score(en, fr), structural_score(en, wrong))

    def test_unknown_locale_does_not_borrow_distance_vocabulary(self):
        self.assertEqual(_alignment_number_tokens("40 yards", "de-DE"), (("40", ""),))
        self.assertEqual(_alignment_number_tokens("40 mètres", "en-US"), (("40", ""),))


if __name__ == "__main__":
    unittest.main()
