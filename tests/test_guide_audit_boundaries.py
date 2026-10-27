"""Source-only regression: discussion/footer text is not guide prose.

Synthetic HTML models indexed Midnight Outlaw Rogue, Holy Priest, and
Preservation Evoker guide endings. No browser translation is asserted.
"""
import unittest

from scripts.guide_audit_boundaries import trim_guide_footer
from scripts.html_block_extractor import extract_readable_blocks


class GuideAuditBoundariesTests(unittest.TestCase):
    def test_dps_feedback_excludes_author_bio_and_comments(self):
        html = ('<main><h2>Outlaw Rogue Rotation</h2>'
                '<p>Spend combo points at five or more.</p>'
                '<h2>Feedback</h2><p>Join our Discord server.</p>'
                '<h2>JustGuy</h2><p>World of Warcraft guide writer.</p>'
                '<h2>Comments</h2><p>Old player comment.</p></main>')
        self.assertEqual(trim_guide_footer(extract_readable_blocks(html)), [
            ('h2', 'Outlaw Rogue Rotation'),
            ('p', 'Spend combo points at five or more.'),
        ])

    def test_healer_comments_boundary_without_feedback(self):
        html = ('<article><h2>Holy Priest Leveling</h2>'
                '<p>Use your healing cooldowns.</p>'
                '<h3>Comments</h3><p>Reader speculation.</p></article>')
        self.assertEqual(trim_guide_footer(extract_readable_blocks(html)), [
            ('h2', 'Holy Priest Leveling'),
            ('p', 'Use your healing cooldowns.'),
        ])

    def test_healer_contribute_boundary(self):
        blocks = [('h2', 'Preservation Evoker Consumables'),
                  ('p', 'Choose gems for your stats.'),
                  ('h2', 'Contribute'),
                  ('p', 'Submit a correction.')]
        self.assertEqual(trim_guide_footer(blocks), blocks[:2])

    def test_guide_feedback_mentions_and_subheadings_are_preserved(self):
        blocks = [('h2', 'Talent Feedback and Procs'),
                  ('p', 'Feedback on this talent is positive.'),
                  ('h3', 'Feedback from simulations'),
                  ('p', 'Use the best talent build.')]
        self.assertEqual(trim_guide_footer(blocks), blocks)

    def test_footer_matching_is_case_and_space_insensitive(self):
        blocks = [('h2', 'Rotation'), ('p', 'Use spells.'),
                  ('h2', ' FEEDBACK '), ('p', 'Do not score this.')]
        self.assertEqual(trim_guide_footer(blocks), blocks[:2])

    def test_indexed_comments_without_discussion_header(self):
        # Independent Elemental Shaman consumables and Windwalker Monk
        # cheat-sheet search results include individual "Comment by" headings.
        blocks = [('h2', 'Elemental Shaman Consumables'),
                  ('p', 'Use the recommended flask for your build.'),
                  ('h3', 'Comment by avatar1337'),
                  ('p', 'Is a different gem better?'),
                  ('h3', 'Comment by minka25'),
                  ('p', 'Why is the table missing an item?')]
        self.assertEqual(trim_guide_footer(blocks), blocks[:2])

    def test_comment_mentions_inside_guide_prose_are_not_a_boundary(self):
        blocks = [('h2', 'Community Discussion Tips'),
                  ('p', 'A Comment by a player is not an official guide.'),
                  ('h3', 'Comments about talents'),
                  ('p', 'Keep reading for the rotation advice.')]
        self.assertEqual(trim_guide_footer(blocks), blocks)

    def test_indexed_comment_heading_whitespace_and_case(self):
        blocks = [('h2', 'Guide'), ('p', 'Actual guide content.'),
                  ('h3', ' COMMENT   BY  ExamplePlayer '),
                  ('p', 'Reader discussion only.')]
        self.assertEqual(trim_guide_footer(blocks), blocks[:2])

    def test_no_footer_returns_independent_copy(self):
        blocks = [('h2', 'Stats'), ('p', 'Haste and Mastery.')]
        result = trim_guide_footer(blocks)
        self.assertEqual(result, blocks)
        self.assertIsNot(result, blocks)


if __name__ == '__main__':
    unittest.main()
