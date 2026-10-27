"""Cross-role FR player jargon for raid soak assignments (source-only evidence).

Seen in Mistweaver Monk and Holy Paladin raid guides; also appears in
Destruction Warlock raid tips. No browser Translator API claim.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RaidSoakerGlossaryTests(unittest.TestCase):
    def test_role_nouns_are_localized_without_overriding_the_verb(self):
        data = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual((data["sourceLanguage"], data["targetLanguage"]), ("en", "fr"))
        jargon = data["jargon"]
        self.assertEqual(jargon["soaker"], "joueur chargé du soak")
        self.assertEqual(jargon["soakers"], "joueurs chargés du soak")
        # Bare 'soak' has several grammatical uses (verb, noun, mechanic).
        # A context-free override would damage unrelated raid sentences.
        self.assertNotIn("soak", jargon)
        self.assertEqual(jargon["soak mechanic"], "mécanique de soak")
        self.assertEqual(jargon["group soaks"], "soaks de groupe")


if __name__ == "__main__":
    unittest.main()
