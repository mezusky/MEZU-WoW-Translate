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

    def test_generated_utility_placeholders_do_not_dilute_english_prose(self):
        # Indexed Havoc M+ utility tables expose unfinished UTIL*_USECASE cells.
        prose = ("Your abilities should be used when the group takes damage, "
                 "and you can cast healing spells before the next wave while "
                 "you have mana for the fight.")
        blocks = [("td", prose + " " + "UTIL3_USECASE " * 120)]
        result = detect_source_language(blocks, PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")
        self.assertLess(result["tokenCount"], 40)

    def test_generated_placeholders_alone_are_not_language_evidence(self):
        blocks = [("td", "UTIL3_USECASE UTIL4_USECASE RAID_BOSS_TIP"),
                  ("li", "DUNGEON_2_TALENT_OPTION")]
        result = detect_source_language(blocks, PROFILES)
        self.assertIsNone(result["detectedLanguage"])
        self.assertEqual(result["status"], "insufficient_prose")
        self.assertEqual(result["tokenCount"], 0)

    def test_lowercase_underscores_remain_prose(self):
        prose = ("Your player_name can be used with the group when you have "
                 "the right spells and abilities for this fight. You should "
                 "also use your other spells before the next wave.")
        result = detect_source_language([("p", prose)], PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")
        self.assertGreaterEqual(result["tokenCount"], 25)

    def test_repeated_template_words_are_not_strong_language_evidence(self):
        # Synthetic noisy Wowhead-like table cells, not actual page output.
        # Repetition alone must not misclassify a source language.
        for locale, words in (("en", "the and "),
                              ("fr", "les des "),
                              ("de", "der und "),
                              ("it", "che per ")):
            with self.subTest(locale=locale):
                result = detect_source_language([("td", words * 45)], PROFILES)
                self.assertIsNone(result["detectedLanguage"])
                self.assertEqual(result["status"], "ambiguous")
                self.assertLessEqual(result["distinctSignalCounts"][locale], 2)

    def test_distinct_signals_preserve_independent_guide_prose(self):
        # Short source-only paraphrases of Arcane overview and Unholy basics;
        # no Chrome Translator API result is inferred from this evidence.
        examples = (
            "Your spells and abilities should be used when you have enough "
            "mana for the next burst window. The group can use this utility "
            "while you plan your defensive cooldowns and movement.",
            "You should use your cooldowns when they are available and "
            "spend your procs before the next fight. This can help your "
            "group while you have spells to cast during the encounter.",
        )
        for prose in examples:
            with self.subTest(prose=prose[:24]):
                result = detect_source_language([("p", prose)], PROFILES)
                self.assertEqual(result["detectedLanguage"], "en")
                self.assertGreaterEqual(result["distinctSignalCounts"]["en"], 4)

    def test_indexed_stat_widget_formulas_do_not_dilute_prose(self):
        # Devourer overview index repeats calculator configuration fields.
        # Only the surrounding prose may be used as language evidence.
        prose = ("Your abilities can be used when you have enough resources "
                 "for the next burst window. This guide explains how to use "
                 "your cooldowns and manage spells during a difficult fight.")
        widgets = ("stat-guide=32588 "
                   "stats=Int>mastery>haste>=crit>>versatility ")
        result = detect_source_language(
            [("p", prose + widgets * 100)], PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")
        self.assertLess(result["tokenCount"], 40)

    def test_key_value_widgets_alone_are_not_prose(self):
        widgets = ("stat-guide=32588 "
                   "stats=Int>mastery>haste>=crit>>versatility "
                   "talent-code=ABC123 " * 20)
        result = detect_source_language([("td", widgets)], PROFILES)
        self.assertIsNone(result["detectedLanguage"])
        self.assertEqual(result["status"], "insufficient_prose")
        self.assertEqual(result["tokenCount"], 0)

    def test_plain_stat_comparison_prose_is_not_stripped(self):
        # The filter targets assignment syntax, not ordinary guide advice.
        prose = ("You should use your spells when you have enough resources "
                 "and your abilities are ready. The stats of this gear can "
                 "help your group during the next fight, especially when "
                 "your damage and haste are higher than before.")
        result = detect_source_language([("p", prose)], PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")
        self.assertGreater(result["tokenCount"], 30)

    def test_bad_profiles_fail_closed(self):
        with self.assertRaises(ValueError):
            detect_source_language([], {"en": ["the"], "fr": [None]})


if __name__ == "__main__":
    unittest.main()
