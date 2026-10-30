"""Grounded Mage Tower source-guide slugs must keep role and section identity.

These are older English-source guides used as translation/DOM heldouts, not
claims about current Midnight gameplay or browser-rendered MEZU output.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_trend import _canonical_guide_url, _case_matches_guide_identity


class MageTowerGuideIdentityTests(unittest.TestCase):
    EXAMPLES = (
        ("warrior", "protection", "tank", "highlord-kruul"),
        ("paladin", "protection", "tank", "highlord-kruul"),
        ("monk", "brewmaster", "tank", "highlord-kruul"),
        ("priest", "holy", "healer", "lord-erdris-thorn"),
    )

    def test_real_cross_role_guides_have_one_grounded_section(self):
        for wow_class, spec, role, boss in self.EXAMPLES:
            with self.subTest(spec=spec):
                url = (f"https://www.wowhead.com/guide/classes/{wow_class}/"
                       f"{spec}/mage-tower-{role}-challenge-{boss}")
                case = {"wowClass": wow_class, "spec": spec,
                        "role": role, "section": "mage-tower"}
                self.assertTrue(_case_matches_guide_identity(case, _canonical_guide_url(url)))
                self.assertFalse(_case_matches_guide_identity(
                    {**case, "section": "raid"}, _canonical_guide_url(url)))
                self.assertFalse(_case_matches_guide_identity(
                    {**case, "role": "dps"}, _canonical_guide_url(url)))

    def test_mismatched_role_in_challenge_slug_fails_closed(self):
        url = ("https://www.wowhead.com/guide/classes/priest/holy/"
               "mage-tower-tank-challenge-highlord-kruul")
        case = {"wowClass": "priest", "spec": "holy",
                "role": "healer", "section": "mage-tower"}
        self.assertFalse(_case_matches_guide_identity(case, _canonical_guide_url(url)))

    def test_bare_or_extended_section_slugs_do_not_count(self):
        for slug in ("mage-tower", "mage-tower-tank-challenge",
                     "mage-tower-tank-challenge-highlord-kruul-extra",
                     "mage-tower-tank-challenge-unknown-boss",
                     "mage-tower-tank-challenge-highlord-kruul-extra/rotation"):
            with self.subTest(slug=slug):
                url = f"https://www.wowhead.com/guide/classes/warrior/protection/{slug}"
                case = {"wowClass": "warrior", "spec": "protection",
                        "role": "tank", "section": "mage-tower"}
                self.assertFalse(_case_matches_guide_identity(case, _canonical_guide_url(url)))


if __name__ == "__main__":
    unittest.main()
