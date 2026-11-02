"""Parry-haste WoW jargon across Forever, SoD and TBC tank guides.

These are source-only data/locale checks, not a Chrome Translator API or DOM
rendering test. The noun is protected as player jargon; verb forms are not
forced through a potentially ungrammatical global replacement.
"""
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class ParryHasteCrossTankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.terms = select_jargon(cls.player, "en-US", "fr-FR")

    def test_player_jargon_is_preserved_not_literally_translated(self):
        expected = {
            "parry haste": "parry haste",
            "Parry haste": "Parry haste",
            "Parry Haste": "Parry Haste",
            "parry-haste": "parry haste",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(self.terms[source], target)
        # Avoid colliding with generic stats or official ability names.
        for generic in ("parry", "haste", "Parry", "Haste",
                        "Shield Block", "Expertise", "parry-hasting"):
            self.assertNotIn(generic, self.terms)

    def test_cross_guide_nouns_and_negative_controls(self):
        coverage = JargonCoverage(self.terms)
        self.assertEqual(
            coverage.hits("Parry haste speeds the next swing; avoid parry-haste."),
            ["parry haste", "parry-haste"])
        self.assertEqual(
            coverage.hits("Parry haste can occur when a boss parries attacks."),
            ["parry haste"])
        self.assertEqual(coverage.hits(
            "Parry and haste are separate stats. Parry-hasting is a verb."), [])

    def test_no_manual_duplication_or_wrong_locale(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("jargon", "exact"):
            for term in ("parry haste", "Parry haste", "Parry Haste",
                         "parry-haste"):
                self.assertNotIn(term, manual.get(layer, {}))
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")

    def test_independent_sources_and_role_controls_are_in_corpus(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {page["url"] for page in corpus["pages"]}
        for suffix in (
            "forever/guide/classes/paladin/protection/stat-priority-pve-tank",
            "classic/guide/season-of-discovery/classes/warrior/tank-overview",
            "tbc/guide/classes/paladin/tank-stat-priority-attributes-pve",
            "tbc/guide/classes/warrior/protection/tank-stat-priority-attributes-pve",
            "tbc/guide/classes/rogue/dps-stat-priority-attributes-pve",
            "forever/guide/classes/priest/holy/rotation-cooldowns-pve-healer",
            "forever/guide/classes/mage/frost/rotation-cooldowns-pve-dps",
        ):
            self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
