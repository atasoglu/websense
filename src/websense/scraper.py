from .fetcher import Fetcher
from .cleaner import Cleaner
from .parser import Parser


class Scraper:
    """The main entry point for the semantic data pipeline."""

    def __init__(self, model: str = None):
        self.fetcher = Fetcher()
        self.cleaner = Cleaner()
        self.parser = Parser(model=model)

    def scrape(self, url: str, schema: dict = None, example: dict = None) -> dict:
        """
        Scrapes a URL and extracts structured data.

        Args:
            url: The URL to scrape.
            schema: Optional JSON schema dict.
            example: Optional JSON example dict to infer schema from.

        Returns:
            Extracted data as a dictionary.
        """
        # 1. Fetch
        response = self.fetcher.fetch(url)

        # 2. Clean
        content = self.cleaner.to_text(response.text)

        # 3. Extract (Parses & converts schema/example internally)
        return self.parser.extract(content, schema=schema, example=example)
