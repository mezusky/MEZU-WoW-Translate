"""Cross-role cooldown shorthand contract from indexed Wowhead English guides.

Only verifies locale-scoped data and source phrase coverage. Chrome Translator
API output and rich-text rendering remain browser-only checks.
"""
import json
import re
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class CooldownShorthandTests(unittest.TestCase):
    def test_full_and_abbreviated_cooldown_have_same_meaning(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        for phrase in ("on cooldown", "on cd"):
            with self.subTest(phrase=phrase):
                self.assertEqual(terms[phrase], "dès que disponible")
        self.assertEqual(terms["On CD"], "Dès que disponible")
        self.assertEqual(terms["off cooldown"], "disponible")
        self.assertNotIn("cd", terms)  # bare CD can occur in other contexts

    def test_independent_healer_and_dps_source_samples(self):
        # Short excerpts from indexed English guides, not translated output.
        examples = {
            "discipline-priest-rotation": "Cast Mind Blast on cd",
            "restoration-druid-rotation": "On CD, On Self",
            "affliction-warlock-rotation": "cast Dark Harvest essentially on CD",
        }
        ids = {page["id"] for page in PAGES}
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        for guide, sample in examples.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertTrue(any(re.search(
                    r"(?<!\w)" + re.escape(term) + r"(?!\w)", sample, re.I
                ) for term in ("on cd", "On CD")))
                self.assertNotIn(sample, MANUAL.get("exact", {}))
        self.assertEqual(terms["on cd"], "dès que disponible")

    def test_one_source_of_truth_for_cooldown_terms(self):
        for term in ("on cooldown", "off cooldown", "on cd", "On CD"):
            with self.subTest(term=term):
                self.assertNotIn(term, MANUAL.get("jargon", {}))
                self.assertNotIn(term, MANUAL.get("exact", {}))

    def test_no_cross_locale_leakage(self):
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        for source, target in (("fr-FR", "en-US"), ("en-US", "de-DE")):
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    select_jargon(GLOSSARY, source, target)


if __name__ == "__main__":
    unittest.main()
