import pytest
from unittest.mock import patch, MagicMock
from websense.parser import Parser


class TestParser:
    def test_init_with_config(self):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        assert parser.config == mock_config

    @patch("websense.parser.generate_api_response")
    def test_extract_with_schema(self, mock_generate):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        content = "Some content"

        mock_generate.return_value = {"title": "Test Title"}

        result = parser.extract(content, schema=schema)

        assert result == {"title": "Test Title"}
        mock_generate.assert_called_once()
        args, _ = mock_generate.call_args
        assert args[1] == schema
        assert args[2] == mock_config

    @patch("websense.parser.convert_example_to_schema")
    @patch("websense.parser.generate_api_response")
    def test_extract_with_example(self, mock_generate, mock_convert):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        example = {"title": "Example Title"}
        generated_schema = {
            "type": "object",
            "properties": {"title": {"type": "string"}},
        }

        mock_convert.return_value = generated_schema
        mock_generate.return_value = {"title": "Extracted Title"}

        result = parser.extract("content", example=example)

        assert result == {"title": "Extracted Title"}
        mock_convert.assert_called_once_with(example)
        mock_generate.assert_called_once()
        args, _ = mock_generate.call_args
        assert args[1] == generated_schema

    def test_extract_no_schema_or_example(self):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        with pytest.raises(
            ValueError, match="must provide either a schema or a JSON example"
        ):
            parser.extract("content")

    @patch("websense.parser.generate_api_response")
    def test_extract_content_truncation(self, mock_generate):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        long_content = "a" * 15000
        schema = {"type": "object"}

        parser.extract(long_content, schema=schema)

        args, _ = mock_generate.call_args
        prompt = args[0]
        # Should contain truncated content (12000 chars)
        assert len(long_content) > 12000
        assert "a" * 12000 in prompt
        assert "a" * 12001 not in prompt

    @patch("websense.parser.generate_api_response")
    def test_extract_no_truncation(self, mock_generate):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        long_content = "a" * 15000
        schema = {"type": "object"}

        parser.extract(long_content, schema=schema, truncate=False)

        args, _ = mock_generate.call_args
        prompt = args[0]
        # Content should not be truncated
        assert "a" * 15000 in prompt

    @patch("websense.parser.generate_api_response")
    def test_extract_custom_truncate_length(self, mock_generate):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        content = "a" * 1000
        schema = {"type": "object"}

        parser.extract(content, schema=schema, truncate_length=500)

        args, _ = mock_generate.call_args
        prompt = args[0]
        # Content should be truncated to 500 chars
        assert "a" * 500 in prompt
        assert "a" * 501 not in prompt

    @patch("websense.parser.generate_api_response")
    def test_extract_custom_prompt(self, mock_generate):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        content = "Test content"
        schema = {"type": "object"}
        custom_prompt = "Extract product info from this page."

        parser.extract(content, schema=schema, prompt=custom_prompt)

        args, _ = mock_generate.call_args
        prompt = args[0]
        assert custom_prompt in prompt
        assert content in prompt

    @patch("websense.parser.generate_api_response")
    def test_extract_default_prompt(self, mock_generate):
        mock_config = MagicMock()
        parser = Parser(config=mock_config)
        content = "Test content"
        schema = {"type": "object"}

        parser.extract(content, schema=schema)

        args, _ = mock_generate.call_args
        prompt = args[0]
        assert "Extract structured data from the following webpage content" in prompt
