"""Source-only audit matching: no duplicate aliases or nested false coverage.

Synthetic excerpts are not browser-rendered translation evidence.
"""
import json
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class JargonCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
            encoding="utf-8"))
        cls.terms = select_jargon(data, "en-US", "fr-FR")
        cls.matcher = JargonCoverage(cls.terms)

    def test_case_aliases_are_one_hit_even_when_repeated(self):
        hits = self.matcher.hits(
            "Always Be Casting. Always be casting! always be casting.")
        self.assertEqual(hits, ["Always Be Casting"])

    def test_longest_phrase_prevents_nested_double_counting(self):
        hits = self.matcher.hits(
            "Very short cooldowns and short cooldown spells are useful.")
        self.assertEqual(hits, ["very short cooldowns", "short cooldown spells"])
        self.assertNotIn("short cooldown", hits)
        self.assertNotIn("short cooldowns", hits)

    def test_realistic_cross_role_fragments_keep_distinct_concepts(self):
        # Different roles/sections; no phrase or spec-specific overrides.
        examples = (
            ("Use smart heals and spot-healing on injured allies.",
             ["smart heals", "spot-healing"]),
            ("Always Be Casting and use your burst window.",
             ["Always Be Casting", "burst window"]),
            ("Your ranged interrupt is useful during AoE stops.",
             ["ranged interrupt", "AoE stops"]),
        )
        for prose, expected in examples:
            with self.subTest(prose=prose):
                self.assertEqual(self.matcher.hits(prose), expected)

    def test_boundaries_and_limit(self):
        self.assertEqual(self.matcher.hits("CDRplus isn't CDR; cdr helps.", 1),
                         ["CDR"])
        self.assertEqual(self.matcher.hits("CDRplus"), [])
        self.assertEqual(self.matcher.hits("CDR", 0), [])

    def test_unicode_casefold_mismatch_is_not_a_false_hit(self):
        # Python regex IGNORECASE matches dotted/dotless I against ASCII i,
        # but those characters do not have the same Unicode casefold key.
        matcher = JargonCoverage({"id": "identifier"})
        self.assertEqual(matcher.hits("İD"), [])
        self.assertEqual(matcher.hits("ID"), ["id"])

    def test_empty_and_invalid_glossaries(self):
        self.assertEqual(JargonCoverage({}).hits("CDR"), [])
        with self.assertRaises(ValueError):
            JargonCoverage({"": "empty"})
        with self.assertRaises(ValueError):
            JargonCoverage({"valid": "x", 2: "invalid"})

    def test_target_locale_is_selected_before_matching(self):
        data = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
            encoding="utf-8"))
        self.assertEqual(JargonCoverage(
            select_jargon(data, "fr-FR", "fr-FR")).hits("CDR"), [])
        with self.assertRaises(ValueError):
            select_jargon(data, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
