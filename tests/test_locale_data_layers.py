"""Regression checks: never merge French data into another locale pack."""
import unittest
from scripts.locale_glossary import select_locale_data


class LocaleDataLayerTests(unittest.TestCase):
    def test_blizzard_regional_memory_accepted_by_generic_pack(self):
        memory = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR",
                  "exact": {"Use your cooldown": "Utilisez votre CD"}}
        self.assertIs(select_locale_data(memory, "en", "fr"), memory)
        self.assertEqual(select_locale_data(memory, "de", "fr"), {})
        self.assertEqual(select_locale_data(memory, "en", "de"), {})
        self.assertEqual(select_locale_data(memory, "fr", "en"), {})

    def test_region_specific_data_cannot_leak_across_regions(self):
        memory = {"sourceLanguage": "en-US", "targetLanguage": "fr-CA",
                  "exact": {"Shield": "Bouclier"}}
        self.assertEqual(select_locale_data(memory, "en", "fr-FR"), {})
        self.assertIs(select_locale_data(memory, "en", "fr"), memory)

    def test_legacy_untagged_layers_are_only_current_en_fr(self):
        legacy = {"exact": {"Haste": "Hâte"}}
        self.assertIs(select_locale_data(legacy, "en", "fr",
                                         legacy_pair=("en", "fr")), legacy)
        for source, target in (("de", "fr"), ("en", "de"), ("fr", "en"),
                               ("en-US", "fr-FR")):
            with self.subTest(source=source, target=target):
                self.assertEqual(select_locale_data(legacy, source, target,
                                                    legacy_pair=("en", "fr")), {})
        self.assertEqual(select_locale_data(legacy, "en", "fr"), {})

    def test_same_language_skips_even_with_different_region(self):
        memory = {"sourceLanguage": "en", "targetLanguage": "en",
                  "exact": {"Haste": "Haste"}}
        self.assertEqual(select_locale_data(memory, "en-US", "en-GB"), {})

    def test_incomplete_or_invalid_metadata_fails_closed(self):
        with self.assertRaises(ValueError):
            select_locale_data({"sourceLanguage": "en"}, "en", "fr")
        with self.assertRaises(ValueError):
            select_locale_data({"sourceLanguage": "", "targetLanguage": "fr"},
                               "en", "fr")
        with self.assertRaises(ValueError):
            select_locale_data([], "en", "fr")


if __name__ == "__main__":
    unittest.main()
