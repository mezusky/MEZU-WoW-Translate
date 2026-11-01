"""Cross-guide source-only checks for planned healing cooldown language.

Indexed Wowhead Restoration Druid and Preservation Evoker guides share the
"pre-plan cooldowns" wording; Restoration Shaman independently uses
"pre-plan usage". These tests do not validate Chrome's rendered translation.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class PreplannedCooldownPhraseTests(unittest.TestCase):
    def test_locale_scoped_phrases(self):
        glossary = read("data/mezu_player_glossary.json")
        self.assertEqual((glossary["sourceLanguage"], glossary["targetLanguage"]),
                         ("en", "fr"))
        self.assertEqual(glossary["jargon"]["pre-plan cooldowns"],
                         "planifier les CD à l’avance")
        self.assertEqual(glossary["jargon"]["pre-plan usage"],
                         "planifier l’utilisation à l’avance")

    def test_no_ambiguous_standalone_or_manual_duplicates(self):
        glossary = read("data/mezu_player_glossary.json")["jargon"]
        manual = read("data/manual_overrides.json")
        self.assertNotIn("pre-plan", glossary)
        for term in ("pre-plan cooldowns", "pre-plan usage"):
            for layer in ("jargon", "exact"):
                self.assertNotIn(term, manual.get(layer, {}))

    def test_unrelated_healer_guides_in_corpus(self):
        urls = {p["url"] for p in read("data/wowhead_regression_pages.json")["pages"]}
        for slug in (
            "druid/restoration/rotation-cooldowns-pve-healer",
            "evoker/preservation/rotation-cooldowns-pve-healer",
            "shaman/restoration/rotation-cooldowns-pve-healer",
        ):
            with self.subTest(slug=slug):
                self.assertIn("https://www.wowhead.com/guide/classes/" + slug, urls)


if __name__ == "__main__":
    unittest.main()
