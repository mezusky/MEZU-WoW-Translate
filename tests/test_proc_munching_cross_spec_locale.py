"""Source-only cross-spec contract for proc-munching jargon.

Balance Druid rotation (2026) warns about munching a Touch the Cosmos proc;
Fire Mage FAQ uses "munch" the proc for simultaneous Flamestrikes.
A Frost Mage retrospective independently names "Proc Munching".
Do not treat indexed source excerpts as proof of browser translation.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

DATA = Path(__file__).resolve().parents[1] / "data"


class ProcMunchingLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((DATA / "mezu_player_glossary.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((DATA / "manual_overrides.json").read_text(encoding="utf-8"))
        cls.pages = json.loads((DATA / "wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]

    def test_idiom_is_reusable_and_avoids_unsafe_generic_verb(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["proc munching"], "gaspillage de procs")
        self.assertEqual(terms["Proc Munching"], "Gaspillage de procs")
        self.assertEqual(terms["munch the proc"], "gaspiller le proc")
        for unsafe in ("munch", "munching", "munches"):
            self.assertNotIn(unsafe, terms)
        for term in ("proc munching", "Proc Munching", "munch the proc"):
            self.assertNotIn(term, self.manual.get("jargon", {}))
            self.assertNotIn(term, self.manual.get("exact", {}))

    def test_locale_isolation(self):
        self.assertEqual(select_jargon(self.glossary, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en-US", "de-DE")

    def test_independent_rotation_guides_remain_in_corpus(self):
        urls = {page["url"] for page in self.pages}
        for spec in ("druid/balance", "mage/fire", "mage/frost"):
            with self.subTest(spec=spec):
                self.assertIn(
                    "https://www.wowhead.com/guide/classes/" + spec + "/rotation-cooldowns-pve-dps",
                    urls,
                )


if __name__ == "__main__":
    unittest.main()
