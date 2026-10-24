"""Offline audit extraction must ignore non-rendered guide widget content."""
import unittest
from scripts.html_block_extractor import extract_blocks


class TestHiddenGuideContent(unittest.TestCase):
    def test_hidden_talent_build_with_nested_same_tag(self):
        html = ('<article><div hidden><div><p>Old build</p></div></div>'
                '<p>Use <a href="/spell=1">Stormkeeper</a> on cooldown.</p></article>')
        self.assertEqual(extract_blocks(html), [('p', 'Use Stormkeeper on cooldown.')])

    def test_inline_hidden_and_visible_continuation(self):
        html = ('<p>Use <span style="display: none !important"><span>obsolete</span>'
                '</span><b>your</b> cooldown.</p>')
        self.assertEqual(extract_blocks(html), [('p', 'Use your cooldown.')])

    def test_hidden_widget_with_void_elements(self):
        html = ('<article><section style="visibility:hidden"><img src="x">'
                '<p>Hidden</p></section><p>Visible</p></article>')
        self.assertEqual(extract_blocks(html), [('p', 'Visible')])

    def test_hidden_attribute_false_still_hidden(self):
        self.assertEqual(extract_blocks('<p hidden="false">Hidden</p><p>Shown</p>'),
                         [('p', 'Shown')])

    def test_aria_hidden_does_not_imply_visually_hidden(self):
        self.assertEqual(extract_blocks('<p aria-hidden="true">Visible to sighted users</p>'),
                         [('p', 'Visible to sighted users')])

    def test_existing_template_svg_and_script_behavior(self):
        html = ('<p>Start<template><svg><title>Bad</title></svg></template>'
                '<script>Bad</script> End</p>')
        self.assertEqual(extract_blocks(html), [('p', 'Start End')])


if __name__ == '__main__':
    unittest.main()
