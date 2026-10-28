"""Scoped spellqueue window terminology across independent Midnight guides.

Source-only evidence: Arcane Mage rotation and Mistweaver Monk UI/macros
(October 2026). The bare phrase "spell queue" is also a verb in Holy
Paladin and Discipline Priest rotations, so only noun collocations belong
in the locale-specific glossary. No browser Translator API is simulated.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class SpellqueueWindowCrossRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {p["id"]: p["url"] for p in json.loads(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]}

    def test_only_scoped_noun_variants_are_normalized(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "spell queue window": "fenêtre de spell queue",
            "Spell Queue Window": "Fenêtre de spell queue",
            "spellqueue window": "fenêtre de spell queue",
            "Spellqueue Window": "Fenêtre de spell queue",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("jargon", {}))
                self.assertNotIn(source, self.manual.get("exact", {}))
        for unsafe in ("spell queue", "spellqueue", "spell queueing",
                       "spellqueueing", "SpellQueueWindow", "queue"):
            self.assertNotIn(unsafe, jargon)

    def test_independent_guides_and_verb_holdouts(self):
        for page_id, suffix in (
            ("arcane-mage-rotation", "/rotation-cooldowns-pve-dps"),
            ("mistweaver-monk-ui-macros", "/addons-macro-ui-imports"),
            ("discipline-priest-rotation", "/rotation-cooldowns-pve-healer"),
            ("holy-paladin-rotation", "/rotation-cooldowns-pve-healer"),
        ):
            with self.subTest(page=page_id):
                self.assertTrue(self.pages[page_id].endswith(suffix))

    def test_locale_direction_isolation(self):
        self.assertEqual(
            select_jargon(self.player, "en", "fr")["spell queue window"],
            "fenêtre de spell queue",
        )
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en", "de")


if __name__ == "__main__":
    unittest.main()
