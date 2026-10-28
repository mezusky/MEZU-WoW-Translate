"""Cross-class Wowhead primary-stat terminology (source-only regression).

The "Main Stat (Item Level)" label occurs on independent Midnight basics
pages (Windwalker, Survival, Arcane, Destruction). "mainstat" also occurs
in Vengeance DH consumables and gear prose. These are not spell/item IDs.
The browser Translator API and rich-text reconstruction are NOT exercised.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

PLAYER = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class MainStatCrossClassTests(unittest.TestCase):
    def test_precise_french_terms(self):
        terms = select_jargon(PLAYER, "en-US", "fr-FR")
        self.assertEqual(terms["Main Stat (Item Level)"], "Stat principale (niveau d’objet)")
        self.assertEqual(terms["mainstat"], "stat principale")
        for term in ("Main Stat (Item Level)", "mainstat"):
            self.assertNotIn(term, MANUAL.get("jargon", {}))
            self.assertNotIn(term, MANUAL.get("exact", {}))
        # Do not replace isolated "stat", "main" or "item level" in names.
        for unsafe in ("stat", "main", "item level"):
            self.assertNotIn(unsafe, terms)

    def test_independent_source_and_heldout_pages(self):
        by_id = {p["id"]: p["url"] for p in PAGES}
        expected = {
            "windwalker-monk-basics": "/monk/windwalker/basics",
            "survival-hunter-basics": "/hunter/survival/basics",
            "arcane-mage-basics": "/mage/arcane/basics",
            "destruction-warlock-basics": "/warlock/destruction/basics",
            "vengeance-demon-hunter-gear": "/demon-hunter/vengeance/bis-gear",
            "guardian-druid-talent-builds-heldout": "/druid/guardian/talent-builds-pve-tank",
            "fire-mage-talent-builds-heldout": "/mage/fire/talent-builds-pve-dps",
            "restoration-druid-talent-builds-heldout": "/druid/restoration/talent-builds-pve-healer",
        }
        for page_id, suffix in expected.items():
            with self.subTest(page=page_id):
                self.assertEqual(by_id[page_id], "https://www.wowhead.com/guide/classes" + suffix)
        self.assertEqual(len(PAGES), len({p["id"] for p in PAGES}))
        self.assertEqual(len(PAGES), len({p["url"] for p in PAGES}))

    def test_language_isolation(self):
        self.assertEqual(select_jargon(PLAYER, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(PLAYER, "en", "de")


if __name__ == "__main__":
    unittest.main()
