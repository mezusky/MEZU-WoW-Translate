"""Locale-scoped phrase regression from independent current Wowhead guides.

Source-only evidence, not a claim of browser Translator API verification.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class AvoidDowntimePhraseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_phrase_is_reusable_without_overriding_contextual_downtime(self):
        jargon = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(jargon["Avoid Downtime"], "Éviter les temps morts")
        self.assertEqual(jargon["avoid downtime"], "éviter les temps morts")
        # A healer's downtime is often an opportunity to regenerate mana;
        # translating the bare word globally would change that meaning.
        self.assertNotIn("downtime", jargon)
        self.assertNotIn("Downtime", jargon)
        for layer in ("jargon", "exact"):
            for term in ("Avoid Downtime", "avoid downtime"):
                self.assertNotIn(term, self.manual.get(layer, {}))

    def test_cross_spec_source_coverage_and_language_isolation(self):
        urls = {page["url"] for page in self.pages}
        for suffix in (
            "warrior/arms/rotation-cooldowns-pve-dps",
            "warrior/fury/rotation-cooldowns-pve-dps",
            "evoker/devastation/rotation-cooldowns-pve-dps",
            "priest/discipline/rotation-cooldowns-pve-healer",
            "monk/mistweaver/rotation-cooldowns-pve-healer",
        ):
            self.assertIn("https://www.wowhead.com/guide/classes/" + suffix, urls)
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "de-DE", "fr-FR")


if __name__ == "__main__":
    unittest.main()
