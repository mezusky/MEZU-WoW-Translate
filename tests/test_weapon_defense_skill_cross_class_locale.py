"""Source-only cross-role terminology for Classic weapon/defense skills.

This verifies data-layer contracts, not Chrome Translator API or rendered DOM.
"""
import unittest
from pathlib import Path

from scripts.jargon_coverage import JargonCoverage
from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class WeaponDefenseSkillCrossClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.terms = select_jargon(cls.player, "en-US", "fr-FR")

    def test_shared_stat_names_singular_plural_and_case(self):
        expected = {
            "weapon skill": "compétence d’arme",
            "Weapon Skill": "Compétence d’arme",
            "weapon skills": "compétences d’arme",
            "Weapon Skills": "Compétences d’arme",
            "defense skill": "compétence de défense",
            "Defense Skill": "Compétence de défense",
            "defense skills": "compétences de défense",
            "Defense Skills": "Compétences de défense",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(self.terms[source], target)
        # Skill is a mechanic, not an alias for the different rating stats.
        for broad in ("skill", "skills", "weapon", "defense",
                      "defense rating", "weapon expertise", "weapon damage"):
            self.assertNotIn(broad, self.terms)

    def test_independent_stat_phrases_and_no_partial_word_match(self):
        hits = JargonCoverage(self.terms).hits(
            "Weapon Skill versus Defense Skill; weapon skills and defense skills.")
        self.assertIn("weapon skill", hits)
        self.assertIn("defense skill", hits)
        self.assertIn("weapon skills", hits)
        self.assertIn("defense skills", hits)
        self.assertEqual(JargonCoverage(self.terms).hits("skillful weaponry"), [])

    def test_no_manual_sentence_overrides_and_locale_isolation(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for source in ("weapon skill", "Weapon Skill", "weapon skills",
                       "Weapon Skills", "defense skill", "Defense Skill",
                       "defense skills", "Defense Skills"):
            for layer in ("exact", "jargon"):
                self.assertNotIn(source, manual.get(layer, {}))
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")

    def test_independent_classes_and_sections_in_regression_corpus(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {page["url"] for page in corpus["pages"]}
        for suffix in (
            "classic/guide/classes/warrior/tank-stat-priority-attributes-pve",
            "classic/guide/classes/warrior/fury/dps-stat-priority-attributes-pve",
            "classic/guide/classes/rogue/dps-stat-priority-attributes-pve",
            "classic/guide/classes/hunter/dps-stat-priority-attributes-pve",
            "classic/guide/classes/shaman/enhancement/dps-stat-priority-attributes-pve",
            "classic/guide/classes/shaman/leveling-tips",
            "classic/guide/classic-wow-weapon-skills",
            "tbc/guide/classes/warrior/protection/tank-stat-priority-attributes-pve",
        ):
            with self.subTest(url=suffix):
                self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
