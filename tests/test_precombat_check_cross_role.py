"""Reusable pre-combat checklist headings in independent Midnight Wowhead guides.

Source-only evidence: Brewmaster Monk and Blood DK tank rotations, Guardian
Druid rotation, and Survival Hunter DPS rotation (October 2026).
This validates the EN->FR data layer, not Chrome Translator API output.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class PreCombatChecklistLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {
            p["id"]: p["url"]
            for p in json.loads(
                (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
            )["pages"]
        }

    def test_heading_variants_use_natural_french_without_sentence_overrides(self):
        expected = {
            "Pre-Combat Check": "Vérification avant le combat",
            "Pre-Combat Checks": "Vérifications avant le combat",
            "pre-combat check": "vérification avant le combat",
            "pre-combat checks": "vérifications avant le combat",
        }
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("exact", {}))
                self.assertNotIn(source, self.manual.get("jargon", {}))
        # Avoid generic "check" overrides; keep existing unrelated usage.
        self.assertNotIn("check", jargon)

    def test_independent_roles_and_locale_isolation(self):
        for page_id in (
            "brewmaster-monk-rotation", "blood-death-knight-rotation",
            "guardian-druid-rotation", "survival-hunter-rotation",
        ):
            with self.subTest(page=page_id):
                self.assertIn(page_id, self.pages)
                self.assertIn("/rotation-cooldowns-pve-", self.pages[page_id])
        self.assertEqual(select_jargon(self.player, "fr", "fr"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de", "fr")


if __name__ == "__main__":
    unittest.main()
