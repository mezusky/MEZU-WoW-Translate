"""Cross-role regression for reusable cooldown language (source-only evidence).

The current Wowhead Brewmaster (tank), Mistweaver (healer), and Augmentation
Evoker (DPS) rotation guides all discuss cooldown reduction. Mistweaver also
uses "comes off cooldown". These are phrase hints, not browser output claims.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CooldownPhraseMemoryTests(unittest.TestCase):
    def test_locale_scoped_reusable_phrases(self):
        glossary = load("data/mezu_player_glossary.json")
        self.assertEqual((glossary["sourceLanguage"], glossary["targetLanguage"]),
                         ("en", "fr"))
        expected = {
            "cooldown reduction": "réduction de CD",
            "cooldown reductions": "réductions de CD",
            "comes off cooldown": "redevient disponible",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(glossary["jargon"][source], target)

    def test_manual_overrides_do_not_duplicate_shared_phrases(self):
        manual = load("data/manual_overrides.json")
        for phrase in ("cooldown reduction", "cooldown reductions",
                       "comes off cooldown"):
            for layer in ("jargon", "exact"):
                with self.subTest(phrase=phrase, layer=layer):
                    self.assertNotIn(phrase, manual.get(layer, {}))
        # Do not confuse cooldown reduction with the opposite concept:
        # "on cooldown" can mean an ability is unavailable or a usage rule.
        jargon = load("data/mezu_player_glossary.json")["jargon"]
        self.assertNotIn("on cooldown", jargon)
        self.assertEqual(jargon["Use on cooldown"], "À utiliser dès que disponible")

    def test_independent_role_pages_remain_in_regression_corpus(self):
        urls = {p["url"] for p in load("data/wowhead_regression_pages.json")["pages"]}
        for slug in (
            "monk/brewmaster/rotation-cooldowns-pve-tank",
            "monk/mistweaver/rotation-cooldowns-pve-healer",
            "evoker/augmentation/rotation-cooldowns-pve-dps",
        ):
            with self.subTest(slug=slug):
                self.assertIn("https://www.wowhead.com/guide/classes/" + slug, urls)


if __name__ == "__main__":
    unittest.main()
