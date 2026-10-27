"""Canonical Blizzard search IDs and locale-aware name parsing."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from blizzard_search_pairs import collect_search_pairs, search_names


class BlizzardSearchPairsTests(unittest.TestCase):
    def test_localized_name_objects_and_nested_ids(self):
        en = {"results": [{"data": {"id": 123, "name": {"en_US": "Shield Slam"},
                                    "category": {"id": 9, "name": "Not a spell"}}}]}
        fr = {"results": [{"data": {"id": 123, "name": {"fr_FR": "Heurt de bouclier"},
                                    "category": {"id": 10}}}]}
        self.assertEqual(collect_search_pairs(en, fr, "en_US", "fr_FR"),
                         {"123": {"en": "Shield Slam", "fr": "Heurt de bouclier"}})

    def test_plain_names_and_custom_locale_keys(self):
        en = {"results": [{"data": {"id": 5, "name": "Renewing Mist"}}]}
        de = {"results": [{"data": {"id": 5, "name": "Erneuernder Nebel"}}]}
        self.assertEqual(collect_search_pairs(en, de, "en_US", "de_DE", "en-US", "de-DE"),
                         {"5": {"en-US": "Renewing Mist", "de-DE": "Erneuernder Nebel"}})

    def test_descending_search_pairs_by_id_not_result_position(self):
        # English/French search pages can differ in hit order or omit an ID.
        en = {"results": [
            {"data": {"id": 500, "name": {"en_US": "Newest Spell"}}},
            {"data": {"id": 400, "name": {"en_US": "Older Spell"}}},
        ]}
        fr = {"results": [
            {"data": {"id": 400, "name": {"fr_FR": "Sort ancien"}}},
            {"data": {"id": 500, "name": {"fr_FR": "Sort récent"}}},
        ]}
        self.assertEqual(
            collect_search_pairs(en, fr, "en_US", "fr_FR"),
            {"500": {"en": "Newest Spell", "fr": "Sort récent"},
             "400": {"en": "Older Spell", "fr": "Sort ancien"}},
        )

    def test_missing_names_are_not_guessed(self):
        en = {"results": [{"data": {"id": 2, "name": {"en_US": "Garrote"}}}]}
        fr = {"results": [{"data": {"id": 2, "name": {"de_DE": "Erdrosseln"}}}]}
        # Keep the EN-only canonical ID but never fabricate a French name.
        self.assertEqual(collect_search_pairs(en, fr, "en_US", "fr_FR"),
                         {"2": {"en": "Garrote"}})

    def test_unpaired_source_id_blocks_unsafe_same_name_projection(self):
        from merge_entity_locales import project_locale_pairs
        en = {"results": [
            {"data": {"id": 10, "name": "Shared Name"}},
            {"data": {"id": 11, "name": "Shared Name"}},
            {"data": {"id": 12, "name": "Unique Name"}},
        ]}
        fr = {"results": [
            {"data": {"id": 10, "name": "Ancien nom"}},
            {"data": {"id": 12, "name": "Nom unique"}},
        ]}
        rows = collect_search_pairs(en, fr, "en_US", "fr_FR")
        self.assertEqual(rows["11"], {"en": "Shared Name"})
        self.assertEqual(project_locale_pairs({"spell": rows}, "en", "fr"),
                         {"Unique Name": "Nom unique"})

    def test_unpaired_target_id_is_retained_for_future_source_locale(self):
        en = {"results": [{"data": {"id": 5, "name": "Shared"}}]}
        fr = {"results": [{"data": {"id": 6, "name": "Seulement français"}}]}
        self.assertEqual(collect_search_pairs(en, fr, "en_US", "fr_FR"),
                         {"5": {"en": "Shared"},
                          "6": {"fr": "Seulement français"}})

    def test_malformed_hits_and_conflicting_ids(self):
        doc = {"results": [None, {"data": {"id": True, "name": "Bad"}},
                           {"data": {"id": 7, "name": "First"}},
                           {"data": {"id": 7, "name": "Second"}},
                           {"data": {"id": 8, "name": "Valid"}}]}
        self.assertEqual(search_names(doc, "en_US"), {"8": "Valid"})


if __name__ == "__main__":
    unittest.main()
