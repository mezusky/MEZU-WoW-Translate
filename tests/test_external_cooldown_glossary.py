"""Cross-era, cross-role source evidence for external defensive cooldown jargon.

These tests validate locale-scoped data only, not Chrome Translator API output.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class ExternalCooldownGlossaryTests(unittest.TestCase):
    def test_reusable_locale_scoped_phrases(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        expected = {
            "external cooldown": "CD externe",
            "external cooldowns": "CD externes",
            "external raid cooldowns": "CD externes de raid",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
                self.assertNotIn(source, MANUAL.get("exact", {}))
                self.assertNotIn(source, MANUAL.get("jargon", {}))
        # 'external' alone also describes healing, buffs and other concepts.
        self.assertNotIn("external", terms)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "it-IT")

    def test_independent_tank_and_healer_source_phrases(self):
        # Historical cross-era English source excerpts validate the concept.
        # Keep the main regression corpus on current Midnight retail pages.
        evidence = {
            "mop-blood-death-knight-rotation": "External Raid Cooldowns",
            "brewmaster-monk-faq": "The most common external cooldowns you can call for",
            "healing-advanced-guide": "External cooldowns are abilities that increase the healing received",
        }
        terms = select_jargon(GLOSSARY, "en", "fr")
        for guide, excerpt in evidence.items():
            with self.subTest(guide=guide):
                self.assertTrue(any(phrase in excerpt.casefold()
                                    for phrase in terms if phrase.startswith("external")))
        ids = {page["id"] for page in PAGES}
        for guide in ("guardian-druid-overview", "preservation-evoker-overview",
                      "mistweaver-monk-talent-builds", "holy-paladin-overview"):
            with self.subTest(current_guide=guide):
                self.assertIn(guide, ids)


if __name__ == "__main__":
    unittest.main()
