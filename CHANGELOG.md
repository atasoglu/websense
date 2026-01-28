# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
