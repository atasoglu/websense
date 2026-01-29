"""HTTP fetching capabilities for WebSense."""

import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Fetcher:
    """Handles HTTP requests with retry logic and custom headers."""

    def __init__(
        self, user_agent: str = "WebSense/1.0", timeout: int = 10, retries: int = 3
    ):
        """Initialize the Fetcher with HTTP session configuration.

        Args:
            user_agent: User-Agent header for requests.
            timeout: Request timeout in seconds.
            retries: Number of retry attempts for failed requests.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url: str) -> requests.Response:
        """Fetches the content of a URL.

        Args:
            url: The URL to fetch.

        Returns:
            The requests.Response object.

        Raises:
            RuntimeError: If the request fails or returns an error status.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            # We might want to log this or re-raise with a custom exception
            raise RuntimeError(f"Failed to fetch {url}: {str(e)}") from e
