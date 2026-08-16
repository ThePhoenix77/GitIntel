# GitIntel

GitIntel is a command-line tool that reads a Git repository's history and turns it
into three concrete answers:

- **What happened in this repository?** — commits, contributors, activity, and health signals.
- **Who owns this code?** — per-file ownership by modification count, lines changed, and last touch.
- **Where is the risk?** — hotspot files ranked by churn, contributor spread, and ownership clarity.

Everything runs locally against the Git object database. There is no server, no account,
no API token, and no telemetry.

```bash
pipx install gitintel
gitintel analyze .
```

## What GitIntel is

GitIntel is a Python 3.11+ CLI built on [pygit2](https://www.pygit2.org/) (libgit2 bindings),
[Typer](https://typer.tiangolo.com/), and [Rich](https://rich.readthedocs.io/). It walks the
commit graph from `HEAD`, computes per-file change statistics, and renders reports as
terminal tables, JSON, or Markdown.

It works on a local checkout or on a public GitHub URL, which it clones into a local cache
before analyzing.

## Key features

| Capability | Command | Details |
| --- | --- | --- |
| Repository summary, contributors, most-changed files, health signals | [`analyze`](reference/cli.md#gitintel-analyze) | [Analyzing repositories](guide/analyzing-repositories.md) |
| Per-file ownership by modifications, lines changed, last modifier | [`ownership`](reference/cli.md#gitintel-ownership) | [Ownership analysis](guide/ownership-analysis.md) |
| Risk-scored hotspot files with human-readable reasons | [`hotspots`](reference/cli.md#gitintel-hotspots) | [Hotspot analysis](guide/hotspot-analysis.md) |
| `table`, `json`, and `markdown` output | `--format` | [Output formats](guide/output-formats.md) |
| Local paths and GitHub URLs, with an on-disk clone cache | any command | [Repository sources and cache](concepts/repository-sources.md) |
| Short alias `gitit` for every command | — | [Installation](getting-started/installation.md) |

## Who it is for

- **Reviewers and maintainers** deciding who should review a change, or which files deserve
  extra scrutiny.
- **Tech leads** looking for bus-factor and ownership-concentration risk before planning work.
- **Contributors joining a new codebase** who need to know which files matter and who to ask.
- **Automation authors** who want repository statistics as JSON or Markdown inside CI.

See [Use cases](introduction/use-cases.md) for worked examples.

## Where to start

<div class="grid cards" markdown>

- :material-rocket-launch: **New here?**

    Install GitIntel and run your first report in a few minutes.

    [Getting started](getting-started/index.md)

- :material-lightbulb-on: **Want the mental model?**

    Learn how commits become ownership and hotspot metrics.

    [Core concepts](concepts/index.md)

- :material-console: **Need exact flags?**

    Every command, argument, option, and output field.

    [CLI reference](reference/cli.md)

- :material-code-braces: **Contributing?**

    Set up the repo, run tests, and add a command.

    [Developer guide](development/index.md)

</div>

## Project status

GitIntel is at version `0.1.0` (Beta). The CLI surface is small and stable, but the metric
definitions and JSON field names may still change before `1.0.0`. See
[Versioning and releases](releases.md) for the compatibility policy and
[Documentation roadmap](roadmap.md) for what is planned next.

Licensed under the [MIT License](https://github.com/ThePhoenix77/GitIntel/blob/main/LICENSE).
