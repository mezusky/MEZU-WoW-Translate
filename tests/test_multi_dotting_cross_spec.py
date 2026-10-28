"""Protect WoW multi-DoT jargon across independent English Wowhead guides.

Evidence: Shadow Priest Midnight Season 2/Mythic+ ("multi dotting"),
Beast Mastery Hunter Midnight pre-patch ("multi-dotting"), and
historical Shadow raid ("multi dotting adds"). Classic guides corroborate
the heading form, but do not define current gameplay mechanics.
This validates data only; Chrome Translator API/DOM output is not exercised.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))


class MultiDottingCrossSpecTests(unittest.TestCase):
    def test_attested_variants_share_a_reusable_player_term(self):
        expected = {
            "multi-dotting": "multi-DoT",
            "multi dotting": "multi-DoT",
            "Multi-Dotting": "Multi-DoT",
            "multi-DoTting": "multi-DoT",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_avoid_overbroad_dot_and_verb_rules(self):
        for source in ("dot", "DoT", "dotting", "redot", "multi", "multi-dot"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_locale_isolation(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["multi-dotting"], "multi-DoT")
        self.assertEqual(terms["multi dotting"], "multi-DoT")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "es")


if __name__ == "__main__":
    unittest.main()
