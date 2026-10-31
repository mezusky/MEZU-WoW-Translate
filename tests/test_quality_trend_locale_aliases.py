"""Blizzard underscore aliases and BCP-47 locale tags share audit identity.

These are synthetic browser evidence fixtures, not real Chrome verification.
"""
import unittest

from scripts.quality_trend import summarize


def sample(source="en-US", target="fr-FR"):
    page = {
        "url": "https://www.wowhead.com/guide/classes/priest/discipline/rotation-cooldowns-pve-healer",
        "wowClass": "priest", "spec": "discipline", "role": "healer",
        "section": "rotation", "sourceLanguage": source,
        "targetLanguage": target, "browserRendered": True,
        "strictPass": False, "heldout": True,
    }
    return {"qualitySample": {
        "cycleId": "locale-alias-evidence",
        "auditedAt": "2026-10-31T08:00:00+01:00",
        "sourceLanguage": source, "targetLanguage": target,
        "auditMethod": "browser-rendered", "newPagesAudited": 1,
        "browserVerifiedPages": 1, "novelIssueFamilies": 1,
        "browserCases": [page], "strictAuditPassed": False,
        "crossRoleVerified": False, "unrelatedHeldoutsVerified": False,
    }}


class QualityLocaleAliasesTests(unittest.TestCase):
    def test_blizzard_underscore_tags_count_as_different_language_evidence(self):
        report = sample("en_US", "fr_FR")
        result = summarize([report])
        self.assertEqual(result["cycles"][0]["novelIssueRate"], 1.0)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_case_aliases_match_cycle_locale_pair(self):
        report = sample("en_US", "fr_FR")
        case = report["qualitySample"]["browserCases"][0]
        case["sourceLanguage"], case["targetLanguage"] = "EN-us", "FR-fr"
        self.assertEqual(summarize([report])["cycles"][0]["novelIssueRate"], 1.0)

    def test_same_base_language_skips_translation_even_across_regions(self):
        for source, target in (("en_US", "en-GB"), ("fr_FR", "fr-CA"),
                               ("de_DE", "de-AT")):
            with self.subTest(source=source, target=target):
                result = summarize([sample(source, target)])
                self.assertIsNone(result["cycles"][0]["novelIssueRate"])

    def test_invalid_locale_tags_do_not_count_as_browser_evidence(self):
        for invalid in ("en__US", "english", "en/US", ""):
            with self.subTest(invalid=invalid):
                self.assertIsNone(summarize([sample(invalid, "fr")])
                                  ["cycles"][0]["novelIssueRate"])


if __name__ == "__main__":
    unittest.main()
