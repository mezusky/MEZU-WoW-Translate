"""Canonical ID mappings outrank prose rules in any translation direction.

Source-only, synthetic ID fixtures; this does not claim browser translation
or Wowhead DOM reconstruction has been verified.
"""
import unittest

from scripts.merge_entity_locales import project_locale_pairs
from scripts.merge_exact_layers import merge_exact_layers


class ExactLayerPriorityTests(unittest.TestCase):
    def test_manual_cannot_rename_verified_spell_or_item(self):
        entities = {
            "spell": {"123": {"en": "Holy Shock", "fr": "Horion sacré"}},
            "item": {"456": {"en": "Void Shield", "fr": "Bouclier du Vide"}},
        }
        canonical = project_locale_pairs(entities, "en", "fr")
        merged = merge_exact_layers(
            canonical,
            {"Holy Shock": "Choc sacré"},
            {"Void Shield": "Bouclier de vide"},
            {"Holy Shock": "Choc saint", "Void Shield": "Bouclier vide"},
        )
        self.assertEqual(merged["Holy Shock"], "Horion sacré")
        self.assertEqual(merged["Void Shield"], "Bouclier du Vide")

    def test_case_variants_cannot_bypass_id_priority(self):
        canonical = {"Power Word: Shield": "Mot de pouvoir : Bouclier"}
        merged = merge_exact_layers(
            canonical,
            {"power word: shield": "Bouclier de puissance"},
            {},
            {"POWER WORD: SHIELD": "Bouclier du pouvoir"},
        )
        self.assertEqual(merged, canonical)

    def test_manual_exception_still_wins_for_nonentity_prose(self):
        merged = merge_exact_layers(
            {"Penance": "Pénitence"},
            {"Keep your cooldowns ready.": "Gardez vos capacités disponibles."},
            {"Keep your cooldowns ready.": "Gardez vos CD disponibles."},
            {"Keep your cooldowns ready.": "Gardez vos CD prêts.",
             "Powerful opening burst.": "Gros burst à l'open."},
        )
        self.assertEqual(merged["Keep your cooldowns ready."], "Gardez vos CD prêts.")
        self.assertEqual(merged["Powerful opening burst."], "Gros burst à l'open.")
        self.assertEqual(merged["Penance"], "Pénitence")

    def test_official_prose_precedes_community_when_no_manual_rule(self):
        merged = merge_exact_layers({}, {"Raid": "Raid officiel"},
                                    {"Raid": "Raid communautaire"}, {})
        self.assertEqual(merged["Raid"], "Raid officiel")

    def test_reverse_or_nonenglish_direction_stays_generic(self):
        entities = {"spell": {"99": {
            "de": "Heiliger Schock", "fr": "Horion sacré", "en": "Holy Shock"}}}
        canonical = project_locale_pairs(entities, "de", "fr")
        merged = merge_exact_layers(canonical, {}, {},
                                    {"Heiliger Schock": "Choc saint"})
        self.assertEqual(merged["Heiliger Schock"], "Horion sacré")
        self.assertEqual(project_locale_pairs(entities, "fr", "fr"), {})


if __name__ == "__main__":
    unittest.main()
