"""Fixed Wowhead guide sections must not be claimed by invented URL suffixes.

This is an audit identity test, not evidence of Chrome-rendered translation.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_trend import _canonical_guide_url, _case_matches_guide_identity


def matches(wow_class, spec, role, slug, section):
    url = f"https://www.wowhead.com/guide/classes/{wow_class}/{spec}/{slug}"
    case = {"wowClass": wow_class, "spec": spec, "role": role, "section": section}
    return _case_matches_guide_identity(case, _canonical_guide_url(url))


class FixedSectionIdentityTests(unittest.TestCase):
    def test_valid_guides_across_roles_and_sections(self):
        for cls, spec, role, slug, section in (
            ("warrior", "protection", "tank", "rotation-cooldowns-pve-tank", "rotation"),
            ("priest", "discipline", "healer", "enchants-gems-pve-healer", "consumables"),
            ("rogue", "assassination", "dps", "abilities-talents-pve-dps", "abilities"),
            ("druid", "restoration", "healer", "mythic-plus-dungeon-tips", "mythic-plus"),
            ("mage", "fire", "dps", "addons-macro-ui-imports", "macros"),
            ("shaman", "elemental", "dps", "manaforge-omega-raid-tips", "raid"),
            ("monk", "brewmaster", "tank", "tank-leveling-tips", "leveling"),
        ):
            with self.subTest(slug=slug):
                self.assertTrue(matches(cls, spec, role, slug, section))

    def test_arbitrary_suffixes_cannot_claim_browser_coverage(self):
        for slug, section in (
            ("mythic-plus-dungeon-tips-extra", "mythic-plus"),
            ("mythic-keystones-and-dungeons-old", "mythic-plus"),
            ("addons-macro-ui-imports-copy", "macros"),
            ("manaforge-omega-raid-tips-fake", "raid"),
            ("tank-leveling-tips-2027", "leveling"),
            ("rotation-cooldowns-pve-tank-preview", "rotation"),
            ("talent-builds-pve-tank-archive", "talents"),
            ("stat-priority-pve-tank-v2", "stats"),
            ("enchants-gems-pve-tank-v2", "consumables"),
            ("overview-pve-tank-draft", "overview"),
        ):
            with self.subTest(slug=slug):
                self.assertFalse(matches("warrior", "protection", "tank", slug, section))

    def test_role_suffix_cannot_override_canonical_spec_role(self):
        self.assertFalse(matches("warrior", "protection", "tank",
                                 "rotation-cooldowns-pve-dps", "rotation"))


if __name__ == "__main__":
    unittest.main()
