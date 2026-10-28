"""Existing French jargon reused on three unrelated raid-role holdouts.

Source excerpts are indexed English Wowhead text. This does not exercise
browser translation, ID-backed names, or rich-text reconstruction.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon


class RaidCrossRoleReuseTests(unittest.TestCase):
    def test_existing_terms_cover_source_risks(self):
        player = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(player, "en-US", "fr-FR")
        for source, target in {
            "priority target damage": "dégâts sur la cible prioritaire",
            "tier set": "set de classe",
            "healing absorb": "absorption de soins",
            "single-target damage": "dégâts monocibles",
        }.items():
            with self.subTest(term=source):
                self.assertEqual(terms[source], target)
        self.assertEqual(select_jargon(player, "fr", "fr"), {})

    def test_independent_raid_holdouts(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        by_id = {page["id"]: page["url"] for page in pages}
        for page_id, suffix in {
            "brewmaster-monk-manaforge-omega-raid-heldout": "/monk/brewmaster/manaforge-omega-raid-tips",
            "preservation-evoker-manaforge-omega-raid-heldout": "/evoker/preservation/manaforge-omega-raid-tips",
            "arcane-mage-manaforge-omega-raid-heldout": "/mage/arcane/manaforge-omega-raid-tips",
        }.items():
            with self.subTest(page=page_id):
                self.assertEqual(by_id[page_id], "https://www.wowhead.com/guide/classes" + suffix)
        self.assertEqual(len(pages), len({page["id"] for page in pages}))
        self.assertEqual(len(pages), len({page["url"] for page in pages}))


if __name__ == "__main__":
    unittest.main()
