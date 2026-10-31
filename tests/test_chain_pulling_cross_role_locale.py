"""Source-only cross-role chain-pulling jargon regression.

Restoration Druid leveling and Assassination Rogue M+ rotation describe
consecutive pulls with different English spellings. Indexed Wowhead evidence
does not establish browser-rendered translation quality.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class ChainPullingCrossRoleLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_narrow_jargon_does_not_override_other_pull_meanings(self):
        terms = select_jargon(self.player, "en-US", "fr-FR")
        self.assertEqual(terms["chainpulls"], "pulls enchaînés")
        self.assertEqual(terms["chain pulling"], "enchaîner les pulls")
        # A chain pull may also mean an accidental aggro chain; don't force
        # generic "pull" or "chain pull" in unrelated encounter prose.
        for ambiguous in ("pull", "pulls", "chain pull", "chain pulls", "chain", "pulling"):
            self.assertNotIn(ambiguous, terms)
        for layer in ("exact", "jargon"):
            legacy = {key.casefold() for key in self.manual.get(layer, {})}
            self.assertNotIn("chainpulls", legacy)
            self.assertNotIn("chain pulling", legacy)

    def test_locale_isolation_and_same_language_skip(self):
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en-US", "de-DE")

    def test_independent_guide_sources_in_corpus(self):
        urls = {page["url"] for page in self.pages}
        for suffix in (
            "druid/restoration/healer-leveling-tips",
            "rogue/assassination/rotation-cooldowns-pve-dps",
        ):
            with self.subTest(suffix=suffix):
                self.assertIn("https://www.wowhead.com/guide/classes/" + suffix, urls)


if __name__ == "__main__":
    unittest.main()
