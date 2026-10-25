"""Official phrase memory must preserve explicit numeric inequality semantics."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_blizzard_memory import (
    comparison_facts, good_pair, numeric_facts, numeric_semantics_match,
)

MERGER = Path(__file__).resolve().parents[1] / "scripts" / "preserve_blizzard_memory.py"


class NumericComparisonTests(unittest.TestCase):
    def test_unicode_and_ascii_inclusive_operators_are_equivalent(self):
        source = "Keep charges ≥ 3.5 during burst."
        target = "Gardez les charges >= 3,5 pendant le burst."
        self.assertEqual(comparison_facts(source), [(">=", "3.5")])
        self.assertEqual(comparison_facts(target), [(">=", "3.5")])
        self.assertTrue(good_pair(source, target, 7.0))

    def test_reversed_comparison_is_not_accepted(self):
        source = "Keep charges ≥ 3.5 during burst."
        target = "Gardez les charges <= 3,5 pendant le burst."
        self.assertEqual(numeric_facts(source), numeric_facts(target))
        self.assertFalse(good_pair(source, target, 7.0))

    def test_strict_and_inclusive_thresholds_are_not_interchangeable(self):
        self.assertFalse(numeric_semantics_match(
            "Differences below <1% are negligible.",
            "Les écarts inférieurs à <=1 % sont négligeables."
        ))
        self.assertTrue(numeric_semantics_match(
            "Differences below <1% are negligible.",
            "Les écarts inférieurs à < 1 % sont négligeables."
        ))

    def test_comparison_order_and_arrow_are_handled_conservatively(self):
        self.assertEqual(comparison_facts("At >=3 and <5, cast now."),
                         [(">=", "3"), ("<", "5")])
        self.assertNotEqual(comparison_facts("At >=3 and <5, cast now."),
                            comparison_facts("À < 3 et >= 5, lancez maintenant."))
        self.assertEqual(comparison_facts("Step ->3 then continue."), [])

    def test_legacy_unsafe_comparison_is_not_retained(self):
        source = "Keep charges ≥ 3.5 during burst."
        target = "Gardez les charges <= 3,5 pendant le burst."
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder) / "old.json"
            new = Path(folder) / "new.json"
            old.write_text(json.dumps({"exact": {source: target},
                                       "sources": {source: "123"}}), encoding="utf-8")
            new.write_text(json.dumps({"exact": {}}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(MERGER), str(old), str(new)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            merged = json.loads(new.read_text(encoding="utf-8"))
            self.assertNotIn(source, merged["exact"])
            self.assertNotIn(source, merged["sources"])


    def test_balance_druid_inclusive_aoe_breakpoints(self):
        # Live English Balance Druid rotation: inclusive bounds are gameplay-critical.
        self.assertEqual(comparison_facts("on 4 targets and above", "en-US"),
                         [(">=", "4")])
        self.assertEqual(comparison_facts("up to and including 3 targets", "en-US"),
                         [("<=", "3")])
        self.assertTrue(numeric_semantics_match(
            "Enter Lunar Eclipse on 4 targets and above.",
            "Entrez en Éclipse lunaire sur 4 cibles ou plus."
        ))
        self.assertTrue(numeric_semantics_match(
            "Enter Solar Eclipse up to and including 3 targets.",
            "Entrez en Éclipse solaire jusqu'à 3 cibles."
        ))
        self.assertFalse(numeric_semantics_match(
            "Enter Lunar Eclipse on 4 targets and above.",
            "Entrez en Éclipse lunaire sur 4 cibles ou moins."
        ))

    def test_marksmanship_hunter_independent_threshold(self):
        # Independent spec/section: Marksmanship leveling, not Balance rotation.
        self.assertTrue(numeric_semantics_match(
            "Use Multi-Shot on 3 targets and above.",
            "Utilisez Flèches multiples sur 3 cibles ou plus."
        ))
        self.assertFalse(numeric_semantics_match(
            "Use Multi-Shot on 3 targets and above.",
            "Utilisez Flèches multiples sur 3 cibles ou moins."
        ))
        # Keep unknown locale isolation: never borrow English phrase patterns.
        self.assertEqual(comparison_facts("3 targets and above", "de-DE"), [])

if __name__ == "__main__":
    unittest.main()
