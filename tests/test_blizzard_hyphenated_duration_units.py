"""Cross-spec numeric unit reconstruction from indexed retail Wowhead guides.

Synthetic French expectations only: this does not run Chrome Translator API.
Observed on Assassination Rogue, Arcane Mage and Brewmaster Monk pages.
"""
import unittest

from scripts.build_blizzard_memory import numeric_facts, numeric_semantics_match


class HyphenatedDurationTests(unittest.TestCase):
    def test_assassination_rogue_hyphenated_modifier(self):
        source = "Refresh Garrote at the end of the 6-second-long window."
        french = "Rafraîchissez Garrot à la fin de la fenêtre de 6 secondes."
        self.assertIn(("6", "s"), numeric_facts(source, "en-US"))
        self.assertTrue(numeric_semantics_match(source, french))
        self.assertFalse(numeric_semantics_match(
            source, "Rafraîchissez Garrot à la fin de la fenêtre de 6 minutes."
        ))

    def test_arcane_mage_hyphenated_plural(self):
        source = "45-seconds later, repeat the last step."
        self.assertEqual(numeric_facts(source, "en-US"), [("45", "s")])
        self.assertTrue(numeric_semantics_match(
            source, "45 secondes plus tard, répétez la dernière étape."
        ))

    def test_brewmaster_monk_hyphenated_cooldown(self):
        source = "Fortifying Brew has a 6-minute cooldown."
        self.assertTrue(numeric_semantics_match(
            source, "Infusion fortifiante a un temps de recharge de 6 minutes."
        ))
        self.assertFalse(numeric_semantics_match(
            source, "Infusion fortifiante a un temps de recharge de 6 secondes."
        ))

    def test_numeric_range_not_mistaken_for_unit_separator(self):
        self.assertTrue(numeric_semantics_match(
            "This is a 2-3 minute ability.",
            "Cette technique a un temps de recharge de 2 à 3 minutes."
        ))
        self.assertFalse(numeric_semantics_match(
            "This is a 2-3 minute ability.",
            "Cette technique a un temps de recharge de 2 à 4 minutes."
        ))

    def test_existing_threshold_and_signed_number_unchanged(self):
        self.assertEqual(numeric_facts("5+ stacks", "en-US"), [("5+", "stack")])
        self.assertEqual(numeric_facts("-5%", "en-US"), [("-5", "%")])
        self.assertTrue(numeric_semantics_match(
            "Use at 5+ stacks.", "Utilisez avec au moins 5 cumuls."
        ))


if __name__ == "__main__":
    unittest.main()
