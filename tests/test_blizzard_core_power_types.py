"""Canonical PowerType counts on independent retail Wowhead DPS/tank/healer guides.

Indexed English sources and synthetic French expectations only; Chrome's
browser-local Translator API and rendered DOM are not exercised here.
"""
import unittest

from scripts.build_blizzard_memory import (
    good_pair, numeric_semantics_match, resource_count_facts
)


class CorePowerTypeCoverageTests(unittest.TestCase):
    def test_feral_druid_energy_and_combo_points_remain_distinct(self):
        en = "Use Ferocious Bite at 5 Combo Points and 50 Energy."
        fr = "Utilisez Morsure féroce à 5 points de combo et 50 points d'énergie."
        self.assertEqual(resource_count_facts(en, "en-US"),
                         [("5", "4"), ("50", "3")])
        self.assertEqual(resource_count_facts(fr, "fr-FR"),
                         [("5", "4"), ("50", "3")])
        self.assertTrue(numeric_semantics_match(en, fr))

    def test_brewmaster_energy_is_not_mana(self):
        en = "Tiger Palm costs 25 Energy."
        self.assertTrue(numeric_semantics_match(
            en, "Paume du tigre coûte 25 points d'énergie."
        ))
        self.assertFalse(numeric_semantics_match(
            en, "Paume du tigre coûte 25 points de mana."
        ))
        self.assertFalse(good_pair(
            en, "Paume du tigre coûte 25 points de mana.", 8.0
        ))

    def test_blood_death_knight_runes_are_not_runic_power(self):
        en = "Marrowrend costs 2 Runes."
        self.assertTrue(numeric_semantics_match(
            en, "Déchire-moelle coûte 2 runes."
        ))
        self.assertFalse(numeric_semantics_match(
            en, "Déchire-moelle coûte 2 points de puissance runique."
        ))

    def test_shadow_priest_insanity_has_its_own_canonical_id(self):
        en = "Hallucinations generate 4 Insanity."
        self.assertTrue(numeric_semantics_match(
            en, "Les Hallucinations génèrent 4 points d'insanité."
        ))
        self.assertFalse(numeric_semantics_match(
            en, "Les Hallucinations génèrent 4 points d'énergie."
        ))

    def test_mana_resource_is_separate_from_energy(self):
        self.assertTrue(numeric_semantics_match(
            "Restore 50 Mana.", "Rend 50 points de mana."
        ))
        self.assertFalse(numeric_semantics_match(
            "Restore 50 Mana.", "Rend 50 points d'énergie."
        ))

    def test_spell_names_are_not_mistaken_for_counted_resources(self):
        self.assertEqual(resource_count_facts(
            "2 Energy Surge procs and 3 Rune of Hysteria procs.", "en-US"
        ), [])
        self.assertEqual(resource_count_facts(
            "2 Runes and 50 Energy.", "en-US"
        ), [("2", "5"), ("50", "3")])

    def test_unknown_locale_does_not_borrow_english_or_french_names(self):
        self.assertEqual(resource_count_facts(
            "50 Energy and 2 Runes.", "de-DE"
        ), [])
        self.assertEqual(resource_count_facts(
            "50 points d'énergie.", "en-US"
        ), [])


if __name__ == "__main__":
    unittest.main()
