"""Synthetic audit-gate tests: a real guide URL must carry its real WoW role.

The role map is compact data-only metadata, not evidence of browser rendering.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_trend import summarize, SPEC_ROLES


def sample():
    pages = (
        ("warrior", "protection", "tank", "bis-gear", "gear"),
        ("priest", "discipline", "healer", "tier-set-bonuses", "tier-set"),
        ("mage", "fire", "dps", "midnight-season-2-raid-tips", "raid"),
        ("druid", "guardian", "tank", "midnight-pre-patch", "prepatch"),
        ("hunter", "survival", "dps", "mythic-plus-dungeon-tips", "mythic-plus"),
    )
    cases = [{
        "url": f"https://www.wowhead.com/guide/classes/{cls}/{spec}/{slug}",
        "wowClass": cls, "spec": spec, "role": role, "section": section,
        "sourceLanguage": "en", "targetLanguage": "fr",
        "heldout": i < 2, "browserRendered": True, "strictPass": True,
    } for i, (cls, spec, role, slug, section) in enumerate(pages)]
    return {"qualitySample": {
        "cycleId": "role-identity",
        "auditedAt": "2026-10-29T20:00:00+00:00",
        "sourceLanguage": "en", "targetLanguage": "fr",
        "newPagesAudited": len(cases), "novelIssueFamilies": 0,
        "browserVerifiedPages": len(cases), "browserCases": cases,
        "auditMethod": "browser-rendered", "crossRoleVerified": True,
        "unrelatedHeldoutsVerified": True, "strictAuditPassed": True,
    }}


class RoleIdentityTests(unittest.TestCase):
    def test_reference_covers_all_retail_specs(self):
        data = json.loads((ROOT / "data/wow_spec_roles.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 1)
        self.assertEqual(len(SPEC_ROLES), 13)
        self.assertEqual(sum(map(len, SPEC_ROLES.values())), 40)
        self.assertEqual(set(role for specs in SPEC_ROLES.values()
                             for role in specs.values()), {"tank", "healer", "dps"})

    def test_cross_role_sample_remains_valid(self):
        self.assertTrue(summarize([sample()])["cycles"][0]["strictCleanCycle"])

    def test_role_neutral_urls_cannot_be_mislabeled(self):
        # Gear, tier-set, raid, prepatch and Mythic+ do not encode a role.
        for index, wrong in ((0, "healer"), (1, "dps"), (2, "tank"),
                             (3, "dps"), (4, "healer")):
            with self.subTest(index=index):
                case = sample()
                case["qualitySample"]["browserCases"][index]["role"] = wrong
                self.assertFalse(summarize([case])["cycles"][0]["strictCleanCycle"])

    def test_unknown_specialization_fails_closed(self):
        report = sample()
        case = report["qualitySample"]["browserCases"][0]
        case["url"] = "https://www.wowhead.com/guide/classes/warrior/unknown-spec/bis-gear"
        case["spec"] = "unknown-spec"
        self.assertFalse(summarize([report])["cycles"][0]["strictCleanCycle"])

    def test_new_devourer_spec_and_language_independence(self):
        report = sample()
        case = report["qualitySample"]["browserCases"][2]
        case.update({"url": "https://www.wowhead.com/guide/classes/demon-hunter/devourer/bis-gear",
                     "wowClass": "demon-hunter", "spec": "devourer", "role": "dps",
                     "section": "gear"})
        self.assertTrue(summarize([report])["cycles"][0]["strictCleanCycle"])
        case["role"] = "tank"
        self.assertFalse(summarize([report])["cycles"][0]["strictCleanCycle"])
        case["role"] = "dps"
        report["qualitySample"]["sourceLanguage"] = "de"
        for c in report["qualitySample"]["browserCases"]:
            c["sourceLanguage"] = "de"
        self.assertTrue(summarize([report])["cycles"][0]["strictCleanCycle"])


if __name__ == "__main__":
    unittest.main()
