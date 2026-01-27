"""
News Summarizer
Demonstrates how to extract and summarize breaking news from news websites.
"""

from websense import Scraper
import json


def summarize_news(url: str):
    """
    Scrapes a news website and extracts headline information with summaries.

    Args:
        url: The URL of the news website or article.
    """
    print(f"Fetching news from {url}...\n")
    scraper = Scraper()

    try:
        data = scraper.scrape(
            url,
            example={
                "news": [
                    {
                        "headline": "string",
                        "summary": "brief 2-3 sentence summary",
                        "publication_date": "date or timestamp",
                        "category": "news category (politics, tech, sports, etc.)",
                    }
                ]
            },
        )

        print("--- Breaking News ---\n")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Example: BBC News
    summarize_news("https://www.bbc.com/news")
