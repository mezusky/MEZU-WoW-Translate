"""Regression tests for class-specific coverage in the deterministic sampler."""
import unittest

from scripts.sample_wowhead_regression import dimensions, sample


class SamplerTests(unittest.TestCase):
    def test_class_spec_is_not_shared_across_classes(self):
        warrior = {"id": "warrior", "url": "https://www.wowhead.com/guide/classes/warrior/protection/rotation-cooldowns-pve-tank"}
        paladin = {"id": "paladin", "url": "https://www.wowhead.com/guide/classes/paladin/protection/rotation-cooldowns-pve-tank"}
        self.assertNotEqual(dimensions(warrior)["classSpec"], dimensions(paladin)["classSpec"])

    def test_edition_uses_path_not_host_or_guide_segment(self):
        retail = {"url": "https://www.wowhead.com/guide/classes/mage/frost/overview-pve-dps"}
        classic = {"url": "https://www.wowhead.com/classic/guide/classes/mage/frost/overview-pve-dps?x=1"}
        self.assertEqual(dimensions(retail)["edition"], "retail")
        self.assertEqual(dimensions(classic)["edition"], "classic")
        self.assertEqual(dimensions(classic)["classSpec"], "mage/frost")

    def test_midnight_season_guides_have_distinct_sections(self):
        raid = {"url": "https://www.wowhead.com/guide/classes/priest/holy/midnight-season-2-raid-tips"}
        overview = {"url": "https://www.wowhead.com/guide/classes/shaman/enhancement/midnight-season-2"}
        self.assertEqual(dimensions(raid)["section"], "raid")
        self.assertEqual(dimensions(overview)["section"], "overview")

    def test_duplicate_urls_do_not_consume_audit_slots(self):
        url = "https://www.wowhead.com/guide/classes/mage/frost/overview-pve-dps"
        other = "https://www.wowhead.com/guide/classes/priest/holy/rotation-cooldowns-pve-healer"
        pages = [{"id": "a", "url": url}, {"id": "duplicate", "url": url}, {"id": "b", "url": other}]
        selected = sample(pages, count=3, cycle="duplicate-test")
        self.assertEqual(len(selected), 2)
        self.assertEqual({p["url"] for p in selected}, {url, other})

    def test_deterministic_and_unique(self):
        pages = [
            {"id": str(i), "url": "https://www.wowhead.com/guide/classes/" + klass + "/" + spec + "/" + section}
            for i, (klass, spec, section) in enumerate([
                ("warrior", "protection", "rotation-cooldowns-pve-tank"),
                ("paladin", "protection", "rotation-cooldowns-pve-tank"),
                ("priest", "holy", "overview-pve-healer"),
                ("mage", "frost", "stat-priority-pve-dps"),
            ])
        ]
        result = sample(pages, count=4, cycle="2026-11-18")
        self.assertEqual(result, sample(pages, count=4, cycle="2026-11-18"))
        self.assertEqual(len({page["id"] for page in result}), 4)


if __name__ == "__main__":
    unittest.main()
