"""Cross-class off-GCD wording in live English Wowhead guides.

Source-only evidence: Enhancement Shaman rotation (prose and opener),
Balance Druid rotation (opener widget labels), and Holy Priest talents.
This checks the locale data contract, not Chrome DOM/Translator API output.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class OffGCDLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {
            page["id"]: page["url"]
            for page in json.loads(
                (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
            )["pages"]
        }

    def test_off_gcd_variants_are_scoped_to_french(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "off-GCD": "hors GCD",
            "Off-GCD": "Hors GCD",
            "off-gcd": "hors GCD",
            "off GCD": "hors GCD",
            "off the GCD": "hors GCD",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("exact", {}))
                self.assertNotIn(source, self.manual.get("jargon", {}))
        # Do not conflate an ability being available (off cooldown) with
        # an ability being outside the global cooldown.
        for ambiguous in ("off cooldown", "on cooldown", "off", "GCD"):
            self.assertNotIn(ambiguous, jargon)

    def test_heldout_classes_and_locale_isolation(self):
        for page_id in (
            "enhancement-shaman-rotation", "balance-druid-rotation",
            "holy-priest-abilities",
        ):
            with self.subTest(page=page_id):
                self.assertIn(page_id, self.pages)
                self.assertIn("/guide/classes/", self.pages[page_id])
        self.assertEqual(select_jargon(self.player, "fr", "fr"), {})
        self.assertEqual(select_jargon(self.player, "en-US", "en-GB"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de", "fr")


if __name__ == "__main__":
    unittest.main()
