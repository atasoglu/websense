"""Command-line interface for WebSense."""

import json
import sys
from pathlib import Path

import rich_click as click
from ask2api import Config

from .cleaner import Cleaner
from .fetcher import Fetcher
from .scraper import Scraper
from .searcher import Searcher


def styled_echo(message: str, color: str = "cyan", bold: bool = False) -> None:
    """Print styled message to console."""
    click.echo(click.style(message, fg=color, bold=bold))


def print_header() -> None:
    """Print WebSense header."""
    styled_echo("━" * 50, "bright_black")
    styled_echo("  WebSense", "cyan", bold=True)
    styled_echo('  "Making sense of the web."', "bright_black")
    styled_echo("━" * 50, "bright_black")


def print_error(message: str) -> None:
    """Print error message in red."""
    styled_echo(f"✗ Error: {message}", "red", bold=True)


def print_success(message: str) -> None:
    """Print success message in green."""
    styled_echo(f"✓ {message}", "green")


def print_info(message: str) -> None:
    """Print info message in blue."""
    styled_echo(f"ℹ {message}", "blue")


def _try_parse_json(value: str) -> dict | None:
    """Try parsing as JSON, return None on failure."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _load_json_file(path: Path) -> dict:
    """Load JSON from file with error handling."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in file {path}: {e}")
    except Exception as e:
        raise click.ClickException(f"Error reading file {path}: {e}")


def parse_json_input(value: str) -> dict:
    """Parse JSON from either a raw string or a file path."""
    if value.strip().startswith(("{", "[")):
        result = _try_parse_json(value)
        if result is not None:
            return result

    path = Path(value)
    if path.is_file():
        return _load_json_file(path)
    if path.exists():
        raise click.ClickException(f"Path exists but is not a file: {value}")

    result = _try_parse_json(value)
    if result is not None:
        return result
    raise click.ClickException(
        f"Input is neither a valid JSON string nor an existing file: {value}"
    )


def _init_scraper(model, timeout, retries, user_agent) -> Scraper:
    """Initialize Scraper with custom settings.

    Args:
        model: Optional model name.
        timeout: Request timeout in seconds.
        retries: Number of retries.
        user_agent: User-Agent header string.

    Returns:
        Configured Scraper instance.
    """
    config = Config.from_env()
    if model:
        config.model = model

    scraper = Scraper(model=model, config=config)
    # Override fetcher with custom CLI settings
    scraper.fetcher = Fetcher(user_agent=user_agent, timeout=timeout, retries=retries)
    return scraper


def _handle_output(
    content: str, output: str | None, verbose: bool, header: str, success_msg: str
) -> None:
    """Handle CLI output to file or stdout."""
    if output:
        Path(output).write_text(content, encoding="utf-8")
        if verbose:
            print_success(f"{success_msg}: {output}")
    else:
        if verbose:
            styled_echo(f"\n{header}:", "cyan", bold=True)
            styled_echo("─" * 40, "bright_black")
        click.echo(content)


def _load_scrape_inputs(kwargs):
    """Load schema and example inputs from CLI arguments.

    Args:
        kwargs: CLI command keyword arguments.

    Returns:
        A tuple of (schema, example) dictionaries.
    """
    s_in, e_in = kwargs["schema_input"], kwargs["example_input"]
    if not s_in and not e_in:
        raise click.ClickException(
            "You must provide either --schema or --example (string or path)"
        )
    return (
        parse_json_input(s_in) if s_in else None,
        parse_json_input(e_in) if e_in else None,
    )


def _log_scrape_params(url, schema, example, kwargs):
    """Log the parameters used for the scrape command.

    Args:
        url: Target URL.
        schema: Loaded schema dict.
        example: Loaded example dict.
        kwargs: CLI command keyword arguments.
    """
    print_header()
    print_info(f"Target URL: {url}")
    if schema:
        src = "string" if kwargs["schema_input"].strip().startswith("{") else "file"
        print_info(f"Using schema from {src}")
    if example:
        src = "string" if kwargs["example_input"].strip().startswith("{") else "file"
        print_info(f"Using example from {src}")
    print_info(f"Model: {kwargs['model'] or 'default'}")
    print_info(f"Timeout: {kwargs['timeout']}s | Retries: {kwargs['retries']}")
    styled_echo("")


@click.group()
@click.version_option(package_name="websense")
def main() -> None:
    """WebSense - AI-powered web scraping CLI.

    Extract structured data from any webpage using AI.
    """
    pass


