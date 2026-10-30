"""Generic builder/spender vocabulary belongs to the locale data layer.

Keep legacy whole-sentence exceptions unchanged until browser audits justify
removing them; this test prevents duplicate generic terms creeping back.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
MIGRATED = {
    "spender": "spender",
    "spenders": "spenders",
    "generator": "générateur",
    "generators": "générateurs",
    "builder-spender system": "système générateur/spender",
    "primary resource spender": "spender principal",
    "resource spender": "spender de ressource",
}


class BuilderSpenderLocaleTests(unittest.TestCase):
    def test_generic_terms_are_locale_scoped_and_not_duplicated(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(glossary, "en-US", "fr-FR")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for key, value in MIGRATED.items():
            with self.subTest(term=key):
                self.assertEqual(terms[key], value)
                self.assertNotIn(key, manual.get("jargon", {}))
                self.assertNotIn(key, manual.get("exact", {}))
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "es-ES")

    def test_unrelated_generator_spender_specs_are_sampled(self):
        urls = {p["url"] for p in json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]}
        for path in (
            "demon-hunter/vengeance/overview-pve-tank",
            "warlock/affliction/rotation-cooldowns-pve-dps",
            "shaman/enhancement/basics",
        ):
            with self.subTest(path=path):
                self.assertIn("https://www.wowhead.com/guide/classes/" + path, urls)


if __name__ == "__main__":
    unittest.main()
