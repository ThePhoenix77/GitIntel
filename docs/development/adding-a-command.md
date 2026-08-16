# Adding a command

A worked example: adding `gitintel churn`, which lists the files with the most lines changed.
The same seven steps apply to any new command.

## 1. Decide which layer owns the logic

Ask what the command needs:

| Need | Layer | Example |
| --- | --- | --- |
| New Git data (tags, branches, blame) | `git/` | a `get_tags()` in a new `git/tags.py` |
| A new metric over existing commits | `analysis/` | `analysis/churn.py` |
| A new view over existing metrics | `reports/` | `print_churn_*()` |

`churn` only re-shapes data the pipeline already has, so it needs a small analysis function and
three renderers.

## 2. Write the analysis function

Keep it pure — lists in, list out, no I/O:

```python
# src/gitintel/analysis/churn.py
from gitintel.models import Commit


def analyze_churn(commits: list[Commit]) -> list[tuple[str, int]]:
    totals: dict[str, int] = {}

    for commit in commits:
        for change in commit.changes:
            totals[change.path] = (
                totals.get(change.path, 0) + change.additions + change.deletions
            )

    return sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )
```

If the result should be reusable by other commands, expose it as a lazy property on
`AnalysisContext` instead:

```python
@property
def churn(self) -> list[tuple[str, int]]:
    if self._churn is None:
        self._churn = analyze_churn(self.commits)
    return self._churn
```

Remember to add the matching `_churn: list[tuple[str, int]] | None = field(default=None, init=False)`
declaration to the dataclass.

## 3. Add the renderers

In `src/gitintel/reports/terminal.py`, follow the existing dispatcher pattern — one entry point
plus one function per format:

```python
def print_churn(churn, output_format: str = "table") -> None:
    fmt = output_format.lower()

    if fmt == "json":
        print_churn_json(churn)
    elif fmt == "markdown":
        print_churn_markdown(churn)
    else:
        print_churn_table(churn)
```

All three formats are required — do not ship a command that only prints a table.

## 4. Register the CLI command

In `src/gitintel/cli.py`, mirror the structure of `hotspots`:

```python
@app.command()
def churn(
    source: str = typer.Argument(".", help="Repository path or GitHub URL"),
    format: str = typer.Option("table", "--format", "-f", help="table | json | markdown"),
) -> None:
    """Show the files with the most lines changed."""
    context = None

    try:
        repository, context = run_with_progress(
            "Preparing repository...",
            resolve_repository,
            source,
        )

        analysis = run_with_progress(
            "Building analysis pipeline...",
            analyze_repository,
            repository,
            context,
        )

        print_churn(analysis.churn, output_format=format)

    except ValueError as error:
        handle_error(error)

    finally:
        if context and context.temporary:
            cleanup_repository(context.path)
```

Non-negotiables:

- convert user-fixable problems to `ValueError` and let `handle_error()` render them,
- clean up temporary clones in `finally`,
- use `run_with_progress()` so `--quiet` is honoured,
- accept the same `--format` values as the other commands.

## 5. Test it

```python
# tests/test_churn.py
from datetime import datetime

from gitintel.analysis.churn import analyze_churn
from gitintel.models import Commit, FileChange


def test_churn_ranks_by_total_lines():
    commits = [
        Commit(
            hash="a" * 40,
            author="Alice",
            email="alice@example.com",
            message="c",
            date=datetime(2026, 1, 1),
            changes=[
                FileChange(path="a.py", additions=1, deletions=1),
                FileChange(path="b.py", additions=10, deletions=0),
            ],
        )
    ]

    assert analyze_churn(commits)[0] == ("b.py", 10)
```

Add a `CliRunner` test for the command's exit code and a JSON round-trip if the output is meant
to be machine-readable. See [Testing](testing.md).

## 6. Document it

A command is not finished until it is documented:

| Page | What to add |
| --- | --- |
| [`docs/reference/cli.md`](../reference/cli.md) | synopsis, arguments, options, examples, errors |
| [`docs/reference/json-schema.md`](../reference/json-schema.md) | the JSON shape |
| `docs/guide/` | a task-oriented page if the command supports a real workflow |
| `mkdocs.yml` | the new page in `nav` |
| `CHANGELOG.md` | an entry under `Unreleased` → `Added` |
| `README.md` | one line in the command list |

## 7. Verify

```bash
python -m ruff check src tests
python -m pytest --cov --cov-report=term-missing
gitintel churn . --format json | python -m json.tool
mkdocs build --strict
```

Then open a pull request following [Contributing](../contributing.md).
