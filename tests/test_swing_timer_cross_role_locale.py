"""Cross-page swing-timer terminology: melee and ranged auto-attacks.

Source-only locale/data contract; does not assert Chrome Translator API,
DOM reconstruction or actual French output.
"""
import unittest
from pathlib import Path

from scripts.locale_glossary import parse_json_unique_keys, select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class SwingTimerCrossRoleTests(unittest.TestCase):
    def test_player_term_is_preserved_across_melee_and_ranged_contexts(self):
        player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        terms = select_jargon(player, "en-US", "fr-FR")
        for term in ("swing timer", "swing timers", "swing-timer", "Swing Timer"):
            with self.subTest(term=term):
                self.assertEqual(terms[term], term)

        # The generic word 'swing' also describes attacks and animations.
        # Auto Shot is an official Hunter ability, not player jargon.
        for ambiguous in ("swing", "swings", "weapon", "Auto Shot"):
            self.assertNotIn(ambiguous, terms)

    def test_no_legacy_duplicate_or_cross_locale_leak(self):
        manual = parse_json_unique_keys(
            (DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("jargon", "exact"):
            for term in ("swing timer", "swing timers", "swing-timer", "Swing Timer"):
                self.assertNotIn(term, manual.get(layer, {}))
        player = parse_json_unique_keys(
            (DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(player, "fr-FR", "fr-FR"), {})
        with self.assertRaises(ValueError):
            select_jargon(player, "en-US", "de-DE")

    def test_independent_guides_are_in_corpus(self):
        corpus = parse_json_unique_keys(
            (DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))
        urls = {page["url"] for page in corpus["pages"]}
        for suffix in (
            "forever/guide/classes/warrior/arms/rotation-cooldowns-pve-dps",
            "classic/guide/classes/hunter/dps-rotation-cooldowns-abilities-pve",
            "classic/guide/classes/hunter/dps-addons",
            "wotlk/guide/classes/shaman/enhancement/dps-rotation-cooldowns-abilities-pve",
        ):
            self.assertIn("https://www.wowhead.com/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
