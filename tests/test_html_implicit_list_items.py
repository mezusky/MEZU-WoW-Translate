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


    def test_hidden_unclosed_sibling_does_not_hide_following_priority(self):
        examples = (
            ("Protection Warrior", "Shield Slam", "Ignore Pain"),
            ("Preservation Evoker", "Temporal Anomaly", "Dream Breath"),
            ("Demonology Warlock", "Dreadstalkers", "Hand of Gul'dan"),
        )
        for guide, first, last in examples:
            with self.subTest(guide=guide):
                html = (f"<main><h2>{guide}</h2><ol>"
                        f"<li>{first}<li hidden>Hidden tooltip"
                        f"<li>{last}</ol></main>")
                self.assertEqual(extract_readable_blocks(html), [
                    ("h2", guide), ("li", first), ("li", last)
                ])

    def test_hidden_last_item_without_end_tag_does_not_hide_next_section(self):
        html = ("<main><ul><li>First<li hidden>Secret</ul>"
                "<p>After the list.</p></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "First"), ("p", "After the list.")
        ])

    def test_hidden_item_with_inline_child_implicitly_closes(self):
        html = ("<main><ol><li hidden><span>Hidden tooltip"
                "<li>Visible priority</ol></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "Visible priority")
        ])

    def test_nested_hidden_list_remains_hidden_until_its_own_end(self):
        html = ("<main><ul><li hidden>Hidden parent"
                "<ul><li>Hidden child</li></ul>"
                "<li>Visible sibling</ul></main>")
        self.assertEqual(extract_readable_blocks(html), [
            ("li", "Visible sibling")
        ])


if __name__ == "__main__":
    unittest.main()
