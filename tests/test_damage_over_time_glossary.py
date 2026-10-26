"""Cross-class DoT noun phrases from indexed English Wowhead sources.

Source-only fixtures: these are not observed Chrome Translator API output.
Keep the noun-phrase rules locale-scoped; bare verbal "damage over time"
must remain contextual and official linked spells must resolve by entity ID.
"""
import json
import re
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class DamageOverTimeGlossaryTests(unittest.TestCase):
    def test_noun_phrase_number_and_hyphenation(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        for term in ("damage over time effect", "damage-over-time effect"):
            self.assertEqual(jargon[term], "effet de dégâts sur la durée")
        for term in ("damage over time effects", "damage-over-time effects"):
            self.assertEqual(jargon[term], "effets de dégâts sur la durée")
        self.assertEqual(jargon["Damage over Time (DoT) effect"],
                         "effet de dégâts sur la durée (DoT)")
        self.assertNotIn("damage over time", jargon)
        self.assertNotIn("damage-over-time", jargon)

    def test_real_cross_class_english_source_fixtures(self):
        # Independent Feral/Rogue/Priest/Hunter/Mistweaver guide sources.
        # Do not treat the excerpts as translated Chrome output.
        fixtures = {
            "feral-druid-rotation": (
                "Feral's damage over time effects are generally the most efficient spells you can cast.",
                "damage over time effects"),
            "assassination-rogue-leveling": (
                "you will be relying heavily on damage over time effects to deal damage",
                "damage over time effects"),
            "shadow-priest-abilities": (
                "applies a Damage over Time (DoT) effect, dealing Shadow damage",
                "Damage over Time (DoT) effect"),
            "marksmanship-hunter-abilities": (
                "Black Arrow applies a damage over time effect",
                "damage over time effect"),
            "assassination-rogue-rotation": (
                "A 14-second damage-over-time effect which increases with every poison application",
                "damage-over-time effect"),
            "mistweaver-monk-raid": (
                "the raid may still be carrying damage-over-time effects from the bosses",
                "damage-over-time effects"),
        }
        ids = {page["id"] for page in PAGES}
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        for guide, (excerpt, term) in fixtures.items():
            with self.subTest(guide=guide):
                self.assertIn(guide, ids)
                self.assertIsNotNone(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", excerpt, re.I))
                self.assertIn(term, jargon)
                self.assertNotIn(term, MANUAL.get("exact", {}))
                self.assertNotIn(term, MANUAL.get("jargon", {}))

    def test_locale_isolation_and_no_broad_verbal_override(self):
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        for source, target in (("fr-FR", "en-US"), ("en-US", "de-DE")):
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    select_jargon(GLOSSARY, source, target)
        self.assertNotIn("damage over time", MANUAL.get("exact", {}))


if __name__ == "__main__":
    unittest.main()
