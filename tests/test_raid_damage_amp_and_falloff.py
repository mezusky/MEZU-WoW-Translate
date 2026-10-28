"""Reusable raid-mechanic terminology across unrelated Wowhead class guides.

Source-only evidence (not browser translation): Retribution Paladin, Assassination
Rogue and Devourer DH Season 2 raid tips for damage amplification; Holy and
Discipline Priest raid tips plus older Protection Warrior/Vengeance DH raid tips
for distance falloff. Avoid translating generic 'amp', 'drop off' or 'falloff'
without a damage context.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class RaidMechanicJargonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {
            row["id"]: row["url"]
            for row in json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        }

    def test_damage_amp_patterns_are_locale_scoped(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "damage amp window": "fenêtre de dégâts amplifiés",
            "damage amp windows": "fenêtres de dégâts amplifiés",
            "damage amp phase": "phase de dégâts amplifiés",
            "damage amplification window": "fenêtre de dégâts amplifiés",
            "damage amplification windows": "fenêtres de dégâts amplifiés",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("jargon", {}))
                self.assertNotIn(source, self.manual.get("exact", {}))
        self.assertNotIn("amp", jargon)
        self.assertNotIn("damage amp", jargon)

    def test_distance_falloff_is_not_generic_drop_off(self):
        jargon = select_jargon(self.player, "en", "fr")
        for source in ("drop-off damage", "dropoff damage", "falloff damage", "fall-off damage"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "dégâts dégressifs avec la distance")
        # 'Drop off' can also mean placing an AoE away from the group.
        self.assertNotIn("drop off", jargon)
        self.assertNotIn("falloff", jargon)
        self.assertNotIn("distance-based damage", jargon)

    def test_periodic_damage_phrase_is_locale_scoped_not_a_spell(self):
        # Indexed Holy Priest and Restoration Shaman raid prose both use
        # "ticking damage". Do not translate bare "tick", which also names
        # periodic events in cast/channel mechanics.
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        self.assertEqual(jargon["ticking damage"], "dégâts périodiques")
        self.assertNotIn("ticking", jargon)
        self.assertNotIn("tick", jargon)
        self.assertNotIn("dropoff", jargon)
        self.assertNotIn("ticking damage", self.manual.get("jargon", {}))
        self.assertNotIn("dropoff damage", self.manual.get("jargon", {}))

    def test_heldout_roles_and_locale_direction(self):
        for page in (
            "retribution-paladin-raid", "assassination-rogue-raid",
            "devourer-demon-hunter-raid", "holy-priest-raid",
            "discipline-priest-raid", "protection-warrior-manaforge-omega-raid",
            "holy-priest-manaforge-omega-raid",
            "discipline-priest-manaforge-omega-raid",
            "restoration-druid-manaforge-omega-raid",
            "mistweaver-monk-manaforge-omega-raid",
            "blood-death-knight-manaforge-omega-raid",
            "destruction-warlock-manaforge-omega-raid",
        ):
            with self.subTest(page=page):
                self.assertIn(page, self.pages)
                self.assertTrue(self.pages[page].startswith("https://www.wowhead.com/guide/classes/"))
        self.assertEqual(select_jargon(self.player, "fr", "fr"), {})
        self.assertEqual(select_jargon(self.player, "en-US", "en-GB"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de", "fr")


if __name__ == "__main__":
    unittest.main()
