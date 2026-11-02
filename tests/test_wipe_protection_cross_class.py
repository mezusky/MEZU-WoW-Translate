"""Cross-class source-only contract for raid wipe-protection jargon.

Current Brewmaster raid advice and independent Classic Paladin utility advice
use the same concept with different mechanics. No browser DOM or Translator API
result is asserted by these tests.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class WipeProtectionJargonTests(unittest.TestCase):
    def test_shared_noun_is_locale_scoped_and_not_a_sentence_override(self):
        glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        self.assertEqual(glossary["jargon"]["wipe protection"], "protection en cas de wipe")
        self.assertEqual(select_jargon(glossary, "en-US", "fr-FR")["wipe protection"],
                         "protection en cas de wipe")
        self.assertEqual(select_jargon(glossary, "fr", "fr-FR"), {})
        self.assertNotIn("wipe protection", manual.get("exact", {}))
        self.assertNotIn("wipe protection", manual.get("jargon", {}))

    def test_no_unsafe_generic_wipe_override(self):
        glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        for unsafe in ("wipe", "wipes", "wipe the raid", "protection"):
            self.assertNotIn(unsafe, glossary["jargon"])


if __name__ == "__main__":
    unittest.main()
