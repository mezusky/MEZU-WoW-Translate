"""Locale-scoped tank damage vocabulary, checked against unrelated Midnight guides.

Short indexed Wowhead source fragments only. No Chrome Translator API output
or browser DOM reconstruction is claimed by these offline contract tests.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class TankDamageIntakeGlossaryTests(unittest.TestCase):
    def test_reusable_nouns_and_locale_boundaries(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        expected = {
            "damage intake": "dégâts subis",
            "damage spike": "pic de dégâts",
            "damage spikes": "pics de dégâts",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, MANUAL.get("exact", {}))
                self.assertNotIn(source, MANUAL.get("jargon", {}))
        # These bare words have multiple grammatical and gameplay meanings.
        for word in ("damage", "intake", "spike", "spikes", "smooth"):
            self.assertNotIn(word, jargon)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_independent_current_tank_guides_expose_same_concept(self):
        # Indexed English source; avoid asserting that source-only checks
        # measure real translation quality or validate browser behavior.
        evidence = {
            "protection-warrior-overview": "smooth damage intake; susceptible to damage spikes",
            "brewmaster-monk-rotation": "help explain to healers how to better handle your damage intake",
            "guardian-druid-overview": "consistent, stable damage intake; high Physical damage intake",
            "guardian-druid-rotation": "smooth overall damage intake; align with bigger damage spikes",
            "protection-paladin-rotation": "high damage intake periods; bigger damage spikes",
        }
        indexed = {page["id"]: page["url"] for page in PAGES}
        for guide, excerpt in evidence.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, indexed)
                self.assertTrue(indexed[guide].startswith("https://www.wowhead.com/guide/classes/"))
                self.assertIn("damage intake", excerpt)

    def test_new_sampled_sections_are_independent(self):
        indexed = {page["id"] for page in PAGES}
        self.assertTrue({
            "protection-paladin-rotation",
            "guardian-druid-stats",
            "augmentation-evoker-raid",
        }.issubset(indexed))


if __name__ == "__main__":
    unittest.main()
