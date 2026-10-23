"""Regression corpus structure and cross-role/section representation (offline)."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "data/wowhead_regression_pages.json").read_text(encoding="utf-8"))["pages"]


class WowheadRegressionCorpusTests(unittest.TestCase):
    def test_unique_ids_and_urls(self):
        self.assertEqual(len({p["id"] for p in PAGES}), len(PAGES))
        self.assertEqual(len({p["url"] for p in PAGES}), len(PAGES))

    def test_canonical_english_source_urls(self):
        for page in PAGES:
            with self.subTest(page=page["id"]):
                parsed = urlparse(page["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "www.wowhead.com")
                self.assertIn("/guide/classes/", parsed.path)
                self.assertFalse(parsed.query or parsed.fragment)

    def test_cross_class_and_section_coverage(self):
        paths = [urlparse(p["url"]).path.split("/guide/classes/", 1)[1].split("/")
                 for p in PAGES]
        classes = {parts[0] for parts in paths}
        sections = [parts[2] for parts in paths if len(parts) >= 3]
        self.assertGreaterEqual(len(classes), 10)
        for pattern in ("overview", "rotation", "abilities-talents", "stat-priority",
                        "bis-gear", "enchants-gems", "mythic-plus", "raid-tips"):
            with self.subTest(section=pattern):
                self.assertTrue(any(pattern in section for section in sections))


if __name__ == "__main__":
    unittest.main()
