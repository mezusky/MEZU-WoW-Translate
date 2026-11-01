"""Cross-role short-CD jargon: source-only evidence, not browser validation."""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class ShortCooldownCrossRoleTests(unittest.TestCase):
    def test_short_cd_phrases_are_locale_scoped(self):
        payload = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(payload, "en-US", "fr-FR")
        self.assertEqual(terms["short cooldowns"], "CD courts")
        self.assertEqual(terms["very short cooldowns"], "CD très courts")
        self.assertEqual(terms["short cooldown spells"], "sorts à CD court")
        # Bare "short cooldown" can modify different nouns and is ambiguous.
        self.assertNotIn("short cooldown", terms)
        self.assertEqual(select_jargon(payload, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(payload, "en-US", "de-DE")

    def test_not_duplicated_as_manual_overrides(self):
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for phrase in ("short cooldowns", "very short cooldowns", "short cooldown spells"):
            for layer in ("jargon", "exact"):
                with self.subTest(phrase=phrase, layer=layer):
                    self.assertNotIn(phrase, manual.get(layer, {}))

    def test_independent_source_guides_are_in_regression_corpus(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        urls = {p["url"] for p in pages}
        for slug in (
            "warrior/protection/rotation-cooldowns-pve-tank",
            "shaman/restoration/rotation-cooldowns-pve-healer",
            "mage/arcane/overview-pve-dps",
        ):
            with self.subTest(slug=slug):
                self.assertIn("https://www.wowhead.com/guide/classes/" + slug, urls)


if __name__ == "__main__":
    unittest.main()
