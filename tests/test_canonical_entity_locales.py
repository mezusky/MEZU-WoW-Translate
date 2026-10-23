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

    def test_non_english_source_projects_through_canonical_id(self):
        entities = {"spell": {
            "100": {"en": "Holy Shock", "de": "Heiliger Schock", "fr": "Horion sacré"},
            "101": {"en": "Rejuvenation", "de": "Verjüngung", "fr": "Récupération"},
        }}
        self.assertEqual(project_locale_pairs(entities, "de", "fr"), {
            "Heiliger Schock": "Horion sacré",
            "Verjüngung": "Récupération",
        })
        self.assertEqual(project_locale_pairs(entities, "fr", "de"), {
            "Horion sacré": "Heiliger Schock",
            "Récupération": "Verjüngung",
        })

    def test_regional_request_uses_generic_canonical_names(self):
        entities = {"spell": {"100": {"en": "Holy Shock", "fr": "Horion sacré"}}}
        self.assertEqual(project_locale_pairs(entities, "en-US", "fr-FR"),
                         {"Holy Shock": "Horion sacré"})
        self.assertEqual(project_locale_pairs(entities, "en_US", "fr_FR"),
                         {"Holy Shock": "Horion sacré"})

    def test_regional_exact_names_win_without_cross_region_leak(self):
        entities = {"spell": {
            "1": {"en": "Color", "fr": "Couleur", "fr-CA": "Couleur canadienne"},
            "2": {"en": "Regional", "fr-CA": "Régional canadien"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en-US", "fr-CA"),
                         {"Color": "Couleur canadienne", "Regional": "Régional canadien"})
        self.assertEqual(project_locale_pairs(entities, "en-US", "fr-FR"),
                         {"Color": "Couleur"})
        # A specific regional name cannot be used for a generic target.
        self.assertEqual(project_locale_pairs(
            {"spell": {"2": entities["spell"]["2"]}}, "en", "fr"), {})

    def test_regional_requests_preserve_ambiguity_guard(self):
        entities = {"spell": {
            "1": {"en": "Charge", "fr": "Charge"},
            "2": {"en": "Charge", "fr": "Charger"},
        }}
        self.assertNotIn("Charge", project_locale_pairs(entities, "en-US", "fr-FR"))

    def test_skip_identical_languages(self):
        entities = {"spell": {"1": {"en": "Charge", "fr": "Charge"}}}
        self.assertEqual(project_locale_pairs(entities, "fr", "fr"), {})
        self.assertEqual(project_locale_pairs(entities, "en-US", "en-GB"), {})


if __name__ == "__main__":
    unittest.main()
