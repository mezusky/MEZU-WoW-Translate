"""Audit extraction must exclude CSS-hidden guide and official-memory text."""
import unittest

from scripts.html_block_extractor import extract_readable_blocks, inline_style_hidden
from scripts.build_blizzard_memory import clean_blocks


class ExtendedVisibilityTests(unittest.TestCase):
    def test_collapsed_table_row_is_not_a_visible_item(self):
        html = (
            '<main><h1>Assassination Rogue gear</h1><table>'
            '<tr style="visibility:collapse"><td>Obsolete trinket</td></tr>'
            '<tr><td>Current trinket</td></tr></table>'
            '<p>Use the current trinket for burst.</p></main>'
        )
        blocks = extract_readable_blocks(html)
        self.assertIn(('td', 'Current trinket'), blocks)
        self.assertNotIn(('td', 'Obsolete trinket'), blocks)

    def test_hidden_content_visibility_does_not_enter_blizzard_memory(self):
        html = (
            '<article><h2>Class tuning</h2>'
            '<div style="content-visibility:hidden"><p>Discarded draft.</p></div>'
            '<p>New tuning is available.</p></article>'
        )
        self.assertEqual(clean_blocks(html), [
            ('h2', 'Class tuning'),
            ('p', 'New tuning is available.'),
        ])

    def test_cascade_order_and_important_for_content_visibility(self):
        self.assertFalse(inline_style_hidden(
            'content-visibility:hidden; content-visibility:visible'))
        self.assertTrue(inline_style_hidden(
            'content-visibility:hidden !important; content-visibility:visible'))
        self.assertFalse(inline_style_hidden(
            'content-visibility:hidden; content-visibility:visible !important'))
        self.assertTrue(inline_style_hidden('visibility:collapse'))
        self.assertFalse(inline_style_hidden(
            'visibility:collapse; visibility:visible'))


if __name__ == "__main__":
    unittest.main()
