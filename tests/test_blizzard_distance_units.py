"""Cross-class WoW range-distance facts must survive official phrase alignment.

These are synthetic expected translations based on indexed Wowhead guide source,
not output captured from Chrome's Translator API.
"""
import unittest

from scripts.build_blizzard_memory import numeric_facts, numeric_semantics_match, good_pair


class BlizzardDistanceUnitTests(unittest.TestCase):
    def test_shaman_range_and_cooldown_are_separate_facts(self):
        source = "Slows enemies within 10 yards for 8 seconds."
        target = "Ralentit les ennemis dans un rayon de 10 mètres pendant 8 secondes."
        self.assertEqual(numeric_facts(source, "en-US"), [("10", "wow_distance"), ("8", "s")])
        self.assertEqual(numeric_facts(target, "fr-FR"), [("10", "wow_distance"), ("8", "s")])
        self.assertTrue(numeric_semantics_match(source, target))

    def test_holy_priest_healing_range_is_not_a_duration(self):
        source = "Heals 4 allies within 40 yards of the target."
        target = "Soigne 4 alliés à 40 mètres de la cible."
        self.assertTrue(numeric_semantics_match(source, target))
        self.assertFalse(numeric_semantics_match(source,
                         "Soigne 4 alliés pendant 40 secondes autour de la cible."))

    def test_distance_must_not_become_target_count_or_percent(self):
        self.assertFalse(numeric_semantics_match("Affects allies within 8 yards.",
                                                 "Affecte 8 cibles alliées."))
        self.assertFalse(numeric_semantics_match("Affects allies within 8 yards.",
                                                 "Affecte les alliés pendant 8 secondes."))
        self.assertFalse(good_pair("Affects allies within 8 yards.",
                                   "Affecte les alliés pendant 8 secondes.", 6.0))

    def test_abbreviated_yards_and_french_singular(self):
        self.assertEqual(numeric_facts("40 yd range.", "en-US"), [("40", "wow_distance")])
        self.assertEqual(numeric_facts("1 mètre de portée.", "fr-FR"),
                         [("1", "wow_distance")])

    def test_locale_isolation_and_existing_units(self):
        self.assertEqual(numeric_facts("40 yards", "de-DE"), [("40", "")])
        self.assertEqual(numeric_facts("40 mètres", "en-US"), [("40", "")])
        self.assertEqual(numeric_facts("8 seconds, 10 targets.", "en-US"),
                         [("8", "s"), ("10", "target")])


if __name__ == "__main__":
    unittest.main()
