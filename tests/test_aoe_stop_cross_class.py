"""Cross-class source-only regression for AoE stop terminology.

Indexed Wowhead examples: Balance/Restoration Druid and Retribution Paladin
Mythic+ guides. This does not verify Chrome Translator API or rendered DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class AoeStopCrossClassTests(unittest.TestCase):
    def test_singular_forms_preserve_existing_plural_and_locale_isolation(self):
        glossary = json.loads(
            (ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8")
        )
        terms = select_jargon(glossary, "en-US", "fr-FR")
        for source in ("AoE stop", "aoe stop", "AoE-stop"):
            with self.subTest(source=source):
                self.assertEqual(terms[source], "stop AoE")
        self.assertEqual(terms["AoE Stop"], "Stop AoE")
        self.assertEqual(terms["AoE stops"], "stops AoE")
        self.assertEqual(terms["aoe stops"], "stops AoE")
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "de-DE")

    def test_no_manual_sentence_override_or_entity_name_collision(self):
        manual = json.loads(
            (ROOT / "data/manual_overrides.json").read_text(encoding="utf-8")
        )
        for layer in ("jargon", "exact", "protected_names"):
            for source in ("AoE stop", "aoe stop", "AoE-stop"):
                with self.subTest(layer=layer, source=source):
                    self.assertNotIn(source, manual.get(layer, {}))

    def test_independent_tank_healer_and_dps_guides_are_sampled(self):
        pages = json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]
        urls = {page["url"] for page in pages}
        for spec in (
            "druid/restoration/mythic-plus-dungeon-tips",
            "druid/balance/mythic-plus-dungeon-tips",
            "paladin/retribution/mythic-plus-dungeon-tips",
        ):
            with self.subTest(spec=spec):
                self.assertIn("https://www.wowhead.com/guide/classes/" + spec, urls)


if __name__ == "__main__":
    unittest.main()
