"""Regression for compact source-only audit metadata, not browser quality."""
import unittest
from pathlib import Path

from scripts.source_intervention_trend import load_cycles

ROOT = Path(__file__).resolve().parents[1]


class RecentSourceAuditMetadataTests(unittest.TestCase):
    def test_recent_samples_use_corpus_ids_and_unique_cycle_identity(self):
        cycles = load_cycles(
            ROOT / "data/wowhead_audit_trend.json",
            ROOT / "audits",
            ROOT / "data/wowhead_regression_pages.json")
        by_id = {row.get("cycleId"): row for row in cycles}
        recent = {
            "2026-11-02-caster-spell-hit-cross-expansion-source-only": 6,
            "2026-11-02-tbc-url-validation-effective-health-cross-class-source-only": 1,
            "2026-11-02-tank-tps-dtps-cross-expansion-source-only": 3,
            "2026-11-03-hunter-melee-weaving-cross-expansion-source-only": 5,
            "2026-11-03-classic-weapon-defense-skill-cross-role-source-only": 3,
        }
        for cycle_id, expected_count in recent.items():
            with self.subTest(cycle_id=cycle_id):
                row = by_id[cycle_id]
                self.assertEqual(row["sampledPageCount"], expected_count)
                self.assertEqual(len(set(row["sampledPageIds"])), expected_count)
                self.assertEqual((row["sourceLanguage"], row["targetLanguage"]),
                                 ("en", "fr"))
                self.assertEqual(row["browserRenderedPagesVerified"], 0)


if __name__ == "__main__":
    unittest.main()
