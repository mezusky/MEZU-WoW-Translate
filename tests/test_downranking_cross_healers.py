"""Spell-rank economy terminology across unrelated healer guides.

Grounded in indexed EN Wowhead sources for Forever Discipline/Holy Priest,
WotLK Restoration Shaman and TBC Priest. This checks the data contract, not
Chrome's browser-only translation behavior.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class DownrankingLocaleTests(unittest.TestCase):
    def test_spell_rank_terms_are_localized_without_whole_sentence_overrides(self):
        glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual((glossary["sourceLanguage"], glossary["targetLanguage"]),
                         ("en", "fr"))
        jargon = glossary["jargon"]
        self.assertEqual(jargon["downranking"], "utilisation d’un sort de rang inférieur")
        self.assertEqual(jargon["Downranking"], "Utilisation d’un sort de rang inférieur")
        self.assertEqual(jargon["downrank"], "utiliser un sort de rang inférieur")
        self.assertEqual(jargon["Downrank"], "Utiliser un sort de rang inférieur")

        # A bare "rank" is ambiguous (PvP rank, item rank, spell rank).
        for ambiguous in ("rank", "ranks", "ranking", "down", "lower rank"):
            self.assertNotIn(ambiguous, jargon)

        manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        for layer in ("exact", "jargon"):
            for phrase in ("downranking", "Downranking", "downrank", "Downrank"):
                self.assertNotIn(phrase, manual.get(layer, {}))

    def test_term_selection_respects_requested_locale_pair(self):
        from scripts.locale_glossary import select_jargon

        glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        selected = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(selected["downranking"], "utilisation d’un sort de rang inférieur")
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "de-DE")


if __name__ == "__main__":
    unittest.main()
