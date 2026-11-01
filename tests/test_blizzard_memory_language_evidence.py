"""Prevent official phrase memory from learning untranslated localized prose.

Source-only synthetic paraphrases of live Arcane Mage, Discipline Priest and
Protection Paladin guides. This does not reproduce the Chrome Translator API.
"""
import unittest

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

    def test_short_ambiguous_official_spell_text_remains_eligible(self):
        self.assertTrue(language_evidence_safe(
            "Cast Arcane Barrage after Arcane Surge.",
            "Lancez Barrage des Arcanes après Éruption arcanique."
        ))


if __name__ == "__main__":
    unittest.main()
