"""Cross-class canonical Rage/Focus count protection in official phrase memory.

Only explicitly numbered resource names are compared. Locale-specific forms
are data-only and unknown target locales cannot borrow French spellings.
"""
import unittest

from scripts.build_blizzard_memory import numeric_semantics_match, resource_count_facts


class CountedRageFocusTests(unittest.TestCase):
    def test_protection_and_fury_warrior_rage(self):
        self.assertEqual(resource_count_facts("Generate 30 Rage.", "en-US"), [("30", "1")])
        self.assertEqual(resource_count_facts("Génère 30 points de rage.", "fr-FR"), [("30", "1")])
        self.assertTrue(numeric_semantics_match(
            "Generate 30 Rage.", "Génère 30 points de rage."))
        self.assertTrue(numeric_semantics_match(
            "Spend 1 Rage.", "Dépensez 1 point de rage."))

    def test_beast_mastery_and_survival_hunter_focus(self):
        self.assertEqual(resource_count_facts("Restores 30 Focus.", "en-US"), [("30", "2")])
        self.assertEqual(resource_count_facts(
            "Rend 30 points de focalisation.", "fr-FR"), [("30", "2")])
        self.assertTrue(numeric_semantics_match(
            "Generates 10 Focus.", "Génère 10 points de focalisation."))
        self.assertTrue(numeric_semantics_match(
            "Spend 1 Focus.", "Dépensez 1 point de focalisation."))

    def test_wrong_resource_or_quantity_is_rejected(self):
        self.assertFalse(numeric_semantics_match(
            "Generate 30 Rage.", "Génère 30 points de focalisation."))
        self.assertFalse(numeric_semantics_match(
            "Generates 10 Focus.", "Génère 10 points de rage."))
        self.assertFalse(numeric_semantics_match(
            "Generates 10 Focus.", "Génère 20 points de focalisation."))

    def test_other_canonical_resources_are_not_confused(self):
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Holy Power.", "Dépensez 3 points de rage."))
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Combo Points.", "Dépensez 3 points de focalisation."))

    def test_unknown_target_locale_does_not_borrow_france(self):
        self.assertEqual(resource_count_facts("30 points de focalisation", "fr-CA"), [])
        self.assertFalse(numeric_semantics_match(
            "Generates 30 Focus.", "Génère 30 points de focalisation.",
            "en-US", "fr-CA"))


if __name__ == "__main__":
    unittest.main()
