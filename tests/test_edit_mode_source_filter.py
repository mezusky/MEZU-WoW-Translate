"""Whole-cell Edit Mode exports must not distort source-only language audits.

Synthetic layouts reflect the format observed in independent Wowhead Frost Mage,
Guardian Druid, and Beast Mastery Hunter UI guides. No full exports are stored.
These checks do not validate the Chrome Translator API or browser DOM.
"""
import json
import unittest
from pathlib import Path

from scripts.source_language_evidence import (
    audit_source_prose, detect_source_language, is_opaque_edit_mode_export
)

PROFILES = json.loads((Path(__file__).resolve().parents[1] /
                       "data/audit_language_signals.json").read_text(
                           encoding="utf-8"))["profiles"]


def layout(first_frame):
    prefix = f"2 50 0 0 0 7 7 {first_frame} 0.0 45.0 -1 ##$$%/& "
    record = "0 1 1 7 7 UIParent 0.0 45.0 -1 ##$$%/&('%(#,$ "
    return prefix + record * 8


class EditModeSourceFilterTests(unittest.TestCase):
    def test_unrelated_class_exports_are_not_prose(self):
        for first_frame in ("UIParent", "ChatFrame1", "MainActionBar"):
            with self.subTest(frame=first_frame):
                raw = layout(first_frame)
                self.assertTrue(is_opaque_edit_mode_export(raw))
                self.assertEqual(audit_source_prose(raw, "en", PROFILES), ("", False))
                self.assertEqual(audit_source_prose(raw, "fr", PROFILES), ("", False))

    def test_neighboring_description_cells_remain_scored(self):
        blocks = [
            ("td", layout("UIParent")),
            ("td", "You can import this interface for your raid, and "
                   "use the cooldown manager during the fight."),
            ("p", "The setup also helps you track your spells and abilities "
                  "when you play in a dungeon with other players."),
        ]
        evidence = detect_source_language(blocks, PROFILES)
        self.assertEqual(evidence["detectedLanguage"], "en")
        self.assertEqual(audit_source_prose(blocks[1][1], "en", PROFILES)[0],
                         blocks[1][1])

    def test_short_or_prose_like_layout_mentions_are_not_erased(self):
        examples = (
            "Use UIParent in the editor when you adjust the interface.",
            "2 50 0 0 0 7 7 UIParent 0.0 45.0 -1 ##$",
            "The UIParent frame is used to anchor your cooldown manager.",
        )
        for example in examples:
            with self.subTest(example=example[:24]):
                self.assertFalse(is_opaque_edit_mode_export(example))
                self.assertEqual(audit_source_prose(example, "en", PROFILES)[0],
                                 example)


if __name__ == "__main__":
    unittest.main()
