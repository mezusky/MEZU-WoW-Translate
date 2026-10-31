"""Regression checks for HTML's optional </li> end tag in source-only audits.

These synthetic guide fragments represent tank, healer and DPS priority lists;
they are not claims about the live Wowhead DOM or Chrome Translator API.
"""
import unittest

from scripts.html_block_extractor import extract_blocks, extract_readable_blocks


class ImplicitListItemTests(unittest.TestCase):
    def test_unclosed_sibling_items_stay_separate_across_roles(self):
        examples = (
            ("Protection Warrior", "Use Shield Slam.", "Spend excess Rage."),
            ("Discipline Priest", "Apply Atonement.", "Cast Penance."),
            ("Demonology Warlock", "Summon Dreadstalkers.", "Spend Soul Shards."),
        )
        for guide, first, second in examples:
            with self.subTest(guide=guide):
                html = f"<main><h2>{guide}</h2><ol><li>{first}<li>{second}</ol></main>"
                self.assertEqual(extract_readable_blocks(html), [
                    ("h2", guide), ("li", first), ("li", second)
                ])

    def test_nested_list_keeps_parent_item_whole(self):
        html = (
            "<main><ul><li>Prepare the ramp."
            "<ul><li>Apply Atonement.<li>Deal damage.</ul>"
            "Finish the ramp.<li>Recover mana.</ul></main>"
        )
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "Prepare the ramp. Apply Atonement. Deal damage. Finish the ramp."),
            ("li", "Recover mana."),
        ])

    def test_unclosed_nested_paragraph_does_not_swallow_next_item(self):
        html = "<main><ol><li><p>Use Shield Block.<li>Use Ignore Pain.</ol></main>"
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "Use Shield Block."), ("li", "Use Ignore Pain.")
        ])

    def test_explicitly_closed_list_items_remain_unchanged(self):
        self.assertEqual(extract_blocks("<ul><li>One.</li><li>Two.</li></ul>"), [
            ("li", "One."), ("li", "Two.")
        ])

    def test_hidden_sibling_does_not_pollute_visible_items(self):
        html = "<main><ul><li>First.<li hidden>Hidden.</li><li>Second.</ul></main>"
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "First."), ("li", "Second.")
        ])


if __name__ == "__main__":
    unittest.main()
