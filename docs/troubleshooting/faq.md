# FAQ

## General

### What does GitIntel actually do?

It walks the commits reachable from `HEAD`, diffs each one, and turns the result into three
reports: a repository overview with contributors and health signals (`analyze`), per-file
ownership (`ownership`), and risk-scored files (`hotspots`). See
[Why GitIntel](../introduction/why-gitintel.md).

### Does it send my code anywhere?

No. Everything runs locally through libgit2. The only network access is cloning a public GitHub
URL you explicitly pass as the source; local paths trigger no network activity at all.

### Does it need a `git` binary?

No. Repository access goes through `pygit2` (libgit2 bindings), not a `git` subprocess.

### Is there a configuration file?

No. All behaviour is controlled by command-line flags. See
[Design decisions](../architecture/design-decisions.md#no-configuration-file).

### `gitintel` or `gitit`?

Identical. Both console scripts, and `python -m gitintel`, invoke the same Typer application.

## Usage

### Can I analyze a private repository?

Not by URL — the clone is anonymous. Clone it yourself and analyze the local path:

```bash
git clone git@github.com:owner/private-repo.git
gitintel analyze private-repo
```

### Can I analyze a specific branch, tag, or date range?

Not with a flag. Analysis always starts at `HEAD`, so check out what you want first:

```bash
git checkout release/2.0
gitintel analyze .
```

There is no `--since`/`--until`; a depth-limited clone is the closest approximation.

### Can I exclude generated files like lockfiles?

Not inside GitIntel. Use JSON output and filter:

```bash
gitintel --quiet hotspots . --format json \
  | jq '[.hotspots[] | select(.file | test("lock|dist/|vendor/") | not)]'
```

### Which output format should I use?

`table` for reading, `json` for scripts and CI gates, `markdown` for pull request comments and
reports. Comparison: [Output formats](../guide/output-formats.md).

### How do I use it in CI?

Set `fetch-depth: 0` on checkout, run with `--quiet --format json` or `markdown`, and gate on a
`jq` expression. Full workflows: [Automation and CI](../guide/automation.md).

### Why must `--quiet` come before the command?

It is defined on the application callback, not on individual commands, so Typer only accepts it
before the subcommand. `gitintel analyze . --quiet` is a usage error (exit code `2`).

## Results and interpretation

### Is a high risk score a bug?

No. The score measures change activity, spread of authorship, and missing ownership — not
correctness. It marks files worth extra review attention. The rules and thresholds are listed in
[Metrics and scoring](../concepts/metrics.md#hotspot-risk-score).

### Is "owner" the same as `git blame`?

No. GitIntel's owner is the author with the most modifications to a file across history, and
`last_modified_by` is simply the most recent author. Neither is a line-level blame result.

### Why do contributor and ownership views disagree?

Contributors are grouped by email; ownership is grouped by author name. One person using two
emails is one owner but two contributors. See
[Design decisions](../architecture/design-decisions.md#ownership-by-author-name-contributors-by-email).

### Does it honour `.mailmap`?

No. Identity mapping is not implemented.

### Why does the initial commit show so many additions?

The first commit has no parent, so GitIntel counts every line of every file in the tree as an
addition — the same convention `git show` uses for a root commit.

### How are merge commits handled?

Diffed against their first parent only, matching `git log`'s default. Changes are attributed to
the commits that introduced them, not to the merge.

### Why does `Changes` in the hotspot table look so large?

That column is total lines changed (additions + deletions), not the number of commits. The
modification count is a separate column.

### Are results deterministic?

For a fixed repository state, yes. They change as history grows, and a shallow clone yields
different numbers than a full one.

## Performance

### How long does an analysis take?

Roughly linear in the number of commits, dominated by one diff per commit. Small repositories
are instant; repositories with tens of thousands of commits take minutes.

### Can I speed it up?

Analyze a depth-limited clone, or run once with `--format json` and reuse the output for
multiple queries instead of running the tool several times.

### Where is the clone cache and how big does it get?

`$XDG_CACHE_HOME/gitintel` or `~/.cache/gitintel`, one full clone per remote repository
(`owner__repo`). Delete directories you no longer need:

```bash
rm -rf ~/.cache/gitintel
```

## Project

### Which Python versions are supported?

3.11 and newer. CI tests 3.11, 3.12, 3.13, and 3.14.

### Is the Python API stable?

No. Before 1.0, module paths, function signatures, and dataclass fields may change in any minor
release. The CLI and JSON output are the supported interfaces —
[Python API](../reference/python-api.md).

### How do I report a bug or request a feature?

[Open an issue](https://github.com/ThePhoenix77/GitIntel/issues) with the command you ran, the
full output, `gitintel version`, `python -V`, and your OS. Contribution process:
[Contributing](../contributing.md).

### What is the licence?

MIT. See [LICENSE](https://github.com/ThePhoenix77/GitIntel/blob/main/LICENSE).
