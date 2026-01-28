"""
Advanced Configuration Example
Demonstrates all configurable options for scraping with WebSense.
"""

import os
from ask2api import Config
from websense.fetcher import Fetcher
from websense.cleaner import Cleaner
from websense.parser import Parser
import json

# --- 1. Custom Fetcher Configuration ---
fetcher = Fetcher(
    user_agent="MyBot/2.0 (contact@example.com)",  # Custom User-Agent
    timeout=15,  # Request timeout (seconds)
    retries=5,  # Retry attempts for failed requests
)

# --- 2. Custom Cleaner Configuration ---
cleaner = Cleaner(
    # HTML tags to remove
    noisy_elements={
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "noscript",
        "iframe",
        "svg",
        "ads",
        "banner",
        "popup",
    }
)

# --- 3. Custom Parser Configuration ---
config = Config(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="minimax/minimax-m2",
    temperature=0.5,
)
parser = Parser(config=config)

# --- 4. Using Components Individually ---
url = "https://news.ycombinator.com"

# Fetch
response = fetcher.fetch(url)

# Clean (choose output format)
markdown_content = cleaner.to_markdown(response.text)
# text_content = cleaner.to_text(response.text)    # Alternative: plain text

# Use example-based schema
example = {
    "articles": [
        {
            "title": "string",
            "url": "string",
            "points": 0,
            "comments": 0,
        }
    ],
    "top_story": "string",
}

# Setup the extract arguments
extract_kwargs = dict(
    truncate=True,  # Truncate long content
    truncate_length=10000,  # Max characters to send to LLM
    prompt="Extract the top stories from Hacker News.",  # Custom prompt
)

# Parse with custom extraction options
data = parser.extract(
    content=markdown_content,
    example=example,
)

print("\n--- Extracted Data ---")
print(json.dumps(data, indent=2))


# --- 5. Alternative: Using Scraper with Config ---
# For simpler use cases, pass config directly to Scraper
# from websense import Scraper

# scraper = Scraper(config=config)

# data = scraper.scrape(
#     url=url,
#     example=example,
#     convert_markdown=True,
#     extract_kwargs=extract_kwargs,
# )

# print("\n--- Extracted Data (alternative way) ---")
# print(json.dumps(data, indent=2))
