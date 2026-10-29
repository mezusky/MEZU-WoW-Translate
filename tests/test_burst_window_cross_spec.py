"""Source-grounded, locale-scoped burst-window terminology across specs.

English Wowhead source evidence: Havoc DH pre-patch (plural), Devourer DH
pre-patch (plural), and Arcane Mage rotation (singular). This tests only
data-layer selection; it cannot verify browser Translator API output.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
    encoding="utf-8"))


class BurstWindowCrossSpecTests(unittest.TestCase):
    def test_burst_window_is_wow_jargon_not_a_literal_time_slot(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["burst window"], "fenêtre de burst")
        self.assertEqual(terms["burst windows"], "fenêtres de burst")
        self.assertNotIn("window", terms)
        self.assertNotIn("windows", terms)
        # Damage amplification is not always the same as burst timing.
        self.assertEqual(terms["damage amp window"], "fenêtre de dégâts amplifiés")

    def test_no_cross_locale_contamination_or_same_language_translation(self):
        self.assertEqual(select_jargon(GLOSSARY, "en", "en-GB"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "de", "fr")
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")

    def test_no_duplicate_manual_sentence_override(self):
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for phrase in ("burst window", "burst windows"):
            self.assertNotIn(phrase, manual.get("exact", {}))
            self.assertNotIn(phrase, manual.get("jargon", {}))


if __name__ == "__main__":
    unittest.main()
