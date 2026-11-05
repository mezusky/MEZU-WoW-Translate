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

    def test_official_name_typographic_variants_pass(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 during combat.",
                  "translated": "Utilisez L’IMAGE   DIVINE (spell=123) en combat.",
                  "entities": [{"type": "spell", "id": 123,
                                "targetName": "L'image divine"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_official_name_real_difference_still_fails(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 during combat.",
                  "translated": "Utilisez Image sombre (spell=123) en combat.",
                  "entities": [{"type": "spell", "id": 123,
                                "targetName": "Image divine"}]}
        self.assertIn("missing_target_entity:123", audit_sample(sample))

    def test_official_name_prefix_of_other_spell_does_not_pass(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 during combat.",
                  "translated": "Utilisez Frappe mortelle (spell=123) en combat.",
                  "entities": [{"type": "spell", "id": 123,
                                "targetName": "Frappe"}]}
        self.assertIn("missing_target_entity:123", audit_sample(sample))

    def test_official_name_with_punctuation_boundary_passes(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 during combat.",
                  "translated": "Utilisez (Frappe) (spell=123) en combat.",
                  "entities": [{"type": "spell", "id": 123,
                                "targetName": "Frappe"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_entity_kind_collision_detected(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 during combat.",
                  "translated": "Utilisez item=123 pendant le combat."}
        self.assertIn("entity_id_mismatch", audit_sample(sample))

    def test_target_name_only_required_for_matching_kind(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Equip item=123 before combat.",
                  "translated": "Équipez item=123 avant le combat.",
                  "entities": [{"type": "spell", "id": 123,
                                "targetName": "Sort officiel"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_target_name_required_for_matching_kind_and_id(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Equip item=123 before combat.",
                  "translated": "Équipez item=123 avant le combat.",
                  "entities": [{"type": "item", "id": 123,
                                "targetName": "Objet officiel"}]}
        self.assertIn("missing_target_entity:123", audit_sample(sample))

    def test_same_language_no_translation(self):
        sample = {"sourceLanguage": "fr-FR", "targetLanguage": "fr-FR",
                  "source": "Bonjour", "translated": "Bonjour"}
        self.assertEqual(audit_sample(sample), [])


if __name__ == "__main__":
    unittest.main()
