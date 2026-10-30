"""Canonical WoW names must not depend on locale alias insertion order."""
import unittest

from scripts.merge_entity_locales import project_locale_pairs


class CanonicalAliasCollisionTests(unittest.TestCase):
    def test_conflicting_source_aliases_fail_closed(self):
        entities = {"spell": {
            "101": {"en-US": "Lightning Bolt", "en_US": "Chain Lightning",
                    "fr": "Éclair"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en-US", "fr-FR"), {})
        reversed_aliases = {"spell": {
            "101": {"en_US": "Chain Lightning", "en-US": "Lightning Bolt",
                    "fr": "Éclair"},
        }}
        self.assertEqual(project_locale_pairs(reversed_aliases, "en-US", "fr-FR"), {})

    def test_conflicting_target_aliases_fail_closed(self):
        entities = {"spell": {
            "102": {"en": "Shield Slam", "fr-FR": "Heurt de bouclier",
                    "fr_FR": "Coup de bouclier"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en", "fr-FR"), {})

    def test_identical_aliases_are_safe(self):
        entities = {"spell": {
            "103": {"en-US": "Chaos Bolt", "en_US": "Chaos Bolt",
                    "fr-FR": "Trait du chaos", "fr_FR": "Trait du chaos"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en-US", "fr-FR"),
                         {"Chaos Bolt": "Trait du chaos"})

    def test_other_regions_can_use_unambiguous_generic_label(self):
        entities = {"spell": {
            "104": {"en": "Soul Shard", "en-US": "Soul Shard",
                    "en_US": "Different name", "fr": "Éclat d’âme"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en-GB", "fr-FR"),
                         {"Soul Shard": "Éclat d’âme"})
        self.assertEqual(project_locale_pairs(entities, "en-US", "fr-FR"), {})


if __name__ == "__main__":
    unittest.main()
