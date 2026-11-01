"""Source-only regression: block headings must not glue WoW guide prose together.

These synthetic HTML fragments model nested guide widgets seen in indexed
Blood DK priority descriptions. They do not assert live Wowhead DOM shape or
Chrome Translator API behavior.
"""
import unittest

from scripts.html_block_extractor import extract_blocks


class HeadingBoundaryTests(unittest.TestCase):
    def test_heading_inside_priority_item(self):
        html = ('<li>Cast Death Strike above 75 Runic Power'
                '<h4>Why 75?</h4>'
                'This is a resource threshold.</li>')
        self.assertEqual(extract_blocks(html), [
            ("li", "Cast Death Strike above 75 Runic Power Why 75? This is a resource threshold.")
        ])

    def test_heading_inside_gear_table_cell(self):
        html = ('<table><tr><td>Maintain Bone Shield'
                '<h5>Are there other generators?</h5>'
                'Yes, several.</td><td>Second cell</td></tr></table>')
        self.assertEqual(extract_blocks(html), [
            ("td", "Maintain Bone Shield Are there other generators? Yes, several."),
            ("td", "Second cell"),
        ])

    def test_standalone_heading_and_adjacent_paragraphs(self):
        html = '<main><h3>Priority</h3><p>Spend Rage.</p><p>Use cooldowns.</p></main>'
        self.assertEqual(extract_blocks(html), [
            ("h3", "Priority"), ("p", "Spend Rage."), ("p", "Use cooldowns.")
        ])


if __name__ == "__main__":
    unittest.main()
