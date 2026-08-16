# Components

Module-by-module description of the `src/gitintel` package.

## `cli.py` — command interface

Defines the Typer application (`app`), the global callback, and the four commands. Each command
follows the same shape:

```python
repository, context = run_with_progress("Preparing repository...", resolve_repository, path)
analysis = run_with_progress("Building analysis pipeline...", analyze_repository, repository, context)
print_<report>(..., output_format=format)
```

wrapped in `try/except ValueError` (rendered via `handle_error`, exit code `1`) and a `finally`
block that calls `cleanup_repository()` for temporary checkouts.

Notable configuration: `no_args_is_help=True`, `pretty_exceptions_enable=False`, and
`context_settings={"help_option_names": []}` on the app with `--help` re-added manually through
an eager callback — which is why `--version` and `--help` work at the top level and `--help`
works per command.

## `models.py` — shared contracts

Plain dataclasses with no behaviour: `FileChange`, `Commit`, `Contributor`,
`RepositorySummary`, `RepositoryContext`, `FileOwnership`, `Hotspot`. Every other layer speaks
in these types, which is what allows the analysis functions to be tested without Git.

Full field listings: [Python API → data models](../reference/python-api.md#data-models).

## `git/` — data access

| Module | Contents |
| --- | --- |
| `resolver.py` | `resolve_repository()`, `is_remote_repository()`, `normalize_repository_url()`. Decides local vs. remote and builds `RepositoryContext` |
| `repository.py` | `open_repository()` (raises `ValueError` on failure) and `get_repository_metadata()` which parses owner/name/branch/remote/source type |
| `commits.py` | `get_commits(repository, limit=None)` — walks `HEAD` with `GIT_SORT_TIME` and builds `Commit` objects |
| `diff.py` | `get_commit_diff()` — diffs a commit against its first parent with rename detection (`find_similar()`), and special-cases the parentless initial commit by walking the tree |
| `cache.py` | Cache root resolution, URL→directory name normalization, and `clone_or_open_cached_repository()` which reuses, repairs, or creates a clone |
| `clone.py` | `clone_repository()` with a Rich progress bar and cancellation handling; converts every failure into `ValueError` |
| `workspace.py` | `cleanup_repository()` — deletes a directory **only** if its name starts with `gitintel_` |

## `analysis/` — domain logic

| Module | Function | Behaviour |
| --- | --- | --- |
| `pipeline.py` | `analyze_repository()`, `AnalysisContext` | Lazy, memoized properties tying every metric to one commit walk |
| `contributors.py` | `analyze_contributors()` | Aggregates by author email; sorts by commit count |
| `ownership.py` | `analyze_ownership()` | Aggregates per file by author name; tracks last modifier and timestamp |
| `summary.py` | `create_summary()` | Counts commits, contributors, and distinct files |
| `hotspots.py` | `calculate_hotspots()` | Applies the four scoring rules, caps at 100, drops zero-score files, sorts descending |

All four analysis functions are pure: same inputs, same outputs, no I/O.

## `reports/` — presentation

`terminal.py` holds the whole presentation layer despite the module name — including the JSON
and Markdown renderers:

| Group | Functions |
| --- | --- |
| Dispatchers | `print_analysis()`, `print_ownership()`, `print_hotspots()` — lowercase the format and delegate |
| Table | `print_analysis_table()`, `print_ownership_table()`, `print_hotspots_table()`, `print_file_activity()`, `print_health()` |
| JSON | `print_analysis_json()`, `print_ownership_json()`, `print_hotspots_json()` |
| Markdown | `print_analysis_markdown()`, `print_ownership_markdown()`, `print_hotspots_markdown()` |
| Support | `run_with_progress()`, `configure_console()`, `get_display_name()`, `get_file_activity()`, `get_repository_health_data()`, `print_banner()` |

`markdown.py` and `reports/__init__.py` are currently empty placeholders; the Markdown
renderers live in `terminal.py`.

Verbosity is module-level state (`VERBOSE`, `QUIET`) set once by `configure_console()` from the
global CLI callback.

## `__main__.py`

Enables `python -m gitintel` by importing `app` and invoking it.

## Test layout

`tests/` mirrors the package: `test_cli.py`, `test_commits.py`, `test_contributors.py`,
`test_diff.py`, `test_hotspots.py`, `test_ownership.py`, `test_repository.py`. Domain tests
construct `Commit`/`FileChange` objects directly; CLI tests use Typer's `CliRunner`.
`test_hotspots.py` and `test_repository.py` exist but are still empty — they are good first
contributions. See [Testing](../development/testing.md).
