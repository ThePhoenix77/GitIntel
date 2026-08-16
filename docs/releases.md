# Versioning and releases

## Versioning scheme

GitIntel follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

| Increment | Meaning |
| --- | --- |
| `MAJOR` | Backwards-incompatible change to a supported interface |
| `MINOR` | New functionality, backwards compatible |
| `PATCH` | Bug fixes and documentation, backwards compatible |

The current version is `0.1.0`.

!!! warning "Pre-1.0 caveat"
    While the version is below 1.0, minor releases may include breaking changes. Any such change
    is called out in the [changelog](changelog.md) with a migration note. Pin an exact version if
    your automation depends on the output shape:

    ```bash
    pipx install gitintel==0.1.0
    ```

## What counts as a public interface

Covered by the compatibility promise once 1.0 is reached:

- command names, arguments, and options,
- the meaning of exit codes `0`, `1`, and `2`,
- the JSON output structure documented in
  [JSON output schema](reference/json-schema.md).

Explicitly **not** covered:

- the Python API — module paths, function signatures, and dataclass fields may change at any
  time before 1.0 ([Python API](reference/python-api.md)),
- table and Markdown layout: column order, wording, and styling may change in any release,
- hotspot thresholds and health-signal wording, which are tuned as the heuristics improve,
- the on-disk clone cache layout under `~/.cache/gitintel`.

Script against `--format json`, not against table output.

## Release cadence

There is no fixed schedule. Releases happen when meaningful changes have accumulated on `main`;
fixes for crashes or wrong numbers are released as soon as they land.

## Where releases are published

| Channel | Location |
| --- | --- |
| PyPI | <https://pypi.org/project/gitintel/> |
| GitHub releases | <https://github.com/ThePhoenix77/GitIntel/releases> |
| Git tags | `vX.Y.Z` on `main` |
| Changelog | [`CHANGELOG.md`](https://github.com/ThePhoenix77/GitIntel/blob/main/CHANGELOG.md) and [this site](changelog.md) |

## Upgrading

```bash
pipx upgrade gitintel                 # pipx install
python -m pip install --upgrade gitintel
uv tool upgrade gitintel
```

Verify and, if results shift unexpectedly, check the changelog for scoring or format changes:

```bash
gitintel version
```

## Downgrading

```bash
pipx install --force gitintel==0.1.0
python -m pip install "gitintel==0.1.0"
```

## Python support policy

GitIntel supports Python 3.11 and newer, and CI tests 3.11 through 3.14. Dropping a Python
version is a breaking change and will only happen in a `MAJOR` release (or, before 1.0, with an
explicit changelog note).

## Deprecations

When a flag or output field must go away, it is deprecated for at least one minor release
first: the changelog states the replacement, and the release notes list it under `Deprecated`
before it moves to `Removed`.

The step-by-step publishing procedure lives in [Releasing](development/releasing.md).
