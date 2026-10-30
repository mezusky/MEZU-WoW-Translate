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

    def test_raidwide_effect_terms_are_shared_across_roles(self):
        # Preservation Evoker and Restoration Druid describe raidwide
        # damage; Havoc Demon Hunter describes a raidwide DoT.
        # These are prose patterns, not spell/entity name replacements.
        jargon = GLOSSARY["jargon"]
        # Independent Preservation Evoker, Restoration Shaman and Holy/Discipline
        # Priest raid guides use unhyphenated, hyphenated and spaced spellings.
        for spelling in ("raidwide damage", "raid-wide damage", "raid wide damage"):
            with self.subTest(spelling=spelling):
                self.assertEqual(jargon[spelling], "dégâts sur tout le raid")
        self.assertEqual(jargon["raidwide DoT"], "DoT sur tout le raid")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for phrase in ("raidwide damage", "raid-wide damage", "raid wide damage", "raidwide DoT"):
            self.assertNotIn(phrase, manual.get("jargon", {}))
            self.assertNotIn(phrase, manual.get("exact", {}))

    def test_simulation_jargon_is_locale_scoped_across_roles(self):
        # Frost Mage stats, Discipline Priest stats and Enhancement Shaman
        # consumables all use sim/simming; this is player jargon, not a
        # Blizzard spell/entity name or a page-specific sentence override.
        jargon = GLOSSARY["jargon"]
        # Avoid a broad fragment that breaks French grammar inside prose.
        self.assertNotIn("sim your character", jargon)
        self.assertEqual(jargon["Simulate Your Character Now"],
                         "Simulez votre personnage dès maintenant")
        self.assertEqual(jargon["simming"], "sim")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for phrase in ("Simulate Your Character Now", "simming"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, manual.get("jargon", {}))
                self.assertNotIn(phrase, manual.get("exact", {}))

    def test_filler_terms_are_locale_scoped_across_dps_specs(self):
        # Frost DK basics and Elemental Shaman rotation use "filler" in
        # different resource systems; the phrase is WoW jargon, not a spell.
        # The same terms must not leak into other target-language packs.
        jargon = GLOSSARY["jargon"]
        for source, target in {
            "filler": "filler",
            "filler spell": "sort filler",
            "filler spells": "sorts filler",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for source in ("filler", "filler spell", "filler spells"):
            self.assertNotIn(source, manual.get("jargon", {}))
            self.assertNotIn(source, manual.get("exact", {}))
        self.assertNotIn("filling", jargon)

    def test_raid_intermission_phrases_generalize_without_broad_override(self):
        # Fury Warrior, Frost Mage and Holy Priest raid guides independently
        # use this raid phase vocabulary; the generic noun is intentionally
        # left to the prose translator outside these exact constructions.
        jargon = GLOSSARY["jargon"]
        expected = {
            "During the intermission,": "Pendant l’interphase,",
            "during the intermission,": "pendant l’interphase,",
            "In the intermission,": "Pendant l’interphase,",
        }
        for source, target in expected.items():
            self.assertEqual(jargon[source], target)
        # No unpunctuated prefix: "In the intermission part" must remain
        # available to the prose translator, not become "interphase part".
        for phrase in ("intermission", "In the intermission",
                       "During the intermission"):
            self.assertNotIn(phrase, jargon)
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for phrase in expected:
            self.assertNotIn(phrase, manual.get("jargon", {}))
            self.assertNotIn(phrase, manual.get("exact", {}))

    def test_pull_timing_is_contextual_across_unrelated_rotations(self):
        # BM Hunter: "Before pull," and "As pull starts,"; Fire Mage:
        # "before the pull" and "on the pull". Protection Paladin also
        # uses pull timing, but a bare "on pull" rule could corrupt
        # phrases such as "on pull timer". Never translate bare "pull".
        jargon = GLOSSARY["jargon"]
        expected = {
            "Before pull,": "Avant le pull,",
            "As pull starts,": "Au pull,",
            "before the pull": "avant le pull",
            "on the pull": "au pull",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
        for broad in ("pull", "on pull", "pull timer"):
            self.assertNotIn(broad, jargon)
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for phrase in expected:
            self.assertNotIn(phrase, manual.get("jargon", {}))
            self.assertNotIn(phrase, manual.get("exact", {}))

    def test_locale_glossary_has_no_duplicate_legacy_jargon(self):
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        player_keys = {term.casefold() for term in GLOSSARY["jargon"]}
        # Both legacy layers feed the published pack. A duplicate in exact
        # can silently bypass the intended single-source locale glossary,
        # even when the legacy jargon layer is clean.
        for layer in ("jargon", "exact"):
            with self.subTest(layer=layer):
                legacy_keys = {term.casefold() for term in manual.get(layer, {})}
                overlapping = player_keys & legacy_keys
                self.assertEqual(overlapping, set(),
                                 "Move overlapping terms to one locale-scoped source")
        self.assertEqual(GLOSSARY["jargon"]["finishing move"], "coup de grâce")
        self.assertEqual(GLOSSARY["jargon"]["Combo Points"], "points de combo")


    def test_rotation_assistant_editorial_aliases_share_official_ui_name(self):
        # Brewmaster starter prose says "One-Button Rotation Assistant";
        # Holy Priest and Devourer starter headings use "Single Button
        # Rotation Assistant". Blizzard calls the feature Single-Button
        # Assistant. All three refer to the same UI concept.
        jargon = GLOSSARY["jargon"]
        for source in (
            "Single-Button Assistant",
            "One-Button Rotation Assistant",
            "Single Button Rotation Assistant",
        ):
            with self.subTest(source=source):
                self.assertEqual(jargon[source], "Assistant à bouton unique")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for source in ("One-Button Rotation Assistant",
                       "Single Button Rotation Assistant"):
            self.assertNotIn(source, manual.get("jargon", {}))
            self.assertNotIn(source, manual.get("exact", {}))

    def test_resource_caps_and_priority_lists_are_shared_not_manual(self):
        # Havoc DH and Destruction Warlock rotations use resource overcapping;
        # Protection Warrior, Destruction Warlock and Discipline Priest share
        # priority-list wording. Keep all four in one locale-specific layer.
        jargon = GLOSSARY["jargon"]
        expected = {
            "overcap": "overcap",
            "overcapping": "overcap",
            "priority list": "liste de priorités",
            "priority lists": "listes de priorités",
        }
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, manual.get("jargon", {}))
                self.assertNotIn(source, manual.get("exact", {}))
        self.assertNotIn("cap", jargon)  # Ambiguous outside resource context.


    def test_buff_uptime_is_shared_across_specs_without_entity_overrides(self):
        # Augmentation Evoker basics/rotation, Vengeance DH overview and
        # Balance Druid rotation all discuss buff uptime. The heading
        # "Keep your buffs up" is editorial prose, not a spell name.
        jargon = GLOSSARY["jargon"]
        expected = {
            "buff uptime": "uptime des buffs",
            "Keep your buffs up": "Gardez vos buffs actifs",
            "keep your buffs up": "gardez vos buffs actifs",
        }
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, manual.get("jargon", {}))
                self.assertNotIn(source, manual.get("exact", {}))
        # Bare "uptime" already has a legacy player-jargon meaning.
        # Never override it with a buff-specific phrase in all contexts.
        self.assertNotIn("uptime", jargon)
        self.assertEqual(manual["jargon"]["uptime"], "uptime")


if __name__ == "__main__":
    unittest.main()
