"""Reusable tank/healer wording observed in independent Wowhead guides.

English indexed sources: Vengeance DH stat priority and Protection Warrior
effective-health explanations; Holy Priest raid and Mistweaver rotation for
rot damage. Source-only contracts; no browser Translator API claim.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class EffectiveHealthRotDamageLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {
            page["id"]: page["url"]
            for page in json.loads(
                (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
            )["pages"]
        }

    def test_cross_role_terms_and_ambiguous_boundaries(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "effective health": "points de vie effectifs",
            "Effective Health": "Points de vie effectifs",
            "effective hit points": "points de vie effectifs",
            "Effective Hit Points": "Points de vie effectifs",
            "rot damage": "dégâts continus",
            "Rot Damage": "Dégâts continus",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("exact", {}))
                self.assertNotIn(source, self.manual.get("jargon", {}))
        for ambiguous in ("health", "effective", "rot", "damage", "effective healing", "EHP"):
            self.assertNotIn(ambiguous, jargon)

    def test_unrelated_live_guide_sections_are_in_regression_corpus(self):
        evidence = {
            "vengeance-demon-hunter-stats": "/demon-hunter/vengeance/stat-priority-pve-tank",
            "holy-priest-raid": "/priest/holy/midnight-season-2-raid-tips",
            "mistweaver-monk-rotation": "/monk/mistweaver/rotation-cooldowns-pve-healer",
        }
        for page_id, path in evidence.items():
            with self.subTest(page=page_id):
                self.assertIn(path, self.pages[page_id])

    def test_no_cross_locale_leak_or_same_language_translation(self):
        self.assertEqual(select_jargon(self.player, "en-US", "en-GB"), {})
        self.assertEqual(select_jargon(self.player, "fr", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en", "de")
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de", "fr")


if __name__ == "__main__":
    unittest.main()
