"""Quality gates must not be inferred from source-only or partial audits."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_trend import summarize


def report(cycle, method="browser-rendered", novel=0, clean=True):
    return {"qualitySample": {
        "cycleId": cycle,
        "auditedAt": "2026-10-28T22:00:00+01:00" if cycle == "a" else "2026-10-28T23:00:00+01:00",
        "newPagesAudited": 4,
        "novelIssueFamilies": novel,
        "browserVerifiedPages": 4 if method == "browser-rendered" else 0,
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
        self.assertEqual(result["cycles"][-1]["novelIssueRate"], 0.25)
        self.assertEqual(result["consecutiveStrictCleanCycles"], 0)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_rejects_duplicate_cycles_and_invalid_counts(self):
        with self.assertRaises(ValueError):
            summarize([report("a"), report("a")])
        bad = report("a")
        bad["qualitySample"]["newPagesAudited"] = -1
        with self.assertRaises(ValueError):
            summarize([bad])

    def test_legacy_reports_do_not_imply_success(self):
        self.assertEqual(summarize([{"browserRenderedPagesVerified": 0}])["cycles"], [])


if __name__ == "__main__":
    unittest.main()
