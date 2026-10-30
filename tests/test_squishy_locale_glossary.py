"""Durability jargon is reusable French locale data, not guide-specific prose.

Indexed Wowhead evidence: Holy Paladin and Restoration Druid rotations,
Protection Paladin Season 2, and cross-role tank raid rankings.
These are glossary assertions, NOT browser-rendered translation evidence.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
TERMS = {
    "squishy": "fragile",
    "Squishy": "Fragile",
    "squishy targets": "cibles fragiles",
}


class SquishyLocaleTests(unittest.TestCase):
    def test_reusable_terms_belong_to_french_locale(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(glossary, "en-US", "fr-FR")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for source, target in TERMS.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
                self.assertNotIn(source, manual.get("jargon", {}))
                self.assertNotIn(source, manual.get("exact", {}))

    def test_other_translation_directions_do_not_inherit_french_terms(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-CA"), {})
        self.assertEqual(select_jargon(glossary, "en-GB", "en-US"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "de-DE")
        with self.assertRaises(ValueError):
            select_jargon(glossary, "de-DE", "fr-FR")

    def test_heldout_guides_are_distinct_and_representative(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        urls = [p["url"] for p in pages]
        ids = [p["id"] for p in pages]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(len(ids), len(set(ids)))
        for path in (
            "paladin/holy/rotation-cooldowns-pve-healer",
            "druid/restoration/rotation-cooldowns-pve-healer",
            "paladin/protection/midnight-season-2",
            "druid/feral/midnight-season-2",
            "warrior/arms/midnight-season-2",
            "death-knight/frost/cheat-sheet",
        ):
            with self.subTest(path=path):
                self.assertIn("https://www.wowhead.com/guide/classes/" + path, urls)


if __name__ == "__main__":
    unittest.main()
