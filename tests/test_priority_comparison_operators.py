"""Regression checks for stat-priority relation preservation across locales."""
import unittest
from scripts.audit_translation_samples import audit_sample, priority_operators


class PriorityComparisonTests(unittest.TestCase):
    def test_comparators(self):
        self.assertEqual(priority_operators('A > B >> C < D <= E >= F = G'),
                         ['>', '>>', '<', '<=', '>=', '='])

    def test_changed_comparison_detected(self):
        sample = dict(sourceLanguage='en', targetLanguage='fr',
                      source='Haste < Mastery', translated='Hâte > Maîtrise',
                      preserveStatPriority=True)
        self.assertIn('stat_priority_relation_mismatch', audit_sample(sample))

    def test_localized_labels_same_comparison(self):
        sample = dict(sourceLanguage='en', targetLanguage='fr',
                      source='Haste <= Mastery', translated='Hâte <= Maîtrise',
                      preserveStatPriority=True)
        self.assertNotIn('stat_priority_relation_mismatch', audit_sample(sample))


if __name__ == '__main__':
    unittest.main()
