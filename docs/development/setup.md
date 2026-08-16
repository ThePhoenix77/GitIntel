# Development setup

## Requirements

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.11 or newer | `pyproject.toml` sets `requires-python = ">=3.11"`; CI tests 3.11–3.14 |
| Git | any recent version | Needed to clone the repo and to create fixtures |
| C toolchain | only if no `pygit2` wheel exists for your platform | libgit2 headers required in that case |

## Clone and bootstrap

```bash
git clone https://github.com/ThePhoenix77/GitIntel.git
cd GitIntel
make setup
```

`make setup` runs `scripts/bootstrap.sh`, which:

1. finds the first of `python3.11`, `python3`, `python` that reports version ≥ 3.11,
2. creates `.venv` (recreating it if an existing one is older than 3.11),
3. upgrades `pip`, `setuptools`, `wheel`,
4. installs the project in editable mode with dev extras: `pip install -e ".[dev]"`.

Then activate it:

```bash
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### Manual setup

If you prefer not to use the Makefile:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

### Using `uv`

`uv` is a fast alternative and is convenient when your system Python is older than 3.11 —
it downloads an interpreter for you:

```bash
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python -e ".[dev]"
```

!!! warning "Do not install with a Python older than 3.11"
    `pip install -e .` under Python 3.10 will try to resolve incompatible dependency versions
    and can appear to hang for a long time before failing. Check with `python -V` first.

## What gets installed

| Extra | Packages |
| --- | --- |
| runtime | `pygit2>=1.16`, `typer>=0.15`, `rich>=13.9`, `pydantic>=2.10` |
| `dev` | `build>=1.2`, `pytest>=8.3`, `pytest-cov>=6.0`, `ruff>=0.9`, `twine>=6.1` |

Documentation tooling is **not** part of the `dev` extra — install it separately when working
on this site:

```bash
python -m pip install mkdocs-material
```

See [Working on the docs](documentation.md).

## Verify the installation

```bash
python -m pytest -q                      # 6 tests should pass
python -m ruff check src tests           # no findings
gitintel version                         # prints the installed version
gitintel analyze .                       # analyze the GitIntel repo itself
```

Both console scripts (`gitintel` and `gitit`) and `python -m gitintel` point at the same Typer
application.

## Editable install behaviour

The project uses a `src/` layout with setuptools. After `pip install -e .`, edits to files under
`src/gitintel/` take effect immediately — no reinstall needed. Reinstall only when you change
`pyproject.toml` (dependencies, entry points, metadata).

## Editor configuration

- **Interpreter** — point your editor at `.venv/bin/python`.
- **Formatting/linting** — Ruff with the settings from `pyproject.toml` (`line-length = 88`,
  `target-version = "py311"`, rules `F` and `I`). Enable "organize imports on save" with Ruff so
  the `I` rules stay satisfied.
- **Tests** — pytest, rootdir the repository root, test path `tests`.

## Cleaning up

```bash
rm -rf .venv dist build site .pytest_cache
rm -rf ~/.cache/gitintel        # remove cached remote clones
```
