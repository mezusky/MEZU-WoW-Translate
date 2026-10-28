"""Quality gates must not be inferred from source-only or partial audits."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_trend import summarize


def report(cycle, method="browser-rendered", novel=0, clean=True):
    cases = [
        {"url": f"https://www.wowhead.com/guide/classes/{cls}/{spec}/{section}",
         "wowClass": cls, "spec": spec, "role": role, "section": section,
         "heldout": i < 2, "browserRendered": True, "strictPass": True}
        for i, (cls, spec, role, section) in enumerate([
            ("warrior", "protection", "tank", "rotation"),
            ("priest", "discipline", "healer", "talents"),
            ("mage", "fire", "dps", "gear"),
            ("druid", "guardian", "tank", "raid"),
            ("hunter", "survival", "dps", "mythic-plus"),
        ])
    ]
    return {"qualitySample": {
        "cycleId": cycle,
        "auditedAt": "2026-10-28T22:00:00+01:00" if cycle == "a" else "2026-10-28T23:00:00+01:00",
        "newPagesAudited": len(cases),
        "novelIssueFamilies": novel,
        "browserVerifiedPages": len(cases) if method == "browser-rendered" else 0,
        "browserCases": cases,
        "auditMethod": method,
        "crossRoleVerified": True,
        "unrelatedHeldoutsVerified": True,
        "strictAuditPassed": clean,
    }}


class QualityTrendTests(unittest.TestCase):
    def test_source_only_zero_is_unknown_not_clean(self):
        result = summarize([report("a", method="indexed-excerpts")])
        self.assertIsNone(result["cycles"][0]["novelIssueRate"])
        self.assertEqual(result["measuredCycleCount"], 0)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_missing_novelty_is_unknown(self):
        result = summarize([report("a", novel=None)])
        self.assertIsNone(result["cycles"][0]["novelIssueRate"])
        self.assertEqual(result["consecutiveStrictCleanCycles"], 0)

    def test_partial_browser_coverage_cannot_estimate_full_rate(self):
        partial = report("a")
        partial["qualitySample"]["browserVerifiedPages"] = 2
        result = summarize([partial])
        self.assertIsNone(result["cycles"][0]["novelIssueRate"])
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_two_distinct_strict_cycles_required(self):
        self.assertFalse(summarize([report("a")])["eligibleToConsiderStopping"])
        result = summarize([report("b"), report("a")])
        self.assertTrue(result["eligibleToConsiderStopping"])
        self.assertEqual(result["consecutiveStrictCleanCycles"], 2)

    def test_failed_latest_cycle_breaks_streak(self):
        result = summarize([report("a"), report("b", novel=2, clean=False)])
        self.assertEqual(result["consecutiveStrictCleanCycles"], 0)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_high_novel_issue_rate_never_counts_as_clean(self):
        result = summarize([report("a"), report("b", novel=1, clean=True)])
        self.assertEqual(result["cycles"][-1]["novelIssueRate"], 0.2)
        self.assertEqual(result["consecutiveStrictCleanCycles"], 0)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_rejects_duplicate_cycles_and_invalid_counts(self):
        with self.assertRaises(ValueError):
            summarize([report("a"), report("a")])
        bad = report("a")
        bad["qualitySample"]["newPagesAudited"] = -1
        with self.assertRaises(ValueError):
            summarize([bad])

    def test_summary_flags_without_page_evidence_never_pass(self):
        result = report("a")
        del result["qualitySample"]["browserCases"]
        self.assertEqual(summarize([result])["consecutiveStrictCleanCycles"], 0)

    def test_single_page_or_single_role_never_passes(self):
        single = report("a")
        single["qualitySample"]["browserCases"] = single["qualitySample"]["browserCases"][:1]
        single["qualitySample"]["newPagesAudited"] = 1
        single["qualitySample"]["browserVerifiedPages"] = 1
        self.assertFalse(summarize([single])["eligibleToConsiderStopping"])
        one_role = report("a")
        for case in one_role["qualitySample"]["browserCases"]:
            case["role"] = "dps"
        self.assertEqual(summarize([one_role])["consecutiveStrictCleanCycles"], 0)

    def test_duplicate_urls_or_unverified_heldouts_never_pass(self):
        duplicate = report("a")
        cases = duplicate["qualitySample"]["browserCases"]
        cases[1]["url"] = cases[0]["url"]
        self.assertEqual(summarize([duplicate])["consecutiveStrictCleanCycles"], 0)
        unverified = report("a")
        unverified["qualitySample"]["browserCases"][0]["strictPass"] = False
        self.assertEqual(summarize([unverified])["consecutiveStrictCleanCycles"], 0)
        no_heldouts = report("a")
        for case in no_heldouts["qualitySample"]["browserCases"]:
            case["heldout"] = False
        self.assertEqual(summarize([no_heldouts])["consecutiveStrictCleanCycles"], 0)

    def test_malformed_page_metadata_is_not_a_clean_cycle(self):
        malformed = report("a")
        malformed["qualitySample"]["browserCases"][0]["role"] = ["tank"]
        self.assertEqual(summarize([malformed])["consecutiveStrictCleanCycles"], 0)

    def test_legacy_reports_do_not_imply_success(self):
        self.assertEqual(summarize([{"browserRenderedPagesVerified": 0}])["cycles"], [])


if __name__ == "__main__":
    unittest.main()
