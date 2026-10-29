"""End-to-end source audit: HTML extraction must not flatten WoW macro lines.

Representative structures occur in Protection Paladin (tank), Arcane Mage
(DPS), and Holy/Discipline Priest (healer) UI/Macros guides. Synthetic
snippets avoid copying guide prose. Browser translation is not tested.
"""
import json
import unittest
from pathlib import Path

from scripts.html_block_extractor import extract_readable_blocks
from scripts.source_language_evidence import audit_source_prose, detect_source_language

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "data/audit_language_signals.json").read_text(
    encoding="utf-8"))["profiles"]


class HtmlMacroLineBoundariesTests(unittest.TestCase):
    def test_br_separated_tank_macro_does_not_pollute_prose(self):
        html = (
            "<main><p>Use this macro before the next defensive cooldown.<br>"
            "#showtooltip Divine Shield<br>/stopcasting<br>"
            "/cancelaura Divine Shield<br>/cast Divine Shield<br>"
            "This explanation should remain readable.</p></main>"
        )
        blocks = extract_readable_blocks(html)
        self.assertEqual(len(blocks), 1)
        self.assertIn("\n/cast Divine Shield", blocks[0][1])
        clean, evidence = audit_source_prose(blocks[0][1], "en-US", PROFILES)
        self.assertTrue(evidence)
        self.assertIn("Use this macro before", clean)
        self.assertIn("This explanation should remain", clean)
        self.assertNotIn("#showtooltip", clean)
        self.assertNotIn("/cancelaura", clean)
        self.assertNotIn("/cast Divine Shield", clean)

    def test_raw_newlines_preserved_for_dps_and_healer_macros(self):
        for guide, command in (
            ("arcane-mage", "/castsequence reset=10 Arcane Barrage"),
            ("holy-priest", "/cast [@mouseover,help,nodead][] Flash Heal"),
        ):
            with self.subTest(guide=guide):
                html = (
                    "<article><p>Use your spells and cooldowns in combat.\n"
                    "#showtooltip\n" + command + "\n"
                    "Keep this explanation as normal guide prose.</p></article>"
                )
                blocks = extract_readable_blocks(html)
                clean, evidence = audit_source_prose(blocks[0][1], "en", PROFILES)
                self.assertTrue(evidence)
                self.assertNotIn(command, clean)
                self.assertNotIn("#showtooltip", clean)
                self.assertIn("Keep this explanation", clean)

    def test_inline_command_mentions_and_regular_markup_survive(self):
        html = (
            "<main><p>Type /cast in the macro window and use "
            "<a href='/spell=1'>Penance</a> on cooldown.</p></main>"
        )
        blocks = extract_readable_blocks(html)
        self.assertEqual(blocks, [(
            "p", "Type /cast in the macro window and use Penance on cooldown."
        )])
        clean, _ = audit_source_prose(blocks[0][1], "en", PROFILES)
        self.assertIn("Type /cast in the macro window", clean)

    def test_detection_does_not_count_macro_commands_as_prose(self):
        html = (
            "<article><p>Use your spells and cooldowns during the raid. "
            "You can cast your abilities when they are ready, and keep "
            "your rotation going for the entire fight.<br>"
            "#showtooltip<br>/cast Flash Heal<br>"
            "The next cast should be prepared before the encounter.</p>"
            "<p>Remember to use your other abilities after the pull "
            "when your cooldowns are ready.</p></article>"
        )
        blocks = extract_readable_blocks(html)
        result = detect_source_language(blocks, PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")


if __name__ == "__main__":
    unittest.main()