@main.command()
@click.argument("url")
@click.option("--model", "-m", help="LLM model name (e.g., gpt-4, claude-3)")
@click.option(
    "--schema", "-s", "schema_input", help="JSON schema (raw string or file path)"
)
@click.option(
    "--example", "-e", "example_input", help="JSON example (raw string or file path)"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (stdout if not specified)",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Request timeout in seconds [default: 10]",
)
@click.option(
    "--retries", "-r", type=int, default=3, help="Number of retry attempts [default: 3]"
)
@click.option("--user-agent", default="WebSense/1.0", help="Custom User-Agent header")
@click.option(
    "--no-markdown", is_flag=True, help="Disable markdown conversion (use plain text)"
)
@click.option(
    "--truncate-length",
    type=int,
    default=12000,
    help="Max content length for extraction [default: 12000]",
)
@click.option("--prompt", "-p", help="Custom extraction prompt")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def scrape(url: str, **kwargs) -> None:
    """Scrape URL and extract structured data."""
    verbose = kwargs["verbose"]
    schema, example = _load_scrape_inputs(kwargs)

    if verbose:
        _log_scrape_params(url, schema, example, kwargs)

    try:
        scraper = _init_scraper(
            kwargs["model"], kwargs["timeout"], kwargs["retries"], kwargs["user_agent"]
        )
        if verbose:
            styled_echo("⟳ Fetching and extracting...", "yellow")

        result = scraper.scrape(
            url,
            schema=schema,
            example=example,
            convert_markdown=not kwargs["no_markdown"],
            extract_kwargs={
                "truncate_length": kwargs["truncate_length"],
                "prompt": kwargs["prompt"],
            },
        )

        _handle_output(
            json.dumps(result, indent=2, ensure_ascii=False),
            kwargs["output"],
            verbose,
            "📦 Result",
            "Result saved to",
        )
        if verbose:
            print_success("Extraction complete!")

    except Exception as e:
        print_error(str(e) if isinstance(e, RuntimeError) else f"Unexpected error: {e}")
        sys.exit(1)


