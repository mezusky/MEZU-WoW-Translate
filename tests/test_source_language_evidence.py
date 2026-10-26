"""Content-language evidence must be conservative across unrelated WoW roles.

Synthetic guide prose models indexed English leveling/rotation pages with
localized spell names. This does not validate Chrome language detection.
"""
import json
import unittest
from pathlib import Path
from scripts.source_language_evidence import detect_source_language

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "data/audit_language_signals.json").read_text(
    encoding="utf-8"))["profiles"]


class SourceLanguageEvidenceTests(unittest.TestCase):
    def test_english_rogue_leveling_prose(self):
        prose = ("Welcome to the Outlaw Rogue leveling guide. This guide goes "
                 "through various tips and tricks to optimize your journey when "
                 "leveling your character. It includes a breakdown of rotations "
                 "and cooldown usage that suit a leveling character, as well as "
                 "links to the best leveling talent builds.")
        result = detect_source_language([("p", prose)], PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")

    def test_english_evoker_prose_with_french_spell_names(self):
        prose = ("Keep Empower abilities on cooldown: Souffle onirique and Souffle "
                 "de feu are two of your highest value spells. While you won't "
                 "keep them on cooldown all of the time, you should have very "
                 "high casts per minute of both by the end of a fight.")
        self.assertEqual(detect_source_language([("li", prose)], PROFILES)
                         ["detectedLanguage"], "en")

    def test_french_prose_with_english_spell_names(self):
        prose = ("Bienvenue dans ce guide pour votre personnage. Vous pouvez "
                 "utiliser vos sorts lorsque les ennemis sont proches. Cette "
                 "spécialisation possède des capacités de soin très utiles pour "
                 "votre groupe et permet de progresser avec les autres joueurs. "
                 "Vous pouvez aussi utiliser Death Strike pour faire des soins.")
        self.assertEqual(detect_source_language([("p", prose)], PROFILES)
                         ["detectedLanguage"], "fr")

    def test_german_and_italian_prose_are_not_english(self):
        german = ("In diesem Guide zeigen wir euch die besten Talente und "
                  "Fähigkeiten für eure Klasse. Ihr könnt mit diesen Fähigkeiten "
                  "eure Gegner besiegen und solltet dabei auf eure Abklingzeiten "
                  "achten. Die wichtigsten Zauber werden hier erklärt.")
        italian = ("In questa guida vedremo come usare le abilità per il tuo "
                   "personaggio. Quando hai bisogno di migliorare puoi scegliere "
                   "questa specializzazione con una buona combinazione di talenti "
                   "e capacità. Queste sono le migliori opzioni per giocare.")
        self.assertEqual(detect_source_language([("p", german)], PROFILES)
                         ["detectedLanguage"], "de")
        self.assertEqual(detect_source_language([("p", italian)], PROFILES)
                         ["detectedLanguage"], "it")

    def test_short_ambiguous_prose_does_not_claim_a_language(self):
        result = detect_source_language([("li", "Use Evasion on cooldown.")], PROFILES)
        self.assertIsNone(result["detectedLanguage"])
        self.assertEqual(result["status"], "insufficient_prose")

    def test_headings_and_repeated_widget_payload_do_not_dominate(self):
        french = ("Bienvenue dans ce guide pour votre personnage. Vous pouvez "
                  "utiliser vos sorts lorsque les ennemis sont proches. Cette "
                  "spécialisation possède des capacités de soin très utiles pour "
                  "votre groupe et permet de progresser avec les autres joueurs.")
        blocks = [("h1", "English Guide for the Best Talent Builds"),
                  ("p", french), ("p", french),
                  ("p", "Export Talents Open in Calculator " + "the " * 600)]
        result = detect_source_language(blocks, PROFILES)
        self.assertEqual(result["detectedLanguage"], "fr")
        self.assertLess(result["tokenCount"], 60)

    def test_new_language_is_data_only(self):
        portuguese = {"pt": ["para", "quando", "você", "também", "com", "seus",
                              "suas", "pode", "usar", "habilidades"]}
        text = ("Quando você pode usar suas habilidades para ajudar seus aliados, "
                "você também pode usar suas habilidades com seus aliados. "
                "Quando você pode usar suas habilidades para ajudar seus aliados, "
                "você também pode usar suas habilidades com seus aliados.")
        result = detect_source_language([("p", text)], portuguese)
        self.assertEqual(result["detectedLanguage"], "pt")

    def test_bad_profiles_fail_closed(self):
        with self.assertRaises(ValueError):
            detect_source_language([], {"en": ["the"], "fr": [None]})


if __name__ == "__main__":
    unittest.main()
