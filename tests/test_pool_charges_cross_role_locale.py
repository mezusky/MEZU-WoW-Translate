"""Source-only heldout for contextual charge pooling across healer and DPS guides.

Preservation Evoker (current), Restoration Shaman (legacy), and Enhancement
Shaman raid (legacy) independently use the same resource-management concept.
No browser Translator API, DOM, or live full-HTML verification is claimed.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class PoolChargesCrossRoleLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_contextual_pooling_not_generic_pool(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["pool your charges"], "conserver vos charges")
        self.assertEqual(terms["pool charges"], "conserver des charges")
        self.assertEqual(terms["pool charges of"], "conserver des charges de")
        for unsafe in ("pool", "pooling", "pool your", "mana pool"):
            self.assertNotIn(unsafe, {k for k in terms if k.startswith("pool ") or k == "pool"})
        for layer in ("exact", "jargon"):
            legacy = {key.casefold() for key in self.manual.get(layer, {})}
            for phrase in ("pool your charges", "pool charges", "pool charges of"):
                self.assertNotIn(phrase, legacy)

    def test_locale_isolation(self):
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en-US", "de-DE")

    def test_independent_source_pages_in_corpus(self):
        urls = [page["url"] for page in self.pages]
        self.assertEqual(len(urls), len(set(urls)))
        for suffix in (
            "evoker/preservation/rotation-cooldowns-pve-healer",
            "shaman/restoration/new-player-basics",
            "shaman/enhancement/nerub-ar-palace-raid-tips",
        ):
            with self.subTest(suffix=suffix):
                self.assertIn("https://www.wowhead.com/guide/classes/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
