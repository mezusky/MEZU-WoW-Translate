"""Regression checks for canonical WoW entity locale merging."""
import unittest
from scripts.merge_entity_locales import merge_rows, project_locale_pairs


class LocaleEntityTests(unittest.TestCase):
    def test_retains_existing_locales_on_partial_refresh(self):
        old = {"42": {"en": "Soul Shard", "fr": "éclat d'âme"}}
        new = {"42": {"de": "Seelensplitter"}}
        self.assertEqual(merge_rows(old, new)["42"], {
            "en": "Soul Shard", "fr": "éclat d'âme", "de": "Seelensplitter"
        })

    def test_ambiguous_source_not_projected(self):
        entities = {"spell": {
            "1": {"en": "Charge", "fr": "Charge"},
            "2": {"en": "Charge", "fr": "Charger"},
        }}
        self.assertNotIn("Charge", project_locale_pairs(entities, "en", "fr"))

    def test_missing_target_on_colliding_id_blocks_exact_mapping(self):
        # A matching English name with an untranslated canonical ID must
        # not borrow another ID's French name, even across entity types.
        entities = {
            "spell": {"1": {"en": "Shared", "fr": "Nom A"}},
            "item": {"2": {"en": "Shared"}, "3": {"en": "Unique", "fr": "Unique FR"}},
        }
        self.assertEqual(project_locale_pairs(entities, "en", "fr"),
                         {"Unique": "Unique FR"})

    def test_skip_identical_languages(self):
        entities = {"spell": {"1": {"en": "Charge", "fr": "Charge"}}}
        self.assertEqual(project_locale_pairs(entities, "fr", "fr"), {})


if __name__ == "__main__":
    unittest.main()
