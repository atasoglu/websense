"""Web scraper with search and multi-source consolidation."""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .fetcher import Fetcher
from .cleaner import Cleaner
from .parser import Parser
from .searcher import Searcher
from ask2api import Config


class Scraper:
    """Default scraper using Fetcher → Cleaner → markdownify pipeline."""

    def __init__(self, model: str = None, config: Config | None = None):
        """Initialize the Scraper with optional model and configuration.

        Args:
            model: Optional LLM model name to use for parsing. If provided, overrides the model in config.
            config: Optional ask2api Config. If not provided, loads from env.
        """
        if not config:
            config = Config.from_env()
        if model:
            config.model = model
        self.fetcher = Fetcher()
        self.cleaner = Cleaner()
        self.parser = Parser(config)
        self.searcher = Searcher()

    def get_content(self, url: str, convert_markdown: bool = True) -> str:
        """Fetch URL and process content.

        Args:
            url: The URL to fetch.
            convert_markdown: If True, convert HTML to Markdown.

        Returns:
            Processed content as plain text or Markdown.
        """
        response = self.fetcher.fetch(url)
        if convert_markdown:
            return self.cleaner.to_markdown(response.text)
        return self.cleaner.to_text(response.text)

    def scrape(
        self,
        url: str,
        schema: dict = None,
        example: dict = None,
        convert_markdown: bool = True,
        extract_kwargs: dict | None = None,
    ) -> dict:
        """Scrape URL and extract structured data.

        Args:
            url: The URL to scrape.
            schema: Optional JSON schema dict.
            example: Optional JSON example dict to infer schema from.
            convert_markdown: If True, convert HTML to Markdown before parsing.

        Returns:
            Extracted data as a dictionary.
        """
        content = self.get_content(url, convert_markdown)
        return self.parser.extract(
            content, schema=schema, example=example, **(extract_kwargs or {})
        )

    def _judge(
        self,
        query: str,
        data: list[dict],
    ):
        """Consolidates data from multiple sources using LLM.

        Args:
            query: The original search query for context.
            data: List of dictionaries to consolidate.

        Returns:
            Consolidated dictionary of data.
        """
        prompt = f"""Analyze and judge extracted data sources based on the query.

        INSTRUCTIONS:
        1. For each field, select the most accurate and complete value.
        2. Prefer specific values over vague ones, and consensus values.
        3. Use available values when some sources are missing fields.
        4. Return ONLY the consolidated data in JSON, no explanations.

        Query:
        {query}
        """
        json_kwargs = {"indent": 2, "ensure_ascii": False}
        data_str = "Data:" + "\n\n".join(json.dumps(r, **json_kwargs) for r in data)
        return self.parser.extract(data_str, example=data[0], prompt=prompt)

    def search_and_scrape(
        self,
        query: str,
        schema: dict = None,
        example: dict = None,
        convert_markdown: bool = True,
        extract_kwargs: dict = None,
        max_results: int = 1,
        region: str = "wt-wt",
        max_workers: int = 4,
    ) -> dict:
        """Search the web for a query and scrape the results.

        Args:
            query: Search query string.
            schema: Optional JSON schema.
            example: Optional JSON example.
            convert_markdown: Whether to convert HTML to Markdown.
            extract_kwargs: Additional arguments for extraction.
            max_results: Max number of results to fetch.
            region: DuckDuckGo region code.
            max_workers: Max threads for parallel scraping.

        Returns:
            Consolidated data if max_results > 1, else single source data.
        """
        results = self.searcher.search(query, max_results, region)
        if not results:
            raise RuntimeError(f"No search results found for query '{query}'")

        extract_kwargs = extract_kwargs or {}
        # Build extraction prompt with query context
        if "prompt" not in extract_kwargs:
            extract_kwargs["prompt"] = (
                f"The user searched for: '{query}'. Extract the relevant data from this webpage."
            )
        scrape_kwargs = {
            "schema": schema,
            "example": example,
            "convert_markdown": convert_markdown,
            "extract_kwargs": extract_kwargs,
        }

        if max_results == 1:
            url = results[0]["url"]
            return self.scrape(url, **scrape_kwargs)

        with ThreadPoolExecutor(max_workers=min(max_workers, len(results))) as executor:
            futures = [
                executor.submit(self.scrape, r["url"], **scrape_kwargs) for r in results
            ]
            sources = [f.result() for f in as_completed(futures)]
            return self._judge(query, sources)
