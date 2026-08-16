# Terminology

Definitions used consistently across this documentation, the CLI output, and the source code.

## Source

The repository argument you pass to a command: either a filesystem path (`.`,
`/srv/projects/api`) or a GitHub URL (`https://github.com/owner/repo`). Only `http(s)` URLs on
`github.com` are treated as remote; everything else is opened as a local path.

## Repository context

Metadata collected about the analyzed repository — path, source string, owner, repository
name, branch, remote URL, source type (`GitHub` or `Local`), and whether the checkout is
temporary. Modelled by `RepositoryContext` and shown in the panel at the top of every report.

## Commit

A commit reachable from `HEAD`, reduced to the fields GitIntel needs: hash, author name,
author email, message, date, and the list of file changes it introduced. Modelled by `Commit`.

!!! info "Date semantics"
    The `date` field comes from the commit's **commit time** (not the author time) and is
    rendered in the machine's local timezone.

## File change

One file's additions and deletions inside a single commit, modelled by `FileChange`.
Additions and deletions are libgit2 line statistics for that file's patch. For the initial
commit — which has no parent to diff against — every file in the tree is recorded as an
addition of its line count.

## Contributor

An author identity aggregated across commits. Contributors are keyed by **author email**. The
displayed name is taken from the last commit processed for that email — because history is
walked newest-first, that is the *oldest* commit written by that address. Two email
addresses used by the same human produce two contributors; a `.mailmap` file is **not**
applied.

Per contributor GitIntel tracks: commit count, distinct files touched, total additions, and
total deletions (`Contributor`).

## Ownership

Per-file attribution of work, keyed by **author name** (not email), containing:

- `modifications` — how many commits by that author touched the file
- `lines_changed` — additions plus deletions by that author in that file
- `last_modified_by` / `last_modified_at` — the most recent author and timestamp

Modelled by `FileOwnership`. Note the deliberate difference from contributors: ownership groups
by name, contributor statistics group by email.

## Owner

In hotspot output, the *owner* of a file is its **last modifier** (`last_modified_by`), not the
contributor with the largest share. When you need the majority owner, read the `Modify %`
column of [`gitintel ownership`](../guide/ownership-analysis.md) instead.

## Churn (lines changed)

Additions plus deletions. Churn measures how much a file has been rewritten over time; it is
unrelated to the file's current size. A 50-line file rewritten ten times has more churn than a
5 000-line file added once.

## Modification count

How many commits touched a file. Used both as the ranking key for the default
`gitintel ownership` view and as an input to the hotspot score.

## Hotspot

A file with a non-zero risk score, ranked by that score. Risk is a heuristic combining
modification count, churn, contributor spread, and whether an owner could be determined —
see [Metrics and scoring](metrics.md#hotspot-risk-score). Files that trigger no rule at all
are omitted from the hotspot report entirely.

## Risk score

An integer from 1 to 100 (capped) accumulated from the hotspot rules. In table and Markdown
output it is labelled `HIGH` at 70 or above and `MED` below that.

## Repository health signal

One of three fixed checks (`Activity`, `Ownership`, `Maintenance`) reported by
`gitintel analyze` with an `OK` or `WARN` status and a short explanation.

## Report format

The renderer selected by `--format`: `table` (Rich terminal tables), `json` (machine-readable),
or `markdown` (documentation-friendly). Unrecognized values fall back to `table`.
