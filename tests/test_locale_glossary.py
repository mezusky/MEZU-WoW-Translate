"""Contract tests for locale-scoped player terminology, independent of Wowhead."""
import json
import unittest
from pathlib import Path
from scripts.locale_glossary import (locale_matches, select_jargon, select_locale_data,
                                    same_base_language, parse_json_unique_keys)


class LocaleGlossaryTests(unittest.TestCase):
    def setUp(self):
        self.fr = {
            "sourceLanguage": "en",
            "targetLanguage": "fr",
            "jargon": {"tier set": "set de classe", "socket": "châsse"},
        }

    def test_player_glossary_source_has_unique_json_keys(self):
        # JSON normally keeps the last value, masking duplicated source rules.
        path = Path(__file__).resolve().parents[1] / "data" / "mezu_player_glossary.json"
        payload = parse_json_unique_keys(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["jargon"]["Avoid Downtime"], "Éviter les temps morts")
        self.assertEqual(payload["jargon"]["avoid downtime"], "éviter les temps morts")

    def test_duplicate_keys_fail_even_inside_nested_locale_data(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            parse_json_unique_keys('{"sourceLanguage":"en","jargon":{"term":"a","term":"b"}}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            parse_json_unique_keys('{"sourceLanguage":"en","sourceLanguage":"fr"}')
        # Capitalization is intentional in WoW headings and must remain valid.
        self.assertEqual(parse_json_unique_keys('{"Term":"A","term":"b"}'),
                         {"Term": "A", "term": "b"})

    def test_current_pack_and_regional_language_tags(self):
        self.assertEqual(select_jargon(self.fr, "en", "fr"), self.fr["jargon"])
        self.assertEqual(select_jargon(self.fr, "en-US", "fr-FR"), self.fr["jargon"])
        self.assertEqual(select_jargon(self.fr, "en_US", "fr_FR"), self.fr["jargon"])

    def test_wrong_target_language_fails_closed(self):
        with self.assertRaises(ValueError):
            select_jargon(self.fr, "en", "de")
        with self.assertRaises(ValueError):
            select_jargon(self.fr, "de", "fr")

    def test_specific_region_cannot_leak_into_another_region(self):
        canadian = {**self.fr, "targetLanguage": "fr-CA"}
        self.assertFalse(locale_matches("fr-CA", "fr-FR"))
        with self.assertRaises(ValueError):
            select_jargon(canadian, "en", "fr-FR")

    def test_pack_validator_same_base_language_contract(self):
        # The same helper is used by data selection and publication validation.
        # Regional changes must never publish a needless translation pack.
        for source, target in (("en-US", "en-GB"), ("fr-FR", "fr-CA"),
                               ("EN_us", "en"), ("pt-BR", "pt-PT")):
            with self.subTest(source=source, target=target):
                self.assertTrue(same_base_language(source, target))
                self.assertEqual(select_locale_data(self.fr, source, target), {})
        for source, target in (("en-US", "fr-FR"), ("de-DE", "fr-CA"),
                               ("pt-BR", "es-MX")):
            with self.subTest(source=source, target=target):
                self.assertFalse(same_base_language(source, target))
        with self.assertRaises(ValueError):
            same_base_language("", "fr")

    def test_wow_chinese_script_variants_are_not_the_same_language_output(self):
        # Official WoW locale tags distinguish simplified and traditional
        # Chinese even though both use the ISO base language "zh".
        for source, target in (("zh-CN", "zh-TW"),
                               ("zh-Hans", "zh-Hant"),
                               ("zh-SG", "zh-HK"),
                               ("sr-Cyrl", "sr-Latn")):
            with self.subTest(source=source, target=target):
                self.assertFalse(same_base_language(source, target))
        for source, target in (("zh-Hans", "zh-CN"),
                               ("zh-Hant", "zh-TW"),
                               ("en-US", "en-GB")):
            with self.subTest(source=source, target=target):
                self.assertTrue(same_base_language(source, target))

    def test_script_conversion_requires_explicit_directional_glossary(self):
        generic = {"sourceLanguage": "zh", "targetLanguage": "zh",
                   "jargon": {"test": "测试"}}
        specific = {"sourceLanguage": "zh-CN", "targetLanguage": "zh-TW",
                    "jargon": {"测试": "測試"}}
        # A generic same-language layer must never be silently reused as a
        # simplified -> traditional mapping (or in the reverse direction).
        with self.assertRaises(ValueError):
            select_jargon(generic, "zh-CN", "zh-TW")
        self.assertEqual(select_locale_data(generic, "zh-CN", "zh-TW"), {})
        self.assertEqual(select_jargon(specific, "zh-CN", "zh-TW"),
                         specific["jargon"])
        self.assertIs(select_locale_data(specific, "zh-CN", "zh-TW"), specific)
        self.assertEqual(select_locale_data(specific, "zh-TW", "zh-CN"), {})
        self.assertEqual(select_jargon(specific, "zh-TW", "zh-TW"), {})

    def test_identical_source_target_skips_translation(self):
        self.assertEqual(select_jargon(self.fr, "fr", "fr"), {})
        self.assertEqual(select_jargon(self.fr, "fr-FR", "fr_FR"), {})
        self.assertEqual(select_jargon(self.fr, "en-US", "en-GB"), {})

    def test_invalid_entries_fail_instead_of_shipping(self):
        with self.assertRaises(ValueError):
            select_jargon({**self.fr, "jargon": {"socket": ""}}, "en", "fr")
        with self.assertRaises(ValueError):
            select_jargon({**self.fr, "jargon": []}, "en", "fr")

    def test_returned_mapping_is_not_mutating_source(self):
        selected = select_jargon(self.fr, "en", "fr")
        selected["socket"] = "changed"
        self.assertEqual(self.fr["jargon"]["socket"], "châsse")


    def test_raidbots_cta_is_safe_across_specs_without_inline_sim_override(self):
        # A broad "sim your character" replacement breaks sentences such as
        # "you can easily sim your character"; let prose translation handle it.
        path = Path(__file__).resolve().parents[1] / "data" / "mezu_player_glossary.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        terms = select_jargon(payload, "en-US", "fr-FR")
        self.assertNotIn("sim your character", terms)
        self.assertEqual(
            terms["Simulate Your Character Now"],
            "Simulez votre personnage dès maintenant",
        )
        # This repeated Raidbots CTA occurs on unrelated Rogue, Warlock,
        # and Evoker stat guides. No spec-specific sentence override needed.
        self.assertEqual(
            select_jargon(payload, "en", "fr")["Simulate Your Character Now"],
            terms["Simulate Your Character Now"],
        )
        self.assertEqual(select_jargon(payload, "fr", "fr"), {})


    def test_self_dispel_jargon_is_locale_scoped_and_grammar_safe(self):
        # Seen in Mistweaver overview/Mythic+ and Windwalker overview:
        # preserve the distinction between the noun and conjugated verb.
        path = Path(__file__).resolve().parents[1] / "data" / "mezu_player_glossary.json"
        glossary = json.loads(path.read_text(encoding="utf-8"))
        terms = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(terms["self-dispel"], "dissipation sur soi-même")
        self.assertEqual(terms["self-dispels"], "dissipations sur soi-même")
        self.assertEqual(terms["Self Dispel"], "Dissipation sur soi-même")
        # Let the translation engine inflect verbs in full sentences.
        self.assertNotIn("self-dispelled", terms)
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "de-DE", "fr-FR")


class LocaleLayerDirectionTests(unittest.TestCase):
    def setUp(self):
        self.generic = {"sourceLanguage": "en", "targetLanguage": "fr",
                        "phrases": {"cooldown": "temps de recharge"}}

    def test_generic_layer_serves_regional_request(self):
        self.assertIs(select_locale_data(self.generic, "en-US", "fr-FR"), self.generic)
        self.assertIs(select_locale_data(self.generic, "en_GB", "fr_CA"), self.generic)

    def test_region_specific_layer_cannot_serve_generic_pack(self):
        regional = {**self.generic, "sourceLanguage": "en-US", "targetLanguage": "fr-FR"}
        self.assertEqual(select_locale_data(regional, "en", "fr"), {})
        self.assertEqual(select_locale_data(regional, "en-GB", "fr-FR"), {})
        self.assertEqual(select_locale_data(regional, "en-US", "fr-CA"), {})
        self.assertIs(select_locale_data(regional, "en-US", "fr-FR"), regional)

    def test_legacy_layers_only_serve_declared_pair(self):
        legacy = {"exact": {"socket": "châsse"}}
        self.assertIs(select_locale_data(legacy, "en", "fr", legacy_pair=("en", "fr")), legacy)
        self.assertEqual(select_locale_data(legacy, "en-US", "fr-FR", legacy_pair=("en", "fr")), {})
        self.assertEqual(select_locale_data(legacy, "en", "de", legacy_pair=("en", "fr")), {})

    def test_no_translation_for_same_language_and_no_partial_tags(self):
        self.assertEqual(select_locale_data(self.generic, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_locale_data({"sourceLanguage": "en"}, "en", "fr")


if __name__ == "__main__":
    unittest.main()
