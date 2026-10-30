"""Cross-role, multilingual regression: source-only audits must not borrow a pack."""
import unittest

from scripts.audit_locale_contract import resolve_audit_locale_contract


class AuditLocaleContractTests(unittest.TestCase):
    PACK = {"sourceLanguage": "en", "targetLanguage": "fr"}

    def check(self, source, target, status, pack=None):
        result = resolve_audit_locale_contract(
            {"sourceLanguage": source, "targetLanguage": target},
            self.PACK if pack is None else pack,
        )
        self.assertEqual(result["status"], status)
        self.assertEqual(result["canScore"], status == "ready")
        return result

    def test_existing_en_fr_and_regional_aliases(self):
        self.check("en", "fr", "ready")
        result = self.check("en_US", "fr-FR", "ready")
        self.assertEqual((result["sourceLanguage"], result["targetLanguage"]),
                         ("en-us", "fr-fr"))

    def test_same_language_skips_translation_even_across_regions(self):
        for source, target in (("en-US", "en-GB"), ("fr-FR", "fr-CA"),
                               ("de-DE", "de-AT"), ("en", "en")):
            with self.subTest(source=source, target=target):
                self.check(source, target, "skipped_same_language")

    def test_other_translation_directions_never_use_en_fr_glossary(self):
        for source, target in (("fr", "en"), ("en", "de"), ("de", "fr"),
                               ("es-MX", "pt-BR")):
            with self.subTest(source=source, target=target):
                self.check(source, target, "pack_locale_mismatch")

    def test_region_specific_pack_cannot_leak_to_other_regions(self):
        pack = {"sourceLanguage": "en-US", "targetLanguage": "fr-FR"}
        self.check("en-US", "fr-FR", "ready", pack)
        self.check("en-GB", "fr-FR", "pack_locale_mismatch", pack)
        self.check("en", "fr", "pack_locale_mismatch", pack)
        self.check("en-US", "fr-CA", "pack_locale_mismatch", pack)

    def test_invalid_or_missing_metadata_fails_closed(self):
        for source, target in (("", "fr"), ("english", "fr"),
                               ("en", "fr-???"), (None, "fr")):
            with self.subTest(source=source, target=target):
                self.check(source, target, "invalid_locale")
        self.assertEqual(resolve_audit_locale_contract({}, {})["status"],
                         "invalid_locale")
        with self.assertRaises(ValueError):
            resolve_audit_locale_contract([], self.PACK)

    def test_no_hardcoded_french_target(self):
        self.check("de-DE", "es-ES", "ready",
                   {"sourceLanguage": "de", "targetLanguage": "es"})


if __name__ == "__main__":
    unittest.main()
