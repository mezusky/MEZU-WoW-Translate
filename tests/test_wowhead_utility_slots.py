"""Regression for unresolved utility markers observed in live Wowhead dungeon guides."""
import unittest
from scripts.audit_translation_samples import audit_sample


class WowheadUtilitySlotTests(unittest.TestCase):
    def test_preserved_slots_are_not_flagged(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "Useful abilities: UTIL1_NAME and UTIL1_USECASE.",
                  "translated": "Capacités utiles : UTIL1_NAME et UTIL1_USECASE."}
        self.assertNotIn("wowhead_slot_mismatch", audit_sample(sample))

    def test_changed_slot_is_flagged(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "UTIL1_NAME UTIL2_USECASE",
                  "translated": "UTIL1_NAME UTIL3_USECASE"}
        self.assertIn("wowhead_slot_mismatch", audit_sample(sample))

    def test_unrelated_acronyms_are_not_slots(self):
        sample = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "source": "AMS is useful in M+.",
                  "translated": "La carapace anti-magie est utile en MM+."}
        self.assertNotIn("wowhead_slot_mismatch", audit_sample(sample))


if __name__ == "__main__":
    unittest.main()
