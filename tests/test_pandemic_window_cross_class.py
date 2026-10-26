"""Offline EN->FR contract for the shared DoT refresh-window term.

Evidence: current Midnight Wowhead rotation guides for Feral Druid,
Affliction Warlock and Elemental Shaman. These tests do not reproduce
Chrome's Translator API or prove browser DOM reconstruction.
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
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class PandemicWindowCrossClassTests(unittest.TestCase):
    def test_shared_phrase_is_precise_and_locale_scoped(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(jargon["pandemic window"], "fenêtre Pandemic")
        self.assertEqual(jargon["Pandemic window"], "fenêtre Pandemic")
        self.assertEqual(jargon["DOT Pandemic Range"], "fenêtre Pandemic des DoT")
        # A bare "pandemic" can occur in unrelated prose or named entities.
        self.assertNotIn("pandemic", jargon)
        self.assertNotIn("Pandemic", jargon)
        self.assertEqual(select_jargon(GLOSSARY, "fr", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "de", "fr")

    def test_independent_current_guides_contain_the_pattern(self):
        # Short source evidence only, not copies of copyrighted guides.
        evidence = {
            "feral-druid-rotation": "Pandemic and snapshotting",
            "affliction-warlock-rotation": "before your Pandemic window",
            "elemental-shaman-rotation": "within the pandemic window",
        }
        indexed = {page["id"]: page["url"] for page in PAGES}
        for guide, fragment in evidence.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, indexed)
                self.assertTrue(indexed[guide].startswith("https://www.wowhead.com/guide/classes/"))
                self.assertIn("pandemic", fragment.lower())

    def test_no_sentence_override_or_unscoped_duplication(self):
        for term in ("pandemic window", "Pandemic window", "DOT Pandemic Range"):
            with self.subTest(term=term):
                self.assertNotIn(term, MANUAL.get("exact", {}))
                self.assertNotIn(term, MANUAL.get("jargon", {}))


if __name__ == "__main__":
    unittest.main()
