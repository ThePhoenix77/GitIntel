# Metrics and scoring

Every number GitIntel prints is defined here, with the exact rule that produces it.

## Repository summary

| Metric | Definition |
| --- | --- |
| `commits` | Count of commits reachable from `HEAD` |
| `contributors` | Count of distinct author email addresses |
| `files_changed` | Count of distinct file paths appearing in any commit diff |
| `last_commit` | Maximum commit timestamp in the walked history |

## Contributor statistics

For each author email:

| Field | Definition |
| --- | --- |
| `commits` | Commits authored by that email |
| `files_changed` | Distinct file paths that author touched |
| `additions` / `deletions` | Summed line statistics across that author's commits |
| `share` | `commits / total commits × 100` |

Contributors are sorted by commit count, descending.

## File activity

Used by the *Most Changed Files* table in `gitintel analyze`:

| Field | Definition |
| --- | --- |
| `changes` | Number of commits touching the file |
| `lines_changed` | Additions + deletions across those commits |

The top 10 files by `changes` are reported.

## Ownership metrics

For each file path, and each author name that touched it:

| Field | Definition |
| --- | --- |
| `modifications` | Commits by that author touching the file |
| `modify_percent` | `modifications / all modifications of that file × 100` |
| `lines_changed` | Additions + deletions by that author in that file |
| `lines_percent` | `lines_changed / all lines changed in that file × 100` |
| `last_modified_by` | Author of the newest commit touching the file |
| `last_modified_at` | Timestamp of that commit |

Two useful readings:

- **`modify_percent` ≈ 100** — a single author has done essentially all the work on the file.
  Historical ownership is unambiguous, but so is the bus factor.
- **`lines_percent` ≫ `modify_percent`** — the author made few but very large changes
  (an import, a generated file, or a rewrite).

### What ownership does *not* measure

Ownership is computed from **commit diffs**, not from `git blame` of the current file. A
contributor whose lines were later replaced still counts toward the file's history, and code
moved between files is attributed to whoever moved it. Ownership answers *"who has worked on
this file"*, not *"whose code is in this file right now"*.

## Hotspot risk score

`calculate_hotspots()` starts each file at `0` and applies four independent rules. Rules that
add a *reason* also flag it in the report; the intermediate tiers add points silently.

| Rule | Condition | Points | Reason recorded |
| --- | --- | --- | --- |
| Modification frequency | `modifications > 50` | +30 | `Frequently modified` |
| | `20 < modifications ≤ 50` | +15 | — |
| Code churn | `lines_changed > 3000` | +30 | `High code churn` |
| | `1000 < lines_changed ≤ 3000` | +15 | — |
| Contributor spread | `contributors > 5` | +25 | `Many contributors` |
| | `2 < contributors ≤ 5` | +10 | — |
| Ownership clarity | no owner resolved for the file | +15 | `No clear owner` |

The total is capped at `100`. **Files scoring `0` are excluded from the report entirely**, so a
quiet repository can legitimately produce an empty hotspot table.

Results are sorted by score, descending, and the report shows the top 10.

### Reading the score

| Score | Label | Interpretation |
| --- | --- | --- |
| 70–100 | `HIGH` | Multiple risk factors at once: change often, churn heavily, spread across people |
| 1–69 | `MED` | At least one factor is elevated |
| 0 | not reported | No rule triggered |

!!! note "`No clear owner` is rare in practice"
    The owner passed to the scorer comes from the ownership map, which contains an entry for
    every file seen in history. The rule therefore fires only for files present in the change
    statistics but absent from ownership data.

### Worked example

A file with 60 modifications, 1 500 lines changed, and 4 contributors, with a known owner:

```text
modifications 60 > 50      → +30  (Frequently modified)
lines_changed 1500 in (1000, 3000] → +15
contributors 4 in (2, 5]   → +10
owner resolved             →  +0
--------------------------------
risk_score = 55            → MED
```

## Repository health signals

`gitintel analyze` reports three fixed checks:

| Area | Condition | Status | Details text |
| --- | --- | --- | --- |
| Activity | `commits < 50` | OK | `Low change frequency` |
| | `50 ≤ commits < 500` | OK | `Normal development activity` |
| | `commits ≥ 500` | WARN | `High activity (N commits)` |
| Ownership | exactly 1 contributor | WARN | `Single contributor repository` |
| | 2–10 contributors | OK | `N contributors` |
| | more than 10 contributors | WARN | `N contributors` |
| Maintenance | newest commit ≤ 7 days old | OK | `Recently updated` |
| | 8–90 days | OK | `Maintained` |
| | more than 90 days | WARN | `No activity for N days` |

In terminal output `OK` renders as green `[OK]` and `WARN` as yellow `[!!]`.

!!! warning "`WARN` is a prompt, not a verdict"
    "High activity" and "more than 10 contributors" are warnings only in the sense that the
    repository is large enough that ownership needs deliberate attention. They are not defects.

## Determinism and stability

Given the same repository at the same `HEAD`, all metrics are deterministic — with one
exception: the `Maintenance` health signal and any relative day counts depend on the current
date, so they change over time even when the history does not.
