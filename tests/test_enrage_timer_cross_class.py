"""Cross-class raid jargon, scoped to EN->FR data rather than exact prose.

Indexed Enhancement Shaman and Subtlety Rogue raid guides use enrage timing.
No live browser translation or DOM reconstruction is claimed by this test.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))


class EnrageTimerCrossClassTests(unittest.TestCase):
    def test_enrage_timing_is_a_shared_player_term(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["enrage timer"], "timer d’enrage")
        self.assertEqual(terms["enrage timers"], "timers d’enrage")
        # A bare 'enrage' can be a spell name, mechanic or verb.
        self.assertNotIn("enrage", terms)
        self.assertNotIn("Enrage", terms)

    def test_manual_overrides_do_not_duplicate_the_term(self):
        for key in ("enrage timer", "enrage timers"):
            self.assertNotIn(key, MANUAL.get("exact", {}))
            self.assertNotIn(key, MANUAL.get("jargon", {}))

    def test_no_cross_locale_leakage(self):
        self.assertEqual(select_jargon(GLOSSARY, "en", "en-US"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")


if __name__ == "__main__":
    unittest.main()
