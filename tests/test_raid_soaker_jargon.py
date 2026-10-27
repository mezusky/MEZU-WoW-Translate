"""Cross-role FR player jargon for raid soak assignments (source-only evidence).

Seen in Mistweaver Monk and Holy Paladin raid guides; also appears in
Destruction Warlock raid tips. No browser Translator API claim.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class RaidSoakerGlossaryTests(unittest.TestCase):
    def test_role_nouns_are_localized_without_overriding_the_verb(self):
        data = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual((data["sourceLanguage"], data["targetLanguage"]), ("en", "fr"))
        jargon = select_jargon(data, "en", "fr")
        self.assertEqual(jargon["soaker"], "joueur chargé du soak")
        self.assertEqual(jargon["soakers"], "joueurs chargés du soak")
        # Bare 'soak' has several grammatical uses (verb, noun, mechanic).
        # A context-free override would damage unrelated raid sentences.
        self.assertNotIn("soak", jargon)
        self.assertEqual(jargon["soak mechanic"], "mécanique de soak")
        self.assertEqual(jargon["group soaks"], "soaks de groupe")
        self.assertEqual(select_jargon(data, "en-US", "fr-FR")["soakers"],
                         "joueurs chargés du soak")
        self.assertEqual(select_jargon(data, "en", "en"), {})
        with self.assertRaises(ValueError):
            select_jargon(data, "en", "de")


if __name__ == "__main__":
    unittest.main()
