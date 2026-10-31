"""Cross-locale source-only guard against training on Wowhead user comments.

Wowhead's /fr/ and /de/ guide pages can have English guide prose but
localized discussion UI. These fixtures are not browser translation tests.
"""
import unittest

from scripts.guide_audit_boundaries import trim_guide_footer
from scripts.html_block_extractor import extract_readable_blocks


class LocalizedGuideFooterTests(unittest.TestCase):
    def test_localized_comments_headings_cut_off_user_prose(self):
        headings = ("Commentaires", "Kommentare", "Comentarios",
                    "Comentários", "Commenti", "評論", "评论")
        for heading in headings:
            with self.subTest(heading=heading):
                html = ('<main><h2>Protection Warrior Rotation</h2>'
                        '<p>Spend excess Rage on Ignore Pain.</p>'
                        f'<h2>{heading}</h2>'
                        '<p>Unverified player speculation must not be audited.</p>'
                        '</main>')
                self.assertEqual(trim_guide_footer(extract_readable_blocks(html)), [
                    ("h2", "Protection Warrior Rotation"),
                    ("p", "Spend excess Rage on Ignore Pain."),
                ])

    def test_localized_author_heading_without_comments_header(self):
        for heading in ("Commentaire de MagePlayer", "Kommentar von PriestPlayer",
                        "Comentario de TankPlayer", "Comentário de HealerPlayer"):
            with self.subTest(heading=heading):
                blocks = [("h2", "Discipline Priest Rotation"),
                          ("p", "Use Penance offensively."),
                          ("h3", heading),
                          ("p", "Player opinion is not guide content.")]
                self.assertEqual(trim_guide_footer(blocks), blocks[:2])

    def test_french_contribute_footer(self):
        blocks = [("h2", "Preservation Evoker Overview"),
                  ("p", "Echo buffs duplicate healing."),
                  ("h2", "Contribuer"),
                  ("p", "Site contribution instructions.")]
        self.assertEqual(trim_guide_footer(blocks), blocks[:2])

    def test_in_guide_comment_mentions_are_preserved(self):
        blocks = [("h2", "Commentaires sur les talents"),
                  ("p", "A commenter may discuss this build."),
                  ("h3", "Kommentar von"),
                  ("p", "This is not an author heading without a name.")]
        self.assertEqual(trim_guide_footer(blocks), blocks)


if __name__ == "__main__":
    unittest.main()
