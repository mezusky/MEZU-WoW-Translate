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

    def test_official_name_suffix_inside_longer_word_fails(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 during combat.",
                  "translated": "Utilisez SuperFrappe (spell=123) en combat.",
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

    def test_other_entity_name_elsewhere_does_not_mask_wrong_label(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 after spell=456.",
                  "translated": "Utilisez Frappe mortelle (spell=123) après Frappe (spell=456).",
                  "entities": [{"type": "spell", "id": 123, "targetName": "Frappe"}]}
        self.assertIn("missing_target_entity:123", audit_sample(sample))

    def test_unbound_official_name_is_not_proof_of_entity_label(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123 after spell=456.",
                  "translated": "Utilisez spell=123 après Frappe (spell=456).",
                  "entities": [{"type": "spell", "id": 123,
                                "targetName": "Frappe"}]}
        self.assertIn("unverified_entity_label:123", audit_sample(sample))

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

    def test_untyped_item_label_infers_unique_kind(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Equip item=123.",
                  "translated": "Équipez Objet officiel (item=123).",
                  "entities": [{"id": 123, "targetName": "Objet officiel"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_untyped_collision_does_not_guess_kind(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Compare spell=123 and item=123.",
                  "translated": "Comparez Sort officiel (spell=123) et Objet officiel (item=123).",
                  "entities": [{"id": 123, "targetName": "Objet officiel"}]}
        self.assertIn("unverified_entity_label:123", audit_sample(sample))

    def test_repeated_spell_id_checks_all_labels(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use spell=123, then spell=123.",
                  "translated": "Utilisez Frappe (spell=123), puis Frappe mortelle (spell=123).",
                  "entities": [{"type": "spell", "id": 123, "targetName": "Frappe"}]}
        self.assertIn("missing_target_entity:123", audit_sample(sample))

    def test_repeated_item_id_correct_labels_pass(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Equip item=456, then compare item=456.",
                  "translated": "Équipez (Objet officiel) (item=456), puis comparez (Objet officiel) (item=456).",
                  "entities": [{"type": "item", "id": 456, "targetName": "Objet officiel"}]}
        self.assertEqual(audit_sample(sample), [])

    def test_percentages_preserved_with_french_spacing_and_decimal_comma(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Execute below 20% health; bonus increases by 3.5%.",
                  "translated": "Exécution sous 20 % de vie ; bonus augmenté de 3,5\u00a0%. "}
        self.assertEqual(audit_sample(sample), [])

    def test_changed_percentage_is_detected(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Use Execute below 20% health.",
                  "translated": "Utilisez Exécution sous 35 % de vie."}
        self.assertIn("percentage_mismatch", audit_sample(sample))

    def test_percentage_range_lower_bound_is_preserved(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Missing 10-20% of casts reduces damage.",
                  "translated": "Rater 15 à 20 % des sorts réduit les dégâts."}
        self.assertIn("percentage_mismatch", audit_sample(sample))

    def test_percentage_range_french_separator_is_accepted(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Missing 10-20% of casts reduces damage.",
                  "translated": "Rater 10 à 20 % des sorts réduit les dégâts."}
        self.assertEqual(audit_sample(sample), [])

    def test_between_percentage_range_preserves_both_bounds(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Between 10 and 20% of casts can be missed.",
                  "translated": "Entre 15 et 20 % des sorts peuvent être ratés."}
        self.assertIn("percentage_mismatch", audit_sample(sample))

    def test_between_percentage_range_accepts_french_equivalent(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Between 10 and 20% of casts can be missed.",
                  "translated": "Entre 10 et 20 % des sorts peuvent être ratés."}
        self.assertEqual(audit_sample(sample), [])

    def test_written_range_to_single_percentage_detected(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Between 10 and 20% of casts may miss.",
                  "translated": "Jusqu'à 20 % des sorts peuvent rater."}
        self.assertIn("percentage_mismatch", audit_sample(sample))

    def test_written_range_changed_to_other_written_range_detected(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Between 10 and 20% of casts may miss.",
                  "translated": "Entre 15 et 20 % des sorts peuvent rater."}
        self.assertIn("percentage_mismatch", audit_sample(sample))

    def test_written_range_equivalence_preserves_both_endpoints(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Between 10 and 20% of casts may miss.",
                  "translated": "Entre 10 et 20 % des sorts peuvent rater."}
        self.assertEqual(audit_sample(sample), [])

    def test_same_language_no_translation(self):
        sample = {"sourceLanguage": "fr-FR", "targetLanguage": "fr-FR",
                  "source": "Bonjour", "translated": "Bonjour"}
        self.assertEqual(audit_sample(sample), [])


    def test_same_language_different_region_requires_no_translation(self):
        sample = {"sourceLanguage": "en-US", "targetLanguage": "en-GB",
                  "source": "Use your cooldowns.", "translated": "Use your cooldowns."}
        self.assertEqual(audit_sample(sample), [])

    def test_same_language_different_region_flags_unwanted_change(self):
        sample = {"sourceLanguage": "fr-CA", "targetLanguage": "fr-FR",
                  "source": "Utilisez vos sorts.", "translated": "Utilisez vos compétences."}
        self.assertIn("same_language_changed", audit_sample(sample))

    def test_different_languages_still_audited(self):
        sample = {"sourceLanguage": "en-US", "targetLanguage": "fr-CA",
                  "source": "Use your cooldowns.", "translated": "Use your cooldowns."}
        self.assertIn("unchanged_prose_review", audit_sample(sample))


    def test_different_explicit_scripts_are_not_skipped(self):
        sample = {"sourceLanguage": "zh-Hans", "targetLanguage": "zh-Hant",
                  "source": "使用你的技能并提高伤害", "translated": "使用你的技能并提高伤害"}
        self.assertIn("unchanged_prose_review", audit_sample(sample))


if __name__ == "__main__":
    unittest.main()
