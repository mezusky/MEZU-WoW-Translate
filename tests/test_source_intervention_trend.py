"""Source-only intervention rates must not be mistaken for translation quality."""
import unittest

from scripts.source_intervention_trend import summarize


def cycle(ids, families=0, overrides=0):
    return {
        "sampledPageIds": ids,
        "sampledPageCount": len(ids),
        "newReusableTermFamiliesObserved": families,
        "newManualSentenceOverrides": overrides,
    }


class SourceInterventionTrendTests(unittest.TestCase):
    def test_first_seen_pages_and_nonoverlapping_windows(self):
        rows = [
            cycle(["warrior", "priest"], families=1),
            cycle(["mage", "druid"], families=1),
            cycle(["rogue", "shaman"], families=0),
            cycle(["evoker", "monk"], families=0),
        ]
        result = summarize(rows, window=2)
        self.assertEqual(result["eligibleCycles"], 4)
        self.assertEqual(result["early"]["termFamiliesPerPage"], 0.5)
        self.assertEqual(result["recent"]["termFamiliesPerPage"], 0.0)
        self.assertEqual(result["recentTermFamilyRateVsEarly"], "lower")
        self.assertIsNone(result["browserTranslationErrorRate"])
        self.assertIsNone(result["novelTranslationIssueRate"])

    def test_missing_metrics_still_reserve_page_identity(self):
        missing = cycle(["warrior"])
        missing.pop("newManualSentenceOverrides")
        result = summarize([missing, cycle(["warrior"]), cycle(["priest"])], window=1)
        self.assertEqual(result["eligibleCycles"], 1)
        self.assertEqual(result["excludedCycles"]["missingMetrics"], 1)
        self.assertEqual(result["excludedCycles"]["repeatedPages"], 1)
        self.assertIsNone(result["recentTermFamilyRateVsEarly"])

    def test_repeated_pages_inside_cycle_are_not_independent(self):
        result = summarize([cycle(["mage", "mage"]), cycle(["mage", "rogue"]),
                            cycle(["priest"], overrides=1)], window=1)
        self.assertEqual(result["eligibleCycles"], 1)
        self.assertEqual(result["excludedCycles"]["repeatedPages"], 2)
        self.assertEqual(result["recent"]["manualOverridesPerPage"], 1.0)

    def test_invalid_samples_and_boolean_counts_fail_closed(self):
        invalid = cycle(["warrior"])
        invalid["sampledPageCount"] = True
        wrong_length = cycle(["priest"])
        wrong_length["sampledPageCount"] = 2
        bad_metric = cycle(["mage"], families=True)
        result = summarize([invalid, wrong_length, bad_metric], window=1)
        self.assertEqual(result["eligibleCycles"], 0)
        self.assertEqual(result["excludedCycles"]["invalidSample"], 2)
        self.assertEqual(result["excludedCycles"]["missingMetrics"], 1)
        self.assertIsNone(result["recent"]["termFamiliesPerPage"])

    def test_never_claim_acceleration_with_overlapping_windows(self):
        result = summarize([cycle(["warrior"], families=1),
                            cycle(["priest"], families=0)], window=2)
        self.assertIsNone(result["recentTermFamilyRateVsEarly"])

    def test_historical_source_trend_remains_a_proxy(self):
        import json
        from pathlib import Path
        trend_path = Path(__file__).resolve().parents[1] / "data" / "wowhead_audit_trend.json"
        historical = json.loads(trend_path.read_text(encoding="utf-8"))
        result = summarize(historical["cycles"])
        self.assertGreater(result["eligibleCycles"], 0)
        self.assertIsNone(result["browserTranslationErrorRate"])
        self.assertIsNone(result["novelTranslationIssueRate"])

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            summarize([], window=0)
        with self.assertRaises(ValueError):
            summarize({}, window=2)


if __name__ == "__main__":
    unittest.main()
