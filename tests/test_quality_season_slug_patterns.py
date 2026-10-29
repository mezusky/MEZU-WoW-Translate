"""Future expansion/season guide slugs must not require code edits every patch.

Only the audit identity classifier is tested; no browser output is simulated.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_trend import _canonical_guide_url, _case_matches_guide_identity


def valid_case(slug, section, wow_class="warrior", spec="protection", role="tank"):
    url = f"https://www.wowhead.com/guide/classes/{wow_class}/{spec}/{slug}"
    case = {"wowClass": wow_class, "spec": spec, "role": role,
            "section": section}
    return case, _canonical_guide_url(url)


class FutureGuideSectionTests(unittest.TestCase):
    def test_current_and_future_raid_season_prepatch_slugs(self):
        for slug, section in (
            ("midnight-season-2-raid-tips", "raid"),
            ("midnight-season-3-raid-tips", "raid"),
            ("the-last-titan-season-1-raid-tips", "raid"),
            ("midnight-season-2", "season"),
            ("midnight-season-3", "season"),
            ("the-last-titan-season-1", "season"),
            ("midnight-pre-patch", "prepatch"),
            ("the-last-titan-pre-patch", "prepatch"),
            ("manaforge-omega-raid-tips", "raid"),
        ):
            with self.subTest(slug=slug):
                case, url = valid_case(slug, section)
                self.assertTrue(_case_matches_guide_identity(case, url))

    def test_wrong_section_cannot_claim_coverage(self):
        for slug, wrong in (
            ("midnight-season-3-raid-tips", "season"),
            ("midnight-season-3", "raid"),
            ("the-last-titan-pre-patch", "raid"),
        ):
            with self.subTest(slug=slug):
                case, url = valid_case(slug, wrong)
                self.assertFalse(_case_matches_guide_identity(case, url))

    def test_malformed_and_unknown_sections_fail_closed(self):
        for slug in (
            "midnight-season-0-raid-tips",
            "midnight-season-x-raid-tips",
            "midnight-season-3-raid-tips-extra",
            "midnight-season-3-raid",
            "random-raid-tips",
            "midnight-pre-patch-extra",
        ):
            with self.subTest(slug=slug):
                case, url = valid_case(slug, "raid")
                self.assertFalse(_case_matches_guide_identity(case, url))

    def test_role_and_spec_guards_remain_enforced(self):
        case, url = valid_case("midnight-season-3-raid-tips", "raid",
                               wow_class="priest", spec="discipline",
                               role="healer")
        self.assertTrue(_case_matches_guide_identity(case, url))
        case["role"] = "dps"
        self.assertFalse(_case_matches_guide_identity(case, url))


if __name__ == "__main__":
    unittest.main()
