# User guide

Task-oriented documentation for people using GitIntel day to day. For exhaustive flag lists
see the [CLI reference](../reference/cli.md); for the meaning behind the numbers see
[Core concepts](../concepts/index.md).

<div class="grid cards" markdown>

- :material-chart-box: **[Analyzing repositories](analyzing-repositories.md)**

    Repository-wide summaries, contributors, activity, and health.

- :material-account-check: **[Ownership analysis](ownership-analysis.md)**

    Who works on which files, filtering, and reviewer selection.

- :material-fire: **[Hotspot analysis](hotspot-analysis.md)**

    Ranking risk and acting on the results.

- :material-code-json: **[Output formats](output-formats.md)**

    `table`, `json`, `markdown` — and how to pipe them safely.

- :material-robot: **[Automation and CI](automation.md)**

    GitHub Actions, pre-merge reports, scheduled snapshots.

- :material-check-decagram: **[Best practices](best-practices.md)**

    Interpreting metrics honestly and running on large repositories.

</div>

## Invocation shape

```text
gitintel [GLOBAL OPTIONS] COMMAND [ARGUMENT] [COMMAND OPTIONS]
```

```bash
gitintel --quiet ownership /srv/api --all --format json
#        └ global ┘ └ cmd ┘ └ arg ┘ └ command options ┘
```

Global options (`--quiet`, `--version`, `--help`) must precede the command name; command
options follow it. The `gitit` alias is interchangeable with `gitintel` everywhere.
