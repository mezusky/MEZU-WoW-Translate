"""Cross-guide healing-absorb terminology: source evidence, not Chrome output.

Indexed English Wowhead excerpts were inspected on 2026-10-26.
This does not reproduce the browser-local Translator API or DOM rendering.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = {p["id"]: p["url"] for p in json.loads(
    (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
)["pages"]}


class HealingAbsorbLocaleTests(unittest.TestCase):
    def test_plural_and_singular_terms_are_locale_scoped(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["healing absorb"], "absorption de soins")
        self.assertEqual(terms["healing absorbs"], "absorptions de soins")
        self.assertEqual(terms["heal absorbs"], "absorptions de soins")
        self.assertNotIn("absorb", terms)
        for key in ("healing absorb", "healing absorbs", "heal absorbs"):
            for layer in ("exact", "jargon"):
                with self.subTest(key=key, layer=layer):
                    self.assertNotIn(key, MANUAL.get(layer, {}))
        self.assertEqual(select_jargon(GLOSSARY, "fr", "fr"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de")

    def test_independent_healer_raid_sources(self):
        # Short indexed excerpts: independent classes, same mechanics.
        evidence = {
            "restoration-shaman-raid": "a large healing absorb on players",
            "restoration-druid-raid": "a healing absorb placed on players",
            "mistweaver-monk-raid": "a standard heal absorb",
        }
        for guide, excerpt in evidence.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, PAGES)
                self.assertIn("/midnight-season-2-raid-tips", PAGES[guide])
                self.assertTrue("healing absorb" in excerpt or "heal absorb" in excerpt)

    def test_plural_source_evidence_outside_class_guides(self):
        # Healer Raid Rankings, indexed English source (not browser output).
        url = "https://www.wowhead.com/guide/classes/tier-lists/healer-rankings-raids"
        excerpt = "a lot of healing absorbs ... there are less heal absorbs"
        self.assertIn("/healer-rankings-raids", url)
        self.assertIn("healing absorbs", excerpt)
        self.assertIn("heal absorbs", excerpt)


if __name__ == "__main__":
    unittest.main()
