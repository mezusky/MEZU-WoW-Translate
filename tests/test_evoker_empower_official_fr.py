"""Official Evoker Empower terminology stays locale-scoped and unambiguous.

Source evidence: Midnight Evoker Augmentation, Devastation, Preservation
ability/rotation guides. Blizzard's French Evoker class page uses "sorts
renforcés". Fire Mage uses ordinary "empowered spells" for different
effects, so do not turn the generic adjective or verb into a global rule.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))


class EvokerEmpowerTerminologyTests(unittest.TestCase):
    def test_official_evoker_noun_phrase_is_reusable_across_three_specs(self):
        self.assertEqual(GLOSSARY["sourceLanguage"], "en")
        self.assertEqual(GLOSSARY["targetLanguage"], "fr")
        for source, target in {
            "Empower spell": "sort renforcé",
            "Empower spells": "sorts renforcés",
            "Empower Spell": "Sort renforcé",
            "Empower Spells": "Sorts renforcés",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("exact", {}))
                self.assertNotIn(source, MANUAL.get("jargon", {}))

    def test_do_not_overtranslate_generic_empower_language(self):
        # Mage and other classes can have empowered spells without using
        # the Evoker's specific charged Empower spell mechanic.
        for source in ("Empower", "empower", "Empowered", "empowered",
                       "empowered spells", "Empowered spells",
                       "Empowered casts", "Empower abilities"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])


if __name__ == "__main__":
    unittest.main()
