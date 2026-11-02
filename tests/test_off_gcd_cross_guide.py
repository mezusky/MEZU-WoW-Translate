"""Cross-class source-only contract for off-GCD terminology.

Sources: Forever Retribution Paladin abilities and Protection Warrior rotation.
This tests the Data Pack inputs, not Chrome Translator API or DOM output.
"""
import unittest
from pathlib import Path
from scripts.locale_glossary import parse_json_unique_keys, select_jargon


class OffGcdCrossGuideTests(unittest.TestCase):
    def test_paladin_and_warrior_use_one_locale_scoped_concept(self):
        root = Path(__file__).resolve().parents[1] / "data"
        player = parse_json_unique_keys(
            (root / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        manual = parse_json_unique_keys(
            (root / "manual_overrides.json").read_text(encoding="utf-8"))
        terms = select_jargon(player, "en-US", "fr-FR")
        # Paladin Retribution: "Judgement is an off-the-GCD ability".
        self.assertEqual(terms["off-the-GCD"], "hors GCD")
        # Warrior Protection: "Not on GCD" in the priority list.
        self.assertEqual(terms["Not on GCD"], "hors GCD")
        self.assertEqual(terms["off the GCD"], "hors GCD")
        for source in ("off-the-GCD", "Not on GCD"):
            self.assertNotIn(source, manual.get("jargon", {}))
            self.assertNotIn(source, manual.get("exact", {}))
        # Do not rewrite the generic word "cooldown": it also means
        # an ability being unavailable, a different gameplay concept.
        self.assertNotIn("cooldown", terms)
        self.assertEqual(select_jargon(player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(player, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
