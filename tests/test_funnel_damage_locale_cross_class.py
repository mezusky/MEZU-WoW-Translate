"""Locale-scoped funnel-damage terminology across unrelated specs.

Indexed English sources: Affliction Warlock raid, Assassination Rogue talents,
Subtlety Rogue abilities. No Chrome Translator API or DOM replay is implied.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


def data(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


class FunnelDamageLocaleTests(unittest.TestCase):
    def test_contextual_phrases_share_one_fr_locale_layer(self):
        terms = select_jargon(data("mezu_player_glossary.json"), "en-US", "fr-FR")
        self.assertEqual(terms["funnel damage"], "dégâts en funnel")
        self.assertEqual(terms["funneling damage"], "dégâts en funnel")
        self.assertNotIn("funneling", terms)
        manual = data("manual_overrides.json")
        for layer in ("exact", "jargon"):
            self.assertNotIn("funnel damage", manual.get(layer, {}))
            self.assertNotIn("funneling damage", manual.get(layer, {}))
        self.assertEqual(select_jargon(data("mezu_player_glossary.json"),
                                       "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(data("mezu_player_glossary.json"), "en-US", "de-DE")

    def test_unrelated_warlock_rogue_sources_and_heldout_roles(self):
        pages = data("wowhead_regression_pages.json")["pages"]
        ids = {page["id"] for page in pages}
        self.assertTrue({
            "affliction-warlock-raid",
            "assassination-rogue-talent-builds",
            "subtlety-rogue-abilities",
            "vengeance-demon-hunter-cheat-sheet",
            "discipline-priest-cheat-sheet",
            "marksmanship-hunter-cheat-sheet",
            "protection-warrior-cheat-sheet",
        }.issubset(ids))
        self.assertEqual(len(ids), len(pages))
        self.assertEqual(len({page["url"] for page in pages}), len(pages))


if __name__ == "__main__":
    unittest.main()
