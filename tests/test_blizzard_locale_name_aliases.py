"""Blizzard locale-keyed names must not silently choose conflicting aliases.

The same helper is used for search hits (spells/items) and static indexes
(classes/talents/etc.). These are data pipeline tests, not browser translation
claims; they are independent of source/target language direction.
"""
import unittest

from scripts.blizzard_locale_name import verified_locale_name, has_conflicting_locale_aliases
from scripts.blizzard_search_pairs import collect_search_pairs, search_names
from scripts.blizzard_index_pairs import collect_index_pairs, index_names
from scripts.merge_entity_locales import project_locale_pairs


class VerifiedBlizzardLocaleNames(unittest.TestCase):
    def test_same_locale_aliases_agree_after_trimming(self):
        for locale in ("en_US", "en-US", "EN_us"):
            with self.subTest(locale=locale):
                self.assertEqual(verified_locale_name({
                    "en_US": " Shield Slam ", "en-US": "Shield Slam",
                    "fr_FR": "Heurt de bouclier",
                }, locale), "Shield Slam")

    def test_conflicting_aliases_are_rejected_independent_of_order(self):
        aliases = [("en_US", "Shield Slam"), ("en-US", "Shield Bash")]
        for entries in (aliases, list(reversed(aliases))):
            self.assertIsNone(verified_locale_name(dict(entries), "en-US"))
        self.assertIsNone(verified_locale_name({
            "fr_FR": "Heurt de bouclier", "fr-FR": "Coup de bouclier",
        }, "fr_FR"))

    def test_no_cross_region_or_generic_guess(self):
        self.assertIsNone(verified_locale_name({"fr_CA": "Nom canadien"}, "fr_FR"))
        self.assertIsNone(verified_locale_name({"en": "Generic"}, "en_US"))
        self.assertEqual(verified_locale_name(" Plain name ", "de_DE"), "Plain name")

    def test_search_conflict_never_becomes_canonical_translation(self):
        en = {"results": [{"data": {"id": 1, "name": {
            "en_US": "Spell A", "en-US": "Spell B"}}},
            {"data": {"id": 2, "name": {"en_US": "Safe"}}}]}
        fr = {"results": [{"data": {"id": 1, "name": {"fr_FR": "Sort A"}}},
            {"data": {"id": 2, "name": {"fr_FR": "Sûr"}}}]}
        rows = collect_search_pairs(en, fr, "en_US", "fr_FR")
        self.assertEqual(rows["1"], {"fr": "Sort A"})
        self.assertEqual(project_locale_pairs({"spell": rows}, "en", "fr"),
                         {"Safe": "Sûr"})

    def test_index_conflict_never_becomes_canonical_translation(self):
        en = {"talents": [{"id": 1, "name": {
            "en_US": "Talent A", "en-US": "Talent B"}},
            {"id": 2, "name": {"en_US": "Safe"}}]}
        fr = {"talents": [{"id": 1, "name": {"fr_FR": "Talent FR"}},
            {"id": 2, "name": {"fr_FR": "Sûr"}}]}
        rows = collect_index_pairs(en, fr, "en_US", "fr_FR")
        self.assertEqual(rows["1"], {"fr": "Talent FR"})
        self.assertEqual(project_locale_pairs({"talent": rows}, "en", "fr"),
                         {"Safe": "Sûr"})

    def test_conflicting_alias_cannot_be_laundered_by_duplicate_search_hit(self):
        conflict = {"data": {"id": 17, "name": {
            "en_US": "Shield Slam", "en-US": "Shield Bash"}}}
        valid = {"data": {"id": 17, "name": {"en_US": "Shield Slam"}}}
        for hits in ([conflict, valid], [valid, conflict]):
            with self.subTest(order=hits[0] is conflict):
                self.assertNotIn("17", search_names({"results": hits}, "en_US"))
        self.assertTrue(has_conflicting_locale_aliases(conflict["data"]["name"], "en_US"))
        self.assertFalse(has_conflicting_locale_aliases(valid["data"]["name"], "en_US"))

    def test_conflicting_alias_cannot_be_laundered_by_nested_index(self):
        conflict = {"id": 18, "name": {
            "fr_FR": "Heurt de bouclier", "fr-FR": "Coup de bouclier"}}
        valid = {"id": 18, "name": {"fr_FR": "Heurt de bouclier"}}
        for records in ([conflict, valid], [valid, conflict]):
            with self.subTest(order=records[0] is conflict):
                self.assertNotIn("18", index_names({"talents": records}, "fr_FR"))

    def test_missing_alias_is_not_a_conflict(self):
        rows = {"results": [
            {"data": {"id": 19, "name": {"de_DE": "Other locale"}}},
            {"data": {"id": 19, "name": {"en_US": "Charge"}}},
        ]}
        self.assertEqual(search_names(rows, "en_US"), {"19": "Charge"})

    def test_other_language_direction(self):
        de = {"results": [{"data": {"id": 7, "name": {
            "de_DE": "Heiliger Schock", "de-DE": "Heiliger Schock"}}}]}
        fr = {"results": [{"data": {"id": 7, "name": {
            "fr_FR": "Horion sacré", "fr-FR": "Horion sacré"}}}]}
        rows = collect_search_pairs(de, fr, "de_DE", "fr_FR", "de", "fr")
        self.assertEqual(project_locale_pairs({"spell": rows}, "de", "fr"),
                         {"Heiliger Schock": "Horion sacré"})


if __name__ == "__main__":
    unittest.main()
