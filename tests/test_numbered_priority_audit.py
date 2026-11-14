"""Cross-spec regression tests for numbered stat-priority structure.

Short excerpts model the two independent build lists found on live Wowhead
Blood Death Knight and Elemental Shaman stat pages (2026-11-14).
No guide content is stored or fetched by CI.
"""
import unittest

from scripts.audit_translation_samples import audit_sample


class NumberedPriorityAuditTests(unittest.TestCase):
    def sample(self, source, translated, enabled=True):
        return {
            "sourceLanguage": "en-US",
            "targetLanguage": "fr-FR",
            "source": source,
            "translated": translated,
            "preserveNumberedPriority": enabled,
        }

    def test_blood_dk_tied_stats_survive_localization(self):
        sample = self.sample(
            "1. Strength\n2. Haste\n3. Mastery / Critical Strike / Versatility",
            "1. Force\n2. Hâte\n3. Maîtrise / Coup critique / Polyvalence",
        )
        self.assertEqual(audit_sample(sample), [])

    def test_blood_dk_missing_tie_detected(self):
        sample = self.sample(
            "1. Strength\n2. Haste\n3. Mastery / Critical Strike / Versatility",
            "1. Force\n2. Hâte\n3. Maîtrise / Polyvalence",
        )
        self.assertIn("numbered_priority_structure_mismatch", audit_sample(sample))

    def test_elemental_shaman_missing_rank_detected(self):
        sample = self.sample(
            "1. Mastery to 1200 rating\n2. Haste/Crit\n3. Versatility\n4. Intellect",
            "1. Maîtrise jusqu'à 1 200\n2. Hâte/Critique\n4. Intelligence",
        )
        self.assertIn("numbered_priority_structure_mismatch", audit_sample(sample))

    def test_disabled_for_unscoped_guide_prose(self):
        sample = self.sample("1. Strength\n2. Haste", "1. Force", enabled=False)
        self.assertNotIn("numbered_priority_structure_mismatch", audit_sample(sample))

    def test_same_language_does_not_require_translation(self):
        sample = self.sample("1. Hâte\n2. Maîtrise", "1. Hâte\n2. Maîtrise")
        sample.update(sourceLanguage="fr-FR", targetLanguage="fr-CA")
        self.assertEqual(audit_sample(sample), [])


if __name__ == "__main__":
    unittest.main()
