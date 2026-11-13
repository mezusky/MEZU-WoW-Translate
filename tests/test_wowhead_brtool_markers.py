"""Regression coverage for Wowhead numbered template markers across guides."""
import unittest
from scripts.audit_translation_samples import audit_sample


class WowheadTemplateMarkerTests(unittest.TestCase):
    def sample(self, source, translated):
        return {"sourceLanguage": "en", "targetLanguage": "fr",
                "source": source, "translated": translated}

    def test_bis_gear_markers_preserved(self):
        self.assertNotIn("wowhead_slot_mismatch", audit_sample(self.sample(
            "BRTOOL1 BRTOOL2 BRTOOL3",
            "BRTOOL1 BRTOOL2 BRTOOL3")))

    def test_bis_gear_marker_lost(self):
        self.assertIn("wowhead_slot_mismatch", audit_sample(self.sample(
            "BRTOOL1 BRTOOL2", "BRTOOL1")))

    def test_bis_gear_marker_renumbered(self):
        self.assertIn("wowhead_slot_mismatch", audit_sample(self.sample(
            "BRTOOL1 BRTOOL2", "BRTOOL1 BRTOOL3")))

    def test_regular_wow_acronyms_not_markers(self):
        self.assertNotIn("wowhead_slot_mismatch", audit_sample(self.sample(
            "BiS DPS AoE GCD", "Meilleur équipement, dégâts, zone, recharge globale")))


if __name__ == "__main__":
    unittest.main()
