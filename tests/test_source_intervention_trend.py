"""Source-only intervention rates must not be mistaken for translation quality."""
import unittest
import json
import tempfile
from pathlib import Path

from scripts.source_intervention_trend import summarize, load_cycles


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

    def test_explicit_audit_samples_extend_history_without_large_history_edits(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            history.write_text(json.dumps({"cycles": [
                {"date": "2026-11-01", **cycle(["prior"], families=1)}
            ]}), encoding="utf-8")
            corpus.write_text(json.dumps({"pages": [
                {"id": key} for key in ("prior", "healer", "tank")
            ]}), encoding="utf-8")
            (audits / "legacy.json").write_text(json.dumps({
                "auditMethod": "indexed-source-only", "date": "2026-11-02"
            }), encoding="utf-8")
            report = {"date": "2026-11-02", "auditMethod": "indexed-source-only",
                      "sourceInterventionSample": {
                          "cycleId": "heldout-1", "sourceLanguage": "en-US",
                          "targetLanguage": "fr-FR",
                          "sampledPageIds": ["healer", "tank"],
                          "sampledPageCount": 2,
                          "newReusableTermFamiliesObserved": 0,
                          "newManualSentenceOverrides": 0,
                          "browserRenderedPagesVerified": 0}}
            (audits / "new.json").write_text(json.dumps(report), encoding="utf-8")
            cycles = load_cycles(history, audits, corpus)
            self.assertEqual(len(cycles), 2)
            summary = summarize(cycles, window=1)
            self.assertEqual(summary["eligibleCycles"], 2)
            self.assertEqual(summary["recent"]["sampledPages"], 2)
            self.assertEqual(summary["recent"]["termFamiliesPerPage"], 0.0)
            self.assertIsNone(summary["browserTranslationErrorRate"])

    def test_explicit_samples_reject_unknown_pages_and_locale_leakage(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            history.write_text('{"cycles":[]}', encoding="utf-8")
            corpus.write_text('{"pages":[{"id":"tank"}]}', encoding="utf-8")
            sample = {"cycleId": "a", "sourceLanguage": "en",
                      "targetLanguage": "fr", "sampledPageIds": ["tank"],
                      "sampledPageCount": 1,
                      "newReusableTermFamiliesObserved": 0,
                      "newManualSentenceOverrides": 0,
                      "browserRenderedPagesVerified": 0}
            report = {"date": "2026-11-02", "auditMethod": "indexed-source-only",
                      "sourceInterventionSample": sample}
            path = audits / "sample.json"
            for field, bad in (("sampledPageIds", ["invented"]),
                               ("sampledPageCount", True),
                               ("targetLanguage", "en-GB"),
                               ("sourceLanguage", "malformed_locale"),
                               ("browserRenderedPagesVerified", True)):
                with self.subTest(field=field):
                    original = sample[field]
                    sample[field] = bad
                    path.write_text(json.dumps(report), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_cycles(history, audits, corpus)
                    sample[field] = original

    def test_invalid_date_and_duplicate_audit_cycles_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            history.write_text(json.dumps({"cycles": [
                {"date": "2026-11-01", **cycle(["prior"])}
            ]}), encoding="utf-8")
            corpus.write_text('{"pages":[{"id":"tank"},{"id":"prior"}]}', encoding="utf-8")
            report = {"date": "2026-11-40", "auditMethod": "indexed-source-only",
                      "sourceInterventionSample": {
                          "cycleId": "same", "sourceLanguage": "en",
                          "targetLanguage": "fr", "sampledPageIds": ["tank"],
                          "sampledPageCount": 1,
                          "newReusableTermFamiliesObserved": 0,
                          "newManualSentenceOverrides": 0,
                          "browserRenderedPagesVerified": 0}}
            path = audits / "one.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cycles(history, audits, corpus)
            report["date"] = "2026-11-02"
            path.write_text(json.dumps(report), encoding="utf-8")
            (audits / "two.json").write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cycles(history, audits, corpus)

    def test_archived_audit_cycle_is_not_counted_twice(self):
        # Moving an audit into historical storage must preserve first-seen
        # measurements rather than creating a duplicate heldout cycle.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            sample = {"cycleId": "archived", "sourceLanguage": "en-US",
                      "targetLanguage": "fr-FR", "sampledPageIds": ["healer"],
                      "sampledPageCount": 1,
                      "newReusableTermFamiliesObserved": 1,
                      "newManualSentenceOverrides": 0,
                      "browserRenderedPagesVerified": 0}
            archived = {**sample, "date": "2026-11-02"}
            history.write_text(json.dumps({"cycles": [archived]}),
                               encoding="utf-8")
            corpus.write_text('{"pages":[{"id":"healer"}]}',
                              encoding="utf-8")
            report = {"date": "2026-11-02",
                      "auditMethod": "indexed-source-only",
                      "sourceInterventionSample": sample}
            path = audits / "archived.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            self.assertEqual(load_cycles(history, audits, corpus), [archived])
            report["sourceInterventionSample"] = {
                **sample, "newReusableTermFamiliesObserved": 2}
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cycles(history, audits, corpus)

    def test_duplicate_historical_cycle_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            corpus.write_text('{"pages":[]}', encoding="utf-8")
            history.write_text(json.dumps({"cycles": [
                {"cycleId": "duplicate", **cycle(["a"])},
                {"cycleId": "duplicate", **cycle(["b"])}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cycles(history, audits, corpus)

    def test_older_audit_survives_later_historical_updates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            history.write_text(json.dumps({"cycles": [
                {"date": "2026-11-04", **cycle(["future"])}
            ]}), encoding="utf-8")
            corpus.write_text('{"pages":[{"id":"future"},{"id":"earlier"}]}', encoding="utf-8")
            report = {"date": "2026-11-02", "auditMethod": "indexed-source-only",
                      "sourceInterventionSample": {
                          "cycleId": "older", "sourceLanguage": "en",
                          "targetLanguage": "fr", "sampledPageIds": ["earlier"],
                          "sampledPageCount": 1,
                          "newReusableTermFamiliesObserved": 0,
                          "newManualSentenceOverrides": 0,
                          "browserRenderedPagesVerified": 0}}
            (audits / "older.json").write_text(json.dumps(report), encoding="utf-8")
            cycles = load_cycles(history, audits, corpus)
            self.assertEqual([row["date"] for row in cycles],
                             ["2026-11-02", "2026-11-04"])
            self.assertEqual(summarize(cycles, window=1)["eligibleCycles"], 2)

    def test_repository_heldout_audit_is_counted_without_browser_claims(self):
        root = Path(__file__).resolve().parents[1]
        cycles = load_cycles(root / "data/wowhead_audit_trend.json",
                             root / "audits",
                             root / "data/wowhead_regression_pages.json")
        ids = {row.get("cycleId") for row in cycles}
        self.assertIn("2026-11-02-cross-role-structured-heldouts-wipe-protection", ids)
        report = summarize(cycles)
        self.assertGreaterEqual(report["eligibleCycles"], 25)
        self.assertIsNone(report["browserTranslationErrorRate"])
        self.assertIsNone(report["novelTranslationIssueRate"])

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            summarize([], window=0)
        with self.assertRaises(ValueError):
            summarize({}, window=2)


if __name__ == "__main__":
    unittest.main()
