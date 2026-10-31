"""Source-only WoW idiom contract; not a browser translation assertion.

English Wowhead uses "fish for" for procs, critical hits and resets across
unrelated specs. Keep a reusable French phrase, not whole-guide overrides.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class FishForCrossSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_reusable_idiom_is_scoped_to_french_not_literal_fishing(self):
        terms = select_jargon(self.player, "en-US", "fr-FR")
        self.assertEqual(terms["fish for"], "chercher à obtenir")
        self.assertEqual(terms["Fish for"], "Chercher à obtenir")
        self.assertNotIn("fish", terms)
        self.assertNotIn("fishing", terms)
        self.assertNotIn("fish for", self.manual.get("jargon", {}))
        self.assertNotIn("fish for", self.manual.get("exact", {}))
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-CA"), {})

    def test_independent_source_guides_in_corpus(self):
        # Fire Mage: critical hits; Enhancement Shaman: Tempest procs;
        # Protection Warrior: Shield Slam resets; Subtlety Rogue: big hit.
        paths = (
            "mage/fire/abilities-talents-pve-dps",
            "shaman/enhancement/rotation-cooldowns-pve-dps",
            "warrior/protection/abilities-talents-pve-tank",
            "rogue/subtlety/overview-pve-dps",
        )
        urls = {page["url"] for page in self.pages}
        for path in paths:
            with self.subTest(path=path):
                self.assertIn("https://www.wowhead.com/guide/classes/" + path, urls)


if __name__ == "__main__":
    unittest.main()
