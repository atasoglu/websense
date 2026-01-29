# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-01-30

### Added
- **Web Search Integration**: New `Searcher` module using DuckDuckGo for live search capabilities.
- **Search-and-Scrape**: Seamless integration to search web and scrape top results in a single step.
- **Multi-Source Consolidation**: Advanced feature to crawl multiple sources and synthesize them into one structured response using LLM.
- **CLI Search Commands**: Added `search` and `search-scrape` commands to terminal interface.
- **New Examples**: Added `multi_source_consolidation.py` and news extraction examples.

### Changed
- **Architectural Cleanup**: Simplified `Searcher` and `Scraper` classes for better modularity.
- **Improved Test Coverage**: Reached 99% code coverage with robust test suites for search and consolidation.
- **Robustness**: Improved error handling for network issues and empty search results.

### Fixed
- Fixed crash in `search_and_scrape` when `extract_kwargs` was missing.
- Fixed linting and pre-commit errors across the codebase.

## [0.3.0] - 2026-01-28

### Added
- **CLI module**: New command-line interface with `websense scrape` and `websense content` commands
- Full parameter support via CLI options: `--model`, `--timeout`, `--retries`, `--user-agent`, etc.
- Colorful, minimal CLI output with progress indicators
- `rich-click` dependency for CLI functionality


## [0.2.0] - 2026-01-28

### Added
- **Markdown output support**: Web content can now be exported as Markdown using `markdownify`
- GitHub Actions workflows for pre-commit checks and PyPI publishing
- Advanced configuration examples

### Changed
- Refactored `cleaner.py` module for improved maintainability
- Enhanced docstrings across all modules for better documentation
- Improved test coverage to 100%

### Fixed
- Author name formatting in `pyproject.toml`

## [0.1.1] - 2026-01-28

### Fixed
- Fixed author metadata display in package metadata

## [0.1.0] - 2026-01-27

### Added
- Initial release of websense
- Core scraper module for web data extraction
- Parser module for content processing
- Cleaner module for data cleaning
- Fetcher module for HTTP requests
- Comprehensive test suite
