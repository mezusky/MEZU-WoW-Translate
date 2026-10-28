"""Four independent held-out Wowhead guide sources across raid and season sections.

The pages are English-source canonical URLs; this test verifies only corpus
structure and never claims that Chrome Translator API or DOM rendering passed.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class HeldoutSeasonRaidCoverageTests(unittest.TestCase):
    def test_new_pages_and_sections(self):
        by_id = {page["id"]: page["url"] for page in PAGES}
        expected = {
            "survival-hunter-midnight-season-2": "/hunter/survival/midnight-season-2",
            "subtlety-rogue-midnight-season-2": "/rogue/subtlety/midnight-season-2",
            "enhancement-shaman-tier-set": "/shaman/enhancement/tier-set-bonuses",
            "frost-death-knight-manaforge-omega-raid": "/death-knight/frost/manaforge-omega-raid-tips",
        }
        for key, suffix in expected.items():
            with self.subTest(page=key):
                self.assertIn(key, by_id)
                self.assertEqual(by_id[key], "https://www.wowhead.com/guide/classes" + suffix)

    def test_no_duplicate_ids_or_urls(self):
        self.assertEqual(len(PAGES), len({p["id"] for p in PAGES}))
        self.assertEqual(len(PAGES), len({p["url"] for p in PAGES}))


if __name__ == "__main__":
    unittest.main()
