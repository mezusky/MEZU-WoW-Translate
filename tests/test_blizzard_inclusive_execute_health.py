"""Inclusive execute-health thresholds sampled from independent Wowhead guides.

English source: Protection Warrior rotation and Shadow Priest leveling.
French examples are synthetic expected prose, not browser Translator API output.
"""
import unittest

from scripts.build_blizzard_memory import comparison_facts, numeric_semantics_match, good_pair


class InclusiveHealthThresholdTests(unittest.TestCase):
    def test_warrior_execute_at_or_below_is_inclusive(self):
        source = "Execute targets at or below 20% health."
        target = "Utilisez Exécution sur les cibles ayant au maximum 20 % de points de vie."
        self.assertEqual(comparison_facts(source, "en-US"), [("<=", "20")])
        self.assertEqual(comparison_facts(target, "fr-FR"), [("<=", "20")])
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez Exécution sur les cibles ayant moins de 20 % de points de vie."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez Exécution sur les cibles ayant au moins 20 % de points de vie."
        ))

    def test_priest_execute_cross_class(self):
        source = "Shadow Word: Death targets at or below 20% health."
        target = "Mot de l'ombre : Mort sur les cibles à 20 % de vie au maximum."
        # Prefix wording is unambiguous; a compact postposed variant is not
        # assumed to work unless the locale grammar explicitly recognizes it.
        canonical = "Utilisez Mot de l'ombre : Mort sur les cibles avec au maximum 20 % de vie."
        self.assertTrue(numeric_semantics_match(source, canonical))
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez Mot de l'ombre : Mort sur les cibles avec plus de 20 % de vie."
        ))

    def test_upper_bound_and_locale_isolation(self):
        self.assertEqual(comparison_facts("at or above 80% health", "en-US"), [(">=", "80")])
        self.assertTrue(numeric_semantics_match(
            "Use this above threshold at or above 80% health.",
            "Utilisez ceci au moins à 80 % de points de vie."
        ))
        self.assertEqual(comparison_facts("at or below 20%", "de-DE"), [])
        self.assertEqual(comparison_facts("at or above 80%", "fr-FR"), [])

    def test_official_phrase_gate_rejects_strict_substitution(self):
        self.assertTrue(good_pair(
            "Execute targets at or below 20% health.",
            "Exécutez les cibles ayant au maximum 20 % de vie.", 8.0
        ))
        self.assertFalse(good_pair(
            "Execute targets at or below 20% health.",
            "Exécutez les cibles ayant moins de 20 % de vie.", 8.0
        ))


if __name__ == "__main__":
    unittest.main()
