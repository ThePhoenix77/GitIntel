# Debugging

## See the real exception

`pretty_exceptions_enable=False` is set on the Typer app, so unexpected failures already print a
plain traceback. Only `ValueError` is converted into the friendly red panel — if you need to see
where one originated, run the pipeline directly in Python instead of through the CLI:

```python
from gitintel.analysis.pipeline import analyze_repository
from gitintel.git.resolver import resolve_repository

repository, context = resolve_repository(".")
analysis = analyze_repository(repository, context)

print(len(analysis.commits))
print(analysis.summary)
```

## Interactive inspection

```bash
python -m pdb -m gitintel analyze .
```

or drop a breakpoint into the code under investigation:

```python
breakpoint()
```

Post-mortem on the last failure inside an interpreter session:

```python
import pdb
pdb.pm()
```

## Inspecting the pipeline

`AnalysisContext` properties are memoized, so you can poke at intermediate values cheaply once
the first access has walked history:

```python
analysis.commits[0]                       # newest Commit, with its FileChange list
analysis.changes["src/gitintel/cli.py"]   # modifications, lines_changed, contributors
analysis.ownership_map["src/gitintel/cli.py"]
[h for h in analysis.hotspots if h.risk_score > 40]
```

Remember the walk order is newest-first (`GIT_SORT_TIME`); a surprising "last modified by" value
usually traces back to that.

## Comparing against Git

When a number looks wrong, check GitIntel's view against Git's:

```bash
git log --oneline | wc -l                       # commits reachable from HEAD
git shortlog -sne                               # commits per author (by identity)
git log --numstat -- src/gitintel/cli.py        # per-commit line changes for a file
git log --follow --oneline -- <path>            # history across renames
```

Expected differences:

- GitIntel ignores `.mailmap`, so identities Git merges may appear separately.
- Merge commits are diffed against the first parent only.
- The initial commit counts every file's line count as additions.
- A shallow clone (`git clone --depth 1`) gives GitIntel only the commits it has.

## Reproducing remote-source problems

```bash
gitintel analyze https://github.com/owner/repo     # first run clones
ls ~/.cache/gitintel                               # inspect cache directory names
rm -rf ~/.cache/gitintel/owner__repo               # force a fresh clone
```

A cached clone is never refreshed. If results look stale, delete the directory before blaming
the analysis.

## Output-related debugging

```bash
gitintel --quiet analyze . --format json | python -m json.tool    # is stdout valid JSON?
COLUMNS=200 gitintel --quiet analyze . --format json              # avoid Rich soft-wrapping
```

`--quiet` must come **before** the subcommand; it is a global option. Placing it afterwards
exits with code `2`.

## Checking what the CLI parsed

```bash
gitintel --help
gitintel ownership --help
gitintel version
```

Typer generates help from the function signatures in `cli.py`, so this is the fastest way to
confirm that a new option is wired up the way you intended.

## Profiling

```bash
python -X importtime -m gitintel version                     # startup cost
python -m cProfile -s cumtime -m gitintel analyze . | head -40
```

On large repositories, expect `get_commit_diff` to dominate: one diff per commit is the
pipeline's fundamental cost. See
[Analysis pipeline → cost model](../concepts/analysis-pipeline.md).
