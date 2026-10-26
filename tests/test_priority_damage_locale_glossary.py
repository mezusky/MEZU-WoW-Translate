"""Cross-class priority-damage terminology and locale-layer migration.

Short Wowhead English-source evidence only; these tests do not claim to
reproduce Chrome's Translator API or to inspect reconstructed browser DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class PriorityDamageLocaleGlossaryTests(unittest.TestCase):
    def test_locale_scoped_terms_without_duplicate_legacy_entries(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["priority damage"], "dégâts prio")
        self.assertEqual(terms["priority-target damage"], "dégâts sur la cible prioritaire")
        for key in ("priority damage", "priority-target damage"):
            for layer in ("exact", "jargon"):
                with self.subTest(key=key, layer=layer):
                    self.assertNotIn(key, MANUAL.get(layer, {}))
        self.assertNotIn("priority", terms)
        self.assertNotIn("target", terms)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_english_source_evidence_across_independent_dps_classes(self):
        # Indexed source snippets, not output from the MEZU browser extension.
        evidence = {
            "marksmanship-hunter-mythic-plus": "extremely poor priority-target damage",
            "survival-hunter-mythic-plus": "free cleave, priority damage, and good AoE",
            "fire-mage-mythic-plus": "gives up much of its priority damage to AoE",
            "devourer-demon-hunter-mythic-plus": "high burst cleave and strong priority damage",
            "enhancement-shaman-mythic-plus": "the priority damage lost by Crash Lightning splitting between targets",
        }
        pages = {p["id"]: p["url"] for p in PAGES}
        for guide, excerpt in evidence.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, pages)
                self.assertTrue(pages[guide].startswith("https://www.wowhead.com/guide/classes/"))
                self.assertTrue(
                    "priority damage" in excerpt or "priority-target damage" in excerpt
                )

    def test_unrelated_healer_source_remains_in_corpus(self):
        pages = {p["id"]: p["url"] for p in PAGES}
        self.assertIn("discipline-priest-abilities", pages)
        self.assertIn("/priest/discipline/abilities-talents", pages["discipline-priest-abilities"])
        # Spell names require official IDs, not this prose-only jargon rule.
        self.assertNotIn("Power Word: Shield", select_jargon(GLOSSARY, "en", "fr"))


if __name__ == "__main__":
    unittest.main()
