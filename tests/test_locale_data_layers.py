"""Regression checks: never merge French data into another locale pack."""
import unittest
from scripts.locale_glossary import select_locale_data


class LocaleDataLayerTests(unittest.TestCase):
    def test_blizzard_regional_memory_accepted_by_generic_pack(self):
        memory = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR",
                  "exact": {"Use your cooldown": "Utilisez votre CD"}}
        self.assertEqual(select_locale_data(memory, "en", "fr"), {})
        self.assertIs(select_locale_data(memory, "en", "fr",
                                        canonical_pair=("en-US", "fr-FR")), memory)
        self.assertEqual(select_locale_data(memory, "de", "fr",
                                            canonical_pair=("en-US", "fr-FR")), {})
        self.assertEqual(select_locale_data(memory, "en", "de",
                                            canonical_pair=("en-US", "fr-FR")), {})
        self.assertEqual(select_locale_data(memory, "fr", "en",
                                            canonical_pair=("en-US", "fr-FR")), {})

    def test_region_specific_data_cannot_leak_across_regions(self):
        memory = {"sourceLanguage": "en-US", "targetLanguage": "fr-CA",
                  "exact": {"Shield": "Bouclier"}}
        self.assertEqual(select_locale_data(memory, "en", "fr-FR"), {})
        self.assertEqual(select_locale_data(memory, "en", "fr"), {})
        self.assertEqual(select_locale_data(memory, "en", "fr",
                                            canonical_pair=("en-US", "fr-FR")), {})

    def test_canonical_pair_does_not_cross_regional_requests(self):
        memory = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR",
                  "exact": {"Haste": "Hâte"}}
        pair = ("en-US", "fr-FR")
        self.assertEqual(select_locale_data(memory, "en-GB", "fr",
                                            canonical_pair=pair), {})
        self.assertEqual(select_locale_data(memory, "en", "fr-CA",
                                            canonical_pair=pair), {})
        self.assertIs(select_locale_data(memory, "en-US", "fr-FR",
                                         canonical_pair=pair), memory)
        with self.assertRaises(ValueError):
            select_locale_data(memory, "en", "fr", canonical_pair=("en-US",))

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
