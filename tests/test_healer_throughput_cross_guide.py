"""Source-grounded EN->FR healer throughput terminology across unrelated guides.

Sources: Restoration Shaman M+ (high healing output) and Season 2 healer
raid rankings (healing throughput). Unqualified 'throughput' stays unforced. This checks the locale-scoped Data Pack input only;
it does not claim to reproduce Chrome Translator or DOM behavior.
"""
import json
import unittest
from pathlib import Path

from scripts.locale_glossary import select_jargon

GLOSSARY = json.loads(
    (Path(__file__).resolve().parents[1] / "data/mezu_player_glossary.json")
    .read_text(encoding="utf-8")
)


class HealerThroughputCrossGuideTests(unittest.TestCase):
    def test_reusable_healing_terms_not_whole_sentence_overrides(self):
        jargon = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(jargon["healing output"], "volume de soins")
        self.assertEqual(jargon["healing throughput"], "volume de soins")
        self.assertNotIn("high throughput", jargon)
        self.assertNotIn("throughput", jargon)

    def test_unrelated_healer_prose_shares_terminology(self):
        # Source excerpts are deliberately short, not copied guide blocks.
        samples = (
            ("shaman-restoration", "High healing output"),
            ("raid-healer-rankings", "healing throughput"),
        )
        jargon = select_jargon(GLOSSARY, "en", "fr")
        for spec, text in samples:
            with self.subTest(spec=spec):
                self.assertTrue(any(term in text.casefold() for term in (
                    "healing output", "healing throughput",
                )))
                self.assertEqual(jargon["healing output" if "output" in text.casefold() else "healing throughput"], "volume de soins")

    def test_french_rules_do_not_leak_into_other_targets_or_skip_pair(self):
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "de-DE")


if __name__ == "__main__":
    unittest.main()
