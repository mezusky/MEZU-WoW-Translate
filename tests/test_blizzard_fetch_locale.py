"""Official Blizzard memory fetches must request each page's own locale."""
import unittest
from unittest.mock import patch

from scripts.build_blizzard_memory import accept_language_for_url, fetch


class BlizzardFetchLocaleTests(unittest.TestCase):
    def test_source_and_target_news_urls_request_their_own_languages(self):
        self.assertEqual(
            accept_language_for_url("https://worldofwarcraft.blizzard.com/en-us/news/24245217"),
            "en-US,en;q=0.8",
        )
        self.assertEqual(
            accept_language_for_url("https://worldofwarcraft.blizzard.com/fr-fr/news/24245217"),
            "fr-FR,fr;q=0.8",
        )

    def test_future_locales_are_not_hardcoded_to_english_or_french(self):
        self.assertEqual(
            accept_language_for_url("https://worldofwarcraft.blizzard.com/de-de/news/123"),
            "de-DE,de;q=0.8",
        )
        self.assertEqual(
            accept_language_for_url("https://worldofwarcraft.blizzard.com/pt-br/news/123"),
            "pt-BR,pt;q=0.8",
        )

    def test_missing_locale_fails_closed_instead_of_fetching_english(self):
        with self.assertRaises(ValueError):
            accept_language_for_url("https://worldofwarcraft.blizzard.com/news/123")

    def test_fetch_passes_locale_header_to_request(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"<main>Bonjour</main>"

        with patch("urllib.request.urlopen", return_value=FakeResponse()) as mocked:
            result = fetch("https://worldofwarcraft.blizzard.com/fr-fr/news/123")
        request = mocked.call_args.args[0]
        self.assertEqual(request.get_header("Accept-language"), "fr-FR,fr;q=0.8")
        self.assertEqual(result, "<main>Bonjour</main>")


if __name__ == "__main__":
    unittest.main()
