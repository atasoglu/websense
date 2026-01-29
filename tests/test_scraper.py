from unittest.mock import Mock, patch, MagicMock
from websense.scraper import Scraper
import pytest


class TestScraper:
    @patch("websense.scraper.Searcher")
    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_init(self, MockParser, MockCleaner, MockFetcher, MockConfig, MockSearcher):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        scraper = Scraper()

        MockConfig.from_env.assert_called_once()
        assert scraper.searcher == MockSearcher.return_value

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_get_content(self, MockParser, MockCleaner, MockFetcher, MockConfig):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_fetcher_instance = MockFetcher.return_value
        mock_cleaner_instance = MockCleaner.return_value

        mock_response = Mock()
        mock_response.text = "<html>Raw Content</html>"
        mock_fetcher_instance.fetch.return_value = mock_response

        mock_cleaner_instance.to_markdown.return_value = "# Markdown Content"

        scraper = Scraper()
        result = scraper.get_content("http://example.com")

        assert result == "# Markdown Content"

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_scrape(self, MockParser, MockCleaner, MockFetcher, MockConfig):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_parser_instance = MockParser.return_value
        MockCleaner.return_value.to_markdown.return_value = "# Content"
        mock_parser_instance.extract.return_value = {"key": "value"}

        scraper = Scraper()
        result = scraper.scrape(
            "http://example.com", schema={"type": "json"}, extract_kwargs={}
        )

        assert result == {"key": "value"}

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    @patch("websense.scraper.Searcher")
    def test_search_and_scrape_single(
        self, MockSearcher, MockParser, MockCleaner, MockFetcher, MockConfig
    ):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_searcher = MockSearcher.return_value
        mock_searcher.search.return_value = [{"url": "https://example.com/1"}]

        mock_parser = MockParser.return_value
        mock_parser.extract.return_value = {"field": "data"}

        scraper = Scraper()
        # Must pass extract_kwargs={} to avoid crash in current src
        result = scraper.search_and_scrape("query", max_results=1, extract_kwargs={})

        assert result == {"field": "data"}

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    @patch("websense.scraper.Searcher")
    def test_search_and_scrape_multi(
        self, MockSearcher, MockParser, MockCleaner, MockFetcher, MockConfig
    ):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_searcher = MockSearcher.return_value
        mock_searcher.search.return_value = [
            {"url": "https://example.com/1"},
            {"url": "https://example.com/2"},
        ]

        mock_parser = MockParser.return_value
        # side_effect: first two for individual scrapes, third for consolidation (judge)
        mock_parser.extract.side_effect = [{"f": 1}, {"f": 2}, {"f": "consolidated"}]

        scraper = Scraper()
        result = scraper.search_and_scrape("query", max_results=2, extract_kwargs={})

        assert result == {"f": "consolidated"}

    def test_judge(self):
        """Test the _judge method directly."""
        with (
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.scraper.Config") as MockConfig,
        ):
            mock_config_instance = MagicMock()
            MockConfig.from_env.return_value = mock_config_instance
            mock_parser = MockParser.return_value
            mock_parser.extract.return_value = {"merged": "ok"}

            scraper = Scraper()
            data = [{"a": 1}, {"b": 2}]
            result = scraper._judge("test query", data)

            assert result == {"merged": "ok"}
            mock_parser.extract.assert_called_once()
            # Verify data was passed in the prompt
            call_args = mock_parser.extract.call_args
            assert "test query" in call_args[1]["prompt"]

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Searcher")
    def test_search_and_scrape_no_results(self, MockSearcher, MockConfig):
        """Test search_and_scrape raising error when no results."""
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance
        MockSearcher.return_value.search.return_value = []
        scraper = Scraper()
        with pytest.raises(RuntimeError, match="No search results found"):
            scraper.search_and_scrape("query", extract_kwargs={})
