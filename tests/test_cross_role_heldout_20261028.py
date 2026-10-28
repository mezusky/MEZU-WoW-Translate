"""Offline regression guard for independently indexed 2026-10-28 Wowhead sources.

These assertions do not claim the browser Translator API or DOM was tested.
The source pages were inspected through assistant web indexing because direct
Wowhead HTML returned a JavaScript verification challenge.
"""
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


class CrossRoleHeldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))

    def test_independent_role_and_section_samples(self):
        expected = {
            "protection-warrior-stats-heldout": "warrior/protection/stat-priority-pve-tank",
            "vengeance-demon-hunter-consumables-heldout": "demon-hunter/vengeance/enchants-gems-pve-tank",
            "augmentation-evoker-gear-heldout": "evoker/augmentation/bis-gear",
            "beast-mastery-hunter-overview-heldout": "hunter/beast-mastery/overview-pve-dps",
        }
        indexed = {p["id"]: p["url"] for p in self.pages}
        for page_id, suffix in expected.items():
            with self.subTest(page_id=page_id):
                self.assertIn(page_id, indexed)
                self.assertTrue(indexed[page_id].endswith(suffix))
        self.assertEqual(len({p["url"] for p in self.pages}), len(self.pages))

    def test_do_not_overgeneralize_clipping_or_chaining(self):
        # Evoker Disintegrate and Mage Arcane Missiles discuss channel
        # clipping; Hunter Wing Clip is an official spell name. Bare
        # "clip"/"chain" rewrites could corrupt canonical names and prose.
        for unsafe in ("clip", "Clip", "clipping", "Clipping",
                       "chain", "Chain", "chaining", "Chaining",
                       "Wing Clip"):
            with self.subTest(term=unsafe):
                self.assertNotIn(unsafe, self.player["jargon"])
                self.assertNotIn(unsafe, self.manual.get("jargon", {}))

    def test_player_jargon_remains_locale_scoped(self):
        self.assertEqual(self.player["sourceLanguage"], "en")
        self.assertEqual(self.player["targetLanguage"], "fr")


if __name__ == "__main__":
    unittest.main()
