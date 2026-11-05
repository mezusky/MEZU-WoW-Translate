"""Regression checks for captured-output auditing; no browser API required."""
import unittest
from scripts.audit_translation_samples import audit_sample


class TranslationSampleAuditTests(unittest.TestCase):
    def test_unrelated_glossary_entity_does_not_fail(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Haste reduces the global cooldown.",
                  "translated": "La hâte réduit le temps de recharge global.",
                  "entities": [{"id": 123, "targetName": "Nom absent"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_referenced_entity_requires_official_name(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 in your rotation.",
                  "translated": "Utilisez spell=123 dans votre rotation.",
                  "entities": [{"id": 123, "targetName": "Nom officiel"}]}
        self.assertIn("missing_target_entity:123", audit_sample(sample))

    def test_preserved_entity_name_passes(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 in your rotation.",
                  "translated": "Utilisez Nom officiel (spell=123) dans votre rotation.",
                  "entities": [{"id": 123, "targetName": "Nom officiel"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_same_language_no_translation(self):
        sample = {"sourceLanguage": "fr-FR", "targetLanguage": "fr-FR",
                  "source": "Bonjour", "translated": "Bonjour"}
        self.assertEqual(audit_sample(sample), [])


if __name__ == "__main__":
    unittest.main()
