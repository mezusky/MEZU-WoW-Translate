"""Cross-class English Wowhead source evidence for damage-profile noun phrases.

Source-only fixtures: Chrome Translator API output is not simulated here.
Keep this as French locale data; verbs such as "profile" remain contextual.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class DamageProfileGlossaryTests(unittest.TestCase):
    def test_noun_phrase_and_locale_isolation(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(jargon["damage profile"], "profil de dégâts")
        self.assertEqual(jargon["damage profiles"], "profils de dégâts")
        self.assertNotIn("profile", jargon)
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en-US", "de-DE")

    def test_independent_english_guides_and_no_manual_sentence_override(self):
        # Indexed Wowhead prose; each excerpt is intentionally short.
        fixtures = {
            "devastation-evoker-overview": "a bit of a different damage profile",
            "havoc-demon-hunter-overview": "Throughput & Damage Profiles",
            "assassination-rogue-raid": "a good damage profile for Assassination",
        }
        ids = {page["id"] for page in PAGES}
        for guide, excerpt in fixtures.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertIn("damage profile", excerpt.casefold())
        for layer in ("exact", "jargon"):
            self.assertNotIn("damage profile", MANUAL.get(layer, {}))
            self.assertNotIn("damage profiles", MANUAL.get(layer, {}))


if __name__ == "__main__":
    unittest.main()
