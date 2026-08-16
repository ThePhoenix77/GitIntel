# Getting started

This section takes you from an empty terminal to a working GitIntel report.

<div class="grid cards" markdown>

- :material-package-down: **[Installation](installation.md)**

    Prerequisites, `pipx`/`pip`/`uv` installation, installing from source, and verification.

- :material-flash: **[Quickstart](quickstart.md)**

    Three commands that cover everything GitIntel does.

- :material-book-open-page-variant: **[Your first analysis](first-analysis.md)**

    A guided tour of a real report, table by table, with an explanation of every number.

</div>

## Requirements at a glance

| Requirement | Value |
| --- | --- |
| Python | 3.11, 3.12, 3.13, or 3.14 |
| Operating systems | Linux, macOS, Windows (anything `pygit2` publishes wheels for) |
| Runtime dependencies | `pygit2`, `typer`, `rich`, `pydantic` (installed automatically) |
| Git installation | Not required — GitIntel talks to repositories through libgit2 |
| Network access | Only when analyzing a remote GitHub URL |
| Accounts, tokens, config files | None |

## The 60-second version

```bash
pipx install gitintel
cd /path/to/your/repository
gitintel analyze .
```

If that worked, jump straight to [Your first analysis](first-analysis.md) to interpret the
output, or to the [CLI reference](../reference/cli.md) for every flag.
