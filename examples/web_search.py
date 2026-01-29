import json
from websense import Scraper


def main():
    query = "today's top news stories"
    prompt = f"""
The user searched for: '{query}'. Extract the relevant data from this webpage.
Extract structured data from the following webpage content.
If the page is not relevant, set quality to 'poor'.
If the page is relevant, set quality to 'good' and extract the data."""

    scraper = Scraper(model="gpt-4.1-mini")
    result = scraper.search_and_scrape(
        query,
        example={
            "page": {"title": "string", "summary": "string", "quality": "str"},
            "news_highlights": ["string"],
        },
        extract_kwargs={"prompt": prompt},
        max_results=3,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
