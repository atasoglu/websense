from unittest.mock import Mock, patch, MagicMock
from websense.scraper import Scraper


class TestScraper:
    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_init_default(self, MockParser, MockCleaner, MockFetcher, MockConfig):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        scraper = Scraper()

        MockConfig.from_env.assert_called_once()
        MockFetcher.assert_called_once()
        MockCleaner.assert_called_once()
        MockParser.assert_called_once_with(mock_config_instance)

        assert scraper.fetcher == MockFetcher.return_value
        assert scraper.cleaner == MockCleaner.return_value
        assert scraper.parser == MockParser.return_value

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_init_with_model(self, MockParser, MockCleaner, MockFetcher, MockConfig):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        _ = Scraper(model="gpt-4")

        MockConfig.from_env.assert_called_once()
        assert mock_config_instance.model == "gpt-4"
        MockParser.assert_called_once_with(mock_config_instance)

    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_init_with_custom_config(self, MockParser, MockCleaner, MockFetcher):
        custom_config = MagicMock()

        scraper = Scraper(config=custom_config)

        MockParser.assert_called_once_with(custom_config)
        assert scraper.fetcher == MockFetcher.return_value
        assert scraper.cleaner == MockCleaner.return_value
        assert scraper.parser == MockParser.return_value

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_get_content_markdown(
        self, MockParser, MockCleaner, MockFetcher, MockConfig
    ):
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

        mock_fetcher_instance.fetch.assert_called_once_with("http://example.com")
        mock_cleaner_instance.to_markdown.assert_called_once_with(
            "<html>Raw Content</html>"
        )
        assert result == "# Markdown Content"

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_get_content_text(self, MockParser, MockCleaner, MockFetcher, MockConfig):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_fetcher_instance = MockFetcher.return_value
        mock_cleaner_instance = MockCleaner.return_value

        mock_response = Mock()
        mock_response.text = "<html>Raw Content</html>"
        mock_fetcher_instance.fetch.return_value = mock_response

        mock_cleaner_instance.to_text.return_value = "Plain Text Content"

        scraper = Scraper()
        result = scraper.get_content("http://example.com", convert_markdown=False)

        mock_fetcher_instance.fetch.assert_called_once_with("http://example.com")
        mock_cleaner_instance.to_text.assert_called_once_with(
            "<html>Raw Content</html>"
        )
        assert result == "Plain Text Content"

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_scrape_with_markdown(
        self, MockParser, MockCleaner, MockFetcher, MockConfig
    ):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_fetcher_instance = MockFetcher.return_value
        mock_cleaner_instance = MockCleaner.return_value
        mock_parser_instance = MockParser.return_value

        mock_response = Mock()
        mock_response.text = "<html>Raw Content</html>"
        mock_fetcher_instance.fetch.return_value = mock_response

        mock_cleaner_instance.to_markdown.return_value = "# Markdown Content"

        expected_data = {"key": "value"}
        mock_parser_instance.extract.return_value = expected_data

        scraper = Scraper()
        result = scraper.scrape("http://example.com", schema={"type": "json"})

        mock_fetcher_instance.fetch.assert_called_once_with("http://example.com")
        mock_cleaner_instance.to_markdown.assert_called_once_with(
            "<html>Raw Content</html>"
        )
        mock_parser_instance.extract.assert_called_once_with(
            "# Markdown Content", schema={"type": "json"}, example=None
        )
        assert result == expected_data

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_scrape_with_text(self, MockParser, MockCleaner, MockFetcher, MockConfig):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_fetcher_instance = MockFetcher.return_value
        mock_cleaner_instance = MockCleaner.return_value
        mock_parser_instance = MockParser.return_value

        mock_response = Mock()
        mock_response.text = "<html>Raw Content</html>"
        mock_fetcher_instance.fetch.return_value = mock_response

        mock_cleaner_instance.to_text.return_value = "Plain Text"

        expected_data = {"key": "value"}
        mock_parser_instance.extract.return_value = expected_data

        scraper = Scraper()
        result = scraper.scrape(
            "http://example.com", schema={"type": "json"}, convert_markdown=False
        )

        mock_cleaner_instance.to_text.assert_called_once_with(
            "<html>Raw Content</html>"
        )
        mock_parser_instance.extract.assert_called_once_with(
            "Plain Text", schema={"type": "json"}, example=None
        )
        assert result == expected_data

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_scrape_with_example(
        self, MockParser, MockCleaner, MockFetcher, MockConfig
    ):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_fetcher_instance = MockFetcher.return_value
        mock_cleaner_instance = MockCleaner.return_value
        mock_parser_instance = MockParser.return_value

        mock_response = Mock()
        mock_response.text = "<html>Content</html>"
        mock_fetcher_instance.fetch.return_value = mock_response

        mock_cleaner_instance.to_markdown.return_value = "# Content"
        mock_parser_instance.extract.return_value = {"title": "Extracted"}

        scraper = Scraper()
        example = {"title": "Example"}
        result = scraper.scrape("http://example.com", example=example)

        mock_parser_instance.extract.assert_called_once_with(
            "# Content", schema=None, example=example
        )
        assert result == {"title": "Extracted"}

    @patch("websense.scraper.Config")
    @patch("websense.scraper.Fetcher")
    @patch("websense.scraper.Cleaner")
    @patch("websense.scraper.Parser")
    def test_scrape_with_extract_kwargs(
        self, MockParser, MockCleaner, MockFetcher, MockConfig
    ):
        mock_config_instance = MagicMock()
        MockConfig.from_env.return_value = mock_config_instance

        mock_fetcher_instance = MockFetcher.return_value
        mock_cleaner_instance = MockCleaner.return_value
        mock_parser_instance = MockParser.return_value

        mock_response = Mock()
        mock_response.text = "<html>Content</html>"
        mock_fetcher_instance.fetch.return_value = mock_response

        mock_cleaner_instance.to_markdown.return_value = "# Content"
        mock_parser_instance.extract.return_value = {"data": "value"}

        scraper = Scraper()
        result = scraper.scrape(
            "http://example.com",
            schema={"type": "object"},
            extract_kwargs={"truncate": False, "prompt": "Custom prompt"},
        )

        mock_parser_instance.extract.assert_called_once_with(
            "# Content",
            schema={"type": "object"},
            example=None,
            truncate=False,
            prompt="Custom prompt",
        )
        assert result == {"data": "value"}
