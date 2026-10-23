"""Source-access classification must not inflate translation regression counts."""
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from wowhead_source_status import classify_html_source, classify_fetch_error


class WowheadSourceStatusTests(unittest.TestCase):
    def test_http_403_is_access_blocked(self):
        error = HTTPError("https://www.wowhead.com/guide/", 403, "Forbidden", {}, None)
        status, note = classify_fetch_error(error)
        self.assertEqual(status, "blocked_http")
        self.assertIn("403", note)

    def test_http_429_is_access_blocked(self):
        error = HTTPError("https://www.wowhead.com/guide/", 429, "Too Many Requests", {}, None)
        self.assertEqual(classify_fetch_error(error)[0], "blocked_http")

    def test_javascript_challenge_with_http_200_is_not_guide(self):
        html = "<h1>JavaScript is disabled</h1>Enable JavaScript and reload the page to verify that you're not a robot."
        self.assertEqual(classify_html_source(html)[0], "blocked_challenge")

    def test_real_guide_html_is_accessible(self):
        html = "<article><h1>Frost Mage Talent Builds</h1><p>Raid and Mythic+ builds.</p></article>"
        self.assertEqual(classify_html_source(html), ("accessible", None))

    def test_empty_body_is_not_scored(self):
        self.assertEqual(classify_html_source("  ")[0], "unscorable")

    def test_network_errors_remain_distinct(self):
        self.assertEqual(classify_fetch_error(TimeoutError("timed out"))[0], "fetch_error")


if __name__ == "__main__":
    unittest.main()
