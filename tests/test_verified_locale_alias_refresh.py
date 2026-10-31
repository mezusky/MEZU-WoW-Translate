"""Cross-class canonical WoW IDs must survive verified locale alias refreshes."""
import unittest

from scripts.merge_entity_locales import (
    merge_verified_locale_refresh, project_locale_pairs,
)


class VerifiedLocaleAliasRefreshTests(unittest.TestCase):
    def test_source_rename_replaces_aliases_and_preserves_third_locale(self):
        # Vengeance DH spell: both aliases denote the same official locale.
        old = {"spell:204596": {
            "en-US": "Old Sigil Name", "fr-FR": "Ancien cachet",
            "de-DE": "Alter Name",
        }}
        fresh = {"spell:204596": {
            "en_US": "Sigil of Flame", "fr_FR": "Cachet de feu",
        }}
        merged = merge_verified_locale_refresh(old, fresh, "en-US", "fr-FR")
        self.assertEqual(merged["spell:204596"],
                         {"en_US": "Sigil of Flame", "fr_FR": "Cachet de feu",
                          "de-DE": "Alter Name"})
        self.assertEqual(
            project_locale_pairs({"spell": merged}, "en-US", "fr-FR"),
            {"Sigil of Flame": "Cachet de feu"},
        )
        self.assertEqual(
            project_locale_pairs({"spell": merged}, "en-US", "de-DE"),
            {"Sigil of Flame": "Alter Name"})
        # Refresh must not mutate the prior canonical snapshot.
        self.assertIn("de-DE", old["spell:204596"])

    def test_unchanged_source_keeps_other_locales_but_replaces_old_aliases(self):
        # Discipline Priest: target spelling corrected without source rename.
        old = {"spell:17": {
            "en_US": "Power Word: Shield", "fr_FR": "Ancien nom",
            "de-DE": "Machtwort: Schild",
        }}
        fresh = {"spell:17": {
            "en-US": "Power Word: Shield", "fr-FR": "Mot de pouvoir : Bouclier",
        }}
        merged = merge_verified_locale_refresh(old, fresh, "en_US", "fr_FR")
        self.assertEqual(merged["spell:17"], {
            "en-US": "Power Word: Shield",
            "fr-FR": "Mot de pouvoir : Bouclier",
            "de-DE": "Machtwort: Schild",
        })
        self.assertEqual(
            project_locale_pairs({"spell": merged}, "en-US", "fr-FR"),
            {"Power Word: Shield": "Mot de pouvoir : Bouclier"},
        )

    def test_partial_alias_refresh_cannot_pair_new_source_with_old_target(self):
        # Mage spell: a missing fresh target must not create a false pair.
        old = {"spell:30451": {
            "en-US": "Arcane Blast", "fr-FR": "Déflagration des Arcanes",
        }}
        fresh = {
            "spell:30451": {"en_US": "Renamed Arcane Blast"},
            "spell:99999": {"en_US": "New Unpaired Spell"},
        }
        merged = merge_verified_locale_refresh(old, fresh, "en-US", "fr-FR")
        self.assertEqual(merged["spell:30451"], old["spell:30451"])
        self.assertEqual(merged["spell:99999"], fresh["spell:99999"])
        self.assertNotIn("New Unpaired Spell",
                         project_locale_pairs({"spell": merged}, "en-US", "fr-FR"))

    def test_conflicting_fresh_aliases_cannot_overwrite_verified_pair(self):
        old = {"spell:1": {"en": "Old Name", "fr": "Ancien nom"}}
        fresh = {"spell:1": {
            "en_US": "New Name", "en-US": "Different Name",
            "fr_FR": "Nouveau nom",
        }}
        merged = merge_verified_locale_refresh(old, fresh, "en_US", "fr_FR")
        self.assertEqual(merged, old)

    def test_conflicting_old_aliases_are_repaired_without_dropping_third_locale(self):
        # A previously ambiguous Hunter source name must not survive a fresh
        # verified pair under either spelling; other locales remain ID-backed.
        old = {"spell:34026": {
            "en-US": "Kill Command", "en_US": "Outdated Kill Command",
            "fr-FR": "Ancien ordre", "de-DE": "Altes Kommando",
        }}
        fresh = {"spell:34026": {
            "en_US": "Kill Command", "fr_FR": "Ordre de tuer",
        }}
        merged = merge_verified_locale_refresh(old, fresh, "en-US", "fr-FR")
        self.assertEqual(merged["spell:34026"],
                         {"en_US": "Kill Command", "fr_FR": "Ordre de tuer",
                          "de-DE": "Altes Kommando"})
        self.assertEqual(
            project_locale_pairs({"spell": merged}, "en-US", "fr-FR"),
            {"Kill Command": "Ordre de tuer"},
        )

    def test_source_and_target_aliases_cannot_be_the_same_locale(self):
        with self.assertRaises(ValueError):
            merge_verified_locale_refresh({}, {}, "en_US", "en-US")


if __name__ == "__main__":
    unittest.main()
