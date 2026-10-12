import unittest
from scripts.html_block_extractor import extract_blocks


class TestInlineMarkup(unittest.TestCase):
    def test_inline_spell_link(self):
        self.assertEqual(extract_blocks('<p>Use <a href="/spell=1">Spell</a> now</p>'), [('p', 'Use Spell now')])

    def test_script_is_not_guide_text(self):
        self.assertEqual(extract_blocks('<p>Before<script>BAD</script>After</p>'), [('p', 'Before After')])
