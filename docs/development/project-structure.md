# Project structure

```text
GitIntel/
├── .github/
│   └── workflows/
│       ├── ci.yml              # lint, tests, package build (Python 3.11–3.14)
│       └── docs.yml            # builds and deploys this site to GitHub Pages
├── docs/                       # documentation sources (this site)
├── scripts/
│   └── bootstrap.sh            # creates .venv and installs .[dev]
├── src/
│   └── gitintel/
│       ├── __init__.py         # package version
│       ├── __main__.py         # python -m gitintel
│       ├── cli.py              # Typer app: analyze, ownership, hotspots, version
│       ├── models.py           # shared dataclasses
│       ├── analysis/
│       │   ├── pipeline.py     # AnalysisContext, analyze_repository()
│       │   ├── contributors.py
│       │   ├── ownership.py
│       │   ├── hotspots.py
│       │   └── summary.py
│       ├── git/
│       │   ├── resolver.py     # local path vs GitHub URL
│       │   ├── repository.py   # open + metadata
│       │   ├── commits.py      # HEAD walk
│       │   ├── diff.py         # per-commit file changes
│       │   ├── cache.py        # ~/.cache/gitintel clone cache
│       │   ├── clone.py        # clone with progress
│       │   └── workspace.py    # temporary directory cleanup
│       └── reports/
│           ├── terminal.py     # table, JSON and Markdown renderers
│           └── markdown.py     # placeholder
├── tests/                      # pytest suite mirroring the package
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE                     # MIT
├── Makefile                    # make setup
├── SECURITY.md
├── mkdocs.yml                  # documentation site configuration
├── pyproject.toml              # metadata, dependencies, entry points, ruff, pytest
└── README.md
```

## Where to make a change

| Task | Files to touch |
| --- | --- |
| Add or change a CLI command, option, or help text | `src/gitintel/cli.py`, `docs/reference/cli.md` |
| Change how commits or diffs are read | `src/gitintel/git/commits.py`, `git/diff.py` |
| Change repository resolution or caching | `src/gitintel/git/resolver.py`, `git/cache.py`, `git/clone.py` |
| Change a metric or scoring rule | the relevant `src/gitintel/analysis/*.py`, `docs/concepts/metrics.md` |
| Change output (any format) | `src/gitintel/reports/terminal.py`, `docs/reference/json-schema.md` |
| Add a field to a shared type | `src/gitintel/models.py` + every renderer that prints it |
| Change dependencies or entry points | `pyproject.toml` |
| Change CI | `.github/workflows/ci.yml` |
| Change this site | `docs/`, `mkdocs.yml` |

## Layering rules

- `models.py` imports nothing from the package.
- `git/` may import `models` only.
- `analysis/` may import `git` and `models`, never `reports`.
- `reports/` may import `models`, never `git` or `analysis` internals.
- `cli.py` is the only module allowed to orchestrate across layers and the only one that exits
  the process.

Keeping the metric functions free of I/O is what makes them testable with hand-built `Commit`
objects — see [Testing](testing.md).

## Packaging

`pyproject.toml` uses setuptools with automatic discovery under `src/`:

```toml
[project.scripts]
gitintel = "gitintel.cli:app"
gitit = "gitintel.cli:app"
```

Both scripts and `python -m gitintel` are the same entry point. The version lives in
`pyproject.toml` and in `src/gitintel/__init__.py`; both must be bumped together
(see [Releasing](releasing.md)).
