"""Cross-spec source-only checks for structured raid reminder imports.

Based on Holy and Discipline Priest Midnight Season 2 raid guides. This
does not assert Chrome translation or preservation of the live DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.source_language_evidence import (
    audit_source_prose, clean_non_prose, detect_source_language,
)

PROFILES = json.loads(
    (Path(__file__).resolve().parents[1] / "data/audit_language_signals.json")
    .read_text(encoding="utf-8")
)["profiles"]


class RaidReminderAuditTests(unittest.TestCase):
    def test_two_healer_specs_share_the_same_structured_format(self):
        prose = (
            "You should use your healing cooldowns when the group takes "
            "damage, and you can cast healing spells before the next wave "
            "while you have mana for the fight."
        )
        for spec_id, tag, spell in (
            ("holy-priest", 257, 64843),
            ("discipline-priest", 256, 472433),
        ):
            with self.subTest(spec=spec_id):
                notes = (
                    "EncounterID:3379;Difficulty:Heroic;Name:Nymrissa "
                    f"time:42;ph:1;tag:{tag};spellid:{spell}; "
                    f"time:78;ph:1.5;tag:{tag};spellid:{spell};"
                )
                mixed = prose + " " + notes + " Continue healing your group."
                cleaned, is_prose = audit_source_prose(mixed, "en-US", PROFILES)
                self.assertTrue(is_prose)
                self.assertNotIn("EncounterID:", cleaned)
                self.assertNotIn("spellid:", cleaned)
                self.assertIn("Continue healing your group.", cleaned)
                self.assertEqual(
                    detect_source_language([("p", mixed)], PROFILES)
                    ["detectedLanguage"], "en"
                )

    def test_notes_alone_cannot_become_language_evidence(self):
        notes = (
            "EncounterID:3470;Difficulty:Heroic;Name:Nek'zali "
            "time:31;ph:1;tag:257;spellid:200183; "
            "time:89;ph:1.5;tag:257;spellid:64843;"
        )
        self.assertFalse(clean_non_prose(notes).strip())
        result = detect_source_language([("td", notes)], PROFILES)
        self.assertEqual(result["tokenCount"], 0)
        self.assertIsNone(result["detectedLanguage"])

    def test_ordinary_raid_prose_and_incomplete_records_are_preserved(self):
        prose = (
            "Use time:25 as a reminder, and explain that EncounterID:3379 "
            "is an encounter identifier. The group should use its healing "
            "cooldowns when the next raid damage event occurs."
        )
        self.assertEqual(clean_non_prose(prose), prose)


if __name__ == "__main__":
    unittest.main()
