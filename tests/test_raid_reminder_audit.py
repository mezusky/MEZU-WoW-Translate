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


    def test_method_raid_tools_time_spell_notes_do_not_pollute_prose(self):
        # Restoration Shaman Manaforge Omega; different from NSRT priest notes.
        prose = "Plan your healing cooldowns for the next raid damage event."
        notes = (
            "{time:1:20}1:20 Theun {spell:114052} Asc\n"
            "{time:2:20}2:20 Theun {spell:108280} HTT"
        )
        cleaned, signal = audit_source_prose(
            prose + "\n" + notes + "\nContinue healing the group.", "en", PROFILES
        )
        self.assertTrue(signal)
        self.assertIn(prose, cleaned)
        self.assertIn("Continue healing the group.", cleaned)
        self.assertNotIn("{time:", cleaned)
        self.assertNotIn("{spell:", cleaned)

    def test_mrt_note_requires_structured_line_not_ordinary_prose(self):
        # Avoid hiding explanatory text or incomplete user-written examples.
        prose = "Explain the {time:1:20} marker and {spell:114052} link to your raid."
        self.assertEqual(clean_non_prose(prose), prose)
        self.assertEqual(clean_non_prose("{time:1:20} This is a prose explanation."),
                         "{time:1:20} This is a prose explanation.")


if __name__ == "__main__":
    unittest.main()
