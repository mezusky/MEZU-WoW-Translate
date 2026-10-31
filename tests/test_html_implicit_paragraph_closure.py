"""Audit-only HTMLParser repair for implicitly closed sibling paragraphs.

Representative WoW guide structures span tank rotation, healer guidance and
DPS stats. These are synthetic fragments, not verified Wowhead DOM or Chrome
Translator API output.
"""
import unittest

from scripts.html_block_extractor import extract_blocks, extract_readable_blocks


class ImplicitParagraphClosureTests(unittest.TestCase):
    def test_adjacent_unclosed_paragraphs_are_independent_across_roles(self):
        cases = (
            ("Protection Warrior", "Maintain Shield Block.", "Spend Rage."),
            ("Restoration Druid", "Apply your HoTs.", "Prepare your next heal."),
            ("Arcane Mage", "Manage Arcane Charges.", "Check your stat priority."),
        )
        for guide, first, second in cases:
            with self.subTest(guide=guide):
                html = f"<main><h2>{guide}</h2><p>{first}<p>{second}</p></main>"
                self.assertEqual(extract_readable_blocks(html), [
                    ("h2", guide), ("p", first), ("p", second)
                ])

    def test_implicit_closure_inside_cell_keeps_one_parent_block(self):
        html = "<main><table><tr><td><p>Keep a defensive ready.<p>Use it early.</td></tr></table></main>"
        self.assertEqual(extract_readable_blocks(html), [
            ("td", "Keep a defensive ready. Use it early.")
        ])

    def test_implicit_closure_inside_list_keeps_one_parent_block(self):
        html = "<main><ul><li><p>Build resources.<p>Spend before capping.</li></ul></main>"
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "Build resources. Spend before capping.")
        ])

    def test_hidden_new_paragraph_still_closes_visible_previous_one(self):
        html = "<main><p>First visible tip.<p hidden>Hidden template tip.</p><p>Second visible tip.</p></main>"
        self.assertEqual(extract_readable_blocks(html), [
            ("p", "First visible tip."), ("p", "Second visible tip.")
        ])

    def test_inert_descendant_does_not_close_visible_paragraph(self):
        html = "<p>Before <template><p>Never visible</p></template> after.</p>"
        self.assertEqual(extract_blocks(html), [("p", "Before after.")])

    def test_valid_sibling_paragraphs_unchanged(self):
        self.assertEqual(extract_blocks("<p>First.</p><p>Second.</p>"), [
            ("p", "First."), ("p", "Second.")
        ])


if __name__ == "__main__":
    unittest.main()
