"""Inclusive written comparison semantics observed in Arcane Mage rotation.

Synthetic expected French translations, not Chrome Translator API output.
"""
import unittest

from scripts.build_blizzard_memory import comparison_facts, numeric_semantics_match, good_pair


class ExplicitInclusiveComparisonTests(unittest.TestCase):
    def test_arcane_mage_opener_lte(self):
        source = "Use trinkets that buff you for less than or equal to 15 seconds."
        target = "Utilisez les bijoux dont l'effet dure au maximum 15 secondes."
        self.assertEqual(comparison_facts(source, "en-US"), [("<=", "15")])
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertTrue(good_pair(source, target, 8.0))

    def test_gte_and_gendered_french_forms(self):
        self.assertEqual(comparison_facts("greater than or equal to 5 targets", "en-US"), [(">=", "5")])
        self.assertEqual(comparison_facts("supérieur ou égal à 5 cibles", "fr-FR"), [(">=", "5")])
        self.assertEqual(comparison_facts("supérieure ou égale à 5 cibles", "fr-FR"), [(">=", "5")])
        self.assertEqual(comparison_facts("inférieure ou égale à 15 secondes", "fr-FR"), [("<=", "15")])

    def test_strict_threshold_is_not_equivalent(self):
        source = "Use trinkets that buff you for less than or equal to 15 seconds."
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez les bijoux dont l'effet dure moins de 15 secondes."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez les bijoux dont l'effet dure au moins 15 secondes."
        ))

    def test_locale_isolation_and_existing_forms(self):
        self.assertEqual(comparison_facts("less than or equal to 15", "de-DE"), [])
        self.assertEqual(comparison_facts("less than or equal to 15", "fr-FR"), [])
        self.assertEqual(comparison_facts("at or below 15", "en-US"), [("<=", "15")])
        self.assertEqual(comparison_facts("au maximum 15", "fr-FR"), [("<=", "15")])


if __name__ == "__main__":
    unittest.main()