@main.command()
@click.argument("url")
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Request timeout in seconds [default: 10]",
)
@click.option(
    "--retries", "-r", type=int, default=3, help="Number of retry attempts [default: 3]"
)
@click.option("--user-agent", default="WebSense/1.0", help="Custom User-Agent header")
@click.option(
    "--no-markdown", is_flag=True, help="Output plain text instead of markdown"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (stdout if not specified)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def content(url: str, **kwargs) -> None:
    """Fetch and clean webpage content."""
    verbose = kwargs["verbose"]
    _log_content_params(url, kwargs) if verbose else None

    try:
        result = _fetch_content(url, kwargs)
        _handle_output(
            result, kwargs["output"], verbose, "📄 Content", "Content saved to"
        )
        print_success("Content extraction complete!") if verbose else None
    except Exception as e:
        _handle_error(e)


def _log_content_params(url: str, kwargs: dict) -> None:
    """Log the parameters used for the content command.

    Args:
        url: Target URL.
        kwargs: CLI command keyword arguments.
    """
    print_header()
    print_info(f"Target URL: {url}")
    print_info(f"Format: {'plain text' if kwargs['no_markdown'] else 'markdown'}")
    styled_echo("")
    styled_echo("⟳ Fetching content...", "yellow")


def _fetch_content(url: str, kwargs: dict) -> str:
    """Fetch and clean content from a URL.

    Args:
        url: Target URL.
        kwargs: CLI command keyword arguments.

    Returns:
        Cleaned content as string.
    """
    fetcher = Fetcher(
        user_agent=kwargs["user_agent"],
        timeout=kwargs["timeout"],
        retries=kwargs["retries"],
    )
    response = fetcher.fetch(url)
    cleaner = Cleaner()
    return (
        cleaner.to_text(response.text)
        if kwargs["no_markdown"]
        else cleaner.to_markdown(response.text)
    )


def _handle_error(e: Exception) -> None:
    """Handle and print exceptions before exiting.

    Args:
        e: The exception to handle.
    """
    print_error(str(e) if isinstance(e, RuntimeError) else f"Unexpected error: {e}")
    sys.exit(1)


@main.command()
@click.argument("query")
@click.option(
    "--max-results",
    "-n",
    type=int,
    default=5,
    help="Maximum number of results [default: 5]",
)
@click.option(
    "--region",
    "-R",
    default="wt-wt",
    help="DuckDuckGo region code [default: wt-wt (worldwide)]",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (stdout if not specified)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def search(query: str, **kwargs) -> None:
    """Search the web for a query."""
    verbose = kwargs["verbose"]
    if verbose:
        print_header()
        print_info(f"Search query: {query}")
        print_info(f"Max results: {kwargs['max_results']}")
        print_info(f"Region: {kwargs['region']}")
        styled_echo("")

    try:
        searcher = Searcher()
        if verbose:
            styled_echo("⟳ Searching...", "yellow")

        results = searcher.search(
            query, max_results=kwargs["max_results"], region=kwargs["region"]
        )

        _handle_output(
            json.dumps(results, indent=2, ensure_ascii=False),
            kwargs["output"],
            verbose,
            "🔍 Search Results",
            "Results saved to",
        )
        if verbose:
            print_success(f"Found {len(results)} results!")

    except Exception as e:
        print_error(str(e) if isinstance(e, RuntimeError) else f"Unexpected error: {e}")
        sys.exit(1)


@main.command("search-scrape")
@click.argument("query")
@click.option("--model", "-m", help="LLM model name (e.g., gpt-4, claude-3)")
@click.option(
    "--schema", "-s", "schema_input", help="JSON schema (raw string or file path)"
)
@click.option(
    "--example", "-e", "example_input", help="JSON example (raw string or file path)"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (stdout if not specified)",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Request timeout in seconds [default: 10]",
)
@click.option(
    "--retries", "-r", type=int, default=3, help="Number of retry attempts [default: 3]"
)
@click.option("--user-agent", default="WebSense/1.0", help="Custom User-Agent header")
@click.option(
    "--no-markdown", is_flag=True, help="Disable markdown conversion (use plain text)"
)
@click.option(
    "--truncate-length",
    type=int,
    default=12000,
    help="Max content length for extraction [default: 12000]",
)
@click.option("--prompt", "-p", help="Custom extraction prompt")
@click.option(
    "--top-k",
    "-k",
    type=int,
    default=1,
    help="Number of top results to scrape and consolidate [default: 1]",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def search_scrape(query: str, **kwargs) -> None:
    """Search web, scrape top-k results, and extract consolidated structured data."""
    verbose, top_k = kwargs["verbose"], kwargs["top_k"]
    schema, example = _load_scrape_inputs(kwargs)

    _log_search_scrape_params(
        query, top_k, schema, example, kwargs
    ) if verbose else None

    try:
        scraper = _init_scraper(
            kwargs["model"], kwargs["timeout"], kwargs["retries"], kwargs["user_agent"]
        )
        _log_search_start(top_k) if verbose else None

        result = scraper.search_and_scrape(
            query,
            schema=schema,
            example=example,
            convert_markdown=not kwargs["no_markdown"],
            extract_kwargs={
                "truncate_length": kwargs["truncate_length"],
                "prompt": kwargs["prompt"],
            },
            max_results=top_k,
        )

        _log_sources(result["sources"]) if verbose else None
        _handle_output(
            json.dumps(result, indent=2, ensure_ascii=False),
            kwargs["output"],
            verbose,
            "📦 Consolidated Result",
            "Result saved to",
        )
        print_success("Search and extraction complete!") if verbose else None
    except Exception as e:
        _handle_error(e)


def _log_search_scrape_params(
    query: str, top_k: int, schema, example, kwargs: dict
) -> None:
    """Log the parameters used for the search-scrape command.

    Args:
        query: Search query.
        top_k: Number of sources.
        schema: Loaded schema dict.
        example: Loaded example dict.
        kwargs: CLI command keyword arguments.
    """
    print_header()
    print_info(f"Search query: {query}")
    print_info(f"Top-K sources: {top_k}")
    if schema:
        print_info(
            f"Using schema from {'string' if kwargs['schema_input'].strip().startswith('{') else 'file'}"
        )
    if example:
        print_info(
            f"Using example from {'string' if kwargs['example_input'].strip().startswith('{') else 'file'}"
        )
    print_info(f"Model: {kwargs['model'] or 'default'}")
    print_info(f"Timeout: {kwargs['timeout']}s | Retries: {kwargs['retries']}")
    styled_echo("")


def _log_search_start(top_k: int) -> None:
    """Log the start of a multi-source search.

    Args:
        top_k: Number of sources to search.
    """
    msg = (
        f"⟳ Searching and extracting from {top_k} sources..."
        if top_k > 1
        else "⟳ Searching and extracting..."
    )
    styled_echo(msg, "yellow")


def _log_sources(sources: list[dict]) -> None:
    """Log the status of individual sources scraped.

    Args:
        sources: List of dictionaries containing scrape status.
    """
    successful = sum(1 for s in sources if s["success"])
    print_info(f"Successfully scraped {successful}/{len(sources)} sources")
    for src in sources:
        status, color = ("✓", "green") if src["success"] else ("✗", "red")
        styled_echo(f"  {status} {src['url'][:60]}...", color)
    styled_echo("")


if __name__ == "__main__":
    main()
