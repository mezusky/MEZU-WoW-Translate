"""Standalone Blizzard collectors must enforce the same alias checks as package imports.

The build pipeline may put scripts/ directly on sys.path. That invokes the
absolute-import fallback, which must import every referenced safety helper.
"""
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StandaloneBlizzardCollectorTests(unittest.TestCase):
    def test_absolute_import_fallback_rejects_conflicting_aliases(self):
        program = """
import sys
sys.path.insert(0, "scripts")
from blizzard_index_pairs import index_names
from blizzard_search_pairs import search_names

hits = [
    {"id": 101, "name": {"en_US": "Alpha", "en-US": "Wrong Alpha"}},
    {"id": 101, "name": {"en_US": "Alpha"}},
    {"id": 102, "name": {"en_US": "Gamma", "en-US": "Gamma"}},
]
assert index_names({"results": [{"data": hit} for hit in hits]}, "en-US") == {"102": "Gamma"}
assert search_names({"results": [{"data": hit} for hit in hits]}, "en-US") == {"102": "Gamma"}
"""
        result = subprocess.run(
            [sys.executable, "-c", program],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
