"""Source-backed target-cap jargon across unrelated WoW specs.

Only checks locale-scoped data, not browser Translator API or Wowhead DOM.
A bare 'hard cap' must remain contextual: it can describe stat limits.
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


class TargetCapCrossClassTests(unittest.TestCase):
    def test_target_cap_is_contextual_and_locale_scoped(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["target capped"], "limité en nombre de cibles")
        self.assertEqual(terms["hard-capped AoE"], "AoE limitée à un nombre fixe de cibles")
        for unsafe in ("hard cap", "hard capped", "soft cap", "target"):
            self.assertNotIn(unsafe, terms)
        for layer in ("exact", "jargon"):
            self.assertNotIn("target capped", MANUAL.get(layer, {}))
            self.assertNotIn("hard-capped AoE", MANUAL.get(layer, {}))
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_independent_hunter_rogue_and_shaman_evidence(self):
        # Hunter Mythic+ discusses hard-capped AoE; Rogue overview describes
        # target-capped Blade Flurry; Shaman M+ is held out for comparison.
        self.assertTrue({
            "marksmanship-hunter-mythic-plus",
            "outlaw-rogue-overview",
            "elemental-shaman-mythic-plus",
            "marksmanship-hunter-abilities",
        }.issubset(PAGES))


if __name__ == "__main__":
    unittest.main()
