"""Canonical entity locale safety tests, runnable by CI unittest discovery."""
import unittest

from scripts.merge_entity_locales import (
    project_locale_pairs,
    merge_verified_locale_refresh,
)


class EntityLocaleMergeContractTests(unittest.TestCase):
    def test_incomplete_locales_keep_canonical_ids(self):
        entities = {"spell": {"1": {"en": "Name"}, "2": {"fr": "Nom"}}}
        self.assertTrue(all(str(i).isdigit() for bucket in entities.values() for i in bucket))
        self.assertEqual(project_locale_pairs(entities, "en", "fr"), {})

    def test_same_locale_skips_translation(self):
        entities = {"spell": {"42": {"en": "Arcane", "fr": "Arcanes"}}}
        self.assertEqual(project_locale_pairs(entities, "en", "en"), {})

    def test_ambiguous_incomplete_ids_do_not_leak_into_exact_pairs(self):
        entities = {"spell": {
            "1": {"en": "Shared", "fr": "Partagé"},
            "2": {"en": "Shared"},
            "3": {"en": "Unique", "fr": "Unique FR"},
        }}
        self.assertEqual(project_locale_pairs(entities, "en", "fr"),
                         {"Unique": "Unique FR"})

    def test_collision_guard_across_entity_types_and_locales(self):
        entities = {
            "spell": {"1": {"de": "Echo", "fr": "Écho"}},
            "item": {"2": {"de": "Echo"}, "3": {"de": "Schild", "fr": "Bouclier"}},
        }
        self.assertEqual(project_locale_pairs(entities, "de", "fr"),
                         {"Schild": "Bouclier"})

    def test_partial_source_refresh_does_not_pair_stale_target(self):
        previous = {"7": {"en": "Old Spell", "fr": "Ancien sort", "de": "Alter Zauber"}}
        fresh = {"7": {"en": "Renamed Spell"}, "8": {"en": "Unpaired Spell"}}
        merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
        self.assertEqual(merged["7"], previous["7"])
        self.assertEqual(merged["8"], {"en": "Unpaired Spell"})
        self.assertEqual(project_locale_pairs({"spell": merged}, "en", "fr"),
                         {"Old Spell": "Ancien sort"})

    def test_partial_target_refresh_does_not_pair_stale_source(self):
        previous = {"7": {"en": "Old Spell", "fr": "Ancien sort"}}
        fresh = {"7": {"fr": "Nouveau sort"}, "8": {"fr": "Nom seulement"}}
        merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
        self.assertEqual(merged["7"], previous["7"])
        self.assertEqual(merged["8"], {"fr": "Nom seulement"})

    def test_blank_target_cannot_pair_new_source_with_stale_translation(self):
        previous = {"7": {"en": "Old Spell", "fr": "Ancien sort"}}
        for blank in ("", "   ", None, 0):
            with self.subTest(blank=blank):
                fresh = {"7": {"en": "Renamed Spell", "fr": blank}}
                merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
                self.assertEqual(merged, previous)
                self.assertEqual(
                    project_locale_pairs({"spell": merged}, "en", "fr"),
                    {"Old Spell": "Ancien sort"},
                )

    def test_blank_source_cannot_pair_new_target_with_stale_source(self):
        previous = {"7": {"en": "Old Spell", "fr": "Ancien sort"}}
        for blank in ("", "  ", None):
            with self.subTest(blank=blank):
                fresh = {"7": {"en": blank, "fr": "Nouveau sort"}}
                merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
                self.assertEqual(merged, previous)

    def test_source_rename_invalidates_unverified_third_locales(self):
        previous = {"7": {"en": "Old Spell", "fr": "Ancien sort", "de": "Alter Zauber"}}
        fresh = {"7": {"en": "New Spell", "fr": "Nouveau sort"}}
        merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
        self.assertEqual(merged["7"], {"en": "New Spell", "fr": "Nouveau sort"})
        self.assertEqual(project_locale_pairs({"spell": merged}, "en", "fr"),
                         {"New Spell": "Nouveau sort"})
        self.assertEqual(project_locale_pairs({"spell": merged}, "en", "de"), {})
        for blank in ("", "  ", None):
            with self.subTest(blank=blank):
                incomplete = merge_verified_locale_refresh(
                    previous,
                    {"7": {"en": "New Spell", "fr": "Nouveau sort", "de": blank}},
                    "en", "fr",
                )
                self.assertNotIn("de", incomplete["7"])
        # A later independently verified German name restores ID-based coverage.
        updated = merge_verified_locale_refresh(
            merged, {"7": {"en": "New Spell", "de": "Neuer Zauber"}}, "en", "de"
        )
        self.assertEqual(project_locale_pairs({"spell": updated}, "en", "de"),
                         {"New Spell": "Neuer Zauber"})

    def test_unchanged_source_preserves_other_verified_locales(self):
        previous = {"7": {"en": "Same Spell", "fr": "Ancien sort", "de": "Alter Zauber"}}
        fresh = {"7": {"en": "Same Spell", "fr": "Nouveau sort"}}
        merged = merge_verified_locale_refresh(previous, fresh, "en", "fr")
        self.assertEqual(merged["7"]["de"], "Alter Zauber")
        self.assertEqual(project_locale_pairs({"spell": merged}, "en", "de"),
                         {"Same Spell": "Alter Zauber"})

    def test_non_english_source_rename_invalidates_stale_other_language(self):
        previous = {"9": {"de": "Alter Name", "fr": "Ancien nom", "en": "Old Name"}}
        merged = merge_verified_locale_refresh(
            previous, {"9": {"de": "Neuer Name", "fr": "Nouveau nom"}}, "de", "fr"
        )
        self.assertEqual(merged["9"], {"de": "Neuer Name", "fr": "Nouveau nom"})
        self.assertEqual(project_locale_pairs({"spell": merged}, "de", "en"), {})
        self.assertEqual(project_locale_pairs({"spell": merged}, "de", "fr"),
                         {"Neuer Name": "Nouveau nom"})

    def test_generic_locale_keys_and_identical_pair_rejected(self):
        previous = {"1": {"de": "Alt", "fr": "Ancien"}}
        self.assertEqual(merge_verified_locale_refresh(
            previous, {"1": {"de": "Neu"}}, "de", "fr"
        ), previous)
        with self.assertRaises(ValueError):
            merge_verified_locale_refresh(previous, {}, "fr", "fr")


if __name__ == "__main__":
    unittest.main()
