"""Cross-role postfix-plus and worded-threshold equivalence in official memory.

English source patterns sampled from Enhancement Shaman (5+ stacks),
Vengeance Demon Hunter (4+ Souls) and Outlaw Rogue (stage 3 or higher).
French strings are synthetic expectations, NOT browser translation output.
"""
import unittest

from scripts.build_blizzard_memory import (
    comparison_facts, good_pair, numeric_facts, numeric_semantics_match,
    resource_count_facts,
)


class CompactInclusiveThresholdTests(unittest.TestCase):
    def test_shaman_postfix_plus_matches_worded_french(self):
        source = "Cast with 5+ stacks."
        self.assertEqual(numeric_facts(source, "en-US"), [("5+", "stack")])
        self.assertEqual(comparison_facts(source, "en-US"), [(">=", "5")])
        self.assertTrue(numeric_semantics_match(
            source, "Lancez avec au moins 5 cumuls."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Lancez avec 5 cumuls."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Lancez avec au plus 5 cumuls."
        ))

    def test_vengeance_soul_threshold(self):
        self.assertTrue(numeric_semantics_match(
            "Use Spirit Bomb with 4+ Souls.",
            "Utilisez Bombe spirituelle avec 4 âmes ou plus."
        ))
        self.assertFalse(numeric_semantics_match(
            "Use Spirit Bomb with 4+ Souls.",
            "Utilisez Bombe spirituelle avec 4 âmes."
        ))

    def test_canonical_resource_count_with_plus(self):
        self.assertEqual(resource_count_facts("5+ Soul Shards", "en-US"),
                         [("5", "7")])
        self.assertEqual(resource_count_facts("au moins 5 éclats d'âme", "fr-FR"),
                         [("5", "7")])
        self.assertTrue(numeric_semantics_match(
            "Spend 5+ Soul Shards.",
            "Dépensez au moins 5 éclats d'âme."
        ))

    def test_rogue_stage_or_higher(self):
        self.assertEqual(comparison_facts("stage 3 or higher", "en-US"),
                         [(">=", "3")])
        self.assertTrue(numeric_semantics_match(
            "Cast at stage 3 or higher.",
            "Lancez au niveau 3 ou plus."
        ))
        self.assertFalse(numeric_semantics_match(
            "Cast at stage 3 or higher.",
            "Lancez au niveau 3 ou moins."
        ))

    def test_english_or_lower(self):
        self.assertEqual(comparison_facts("at stage 2 or lower", "en-US"),
                         [("<=", "2")])
        self.assertTrue(numeric_semantics_match(
            "Use at stage 2 or lower.",
            "Utilisez au niveau 2 ou moins."
        ))

    def test_addition_and_signed_modifiers_are_not_thresholds(self):
        self.assertEqual(comparison_facts("5+10", "en-US"), [])
        self.assertEqual(comparison_facts("+5% damage", "en-US"), [])
        self.assertEqual(comparison_facts("5+ stacks", "de-DE"), [(">=", "5")])
        self.assertEqual(comparison_facts("5 or higher", "de-DE"), [])

    def test_official_memory_gate_keeps_valid_pair_only(self):
        self.assertTrue(good_pair(
            "Cast this ability with 5+ stacks.",
            "Lancez cette capacité avec au moins 5 cumuls.", 8.0
        ))
        self.assertFalse(good_pair(
            "Cast this ability with 5+ stacks.",
            "Lancez cette capacité avec exactement 5 cumuls.", 8.0
        ))


if __name__ == "__main__":
    unittest.main()
