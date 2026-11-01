"""Prevent official phrase memory from learning untranslated localized prose.

Source-only synthetic paraphrases of live Arcane Mage, Discipline Priest and
Protection Paladin guides. This does not reproduce the Chrome Translator API.
"""
import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.build_blizzard_memory import good_pair, language_evidence_safe


ARCANE_EN = (
    "You should use your Arcane Charges when you have enough resources for "
    "the next burst window. This guide explains how to use your spells "
    "and abilities before the fight, and when you can cast other cooldowns."
)
ARCANE_FR = (
    "Vous pouvez utiliser vos charges arcaniques lorsque vous avez assez de "
    "ressources pour la prochaine phase de dégâts. Cette section explique "
    "comment utiliser vos sorts et vos capacités avant le combat, ainsi "
    "que les autres actions que vous pouvez faire."
)
ARCANE_FALLBACK = (
    "You should use your charges arcaniques when you have enough resources "
    "for the next burst window. This guide explains how to use your spells "
    "and abilities before the fight, and when you can cast other cooldowns."
)

DISC_EN = (
    "When your allies take damage, you should prepare Atonement before "
    "the next raid mechanic. You can use your other spells to help the "
    "group while you plan the timing of your healing cooldowns."
)
DISC_FALLBACK = (
    "When your allies take damage, you should prepare Expiation before "
    "the next raid mechanic. You can use your other spells to help the "
    "group while you plan the timing of your healing cooldowns."
)

PALADIN_FR = (
    "Vous pouvez utiliser vos sorts lorsque les ennemis attaquent votre "
    "groupe. Cette capacité vous aide à protéger les autres joueurs "
    "pendant le combat, et vous pouvez aussi utiliser vos capacités "
    "défensives avant les dégâts pour survivre."
)


class BlizzardMemoryLanguageEvidenceTests(unittest.TestCase):
    def test_arcane_target_fallback_is_not_official_french_memory(self):
        self.assertFalse(language_evidence_safe(ARCANE_EN, ARCANE_FALLBACK))
        self.assertFalse(good_pair(ARCANE_EN, ARCANE_FALLBACK, 8.0))
        self.assertTrue(language_evidence_safe(ARCANE_EN, ARCANE_FR))

    def test_independent_healer_fallback_is_rejected(self):
        self.assertFalse(language_evidence_safe(DISC_EN, DISC_FALLBACK))

    def test_multilingual_direction_is_not_hardcoded(self):
        self.assertTrue(language_evidence_safe(PALADIN_FR, ARCANE_EN,
                                              "fr-FR", "en-US"))
        self.assertFalse(language_evidence_safe(PALADIN_FR, ARCANE_EN,
                                               "fr-FR", "de-DE"))

    def test_legacy_fallback_is_removed_during_memory_retention(self):
        merger = Path(__file__).resolve().parents[1] / "scripts" / "preserve_blizzard_memory.py"
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder) / "old.json"
            new = Path(folder) / "new.json"
            old.write_text(json.dumps({
                "sourceLanguage": "en-US", "targetLanguage": "fr-FR",
                "exact": {DISC_EN: DISC_FALLBACK, ARCANE_EN: ARCANE_FR},
            }), encoding="utf-8")
            new.write_text(json.dumps({
                "sourceLanguage": "en-US", "targetLanguage": "fr-FR", "exact": {},
            }), encoding="utf-8")
            result = subprocess.run([sys.executable, str(merger), str(old), str(new)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            retained = json.loads(new.read_text(encoding="utf-8"))["exact"]
            self.assertNotIn(DISC_EN, retained)
            self.assertEqual(retained[ARCANE_EN], ARCANE_FR)

    def test_short_ambiguous_official_spell_text_remains_eligible(self):
        self.assertTrue(language_evidence_safe(
            "Cast Arcane Barrage after Arcane Surge.",
            "Lancez Barrage des Arcanes après Éruption arcanique."
        ))


if __name__ == "__main__":
    unittest.main()
