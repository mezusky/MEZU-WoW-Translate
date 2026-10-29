"""Official Runic Power resource wording across Blood, Frost and Unholy DK.

Blizzard's French Death Knight class page labels the resource
"Puissance Runique". Source-only tests do not prove browser rendering.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

ROOT = Path(__file__).resolve().parents[1]


class RunicPowerOfficialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(
            encoding="utf-8"))
        cls.pages = {entry["url"] for entry in json.loads(
            (ROOT / "data/wowhead_regression_pages.json").read_text(
                encoding="utf-8"))["pages"]}
        cls.manual = json.loads((ROOT / "data/manual_overrides.json").read_text(
            encoding="utf-8"))

    def test_official_resource_name_is_locale_scoped(self):
        terms = select_jargon(self.glossary, "en-US", "fr-FR")
        self.assertEqual(terms["Runic Power"], "Puissance runique")
        self.assertEqual(terms["runic power"], "puissance runique")
        self.assertNotIn("Power", terms)
        self.assertNotIn("power", terms)
        for term in ("Runic Power", "runic power"):
            self.assertNotIn(term, self.manual.get("exact", {}))
            self.assertNotIn(term, self.manual.get("jargon", {}))
        self.assertEqual(select_jargon(self.glossary, "fr", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(self.glossary, "en", "de")

    def test_three_independent_dk_specs_have_regression_pages(self):
        for spec, role in (("blood", "tank"), ("frost", "dps"),
                           ("unholy", "dps")):
            with self.subTest(spec=spec):
                url = ("https://www.wowhead.com/guide/classes/death-knight/"
                       + spec + "/abilities-talents-pve-" + role)
                self.assertIn(url, self.pages)


if __name__ == "__main__":
    unittest.main()
