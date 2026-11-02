"""Source-only audit regression: deep WoW guide headings remain visible blocks.

Synthetic HTML models tank, healer, and DPS guides; it does not prove live
Wowhead DOM structure or Chrome Translator API behavior.
"""
import unittest

from scripts.html_block_extractor import extract_blocks, extract_readable_blocks


class DeepHeadingTests(unittest.TestCase):
    def test_h5_h6_are_retained_as_standalone_source_blocks(self):
        cases = (
            ("Brewmaster Monk", "Managing Stagger", "Use Purifying Brew."),
            ("Discipline Priest", "Raid Preparation", "Prepare Atonement."),
            ("Frost Mage", "Stat Breakpoints", "Check Mastery rating."),
        )
        for spec, heading, prose in cases:
            with self.subTest(spec=spec):
                html = f"<main><h5>{heading}</h5><h6>Details</h6><p>{prose}</p></main>"
                self.assertEqual(extract_readable_blocks(html), [
                    ("h5", heading), ("h6", "Details"), ("p", prose),
                ])

    def test_deep_heading_does_not_leak_site_navigation(self):
        html = ("<nav><h5>Sidebar link</h5></nav>"
                "<article><h6>Talent Notes</h6><p>Spend Rage.</p></article>")
        self.assertEqual(extract_readable_blocks(html), [
            ("h6", "Talent Notes"), ("p", "Spend Rage."),
        ])

    def test_nested_deep_heading_preserves_parent_list_or_cell(self):
        html = ("<li>Spend Runic Power<h5>Why 75?</h5>Save resources.</li>"
                "<td>Mitigate damage<h6>When?</h6>Before the hit.</td>")
        self.assertEqual(extract_blocks(html), [
            ("li", "Spend Runic Power Why 75? Save resources."),
            ("td", "Mitigate damage When? Before the hit."),
        ])


if __name__ == "__main__":
    unittest.main()
