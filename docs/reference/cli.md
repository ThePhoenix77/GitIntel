# CLI reference

Complete reference for the `gitintel` command line interface, version `0.1.0`.

## Synopsis

```text
gitintel [--help] [--version] [--quiet] COMMAND [ARGS] [OPTIONS]
gitit    [--help] [--version] [--quiet] COMMAND [ARGS] [OPTIONS]
python -m gitintel ...
```

`gitit` is an alias for `gitintel`; both entry points expose the same application.

Running `gitintel` with no command prints the help text and exits with code `2` (Typer's
standard "no command given" behaviour).

## Global options

Global options are defined on the application callback and **must appear before the command
name**.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--help` | flag | — | Show top-level help and exit |
| `--version` | flag | — | Print the installed version and exit |
| `--quiet`, `-q` | flag | `false` | Suppress progress spinners |
| `--install-completion` | flag | — | Install shell completion for the current shell |
| `--show-completion` | flag | — | Print the completion script without installing it |

```bash
gitintel --quiet analyze . --format json     # correct
gitintel analyze . --quiet                   # error: no such option
```

!!! info "What `--quiet` does and does not suppress"
    It suppresses the spinners emitted while resolving the repository and building the
    analysis. The clone progress bar and the `[OK] Repository cloned: ...` line printed when a
    remote URL is downloaded are not affected.

## Commands

| Command | Purpose |
| --- | --- |
| [`analyze`](#gitintel-analyze) | Repository summary, contributors, activity, health |
| [`ownership`](#gitintel-ownership) | Per-file ownership metrics |
| [`hotspots`](#gitintel-hotspots) | Risk-scored hotspot files |
| [`version`](#gitintel-version) | Print the installed version |

---

## `gitintel analyze`

Analyze repository history and print summary metrics.

```text
gitintel analyze [PATH] [--format FORMAT]
```

### Arguments

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `PATH` | string | `.` | Local repository path or public GitHub URL |

### Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--format`, `-f` | `table` \| `json` \| `markdown` | `table` | Output format (case-insensitive; unknown values fall back to `table`) |
| `--help` | flag | — | Show command help and exit |

### Output

- Repository panel: name, owner, branch, path, source, remote
- `Repository Summary`: commits, contributors, files changed, last commit
- `Top Contributors`: commits, distinct files, share
- `Most Changed Files`: top 10 by number of touching commits
- `Repository Health`: Activity, Ownership, Maintenance

JSON keys: `repository`, `summary`, `contributors`, `most_changed_files`, `repository_health`.

### Examples

```bash
gitintel analyze .
gitintel analyze /srv/projects/api --format markdown
gitintel --quiet analyze https://github.com/ThePhoenix77/GitIntel --format json
```

### Errors

| Situation | Message | Exit code |
| --- | --- | --- |
| Path is not a Git repository | `Invalid Git repository: <path>` | `1` |
| GitHub URL cannot be cloned | `Unable to clone repository: <url>` | `1` |
| Clone interrupted with ++ctrl+c++ | `Cloning cancelled by user` | `1` |

---

## `gitintel ownership`

Analyze file ownership and contributor activity per file.

```text
gitintel ownership [PATH] [--all] [--file FILE] [--format FORMAT]
```

### Arguments

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `PATH` | string | `.` | Local repository path or public GitHub URL |

### Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--all` | flag | `false` | Report every file instead of the top 20 by modification count |
| `--file` | string | — | Report a single file; must match the repository-relative path exactly |
| `--format`, `-f` | `table` \| `json` \| `markdown` | `table` | Output format |
| `--help` | flag | — | Show command help and exit |

Selection order: `--file` is applied first and takes precedence over `--all`. Without either,
the 20 files with the most modifications are reported, sorted descending. With `--all`, files
appear in the order they were first encountered in history (unsorted).

### Output columns

`File`, `Contributor`, `Modifications`, `Modify %`, `Lines Changed`, `Lines %`, `Last Modified`.
One row per contributor per file; the `Last Modified` cell is populated only on the row of the
most recent author.

JSON keys: `repository`, `ownership`.

### Examples

```bash
gitintel ownership .
gitintel ownership . --all
gitintel ownership . --file src/gitintel/cli.py
gitintel --quiet ownership . --file README.md --format markdown
gitintel --quiet ownership . --all --format json | jq '.ownership | length'
```

### Errors

| Situation | Message | Exit code |
| --- | --- | --- |
| `--file` path has no history | `File not found: <path>` | `1` |
| Path is not a Git repository | `Invalid Git repository: <path>` | `1` |
| No ownership data at all | `No ownership data found.` (table/markdown) | `0` |

---

## `gitintel hotspots`

Identify hotspot files that may need review.

```text
gitintel hotspots [SOURCE] [--format FORMAT]
```

### Arguments

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `SOURCE` | string | `.` | Local repository path or public GitHub URL |

### Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--format`, `-f` | `table` \| `json` \| `markdown` | `table` | Output format |
| `--help` | flag | — | Show command help and exit |

### Output columns

`File`, `Risk` (`HIGH` ≥ 70 else `MED`, plus the numeric score), `Changes` (lines changed),
`Contributors`, `Owner` (last modifier). Limited to the top 10 files; files scoring `0` are
omitted.

JSON keys: `repository`, `hotspots` (each with `file`, `risk_score`, `changes`,
`contributors`, `owner`, `reasons`).

### Examples

```bash
gitintel hotspots .
gitintel hotspots https://github.com/ThePhoenix77/GitIntel
gitintel --quiet hotspots . --format json | jq '.hotspots[] | select(.risk_score >= 70)'
```

---

## `gitintel version`

Print the installed version and exit. Equivalent to the global `--version` flag.

```bash
gitintel version
```

```text
0.1.0
```

---

## Environment variables

| Variable | Effect |
| --- | --- |
| `XDG_CACHE_HOME` | Overrides the clone cache root; GitIntel uses `$XDG_CACHE_HOME/gitintel` instead of `~/.cache/gitintel` |
| `COLUMNS` | Read by Rich to size output. Set it (e.g. `COLUMNS=200`) when redirecting JSON or Markdown so long values are not soft-wrapped |
| `NO_COLOR` | Honoured by Rich to disable ANSI colors |
| `TERM=dumb` | Also disables styling in Rich |

GitIntel itself reads no configuration file and no other environment variables.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success (including `--help` and `--version` output) |
| `1` | A `ValueError` raised during resolution or analysis, or `--file` matched nothing |
| `2` | Usage error — unknown option, unknown command, or no command given |

Details and message-by-message guidance: [Exit codes and errors](errors.md).
