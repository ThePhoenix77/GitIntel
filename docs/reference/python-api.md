# Python API

GitIntel is primarily a CLI, but the analysis layer is plain Python and can be imported. The
public surface described here is what the CLI itself uses.

!!! warning "Not a stable API yet"
    Nothing outside the CLI is covered by a compatibility promise before `1.0.0`. Pin an exact
    version if you build on these functions.

## Minimal example

```python
from gitintel.analysis.pipeline import analyze_repository
from gitintel.git.resolver import resolve_repository

repository, context = resolve_repository(".")
analysis = analyze_repository(repository, context)

print(context.repo_name, context.branch)
print(analysis.summary.commits, "commits")

for contributor in analysis.contributors[:5]:
    print(f"{contributor.name:<24} {contributor.commits:>4} commits")

for hotspot in analysis.hotspots[:5]:
    print(f"{hotspot.risk_score:>3} {hotspot.file_path} {hotspot.reasons}")
```

## Entry points

### `resolve_repository(source) -> tuple[pygit2.Repository, RepositoryContext]`

`gitintel.git.resolver`

Opens a local path or clones/reuses a cached GitHub URL, then extracts repository metadata.
Raises `ValueError` when the path is not a repository or the clone fails.

```python
repository, context = resolve_repository("https://github.com/ThePhoenix77/GitIntel")
```

Related helpers in the same module: `is_remote_repository(source)` and
`normalize_repository_url(source)`.

### `analyze_repository(repository, repository_context) -> AnalysisContext`

`gitintel.analysis.pipeline`

Builds the lazy analysis container. No history is read until a property is accessed.

### `AnalysisContext`

| Property | Type | Description |
| --- | --- | --- |
| `commits` | `list[Commit]` | Commits from `HEAD` in time order, with per-file changes |
| `contributors` | `list[Contributor]` | Sorted by commit count, descending |
| `summary` | `RepositorySummary` | Commit, contributor, and file counts |
| `ownership` | `list[FileOwnership]` | Per-file ownership metrics |
| `changes` | `dict[str, dict]` | `{path: {modifications, lines_changed, contributors}}` |
| `ownership_map` | `dict[str, str]` | `{path: last modifier}` |
| `hotspots` | `list[Hotspot]` | Sorted by risk score, descending |

Each property memoizes its result, so repeated access is free and dependent metrics reuse the
single commit walk.

## Data models

All models live in `gitintel.models` and are standard dataclasses.

```python
@dataclass
class FileChange:
    path: str
    additions: int
    deletions: int

@dataclass
class Commit:
    hash: str
    author: str
    email: str
    message: str
    date: datetime
    changes: list[FileChange]

@dataclass
class Contributor:
    name: str
    email: str
    commits: int
    files_changed: int
    additions: int
    deletions: int

@dataclass
class RepositorySummary:
    commits: int
    contributors: int
    files_changed: int

@dataclass
class RepositoryContext:
    path: Path
    source: str
    temporary: bool
    owner: str
    repo_name: str
    branch: str
    remote_url: str
    source_type: str

@dataclass
class FileOwnership:
    path: str
    modifications: dict[str, int]      # author name -> commits
    lines_changed: dict[str, int]      # author name -> additions + deletions
    last_modified_by: str
    last_modified_at: datetime

@dataclass
class Hotspot:
    file_path: str
    risk_score: float
    modifications: int
    lines_changed: int
    contributors: int
    owner: str | None = None
    reasons: list[str] = field(default_factory=list)
```

## Analysis functions

These are pure functions; you can call them on your own `Commit` lists, which is exactly what
the test suite does.

| Function | Module | Signature |
| --- | --- | --- |
| `analyze_contributors` | `gitintel.analysis.contributors` | `(commits) -> list[Contributor]` |
| `analyze_ownership` | `gitintel.analysis.ownership` | `(commits) -> list[FileOwnership]` |
| `create_summary` | `gitintel.analysis.summary` | `(commits, contributors) -> RepositorySummary` |
| `calculate_hotspots` | `gitintel.analysis.hotspots` | `(commits, file_changes, ownership) -> list[Hotspot]` |

```python
from datetime import datetime

from gitintel.analysis.ownership import analyze_ownership
from gitintel.models import Commit, FileChange

commits = [
    Commit(
        hash="abc123",
        author="Jane Doe",
        email="jane@example.com",
        message="Add parser",
        date=datetime(2026, 1, 1, 12, 0),
        changes=[FileChange(path="src/parser.py", additions=120, deletions=4)],
    )
]

ownership = analyze_ownership(commits)
print(ownership[0].modifications)   # {'Jane Doe': 1}
```

## Git layer

| Function | Module | Purpose |
| --- | --- | --- |
| `open_repository(path)` | `gitintel.git.repository` | Open a repository, raising `ValueError` if invalid |
| `get_repository_metadata(repository)` | `gitintel.git.repository` | `(owner, repo_name, branch, remote_url, source_type)` |
| `get_commits(repository, limit=None)` | `gitintel.git.commits` | Walk `HEAD`, optionally limited to `limit` commits |
| `get_commit_diff(repository, commit)` | `gitintel.git.diff` | `list[FileChange]` for one commit |
| `clone_repository(url, destination=None)` | `gitintel.git.clone` | Clone with a progress bar |
| `clone_or_open_cached_repository(url)` | `gitintel.git.cache` | `(path, was_cached)` |
| `get_cache_root()` / `get_cache_repo_path(url)` | `gitintel.git.cache` | Cache locations |
| `cleanup_repository(path)` | `gitintel.git.workspace` | Delete a temporary `gitintel_*` clone |

!!! tip "`get_commits` supports a limit the CLI does not expose"
    `get_commits(repository, limit=500)` stops after 500 commits. This is useful when scripting
    against very large repositories, even though no CLI flag surfaces it yet.

## Rendering helpers

`gitintel.reports.terminal` contains the renderers (`print_analysis`, `print_ownership`,
`print_hotspots`, plus the per-format variants), the `run_with_progress` wrapper, and
`configure_console(verbose=False, quiet=False)` which sets module-level verbosity. They print
to a Rich console rather than returning strings, so prefer building your own output from the
dataclasses when embedding GitIntel in another tool.
