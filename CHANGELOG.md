# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/).


## [0.1.1] - 2026-09-19
### Fixed
- Remove unused pydantic dependency to reduce package size and installation overhead
- Fix duplicated code in hotspots table rendering that was printing tables twice
- Remove unused verbose flag infrastructure and clean up commented-out code
- Add error context to clone failures for better debugging with exception type and message
- Move `--quiet` flag from global to per-command for more flexible usage

### Changed
- Removed empty `markdown.py` placeholder file and updated architecture documentation
- Added proper module documentation to `reports/__init__.py`
- Improved error messages with truncation for very long error messages to avoid overwhelming output

### Added
- Comprehensive test coverage: added 59 new tests (from 6 to 65 total tests)
- Test coverage improved from 30% to 53% overall
- Added complete test suite for hotspots scoring algorithm (18 tests)
- Added repository metadata extraction tests (11 tests) 
- Added cache functionality tests (11 tests)
- Added error handling tests (19 tests)
- Tests now cover boundary conditions, edge cases, and error paths

## [0.1.0] - 2026-08-11
### Added
- Initial public release of GitIntel
- CLI commands: `analyze`, `ownership`, and `hotspots`
- Support for output formats: `table`, `json`, and `markdown`
- Local virtual environment development workflow
- GitHub Actions CI for multiple Python versions
- Release documentation and contributing guide
