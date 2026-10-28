"""Conservative LoS noun collocations across tank, healer and DPS guides.

Indexed English Wowhead source (not translated browser output):
- Frost Mage M+ uses "breaking line of sight" and "break line of sight".
- Fire Mage M+ uses "out of Line of Sight".
- Discipline Priest M+ discusses line of sight as both a noun and a verb.
- Brewmaster Monk tank guides use LOS as a gameplay verb.
Only unambiguous collocations are normalized; a generic "line of sight"
replacement would corrupt verbal usages such as "line of sight the cast".
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


class LineOfSightCrossRoleTests(unittest.TestCase):
    def test_only_attested_unambiguous_collocations(self):
        expected = {
            "break line of sight": "casser la ligne de vue",
            "out of line of sight": "hors de la ligne de vue",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_ambiguous_verbal_uses_not_rewritten(self):
        for source in ("line of sight", "Line of Sight", "LOS", "LoS",
                       "line-of-sight", "line of sighting", "line-of-sighting"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_independent_existing_guides(self):
        ids = {p["id"] for p in PAGES}
        self.assertTrue({
            "frost-mage-mythic-plus", "fire-mage-mythic-plus",
            "discipline-priest-mythic-plus", "brewmaster-monk-mythic-plus"
        }.issubset(ids))

    def test_locale_isolation(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["break line of sight"], "casser la ligne de vue")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")


if __name__ == "__main__":
    unittest.main()
