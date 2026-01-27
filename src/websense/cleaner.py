from bs4 import BeautifulSoup


class Cleaner:
    """Handles the extraction of 'meaningful' text from HTML."""

    @staticmethod
    def to_text(html: str) -> str:
        """Strips non-content tags and normalizes whitespace."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove noisy elements
        for noise in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "noscript",
                "iframe",
                "svg",
            ]
        ):
            noise.decompose()

        # Get text and clean up whitespace
        lines = (line.strip() for line in soup.get_text(separator="\n").splitlines())
        return "\n".join(line for line in lines if line)
