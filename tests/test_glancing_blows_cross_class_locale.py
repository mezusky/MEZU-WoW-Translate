"""Source-only Classic glancing-blow terminology; not a browser translation test."""
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class GlancingBlowsCrossClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.terms = select_jargon(cls.player, "en-US", "fr-FR")

    def test_singular_plural_and_heading_case(self):
        expected = {
            "glancing blow": "coup éraflé",
            "glancing blows": "coups éraflés",
            "Glancing Blow": "Coup éraflé",
            "Glancing Blows": "Coups éraflés",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(self.terms[source], target)
        for ambiguous in ("glance", "glancing", "blow", "blows",
                          "weapon skillful"):
            self.assertNotIn(ambiguous, self.terms)

    def test_longest_phrase_and_distinct_white_hits(self):
        hits = JargonCoverage(self.terms).hits(
            "Glancing Blows reduce damage on white hits; a glancing blow cannot crit.")
        self.assertIn("glancing blows", hits)
        self.assertIn("white hits", hits)
        self.assertIn("glancing blow", hits)
        self.assertEqual(len(hits), 3)
        self.assertEqual(JargonCoverage(self.terms).hits("a quick glance"), [])

    def test_no_legacy_overrides_or_other_locale_leakage(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("exact", "jargon"):
            for alias in ("glancing blow", "glancing blows",
                          "Glancing Blow", "Glancing Blows"):
                self.assertNotIn(alias, manual.get(layer, {}))
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")

    def test_independent_rogue_and_warrior_guides_plus_feral_control(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {page["url"] for page in corpus["pages"]}
        for suffix in (
            "classic/guide/classes/rogue/dps-stat-priority-attributes-pve",
            "classic/guide/classes/warrior/fury/dps-stat-priority-attributes-pve",
            "classic/guide/classes/warrior/tank-stat-priority-attributes-pve",
            "classic/guide/classes/druid/feral/dps-stat-priority-attributes-pve",
        ):
            self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
