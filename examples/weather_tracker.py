"""
Weather Status Tracker
Demonstrates how to extract weather information and forecasts from weather websites.
"""

from websense import Scraper
import json


def fetch_weather_status(url: str, location: str = None):
    """
    Scrapes a weather website and extracts current weather and forecast data.

    Args:
        url: The URL of the weather website.
        location: Optional location name (for context).
    """
    location_text = f" for {location}" if location else ""
    print(f"Fetching weather status{location_text}...\n")
    scraper = Scraper()

    try:
        data = scraper.scrape(
            url,
            example={
                "location": "city or region name",
                "current_temperature": "number with unit (e.g., 25°C)",
                "condition": "weather description (sunny, rainy, cloudy, etc.)",
                "humidity": "percentage",
                "wind_speed": "speed with unit",
                "air_quality": "air quality index or status",
                "forecast": [
                    {
                        "day": "day of week or date",
                        "high_temp": "number",
                        "low_temp": "number",
                        "condition": "weather description",
                    }
                ],
            },
        )

        print("--- Weather Status ---\n")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Example: Weather.com
    fetch_weather_status(
        "https://weather.com/weather/today/l/USNY0996:1:US", location="New York"
    )
