"""Inline CSS precedence must not produce false visible/hidden guide blocks."""
import unittest

from scripts.html_block_extractor import extract_blocks, inline_style_hidden


class TestInlineVisibilityPrecedence(unittest.TestCase):
    def test_later_display_overrides_earlier_normal_declaration(self):
        html = '<article><p style="display:none;display:block">Shown</p></article>'
        self.assertEqual(extract_blocks(html), [("p", "Shown")])

    def test_later_hidden_declaration_wins(self):
        html = '<article><p style="display:block;display:none">Hidden</p><p>Shown</p></article>'
        self.assertEqual(extract_blocks(html), [("p", "Shown")])

    def test_important_hidden_survives_later_normal_override(self):
        self.assertTrue(inline_style_hidden("display:none!important; display:grid"))

    def test_later_important_visible_overrides_earlier_important_hidden(self):
        self.assertFalse(inline_style_hidden("display:none!important;display:flex!important"))

    def test_visibility_and_comments_are_handled(self):
        self.assertFalse(inline_style_hidden("visibility:hidden;/* legacy */visibility:visible"))
        self.assertTrue(inline_style_hidden("/* note */display:none;visibility:visible"))
        self.assertFalse(inline_style_hidden("display:none; /* reset */ display:block"))


if __name__ == "__main__":
    unittest.main()
