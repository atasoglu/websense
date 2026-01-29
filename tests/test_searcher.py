from unittest.mock import patch
import pytest
from websense.searcher import Searcher


class TestSearcher:
    """Tests for Searcher class."""

    @patch("websense.searcher.DDGS")
    def test_search_returns_results(self, MockDDGS):
        """Test search returns formatted results."""
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [
            {
                "title": "Result 1",
                "href": "https://example1.com",
                "body": "Description 1",
            },
            {
                "title": "Result 2",
                "href": "https://example2.com",
                "body": "Description 2",
            },
        ]

        searcher = Searcher()
        # User's search method now requires 3 arguments
        results = searcher.search("test query", max_results=5, region="wt-wt")

        assert len(results) == 2
        assert results[0] == {
            "title": "Result 1",
            "url": "https://example1.com",
            "description": "Description 1",
        }
        mock_ddgs_instance.text.assert_called_once_with(
            "test query", region="wt-wt", max_results=5
        )

    @patch("websense.searcher.DDGS")
    def test_search_empty_results(self, MockDDGS):
        """Test search returns empty list when no results."""
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = []

        searcher = Searcher()
        results = searcher.search("test query", max_results=5, region="wt-wt")

        assert results == []

    @patch("websense.searcher.DDGS")
    def test_search_handles_missing_fields(self, MockDDGS):
        """Test search handles results with missing fields."""
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [
            {"title": "Only Title"},
            {"href": "https://only-url.com"},
            {},
        ]

        searcher = Searcher()
        results = searcher.search("test query", max_results=5, region="wt-wt")

        assert results == [
            {"title": "Only Title", "url": "", "description": ""},
            {"title": "", "url": "https://only-url.com", "description": ""},
            {"title": "", "url": "", "description": ""},
        ]

    @patch("websense.searcher.DDGS")
    def test_search_raises_on_error(self, MockDDGS):
        """Test search raises RuntimeError on exception."""
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.side_effect = Exception("Network error")

        searcher = Searcher()
        with pytest.raises(RuntimeError) as exc_info:
            searcher.search("test query", max_results=5, region="wt-wt")

        assert "Search failed for query 'test query'" in str(exc_info.value)
