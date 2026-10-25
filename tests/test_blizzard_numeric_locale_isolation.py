"""Cross-role numeric-unit vocabulary isolation for official Blizzard phrase memory.

Source examples come from indexed Wowhead Brewmaster, Restoration Shaman and
Beast Mastery Hunter guides. Expected translations are synthetic, not captured
from Chrome Translator API.
"""
import unittest

from scripts.build_blizzard_memory import (
    numeric_facts, numeric_semantics_match, structural_score,
)


class NumericLocaleIsolationTests(unittest.TestCase):
    def test_time_units_translate_by_locale(self):
        source = "The buff lasts 15 seconds and recharges in 2 minutes."
        target = "L'effet dure 15 secondes et se recharge en 2 minutes."
        self.assertEqual(numeric_facts(source, "en-US"),
                         [("15", "s"), ("2", "min")])
        self.assertEqual(numeric_facts(target, "fr-FR"),
                         [("15", "s"), ("2", "min")])
        self.assertTrue(numeric_semantics_match(source, target))

    def test_counted_targets_and_stacks_translate_by_locale(self):
        source = "Heals 5 targets with 2 stacks."
        target = "Soigne 5 cibles avec 2 cumuls."
        self.assertEqual(numeric_facts(source, "en-US"),
                         [("5", "target"), ("2", "stack")])
        self.assertEqual(numeric_facts(target, "fr-FR"),
                         [("5", "target"), ("2", "stack")])
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertFalse(numeric_semantics_match(source,
                         "Soigne 5 cumuls avec 2 cibles."))

    def test_written_english_units_do_not_leak_into_french(self):
        self.assertEqual(numeric_facts("15 seconds, 5 targets, 2 stacks", "fr-FR"),
                         [("15", ""), ("5", ""), ("2", "")])

    def test_written_french_units_do_not_leak_into_english(self):
        self.assertEqual(numeric_facts("15 secondes, 5 cibles, 2 cumuls", "en-US"),
                         [("15", ""), ("5", ""), ("2", "")])

    def test_unknown_locale_does_not_inherit_en_or_fr(self):
        self.assertEqual(numeric_facts("15 seconds, 5 cibles", "de-DE"),
                         [("15", ""), ("5", "")])
        self.assertEqual(numeric_facts("15 secondes, 5 targets", "es-ES"),
                         [("15", ""), ("5", "")])

    def test_shared_symbols_remain_locale_independent(self):
        for locale in ("en-US", "fr-FR", "de-DE"):
            with self.subTest(locale=locale):
                self.assertEqual(numeric_facts("100 ms, 2 s, 3 min, 4 h, 5%", locale),
                                 [("100", "ms"), ("2", "s"), ("3", "min"),
                                  ("4", "h"), ("5", "%")])

    def test_hyphenated_and_abbreviated_duration_regression(self):
        self.assertTrue(numeric_semantics_match(
            "A 6-second-long buff with a 45-seconds recharge.",
            "Un effet de 6 secondes avec une recharge de 45 secondes."))
        self.assertTrue(numeric_semantics_match(
            "After 2 hrs. and 30 mins.", "Après 2 heures et 30 minutes."))
        self.assertFalse(numeric_semantics_match(
            "A 6-second-long buff.", "Un effet de 6 minutes."))

    def test_alignment_uses_locale_scoped_canonical_units(self):
        en = ("li", "Heals 5 targets for 10 seconds.")
        fr = ("li", "Soigne 5 cibles pendant 10 secondes.")
        wrong = ("li", "Soigne 5 cumuls pendant 10 secondes.")
        self.assertGreater(structural_score(en, fr), structural_score(en, wrong))


if __name__ == "__main__":
    unittest.main()
