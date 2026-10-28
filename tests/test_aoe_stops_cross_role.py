"""Locale-scoped AoE stop jargon across unrelated Midnight Mythic+ guides.

Indexed English source: Marksmanship Hunter, Demonology Warlock and Holy
Paladin Mythic+ guides use "AoE stops" for CC that prevents enemy casts.
The verb "stop" and other uses of "stops" must not be globally rewritten.
This tests data and source-corpus coverage, not browser Translator API output.
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


class AoeStopsCrossRoleTests(unittest.TestCase):
    def test_attested_plural_noun_variants(self):
        for source, target in {
            "AoE stops": "stops AoE",
            "aoe stops": "stops AoE",
            "AoE Stops": "Stops AoE",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_do_not_rewrite_ambiguous_verbs(self):
        for source in ("stop", "stops", "stopped", "stopping", "AoE stop", "Stop"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_cross_role_heldout_coverage(self):
        ids = {page["id"] for page in PAGES}
        self.assertTrue({
            "marksmanship-hunter-mythic-plus",
            "demonology-warlock-mythic-plus",
            "holy-paladin-mythic-plus",
        }.issubset(ids))

    def test_locale_pair_isolation(self):
        selected = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(selected["AoE stops"], "stops AoE")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")


if __name__ == "__main__":
    unittest.main()
