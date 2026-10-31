"""Nested semantic HTML blocks must not double-count guide prose.

Synthetic markup exercises the source-only audit extractor; this is not a
claim about live Wowhead DOM or Chrome Translator API reconstruction.
"""
import unittest

from scripts.html_block_extractor import extract_blocks, extract_readable_blocks


class NestedAuditBlockDedupTests(unittest.TestCase):
    def test_list_with_nested_paragraph_is_one_logical_block(self):
        html = ('<main><ul><li>Use <p>Penance on cooldown.</p> '
                'Then cast Smite.</li></ul></main>')
        self.assertEqual(
            extract_readable_blocks(html),
            [('li', 'Use Penance on cooldown. Then cast Smite.')],
        )

    def test_table_cell_with_nested_paragraph_is_one_block(self):
        html = ('<article><table><tr><td><p>Spend Rage</p>'
                '<p>before it caps.</p></td></tr></table></article>')
        self.assertEqual(
            extract_readable_blocks(html),
            [('td', 'Spend Rage before it caps.')],
        )

    def test_independent_sibling_blocks_are_not_lost(self):
        html = ('<main><p>Prepare Echo buffs.</p>'
                '<ul><li><p>Consume Echo.</p></li></ul>'
                '<p>Continue healing.</p></main>')
        self.assertEqual(
            extract_readable_blocks(html),
            [('p', 'Prepare Echo buffs.'), ('li', 'Consume Echo.'),
             ('p', 'Continue healing.')],
        )

    def test_unclosed_nested_markup_does_not_duplicate_on_close(self):
        self.assertEqual(
            extract_blocks('<li>Maintain <p>Shadow Word: Pain'),
            [('li', 'Maintain Shadow Word: Pain')],
        )


    def test_unclosed_paragraph_does_not_swallow_next_list_item(self):
        html = ('<main><ul><li><p>Cast Penance.</li>'
                '<li>Cast Smite.</li></ul></main>')
        self.assertEqual(
            extract_readable_blocks(html),
            [('li', 'Cast Penance.'), ('li', 'Cast Smite.')],
        )

    def test_unclosed_paragraph_does_not_swallow_next_table_cell(self):
        html = ('<main><table><tr><td><p>Maintain Shield Block.</td>'
                '<td>Spend Rage.</td></tr></table></main>')
        self.assertEqual(
            extract_readable_blocks(html),
            [('td', 'Maintain Shield Block.'), ('td', 'Spend Rage.')],
        )

    def test_normal_nested_paragraph_still_emits_one_parent(self):
        self.assertEqual(
            extract_blocks('<li><p>Prepare Echo.</p> Consume Echo.</li>'),
            [('li', 'Prepare Echo. Consume Echo.')],
        )


if __name__ == '__main__':
    unittest.main()
