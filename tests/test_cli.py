"""Unit tests for the CLI module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from websense.cli import (
    main,
    print_header,
    print_error,
    print_success,
    print_info,
    parse_json_input,
)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_json_file(tmp_path):
    """Create a temporary JSON file."""

    def _create(data: dict, filename: str = "test.json") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(json.dumps(data), encoding="utf-8")
        return file_path

    return _create


class TestHelperFunctions:
    """Tests for CLI helper functions."""

    def test_styled_echo(self, runner):
        """Test styled_echo outputs correctly."""
        result = runner.invoke(main, ["--help"])
        # styled_echo is used internally, we can verify it doesn't crash
        assert result.exit_code == 0

    def test_print_header(self, capsys):
        """Test print_header outputs header."""
        print_header()
        captured = capsys.readouterr()
        assert "WebSense" in captured.out
        assert "Making sense of the web" in captured.out

    def test_print_error(self, capsys):
        """Test print_error outputs error message."""
        print_error("test error")
        captured = capsys.readouterr()
        assert "test error" in captured.out
        assert "Error" in captured.out

    def test_print_success(self, capsys):
        """Test print_success outputs success message."""
        print_success("done")
        captured = capsys.readouterr()
        assert "done" in captured.out

    def test_print_info(self, capsys):
        """Test print_info outputs info message."""
        print_info("info message")
        captured = capsys.readouterr()
        assert "info message" in captured.out

    def test_parse_json_input_file_success(self, temp_json_file):
        """Test parse_json_input with valid JSON file."""
        data = {"key": "value"}
        file_path = temp_json_file(data)
        result = parse_json_input(str(file_path))
        assert result == data

    def test_parse_json_input_raw_string(self):
        """Test parse_json_input with raw JSON string."""
        data = {"key": "value"}
        result = parse_json_input(json.dumps(data))
        assert result == data

    def test_parse_json_input_not_found(self):
        """Test parse_json_input with missing file."""
        from click import ClickException

        # If it's not a valid JSON string and file doesn't exist
        with pytest.raises(
            ClickException,
            match="Input is neither a valid JSON string nor an existing file",
        ):
            parse_json_input("nonexistent.json")

    def test_parse_json_input_invalid_json_in_file(self, tmp_path):
        """Test parse_json_input with invalid JSON in a file."""
        from click import ClickException

        file_path = tmp_path / "bad.json"
        file_path.write_text("invalid json", encoding="utf-8")
        with pytest.raises(ClickException, match="Invalid JSON in file"):
            parse_json_input(str(file_path))

    def test_parse_json_input_not_a_file(self, tmp_path):
        """Test parse_json_input with a path that is a directory."""
        from click import ClickException

        dir_path = tmp_path / "test_dir"
        dir_path.mkdir()
        with pytest.raises(ClickException, match="is not a file"):
            parse_json_input(str(dir_path))

    def test_parse_json_input_file_read_error(self, tmp_path):
        """Test parse_json_input for generic read error."""
        from click import ClickException

        path = tmp_path / "locked.json"
        path.write_text("{}", encoding="utf-8")
        # Mock Path.read_text to raise exception
        with patch("pathlib.Path.read_text", side_effect=OSError("Read error")):
            with pytest.raises(ClickException, match="Error reading file"):
                parse_json_input(str(path))

    def test_parse_json_input_raw_json_malformed(self):
        """Test parse_json_input with raw JSON that is slightly malformed but starts with brace."""
        from click import ClickException

        with pytest.raises(
            ClickException, match="neither a valid JSON string nor an existing file"
        ):
            parse_json_input("{'key': 'value'}")


class TestMainCommand:
    """Tests for the main CLI group."""

    def test_main_help(self, runner):
        """Test main command shows help."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "WebSense" in result.output
        assert "scrape" in result.output
        assert "content" in result.output

    def test_main_version(self, runner):
        """Test main command shows version."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0


class TestScrapeCommand:
    """Tests for the scrape command."""

    def test_scrape_help(self, runner):
        """Test scrape command shows help."""
        result = runner.invoke(main, ["scrape", "--help"])
        assert result.exit_code == 0
        assert "URL" in result.output
        assert "--model" in result.output
        assert "--schema" in result.output
        assert "--example" in result.output
        assert "--timeout" in result.output
        assert "--retries" in result.output

    def test_scrape_missing_url(self, runner):
        """Test scrape command requires URL."""
        result = runner.invoke(main, ["scrape"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "URL" in result.output

    def test_scrape_missing_schema_and_example(self, runner):
        """Test scrape requires schema or example."""
        result = runner.invoke(main, ["scrape", "https://example.com"])
        assert result.exit_code != 0
        assert "schema" in result.output.lower() or "example" in result.output.lower()

    def test_scrape_with_example(self, runner, temp_json_file):
        """Test scrape with example file."""
        example = {"title": "string", "price": 0}
        example_path = temp_json_file(example, "example.json")

        mock_result = {"title": "Test Product", "price": 99}

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test content"
            MockCleaner.return_value = mock_cleaner

            mock_parser = MagicMock()
            mock_parser.extract.return_value = mock_result
            MockParser.return_value = mock_parser

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main, ["scrape", "https://example.com", "--example", str(example_path)]
            )

            assert result.exit_code == 0
            assert "Test Product" in result.output

    def test_scrape_with_schema(self, runner, temp_json_file):
        """Test scrape with schema file."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_path = temp_json_file(schema, "schema.json")

        mock_result = {"name": "Test"}

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test content"
            MockCleaner.return_value = mock_cleaner

            mock_parser = MagicMock()
            mock_parser.extract.return_value = mock_result
            MockParser.return_value = mock_parser

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main, ["scrape", "https://example.com", "--schema", str(schema_path)]
            )

            assert result.exit_code == 0

    def test_scrape_with_output_file(self, runner, temp_json_file, tmp_path):
        """Test scrape saves output to file."""
        example = {"title": "string"}
        example_path = temp_json_file(example, "example.json")
        output_path = tmp_path / "output.json"

        mock_result = {"title": "Test"}

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html>Test</html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test"
            MockCleaner.return_value = mock_cleaner

            mock_parser = MagicMock()
            mock_parser.extract.return_value = mock_result
            MockParser.return_value = mock_parser

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--example",
                    str(example_path),
                    "--output",
                    str(output_path),
                ],
            )

            assert result.exit_code == 0
            assert output_path.exists()

    def test_scrape_verbose_saved_output(self, runner, temp_json_file, tmp_path):
        """Test scrape with verbose and output file to cover line 197."""
        example = {"title": "string"}
        example_path = temp_json_file(example, "example.json")
        output_path = tmp_path / "v_output.json"

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
            patch("websense.cli.Scraper.scrape") as mock_scrape,
        ):
            MockFetcher.return_value = MagicMock()
            MockCleaner.return_value = MagicMock()
            MockParser.return_value = MagicMock()
            MockConfig.from_env.return_value = MagicMock()
            mock_scrape.return_value = {"title": "Test"}

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--example",
                    str(example_path),
                    "--output",
                    str(output_path),
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "Result saved to" in result.output
            assert "Using example from file" in result.output

    def test_scrape_verbose_raw_json(self, runner):
        """Test scrape with verbose and raw JSON to cover lines 146-147."""
        with (
            patch("websense.cli.Fetcher"),
            patch("websense.scraper.Cleaner"),
            patch("websense.scraper.Parser"),
            patch("websense.cli.Config") as MockConfig,
            patch("websense.cli.Scraper.scrape") as mock_scrape,
        ):
            MockConfig.from_env.return_value = MagicMock()
            mock_scrape.return_value = {"x": 1}

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--schema",
                    '{"type": "object"}',
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "Using schema from string" in result.output

    def test_scrape_verbose_mode(self, runner, temp_json_file):
        """Test scrape with verbose output."""
        example = {"title": "string"}
        example_path = temp_json_file(example, "example.json")

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html>Test</html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test"
            MockCleaner.return_value = mock_cleaner

            mock_parser = MagicMock()
            mock_parser.extract.return_value = {"title": "x"}
            MockParser.return_value = mock_parser

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--example",
                    str(example_path),
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "WebSense" in result.output

    def test_scrape_with_model(self, runner, temp_json_file):
        """Test scrape with custom model."""
        example = {"title": "string"}
        example_path = temp_json_file(example, "example.json")

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html>Test</html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test"
            MockCleaner.return_value = mock_cleaner

            mock_parser = MagicMock()
            mock_parser.extract.return_value = {"title": "x"}
            MockParser.return_value = mock_parser

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--example",
                    str(example_path),
                    "--model",
                    "gpt-4",
                ],
            )

            assert result.exit_code == 0
            assert mock_config.model == "gpt-4"

    def test_scrape_runtime_error(self, runner, temp_json_file):
        """Test scrape handles runtime errors."""
        example = {"title": "string"}
        example_path = temp_json_file(example, "example.json")

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_fetcher.fetch.side_effect = RuntimeError("Connection failed")
            MockFetcher.return_value = mock_fetcher

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main, ["scrape", "https://example.com", "--example", str(example_path)]
            )

            assert result.exit_code == 1
            assert "Connection failed" in result.output

    def test_scrape_no_markdown(self, runner, temp_json_file):
        """Test scrape with no-markdown flag."""
        example = {"title": "string"}
        example_path = temp_json_file(example, "example.json")

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html>Test</html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_text.return_value = "Test"
            MockCleaner.return_value = mock_cleaner

            mock_parser = MagicMock()
            mock_parser.extract.return_value = {"title": "x"}
            MockParser.return_value = mock_parser

            mock_config = MagicMock()
            MockConfig.from_env.return_value = mock_config

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--example",
                    str(example_path),
                    "--no-markdown",
                ],
            )

            assert result.exit_code == 0
            mock_cleaner.to_text.assert_called_once()

    def test_scrape_with_raw_json_example(self, runner):
        """Test scrape with raw JSON example string."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            MockFetcher.return_value = MagicMock()
            MockCleaner.return_value = MagicMock()
            mock_parser = MagicMock()
            mock_parser.extract.return_value = {"title": "x"}
            MockParser.return_value = mock_parser
            MockConfig.from_env.return_value = MagicMock()

            result = runner.invoke(
                main,
                ["scrape", "https://example.com", "--example", '{"title": "string"}'],
            )

            assert result.exit_code == 0

    def test_scrape_with_raw_json_schema(self, runner):
        """Test scrape with raw JSON schema string."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
        ):
            MockFetcher.return_value = MagicMock()
            MockCleaner.return_value = MagicMock()
            mock_parser = MagicMock()
            mock_parser.extract.return_value = {"title": "x"}
            MockParser.return_value = mock_parser
            MockConfig.from_env.return_value = MagicMock()

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--schema",
                    '{"type": "object", "properties": {"title": {"type": "string"}}}',
                ],
            )

            assert result.exit_code == 0

    def test_scrape_with_prompt(self, runner):
        """Test scrape with custom prompt."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.scraper.Cleaner") as MockCleaner,
            patch("websense.scraper.Parser") as MockParser,
            patch("websense.cli.Config") as MockConfig,
            patch("websense.cli.Scraper.scrape") as mock_scrape,
        ):
            MockFetcher.return_value = MagicMock()
            MockCleaner.return_value = MagicMock()
            MockParser.return_value = MagicMock()
            MockConfig.from_env.return_value = MagicMock()
            mock_scrape.return_value = {"status": "ok"}

            result = runner.invoke(
                main,
                [
                    "scrape",
                    "https://example.com",
                    "--example",
                    '{"x": 1}',
                    "--prompt",
                    "Custom prompt",
                ],
            )

            assert result.exit_code == 0
            # Verify prompt was passed in extract_kwargs
            call_kwargs = mock_scrape.call_args[1]
            assert call_kwargs["extract_kwargs"]["prompt"] == "Custom prompt"

    def test_scrape_unexpected_error(self, runner):
        """Test scrape handles unexpected exceptions."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Config") as MockConfig,
        ):
            MockFetcher.side_effect = Exception("Boom")
            MockConfig.from_env.return_value = MagicMock()

            result = runner.invoke(
                main, ["scrape", "https://example.com", "--example", '{"x": 1}']
            )

            assert result.exit_code == 1
            assert "Unexpected error" in result.output


