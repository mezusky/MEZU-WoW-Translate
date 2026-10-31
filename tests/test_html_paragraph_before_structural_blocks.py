"""Source-only HTML repair for implicit paragraph endings before block tags.

The examples reflect list/table/heading patterns in independent Wowhead tank,
healer and DPS guides. They are synthetic, not a claim about live browser DOM
or Chrome Translator API output.
"""
import unittest

from scripts.html_block_extractor import extract_readable_blocks


class ParagraphBeforeBlockTests(unittest.TestCase):
    def test_tank_intro_does_not_absorb_priority_list(self):
        html = (
            "<main><p>Protection Warrior priority:"
            "<ol><li>Maintain Shield Block.</li><li>Spend excess Rage.</li></ol>"
            "<p>Use Shield Wall for dangerous hits.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("p", "Protection Warrior priority:"),
            ("li", "Maintain Shield Block."),
            ("li", "Spend excess Rage."),
            ("p", "Use Shield Wall for dangerous hits."),
        ])

    def test_healer_intro_does_not_absorb_table_cells(self):
        html = (
            "<article><p>Discipline Priest ramp planning:"
            "<table><tr><td>Apply Atonement.</td>"
            "<td>Cast Power Word: Radiance.</td></tr></table>"
            "<p>Follow with damage spells.</p></article>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("p", "Discipline Priest ramp planning:"),
            ("td", "Apply Atonement."),
            ("td", "Cast Power Word: Radiance."),
            ("p", "Follow with damage spells."),
        ])

    def test_dps_intro_does_not_absorb_next_heading(self):
        html = (
            "<main><p>Manage Arcane Charges."
            "<h2>Easy Mode Priority</h2><p>Use Arcane Barrage.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("p", "Manage Arcane Charges."),
            ("h2", "Easy Mode Priority"),
            ("p", "Use Arcane Barrage."),
        ])

    def test_nested_list_parent_still_owns_its_child_paragraph(self):
        html = (
            "<main><ul><li><p>Plan your ramp."
            "<ul><li>Apply Atonement.</li></ul>"
            "Then deal damage.</li></ul></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "Plan your ramp. Apply Atonement. Then deal damage."),
        ])

    def test_hidden_list_still_closes_visible_paragraph(self):
        html = (
            "<main><p>Visible priority."
            "<ul hidden><li>Old priority.</li></ul>"
            "<p>Updated priority.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("p", "Visible priority."),
            ("p", "Updated priority."),
        ])


if __name__ == "__main__":
    unittest.main()
