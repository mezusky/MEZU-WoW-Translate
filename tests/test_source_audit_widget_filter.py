"""Source-only audit filtering: multilingual prose vs. serialized guide widgets.

Examples are compact observations from indexed Wowhead cheat sheets and
rotation pages; they do not represent Chrome Translator API output.
"""
import json
import unittest
from pathlib import Path

from scripts.source_language_evidence import audit_source_prose, detect_source_language

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "data/audit_language_signals.json").read_text(
    encoding="utf-8"))["profiles"]


class SourceAuditWidgetFilterTests(unittest.TestCase):
    def test_independent_cheat_sheet_sources_remain_in_regression_corpus(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(
            encoding="utf-8"))["pages"]
        ids = {page["id"] for page in pages}
        self.assertTrue({
            "affliction-warlock-cheat-sheet",
            "arcane-mage-cheat-sheet",
            "balance-druid-cheat-sheet",
        }.issubset(ids))

    def test_three_unrelated_cheat_sheet_stat_widgets_are_not_prose(self):
        widgets = (
            "stat-guide=5525 stats=intellect>>Haste>Crit>Mastery>Versatility]",
            "stat-guide=5554 stats=int>>haste>>versatility=crit=mastery]",
            "stat-guide=5542 stats=int>mastery>crit>>haste>vers]",
        )
        for widget in widgets:
            with self.subTest(widget=widget[:20]):
                clean, has_prose = audit_source_prose(widget, "en-US", PROFILES)
                self.assertFalse(has_prose)
                self.assertNotIn("stat-guide=", clean)
                self.assertNotIn("stats=", clean)

    def test_widget_payload_does_not_erase_real_english_prose(self):
        value = ("Your spells and abilities should be used before the next "
                 "fight. stat-guide=5525 stats=intellect>>Haste>Crit]")
        clean, has_prose = audit_source_prose(value, "en-GB", PROFILES)
        self.assertTrue(has_prose)
        self.assertIn("Your spells and abilities", clean)
        self.assertNotIn("stat-guide=", clean)

    def test_french_and_german_source_are_not_filtered_by_english(self):
        examples = (
            ("fr-FR", "Vous pouvez utiliser vos sorts avant le combat.", True),
            ("de-DE", "Ihr könnt diese Fähigkeiten auch vor dem Kampf verwenden.", True),
            ("fr-FR", "Your spells should be used before combat.", False),
            ("it-IT", "Quando puoi usare le abilità prima del combattimento.", True),
        )
        for locale, value, expected in examples:
            with self.subTest(locale=locale, value=value[:12]):
                self.assertEqual(audit_source_prose(value, locale, PROFILES)[1], expected)

    def test_generated_placeholder_is_not_a_language_signal(self):
        clean, has_prose = audit_source_prose(
            "UTIL3_USECASE DUNGEON_2_TALENT_OPTION stats=int>mastery>haste]",
            "en-US", PROFILES)
        self.assertFalse(has_prose)
        self.assertNotIn("UTIL3_USECASE", clean)

    def test_opaque_imports_from_independent_ui_guides_are_not_prose(self):
        # Indexed Augmentation Evoker and Holy Priest UI guides expose CDM
        # import payloads. Use synthetic strings, not copied full profiles.
        for class_name in ("Augmentation Evoker", "Holy Priest"):
            with self.subTest(class_name=class_name):
                payload = "1|" + "LY+9TkJREIQBzbwCDhWGF7ChoDLEB6C49ogRhYKfAhRCgyfoM6CJGhJ7X8LG2IuCF8OPgBq0Ibf2zIXm253Z3Zw5rc1mZ"
                clean, has_prose = audit_source_prose(payload, "en-US", PROFILES)
                self.assertEqual(clean, "")
                self.assertFalse(has_prose)

    def test_opaque_import_filter_preserves_adjacent_prose_and_short_codes(self):
        payload = "1|" + "AbCdEf0123456789+/" * 6
        value = "You can import this profile and use it during combat. " + payload
        clean, has_prose = audit_source_prose(value, "en-US", PROFILES)
        self.assertTrue(has_prose)
        self.assertIn("You can import this profile", clean)
        self.assertNotIn(payload, clean)
        short, _ = audit_source_prose("Use build 1|abc123 for the raid.", "en", PROFILES)
        self.assertIn("1|abc123", short)

    def test_language_detection_ignores_import_payload_in_guide_table(self):
        prose = ("You should use your spells and abilities during the fight, "
                 "because they will help with your cooldowns and your damage. "
                 "After each cast you can use the other abilities when they "
                 "are ready, and this is how you keep your rotation going.")
        payload = "1|" + "AbCdEf0123456789+/" * 10
        blocks = [("p", prose), ("td", payload)]
        result = detect_source_language(blocks, PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")

    def test_missing_profile_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_source_prose("Some source text", "pt-BR", PROFILES)


if __name__ == "__main__":
    unittest.main()
