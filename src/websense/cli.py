"""Command-line interface for WebSense."""

import json
import sys
from pathlib import Path

import rich_click as click
from ask2api import Config

from .cleaner import Cleaner
from .fetcher import Fetcher
from .parser import Parser
from .scraper import Scraper


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


def parse_json_input(value: str) -> dict:
    """Parse JSON from either a raw string or a file path."""
    # First, try to parse as raw JSON string
    try:
        if value.strip().startswith(("{", "[")):
            return json.loads(value)
    except json.JSONDecodeError:
        pass

    # If not a JSON string, try to treat as file path
    path = Path(value)
    if path.exists():
        if path.is_file():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise click.ClickException(f"Invalid JSON in file {value}: {e}")
            except Exception as e:
                raise click.ClickException(f"Error reading file {value}: {str(e)}")
        else:
            raise click.ClickException(f"Path exists but is not a file: {value}")

    # If not a file, try to parse as raw JSON one last time
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # If it's not JSON and not a file, raise a clear error
        raise click.ClickException(
            f"Input is neither a valid JSON string nor an existing file: {value}"
        )


def _init_scraper(model, timeout, retries, user_agent) -> Scraper:
    """Initialize Scraper with custom settings."""
    config = Config.from_env()
    if model:
        config.model = model

    scraper = Scraper.__new__(Scraper)
    scraper.fetcher = Fetcher(user_agent=user_agent, timeout=timeout, retries=retries)
    scraper.cleaner = Cleaner()
    scraper.parser = Parser(config)
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
    if verbose:
        print_header()
        print_info(f"Target URL: {url}")
        print_info(f"Format: {'plain text' if kwargs['no_markdown'] else 'markdown'}")
        styled_echo("")

    try:
        fetcher = Fetcher(
            user_agent=kwargs["user_agent"],
            timeout=kwargs["timeout"],
            retries=kwargs["retries"],
        )
        if verbose:
            styled_echo("⟳ Fetching content...", "yellow")

        response = fetcher.fetch(url)
        cleaner = Cleaner()
        result = (
            cleaner.to_text(response.text)
            if kwargs["no_markdown"]
            else cleaner.to_markdown(response.text)
        )

        _handle_output(
            result, kwargs["output"], verbose, "📄 Content", "Content saved to"
        )
        if verbose:
            print_success("Content extraction complete!")

    except Exception as e:
        print_error(str(e) if isinstance(e, RuntimeError) else f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
