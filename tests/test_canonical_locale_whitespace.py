"""Canonical ID names ignore boundary padding, not meaningful internal spaces."""
import unittest

from scripts.merge_entity_locales import (
    merge_verified_locale_refresh, project_locale_pairs,
)


class CanonicalLocaleWhitespaceTests(unittest.TestCase):
    def test_equivalent_aliases_with_padding_are_not_conflicts(self):
        entities = {"spell": {"spell:30451": {
            "en_US": " Arcane Blast ", "en-US": "Arcane Blast",
            "fr_FR": " Déflagration des Arcanes ",
        }}}
        self.assertEqual(
            project_locale_pairs(entities, "en-US", "fr-FR"),
            {"Arcane Blast": "Déflagration des Arcanes"},
        )

    def test_padding_does_not_invalidate_unrelated_verified_locale(self):
        old = {"spell:17": {
            "en-US": "Power Word: Shield", "fr-FR": "Ancien nom",
            "de-DE": "Machtwort: Schild",
        }}
        fresh = {"spell:17": {
            "en_US": " Power Word: Shield ", "fr_FR": " Mot de pouvoir : Bouclier ",
        }}
        merged = merge_verified_locale_refresh(old, fresh, "en-US", "fr-FR")
        self.assertEqual(merged["spell:17"], {
            "en_US": "Power Word: Shield",
            "fr_FR": "Mot de pouvoir : Bouclier",
            "de-DE": "Machtwort: Schild",
        })
        self.assertEqual(old["spell:17"]["fr-FR"], "Ancien nom")

    def test_trimmed_collision_with_different_targets_fails_closed(self):
        entities = {"spell": {
            "spell:1": {"en": "Shadow Bolt ", "fr": "Trait de l’ombre"},
            "spell:2": {"en": " Shadow Bolt", "fr": "Autre nom"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en", "fr"), {})

    def test_internal_whitespace_is_not_silently_rewritten(self):
        entities = {"spell": {"spell:1": {
            "en": "Power  Word", "fr": "Mot de pouvoir",
        }}}
        self.assertEqual(
            project_locale_pairs(entities, "en", "fr"),
            {"Power  Word": "Mot de pouvoir"},
        )


if __name__ == "__main__":
    unittest.main()
