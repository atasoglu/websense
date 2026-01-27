from unittest.mock import Mock, patch
from websense.scraper import Scraper


class TestScraper:
    def test_init(self):
        with (
            patch("websense.scraper.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
        ):
            scraper = Scraper(model="gpt-4")

            MockFetcher.assert_called_once()
            MockCleaner.assert_called_once()
            MockParser.assert_called_once_with(model="gpt-4")

            assert scraper.fetcher == MockFetcher.return_value
            assert scraper.cleaner == MockCleaner.return_value
            assert scraper.parser == MockParser.return_value

    def test_scrape_flow(self):
        with (
            patch("websense.scraper.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
        ):
            # Setup mocks
            mock_fetcher_instance = MockFetcher.return_value
            mock_cleaner_instance = MockCleaner.return_value
            mock_parser_instance = MockParser.return_value

            # Mock fetch response
            mock_response = Mock()
            mock_response.text = "<html>Raw Content</html>"
            mock_fetcher_instance.fetch.return_value = mock_response

            # Mock cleaner result
            mock_cleaner_instance.to_text.return_value = "Cleaned Content"

            # Mock parser result
            expected_data = {"key": "value"}
            mock_parser_instance.extract.return_value = expected_data

            scraper = Scraper()
            result = scraper.scrape("http://example.com", schema={"type": "json"})

            # Verify calls
            mock_fetcher_instance.fetch.assert_called_once_with("http://example.com")

            mock_cleaner_instance.to_text.assert_called_once_with(
                "<html>Raw Content</html>"
            )

            mock_parser_instance.extract.assert_called_once_with(
                "Cleaned Content", schema={"type": "json"}, example=None
            )

            assert result == expected_data
