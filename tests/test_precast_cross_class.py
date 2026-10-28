"""Scoped pre-cast jargon on independent Midnight rotations (source-only).

English Wowhead evidence: Fire Mage, Demonology Warlock, Augmentation
Evoker, and Windwalker Monk rotation guides (Oct 2026). "Pre-cast" is
WoW-player shorthand, not an official spell name. This tests data and
locale isolation only; no Chrome Translator API/DOM execution.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class PrecastCrossClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {p["id"]: p["url"] for p in json.loads(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]}

    def test_attested_precast_variants_only(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        for source, target in (("Pre-cast", "Pré-cast"), ("pre-cast", "pré-cast")):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("jargon", {}))
                self.assertNotIn(source, self.manual.get("exact", {}))
        # Do not guess grammatical forms: pre-casting can be a gerund,
        # while "cast" and "pre" are too broad for a glossary override.
        for unsafe in ("pre", "cast", "pre-casting", "Pre-casting", "precise"):
            self.assertNotIn(unsafe, jargon)

    def test_independent_source_guides(self):
        for page_id in ("fire-mage-rotation", "demonology-warlock-rotation",
                        "augmentation-evoker-rotation", "windwalker-monk-rotation"):
            with self.subTest(page=page_id):
                self.assertIn(page_id, self.pages)
                self.assertIn("/rotation-cooldowns-pve-dps", self.pages[page_id])

    def test_locale_direction_isolation(self):
        self.assertEqual(select_jargon(self.player, "en", "fr")["pre-cast"], "pré-cast")
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en", "de")


if __name__ == "__main__":
    unittest.main()
