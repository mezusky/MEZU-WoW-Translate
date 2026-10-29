"""Reusable macro-guide targeting terminology across independent specs.

Source evidence: Restoration Shaman, Discipline Priest, Demonology Warlock
and Frost DK UI/Macros Wowhead guides (Oct 2026). Source-only evidence:
this does not validate browser Translator API or DOM reconstruction.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon
from scripts.source_language_evidence import clean_non_prose

ROOT = Path(__file__).resolve().parents[1]
PLAYER = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class ReticleCrossClassTests(unittest.TestCase):
    def test_short_reusable_phrases_not_whole_sentence_overrides(self):
        expected = {
            "targeting reticle": "réticule de ciblage",
            "reticle based abilities": "capacités à ciblage au sol",
        }
        terms = select_jargon(PLAYER, "en-US", "fr-FR")
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(terms[source], target)
                self.assertNotIn(source, MANUAL.get("exact", {}))
                self.assertNotIn(source, MANUAL.get("jargon", {}))
        # Never globally replace 'target', 'cast', 'cursor', or the game macro syntax.
        for unsafe in ("reticle", "target", "cursor", "@cursor", "/cast", "cast"):
            self.assertNotIn(unsafe, terms)

    def test_cross_class_heldouts_are_unique(self):
        by_id = {p["id"]: p["url"] for p in PAGES}
        for page_id, suffix in (
            ("frost-death-knight-ui-macros-heldout", "/death-knight/frost/addons-macro-ui-imports"),
            ("demonology-warlock-ui-macros-heldout", "/warlock/demonology/addons-macro-ui-imports"),
            ("assassination-rogue-ui-macros-heldout", "/rogue/assassination/addons-macro-ui-imports"),
            ("restoration-shaman-ui-macros", "/shaman/restoration/addons-macro-ui-imports"),
            ("discipline-priest-ui-macros", "/priest/discipline/addons-macro-ui-imports"),
        ):
            with self.subTest(page=page_id):
                self.assertEqual(by_id[page_id], "https://www.wowhead.com/guide/classes" + suffix)
        self.assertEqual(len(PAGES), len({p["id"] for p in PAGES}))
        self.assertEqual(len(PAGES), len({p["url"] for p in PAGES}))

    def test_macro_commands_stay_out_of_source_prose(self):
        source = (
            "Use the targeting reticle to place the spell.\n"
            "#showtooltip Soulstone\n"
            "/cast [target=mouseover,exists] [] Soulstone\n"
            "Reticle based abilities can also be cast at your cursor.\n"
            "#showtooltip\n"
            "/cast [@cursor] Shadowfury"
        )
        clean = clean_non_prose(source)
        self.assertIn("targeting reticle", clean)
        self.assertIn("Reticle based abilities", clean)
        self.assertNotIn("#showtooltip", clean)
        self.assertNotIn("/cast", clean)
        self.assertNotIn("target=mouseover", clean)

    def test_locale_isolation(self):
        self.assertEqual(select_jargon(PLAYER, "en", "fr")["targeting reticle"],
                         "réticule de ciblage")
        self.assertEqual(select_jargon(PLAYER, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(PLAYER, "de", "fr")


if __name__ == "__main__":
    unittest.main()
