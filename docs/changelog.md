# Changelog

All notable changes to GitIntel are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to
[Semantic Versioning](https://semver.org/).

The canonical file is
[`CHANGELOG.md`](https://github.com/ThePhoenix77/GitIntel/blob/main/CHANGELOG.md) in the
repository; this page mirrors it. Release tags and downloadable artifacts are on the
[releases page](https://github.com/ThePhoenix77/GitIntel/releases).

## Unreleased

### Added

- Documentation website built with MkDocs Material, deployed to GitHub Pages.

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
| `hotspots --format table` prints the table twice | Cosmetic | Use `--format json` or `--format markdown` |
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
