"""Implicit HTML table-cell closure across independent Wowhead guide sections.

These are synthetic source-audit fixtures, not live DOM/Translator API claims.
HTMLParser does not repair omitted </td> or </th> tags on its own.
"""
import unittest

from scripts.html_block_extractor import extract_readable_blocks


class ImplicitTableCellTests(unittest.TestCase):
    def test_missing_cell_end_tags_do_not_merge_gear_rows(self):
        html = ("<main><table><tr><th>Slot<th>Best item"
                "<tr><td>Weapon<td>Staff<tr><td>Ring<td>Band"
                "</table></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("th", "Slot"), ("th", "Best item"),
            ("td", "Weapon"), ("td", "Staff"),
            ("td", "Ring"), ("td", "Band"),
        ])

    def test_unclosed_paragraph_does_not_swallow_next_stat_cell(self):
        html = ("<main><table><tr><td><p>Haste first."
                "<td>Mastery second.</tr></table></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("td", "Haste first."), ("td", "Mastery second."),
        ])

    def test_hidden_unclosed_cell_does_not_hide_healer_consumables(self):
        html = ("<main><table><tr><td>Flask"
                "<td hidden><span>Obsolete enchant"
                "<td>Current flask</tr><tr><td>Gem<td>Current gem"
                "</table></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("td", "Flask"), ("td", "Current flask"),
            ("td", "Gem"), ("td", "Current gem"),
        ])

    def test_nested_table_keeps_outer_raid_cell_open(self):
        html = ("<main><table><tr><td>Boss timing "
                "<table><tr><td>Phase one</td></tr></table>"
                " then move</td><td>Defensive CD</td></tr></table></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("td", "Boss timing Phase one then move"),
            ("td", "Defensive CD"),
        ])

    def test_explicit_cells_are_unchanged(self):
        html = ("<main><table><tr><td>Shield Block</td>"
                "<td>Ignore Pain</td></tr></table></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("td", "Shield Block"), ("td", "Ignore Pain"),
        ])


if __name__ == "__main__":
    unittest.main()
