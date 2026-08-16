# Testing

## Running the suite

```bash
python -m pytest -q                              # quick run
python -m pytest --cov --cov-report=term-missing # what CI runs
python -m pytest tests/test_ownership.py -v      # one file
python -m pytest -k ownership                    # by name
```

Configuration lives in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["gitintel"]
```

Coverage is branch-based over the `gitintel` package, with covered files skipped in the report.
There is no minimum coverage gate — CI fails on test failures, not on coverage numbers.

## Current suite

| File | Covers | Status |
| --- | --- | --- |
| `test_cli.py` | `--version`, `python -m gitintel --help` via Typer's `CliRunner` | 2 tests |
| `test_commits.py` | `get_commits()` against the checked-out repository | 1 test |
| `test_contributors.py` | `analyze_contributors()` | 1 test |
| `test_diff.py` | per-commit `FileChange` extraction | 1 test |
| `test_ownership.py` | `analyze_ownership()` | 1 test |
| `test_hotspots.py` | — | **empty** |
| `test_repository.py` | — | **empty** |

The two empty files are deliberate placeholders and are the easiest useful contribution to the
project: `calculate_hotspots()` is a pure function and needs no repository at all.

## Two kinds of test

### Pure domain tests (preferred)

Analysis functions take lists of dataclasses, so they can be tested without touching Git:

```python
from datetime import datetime

from gitintel.analysis.hotspots import calculate_hotspots
from gitintel.models import Commit, FileChange


def test_no_owner_adds_risk():
    commits = [
        Commit(
            hash="a" * 40,
            author="Alice",
            email="alice@example.com",
            message="change",
            date=datetime(2026, 1, 1),
            changes=[FileChange(path="src/app.py", additions=10, deletions=2)],
        )
    ]

    changes = {
        "src/app.py": {
            "modifications": 25,
            "lines_changed": 1200,
            "contributors": 3,
        }
    }

    hotspots = calculate_hotspots(commits, changes, ownership_map={})

    assert hotspots[0].file_path == "src/app.py"
    assert "No clear owner" in hotspots[0].reasons
```

Build the exact inputs a rule needs and assert on the score and reasons. Threshold values are
documented in [Metrics and scoring](../concepts/metrics.md#hotspot-risk-score).

### Repository-backed tests

The existing Git-layer tests open `"."` — the GitIntel checkout itself — and assert on shapes
rather than values:

```python
repository = open_repository(".")
commits = get_commits(repository)

assert len(commits) > 0
```

Never assert on real commit counts, author names, or hashes: they change with every merge and
CI checks out a different history depth than your machine. For value-level assertions, create a
throwaway repository instead:

```python
import pygit2
import pytest


@pytest.fixture
def repository(tmp_path):
    repo = pygit2.init_repository(tmp_path / "repo")
    signature = pygit2.Signature("Alice", "alice@example.com")

    (tmp_path / "repo" / "app.py").write_text("print('hi')\n")
    repo.index.add("app.py")
    repo.index.write()

    repo.create_commit(
        "HEAD", signature, signature, "initial", repo.index.write_tree(), []
    )

    return repo
```

!!! warning "CI clones are shallow-ish"
    `actions/checkout@v4` fetches a single commit by default, so repository-backed tests must
    tolerate a history of length one. That is why the existing tests assert `> 0` rather than a
    specific count.

## Writing a new test

1. Put it in the file matching the module under test; create one if the module is new.
2. Name it `test_<behaviour>`, not `test_<function>`.
3. Prefer pure inputs; fall back to `tmp_path` repositories; use the checkout only for smoke
   tests.
4. Assert on behaviour a user could observe — a score, a reason string, an exit code — not on
   internal call order.
5. For CLI behaviour, use `CliRunner` and assert on `result.exit_code` and `result.stdout`.

## Before opening a pull request

```bash
python -m ruff check src tests
python -m pytest --cov --cov-report=term-missing
python -m build --sdist --wheel --outdir dist
python -m twine check dist/*
```

Those four commands are exactly what [CI](https://github.com/ThePhoenix77/GitIntel/blob/main/.github/workflows/ci.yml)
runs on Python 3.11 through 3.14.
