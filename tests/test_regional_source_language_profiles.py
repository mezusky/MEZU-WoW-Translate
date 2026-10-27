"""Regional language evidence must not compete with its own base language.

Source-only Wowhead audit helpers; this does not validate Chrome detection,
DOM reconstruction, or the browser Translator API.
"""
import unittest

from scripts.source_language_evidence import (
    audit_source_prose,
    detect_source_language,
)


class RegionalLanguageEvidenceTests(unittest.TestCase):
    def test_base_and_regional_profiles_do_not_split_english_evidence(self):
        english = ["the", "and", "your", "you", "when", "should", "with",
                   "can", "have", "during", "before", "after"]
        french = ["les", "des", "pour", "avec", "votre", "vous"]
        profiles = {"en": english, "en-US": english, "fr_FR": french}
        # Independent tank/evoker-like prose; not a copied guide passage.
        prose = ("You should use your defensive spells when the group takes "
                 "damage, and you can cast them before the next phase. Your "
                 "cooldowns can help during the fight and you have to manage "
                 "your resources with the rest of the group.")
        result = detect_source_language([("p", prose)], profiles)
        self.assertEqual(result["detectedLanguage"], "en")
        self.assertEqual(result["status"], "strong_evidence")
        self.assertEqual(set(result["signalCounts"]), {"en", "fr"})

    def test_regional_only_profiles_and_underscore_aliases(self):
        profiles = {
            "en_US": ["your", "spells", "when", "you"],
            "fr-FR": ["vous", "votre", "avec", "pour"],
        }
        clean, english = audit_source_prose(
            "Use your spells when you can.", "en-US", profiles)
        self.assertEqual(clean, "Use your spells when you can.")
        self.assertTrue(english)
        _, french = audit_source_prose(
            "Vous pouvez jouer avec votre groupe pour avancer.", "fr_FR", profiles)
        self.assertTrue(french)
        with self.assertRaises(ValueError):
            audit_source_prose("Use your spells", "de-DE", profiles)

    def test_region_aliases_do_not_inflate_evidence(self):
        profiles = {
            "en": ["the", "and"],
            "en-US": ["the", "and"],
            "fr": ["les", "des"],
        }
        result = detect_source_language([("td", "the and " * 50)], profiles)
        self.assertIsNone(result["detectedLanguage"])
        self.assertEqual(result["distinctSignalCounts"]["en"], 2)
        self.assertEqual(set(result["signalCounts"]), {"en", "fr"})


if __name__ == "__main__":
    unittest.main()
