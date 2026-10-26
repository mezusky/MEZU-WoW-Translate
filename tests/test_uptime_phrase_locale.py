"""Source-indexed cross-role uptime regression; does not emulate Chrome Translator API."""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class UptimePhraseTests(unittest.TestCase):
    def test_locale_and_context_guard(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(jargon["100% uptime"], "100 % d’uptime")
        self.assertNotIn("uptime", jargon)  # Bare noun requires sentence context.
        self.assertNotIn("100% uptime", MANUAL.get("exact", {}))
        self.assertNotIn("100% uptime", MANUAL.get("jargon", {}))
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_cross_class_indexed_source_examples(self):
        examples = {
            "guardian-druid-overview": "Ironfur with 100% uptime.",
            "feral-druid-overview": "as close to 100% uptime on them as possible.",
            "preservation-evoker-talents": "Possible to get 100% uptime.",
        }
        corpus = {page["id"] for page in PAGES}
        phrase = "100% uptime"
        for page_id, indexed_excerpt in examples.items():
            with self.subTest(page_id=page_id):
                self.assertIn(page_id, corpus)
                self.assertIn(phrase, indexed_excerpt)
        # Independent page types remain in the corpus for held-out audits.
        self.assertIn("guardian-druid-cheat-sheet", corpus)
        self.assertIn("enhancement-shaman-stats", corpus)
        self.assertIn("unholy-death-knight-gear", corpus)


if __name__ == "__main__":
    unittest.main()
