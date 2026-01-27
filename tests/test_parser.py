import pytest
from unittest.mock import patch, MagicMock
from websense.parser import Parser


class TestParser:
    @patch("websense.parser.Config")
    def test_init_defaults(self, mock_config_cls):
        mock_config_instance = MagicMock()
        mock_config_cls.from_env.return_value = mock_config_instance

        parser = Parser()

        mock_config_cls.from_env.assert_called_once()
        assert parser.config == mock_config_instance

    @patch("websense.parser.Config")
    def test_init_custom_model(self, mock_config_cls):
        mock_config_instance = MagicMock()
        mock_config_cls.from_env.return_value = mock_config_instance

        parser = Parser(model="gpt-4")

        assert parser.config.model == "gpt-4"

    @patch("websense.parser.generate_api_response")
    def test_extract_with_schema(self, mock_generate):
        parser = Parser()
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        content = "Some content"

        mock_generate.return_value = {"title": "Test Title"}

        result = parser.extract(content, schema=schema)

        assert result == {"title": "Test Title"}
        mock_generate.assert_called_once()
        args, _ = mock_generate.call_args
        assert args[1] == schema
        assert parser.config in args

    @patch("websense.parser.generate_api_response")
    @patch("websense.parser.convert_example_to_schema")
    def test_extract_with_example(self, mock_convert, mock_generate):
        parser = Parser()
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
        parser = Parser()
        with pytest.raises(
            ValueError, match="must provide either a schema or a JSON example"
        ):
            parser.extract("content")

    @patch("websense.parser.generate_api_response")
    def test_extract_content_truncation(self, mock_generate):
        parser = Parser()
        long_content = "a" * 15000
        schema = {"type": "object"}

        parser.extract(long_content, schema=schema)

        args, _ = mock_generate.call_args
        prompt = args[0]
        # Should contain truncated content (12000 chars)
        assert len(long_content) > 12000
        # The prompt format is "Extract structured data from the following webpage content:\n\n{truncated_content}"
        # We check if the prompt contains the truncated version (12000 'a's)
        assert "a" * 12000 in prompt
        assert (
            "a" * 12001 not in prompt
        )  # should not have the 12001th char from content itself (if we ignore prompt prefix)
