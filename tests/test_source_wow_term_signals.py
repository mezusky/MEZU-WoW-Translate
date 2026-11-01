"""Locale-scoped short WoW labels for source-only audits.

Indexed Wowhead tank/healer/DPS guides contain isolated labels such as GCD,
Mythic+ and Holy Power, often beside localized spell links. These tests do not
claim to reproduce Chrome Translator API or the rendered DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.source_language_evidence import compile_wow_term_signals

ROOT = Path(__file__).resolve().parents[1]
SIGNALS = json.loads((ROOT / "data/audit_language_signals.json").read_text(
    encoding="utf-8"))["wowTerms"]


class SourceWowTermSignalTests(unittest.TestCase):
    def test_current_english_labels_keep_source_audit_coverage(self):
        matcher = compile_wow_term_signals(SIGNALS, "en-US")
        for label in ("GCD", "Holy Power", "Mythic+", "Best in Slot",
                      "defensive", "Mitigation"):
            with self.subTest(label=label):
                self.assertIsNotNone(matcher.search(label))
        self.assertIsNone(matcher.search("mythical"))
        self.assertIsNone(matcher.search("cooldowns"))  # not bare cooldown

    def test_no_english_fallback_on_other_source_languages(self):
        self.assertIsNone(compile_wow_term_signals(SIGNALS, "fr-FR"))
        self.assertIsNone(compile_wow_term_signals(SIGNALS, "de-DE"))

    def test_new_locale_labels_are_data_only(self):
        data = {"en": ["Holy Power"], "fr-FR": ["Puissance sacrée"],
                "de-DE": ["Heilige Kraft"]}
        french = compile_wow_term_signals(data, "fr-CA")
        german = compile_wow_term_signals(data, "de-DE")
        self.assertIsNotNone(french.search("puissance sacrée"))
        self.assertIsNone(french.search("Holy Power"))
        self.assertIsNotNone(german.search("Heilige Kraft"))
        self.assertIsNone(german.search("Puissance sacrée"))

    def test_invalid_signal_data_fails_closed(self):
        with self.assertRaises(ValueError):
            compile_wow_term_signals({"en": [None]}, "en")
        with self.assertRaises(ValueError):
            compile_wow_term_signals({"en": [""]}, "en")


if __name__ == "__main__":
    unittest.main()
