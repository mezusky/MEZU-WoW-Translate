"""Cross-class priority-target noun terminology (source-only evidence).

These tests validate the locale-scoped data contract, not the Chrome
Translator API's phrase selection or rendered Wowhead DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = {p["id"] for p in json.loads(
    (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
)["pages"]}


class PriorityTargetNounTests(unittest.TestCase):
    def test_locale_scoped_noun_and_longer_damage_phrases(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["priority target"], "cible prioritaire")
        self.assertEqual(terms["priority target damage"], "dégâts sur la cible prioritaire")
        self.assertEqual(terms["priority-target damage"], "dégâts sur la cible prioritaire")
        for layer in ("exact", "jargon"):
            self.assertNotIn("priority target", MANUAL.get(layer, {}))
        self.assertNotIn("target", terms)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_independent_raid_and_hunter_evidence(self):
        # Indexed English source: Fury says the Heart is the priority target;
        # Marksmanship describes a priority target being present.
        self.assertTrue({"fury-warrior-raid",
                         "marksmanship-hunter-mythic-plus",
                         "frost-mage-mythic-plus"}.issubset(PAGES))


if __name__ == "__main__":
    unittest.main()
