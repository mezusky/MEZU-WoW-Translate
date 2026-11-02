"""Source-only cross-class white-hit terminology, not browser translation evidence."""
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class WhiteHitsCrossClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.terms = select_jargon(cls.player, "en-US", "fr-FR")

    def test_white_hits_are_auto_attack_jargon_not_color(self):
        expected = {
            "white hit": "coup blanc",
            "white hits": "coups blancs",
            "white auto attacks": "coups blancs",
            "White Auto Attacks": "Coups blancs",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(self.terms[source], target)
        for ambiguous in ("white", "hits", "clip", "clipping", "Auto Shot"):
            self.assertNotIn(ambiguous, self.terms)

    def test_longest_match_prevents_duplicate_auto_attack_count(self):
        matcher = JargonCoverage(self.terms)
        hits = matcher.hits("White Auto Attacks and white hits can glance.")
        self.assertEqual(hits, ["White Auto Attacks", "white hits"])
        self.assertNotIn("auto attacks", hits)

    def test_locale_and_legacy_override_boundaries(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("exact", "jargon"):
            for term in ("white hit", "white hits", "white auto attacks",
                         "White Auto Attacks"):
                self.assertNotIn(term, manual.get(layer, {}))
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")

    def test_independent_shaman_and_rogue_sources_plus_hunter_control(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {page["url"] for page in corpus["pages"]}
        for suffix in (
            "wotlk/guide/classes/shaman/enhancement/dps-rotation-cooldowns-abilities-pve",
            "wotlk/guide/classes/shaman/enhancement/dps-leveling-tips",
            "classic/guide/classes/rogue/dps-stat-priority-attributes-pve",
            "classic/guide/classes/hunter/dps-stat-priority-attributes-pve",
        ):
            self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
