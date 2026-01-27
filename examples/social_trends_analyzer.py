"""
Social Trends Analyzer
Demonstrates how to extract trending topics and social media insights from various platforms.
"""

from websense import Scraper
import json


def analyze_social_trends(url: str, platform: str = None):
    """
    Scrapes social media or trend websites and extracts trending topics and metrics.

    Args:
        url: The URL to scrape for trending information.
        platform: Optional platform name (Twitter, TikTok, Reddit, etc.).
    """
    platform_text = f" from {platform}" if platform else ""
    print(f"Analyzing social trends{platform_text}...\n")
    scraper = Scraper()

    try:
        data = scraper.scrape(
            url,
            example={
                "trending_topics": [
                    {
                        "rank": 1,
                        "topic": "topic or hashtag name",
                        "post_count": 0,
                        "engagement": "number of likes/shares/comments",
                        "sentiment": "positive, negative, or neutral",
                    }
                ],
                "trending_category": "category of trends (entertainment, politics, sports, etc.)",
                "timeframe": "real-time, last 24 hours, etc.",
                "growth_rate": "trending up or down",
            },
        )

        print("--- Social Trends ---\n")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # For demonstration, using a news aggregator that shows trending stories
    analyze_social_trends("https://news.ycombinator.com/", platform="Hacker News")
