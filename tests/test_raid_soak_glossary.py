"""Cross-role Wowhead raid-soak noun phrases; source-only, not Chrome replay."""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class RaidSoakGlossaryTests(unittest.TestCase):
    def test_locale_scoped_noun_phrases(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        expected = {
            "soak mechanic": "mécanique de soak",
            "soak mechanics": "mécaniques de soak",
            "group soak": "soak de groupe",
            "group soaks": "soaks de groupe",
        }
        for phrase, translation in expected.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(jargon[phrase], translation)
                self.assertNotIn(phrase, MANUAL.get("exact", {}))
                self.assertNotIn(phrase, MANUAL.get("jargon", {}))
        # Bare 'soak' may be a verb, noun or mechanic; leave it contextual.
        self.assertNotIn("soak", jargon)
        self.assertNotIn("soaking", jargon)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_independent_raid_guides(self):
        fixtures = {
            "assassination-rogue-raid": "The other boss has a soak mechanic",
            "devastation-evoker-raid": "Mighty Thud creates multiple group soaks",
        }
        ids = {page["id"] for page in PAGES}
        jargon = select_jargon(GLOSSARY, "en", "fr")
        for guide, excerpt in fixtures.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertTrue(any(phrase in excerpt.casefold() for phrase in jargon if "soak" in phrase))
        # Holy Priest is an independent healer page, not an exception to the rule.
        self.assertIn("holy-priest-raid", ids)


if __name__ == "__main__":
    unittest.main()
