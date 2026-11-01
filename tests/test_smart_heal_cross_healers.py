"""Cross-guide smart-heal terminology is locale-scoped, not an entity rename.

Indexed English evidence: Retail Restoration Shaman rotation (Chain Heal),
Retail Preservation Evoker abilities (not smart healing), and independent
Cataclysm Restoration Druid / WotLK Holy Priest guide excerpts.
Source-only: these tests do not claim browser Translator API verification.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]
PLAYER = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))


class SmartHealCrossHealerTests(unittest.TestCase):
    def test_singular_plural_and_mechanic_have_shared_meaning(self):
        jargon = select_jargon(PLAYER, "en-US", "fr-FR")
        self.assertEqual(jargon["smart heal"], "soin intelligent")
        self.assertEqual(jargon["smart heals"], "soins intelligents")
        self.assertEqual(jargon["smart healing"], "soins intelligents")

    def test_no_manual_exception_or_official_spell_rename(self):
        for term in ("smart heal", "smart heals", "smart healing"):
            self.assertNotIn(term, MANUAL.get("exact", {}))
            self.assertNotIn(term, MANUAL.get("jargon", {}))
        # "SmartHeal" may be an addon/product name, not this WoW mechanic.
        self.assertNotIn("SmartHeal", PLAYER["jargon"])
        self.assertNotIn("smart", PLAYER["jargon"])

    def test_isolated_from_other_translation_directions(self):
        self.assertEqual(select_jargon(PLAYER, "fr", "fr"), {})
        for source, target in (("de", "fr"), ("en", "de"), ("fr", "en")):
            with self.subTest(source=source, target=target):
                with self.assertRaises(ValueError):
                    select_jargon(PLAYER, source, target)

    def test_unrelated_retail_healer_sources_already_in_corpus(self):
        pages = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]
        urls = {page["url"] for page in pages}
        self.assertIn(
            "https://www.wowhead.com/guide/classes/shaman/restoration/rotation-cooldowns-pve-healer", urls)
        self.assertIn(
            "https://www.wowhead.com/guide/classes/evoker/preservation/abilities-talents-pve-healer", urls)


if __name__ == "__main__":
    unittest.main()
