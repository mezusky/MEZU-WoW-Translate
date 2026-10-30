"""Novelty rates require page-level browser evidence, not summary claims.

Source-only excerpts cannot establish rendered translation quality. A failed
rendered page remains measurable but must not pass the clean-cycle stop gate.
"""
import unittest

from scripts.quality_trend import summarize


def sample(*, method="browser-rendered", strict_pass=False):
    page = {
        "url": "https://www.wowhead.com/guide/classes/warrior/protection/rotation-cooldowns-pve-tank",
        "wowClass": "warrior",
        "spec": "protection",
        "role": "tank",
        "section": "rotation",
        "sourceLanguage": "en",
        "targetLanguage": "fr",
        "browserRendered": True,
        "strictPass": strict_pass,
        "heldout": True,
    }
    return {"qualitySample": {
        "cycleId": "measured-evidence",
        "auditedAt": "2026-10-30T17:00:00+01:00",
        "sourceLanguage": "en",
        "targetLanguage": "fr",
        "auditMethod": method,
        "newPagesAudited": 1,
        "browserVerifiedPages": 1,
        "novelIssueFamilies": 1,
        "browserCases": [page],
        "crossRoleVerified": False,
        "unrelatedHeldoutsVerified": False,
        "strictAuditPassed": False,
    }}


class MeasuredEvidenceTests(unittest.TestCase):
    def test_failed_but_rendered_page_has_rate_without_clean_pass(self):
        result = summarize([sample()])
        self.assertEqual(result["measuredCycleCount"], 1)
        self.assertEqual(result["cycles"][0]["novelIssueRate"], 1.0)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_claimed_browser_count_without_manifest_is_unknown(self):
        report = sample()
        report["qualitySample"].pop("browserCases")
        result = summarize([report])
        self.assertIsNone(result["cycles"][0]["novelIssueRate"])
        self.assertEqual(result["measuredCycleCount"], 0)

    def test_unverified_or_wrong_page_metadata_is_unknown(self):
        for field, value in (("browserRendered", False), ("role", "dps"),
                             ("targetLanguage", "de"), ("url", "https://example.org")):
            with self.subTest(field=field):
                report = sample()
                report["qualitySample"]["browserCases"][0][field] = value
                result = summarize([report])
                self.assertIsNone(result["cycles"][0]["novelIssueRate"])

    def test_partial_or_inflated_page_count_is_unknown(self):
        for count in (0, 2):
            with self.subTest(count=count):
                report = sample()
                report["qualitySample"]["browserVerifiedPages"] = count
                self.assertIsNone(summarize([report])["cycles"][0]["novelIssueRate"])

    def test_indexed_source_is_not_browser_measurement(self):
        report = sample(method="indexed-excerpts")
        self.assertIsNone(summarize([report])["cycles"][0]["novelIssueRate"])

    def test_same_language_does_not_measure_translation(self):
        report = sample()
        report["qualitySample"]["targetLanguage"] = "en-US"
        report["qualitySample"]["browserCases"][0]["targetLanguage"] = "en-US"
        self.assertIsNone(summarize([report])["cycles"][0]["novelIssueRate"])


if __name__ == "__main__":
    unittest.main()
