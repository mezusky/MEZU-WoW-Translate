"""Cross-guide worded-threshold safety in official Blizzard phrase memory.

Source patterns sampled from Wowhead Destruction Warlock, Survival Hunter
raid tips, and Subtlety Rogue rotations. Synthetic translations are not a
browser Translator API audit.
"""
import unittest

from scripts.build_blizzard_memory import comparison_facts, numeric_semantics_match, good_pair


class LocalizedThresholdTests(unittest.TestCase):
    def test_warlock_less_than_four_shards(self):
        source = "Use Soul Fire when you have less than 4 Soul Shards."
        target = "Utilisez Feu de l'âme quand vous avez moins de 4 éclats d'âme."
        self.assertEqual(comparison_facts(source, "en-US"), [("<", "4")])
        self.assertEqual(comparison_facts(target, "fr-FR"), [("<", "4")])
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez Feu de l'âme quand vous avez plus de 4 éclats d'âme."
        ))

    def test_raid_fewer_than_three_hunters(self):
        source = "If you have fewer than 3 hunters, prioritize the first target."
        target = "Si vous avez moins de 3 chasseurs, privilégiez la première cible."
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertFalse(numeric_semantics_match(
            source, "Si vous avez au moins 3 chasseurs, privilégiez la première cible."
        ))

    def test_rogue_or_more_combo_points(self):
        source = "Use finishing moves with 6 or more Combo Points."
        target = "Utilisez les coups de grâce avec 6 points de combo ou plus."
        self.assertEqual(comparison_facts(source, "en-US"), [(">=", "6")])
        self.assertEqual(comparison_facts(target, "fr-FR"), [(">=", "6")])
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertFalse(numeric_semantics_match(
            source, "Utilisez les coups de grâce avec 6 points de combo ou moins."
        ))

    def test_inclusive_and_strict_directions(self):
        self.assertTrue(numeric_semantics_match(
            "Cast at least 4 times, and at most 2 times during the opener.",
            "Lancez au moins 4 fois et au plus 2 fois pendant l'ouverture."
        ))
        self.assertFalse(numeric_semantics_match(
            "Cast at least 4 times.", "Lancez plus de 4 fois."
        ))
        self.assertTrue(numeric_semantics_match(
            "Use up to 4 charges.", "Utilisez jusqu'à 4 charges."
        ))

    def test_longest_phrase_and_symbol_equivalence(self):
        self.assertEqual(comparison_facts("No more than 4 targets", "en-US"), [("<=", "4")])
        self.assertEqual(comparison_facts("Pas plus de 4 cibles", "fr-FR"), [("<=", "4")])
        self.assertTrue(numeric_semantics_match(
            "Use < 4 targets and >= 2 stacks.",
            "Utilisez moins de 4 cibles et au moins 2 cumuls."
        ))
        self.assertFalse(numeric_semantics_match(
            "Use < 4 targets.", "Utilisez au plus 4 cibles."
        ))

    def test_grouped_numbers_in_thresholds(self):
        self.assertTrue(numeric_semantics_match(
            "Deal more than 1,000 damage.",
            "Infligez plus de 1 000 points de dégâts."
        ))
        self.assertFalse(numeric_semantics_match(
            "Deal more than 1,000 damage.",
            "Infligez plus de 1,001 points de dégâts."
        ))

    def test_good_pair_gate_rejects_reversed_inequality(self):
        source = "You should cast the spell with less than 4 Soul Shards."
        correct = "Vous devriez lancer le sort avec moins de 4 éclats d'âme."
        wrong = "Vous devriez lancer le sort avec plus de 4 éclats d'âme."
        self.assertTrue(good_pair(source, correct, 8.0))
        self.assertFalse(good_pair(source, wrong, 8.0))

    def test_locale_isolation_and_non_comparison_prose(self):
        self.assertEqual(comparison_facts("less than 4", "de-DE"), [])
        self.assertEqual(comparison_facts("moins de 4", "en-US"), [])
        self.assertEqual(comparison_facts("You have 4 shards.", "en-US"), [])
        self.assertEqual(comparison_facts("Vous avez 4 éclats.", "fr-FR"), [])


if __name__ == "__main__":
    unittest.main()
