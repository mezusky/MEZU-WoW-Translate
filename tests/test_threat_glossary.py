"""Cross-spec WoW tank threat terminology stays distinct from forum threads.

Evidence: live indexed English Blood DK basics and Brewmaster abilities guides.
This checks source terminology only, not Chrome Translator API output.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JARGON = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
    encoding="utf-8"))["jargon"]
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(
    encoding="utf-8"))["exact"]


class ThreatGlossaryTests(unittest.TestCase):
    def test_verified_tank_phrases_are_shared(self):
        self.assertEqual(JARGON["threat generation"], "génération de menace")
        self.assertEqual(JARGON["threat management"], "gestion de la menace")
        self.assertNotIn("threat generation", MANUAL)
        self.assertNotIn("threat management", MANUAL)

    def test_thread_typo_does_not_translate_forum_discussions(self):
        self.assertFalse(any("thread" in key.casefold() for key in JARGON))
        self.assertFalse(any("thread" in key.casefold() for key in MANUAL))
        # Only whole words should match: no accidental substring substitution.
        source = "Read the discussion thread before the raid."
        for key in ("threat generation", "threat management"):
            self.assertIsNone(re.search(r"(?<!\w)" + re.escape(key) + r"(?!\w)",
                                        source, re.IGNORECASE))

    def test_snap_threat_migration_is_cross_guide_and_locale_scoped(self):
        # Source-only evidence from independent Retail Vengeance DH and
        # Classic Blood DK/Protection Paladin guides, not browser output.
        from scripts.locale_glossary import select_jargon
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
            encoding="utf-8"))
        terms = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(terms["snap aggro"], "aggro instantanée")
        self.assertEqual(terms["snap threat"], "génération immédiate de menace")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for layer in ("exact", "jargon"):
            self.assertNotIn("snap aggro", manual.get(layer, {}))
            self.assertNotIn("snap threat", manual.get(layer, {}))
        self.assertNotIn("snap", terms)
        self.assertNotIn("threat", terms)
        for source, phrase in (
            ("Powerful opening burst, allowing for snap aggro.", "snap aggro"),
            ("perfect for establishing snap threat when swapping targets", "snap threat"),
            ("great snap threat and sustained threat", "snap threat"),
        ):
            with self.subTest(source=source):
                self.assertIsNotNone(re.search(
                    r"(?<!\\w)" + re.escape(phrase) + r"(?!\\w)",
                    source, re.IGNORECASE))
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en", "de")

    def test_independent_tank_pages_remain_in_corpus(self):
        pages = {p["id"] for p in json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(
                encoding="utf-8"))["pages"]}
        self.assertTrue({"blood-death-knight-basics",
                         "brewmaster-monk-talents"}.issubset(pages))


if __name__ == "__main__":
    unittest.main()
