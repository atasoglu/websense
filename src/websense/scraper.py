from .fetcher import Fetcher
from .cleaner import Cleaner
from .parser import Parser
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
