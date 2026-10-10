import unittest
from scripts.html_block_extractor import extract_blocks


class TestExtractor(unittest.TestCase):
    def test_nested_list(self):
        blocks = extract_blocks('<li>Before <p>Inside</p> After</li>')
        self.assertIn(('li', 'Before Inside After'), blocks)

    def test_script_is_ignored(self):
        self.assertEqual(extract_blocks('<p>Before<script>BAD</script>After</p>'), [('p', 'Before After')])
