"""Cross-page Wowhead template-slot regression cases (captured snippets only)."""
import unittest
from scripts.audit_translation_samples import audit_sample


class WowheadSlotTests(unittest.TestCase):
    def sample(self, source, translated):
        return {"sourceLanguage": "en-US", "targetLanguage": "fr-FR",
                "source": source, "translated": translated}

    def test_repeated_dungeon_utility_slots_preserved(self):
        source = ("The Blinding Vale: UTIL1_NAME UTIL1_USECASE. "
                  "Murder Row: UTIL1_NAME UTIL1_USECASE.")
        translated = ("Le Val aveuglant : UTIL1_NAME UTIL1_USECASE. "
                      "La rue du Meurtre : UTIL1_NAME UTIL1_USECASE.")
        self.assertNotIn("wowhead_slot_mismatch",
                         audit_sample(self.sample(source, translated)))

    def test_dropped_slot_on_second_dungeon_detected(self):
        source = ("The Blinding Vale: UTIL1_NAME UTIL1_USECASE. "
                  "Murder Row: UTIL1_NAME UTIL1_USECASE.")
        translated = ("Le Val aveuglant : UTIL1_NAME UTIL1_USECASE. "
                      "La rue du Meurtre : UTIL1_NAME.")
        self.assertIn("wowhead_slot_mismatch",
                      audit_sample(self.sample(source, translated)))

    def test_changed_slot_number_detected(self):
        source = "UTIL1_NAME UTIL2_NAME UTIL1_USECASE UTIL2_USECASE"
        translated = "UTIL1_NAME UTIL3_NAME UTIL1_USECASE UTIL2_USECASE"
        self.assertIn("wowhead_slot_mismatch",
                      audit_sample(self.sample(source, translated)))

    def test_wow_acronyms_are_not_template_slots(self):
        source = "Use AMS and DND for M+."
        translated = "Utilisez AMS et DND en MM+."
        self.assertNotIn("wowhead_slot_mismatch",
                         audit_sample(self.sample(source, translated)))


if __name__ == "__main__":
    unittest.main()
