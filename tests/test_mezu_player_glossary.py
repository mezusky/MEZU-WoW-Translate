"""Offline contract tests for locale-specific, reusable player terminology."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))


class PlayerGlossaryTests(unittest.TestCase):
    def test_locale_is_explicit(self):
        self.assertEqual(GLOSSARY["sourceLanguage"], "en")
        self.assertEqual(GLOSSARY["targetLanguage"], "fr")
        self.assertNotEqual(GLOSSARY["sourceLanguage"], GLOSSARY["targetLanguage"])

    def test_jargon_entries_are_valid(self):
        jargon = GLOSSARY["jargon"]
        self.assertIsInstance(jargon, dict)
        for source, target in jargon.items():
            with self.subTest(source=source):
                self.assertIsInstance(source, str)
                self.assertIsInstance(target, str)
                self.assertTrue(source.strip())
                self.assertTrue(target.strip())

    def test_tier_terms_generalize_across_labels(self):
        jargon = GLOSSARY["jargon"]
        for source, target in {
            "tier set": "set de classe",
            "tier sets": "sets de classe",
            "set bonus": "bonus de set",
            "set bonuses": "bonus de set",
            "2-Set Bonus": "Bonus 2 pièces",
            "4-Set Bonus": "Bonus 4 pièces",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)


    def test_offpiece_variants_share_one_locale_specific_translation(self):
        # Seen across Preservation Evoker and unrelated Rogue/Monk gear guides.
        jargon = GLOSSARY["jargon"]
        for source in ("off-piece", "offpiece", "off piece"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "pièce hors set")
        for source in ("off-pieces", "offpieces", "off pieces"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "pièces hors set")


    def test_stat_threshold_terms_generalize_across_specs(self):
        # Blood DK, Arcane Mage and Brewmaster guides use the same stat section.
        jargon = GLOSSARY["jargon"]
        self.assertEqual(jargon["diminishing returns"], "rendements décroissants")
        self.assertEqual(jargon["diminishing return"], "rendement décroissant")
        self.assertEqual(jargon["breakpoint"], "seuil")
        self.assertEqual(jargon["breakpoints"], "seuils")


    def test_crafting_terms_shared_across_unrelated_specs(self):
        # Rogue gearing guides use sequence wording; Blizzard's profession
        # Crafting Orders system has a distinct official French name.
        jargon = GLOSSARY["jargon"]
        # "Crafting Orders" is a profession UI system ("commandes d'artisanat"),
        # while "recommended crafting order" means a sequence of gear crafts.
        # A bare phrase rule would silently conflate these unrelated concepts.
        self.assertNotIn("crafting order", jargon)
        self.assertEqual(jargon["recommended crafting order"],
                         "ordre de fabrication recommandé")
        self.assertEqual(jargon["Recommended Crafting Order"],
                         "Ordre de fabrication recommandé")
        for spelling in ("off-hand", "offhand"):
            with self.subTest(spelling=spelling):
                self.assertEqual(jargon[spelling], "main gauche")
        for spelling in ("off-hands", "offhands"):
            with self.subTest(spelling=spelling):
                self.assertEqual(jargon[spelling], "mains gauches")
        self.assertEqual(jargon["embellishment"], "embellissement")
        self.assertEqual(jargon["embellishments"], "embellissements")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        self.assertNotIn("crafting order", manual.get("exact", {}))
        # "off-piece" means non-set armor, not an off-hand weapon.
        self.assertEqual(jargon["off-piece"], "pièce hors set")


    def test_active_trinket_jargon_generalizes_across_caster_specs(self):
        # Shadow Priest and Affliction/Demonology Warlock opener guides use
        # both hyphenated and spaced variants; not every trinket is activable.
        jargon = GLOSSARY["jargon"]
        for source in ("on-use trinket", "on use trinket"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "bijou activable")
        for source in ("on-use trinkets", "on use trinkets"):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "bijoux activables")
        self.assertEqual(jargon["On-use Trinket"], "Bijou activable")
        self.assertEqual(jargon["trinket"], "bijou")

    def test_hyphenated_caster_movement_term_is_protected(self):
        # Arcane Mage uses "Stutter Stepping"; Elemental Shaman raid tips
        # use "stutter-stepping". Neither is a spell or item entity.
        jargon = GLOSSARY["jargon"]
        self.assertEqual(jargon["stutter-stepping"], "stutter-stepping")
        self.assertEqual(jargon["Stutter-Stepping"], "Stutter-Stepping")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        self.assertEqual(manual["jargon"]["stutter stepping"], "stutter stepping")
        self.assertNotIn("stutter-stepping", manual["jargon"])

    def test_always_be_casting_is_idiomatic_across_caster_guides(self):
        # Current Balance Druid and Elemental Shaman guides use the same
        # heading; Fire Mage and Discipline Priest also use the phrase.
        # Keep the player-facing verb "caster", not "être en train de cast".
        jargon = GLOSSARY["jargon"]
        self.assertEqual(jargon["Always Be Casting"], "Toujours caster")
        self.assertEqual(jargon["Always be casting"], "Toujours caster")
        self.assertEqual(jargon["always be casting"], "toujours caster")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for spelling in ("Always Be Casting", "Always be casting", "always be casting"):
            self.assertNotIn(spelling, manual.get("jargon", {}))

    def test_react_to_procs_generalizes_across_dps_specs(self):
        # Seen in Elemental Shaman, Affliction Warlock, Marksmanship Hunter
        # and Outlaw Rogue; preserve the familiar WoW term "proc".
        jargon = GLOSSARY["jargon"]
        self.assertEqual(jargon["React to procs"], "Réagir aux procs")
        self.assertEqual(jargon["React to Procs"], "Réagir aux procs")
        self.assertEqual(jargon["react to procs"], "réagir aux procs")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for spelling in ("React to procs", "React to Procs", "react to procs"):
            self.assertNotIn(spelling, manual.get("jargon", {}))
            self.assertNotIn(spelling, manual.get("exact", {}))

    def test_locale_glossary_has_no_duplicate_legacy_jargon(self):
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        overlapping = set(GLOSSARY["jargon"]) & set(manual.get("jargon", {}))
        self.assertEqual(overlapping, set(), "Move terms to one locale-scoped source")


if __name__ == "__main__":
    unittest.main()
