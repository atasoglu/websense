from websense import Scraper


def main():
    print("Initializing WebSense...")
    scraper = Scraper()

    url = "https://github.com/atasoglu/ask2api"
    print(f"Scraping {url}...")

    try:
        data = scraper.scrape(
            url,
            example={
                "project_name": "string",
                "description": "brief summary",
                "latest_version": "string",
                "topics": ["topic tags"],
                "stars": 0,
            },
        )

        print("\n--- Extracted Data ---\n")
        import json

        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
