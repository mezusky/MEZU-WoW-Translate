"""Fail closed on malformed data-only multilingual audit profile keys.

English-source Wowhead prose can contain localized spell links; locale
metadata must not silently collapse malformed keys into an unrelated profile.
These checks are source-only and do not assert Chrome Translator API behavior.
"""
import unittest

from scripts.source_language_evidence import (
    audit_source_prose,
    compile_wow_term_signals,
    normalized_language_signals,
)


class LocaleSignalContractTests(unittest.TestCase):
    def test_regional_aliases_still_merge_into_base_language(self):
        result = normalized_language_signals({
            "en_US": ["the", "your"],
            "en-GB": ["should", "your"],
            "fr_FR": ["avec", "votre"],
            "zh-Hant-TW": ["使用"],
        })
        self.assertEqual(result["en"], {"the", "your", "should"})
        self.assertEqual(result["fr"], {"avec", "votre"})
        self.assertEqual(result["zh"], {"使用"})

    def test_malformed_locale_keys_fail_closed(self):
        for bad in ("english", "en--US", "en/../../fr", "fr\r\nX", "en-u", "123", "fr@FR"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    normalized_language_signals({bad: ["the"]})

    def test_malformed_wow_term_locale_cannot_leak_into_english(self):
        with self.assertRaises(ValueError):
            compile_wow_term_signals({"en--US": ["Holy Power"]}, "en-US")
        with self.assertRaises(ValueError):
            audit_source_prose("Use your spells.", "en", {"en/invalid": ["your"]})

    def test_valid_region_only_wow_terms_remain_scoped(self):
        data = {"en_US": ["Holy Power"], "fr_FR": ["Puissance sacrée"]}
        english = compile_wow_term_signals(data, "en-GB")
        french = compile_wow_term_signals(data, "fr-CA")
        self.assertIsNotNone(english.search("Holy Power"))
        self.assertIsNone(english.search("Puissance sacrée"))
        self.assertIsNotNone(french.search("Puissance sacrée"))
        self.assertIsNone(french.search("Holy Power"))


if __name__ == "__main__":
    unittest.main()