class TestContentCommand:
    """Tests for the content command."""

    def test_content_help(self, runner):
        """Test content command shows help."""
        result = runner.invoke(main, ["content", "--help"])
        assert result.exit_code == 0
        assert "URL" in result.output
        assert "--timeout" in result.output
        assert "--no-markdown" in result.output

    def test_content_missing_url(self, runner):
        """Test content command requires URL."""
        result = runner.invoke(main, ["content"])
        assert result.exit_code != 0

    def test_content_basic(self, runner):
        """Test content extraction."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Cleaner") as MockCleaner,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test content</body></html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "# Test content"
            MockCleaner.return_value = mock_cleaner

            result = runner.invoke(main, ["content", "https://example.com"])

            assert result.exit_code == 0
            assert "Test content" in result.output

    def test_content_plain_text(self, runner):
        """Test content extraction as plain text."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Cleaner") as MockCleaner,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_text.return_value = "Test plain text"
            MockCleaner.return_value = mock_cleaner

            result = runner.invoke(
                main, ["content", "https://example.com", "--no-markdown"]
            )

            assert result.exit_code == 0
            mock_cleaner.to_text.assert_called_once()

    def test_content_with_output_file(self, runner, tmp_path):
        """Test content saves to file."""
        output_path = tmp_path / "content.md"

        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Cleaner") as MockCleaner,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "# Test"
            MockCleaner.return_value = mock_cleaner

            result = runner.invoke(
                main, ["content", "https://example.com", "--output", str(output_path)]
            )

            assert result.exit_code == 0
            assert output_path.exists()
            assert "# Test" in output_path.read_text()

    def test_content_verbose(self, runner):
        """Test content with verbose output."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Cleaner") as MockCleaner,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test"
            MockCleaner.return_value = mock_cleaner

            result = runner.invoke(
                main, ["content", "https://example.com", "--verbose"]
            )

            assert result.exit_code == 0
            assert "WebSense" in result.output

    def test_content_custom_options(self, runner):
        """Test content with custom options."""
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Cleaner") as MockCleaner,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "<html>Test</html>"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "Test"
            MockCleaner.return_value = mock_cleaner

            result = runner.invoke(
                main,
                [
                    "content",
                    "https://example.com",
                    "--timeout",
                    "30",
                    "--retries",
                    "5",
                    "--user-agent",
                    "CustomAgent/1.0",
                ],
            )

            assert result.exit_code == 0
            MockFetcher.assert_called_with(
                user_agent="CustomAgent/1.0", timeout=30, retries=5
            )

    def test_content_runtime_error(self, runner):
        """Test content handles runtime errors."""
        with patch("websense.cli.Fetcher") as MockFetcher:
            mock_fetcher = MagicMock()
            mock_fetcher.fetch.side_effect = RuntimeError("Network error")
            MockFetcher.return_value = mock_fetcher

            result = runner.invoke(main, ["content", "https://example.com"])

            assert result.exit_code == 1
            assert "Network error" in result.output

    def test_content_unexpected_error(self, runner):
        """Test content handles unexpected errors."""
        with patch("websense.cli.Fetcher") as MockFetcher:
            mock_fetcher = MagicMock()
            mock_fetcher.fetch.side_effect = Exception("Unexpected")
            MockFetcher.return_value = mock_fetcher

            result = runner.invoke(main, ["content", "https://example.com"])

            assert result.exit_code == 1
            assert "Unexpected" in result.output

    def test_content_verbose_saved_output(self, runner, tmp_path):
        """Test content with verbose and output file to cover line 274."""
        output_path = tmp_path / "v_content.md"
        with (
            patch("websense.cli.Fetcher") as MockFetcher,
            patch("websense.cli.Cleaner") as MockCleaner,
        ):
            mock_fetcher = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "html"
            mock_fetcher.fetch.return_value = mock_response
            MockFetcher.return_value = mock_fetcher

            mock_cleaner = MagicMock()
            mock_cleaner.to_markdown.return_value = "md"
            MockCleaner.return_value = mock_cleaner

            result = runner.invoke(
                main,
                [
                    "content",
                    "https://example.com",
                    "--output",
                    str(output_path),
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "Content saved to" in result.output


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_basic(self, runner):
        """Test basic search functionality."""
        with patch("websense.cli.Searcher") as MockSearcher:
            mock_searcher = MockSearcher.return_value
            mock_searcher.search.return_value = [
                {"title": "T", "url": "U", "description": "D"}
            ]

            result = runner.invoke(main, ["search", "query"])

            assert result.exit_code == 0
            assert "T" in result.output

    def test_search_verbose(self, runner):
        """Test search with verbose output."""
        with patch("websense.cli.Searcher") as MockSearcher:
            mock_searcher = MockSearcher.return_value
            mock_searcher.search.return_value = [
                {"title": "T", "url": "U", "description": "D"}
            ]

            result = runner.invoke(main, ["search", "query", "--verbose"])

            assert result.exit_code == 0
            assert "WebSense" in result.output
            assert "Search query: query" in result.output

    def test_search_error(self, runner):
        """Test search handles errors."""
        with patch("websense.cli.Searcher") as MockSearcher:
            mock_searcher = MockSearcher.return_value
            mock_searcher.search.side_effect = RuntimeError("Search failed")

            result = runner.invoke(main, ["search", "query"])

            assert result.exit_code == 1
            assert "Search failed" in result.output


class TestSearchScrapeCommand:
    """Tests for the search-scrape command."""

    def test_search_scrape_basic(self, runner):
        """Test basic search-scrape functionality."""
        with (
            patch("websense.cli.Scraper") as MockScraper,
            patch("websense.cli.Config"),
        ):
            mock_scraper = MockScraper.return_value
            mock_scraper.search_and_scrape.return_value = {
                "query": "q",
                "top_k": 1,
                "sources": [{"url": "u", "success": True}],
                "data": {"result": "ok"},
            }

            result = runner.invoke(main, ["search-scrape", "q", "--example", '{"x":1}'])

            assert result.exit_code == 0
            assert "ok" in result.output

    def test_search_scrape_verbose(self, runner):
        """Test search-scrape with verbose output."""
        with (
            patch("websense.cli.Scraper") as MockScraper,
            patch("websense.cli.Config"),
        ):
            mock_scraper = MockScraper.return_value
            mock_scraper.search_and_scrape.return_value = {
                "query": "q",
                "top_k": 1,
                "sources": [{"url": "u", "success": True}],
                "data": {"result": "ok"},
            }

            result = runner.invoke(
                main, ["search-scrape", "q", "--example", '{"x":1}', "--verbose"]
            )

            assert result.exit_code == 0
            assert "WebSense" in result.output
            assert "Search query: q" in result.output
            assert "Successfully scraped 1/1 sources" in result.output

    def test_search_scrape_error(self, runner):
        """Test search-scrape handles errors."""
        with (
            patch("websense.cli.Scraper") as MockScraper,
            patch("websense.cli.Config"),
        ):
            mock_scraper = MockScraper.return_value
            mock_scraper.search_and_scrape.side_effect = RuntimeError("Scrape failed")

            result = runner.invoke(main, ["search-scrape", "q", "--example", '{"x":1}'])

            assert result.exit_code == 1
            assert "Scrape failed" in result.output
