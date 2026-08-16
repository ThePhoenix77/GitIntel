# Your first analysis

This page walks through a real `gitintel analyze` run and explains every table and number.
The output below comes from analyzing the GitIntel repository itself.

```bash
gitintel analyze .
```

## The repository panel

```text
╭───────────────────────────── GitIntel Analysis ──────────────────────────────╮
│ Repository: GitIntel                                                         │
│ Owner: ThePhoenix77                                                          │
│ Branch: main                                                                 │
│ Path: /home/dev/repos/GitIntel                                               │
│ Source: GitHub                                                               │
│ Remote: https://github.com/ThePhoenix77/GitIntel.git                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

| Field | Meaning |
| --- | --- |
| `Repository` | Repository name derived from the remote URL, falling back to the directory name |
| `Owner` | Namespace segment of the remote URL (the GitHub user or organization) |
| `Branch` | Short name of the currently checked-out `HEAD` — **the branch that gets analyzed** |
| `Path` | Absolute path of the analyzed working copy (a cache directory for remote URLs) |
| `Source` | `GitHub` when the remote host is github.com, otherwise `Local` |
| `Remote` | The `origin` remote URL, or the first remote if there is no `origin` |

!!! note "Analysis follows `HEAD`, not the default branch"
    GitIntel walks commits reachable from the current `HEAD`. Check out a different branch
    (or clone with a different default) to analyze different history.

## Repository summary

```text
         Repository Summary
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Metric        ┃ Value            ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Commits       │ 6                │
│ Contributors  │ 2                │
│ Files Changed │ 44               │
│ Last Commit   │ 2026-08-15 14:10 │
└───────────────┴──────────────────┘
```

- **Commits** — number of commits reachable from `HEAD` (all of them; there is no depth limit).
- **Contributors** — distinct author **email addresses**. One person committing from two
  addresses counts twice; see [Terminology](../concepts/terminology.md#contributor).
- **Files Changed** — distinct file paths touched anywhere in that history, including files
  that were later deleted or renamed.
- **Last Commit** — committer timestamp of the newest commit, in your local timezone.

## Top contributors

```text
              Top Contributors
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ Contributor    ┃ Commits ┃ Files ┃ Share ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ Boussaden Taha │ 5       │ 6     │ 83.3% │
│ ThePhoenix77   │ 1       │ 39    │ 16.7% │
└────────────────┴─────────┴───────┴───────┘
```

- **Commits** — commits authored by that email address.
- **Files** — distinct files that author has touched.
- **Share** — that author's percentage of all commits.

A high commit share with a low file count means someone iterating deeply on a small area; the
opposite usually indicates bulk or import commits.

## Most changed files

```text
                          Most Changed Files
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ File                                      ┃ Changes ┃ Lines Changed ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ README.md                                 │ 2       │ 181           │
│ .github/PULL_REQUEST_TEMPLATE.md          │ 1       │ 30            │
│ CODE_OF_CONDUCT.md                        │ 1       │ 128           │
└───────────────────────────────────────────┴─────────┴───────────────┘
```

- **Changes** — how many commits touched the file.
- **Lines Changed** — additions plus deletions across those commits (churn, not file size).

Only the top 10 files by change count are displayed. This table appears for the `table` and
`markdown` formats and as `most_changed_files` in JSON.

## Repository health

```text
               Repository Health
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Area        ┃ Status ┃ Details              ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Activity    │ [OK]   │ Low change frequency │
│ Ownership   │ [OK]   │ 2 contributors       │
│ Maintenance │ [OK]   │ Recently updated     │
└─────────────┴────────┴──────────────────────┘
```

The three signals are computed from fixed thresholds — the exact rules are listed in
[Metrics and scoring](../concepts/metrics.md#repository-health-signals). `[!!]` marks a
warning, not an error: a warning simply means the repository deserves a human look
(for example, a single-contributor project or no commits in the last 90 days).

## The same run as JSON

```bash
gitintel --quiet analyze . --format json
```

```json
{
  "repository": {
    "name": "GitIntel",
    "owner": "ThePhoenix77",
    "branch": "main",
    "path": "/home/dev/repos/GitIntel",
    "source": "GitHub",
    "remote": "https://github.com/ThePhoenix77/GitIntel.git"
  },
  "summary": {
    "commits": 6,
    "contributors": 2,
    "files_changed": 44,
    "last_commit": "2026-08-15T14:10:10"
  },
  "contributors": [
    { "name": "Boussaden Taha", "commits": 5, "files_changed": 6, "share": 83.33333333333334 }
  ],
  "most_changed_files": [
    { "file": "README.md", "changes": 2, "lines_changed": 181 }
  ],
  "repository_health": [
    { "area": "Activity", "status": "OK", "details": "Low change frequency" }
  ]
}
```

The complete schema for all three commands is documented in
[JSON output schema](../reference/json-schema.md).

## Next steps

- Dig into one file with [`ownership`](../guide/ownership-analysis.md).
- Rank risk across the repository with [`hotspots`](../guide/hotspot-analysis.md).
- Understand *why* the numbers look the way they do in [Core concepts](../concepts/index.md).
