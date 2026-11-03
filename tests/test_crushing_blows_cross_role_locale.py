"""Source-only Classic crushing-blow terminology; not a browser/DOM replay."""
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class CrushingBlowsCrossRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.terms = select_jargon(cls.player, "en-US", "fr-FR")

    def test_singular_plural_and_heading_case(self):
        expected = {
            "crushing blow": "coup écrasant",
            "crushing blows": "coups écrasants",
            "Crushing Blow": "Coup écrasant",
            "Crushing Blows": "Coups écrasants",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(self.terms[source], target)
        for ambiguous in ("crushing", "blow", "blows", "crushed",
                          "Shield Block", "Glancing", "Weapon Expertise"):
            self.assertNotIn(ambiguous, self.terms)

    def test_crushing_and_glancing_are_distinct_attack_table_concepts(self):
        hits = JargonCoverage(self.terms).hits(
            "Crushing Blows hit tanks; glancing blows affect white hits. "
            "A crushing blow is not a glancing blow.")
        self.assertEqual(hits, ["crushing blows", "glancing blows",
                                "white hits", "crushing blow", "glancing blow"])
        self.assertEqual(JargonCoverage(self.terms).hits("a crushing defeat"), [])

    def test_no_manual_duplicates_or_wrong_locale_leakage(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("exact", "jargon"):
            for alias in ("crushing blow", "crushing blows",
                          "Crushing Blow", "Crushing Blows"):
                self.assertNotIn(alias, manual.get(layer, {}))
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")

    def test_independent_sources_and_dom_holdout_in_corpus(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {page["url"] for page in corpus["pages"]}
        for suffix in (
            "classic/guide/classes/warrior/tank-rotation-cooldowns-abilities-pve",
            "classic/guide/classic-wow-stats-and-attributes-overview",
            "classic/guide/classes/druid/feral/tank-overview-pve",
            "classic/guide/season-of-discovery/classes/druid/tank-overview",
        ):
            self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
