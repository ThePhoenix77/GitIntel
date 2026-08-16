# Releasing

GitIntel is published to PyPI as [`gitintel`](https://pypi.org/project/gitintel/) and follows
[Semantic Versioning](https://semver.org/). The policy behind version numbers is described in
[Versioning and releases](../releases.md); this page is the mechanical checklist.

## 1. Confirm `main` is green

```bash
git checkout main
git pull
python -m ruff check src tests
python -m pytest --cov --cov-report=term-missing
mkdocs build --strict
```

## 2. Bump the version

The version appears in two places and both must match:

```bash
# pyproject.toml
version = "0.2.0"

# src/gitintel/__init__.py
__version__ = "0.2.0"
```

Verify:

```bash
python -m pip install -e .
gitintel version
```

## 3. Update the changelog

Move the `Unreleased` entries in `CHANGELOG.md` into a new version section, following
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/):

```markdown
## [0.2.0] - 2026-09-01
### Added
- `gitintel churn` command

### Changed
- Hotspot churn threshold raised to 4000 lines

### Fixed
- Duplicate table in `gitintel hotspots`
```

Breaking changes get their own `### Removed` / `### Changed` bullets with a migration note.

## 4. Open a release pull request

```bash
git checkout -b release/0.2.0
git add pyproject.toml src/gitintel/__init__.py CHANGELOG.md
git commit -m "release 0.2.0"
git push -u origin release/0.2.0
```

Merge once CI passes on all four Python versions.

## 5. Build and verify the artifacts

```bash
git checkout main && git pull
rm -rf dist
python -m build --sdist --wheel --outdir dist
python -m twine check dist/*
```

Smoke-test the wheel in a clean environment before publishing:

```bash
python -m venv /tmp/relcheck
/tmp/relcheck/bin/pip install dist/gitintel-0.2.0-py3-none-any.whl
/tmp/relcheck/bin/gitintel version
/tmp/relcheck/bin/gitintel analyze .
```

## 6. Publish

Optionally to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Then to PyPI:

```bash
python -m twine upload dist/*
```

Use an API token (username `__token__`) stored in `~/.pypirc` or supplied through the
`TWINE_USERNAME` / `TWINE_PASSWORD` environment variables. Never commit a token.

## 7. Tag and publish release notes

```bash
git tag -a v0.2.0 -m "GitIntel 0.2.0"
git push origin v0.2.0
```

Create the GitHub release from the tag, pasting the changelog section as the body and attaching
the files from `dist/`.

## 8. Verify the published package

```bash
pipx install gitintel==0.2.0
gitintel version
```

Confirm the docs site rebuilt at <https://thephoenix77.github.io/GitIntel/> and that the
[changelog page](../changelog.md) shows the new version.

## Checklist

- [ ] `main` green: ruff, pytest, `mkdocs build --strict`
- [ ] Version bumped in `pyproject.toml` **and** `src/gitintel/__init__.py`
- [ ] `CHANGELOG.md` updated with the release date
- [ ] Release pull request merged
- [ ] `python -m build` and `twine check` pass
- [ ] Wheel smoke-tested in a clean virtual environment
- [ ] Uploaded to PyPI
- [ ] Tag `vX.Y.Z` pushed and GitHub release published
- [ ] Docs site rebuilt and correct
