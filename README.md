# WebSense

[![CI](https://github.com/atasoglu/websense/actions/workflows/test.yml/badge.svg)](https://github.com/atasoglu/websense/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/websense)](https://pypi.org/project/websense/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Making sense of the web."**

WebSense is a Python library that transforms raw websites into structured, meaningful data. It leverages AI through the [ask2api](https://github.com/atasoglu/ask2api) library to semantically understand page content, allowing you to extract complex data structures without writing brittle CSS selectors or XPath expressions.

## Features

- **Semantic Understanding**: Uses LLMs to interpret content meaning, not just match patterns
- **Resilient**: Adapts to layout changes—if the meaning is there, WebSense finds it
- **Minimalist API**: Extract data in 3 lines of code
- **Auto-Cleaning**: Intelligent noise removal filters focus on meaningful content
- **Flexible Schemas**: Use JSON schemas or provide examples for schema inference
- **Web Search Integration**: Search the web and scrape top results in one go
- **Multi-Source Consolidation**: Aggregate information from multiple websites into one structured result
- **Modular Design**: Fetch, search, clean, and parse stages can be customized independently

## Installation

```bash
pip install websense
```

For development:

```bash
git clone https://github.com/atasoglu/websense.git
cd websense
pip install -e ".[dev]"
```

## Quick Start

Extract data with just an example:

```python
from websense import Scraper

scraper = Scraper()

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

You can provide a strict JSON schema for validation:

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"},
        "in_stock": {"type": "boolean"}
    },
    "required": ["title", "price"]
}

data = scraper.scrape("https://example.com/product", schema=schema)
```
Specify a different language model for extraction:

```python
scraper = Scraper(model="gpt-4")
```

### Web Search & Consolidation

Search the web and consolidate information from the top 3 results:

```python
data = scraper.search_and_scrape(
    "latest news about SpaceX Starship",
    max_results=3,
    example={
        "status": "string",
        "last_launch": "string",
        "summary": "brief overview"
    }
)
```

WebSense intelligently crawls multiple sources and uses an LLM-based "judge" to synthesize the most accurate data from all sources.

## CLI Usage

WebSense provides a command-line interface for quick data extraction:

```bash
# Extract structured data from a webpage
websense scrape https://example.com --example schema.json --verbose

# Search the web and consolidate top 3 results
websense search-scrape "Nvidia stock performance 2024" --top-k 3 --example '{"price": "str"}'

# Search search only (returns titles and URLs)
websense search "query" --verbose

# Get cleaned content only
websense content https://example.com --output content.md
```

Available options for `scrape` command:

| Option | Description |
|--------|-------------|
| `--model, -m` | LLM model name |
| `--schema, -s` | JSON schema (file path or raw JSON string) |
| `--example, -e` | JSON example (file path or raw JSON string) |
| `--output, -o` | Output file path |
| `--timeout, -t` | Request timeout (default: 10) |
| `--retries, -r` | Retry attempts (default: 3) |
| `--verbose, -v` | Enable verbose output |

**Pro Tip**: You can pass raw JSON strings directly to the CLI:
```bash
websense scrape https://example.com -e '{"title": "string"}'
```

## How It Works

WebSense follows a three-stage pipeline:

1. **Fetch** (`fetcher.py`): Downloads and retrieves the webpage
2. **Clean** (`cleaner.py`): Removes noise and extracts meaningful text
3. **Parse** (`parser.py`): Uses AI to extract structured data based on your schema/example

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

MIT
