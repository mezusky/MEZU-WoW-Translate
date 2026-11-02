"""Cross-class auto-attack wording: Classic Rogue/Warrior and Forever Arms/Prot.

Source-only data contract. This does not replay the browser Translator API,
DOM segmentation, or actual French page rendering.
"""
import unittest
from pathlib import Path

from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class AutoAttackCrossClassLocaleTests(unittest.TestCase):
    def test_hyphenated_and_spaced_variants_share_one_locale_rule(self):
        player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(player, "en-US", "fr-FR")
        for source in ("auto-attack", "auto attack"):
            self.assertEqual(terms[source], "attaque automatique")
        for source in ("auto-attacks", "auto attacks"):
            self.assertEqual(terms[source], "attaques automatiques")
        self.assertEqual(terms["Auto Attack"], "Attaque automatique")
        self.assertEqual(terms["Auto Attacks"], "Attaques automatiques")

        # Bare attack/swing would overtranslate other combat concepts.
        for ambiguous in ("attack", "attacks", "swing", "next"):
            self.assertNotIn(ambiguous, terms)

    def test_legacy_overrides_are_not_duplicated(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("jargon", "exact"):
            for source in ("auto-attack", "auto-attacks", "auto attack",
                           "auto attacks", "Auto Attack", "Auto Attacks"):
                self.assertNotIn(source, manual.get(layer, {}))

    def test_locale_direction_isolated(self):
        player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(player, "en-US", "de-DE")

    def test_source_guides_remain_in_regression_corpus(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {entry["url"] for entry in corpus["pages"]}
        for suffix in (
            "forever/guide/classes/warrior/arms/dps-abilities",
            "forever/guide/classes/warrior/protection/tank-abilities",
            "classic/guide/classes/rogue/dps-rotation-cooldowns-abilities-pve",
            "classic/guide/classes/warrior/tank-rotation-cooldowns-abilities-pve",
        ):
            self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
