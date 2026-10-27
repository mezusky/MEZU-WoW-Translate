"""Protect complete official indexes while preserving valid updates."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from index_retention import retain_on_partial_index


class IndexRetentionTests(unittest.TestCase):
    def test_partial_response_retains_previous_ids_and_updates_names(self):
        previous = {str(i): {"en": f"Spell {i}", "fr": f"Sort {i}"} for i in range(10)}
        fresh = {"9": {"en": "Spell 9", "fr": "Sort neuf"},
                 "11": {"en": "Spell 11", "fr": "Sort onze"}}
        merged = retain_on_partial_index("talent", fresh, previous)
        self.assertEqual(len(merged), 11)
        self.assertEqual(merged["9"]["fr"], "Sort neuf")
        self.assertEqual(merged["0"], previous["0"])

    def test_normal_index_refresh_can_remove_retired_ids(self):
        previous = {str(i): {"en": f"Spell {i}", "fr": f"Sort {i}"} for i in range(10)}
        fresh = {str(i): {"en": f"Spell {i}", "fr": f"Sort {i}"} for i in range(1, 10)}
        self.assertEqual(retain_on_partial_index("mount", fresh, previous), fresh)

    def test_full_refresh_retains_other_locales_on_surviving_ids(self):
        previous = {
            "1": {"en": "Holy Shock", "fr": "Horion sacré", "de": "Heiliger Schock"},
            "2": {"en": "Retired", "fr": "Retiré", "de": "Alt"},
        }
        fresh = {"1": {"en": "Holy Shock", "fr": "Horion sacré (nouveau)"}}
        # Explicitly mark as a complete refresh despite a small synthetic index.
        result = retain_on_partial_index("spell", fresh, previous, min_ratio=0.4)
        self.assertEqual(result, {"1": {
            "en": "Holy Shock", "fr": "Horion sacré (nouveau)", "de": "Heiliger Schock"
        }})

    def test_partial_refresh_preserves_other_locales_and_prior_ids(self):
        previous = {
            str(i): {"en": f"Spell {i}", "fr": f"Sort {i}", "de": f"Zauber {i}"}
            for i in range(10)
        }
        fresh = {"9": {"en": "Spell 9", "fr": "Sort neuf"}}
        result = retain_on_partial_index("spell", fresh, previous)
        self.assertEqual(len(result), 10)
        self.assertEqual(result["9"]["de"], "Zauber 9")
        self.assertEqual(result["9"]["fr"], "Sort neuf")

    def test_first_sync_does_not_invent_previous_entries(self):
        self.assertEqual(retain_on_partial_index("pet", {}, {}), {})

    def test_empty_partial_index_preserves_prior_coverage(self):
        previous = {"1": {"en": "Warrior", "fr": "Guerrier"}}
        self.assertEqual(retain_on_partial_index("class", {}, previous), previous)


if __name__ == "__main__":
    unittest.main()
