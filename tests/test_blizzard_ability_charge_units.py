"""Cross-class charge-count semantics from live-indexed Wowhead guides.

Frost Mage (Ray of Frost) and Vengeance Demon Hunter (Fracture and
Demon Spikes) both discuss two charges. These synthetic translations are
not actual Chrome Translator API output.
"""
import unittest

from scripts.build_blizzard_memory import (
    _alignment_number_tokens, numeric_facts, numeric_semantics_match,
    structural_score,
)


class AbilityChargeUnitTests(unittest.TestCase):
    def test_frost_mage_two_charges_preserved(self):
        source = "Ray of Frost will have 2 charges."
        target = "Rayon de givre aura 2 charges."
        self.assertEqual(numeric_facts(source, "en-US"),
                         [("2", "wow_ability_charge")])
        self.assertEqual(numeric_facts(target, "fr-FR"),
                         [("2", "wow_ability_charge")])
        self.assertTrue(numeric_semantics_match(source, target))

    def test_vengeance_dh_charges_not_stacks(self):
        source = "Use Fracture at 2 charges."
        target = "Utilisez Fracture à 2 cumuls."
        self.assertFalse(numeric_semantics_match(source, target))

    def test_charges_not_ability_uses_or_targets(self):
        source = "Demon Spikes can hold 2 charges."
        for target in ("Pointes démoniaques peut conserver 2 utilisations.",
                       "Pointes démoniaques peut conserver 2 cibles."):
            with self.subTest(target=target):
                self.assertFalse(numeric_semantics_match(source, target))

    def test_charge_count_must_still_match(self):
        self.assertFalse(numeric_semantics_match(
            "Keep 2 charges.", "Conservez 3 charges."))

    def test_charge_count_and_duration_stay_distinct(self):
        self.assertTrue(numeric_semantics_match(
            "2 charges with a 12-second duration.",
            "2 charges avec une durée de 12 secondes."))
        self.assertFalse(numeric_semantics_match(
            "2 charges with a 12-second duration.",
            "2 charges avec une durée de 12 minutes."))

    def test_alignment_uses_shared_canonical_charge_unit(self):
        en = ("li", "Demon Spikes can hold 2 charges.")
        fr = ("li", "Pointes démoniaques peut conserver 2 charges.")
        wrong = ("li", "Pointes démoniaques peut conserver 2 cumuls.")
        self.assertEqual(_alignment_number_tokens(en[1], "en-US"),
                         _alignment_number_tokens(fr[1], "fr-FR"))
        self.assertGreater(structural_score(en, fr),
                           structural_score(en, wrong))

    def test_no_singular_charge_alias_to_avoid_spell_name(self):
        self.assertEqual(numeric_facts("Cast Charge.", "en-US"), [])
        self.assertEqual(numeric_facts("1 Charge cast.", "en-US"),
                         [("1", "")])
        self.assertEqual(numeric_facts("2 charges", "de-DE"),
                         [("2", "")])


if __name__ == "__main__":
    unittest.main()
