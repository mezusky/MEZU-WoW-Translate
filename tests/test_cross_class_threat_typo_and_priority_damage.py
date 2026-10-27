"""Source-only cross-role terminology checks; NOT a Chrome translation replay.

WoW threat (menace) and forum thread are distinct concepts. Do not turn
thread into threat, even in longer phrases.
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


class CrossClassThreatTypoAndPriorityDamageTests(unittest.TestCase):
    def test_threat_typo_is_contextual_and_locale_scoped(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        expected = {
            "threat generation": "génération de menace",
            "threat management": "gestion de la menace",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
                for layer in ("exact", "jargon"):
                    self.assertNotIn(source, MANUAL.get(layer, {}))
        # Old typo mappings must stay removed: forum threads are not aggro.
        for source in ("bonus thread", "thread transfer", "thread transferred",
                       "thread generation", "thread reduction", "thread", "threads"):
            with self.subTest(negative=source):
                self.assertNotIn(source, terms)
                for layer in ("exact", "jargon"):
                    self.assertNotIn(source, MANUAL.get(layer, {}))
        self.assertNotIn("threat", terms)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_cross_role_source_evidence(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        # Source excerpts, not observed output of the browser translator.
        samples = {
            "blood-death-knight-basics": "threat generation",
            "brewmaster-monk-talents": "threat management",
        }
        for page_id, phrase in samples.items():
            with self.subTest(page=page_id):
                self.assertIn(page_id, PAGES)
                self.assertIn("/guide/classes/", PAGES[page_id])
                self.assertIn(phrase, terms)

    def test_unhyphenated_priority_damage_reuses_existing_semantics(self):
        terms = select_jargon(GLOSSARY, "en", "fr")
        self.assertEqual(terms["priority target damage"],
                         terms["priority-target damage"])
        self.assertEqual(terms["priority damage"], "dégâts prio")
        self.assertNotIn("priority", terms)
        self.assertNotIn("target", terms)
        for key in ("priority target damage", "priority-target damage"):
            for layer in ("exact", "jargon"):
                self.assertNotIn(key, MANUAL.get(layer, {}))
        # Three independent DPS classes/specs, same meaning despite spelling.
        samples = {
            "frost-mage-mythic-plus": "works well for priority target damage",
            "subtlety-rogue-overview": "higher priority target damage in AoE",
            "marksmanship-hunter-mythic-plus": "poor priority-target damage",
        }
        for page_id, excerpt in samples.items():
            with self.subTest(page=page_id):
                self.assertIn(page_id, PAGES)
                self.assertTrue("priority target damage" in excerpt
                                or "priority-target damage" in excerpt)

    def test_new_guides_cover_widget_and_official_entity_risks(self):
        self.assertIn("subtlety-rogue-abilities", PAGES)
        self.assertTrue(PAGES["subtlety-rogue-abilities"].endswith(
            "/abilities-talents-pve-dps"))
        self.assertTrue(PAGES["subtlety-rogue-mythic-plus"].endswith(
            "/mythic-plus-dungeon-tips"))
        # Spell/item names remain the responsibility of canonical IDs.
        self.assertNotIn("Death's Caress", select_jargon(GLOSSARY, "en", "fr"))


if __name__ == "__main__":
    unittest.main()
