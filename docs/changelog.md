# Changelog

All notable changes to GitIntel are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to
[Semantic Versioning](https://semver.org/).

The canonical file is
[`CHANGELOG.md`](https://github.com/ThePhoenix77/GitIntel/blob/main/CHANGELOG.md) in the
repository; this page mirrors it. Release tags and downloadable artifacts are on the
[releases page](https://github.com/ThePhoenix77/GitIntel/releases).

## Unreleased

## [0.1.1] — 2026-09-19

### Fixed

- Remove unused pydantic dependency to reduce package size and installation overhead.
- Fix duplicated code in hotspots table rendering that was printing tables twice.
- Remove unused verbose flag infrastructure and clean up commented-out code.
- Add error context to clone failures for better debugging with exception type and message.
- Move `--quiet` flag from global to per-command for more flexible usage.

### Changed

- Removed empty `markdown.py` placeholder file and updated architecture documentation.
- Added proper module documentation to `reports/__init__.py`.
- Improved error messages with truncation for very long error messages to avoid overwhelming output.

### Added

- Comprehensive test coverage: added 59 new tests (from 6 to 65 total tests).
- Test coverage improved from 30% to 53% overall.
- Added complete test suite for hotspots scoring algorithm (18 tests).
- Added repository metadata extraction tests (11 tests).
- Added cache functionality tests (11 tests).
- Added error handling tests (19 tests).
- Tests now cover boundary conditions, edge cases, and error paths.

## [0.1.0] — 2026-08-11

### Added

- Initial public release of GitIntel.
- CLI commands: `analyze`, `ownership`, and `hotspots`.
- Output formats: `table`, `json`, and `markdown`.
- Local virtual environment development workflow (`make setup`).
- GitHub Actions CI across multiple Python versions.
- Release documentation and contributing guide.

## Known issues

Behaviour present in the current release that is documented but not yet fixed:

| Issue | Impact | Workaround |
| --- | --- | --- |
| No `.mailmap` support | One person with several emails counts as several contributors | Normalise author emails in history |
| Cached remote clones are never refreshed | Stale results for GitHub URLs | `rm -rf ~/.cache/gitintel/owner__repo` |
| Empty repositories raise a traceback | Crash instead of a friendly error | Analyze a repository with at least one commit |

## Writing changelog entries

Every user-visible change needs an entry under `Unreleased` in one of the standard groups:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Write for someone upgrading:
what changed, and what they need to do about it.

The mechanics of turning `Unreleased` into a version section are in
[Releasing](development/releasing.md); the policy behind version numbers is in
[Versioning and releases](releases.md).
