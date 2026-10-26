"""Locale-scoped healer terminology sampled across independent Wowhead guides.

Source-only fixtures from Restoration Druid overview/rotation, Preservation
Evoker stats and Mistweaver Monk overview. Not browser Translator API output.
"""
import json
import re
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))


class HealerHotGlossaryTests(unittest.TestCase):
    def test_effect_variants_have_consistent_grammatical_number(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        for variant in ("heal-over-time", "healing-over-time"):
            with self.subTest(variant=variant):
                self.assertEqual(jargon[variant + " effect"], "effet de soin sur la durée")
                self.assertEqual(jargon[variant + " effects"], "effets de soin sur la durée")
        for variant in ("heal over time effects", "Heal over Time effects"):
            self.assertEqual(jargon[variant], "effets de soin sur la durée")

    def test_real_cross_spec_phrases_are_covered_without_sentence_overrides(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        fixtures = {
            "restoration-druid-overview": "different heal-over-time effects to keep the raid alive",
            "restoration-druid-rotation": "The most valuable heal-over-time effect to extend",
            "preservation-evoker-stats": "some heal-over-time effects like Reversion",
            "mistweaver-monk-overview": "a healing-over-time effect on our allies",
        }
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for guide, excerpt in fixtures.items():
            with self.subTest(guide=guide):
                matches = [term for term in jargon if re.search(
                    r"(?<!\w)" + re.escape(term) + r"(?!\w)", excerpt, re.I
                )]
                self.assertTrue(matches, guide)
                self.assertNotIn(excerpt, manual.get("exact", {}))
        for term in ("heal-over-time effect", "healing-over-time effect"):
            self.assertNotIn(term, manual.get("jargon", {}))

    def test_modern_abilities_pages_cover_remaining_hot_spellings(self):
        # Indexed EN source excerpts from four independent Midnight healer
        # abilities/talents guides. These are NOT Chrome Translator API output.
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        fixtures = {
            "preservation-evoker-talents": (
                "Adds a Heal over Time (HoT) effect to Verdant Embrace.",
                "Heal over Time (HoT) effect",
                "effet de soin sur la durée (HoT)",
            ),
            "restoration-shaman-abilities": (
                "Single target heal that applies a heal over time effect.",
                "heal over time effect",
                "effet de soin sur la durée",
            ),
            "mistweaver-monk-abilities": (
                "Place a heal-over-time effect on your current target.",
                "heal-over-time effect",
                "effet de soin sur la durée",
            ),
            "restoration-druid-talents": (
                "It gives it a chance to extend all of your heal-over-time effects!",
                "heal-over-time effects",
                "effets de soin sur la durée",
            ),
        }
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        corpus = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))
        ids = {page["id"] for page in corpus["pages"]}
        for guide, (excerpt, phrase, expected) in fixtures.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertIn(phrase, excerpt)
                self.assertEqual(jargon[phrase], expected)
                self.assertNotIn(phrase, manual.get("exact", {}))
                self.assertNotIn(phrase, manual.get("jargon", {}))
        # Bare wording can be verbal prose ("heal over time"), not a noun.
        self.assertNotIn("heal over time", jargon)

    def test_parenthesized_hot_variants_across_independent_healers(self):
        # Indexed 2026-10-26 Wowhead EN: Holy Priest overview and Restoration
        # Druid overview; source-only assertions, NOT rendered Chrome output.
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        fixtures = {
            "holy-priest-overview": (
                "All these healing effects also place a Healing over Time (HoT) effect",
                "Healing over Time (HoT) effect",
                "effet de soin sur la durée (HoT)",
            ),
            "restoration-druid-overview": (
                "Can concentrate Heal over Time effects (HoTs) on a single ally",
                "Heal over Time effects (HoTs)",
                "effets de soin sur la durée (HoTs)",
            ),
        }
        corpus = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(
            encoding="utf-8"))
        ids = {page["id"] for page in corpus["pages"]}
        for guide, (excerpt, phrase, expected) in fixtures.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertIn(phrase, excerpt)
                self.assertEqual(jargon[phrase], expected)
        self.assertEqual(jargon["healing-over-time effects (HoTs)"],
                         "effets de soin sur la durée (HoTs)")
        # Bare verbal wording has a different syntax and must stay contextual.
        self.assertNotIn("healing over time", jargon)

    def test_glossary_is_not_available_to_other_translation_directions(self):
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        for source, target in (("de-DE", "fr-FR"), ("en-US", "de-DE"),
                               ("fr-FR", "en-US")):
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    select_jargon(GLOSSARY, source, target)


if __name__ == "__main__":
    unittest.main()
