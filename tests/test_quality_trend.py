"""Quality gates must not be inferred from source-only or partial audits."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_trend import summarize


def report(cycle, method="browser-rendered", novel=0, clean=True):
    pages = ([
        ("warrior", "protection", "tank", "rotation"),
        ("priest", "discipline", "healer", "talents"),
        ("mage", "fire", "dps", "gear"),
        ("druid", "guardian", "tank", "raid"),
        ("hunter", "survival", "dps", "mythic-plus"),
    ] if cycle == "a" else [
        ("monk", "brewmaster", "tank", "rotation"),
        ("paladin", "holy", "healer", "talents"),
        ("rogue", "subtlety", "dps", "gear"),
        ("shaman", "restoration", "healer", "raid"),
        ("evoker", "augmentation", "dps", "mythic-plus"),
    ])
    cases = [
        {"url": f"https://www.wowhead.com/guide/classes/{cls}/{spec}/{section}",
         "wowClass": cls, "spec": spec, "role": role, "section": section,
         "sourceLanguage": "en", "targetLanguage": "fr",
         "heldout": i < 2, "browserRendered": True, "strictPass": True}
        for i, (cls, spec, role, section) in enumerate(pages)
    ]
    return {"qualitySample": {
        "cycleId": cycle,
        "sourceLanguage": "en",
        "targetLanguage": "fr",
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

    def test_repeated_pages_across_cycles_cannot_prove_generalization(self):
        first, second = report("a"), report("b")
        second["qualitySample"]["browserCases"] = first["qualitySample"]["browserCases"]
        result = summarize([first, second])
        self.assertEqual(result["consecutiveStrictCleanCycles"], 1)
        self.assertFalse(result["eligibleToConsiderStopping"])

    def test_query_fragment_and_locale_variants_are_same_guide(self):
        # Browser navigations and localized entity views cannot manufacture
        # independent heldouts from the same underlying Wowhead guide.
        within = report("a")
        cases = within["qualitySample"]["browserCases"]
        cases[1]["url"] = cases[0]["url"] + "?utm_source=mezu#rotation"
        self.assertFalse(summarize([within])["cycles"][0]["strictCleanCycle"])

        first, second = report("a"), report("b")
        # Keep case metadata consistent with the substituted source page;
        # otherwise the newer class/spec identity guard correctly rejects
        # the cycle before URL-overlap behavior can be tested.
        first_case = first["qualitySample"]["browserCases"][0]
        second_case = second["qualitySample"]["browserCases"][0]
        for key in ("wowClass", "spec", "role", "section"):
            second_case[key] = first_case[key]
        second["qualitySample"]["browserCases"][0]["url"] = (
            first["qualitySample"]["browserCases"][0]["url"]
            .replace("/guide/", "/fr/guide/") + "?ref=sidebar#top"
        )
        self.assertEqual(summarize([first, second])["consecutiveStrictCleanCycles"], 1)

        # A different target locale is still the same source guide.
        second["qualitySample"]["browserCases"][0]["url"] = (
            first["qualitySample"]["browserCases"][0]["url"]
            .replace("/guide/", "/mx/guide/")
        )
        self.assertEqual(summarize([first, second])["consecutiveStrictCleanCycles"], 1)

        # PTR content can differ from retail, so retain its namespace.
        second["qualitySample"]["browserCases"][0]["url"] = (
            first["qualitySample"]["browserCases"][0]["url"]
            .replace("/guide/", "/ptr/guide/")
        )
        self.assertEqual(summarize([first, second])["consecutiveStrictCleanCycles"], 2)

    def test_browser_case_class_and_spec_must_match_actual_guide_path(self):
        # Distinct URLs and a declared three-role mix are not enough if the
        # class/spec evidence labels do not describe the verified page.
        for key, value in (
            ("wowClass", "priest"),
            ("spec", "fury"),
        ):
            with self.subTest(key=key):
                sample = report("a")
                sample["qualitySample"]["browserCases"][0][key] = value
                self.assertFalse(summarize([sample])["cycles"][0]["strictCleanCycle"])

        # A URL on Wowhead that is not a class/spec guide cannot impersonate
        # a class guide merely by declaring plausible metadata.
        sample = report("a")
        sample["qualitySample"]["browserCases"][0]["url"] = (
            "https://www.wowhead.com/guide/midnight/mythic-plus-season-overview"
        )
        self.assertFalse(summarize([sample])["cycles"][0]["strictCleanCycle"])

        # PTR namespaces remain supported as independent source variants.
        sample = report("a")
        sample["qualitySample"]["browserCases"][0]["url"] = (
            "https://www.wowhead.com/ptr-2/guide/classes/warrior/protection/rotation"
        )
        self.assertTrue(summarize([sample])["cycles"][0]["strictCleanCycle"])

    def test_non_wowhead_host_cannot_supply_browser_evidence(self):
        for invalid in (
            "https://www.wowhead.com.evil.test/guide/classes/warrior/protection/rotation",
            "https://www.wowhead.com@evil.test/guide/classes/warrior/protection/rotation",
            "http://www.wowhead.com/guide/classes/warrior/protection/rotation",
        ):
            with self.subTest(invalid=invalid):
                sample = report("a")
                sample["qualitySample"]["browserCases"][0]["url"] = invalid
                self.assertFalse(summarize([sample])["cycles"][0]["strictCleanCycle"])

    def test_cross_language_cycles_do_not_combine(self):
        first, second = report("a"), report("b")
        second["qualitySample"]["sourceLanguage"] = "de"
        for case in second["qualitySample"]["browserCases"]:
            case["sourceLanguage"] = "de"
        result = summarize([first, second])
        self.assertEqual(result["consecutiveStrictCleanCycles"], 1)

    def test_same_language_or_missing_locale_evidence_cannot_pass(self):
        same = report("a")
        same["qualitySample"]["targetLanguage"] = "en"
        for case in same["qualitySample"]["browserCases"]:
            case["targetLanguage"] = "en"
        self.assertFalse(summarize([same])["cycles"][0]["strictCleanCycle"])
        missing = report("a")
        del missing["qualitySample"]["browserCases"][0]["sourceLanguage"]
        self.assertFalse(summarize([missing])["cycles"][0]["strictCleanCycle"])
        invalid = report("a")
        invalid["qualitySample"]["sourceLanguage"] = "english"
        self.assertFalse(summarize([invalid])["cycles"][0]["strictCleanCycle"])

    def test_equal_or_naive_timestamps_cannot_form_two_cycles(self):
        first, second = report("a"), report("b")
        second["qualitySample"]["auditedAt"] = first["qualitySample"]["auditedAt"]
        self.assertFalse(summarize([first, second])["eligibleToConsiderStopping"])
        first["qualitySample"]["auditedAt"] = "2026-10-28T22:00:00"
        with self.assertRaises(ValueError):
            summarize([first])

    def test_legacy_reports_do_not_imply_success(self):
        self.assertEqual(summarize([{"browserRenderedPagesVerified": 0}])["cycles"], [])


    def test_explicit_url_role_cannot_be_mislabeled(self):
        # These guide slugs carry a role; a fabricated cross-role mix must
        # never count as independent browser evidence.
        for wow_class, spec, slug, expected, wrong in (
            ("warrior", "protection", "rotation-cooldowns-pve-tank", "tank", "dps"),
            ("priest", "discipline", "healer-leveling-tips", "healer", "tank"),
            ("mage", "fire", "rotation-cooldowns-pve-dps", "dps", "healer"),
        ):
            with self.subTest(slug=slug):
                sample = report("a")
                case = sample["qualitySample"]["browserCases"][0]
                case["url"] = (
                    f"https://www.wowhead.com/guide/classes/{wow_class}/{spec}/{slug}"
                )
                case["wowClass"] = wow_class
                case["spec"] = spec
                case["role"] = expected
                self.assertTrue(summarize([sample])["cycles"][0]["strictCleanCycle"])
                case["role"] = wrong
                self.assertFalse(summarize([sample])["cycles"][0]["strictCleanCycle"])

    def test_role_not_in_slug_does_not_require_a_guessed_mapping(self):
        sample = report("a")
        sample["qualitySample"]["browserCases"][0]["url"] = (
            "https://www.wowhead.com/guide/classes/warrior/protection/bis-gear"
        )
        self.assertTrue(summarize([sample])["cycles"][0]["strictCleanCycle"])


if __name__ == "__main__":
    unittest.main()
