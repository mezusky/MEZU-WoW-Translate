"""Protect player jargon shared by independent retail guides.

English source evidence: Feral Druid Midnight rotation (snapshotting, snapshot
strength, Pooling), Assassination Rogue Midnight rotation (Pooling), and
Affliction Warlock MoP Classic rotation (snapshotting). The historical guide
is only corroborating terminology, not a claim about retail mechanics.
No Chrome Translator API or DOM output is exercised here.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from locale_glossary import select_jargon

GLOSSARY = json.loads((ROOT / "data/mezu_player_glossary.json").read_text(encoding="utf-8"))
MANUAL = json.loads((ROOT / "data/manual_overrides.json").read_text(encoding="utf-8"))


class SnapshotPoolingCrossClassTests(unittest.TestCase):
    def test_reusable_terms_keep_wow_meaning_without_sentence_overrides(self):
        expected = {
            "snapshotting": "snapshotting",
            "Snapshotting": "Snapshotting",
            "snapshot strength": "puissance du snapshot",
            "pooling": "pooling",
            "Pooling": "Pooling",
        }
        for source, target in expected.items():
            with self.subTest(source=source):
                self.assertEqual(GLOSSARY["jargon"][source], target)
                self.assertNotIn(source, MANUAL.get("jargon", {}))
                self.assertNotIn(source, MANUAL.get("exact", {}))

    def test_do_not_generalize_ambiguous_words(self):
        # A generic snapshot can be a UI screenshot, and a pool can be a
        # ground effect. These are not always rotation mechanics.
        for source in ("snapshot", "Snapshot", "pool", "Pool",
                       "snapshots", "pooling resources", "pooling Chi"):
            with self.subTest(source=source):
                self.assertNotIn(source, GLOSSARY["jargon"])

    def test_locale_isolation_and_no_translation_same_language(self):
        terms = select_jargon(GLOSSARY, "en-US", "fr-FR")
        self.assertEqual(terms["snapshot strength"], "puissance du snapshot")
        self.assertEqual(terms["pooling"], "pooling")
        self.assertEqual(select_jargon(GLOSSARY, "fr-FR", "fr-CA"), {})
        with self.assertRaises(ValueError):
            select_jargon(GLOSSARY, "en", "es")


if __name__ == "__main__":
    unittest.main()
