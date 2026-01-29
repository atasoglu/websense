"""HTML cleaning and normalization for WebSense."""

from bs4 import BeautifulSoup

from markdownify import markdownify as md
from typing import Iterable


class Cleaner:
    """Handles the extraction of 'meaningful' text from HTML."""

    NOISE = {
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "noscript",
        "iframe",
        "svg",
    }

    def __init__(self, noisy_elements: Iterable[str] | None = None) -> None:
        """Initialize the Cleaner with optional custom noisy elements.

        Args:
            noisy_elements: HTML tags to remove. Defaults to NOISE class attribute.
        """
        self.noise = set(noisy_elements or []) or self.NOISE

    def preprocess(self, html: str) -> BeautifulSoup:
        """Parse HTML and remove noisy elements.

        Args:
            html: Raw HTML content.

        Returns:
            BeautifulSoup object with noisy elements removed.
        """
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(self.noise):
            tag.decompose()

        return soup

    def to_text(self, html: str) -> str:
        """Strips non-content tags and normalizes whitespace.

        Args:
            html: Raw HTML content.

        Returns:
            Normalized plain text content.
        """
        soup = self.preprocess(html)
        # Get text and clean up whitespace
        lines = (line.strip() for line in soup.get_text(separator="\n").splitlines())
        return "\n".join(line for line in lines if line)

    def to_markdown(self, html: str) -> str:
        """Converts HTML to Markdown format for better LLM comprehension.

        Args:
            html: Raw HTML content.

        Returns:
            Markdown formatted content.
        """

        soup = self.preprocess(html)
        return md(str(soup), heading_style="ATX")
