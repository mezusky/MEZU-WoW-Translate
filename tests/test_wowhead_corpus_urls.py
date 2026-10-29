"""Keep Wowhead regression URLs canonical; do not fetch Wowhead in CI."""
import json
import re
import unittest
from pathlib import Path


class WowheadCorpusUrlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = Path(__file__).resolve().parents[1] / "data" / "wowhead_regression_pages.json"
        cls.pages = json.loads(corpus.read_text(encoding="utf-8"))["pages"]

    def test_unique_ids_and_urls(self):
        ids = [page["id"] for page in self.pages]
        urls = [page["url"] for page in self.pages]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(urls), len(set(urls)))

    def test_gear_guides_use_current_canonical_slug(self):
        # Three original corpus entries used an obsolete /bis-gear-pve-* slug.
        # Wowhead's live indexed guides for independent classes use /bis-gear.
        for page in self.pages:
            if "/bis-gear" in page["url"]:
                with self.subTest(guide=page["id"]):
                    self.assertRegex(page["url"], r"/bis-gear$")
                    self.assertNotRegex(page["url"], r"/bis-gear-pve-")

    def test_new_heldouts_span_roles_and_sections(self):
        urls = {page["url"] for page in self.pages}
        expected = (
            "https://www.wowhead.com/guide/classes/shaman/enhancement/overview-pve-dps",
            "https://www.wowhead.com/guide/classes/evoker/preservation/midnight-pre-patch",
            "https://www.wowhead.com/guide/classes/warrior/protection/midnight-pre-patch",
            "https://www.wowhead.com/guide/classes/warlock/demonology/overview-pve-dps",
            "https://www.wowhead.com/guide/classes/monk/windwalker/talent-builds-pve-dps",
        )
        self.assertTrue(set(expected).issubset(urls))


if __name__ == "__main__":
    unittest.main()
