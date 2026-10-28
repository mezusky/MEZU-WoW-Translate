"""Official combat-resurrection nouns reused across roles, not action verbs.

Source: current Wowhead Protection/Holy Paladin and Affliction Warlock
abilities guides, plus Blizzard's French patch 4.1 and 6.0.2 notes.
This tests static glossary selection, not Chrome Translator API or DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class CombatResurrectionTermsTests(unittest.TestCase):
    def test_blizzard_attested_nouns(self):
        expected = {
            "battle resurrection": "résurrection en combat",
            "battle resurrections": "résurrections en combat",
            "Battle Resurrection": "Résurrection en combat",
            "Battle Resurrections": "Résurrections en combat",
            "combat resurrection": "résurrection en combat",
            "combat resurrections": "résurrections en combat",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("exact", {}))
                self.assertNotIn(source, MANUAL.get("jargon", {}))

    def test_do_not_rewrite_ambiguous_verbs_or_spell_names(self):
        for source in ("battle res", "battle rez", "combat res", "res",
                       "rez", "Rebirth", "Soulstone", "Intercession",
                       "Raise Ally", "battle res the healer"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_locale_isolation(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["battle resurrection"], "résurrection en combat")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "de", "fr")

    def test_independent_live_guide_sections(self):
        by_id = {page["id"]: page["url"] for page in PAGES}
        expected = {
            "protection-paladin-abilities": "/paladin/protection/abilities-talents-pve-tank",
            "holy-paladin-abilities": "/paladin/holy/abilities-talents-pve-healer",
            "affliction-warlock-abilities": "/warlock/affliction/abilities-talents-pve-dps",
        }
        for key, suffix in expected.items():
            with self.subTest(guide=key):
                self.assertEqual(by_id[key], "https://www.wowhead.com/guide/classes" + suffix)


if __name__ == "__main__":
    unittest.main()
