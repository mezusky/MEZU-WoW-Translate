import unittest
from scripts.html_block_extractor import extract_blocks


class TestInlineMarkup(unittest.TestCase):
    def test_inline_spell_link(self):
        self.assertEqual(extract_blocks('<p>Use <a href="/spell=1">Spell</a> now</p>'), [('p', 'Use Spell now')])

    def test_template_talent_widget_is_not_visible_guide_prose(self):
        html = ('<article><template><p>Hidden talent preview</p></template>'
                '<p>Use <a href="/spell=1">Penance</a> on cooldown.</p></article>')
        self.assertEqual(extract_blocks(html), [('p', 'Use Penance on cooldown.')])

    def test_svg_labels_do_not_leak_into_visible_text(self):
        html = ('<p>Use <svg><title>Copy build icon</title><text>Hidden</text>'
                '</svg>your cooldown.</p>')
        self.assertEqual(extract_blocks(html), [('p', 'Use your cooldown.')])

    def test_nested_inert_markup_does_not_truncate_following_content(self):
        html = ('<p>Start<template><svg><text>Invisible</text></svg>'
                '<p>Hidden</p></template> Finish</p>')
        self.assertEqual(extract_blocks(html), [('p', 'Start Finish')])

    def test_script_is_not_guide_text(self):
        self.assertEqual(extract_blocks('<p>Before<script>BAD</script>After</p>'), [('p', 'Before After')])
