"""Shared pre-pull and opener timeline labels in independent Wowhead guides.

English source evidence (Oct 2026): Protection Paladin tank rotation,
Beast Mastery Hunter and Destruction Warlock DPS rotations, Augmentation
Evoker support rotation, and Devourer Demon Hunter rotation. This checks
French data rules only; it does not simulate Chrome Translator API or DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class PrepullTimelineLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {row["id"]: row["url"] for row in json.loads(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]}

    def test_scoped_wow_player_labels_and_specificity(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "Pre-pull": "avant le pull",
            "pre-pull": "avant le pull",
            "Sample Timeline": "Exemple de timeline",
            "sample timeline": "exemple de timeline",
            "ST Sample Timeline": "Exemple de timeline monocible",
            "AoE Sample Timeline": "Exemple de timeline AoE",
            "AOE Sample Timeline": "Exemple de timeline AoE",
        }
        for source, french in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], french)
                self.assertNotIn(source, self.manual.get("exact", {}))
        # These are guide labels, not an invitation to translate unrelated
        # words or alter existing technical timeline/import strings.
        for generic in ("pre", "timeline", "sample", "pulling"):
            self.assertNotIn(generic, jargon)

    def test_independent_role_and_section_samples(self):
        for page_id in (
            "protection-paladin-rotation", "beast-mastery-hunter-rotation",
            "destruction-warlock-rotation", "augmentation-evoker-rotation",
            "devourer-demon-hunter-rotation",
        ):
            with self.subTest(page=page_id):
                self.assertIn(page_id, self.pages)
                self.assertIn("/rotation-cooldowns-pve-", self.pages[page_id])

    def test_locale_direction_does_not_leak(self):
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-FR"), {})
        self.assertEqual(select_jargon(self.player, "en-GB", "en-US"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
