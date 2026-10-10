"""Regression tests for HTML audit block extraction."""
import unittest
from scripts.html_block_extractor import extract_blocks


class TestMarkup(unittest.TestCase):
    def test_hidden_script_is_not_prose(self):
        self.assertEqual(extract_blocks("<p>A<script>ignore</script>B</p>"), [("p", "A B")])

    def test_inline_link_preserves_words(self):
        self.assertEqual(extract_blocks('<p>Use <a href="/spell=1">Penance</a> now</p>'), [("p", "Use Penance now")])
