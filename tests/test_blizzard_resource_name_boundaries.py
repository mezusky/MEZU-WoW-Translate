"""Counted resources must not absorb adjacent proper spell or spec names.

Source-only synthetic regression checks; Chrome Translator API remains unverified.
"""
import unittest

from scripts.build_blizzard_memory import numeric_semantics_match, resource_count_facts


class ResourceNameBoundaryTests(unittest.TestCase):
    def test_chi_spell_name_is_not_chi_resource(self):
        self.assertEqual(resource_count_facts("2 Chi Burst casts", "en-US"), [])
        self.assertEqual(resource_count_facts("3 Chi Wave casts", "en-US"), [])
        self.assertEqual(resource_count_facts("2 Chi-Ji appearances", "en-US"), [])

    def test_fury_spec_and_talent_names_are_not_fury_resource(self):
        self.assertEqual(resource_count_facts("3 Fury Warriors", "en-US"), [])
        self.assertEqual(resource_count_facts("3 Fury of the Aldrachi procs", "en-US"), [])

    def test_normal_counted_resources_still_match(self):
        self.assertEqual(resource_count_facts("Spend 2 Chi before the next cast.", "en-US"),
                         [("2", "12")])
        self.assertEqual(resource_count_facts("Generate 30 Fury during combat.", "en-US"),
                         [("30", "17")])
        self.assertEqual(resource_count_facts("Dépensez 2 points de chi.", "fr-FR"),
                         [("2", "12")])
        self.assertTrue(numeric_semantics_match(
            "Spend 2 Chi before the next cast.", "Dépensez 2 points de chi avant le prochain sort."))

    def test_title_case_filter_does_not_ignore_real_mismatch(self):
        self.assertFalse(numeric_semantics_match(
            "Spend 2 Chi.", "Dépensez 2 points de fureur."))
        self.assertFalse(numeric_semantics_match(
            "Generate 30 Fury.", "Générez 30 points de chi."))

    def test_other_locale_and_punctuation(self):
        self.assertEqual(resource_count_facts("2 Chi Burst casts", "de-DE"), [])
        self.assertEqual(resource_count_facts("2 Chi. Burst follows.", "en-US"), [("2", "12")])
        self.assertEqual(resource_count_facts("2 points de chi : dépensez-les.", "fr-FR"),
                         [("2", "12")])


if __name__ == "__main__":
    unittest.main()
