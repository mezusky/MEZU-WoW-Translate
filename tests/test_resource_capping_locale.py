"""Cross-guide, data-only checks for French resource-capping terminology.

Source evidence is indexed English Wowhead text, not a Chrome/Translator API
render. These tests protect reusable locale-scoped terms without asserting
browser translation quality or requiring GitHub runners to fetch Wowhead.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYER = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
URLS = {page["url"] for page in PAGES}


class ResourceCappingLocaleTests(unittest.TestCase):
    def test_explicit_locale_and_semantic_distinction(self):
        self.assertEqual((PLAYER["sourceLanguage"], PLAYER["targetLanguage"]), ("en", "fr"))
        jargon = PLAYER["jargon"]
        self.assertEqual(jargon["Avoid Rage Waste"], "Éviter de gaspiller de la rage")
        self.assertEqual(jargon["Avoid Rage Capping"], "Éviter d’atteindre le maximum de rage")
        self.assertEqual(jargon["avoid capping Rage"], "éviter d’atteindre le maximum de rage")
        # Wasting rage through bad spending and losing resource at cap are
        # related but not synonymous. Do not flatten them into one broad rule.
        self.assertNotEqual(jargon["Avoid Rage Waste"], jargon["Avoid Rage Capping"])

    def test_shard_cap_variants_are_not_generic_overcap_rewrites(self):
        jargon = PLAYER["jargon"]
        expected = "Évitez de gaspiller des éclats d’âme en atteignant la limite"
        for source in ("Do not overcap Soul Shards", "Don't overcap Soul Shards"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], expected)
        # The same word can refer to stacks, charges or energy elsewhere.
        self.assertNotIn("do not overcap", jargon)
        self.assertNotIn("don't overcap", jargon)

    def test_terms_live_in_locale_data_not_manual_sentence_overrides(self):
        for source in ("Avoid Rage Waste", "Avoid Rage Capping", "avoid capping Rage",
                       "Do not overcap Soul Shards", "Don't overcap Soul Shards"):
            with self.subTest(source=source):
                self.assertNotIn(source, MANUAL.get("exact", {}))
                self.assertNotIn(source, MANUAL.get("jargon", {}))

    def test_unrelated_source_guides_cover_both_resources(self):
        # Warrior Protection and Guardian Druid discuss Rage; Destruction
        # and Demonology Warlock independently discuss Soul Shard overcapping.
        for cls, spec, slug in (
            ("warrior", "protection", "rotation-cooldowns-pve-tank"),
            ("druid", "guardian", "rotation-cooldowns-pve-tank"),
            ("warlock", "destruction", "rotation-cooldowns-pve-dps"),
            ("warlock", "demonology", "rotation-cooldowns-pve-dps"),
        ):
            with self.subTest(spec=spec):
                self.assertIn(f"https://www.wowhead.com/guide/classes/{cls}/{spec}/{slug}", URLS)

    def test_new_heldout_sources_span_four_specs_and_two_sections(self):
        cases = (
            ("mage", "arcane", "midnight-pre-patch"),
            ("shaman", "enhancement", "midnight-pre-patch"),
            ("hunter", "beast-mastery", "dps-leveling-tips"),
            ("rogue", "subtlety", "dps-leveling-tips"),
        )
        for cls, spec, slug in cases:
            with self.subTest(spec=spec):
                self.assertIn(f"https://www.wowhead.com/guide/classes/{cls}/{spec}/{slug}", URLS)


if __name__ == "__main__":
    unittest.main()
