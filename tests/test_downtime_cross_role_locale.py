"""Source-only downtime jargon regression across unrelated WoW specs.

English Wowhead evidence checked 2026-10-30:
- Fury Warrior leveling: "without downtime", "virtually no downtime"
- Feral Druid leveling: "downtime in between pulls"
- Restoration Druid rotation: "during downtime"
- Holy Priest leveling: "during downtime"

This checks data-layer scoping, not browser Translator API or DOM rendering.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class DowntimeCrossRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = {
            p["url"] for p in json.loads(
                (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8")
            )["pages"]
        }

    def test_reusable_locale_scoped_phrases(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        for source, target in {
            "downtime": "temps mort",
            "during downtime": "pendant les temps morts",
            "without downtime": "sans temps mort",
            "no downtime": "aucun temps mort",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("jargon", {}))
                self.assertNotIn(source, self.manual.get("exact", {}))

    def test_no_unbounded_downtime_overrides(self):
        jargon = select_jargon(self.player, "en", "fr")
        for unsafe in ("down", "time", "during", "without", "no", "uptime"):
            self.assertNotIn(unsafe, jargon)

    def test_unrelated_dps_and_healer_sources_in_corpus(self):
        for url in (
            "https://www.wowhead.com/guide/classes/warrior/fury/dps-leveling-tips",
            "https://www.wowhead.com/guide/classes/druid/feral/dps-leveling-tips",
            "https://www.wowhead.com/guide/classes/druid/restoration/rotation-cooldowns-pve-healer",
            "https://www.wowhead.com/guide/classes/priest/holy/healer-leveling-tips",
        ):
            with self.subTest(url=url):
                self.assertIn(url, self.pages)

    def test_language_direction_isolation(self):
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en", "de")
        with self.assertRaises(ValueError):
            select_jargon(self.player, "de", "fr")


if __name__ == "__main__":
    unittest.main()
