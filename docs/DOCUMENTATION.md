# GitIntel Documentation

## Overview

GitIntel is a command-line tool that analyzes Git repositories and provides insights into commit history, owner activity, and file hotspots.

## Architecture

- `src/gitintel/cli.py` — CLI entrypoint and command definitions using Typer.
- `src/gitintel/git/` — repository access, commit loading, diff generation, and temporary workspace handling.
- `src/gitintel/analysis/` — domain logic for repository analysis, contributor ownership, and hotspot detection.
- `src/gitintel/reports/` — presentation layer for terminal and markdown output.

## Commands

- `analyze` — perform a full repository analysis and print summary reports.
- `ownership` — compute file ownership and contributor impact metrics.
- `hotspots` — detect risky files and concentrated contribution areas.

## Development

Use the existing virtual environment and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m pytest -q
```

## Release Notes

This documentation is intended as a reference companion to the `README.md` and GitHub release notes.
