"""Cross-role mouseover macro headings, not executable macro tokens.

Source evidence: current Wowhead Guardian/Feral Druid, Restoration
Druid/Shaman, Preservation Evoker, and Outlaw Rogue UI & Macros guides.
No claim about the rendered Chrome translation.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class MouseoverMacroGlossaryTests(unittest.TestCase):
    def test_reusable_headings_not_entire_sentences(self):
        expected = {
            "mouseover macro": "macro mouseover",
            "mouseover macros": "macros mouseover",
            "Mouseover Macro": "Macro mouseover",
            "Mouseover Macros": "Macros mouseover",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)

    def test_macro_tokens_and_verb_are_not_rewritten(self):
        for source in ("@mouseover", "mouseover", "mouse over", "mouse-over",
                       "/cast [@mouseover]", "mouseover cast"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_locale_isolation_and_same_language_skip(self):
        self.assertEqual(select_jargon(GLOSSARY, "en-US", "fr-FR")["mouseover macros"],
                         "macros mouseover")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "de", "fr")

    def test_existing_independent_roles_and_macro_sections(self):
        by_id = {p["id"]: p["url"] for p in PAGES}
        for guide in ("guardian-druid-ui-macros", "feral-druid-ui-macros",
                      "restoration-shaman-ui-macros", "restoration-druid-ui-macros",
                      "preservation-evoker-ui-macros", "outlaw-rogue-ui-macros"):
            with self.subTest(guide=guide):
                self.assertIn(guide, by_id)
                self.assertTrue(by_id[guide].endswith("/addons-macro-ui-imports"))


if __name__ == "__main__":
    unittest.main()
