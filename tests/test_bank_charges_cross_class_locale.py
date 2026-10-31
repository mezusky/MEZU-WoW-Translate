"""Source-only cross-class contract for storing charges before a cooldown.

Fire Mage leveling banks Fire Blast charges for Combustion; Demonology
Warlock rotation banks Demonic Core charges for Tyrant windows. This does
not assert that Chrome's Translator API or rich-text rendering was tested.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class BankChargesCrossClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_wo_w_resource_phrase_without_unsafe_generic_bank(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["bank charges"], "garder des charges en réserve")
        self.assertEqual(terms["bank charges of"], "conserver des charges de")
        for unsafe in ("bank", "banking", "bank charges for"):
            self.assertNotIn(unsafe, terms)
        for layer in ("jargon", "exact"):
            legacy = {key.casefold() for key in self.manual.get(layer, {})}
            self.assertNotIn("bank charges", legacy)
            self.assertNotIn("bank charges of", legacy)

    def test_locale_isolation_and_cross_class_sources(self):
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en-US", "de-DE")
        urls = {page["url"] for page in self.pages}
        for path in (
            "mage/fire/dps-leveling-tips",
            "warlock/demonology/rotation-cooldowns-pve-dps",
        ):
            with self.subTest(path=path):
                self.assertIn("https://www.wowhead.com/guide/classes/" + path, urls)


if __name__ == "__main__":
    unittest.main()
