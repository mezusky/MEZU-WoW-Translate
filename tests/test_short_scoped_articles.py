"""Short real article content must not be diluted by global page chrome."""
import unittest

from scripts.html_block_extractor import extract_readable_blocks
from scripts.build_blizzard_memory import clean_blocks


class ShortArticleScopeTests(unittest.TestCase):
    def test_short_wowhead_article_keeps_only_its_visible_guide_text(self):
        html = (
            '<nav><p>Old guide links and unrelated navigation.</p></nav>'
            '<main><h1>Raid guide</h1>'
            '<p>Use defensive cooldowns when raid damage begins.</p></main>'
            '<footer><p>Unrelated footer and advertisements.</p></footer>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h1', 'Raid guide'),
            ('p', 'Use defensive cooldowns when raid damage begins.'),
        ])

    def test_short_blizzard_notice_does_not_learn_navigation(self):
        html = (
            '<header><p>Visit the official World of Warcraft website.</p></header>'
            '<article><h2>Class tuning</h2>'
            '<p>Several talents receive adjustments this week.</p></article>'
            '<footer><p>Read more Blizzard news.</p></footer>'
        )
        self.assertEqual(clean_blocks(html), [
            ('h2', 'Class tuning'),
            ('p', 'Several talents receive adjustments this week.'),
        ])

    def test_heading_only_wrapper_can_fall_back_to_real_body(self):
        html = (
            '<main><h1>Site title</h1></main>'
            '<section><p>Actual article prose outside the empty wrapper.</p></section>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h1', 'Site title'),
            ('p', 'Actual article prose outside the empty wrapper.'),
        ])


if __name__ == "__main__":
    unittest.main()
