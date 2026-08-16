
<h1 align="center">
<img width="300" alt="gitintel" src="https://github.com/user-attachments/assets/5327bb01-3abd-4afc-a2f4-b610f07de11f" />
</h1><br>

[![CI](https://img.shields.io/github/actions/workflow/status/ThePhoenix77/GitIntel/ci.yml?branch=main&logo=github&label=CI)](https://github.com/ThePhoenix77/GitIntel/actions?query=branch%3Amain+workflow%3ACI)
[![PyPI](https://img.shields.io/pypi/v/gitintel.svg)](https://pypi.org/project/gitintel)
[![Python Version](https://img.shields.io/pypi/pyversions/gitintel.svg)](https://pypi.org/project/gitintel)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-thephoenix77.github.io%2FGitIntel-blue)](https://thephoenix77.github.io/GitIntel/)

**Documentation: <https://thephoenix77.github.io/GitIntel/>**

GitIntel is a command-line repository intelligence tool that helps developers understand repository history, ownership, and risk hotspots.

## Overview

GitIntel analyzes commit history, contributor contributions, and file ownership to help teams make informed maintenance and review decisions.

## Key Features

- Analyze Git history and contributor activity across a repository
- Report file ownership by modifications, lines changed, and last touch
- Identify hotspot files with risk and contributor concentration insights
- Export reports as `table`, `json`, or `markdown`
- Support local repositories and remote GitHub URLs
- Provide a lightweight alias: `gitit`

## Installation

### From PyPI

For the recommended command-line installation, use [pipx](https://pipx.pypa.io/):

```bash
pipx install gitintel
```

This makes `gitintel` available globally without requiring you to activate a
virtual environment.

Alternatively, install with pip:

```bash
python -m pip install gitintel
```

### From source

```bash
git clone git@github.com:ThePhoenix77/GitIntel.git
cd GitIntel
python -m pip install -e .
```


## Quick setup

For development, create a Python 3.11+ virtual environment and install the developer tools:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The convenience script is also available:

```bash
make setup
```

## Quick Start

Analyze a repository:

```bash
gitintel analyze .
```

Use the alias:

```bash
gitit analyze .
```

No account or configuration is required. Run `gitintel --help` to see all commands,
or pass a GitHub repository URL directly:

```bash
gitintel hotspots https://github.com/ThePhoenix77/GitIntel
```

## CLI Reference

### `analyze`

Analyze repository history and summary metrics.

```bash
gitintel analyze <path> [--format table|json|markdown]
```

Example:

```bash
gitintel analyze . --format markdown
```

### `ownership`

Inspect file ownership and contributor activity.

```bash
gitintel ownership <path> [--all] [--file <path>] [--format table|json|markdown]
```

Examples:

```bash
gitintel ownership .
gitintel ownership . --all
gitintel ownership . --file src/gitintel/cli.py --format markdown
```

### `hotspots`

Identify hotspot files that may need review.

```bash
gitintel hotspots <path> [--format table|json|markdown]
```

Example:

```bash
gitintel hotspots . --format json
```

## Options

- `--format`, `-f` — Output format: `table`, `json`, or `markdown`
- `--all` — Include all ownership results instead of the default top files
- `--file` — Filter ownership results to a specific file path
- `--quiet`, `-q` — Suppress progress output

## Development

Create and activate a local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run tests:

```bash
python -m pytest -q
```

## Project Structure

- `src/gitintel/cli.py` — CLI entrypoint and command definitions
- `src/gitintel/git/` — Git repository access, diffs, and commit resolution
- `src/gitintel/analysis/` — analysis pipeline, ownership, and hotspot logic
- `src/gitintel/reports/` — terminal and markdown reporting

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a descriptive feature branch
3. Open a pull request with tests and examples

Read the full contribution guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License. See `LICENSE` for details.
