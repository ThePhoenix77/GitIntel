# JSON output schema

`--format json` prints exactly one JSON document per run, indented with two spaces. This page
documents every field emitted by version `0.1.0`.

!!! warning "Pre-1.0 stability"
    Field names may change before `1.0.0`. See [Versioning and releases](../releases.md).

## Shared: `repository`

Present in all three commands.

```json
{
  "repository": {
    "name": "GitIntel",
    "owner": "ThePhoenix77",
    "branch": "main",
    "path": "/home/dev/repos/GitIntel",
    "source": "GitHub",
    "remote": "https://github.com/ThePhoenix77/GitIntel.git"
  }
}
```

| Field | Type | Notes |
| --- | --- | --- |
| `name` | string | Repository name from the remote, else the directory name |
| `owner` | string | Namespace from the remote URL, or `"Unknown"` |
| `branch` | string | Short `HEAD` name, or `"Unknown"` |
| `path` | string | Absolute path of the analyzed checkout |
| `source` | string | `"GitHub"` or `"Local"` |
| `remote` | string | Remote URL, or `"N/A"` |

## `gitintel analyze --format json`

```json
{
  "repository": { "...": "see above" },
  "summary": {
    "commits": 6,
    "contributors": 2,
    "files_changed": 44,
    "last_commit": "2026-08-15T14:10:10"
  },
  "contributors": [
    {
      "name": "Boussaden Taha",
      "commits": 5,
      "files_changed": 6,
      "share": 83.33333333333334
    }
  ],
  "most_changed_files": [
    { "file": "README.md", "changes": 2, "lines_changed": 181 }
  ],
  "repository_health": [
    { "area": "Activity", "status": "OK", "details": "Low change frequency" },
    { "area": "Ownership", "status": "OK", "details": "2 contributors" },
    { "area": "Maintenance", "status": "OK", "details": "Recently updated" }
  ]
}
```

| Path | Type | Notes |
| --- | --- | --- |
| `summary.commits` | integer | Commits reachable from `HEAD` |
| `summary.contributors` | integer | Distinct author emails |
| `summary.files_changed` | integer | Distinct file paths in history |
| `summary.last_commit` | string \| null | ISO 8601 local time; `null` when there are no commits |
| `contributors[].name` | string | Author name |
| `contributors[].commits` | integer | Commits by that author email |
| `contributors[].files_changed` | integer | Distinct files touched |
| `contributors[].share` | float | Percentage of all commits, unrounded |
| `most_changed_files[]` | array | Top 10 by `changes` |
| `most_changed_files[].changes` | integer | Commits touching the file |
| `most_changed_files[].lines_changed` | integer | Additions + deletions |
| `repository_health[].area` | string | `Activity`, `Ownership`, or `Maintenance` |
| `repository_health[].status` | string | `OK` or `WARN` |
| `repository_health[].details` | string | Human-readable explanation |

Contributor email addresses are **not** included in `analyze` JSON.

## `gitintel ownership --format json`

```json
{
  "repository": { "...": "see above" },
  "ownership": [
    {
      "file": "README.md",
      "contributor": "Boussaden Taha",
      "modifications": 1,
      "modify_percent": 50.0,
      "lines_changed": 5,
      "lines_percent": 2.7624309392265194,
      "last_modified_by": "Boussaden Taha",
      "last_modified_at": "2026-08-15T14:10:10"
    }
  ]
}
```

| Path | Type | Notes |
| --- | --- | --- |
| `ownership[]` | array | **One entry per file *and* contributor** — the same `file` appears once per contributor |
| `ownership[].file` | string | Repository-relative path |
| `ownership[].contributor` | string | Author name |
| `ownership[].modifications` | integer | Commits by this author touching the file |
| `ownership[].modify_percent` | float | Share of the file's modifications |
| `ownership[].lines_changed` | integer | Additions + deletions by this author |
| `ownership[].lines_percent` | float | Share of the file's churn |
| `ownership[].last_modified_by` | string | Most recent author of the file (repeated on every row for that file) |
| `ownership[].last_modified_at` | string \| null | ISO 8601 timestamp of that commit |

Group the flat list back into one entry per file:

```bash
gitintel --quiet ownership . --all --format json \
  | jq '.ownership | group_by(.file) | map({file: .[0].file, owners: length})'
```

## `gitintel hotspots --format json`

```json
{
  "repository": { "...": "see above" },
  "hotspots": [
    {
      "file": "src/gitintel/reports/terminal.py",
      "risk_score": 15,
      "changes": 1208,
      "contributors": 1,
      "owner": "ThePhoenix77",
      "reasons": []
    }
  ]
}
```

| Path | Type | Notes |
| --- | --- | --- |
| `hotspots[]` | array | Top 10 by `risk_score`, descending; files scoring `0` are omitted |
| `hotspots[].file` | string | Repository-relative path |
| `hotspots[].risk_score` | number | 1–100 |
| `hotspots[].changes` | integer | **Lines changed** (churn), not the modification count |
| `hotspots[].contributors` | integer | Distinct author names touching the file |
| `hotspots[].owner` | string \| null | Last author to modify the file |
| `hotspots[].reasons` | array of string | Any of `Frequently modified`, `High code churn`, `Many contributors`, `No clear owner`; empty when only mid-tier thresholds were hit |

## Parsing notes

- Output goes through a Rich console, which soft-wraps at the detected terminal width (80
  columns when redirected). Whitespace between tokens is insignificant for parsers, but set
  `COLUMNS=200` if you need byte-stable files.
- Always pass the global `--quiet` flag when redirecting, so progress spinners are not mixed
  into the stream.
- Percentages are unrounded IEEE-754 doubles; round them yourself for display.
- Timestamps are naive local-time ISO 8601 strings with no timezone offset.
