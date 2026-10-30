"""Block-separated WoW macros are not translation prose (source audit only)."""
import unittest

from scripts.html_block_extractor import extract_blocks
from scripts.source_language_evidence import clean_non_prose


class DivMacroBoundaryTests(unittest.TestCase):
    def test_div_macro_lines_do_not_pollute_surrounding_prose(self):
        # The same div layout is used by unrelated healer/tank/DPS snippets.
        examples = (
            ("Discipline Priest", "/cast [@mouseover] Penance"),
            ("Protection Paladin", "/cancelaura Divine Shield"),
            ("Shadow Priest", "/run local n=UnitName('target')"),
        )
        for role, command in examples:
            with self.subTest(role=role):
                html = (
                    "<p>Use your cooldowns carefully."
                    "<div>#showtooltip</div>"
                    f"<div>{command}</div>"
                    "<div>Keep the explanation readable for your group.</div>"
                    "</p>"
                )
                blocks = extract_blocks(html)
                self.assertEqual(len(blocks), 1)
                raw = blocks[0][1]
                self.assertIn("\n#showtooltip", raw)
                self.assertIn("\n" + command, raw)
                cleaned = clean_non_prose(raw)
                self.assertNotIn(command, cleaned)
                self.assertNotIn("#showtooltip", cleaned)
                self.assertIn("Use your cooldowns carefully.", cleaned)
                self.assertIn("Keep the explanation readable", cleaned)

    def test_inline_macro_mentions_remain_explanatory_prose(self):
        html = "<p>Type /cast in the macro window, then use the spell.</p>"
        cleaned = clean_non_prose(extract_blocks(html)[0][1])
        self.assertIn("/cast in the macro window", cleaned)

    def test_inline_emphasis_still_joins_words(self):
        html = "<p>Use <strong>your</strong> defensive cooldown.</p>"
        self.assertEqual(extract_blocks(html), [
            ("p", "Use your defensive cooldown.")
        ])


if __name__ == "__main__":
    unittest.main()
