"""Regression corpus structure and cross-role/section representation (offline)."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class WowheadRegressionCorpusTests(unittest.TestCase):
    def test_unique_ids_and_urls(self):
        self.assertEqual(len({p["id"] for p in PAGES}), len(PAGES))
        self.assertEqual(len({p["url"] for p in PAGES}), len(PAGES))

    def test_canonical_english_source_urls(self):
        for page in PAGES:
            with self.subTest(page=page["id"]):
                parsed = urlparse(page["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "www.wowhead.com")
                self.assertIn("/guide/classes/", parsed.path)
                self.assertFalse(parsed.query or parsed.fragment)

    def test_cross_class_and_section_coverage(self):
        paths = [urlparse(p["url"]).path.split("/guide/classes/", 1)[1].split("/")
                 for p in PAGES]
        classes = {parts[0] for parts in paths}
        sections = [parts[2] for parts in paths if len(parts) >= 3]
        self.assertGreaterEqual(len(classes), 13)
        for pattern in ("overview", "rotation", "abilities-talents", "stat-priority",
                        "bis-gear", "enchants-gems", "mythic-plus", "raid-tips",
                        "tier-set-bonuses"):
            with self.subTest(section=pattern):
                self.assertTrue(any(pattern in section for section in sections))


    def test_tier_set_guides_cover_independent_classes(self):
        # A shared terminology rule must not be validated on one spec alone.
        tier_classes = {
            urlparse(page["url"]).path.split("/guide/classes/", 1)[1].split("/")[0]
            for page in PAGES if "/tier-set-bonuses" in page["url"]
        }
        self.assertGreaterEqual(len(tier_classes), 6)


    def test_crafting_gear_guides_cover_independent_classes(self):
        # Reusable off-hand / embellishment / crafting-order wording is
        # sampled on four unrelated classes rather than one author's guide.
        required = {
            "discipline-priest-gear",
            "preservation-evoker-gear",
            "fire-mage-gear",
            "demonology-warlock-gear",
        }
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))


    def test_talent_import_guides_cover_independent_classes(self):
        # Talent import widgets are structurally different from ability listings.
        classes = {
            urlparse(page["url"]).path.split("/guide/classes/", 1)[1].split("/")[0]
            for page in PAGES if "/talent-builds-pve-" in page["url"]
        }
        self.assertGreaterEqual(len(classes), 4)


    def test_raid_guides_cover_tank_healer_and_dps(self):
        # Validate independent role coverage before generalizing raid terminology.
        required = {
            "protection-warrior-raid",  # tank
            "holy-priest-raid",         # healer
            "unholy-death-knight-raid", # damage dealer
        }
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))


    def test_proc_heading_samples_span_independent_dps_classes(self):
        # Same source phrase occurs across Shaman, Warlock, Hunter and Rogue.
        # Source-only coverage is not browser translation verification.
        required = {
            "elemental-shaman-overview",
            "affliction-warlock-rotation",
            "marksmanship-hunter-overview",
            "outlaw-rogue-overview",
        }
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))



if __name__ == "__main__":
    unittest.main()
