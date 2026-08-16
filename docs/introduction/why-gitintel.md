# Why GitIntel

Git already stores everything you need to understand how a codebase evolves. The problem is
that the built-in tools answer one question at a time, per invocation, in a format meant for
humans reading a single result.

## The gap GitIntel fills

Answering "who owns this file and how risky is it?" with plain Git usually looks like this:

```bash
git shortlog -sne -- src/gitintel/cli.py     # who touched it
git log --numstat -- src/gitintel/cli.py     # how much churn
git log -1 --format='%an %ad' -- src/...     # who touched it last
```

Repeat that for every file, aggregate it yourself, and you have the beginnings of an ownership
report. GitIntel does that pass once over the whole history and gives you the aggregate in
one command:

```bash
gitintel ownership . --format json
```

## Design goals

**One walk, many reports.**
The commit walk and per-commit diffs are the expensive part. GitIntel walks history once per
run and caches the intermediate results in memory, so summary, contributor, ownership, and
hotspot metrics are all derived from the same pass. See
[Analysis pipeline](../concepts/analysis-pipeline.md).

**Local and offline by default.**
Analysis uses libgit2 through `pygit2` against the local object database. No GitHub API calls,
no rate limits, and no credentials. A GitHub URL is handled by cloning it locally first, then
analyzing the clone like any other repository.

**Readable in a terminal, parseable in a pipeline.**
The same analysis renders as a Rich table for humans, JSON for scripts, and Markdown for pull
request comments or wiki pages — selected with a single `--format` flag.

**Small surface area.**
Three commands, four options, no configuration file, no state to manage. The only persistent
artifact is the clone cache described in
[Repository sources and cache](../concepts/repository-sources.md).

## What GitIntel deliberately is not

- **Not a code quality or static analysis tool.** It never parses your source code; it only
  reads commit metadata and diff line counts.
- **Not a forge client.** It does not read issues, pull requests, reviews, or CI results.
  Its only remote interaction is a `git clone` of a public GitHub URL.
- **Not a performance dashboard for people.** Contributor counts describe the code's history,
  not individual productivity. See [Best practices](../guide/best-practices.md) for how to
  read the numbers responsibly.
- **Not a blame-accurate ownership engine.** Ownership is attributed from commit diffs, not
  from `git blame` of the current file content. The difference matters and is explained in
  [Metrics and scoring](../concepts/metrics.md#what-ownership-does-not-measure).

## Comparison at a glance

| Question | Plain Git | GitIntel |
| --- | --- | --- |
| Top contributors | `git shortlog -sne` | `gitintel analyze .` (with file counts and share) |
| Churn per file | `git log --numstat` + manual aggregation | `gitintel analyze .` (Most Changed Files) |
| Per-file ownership split | one `git log` per file | `gitintel ownership .` |
| Risk ranking across files | not available | `gitintel hotspots .` |
| Machine-readable report | custom formatting flags per command | `--format json` on every command |
