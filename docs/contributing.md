# Contributing

Contributions are welcome — bug reports, documentation fixes, tests, and features. This page is
the working version of
[`CONTRIBUTING.md`](https://github.com/ThePhoenix77/GitIntel/blob/main/CONTRIBUTING.md), with
links into the developer guide.

Participation is governed by the
[Code of Conduct](https://github.com/ThePhoenix77/GitIntel/blob/main/CODE_OF_CONDUCT.md).

## Ways to contribute

| Contribution | Where to start |
| --- | --- |
| Bug report | [Issues](https://github.com/ThePhoenix77/GitIntel/issues) |
| Feature proposal | Open an issue describing the problem before writing code |
| Tests | `tests/test_hotspots.py` and `tests/test_repository.py` are empty placeholders |
| Documentation | [Working on the docs](development/documentation.md) |
| Security issue | Follow [SECURITY.md](https://github.com/ThePhoenix77/GitIntel/blob/main/SECURITY.md) — do not open a public issue |

## Before you start

For anything larger than a bug fix or a docs change, open an issue first. It is cheaper to agree
on an approach than to rework a finished pull request — especially for changes to scoring rules
or output formats, which affect everyone's scripts.

## Workflow

```bash
# 1. Fork on GitHub, then clone your fork
git clone https://github.com/<you>/GitIntel.git
cd GitIntel

# 2. Set up the environment
make setup
source .venv/bin/activate

# 3. Branch
git checkout -b feature/describe-your-change

# 4. Make the change, with tests

# 5. Run everything CI runs
python -m ruff check src tests
python -m pytest --cov --cov-report=term-missing
python -m build --sdist --wheel --outdir dist
python -m twine check dist/*

# 6. Push and open a pull request against main
git push -u origin feature/describe-your-change
```

Setup details: [Development setup](development/setup.md).

## Branch naming

| Prefix | Use |
| --- | --- |
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `test/` | Tests only |
| `release/` | Version bump and changelog |

Keep one logical change per branch.

## Commit messages

Imperative subject under ~72 characters, with a body explaining *why* when the reason is not
obvious:

```text
add churn threshold to hotspot scoring

Files with heavy line churn but few contributors were scoring zero,
so long-lived utility modules never appeared in the report.
```

## Pull requests

Include:

- a short summary of the change,
- the problem it solves (link the issue),
- how you verified it — commands run and their outcome,
- any breaking changes with a migration note,
- documentation updates for user-visible behaviour,
- a `CHANGELOG.md` entry under `Unreleased`.

CI runs Ruff, pytest with coverage, and a package build across Python 3.11–3.14. Pull requests
also build this site with `mkdocs build --strict`, so a broken documentation link fails the
build.

## Code expectations

- Follow the house style in [Coding conventions](development/coding-conventions.md).
- Respect the layer boundaries described in
  [Project structure](development/project-structure.md#layering-rules).
- Add tests for new behaviour; prefer pure tests over repository-backed ones —
  [Testing](development/testing.md).
- Support all three output formats when you change output —
  [Adding a command](development/adding-a-command.md).
- Avoid new runtime dependencies unless there is no reasonable alternative, and say why in the
  pull request.
- Do not reformat unrelated code.

## Reporting bugs

A good report contains:

- the exact command,
- the full output, including any traceback,
- `gitintel version` and `python -V`,
- your operating system,
- whether the source was a local path or a GitHub URL, and whether the clone was shallow.

## Documentation contributions

Documentation is part of the product. Small fixes can go straight to a pull request — every page
has an edit pencil in the top right that opens the source file on GitHub. Build with
`mkdocs build --strict` before pushing.

## Review

Expect review comments on: matching the existing style, test coverage, whether behaviour change
is documented, and whether output format changes would break downstream scripts. Maintainers
merge once CI is green and the discussion is resolved.
