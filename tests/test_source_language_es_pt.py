"""Data-only Spanish/Portuguese source evidence, with English-prose safeguards.

Wowhead localized URLs can still contain English prose and localized spell/item
names. These tests validate only the source audit heuristic, not Chrome or MEZU
translation output. No locale is inferred from a URL path.
"""
import json
import unittest
from pathlib import Path

from scripts.source_language_evidence import detect_source_language

DATA = Path(__file__).resolve().parents[1] / "data"
PROFILES = json.loads((DATA / "audit_language_signals.json").read_text(
    encoding="utf-8"))["profiles"]


class ExtendedLanguageEvidenceTests(unittest.TestCase):
    def test_spanish_guide_prose(self):
        prose = (
            "Para mejorar tu personaje, debes usar tus habilidades cuando los "
            "enemigos están cerca. Puedes elegir talentos para aumentar el daño "
            "y ayudar a tu grupo durante el combate. También es importante "
            "mantener tus hechizos activos antes de utilizar otras habilidades "
            "y después de cada encuentro."
        )
        self.assertEqual(detect_source_language([("p", prose)], PROFILES)
                         ["detectedLanguage"], "es")

    def test_portuguese_guide_prose(self):
        prose = (
            "Quando você joga com seu personagem, pode usar suas habilidades "
            "para ajudar o grupo durante o combate. Também deve manter seus "
            "feitiços ativos enquanto os inimigos estão próximos, antes de "
            "escolher outros talentos e depois de cada encontro. Isso melhora "
            "o dano e a cura dos aliados."
        )
        self.assertEqual(detect_source_language([("p", prose)], PROFILES)
                         ["detectedLanguage"], "pt")

    def test_english_prose_with_french_official_item_names(self):
        # Protection Warrior consumables: a /fr page localizes item names but
        # can leave explanatory prose in English. URL locale is not source.
        prose = (
            "Consumables are important for your character when you are "
            "preparing for a dungeon or raid. You should use Flacon des "
            "chevaliers de sang and Huile de phénix thalassienne with your "
            "other spells and abilities, and you can choose more equipment "
            "when your group needs additional damage."
        )
        result = detect_source_language([("p", prose)], PROFILES)
        self.assertEqual(result["detectedLanguage"], "en")

    def test_short_localized_names_are_not_prose_evidence(self):
        for name in ("Déluge de lames", "Cercle démoniaque",
                     "Metamorfose do Caos", "Enfoque certero"):
            with self.subTest(name=name):
                result = detect_source_language([("td", name)], PROFILES)
                self.assertIsNone(result["detectedLanguage"])
                self.assertEqual(result["status"], "insufficient_prose")


if __name__ == "__main__":
    unittest.main()
