"""Cross-class numeric resource identities use locale data and canonical IDs.

Short, synthetic examples based on distinct WoW roles. These validate only the
official Blizzard phrase-memory safety gate, not Chrome's Translator API.
"""
import unittest

from scripts.build_blizzard_memory import numeric_semantics_match, resource_count_facts


class ChiFuryResourceTests(unittest.TestCase):
    def test_vengeance_demon_hunter_fury(self):
        self.assertEqual(resource_count_facts("Maintain 75 Fury.", "en-US"), [("75", "17")])
        self.assertEqual(resource_count_facts("Gardez 75 points de fureur.", "fr-FR"),
                         [("75", "17")])
        self.assertTrue(numeric_semantics_match(
            "Maintain 75 Fury.", "Gardez 75 points de fureur."))

    def test_windwalker_monk_chi(self):
        self.assertEqual(resource_count_facts("Spend 2 Chi.", "en-US"), [("2", "12")])
        self.assertEqual(resource_count_facts("Dépensez 2 points de chi.", "fr-FR"),
                         [("2", "12")])
        self.assertTrue(numeric_semantics_match(
            "Spend 2 Chi.", "Dépensez 2 points de chi."))

    def test_abbreviated_runic_power(self):
        self.assertEqual(resource_count_facts("45 RP", "en-US"), [("45", "6")])
        self.assertTrue(numeric_semantics_match(
            "You need 45 RP.", "Il vous faut 45 points de puissance runique."))
        self.assertFalse(numeric_semantics_match(
            "You need 45 RP.", "Il vous faut 45 points de fureur."))

    def test_resource_identity_cannot_be_swapped(self):
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Chi.", "Gagnez 2 points de fureur."))
        self.assertFalse(numeric_semantics_match(
            "Gain 75 Fury.", "Gagnez 75 points de chi."))
        self.assertFalse(numeric_semantics_match(
            "Gain 75 Fury.", "Gagnez 75 points de puissance runique."))

    def test_narrative_terms_not_assumed_resources(self):
        self.assertEqual(resource_count_facts("A fury of strikes.", "en-US"), [])
        self.assertEqual(resource_count_facts("The chi of the monk.", "en-US"), [])
        self.assertEqual(resource_count_facts("La fureur du combat.", "fr-FR"), [])

    def test_hyphenated_character_name_not_chi_resource(self):
        self.assertEqual(resource_count_facts("2 Chi-Ji appearances", "en-US"), [])
        self.assertEqual(resource_count_facts("2 Chi-Ji", "fr-FR"), [])

    def test_locale_isolation(self):
        self.assertEqual(resource_count_facts("75 points de fureur", "fr-CA"), [])
        self.assertEqual(resource_count_facts("2 points de chi", "de-DE"), [])
        self.assertFalse(numeric_semantics_match(
            "Gain 2 Chi.", "Gagnez 2 points de chi.", "en-US", "fr-CA"))


if __name__ == "__main__":
    unittest.main()
