# Coding conventions

## Linting

Ruff is the only style tool, configured in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["F", "I"]

[tool.ruff.lint.isort]
known-first-party = ["gitintel"]
```

- `F` — pyflakes: unused imports and variables, undefined names, f-strings without placeholders.
- `I` — isort: import ordering and grouping, with `gitintel` treated as first-party.

Run exactly what CI runs:

```bash
python -m ruff check src tests
python -m ruff check --fix src tests     # auto-fix import order and simple issues
```

Ruff's formatter is **not** part of CI. Do not reformat files you are not otherwise changing —
it makes reviews and `git blame` noisy.

## Style

The codebase has a consistent, slightly unusual house style. Match it rather than your editor's
defaults:

- **One argument per line** in multi-line calls, with a trailing comma:

    ```python
    ownership = analyze_ownership(
        commits,
    )
    ```

- **Blank line between logical steps** inside functions; the code favours breathing room over
  density.
- **Modern typing syntax** — `list[Commit]`, `str | None`, `dict[str, int]`. No `typing.List`,
  no `Optional`.
- **Dataclasses for data**, plain functions for behaviour. No classes with methods except
  `AnalysisContext`.
- **Explicit names** — `repository`, `context`, `commits` rather than `repo`, `ctx`, `cs`.
- **Docstrings** only where behaviour is not obvious from the signature; there are no
  enforced docstring rules.

## Imports

Absolute imports throughout, ordered by Ruff:

```python
from gitintel.analysis.ownership import analyze_ownership
from gitintel.git.commits import get_commits
```

All imports go at the top of the module. Respect the layering rules in
[Project structure](project-structure.md#layering-rules).

## Errors

- Raise `ValueError` with a user-facing message for anything the user can fix
  (`Invalid Git repository: {path}`, `File not found: {path}`). The CLI turns these into a red
  panel and exit code `1`.
- Do not call `sys.exit()` or `typer.Exit` outside `cli.py`.
- Do not swallow exceptions from `pygit2` in the analysis layer; let them surface so the bug is
  visible.
- Keep messages specific and include the offending value.

## Output

- Never use `print()`; write through the Rich `Console` in `reports/terminal.py`.
- Respect the module-level `QUIET` flag — progress and decoration must be suppressed, report
  content must not.
- JSON output must remain parseable: no extra text on stdout, no Rich markup in values.
- When you add a field to one format, add it to all three (`table`, `json`, `markdown`) and
  update [the JSON schema reference](../reference/json-schema.md).

## Compatibility

- Target Python 3.11; CI also runs 3.12, 3.13 and 3.14. Do not use syntax or stdlib APIs newer
  than 3.11.
- Avoid new runtime dependencies. The current four (`pygit2`, `typer`, `rich`, `pydantic`) are
  enough for the tool's scope; adding one needs justification in the pull request.
- Use `pathlib.Path` rather than `os.path`.

## Commits and branches

- Branch names: `feature/short-description`, `fix/short-description`, `docs/short-description`.
- One logical change per branch.
- Imperative commit subjects (`add hotspot threshold for churn`), body explaining *why* when it
  is not obvious.

Full expectations for pull requests: [Contributing](../contributing.md).
