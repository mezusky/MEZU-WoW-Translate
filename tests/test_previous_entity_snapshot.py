"""A partial Blizzard refresh must never erase an unreadable prior snapshot."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.previous_entity_snapshot import load_previous_entities


class PreviousEntitySnapshotTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.pack = root / "datapack.json"
        self.manifest = root / "manifest.json"

    def write_pair(self, entities=None):
        if entities is None:
            entities = {"spell": {"123": {"en": "Shield Slam", "fr": "Heurt de bouclier"}},
                        "item": {"456": {"en": "Trinket", "fr": "Bijou"}}}
        counts = {kind: len(rows) for kind, rows in sorted(entities.items())}
        self.pack.write_text(json.dumps({
            "version": "abc", "sourceLanguage": "en", "targetLanguage": "fr",
            "entities": entities,
        }), encoding="utf-8")
        self.manifest.write_text(json.dumps({
            "version": "abc", "sourceLanguage": "en", "targetLanguage": "fr",
            "entity_count": sum(counts.values()),
            "entity_counts_by_kind": counts,
        }), encoding="utf-8")
        return entities

    def load(self, source="en", target="fr"):
        return load_previous_entities(self.pack, self.manifest, source, target)

    def test_clean_bootstrap_has_no_previous_snapshot(self):
        self.assertEqual(self.load(), {})

    def test_valid_snapshot_preserves_canonical_ids(self):
        self.assertEqual(self.load() if False else self.load_after_write(), self.entities)

    def load_after_write(self):
        self.entities = self.write_pair()
        return self.load()

    def test_missing_one_side_is_not_bootstrap(self):
        self.write_pair()
        self.manifest.unlink()
        with self.assertRaisesRegex(ValueError, "exist together"):
            self.load()

    def test_invalid_json_fails_closed(self):
        self.write_pair()
        self.pack.write_text('{"entities":', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "datapack.json"):
            self.load()

    def test_duplicate_ids_fail_closed(self):
        self.write_pair()
        self.pack.write_text(
            '{"version":"abc","sourceLanguage":"en","targetLanguage":"fr",'
            '"entities":{"spell":{"123":{},"123":{}}}}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            self.load()

    def test_mismatched_manifest_count_fails_closed(self):
        self.write_pair()
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        manifest["entity_count"] -= 1
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "entity count"):
            self.load()

    def test_mismatched_category_count_fails_closed(self):
        self.write_pair()
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        manifest["entity_counts_by_kind"]["spell"] = 0
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "category counts"):
            self.load()

    def test_mismatched_locale_pair_fails_closed(self):
        self.write_pair()
        with self.assertRaisesRegex(ValueError, "targetLanguage"):
            self.load(target="de")

    def test_mismatched_version_fails_closed(self):
        self.write_pair()
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        manifest["version"] = "different"
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "version"):
            self.load()


if __name__ == "__main__":
    unittest.main()
