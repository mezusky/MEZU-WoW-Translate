"""Contract tests for locale-scoped player terminology, independent of Wowhead."""
import json
import unittest
from pathlib import Path
from scripts.locale_glossary import locale_matches, select_jargon, select_locale_data, same_base_language


class LocaleGlossaryTests(unittest.TestCase):
    def setUp(self):
        self.fr = {
            "sourceLanguage": "en",
            "targetLanguage": "fr",
            "jargon": {"tier set": "set de classe", "socket": "châsse"},
        }

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
