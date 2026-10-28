"""Offline guard for official combat-assistant names reused across starter guides.

The 2025 Blizzard article 24205457 has matching EN/FR headings. Keep this
as official phrase memory, not page-specific manual sentence overrides.
This does not claim to reproduce the browser Translator API.
"""
import unittest

from scripts.build_blizzard_memory import SEED_IDS, align_blocks, good_pair


class OfficialCombatAssistantMemoryTests(unittest.TestCase):
    def test_source_article_remains_in_deterministic_seed_set(self):
        self.assertIn("24205457", SEED_IDS)

    def test_official_ui_labels_align_as_reusable_short_phrases(self):
        # Verified against the paired official Blizzard EN/FR article.
        source = [
            ("h3", "Assisted Highlight"),
            ("h3", "Single-Button Assistant"),
        ]
        target = [
            ("h3", "Surbrillance d’aide"),
            ("h3", "Assistant à bouton unique"),
        ]
        pairs = align_blocks(source, target)
        self.assertEqual(len(pairs), 2)
        for (source_tag, english), (target_tag, french), score in pairs:
            with self.subTest(source=english):
                self.assertEqual(source_tag, "h3")
                self.assertEqual(target_tag, "h3")
                self.assertTrue(good_pair(english, french, score))

    def test_only_verified_ui_names_are_expected(self):
        # A Wowhead heading such as "Single Button Rotation Assistant" is
        # editorial wording, not an official Blizzard UI name.
        self.assertNotIn("Single Button Rotation Assistant", {
            "Assisted Highlight", "Single-Button Assistant"
        })


if __name__ == "__main__":
    unittest.main()
