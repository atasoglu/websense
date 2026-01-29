"""Web search functionality using DuckDuckGo."""

from ddgs import DDGS


class Searcher:
    """Handles web search operations using DuckDuckGo."""

    def search(
        self, query: str, max_results: int = 5, region: str = "wt-wt"
    ) -> list[dict]:
        """Perform a web search and return results.

        Args:
            query: The search query string.
            max_results: Maximum number of results to return.
            region: DuckDuckGo region code (e.g., 'wt-wt', 'us-en').

        Returns:
            A list of dictionaries, each containing:
                - title: The title of the result.
                - url: The URL of the result.
                - description: A snippet/description of the result.

        Raises:
            RuntimeError: If the search fails.
        """
        try:
            results = DDGS().text(query, region=region, max_results=max_results)
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "description": r.get("body", ""),
                }
                for r in results
            ]
        except Exception as e:
            raise RuntimeError(f"Search failed for query '{query}': {str(e)}") from e
