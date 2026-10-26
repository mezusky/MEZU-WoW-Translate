"""Locale-scoped bonus-loot vocabulary across independent Midnight gear guides.

Evidence: English Wowhead search-index excerpts reviewed 2026-10-26.
These tests verify data contracts and source samples, NOT Chrome translation.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = {p["id"]: p["url"] for p in json.loads(
    (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
)["pages"]}


class BonusRollLocaleGlossaryTests(unittest.TestCase):
    def test_player_terms_are_scoped_and_not_duplicated(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        expected = {
            "bonus roll": "jet bonus",
            "bonus rolls": "jets bonus",
            "Bonus Roll": "Jet bonus",
            "Bonus Rolls": "Jets bonus",
            "Bonus Loot rolls": "jets de butin bonus",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
                for layer in ("exact", "jargon"):
                    self.assertNotIn(source, MANUAL.get(layer, {}))
        # The generic English word "roll" also means other things.
        self.assertNotIn("roll", terms)
        self.assertNotIn("rolling", terms)
        self.assertEqual(select_jargon(GLOSSARY, "fr", "fr"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")

    def test_cross_class_gearing_evidence(self):
        # Distinct class authors and roles; source-only excerpts, not a
        # claim that the MEZU extension rendered these strings correctly.
        evidence = {
            "outlaw-rogue-gear": "Using a Bonus Roll will reward an item level equivalent",
            "restoration-shaman-gear": "Bonus rolls will allow you to get them at myth-track",
            "restoration-druid-gear": "via Bonus Loot rolls",
        }
        for guide, excerpt in evidence.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, PAGES)
                self.assertIn("/bis-gear", PAGES[guide])
                self.assertTrue(
                    "Bonus Roll" in excerpt or "Bonus rolls" in excerpt
                    or "Bonus Loot rolls" in excerpt
                )

    def test_raid_widget_is_independent_non_prose_risk(self):
        # This guide contains long talent-import strings; glossary rules
        # should not be used to infer safe handling of those DOM widgets.
        self.assertIn("demonology-warlock-raid", PAGES)
        self.assertTrue(PAGES["demonology-warlock-raid"].endswith(
            "/midnight-season-2-raid-tips"
        ))


if __name__ == "__main__":
    unittest.main()
