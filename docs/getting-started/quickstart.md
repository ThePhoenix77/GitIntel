# Quickstart

Five minutes, three commands, no configuration.

## 1. Point GitIntel at a repository

Every command takes a repository argument that defaults to `.`:

```bash
cd /path/to/your/repository
gitintel analyze .
```

You can also pass a public GitHub URL. GitIntel clones it into a local cache and analyzes the
clone:

```bash
gitintel analyze https://github.com/ThePhoenix77/GitIntel
```

## 2. Summarize the repository

```bash
gitintel analyze .
```

Prints four tables: repository summary, top contributors, most changed files, and repository
health. Walk through them in [Your first analysis](first-analysis.md).

## 3. Find out who owns a file

```bash
gitintel --quiet ownership . --file src/gitintel/cli.py --format markdown
```

```text
| File                  | Contributor    | Modifications | Modify % | Lines Changed | Lines % | Last Modified                       |
|-----------------------|----------------|---------------|----------|---------------|---------|-------------------------------------|
| src/gitintel/cli.py   | Boussaden Taha | 4             | 80.0%    | 512           | 91.2%   | Boussaden Taha 2026-08-15 14:10:10  |
| src/gitintel/cli.py   | ThePhoenix77   | 1             | 20.0%    | 49            | 8.8%    |                                     |
```

Without `--file`, the command reports the 20 most-modified files. Add `--all` to report every
file in history.

## 4. Rank the risky files

```bash
gitintel hotspots .
```

Files are scored 0–100 from change frequency, churn, contributor spread, and ownership
clarity, and the top 10 are shown. The scoring rules are documented in
[Metrics and scoring](../concepts/metrics.md#hotspot-risk-score).

## 5. Get machine-readable output

Every command accepts `--format table|json|markdown`:

```bash
gitintel --quiet analyze . --format json > analysis.json
gitintel --quiet hotspots . --format markdown >> report.md
```

!!! warning "Put global options before the subcommand"
    `--quiet` belongs to the top-level app, so it must appear *before* the command name:
    `gitintel --quiet analyze .` works, `gitintel analyze . --quiet` does not.

## Command cheat sheet

| Goal | Command |
| --- | --- |
| Repository overview | `gitintel analyze .` |
| Overview of a GitHub project | `gitintel analyze https://github.com/owner/repo` |
| Top 20 owned files | `gitintel ownership .` |
| Ownership of every file | `gitintel ownership . --all` |
| Ownership of one file | `gitintel ownership . --file path/to/file` |
| Top 10 risk hotspots | `gitintel hotspots .` |
| JSON for scripting | `gitintel --quiet <command> . --format json` |
| Markdown for a PR comment | `gitintel --quiet <command> . --format markdown` |
| Version | `gitintel --version` |
| Help for a command | `gitintel ownership --help` |

## Next steps

- [Your first analysis](first-analysis.md) — understand every column.
- [Core concepts](../concepts/index.md) — the mental model behind the numbers.
- [Automation and CI](../guide/automation.md) — run GitIntel on every pull request.
