"""Blizzard index canonical ID coverage and locale collision regression tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from blizzard_index_pairs import collect_index_pairs, index_names
from index_retention import retain_on_partial_index
from merge_entity_locales import project_locale_pairs


class BlizzardIndexPairsTests(unittest.TestCase):
    def test_unpaired_source_id_blocks_ambiguous_official_name(self):
        en = {"classes": [
            {"id": 1, "name": "Shared"},
            {"id": 2, "name": "Shared"},
            {"id": 3, "name": "Unique"},
        ]}
        fr = {"classes": [
            {"id": 1, "name": "Partagé"},
            {"id": 3, "name": "Unique FR"},
        ]}
        rows = collect_index_pairs(en, fr, "en_US", "fr_FR")
        self.assertEqual(rows["2"], {"en": "Shared"})
        self.assertEqual(project_locale_pairs({"class": rows}, "en", "fr"),
                         {"Unique": "Unique FR"})

    def test_unpaired_target_id_survives_for_future_source_locale(self):
        en = {"races": [{"id": 1, "name": "Race"}]}
        fr = {"races": [{"id": 2, "name": "Race FR"}]}
        self.assertEqual(collect_index_pairs(en, fr, "en_US", "fr_FR"),
                         {"1": {"en": "Race"}, "2": {"fr": "Race FR"}})

    def test_order_independent_and_locale_objects(self):
        en = {"races": [{"id": 10, "name": {"en_US": "Elf"}},
                        {"id": 20, "name": "Orc"}]}
        de = {"races": [{"id": 20, "name": "Ork"},
                        {"id": 10, "name": {"de_DE": "Elf DE"}}]}
        self.assertEqual(collect_index_pairs(en, de, "en_US", "de_DE",
                                             "en", "de"),
                         {"10": {"en": "Elf", "de": "Elf DE"},
                          "20": {"en": "Orc", "de": "Ork"}})

    def test_ignores_metadata_and_conflicting_ids(self):
        doc = {"races": [{"id": 7, "name": "First"},
                         {"id": 7, "name": "Second"},
                         {"id": 8, "name": "Valid"},
                         {"id": True, "name": "Bad"}],
               "_links": {"id": 99, "name": "Metadata"}}
        self.assertEqual(index_names(doc, "en_US"), {"8": "Valid"})

    def test_index_partial_refresh_never_pairs_stale_names(self):
        old = {"1": {"en": "Old", "fr": "Ancien"},
               "2": {"en": "Shared", "fr": "Partagé"}}
        fresh = {"1": {"en": "New"},
                 "3": {"en": "Shared"}}
        merged = retain_on_partial_index("class", fresh, old, min_ratio=1.1)
        self.assertEqual(merged["1"], old["1"])
        self.assertEqual(merged["2"], old["2"])
        self.assertEqual(merged["3"], {"en": "Shared"})
        self.assertEqual(project_locale_pairs({"class": merged}, "en", "fr"),
                         {"Old": "Ancien"})

    def test_full_index_refresh_does_not_stitch_stale_locale(self):
        old = {"1": {"en": "Old", "fr": "Ancien", "de": "Alt"}}
        fresh = {"1": {"en": "New"}, "2": {"en": "Unpaired"}}
        merged = retain_on_partial_index("class", fresh, old)
        self.assertEqual(merged["1"], old["1"])
        self.assertEqual(merged["2"], {"en": "Unpaired"})

    def test_same_locale_pair_rejected(self):
        with self.assertRaises(ValueError):
            collect_index_pairs({}, {}, "fr_FR", "fr_FR", "fr", "fr")


if __name__ == "__main__":
    unittest.main()
