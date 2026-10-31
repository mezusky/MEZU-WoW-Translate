"""Source-only regression: Wowhead URL locale is not the guide prose language.

Real /fr/ and /es/ class guides keep English prose while localizing linked
Blizzard abilities. These short synthetic paraphrases model that structure,
not a Chrome translation result or a complete live HTML audit.
"""
import json
import unittest
from pathlib import Path

from scripts.source_language_evidence import detect_source_language
from scripts.locale_glossary import same_base_language, select_jargon

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / "data" / "audit_language_signals.json").read_text(
    encoding="utf-8"))["profiles"]
GLOSSARY = json.loads((ROOT / "data" / "mezu_player_glossary.json").read_text(
    encoding="utf-8"))


class LocalizedWowheadProseEvidenceTests(unittest.TestCase):
    def test_french_url_with_english_evoker_prose(self):
        # /fr/guide/classes/evoker/preservation/overview-pve-healer
        blocks = [
            ("h1", "Guide Évocateur Préservation"),
            ("p", "Your healing abilities work together when you prepare for "
             "damage. You can cast Souffle onirique and Écho before the group "
             "takes damage, then use your other spells to help them recover."),
            ("li", "When your allies need more healing, you should use "
             "Arbre d’émeraude with your other spells. This guide explains "
             "how to plan your casts during a difficult fight."),
        ]
        self.assertEqual(detect_source_language(blocks, PROFILES)
                         ["detectedLanguage"], "en")

    def test_spanish_url_with_english_devourer_prose(self):
        # /es/guide/classes/demon-hunter/devourer/overview-pve-dps
        blocks = [
            ("h1", "Devourer Demon Hunter"),
            ("p", "You can generate resources with Consumir and spend them "
             "with Rayo de Vacío. When you have enough resources, use "
             "Metamorfosis del Vacío for your stronger damage abilities."),
            ("p", "This guide shows how your spells work together, and "
             "which abilities you should use before and during a fight "
             "to improve your damage without wasting resources."),
        ]
        self.assertEqual(detect_source_language(blocks, PROFILES)
                         ["detectedLanguage"], "en")

    def test_detection_is_evidence_not_a_translation_instruction(self):
        self.assertTrue(same_base_language("en-US", "en-GB"))
        self.assertEqual(select_jargon(GLOSSARY, "en-US", "en-GB"), {})
        self.assertFalse(same_base_language("en-US", "fr-FR"))
        self.assertIn("pool charges", select_jargon(GLOSSARY, "en-US", "fr-FR"))


if __name__ == "__main__":
    unittest.main()
