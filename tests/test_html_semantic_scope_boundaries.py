"""Source-only extraction must not let malformed guide blocks absorb page chrome.

These synthetic cases protect audit statistics, not browser DOM reconstruction.
"""
import unittest

from scripts.html_block_extractor import extract_blocks, extract_readable_blocks


class SemanticScopeBoundaryTests(unittest.TestCase):
    def test_unclosed_guide_paragraph_stops_before_footer(self):
        html = (
            '<nav><p>Unrelated navigation.</p></nav>'
            '<main><h2>Tank cooldowns</h2>'
            '<p>Keep Shield Block active while tanking.</main>'
            '<footer><p>Subscribe to unrelated news.</p></footer>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h2', 'Tank cooldowns'),
            ('p', 'Keep Shield Block active while tanking.'),
        ])

    def test_nested_article_boundary_preserves_following_main_prose(self):
        html = (
            '<main><article><h2>Healer ramp</h2>'
            '<p>Apply Atonement before incoming damage.</article>'
            '<p>Use defensives when needed.</p></main>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h2', 'Healer ramp'),
            ('p', 'Apply Atonement before incoming damage.'),
            ('p', 'Use defensives when needed.'),
        ])

    def test_two_adjacent_semantic_containers_do_not_merge(self):
        html = (
            '<article><p>Spend Arcane Charges before capping.</article>'
            '<article><p>Maintain your damage buffs.</article>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('p', 'Spend Arcane Charges before capping.'),
            ('p', 'Maintain your damage buffs.'),
        ])

    def test_unscoped_mode_still_keeps_footer_separate(self):
        html = (
            '<main><p>Cast Penance on cooldown.</main>'
            '<footer><p>Footer feedback.</p></footer>'
        )
        self.assertEqual(extract_blocks(html), [
            ('p', 'Cast Penance on cooldown.'),
            ('p', 'Footer feedback.'),
        ])


if __name__ == "__main__":
    unittest.main()
