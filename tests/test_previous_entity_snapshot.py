"""A partial Blizzard refresh must never erase an unreadable prior snapshot."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.previous_entity_snapshot import load_previous_entities, stable_pack_version


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
        stable = {"sourceLanguage": "en", "targetLanguage": "fr",
                  "entities": entities, "exact": {"Always Be Casting": "Toujours caster"}}
        version = stable_pack_version(stable)
        self.pack.write_text(json.dumps({**stable, "version": version,
                                         "generated_at": "2026-11-01T00:00:00Z"}),
                             encoding="utf-8")
        self.manifest.write_text(json.dumps({
            "version": version, "sourceLanguage": "en", "targetLanguage": "fr",
            "entity_count": sum(counts.values()),
            "entity_counts_by_kind": counts,
        }), encoding="utf-8")
        return entities

    def load(self, source="en", target="fr"):
        return load_previous_entities(self.pack, self.manifest, source, target)

    def test_clean_bootstrap_has_no_previous_snapshot(self):
        self.assertEqual(self.load(), {})

    def test_valid_snapshot_preserves_canonical_ids(self):
        entities = self.write_pair()
        self.assertEqual(self.load(), entities)

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

    def test_changed_canonical_name_with_same_counts_fails_closed(self):
        self.write_pair()
        pack = json.loads(self.pack.read_text(encoding="utf-8"))
        pack["entities"]["spell"]["123"]["fr"] = "Nom corrompu"
        self.pack.write_text(json.dumps(pack), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "content checksum"):
            self.load()

    def test_changed_prose_layer_with_same_counts_fails_closed(self):
        self.write_pair()
        pack = json.loads(self.pack.read_text(encoding="utf-8"))
        pack["exact"]["Always Be Casting"] = "Traduction corrompue"
        self.pack.write_text(json.dumps(pack), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "content checksum"):
            self.load()

    def test_generation_timestamp_is_not_part_of_version(self):
        self.write_pair()
        pack = json.loads(self.pack.read_text(encoding="utf-8"))
        pack["generated_at"] = "2026-11-02T00:00:00Z"
        self.pack.write_text(json.dumps(pack), encoding="utf-8")
        self.assertEqual(self.load()["spell"]["123"]["fr"], "Heurt de bouclier")

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
