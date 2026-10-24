"""Counted WoW resources must survive official prose memory by canonical ID."""
import unittest

from scripts.build_blizzard_memory import (
    good_pair, numeric_semantics_match, resource_count_facts,
)


class BlizzardResourceCountTests(unittest.TestCase):
    def test_soul_shard_id_matches_across_locales(self):
        self.assertEqual(resource_count_facts("Spend 3 Soul Shards.", "en-US"),
                         [("3", "7")])
        self.assertEqual(resource_count_facts("Dépense 3 éclats d’âme.", "fr-FR"),
                         [("3", "7")])
        self.assertTrue(numeric_semantics_match(
            "Spend 3 Soul Shards.", "Dépense 3 éclats d'âme."))
        self.assertTrue(good_pair(
            "Spend 3 Soul Shards.", "Dépense 3 éclats d’âme.", 6.0))

    def test_wrong_resource_is_not_learned(self):
        self.assertFalse(numeric_semantics_match(
            "Refund 1 Soul Shard.", "Rend 1 charge."))
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Soul Shards.", "Dépense 3 cibles."))
        self.assertFalse(numeric_semantics_match(
            "Spend 3 Soul Shards.", "Dépense 3 points de puissance sacrée."))

    def test_order_and_count_still_matter(self):
        self.assertFalse(numeric_semantics_match(
            "Spend 2 Soul Shards and gain 3 Soul Shards.",
            "Dépense 3 éclats d’âme et gagne 2 éclats d’âme."))
        self.assertFalse(numeric_semantics_match(
            "Spend 2 Soul Shards.", "Dépense 3 éclats d’âme."))

    def test_locale_isolation_fails_closed(self):
        self.assertEqual(resource_count_facts("Spend 2 Soul Shards.", "de-DE"), [])
        self.assertFalse(numeric_semantics_match(
            "Spend 2 Soul Shards.", "Dépense 2 éclats d’âme.",
            "en-US", "fr-CA"))
        self.assertTrue(numeric_semantics_match(
            "Deal 5% more damage.", "Inflige 5 % de dégâts supplémentaires.",
            "en-US", "fr-CA"))


if __name__ == "__main__":
    unittest.main()
