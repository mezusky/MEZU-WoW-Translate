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

    def test_missing_names_are_not_guessed(self):
        en = {"results": [{"data": {"id": 2, "name": {"en_US": "Garrote"}}}]}
        fr = {"results": [{"data": {"id": 2, "name": {"de_DE": "Erdrosseln"}}}]}
        self.assertEqual(collect_search_pairs(en, fr, "en_US", "fr_FR"), {})

    def test_malformed_hits_and_conflicting_ids(self):
        doc = {"results": [None, {"data": {"id": True, "name": "Bad"}},
                           {"data": {"id": 7, "name": "First"}},
                           {"data": {"id": 7, "name": "Second"}},
                           {"data": {"id": 8, "name": "Valid"}}]}
        self.assertEqual(search_names(doc, "en_US"), {"8": "Valid"})


if __name__ == "__main__":
    unittest.main()
