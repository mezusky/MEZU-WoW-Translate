"""Reusable absorb-shield wording across unrelated WoW roles (offline)."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class AbsorbShieldLocaleTests(unittest.TestCase):
    def test_shield_is_not_healing_absorb(self):
        glossary = load("data/mezu_player_glossary.json")
        self.assertEqual(glossary["sourceLanguage"], "en")
        self.assertEqual(glossary["targetLanguage"], "fr")
        terms = glossary["jargon"]
        self.assertEqual(terms["absorb shield"], "bouclier d’absorption")
        self.assertEqual(terms["absorb shields"], "boucliers d’absorption")
        self.assertEqual(terms["healing absorb"], "absorption de soins")
        self.assertNotIn("absorb", terms)
        self.assertNotIn("shield", terms)

    def test_no_legacy_duplicates(self):
        manual = load("data/manual_overrides.json")
        for phrase in ("absorb shield", "absorb shields"):
            for section in ("exact", "jargon"):
                self.assertNotIn(phrase, manual.get(section, {}))

    def test_cross_role_pages_in_corpus(self):
        urls = {page["url"] for page in load("data/wowhead_regression_pages.json")["pages"]}
        # Source evidence: Brewmaster, Mistweaver, Holy Paladin, Discipline Priest.
        for spec in (
            "monk/brewmaster",
            "monk/mistweaver",
            "paladin/holy",
            "priest/discipline",
        ):
            self.assertIn(
                "https://www.wowhead.com/guide/classes/"
                + spec + "/abilities-talents-pve-"
                + ("tank" if spec == "monk/brewmaster" else "healer"),
                urls,
            )


if __name__ == "__main__":
    unittest.main()
