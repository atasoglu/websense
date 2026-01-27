import pytest
import requests
from unittest.mock import Mock, patch
from websense.fetcher import Fetcher


class TestFetcher:
    def test_init_defaults(self):
        fetcher = Fetcher()
        assert fetcher.timeout == 10
        assert fetcher.session.headers["User-Agent"] == "WebSense/1.0"

    def test_init_custom(self):
        fetcher = Fetcher(user_agent="CustomBot", timeout=5, retries=1)
        assert fetcher.timeout == 5
        assert fetcher.session.headers["User-Agent"] == "CustomBot"

    def test_fetch_success(self):
        fetcher = Fetcher()
        with patch.object(fetcher.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Success"
            mock_get.return_value = mock_response

            response = fetcher.fetch("http://example.com")

            assert response == mock_response
            mock_get.assert_called_once_with("http://example.com", timeout=10)
            mock_response.raise_for_status.assert_called_once()

    def test_fetch_http_error(self):
        fetcher = Fetcher()
        with patch.object(fetcher.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                "404 Not Found"
            )
            mock_get.return_value = mock_response

            with pytest.raises(RuntimeError) as excinfo:
                fetcher.fetch("http://example.com")

            assert "Failed to fetch http://example.com" in str(excinfo.value)

    def test_fetch_connection_error(self):
        fetcher = Fetcher()
        with patch.object(fetcher.session, "get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection invalid")

            with pytest.raises(RuntimeError) as excinfo:
                fetcher.fetch("http://example.com")

            assert "Failed to fetch http://example.com" in str(excinfo.value)
