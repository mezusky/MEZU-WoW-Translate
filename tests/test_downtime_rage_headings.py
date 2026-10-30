"""Shared rotation headings verified against unrelated Wowhead source guides.

Source excerpts are not proof of browser-rendered MEZU output.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class DowntimeRageHeadingTests(unittest.TestCase):
    def test_downtime_and_rage_waste_are_distinct_concepts(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(terms["Avoid Downtime"], "Éviter les temps morts")
        self.assertEqual(terms["avoid downtime"], "éviter les temps morts")
        self.assertEqual(terms["Avoid wasting Rage"], "Éviter de gaspiller de la rage")
        self.assertEqual(terms["Avoid Rage Waste"], "Éviter de gaspiller de la rage")
        self.assertEqual(terms["Avoid Rage Capping"], "Éviter d’atteindre le maximum de rage")
        # Do not flatten resource capping, resource waste and time off target.
        self.assertNotEqual(terms["Avoid Downtime"], terms["Avoid Rage Capping"])
        self.assertNotIn("wasting", terms)
        self.assertNotIn("avoid", terms)

    def test_locale_scope_and_no_manual_duplication(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(glossary, "fr", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en", "de")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for phrase in ("Avoid Downtime", "avoid downtime", "Avoid wasting Rage"):
            self.assertNotIn(phrase, manual.get("jargon", {}))
            self.assertNotIn(phrase, manual.get("exact", {}))

    def test_independent_source_guide_coverage(self):
        pages = {p["url"] for p in json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]}
        # Arms/Fury share the same heading; Evoker uses 'avoid downtime'
        # in movement advice. Guardian Druid independently uses Rage waste.
        examples = (
            "warrior/arms/rotation-cooldowns-pve-dps",
            "warrior/fury/rotation-cooldowns-pve-dps",
            "evoker/devastation/rotation-cooldowns-pve-dps",
            "druid/guardian/rotation-cooldowns-pve-tank",
        )
        for path in examples:
            with self.subTest(path=path):
                self.assertIn("https://www.wowhead.com/guide/classes/" + path, pages)


if __name__ == "__main__":
    unittest.main()
