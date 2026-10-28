"""Official nominal overhealing wording, scoped to EN->FR without broad verb rules.

Blizzard EN/FR pre-expansion notes 24246298 pair "overhealing" with
"surplus de soins". Independent Holy and Discipline Priest Wowhead
abilities guides use the noun, while Mistweaver/Paladin/Resto Druid
guides also expose verbal forms that must NOT be blanket-rewritten.
Source-only checks; no Chrome Translator API or DOM verification.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class OverhealingLocaleTests(unittest.TestCase):
    def test_blizzard_attested_noun_and_existing_player_short_form(self):
        expected = {
            "overhealing": "surplus de soins",
            "Overhealing": "Surplus de soins",
            "overheal": "overheal",
            "Overheal": "Overheal",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_no_overbroad_verbal_rules(self):
        for source in ("overheals", "overhealed", "overhealing done to injured allies"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_locale_direction_and_same_language_skip(self):
        self.assertEqual(select_jargon(GLOSSARY, "en-US", "fr-FR")["overhealing"], "surplus de soins")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")

    def test_independent_healer_sources_and_unique_corpus(self):
        by_id = {p["id"]: p["url"] for p in PAGES}
        for spec in ("holy-priest-abilities", "discipline-priest-abilities",
                     "mistweaver-monk-overview", "restoration-druid-abilities",
                     "restoration-shaman-abilities", "holy-paladin-abilities"):
            with self.subTest(spec=spec):
                self.assertIn(spec, by_id)
                self.assertTrue(by_id[spec].startswith("https://www.wowhead.com/guide/classes/"))
        self.assertEqual(len(PAGES), len(by_id))
        self.assertEqual(len(PAGES), len({p["url"] for p in PAGES}))


if __name__ == "__main__":
    unittest.main()
