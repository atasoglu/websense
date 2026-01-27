# WebSense

> **"Making sense of the web."**

WebSense is a Python library that transforms raw websites into structured, meaningful data. It uses AI to "understand" page content, allowing you to extract complex data structures without writing brittle selectors.

## Features

- **Semantic Understanding**: Uses LLMs (`ask2api`) to interpret content, not just match patterns.
- **Resilient**: Adapts to layout changes. If the meaning is there, WebSense finds it.
- **Minimalist API**: Get results in 3 lines of code.
- **Auto-Cleaning**: Intelligent noise removal to focus on what matters.

## Installation

```bash
pip install websense
```

## Quick Start

```python
from websense import Scraper

# Initialize
scraper = Scraper()

# Scrape and Understand
data = scraper.scrape(
    "https://github.com/atasoglu/ask2api",
    example={
        "project_name": "string",
        "description": "string",
        "stars": 0,
        "is_active": True
    }
)

print(data)
```

## Advanced Usage

### Custom Schema

You can provide a strict JSON schema for validation:

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"}
    },
    "required": ["title", "price"]
}

data = scraper.scrape("https://example.com/product", schema=schema)
```
