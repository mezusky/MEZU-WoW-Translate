"""Cross-class French terminology regression for TBC tank threat efficiency."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ThreatPerRageLocaleTests(unittest.TestCase):
    def test_tank_phrase_is_locale_scoped_and_not_a_generic_rage_override(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        jargon = glossary["jargon"]
        self.assertEqual(jargon["threat per rage"], "menace générée par point de rage")
        self.assertEqual(jargon["Threat per Rage"], "Menace générée par point de rage")
        self.assertNotIn("rage", jargon)
        self.assertNotIn("threat", jargon)

    def test_independent_tbc_tank_sources_are_in_corpus(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        urls = {page["url"] for page in pages}
        self.assertIn("https://www.wowhead.com/tbc/guide/classes/druid/feral/tank-overview-pve", urls)
        self.assertIn("https://www.wowhead.com/tbc/guide/classes/warrior/protection/tank-stat-priority-attributes-pve", urls)

if __name__ == "__main__":
    unittest.main()
