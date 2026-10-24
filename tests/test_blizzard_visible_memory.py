"""Official Blizzard phrase-memory extraction must ignore invisible HTML."""
import unittest

from scripts.build_blizzard_memory import clean_blocks


class BlizzardVisibleMemoryTests(unittest.TestCase):
    def test_scoped_article_preserves_nested_visible_prose(self):
        html = (
            "<header><p>Unrelated navigation text outside article.</p></header>"
            "<main><h2>Combat changes</h2>"
            "<p>Spend <strong>Soul Shards</strong> before the burst window.</p>"
            "<p>Use <em>defensive cooldowns</em> during raid damage.</p>"
            "<p>Preserve exact spell names in localized guides.</p>"
            "<script><p>Never translate this script payload.</p></script>"
            "<template><p>Hidden template guide placeholder.</p></template>"
            "<div style='display:none'><p>Hidden rotation advice.</p></div>"
            "</main>"
        )
        blocks = clean_blocks(html)
        texts = [text for _, text in blocks]
        self.assertIn("Spend Soul Shards before the burst window.", texts)
        self.assertIn("Use defensive cooldowns during raid damage.", texts)
        self.assertNotIn("Unrelated navigation text outside article.", texts)
        self.assertFalse(any("script payload" in text or "Hidden" in text for text in texts))

    def test_unscoped_fallback_excludes_hidden_content(self):
        html = (
            "<p>Blizzard class changes are available today.</p>"
            "<p>Talent adjustments apply to all players.</p>"
            "<p hidden>Invisible talent instructions.</p>"
            "<svg><text>Hidden tooltip icon label.</text></svg>"
        )
        texts = [text for _, text in clean_blocks(html)]
        self.assertEqual(texts, [
            "Blizzard class changes are available today.",
            "Talent adjustments apply to all players.",
        ])


if __name__ == "__main__":
    unittest.main()
