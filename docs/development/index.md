# Developer guide

Everything needed to work *on* GitIntel rather than *with* it.

<div class="grid cards" markdown>

- :material-hammer-wrench: **[Development setup](setup.md)** — virtual environment, editable install, tooling.
- :material-file-tree: **[Project structure](project-structure.md)** — where everything lives.
- :material-format-list-checks: **[Coding conventions](coding-conventions.md)** — style, linting, typing.
- :material-test-tube: **[Testing](testing.md)** — pytest, coverage, writing new tests.
- :material-bug: **[Debugging](debugging.md)** — inspecting the pipeline and pygit2.
- :material-plus-box: **[Adding a command](adding-a-command.md)** — end-to-end feature walkthrough.
- :material-book-edit: **[Working on the docs](documentation.md)** — build and preview this site.
- :material-tag-outline: **[Releasing](releasing.md)** — version bump, build, publish.

</div>

## 60-second setup

```bash
git clone https://github.com/ThePhoenix77/GitIntel.git
cd GitIntel
make setup                     # creates .venv and installs .[dev]
source .venv/bin/activate
python -m pytest -q
python -m ruff check src tests
```

## What CI enforces

The [`CI` workflow](https://github.com/ThePhoenix77/GitIntel/blob/main/.github/workflows/ci.yml)
runs on every push and pull request to `main`, across Python 3.11–3.14:

1. `python -m ruff check src tests`
2. `python -m pytest --cov --cov-report=term-missing`
3. `python -m build --sdist --wheel` followed by `python -m twine check dist/*`

Run all three locally before opening a pull request and CI will rarely surprise you.

## Contribution flow

```mermaid
flowchart LR
    A[Fork + branch] --> B[Change code]
    B --> C[Add or update tests]
    C --> D[ruff + pytest + build]
    D --> E[Update docs]
    E --> F[Open pull request]
    F --> G[CI + review]
```

Details and expectations: [Contributing](../contributing.md).
