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

    def test_independent_tank_and_healer_sources(self):
        ids = {page["id"] for page in PAGES}
        evidence = {
            "mop-blood-death-knight-rotation": "External Raid Cooldowns",
            "brewmaster-monk-faq": "The most common external cooldowns you can call for",
            "mop-holy-priest-overview": "Great external single-target cooldowns",
        }
        for guide, excerpt in evidence.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertIn("external", excerpt.casefold())
        self.assertIn("holy-paladin-overview", ids)


if __name__ == "__main__":
    unittest.main()
