# Contributing to GitIntel

Thank you for your interest in contributing to GitIntel! This guide explains how to collaborate on the project in a way that keeps contributions consistent, high quality, and easy to review.

## Getting Started

1. Fork the repository on GitHub.
2. Create a new branch for your work:

```bash
git checkout -b feature/describe-your-change
```

3. Keep your branch focused on a single feature, bug fix, or documentation update.

## Development Setup

Install the project in editable mode inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m pytest -q
```

Run the same lint check used by CI:

```bash
python -m ruff check src tests
```

## Code Style

- Keep code readable, idiomatic, and consistent with existing project style.
- Use descriptive names and avoid overly complex functions.
- Document public behavior with docstrings when appropriate.

## Testing

Before submitting a pull request, ensure:

- All existing tests pass
- New features or bug fixes include tests when applicable
- The code changes are covered by tests for the expected behavior

## Documentation

- Update `README.md` and the documentation site under `docs/` when adding or modifying functionality.
- Preview the site locally with `python -m pip install -r docs/requirements.txt && mkdocs serve`, and validate it with `mkdocs build --strict` before opening a pull request.
- Keep examples clear and concise.

## Pull Request Guidelines

When you open a PR, include:

- A short summary of the change
- The problem it solves
- Test coverage and verification steps
- Any breaking changes or migration notes

## Issues and Feature Requests

If you want to propose a new feature or report a bug, please open an issue describing:

- What you expected to happen
- What actually happened
- How to reproduce the issue

## Thank You

Contributions make GitIntel better for everyone. We appreciate your help and look forward to reviewing your work.
