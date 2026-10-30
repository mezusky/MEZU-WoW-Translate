"""Source-only regression for contextual cooldown instructions and talent coverage.

Indexed English Wowhead sources checked 2026-10-30:
- Blood Death Knight: "Keep cooldowns on cooldown"
- Arms Warrior: "Keep Abilities on cooldown"
- Unholy Death Knight: "Keep Abilities on Cooldown"
- Outlaw Rogue: "Using your cooldowns on cooldown"

These are *action* instructions, unlike "the spell is on cooldown" (unavailable).
No browser Translator API or DOM reconstruction is claimed.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class CooldownActionAndTalentMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.roles = json.loads((DATA / "wow_spec_roles.json").read_text(encoding="utf-8"))["roles"]
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_action_phrases_are_reusable_and_locale_scoped(self):
        jargon = select_jargon(self.player, "en-US", "fr-FR")
        expected = {
            "Keep cooldowns on cooldown": "Utiliser les CD dès qu’ils sont disponibles",
            "Keep Abilities on cooldown": "Utiliser les capacités dès qu’elles sont disponibles",
            "Keep Abilities on Cooldown": "Utiliser les capacités dès qu’elles sont disponibles",
            "Using your cooldowns on cooldown": "Utiliser vos CD dès qu’ils sont disponibles",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(jargon[source], target)
                self.assertNotIn(source, self.manual.get("jargon", {}))
                self.assertNotIn(source, self.manual.get("exact", {}))

    def test_no_ambiguous_cooldown_state_override(self):
        # "Cast on cooldown" means use when ready; "is on cooldown" means
        # currently unavailable. Never apply a context-free phrase replacement.
        jargon = select_jargon(self.player, "en", "fr")
        for unsafe in ("on cooldown", "On Cooldown", "off cooldown",
                       "is on cooldown", "cooldowns on cooldown"):
            with self.subTest(source=unsafe):
                self.assertNotIn(unsafe, jargon)
        self.assertEqual(select_jargon(self.player, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.player, "en", "de")

    def test_all_known_retail_specs_have_a_talent_build_source(self):
        urls = [p["url"] for p in self.pages]
        self.assertEqual(len(urls), len(set(urls)))
        for wow_class, specs in self.roles.items():
            for spec, role in specs.items():
                url = ("https://www.wowhead.com/guide/classes/"
                       f"{wow_class}/{spec}/talent-builds-pve-{role}")
                with self.subTest(wow_class=wow_class, spec=spec):
                    self.assertIn(url, urls)


if __name__ == "__main__":
    unittest.main()
