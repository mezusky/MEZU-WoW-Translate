"""Regression checks for cumulative Blizzard translation memory."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MERGER = Path(__file__).resolve().parents[1] / "scripts" / "preserve_blizzard_memory.py"


class BlizzardMemoryRetentionTests(unittest.TestCase):
    def merge(self, old, new):
        with tempfile.TemporaryDirectory() as tmp:
            previous = Path(tmp) / "previous.json"
            current = Path(tmp) / "current.json"
            previous.write_text(json.dumps(old), encoding="utf-8")
            current.write_text(json.dumps(new), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(MERGER), str(previous), str(current)],
                capture_output=True, text=True,
            )
            if result.returncode:
                return result, None
            return result, json.loads(current.read_text(encoding="utf-8"))

    def test_partial_sync_keeps_validated_pairs(self):
        old = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR",
               "exact": {"Shield Slam": "Heurt de bouclier"},
               "sources": {"Shield Slam": "123"}}
        new = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR",
               "exact": {"Ignore Pain": "Dur au mal"}}
        result, merged = self.merge(old, new)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(merged["pair_count"], 2)
        self.assertEqual(merged["exact"]["Shield Slam"], "Heurt de bouclier")
        self.assertEqual(merged["exact"]["Ignore Pain"], "Dur au mal")

    def test_conflicting_pairs_are_quarantined(self):
        old = {"exact": {"Rage": "Rage"}}
        new = {"exact": {"Rage": "Colère"}}
        result, merged = self.merge(old, new)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("Rage", merged["exact"])
        self.assertIn("Rage", merged["ambiguous"])

    def test_cross_locale_merge_is_rejected(self):
        old = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR", "exact": {}}
        new = {"sourceLanguage": "en-US", "targetLanguage": "de-DE", "exact": {}}
        result, merged = self.merge(old, new)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(merged)


if __name__ == "__main__":
    unittest.main()
