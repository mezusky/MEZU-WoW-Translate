"""Regression corpus structure and cross-role/section representation (offline)."""
import json
import re
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
                # A localized /fr/guide/... URL may still contain English prose
                # but localizes spell links, so it is NOT an English-source URL.
                # The English PTR preview uses /ptr-2/guide/... instead.
                self.assertRegex(parsed.path,
                                 r"^/(?:ptr(?:-\\d+)?/)?guide/classes/[a-z-]+/[a-z-]+/[a-z0-9-]+$")
                self.assertFalse(parsed.query or parsed.fragment)

    def test_localized_url_is_not_an_english_source(self):
        pattern = r"^/(?:ptr(?:-\\d+)?/)?guide/classes/[a-z-]+/[a-z-]+/[a-z0-9-]+$"
        for locale in ("fr", "de", "it", "pt", "cn"):
            with self.subTest(locale=locale):
                self.assertIsNone(re.fullmatch(pattern,
                    f"/{locale}/guide/classes/priest/discipline/rotation-cooldowns-pve-healer"))
        self.assertIsNotNone(re.fullmatch(pattern,
            "/ptr-2/guide/classes/shaman/enhancement/midnight-season-2-raid-tips"))

    def test_new_independent_guides_cover_id_names_and_widgets(self):
        required = {
            "blood-death-knight-overview",  # tank; Runic Power and linked spells
            "demonology-warlock-consumables",  # DPS; item/enchant names
            "survival-hunter-talent-builds",  # DPS; talent copy/import widgets
        }
        self.assertTrue(required.issubset({page["id"] for page in PAGES}))

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



    def test_raidwide_effects_sample_independent_roles(self):
        # English source coverage only; no assertion about Chrome output.
        required = {
            "preservation-evoker-raid",  # healer
            "restoration-druid-raid",   # healer, unrelated class
            "havoc-demon-hunter-raid",  # DPS
        }
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))

    def test_ui_macro_guides_span_tank_healer_and_dps(self):
        # New Midnight UI pages contain import strings and /cast macros.
        # Those are non-prose payloads, not translation training material.
        required = {
            "protection-warrior-ui-macros",   # tank
            "preservation-evoker-ui-macros", # healer
            "fire-mage-ui-macros",           # ranged DPS
            "protection-paladin-ui-macros", # independent tank class
            "restoration-druid-ui-macros",  # independent healer class
            "outlaw-rogue-ui-macros",       # melee DPS
        }
        pages = {page["id"]: page["url"] for page in PAGES}
        self.assertTrue(required.issubset(pages))
        for page_id in required:
            with self.subTest(page=page_id):
                self.assertTrue(pages[page_id].endswith("/addons-macro-ui-imports"))

    def test_unholy_and_blood_dk_stats_are_independent_samples(self):
        # Identical numerical threshold sections must remain comparable
        # across two specs; no browser translation claim.
        required = {"unholy-death-knight-stats", "blood-death-knight-stats"}
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))


    def test_raid_damage_spelling_samples_span_healer_classes(self):
        # Indexed English sources: Evoker uses raidwide, Shaman raid-wide,
        # and Holy/Discipline Priest use raid wide. No browser output claim.
        required = {
            "preservation-evoker-raid",
            "restoration-shaman-raid",
            "holy-priest-raid",
            "discipline-priest-raid",
        }
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))

    def test_new_tank_stats_and_melee_consumables_are_independent(self):
        # Numeric threshold prose and official item IDs are separate risks.
        required = {"vengeance-demon-hunter-stats", "subtlety-rogue-consumables"}
        self.assertTrue(required.issubset({p["id"] for p in PAGES}))


if __name__ == "__main__":
    unittest.main()
