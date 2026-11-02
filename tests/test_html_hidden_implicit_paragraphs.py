"""Audit-only repair of HTML's implicit closing of hidden paragraphs.

Synthetic structures model cross-role guide prose; they are not live Wowhead
DOM observations or proof of Chrome Translator API behavior.
"""
import unittest

from scripts.html_block_extractor import extract_readable_blocks


class HiddenImplicitParagraphTests(unittest.TestCase):
    def test_hidden_unclosed_paragraph_does_not_swallow_next_role_tip(self):
        cases = (
            ("Protection Warrior", "Use Shield Slam."),
            ("Discipline Priest", "Apply Atonement."),
            ("Arcane Mage", "Spend Arcane Charges."),
        )
        for role, visible in cases:
            with self.subTest(role=role):
                html = (
                    "<main><p hidden><span>Outdated tooltip"
                    f"<p>{visible}</p></main>"
                )
                self.assertEqual(extract_readable_blocks(html), [("p", visible)])

    def test_visible_paragraphs_survive_hidden_unclosed_sibling(self):
        html = (
            "<main><p>Keep Bone Shield active."
            "<p style='display:none'><em>Old priority"
            "<p>Use Death Strike.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("p", "Keep Bone Shield active."),
            ("p", "Use Death Strike."),
        ])

    def test_hidden_paragraph_ends_before_structural_heading(self):
        html = (
            "<main><p hidden>Obsolete text"
            "<h3>Current priority</h3><p>Spend Rage.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("h3", "Current priority"), ("p", "Spend Rage."),
        ])

    def test_nested_hidden_container_does_not_become_visible(self):
        html = (
            "<main><div hidden><p>Old tip<p>Still old.</p></div>"
            "<p>Current tip.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [("p", "Current tip.")])

    def test_inert_template_inside_hidden_paragraph_stays_hidden(self):
        html = (
            "<main><p hidden><template><p>Inert text.</p></template>"
            "Still hidden.</p><p>Current text.</p></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [("p", "Current text.")])


if __name__ == "__main__":
    unittest.main()
