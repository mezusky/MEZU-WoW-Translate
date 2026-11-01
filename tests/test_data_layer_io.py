"""Required Data Pack inputs must never disappear silently on a bad refresh."""
import tempfile
import unittest
from pathlib import Path

from scripts.data_layer_io import load_required_layer


class RequiredTranslationLayerTests(unittest.TestCase):
    def test_valid_locale_layer_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "glossary.json"
            path.write_text('{"sourceLanguage":"en","targetLanguage":"fr","exact":{"Shield Block":"Maîtrise du blocage"}}', encoding="utf-8")
            self.assertEqual(load_required_layer(path)["exact"]["Shield Block"],
                             "Maîtrise du blocage")

    def test_missing_layer_fails_instead_of_returning_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "missing.json"):
                load_required_layer(Path(folder) / "missing.json")

    def test_malformed_json_fails_instead_of_returning_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "community.json"
            path.write_text('{"exact":', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "community.json"):
                load_required_layer(path)

    def test_duplicate_nested_key_fails_instead_of_last_write_wins(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            path.write_text('{"exact":{"Rage":"Rage","Rage":"Colère"}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_required_layer(path)

    def test_empty_or_nonobject_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manual.json"
            for value in ("{}", "[]", "null"):
                with self.subTest(value=value):
                    path.write_text(value, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_required_layer(path)


if __name__ == "__main__":
    unittest.main()
