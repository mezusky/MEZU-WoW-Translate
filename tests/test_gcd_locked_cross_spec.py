"""Cross-spec GCD saturation terminology, sourced from independent Wowhead guides.

Source-index evidence is not browser-rendered French or a DOM audit.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class GcdLockedJargonTests(unittest.TestCase):
    def test_gcd_locked_is_not_a_cooldown_recharge(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        fr = select_jargon(glossary, "en-US", "fr-FR")
        self.assertEqual(fr["GCD-locked"], "sans GCD libre")
        self.assertEqual(fr["GCD locked"], "sans GCD libre")
        self.assertEqual(fr["GCD-locked specialization"], "spécialisation sans GCD libre")
        self.assertEqual(fr["GCD-locked spec"], "spé sans GCD libre")
        self.assertNotIn("locked", fr)
        self.assertNotIn("GCD", fr)

    def test_target_locale_isolated_and_no_legacy_duplication(self):
        glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
        self.assertEqual(select_jargon(glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(glossary, "en-US", "de-DE")
        manual = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))
        for phrase in ("GCD-locked", "GCD locked", "GCD-locked specialization", "GCD-locked spec"):
            self.assertNotIn(phrase, manual.get("exact", {}))
            self.assertNotIn(phrase, manual.get("jargon", {}))

    def test_independent_specs_and_sections_are_in_corpus(self):
        pages = {p["url"] for p in json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8")
        )["pages"]}
        for path in (
            "hunter/survival/dps-leveling-tips",
            "shaman/enhancement/basics",
            "monk/mistweaver/talent-builds-pve-healer",
        ):
            with self.subTest(path=path):
                self.assertIn("https://www.wowhead.com/guide/classes/" + path, pages)


if __name__ == "__main__":
    unittest.main()
