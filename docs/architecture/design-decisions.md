# Design decisions

Why GitIntel is built the way it is, and what each choice costs.

## libgit2 (`pygit2`) instead of shelling out to `git`

**Decision.** All repository access goes through `pygit2`.

**Why.** Structured objects instead of parsed text, no dependency on a `git` binary being
installed or on its output format staying stable, and no per-commit process spawn — which
matters because GitIntel diffs every commit.

**Cost.** `pygit2` must be installable on the target platform; where no wheel exists, users
need a compiler and libgit2 headers. Behaviour also differs slightly from the `git` CLI (no
`.mailmap` handling, no user config for rename detection).

## Analyze `HEAD` only

**Decision.** The commit walk starts at `HEAD`; there are no `--branch`, `--since`, or
`--limit` flags.

**Why.** It keeps the CLI surface minimal and makes the result predictable: "what you have
checked out is what you get". Selecting history is already Git's job (`git checkout`).

**Cost.** No time-boxed reports and no branch comparison without running the tool twice.
`get_commits()` accepts a `limit` argument internally, so exposing it later is straightforward.

## Lazy, memoized analysis context

**Decision.** `analyze_repository()` returns an `AnalysisContext` whose metrics are cached
properties rather than computing everything eagerly.

**Why.** `gitintel hotspots` needs ownership and change statistics but not the contributor
table; `gitintel ownership` needs neither hotspots nor health. Laziness means each command pays
only for what it renders, while `analyze` still walks history once for four tables.

**Cost.** Work happens during rendering rather than at a well-defined "analysis" step, so
timing and error surfaces are less obvious than in an eager design.

## Diff against the first parent only

**Decision.** Merge commits are diffed against `parents[0]`.

**Why.** It matches `git log` default behaviour and avoids double-counting: changes introduced
on a branch are attributed to the commits that made them, not to the merge that integrated
them.

**Cost.** Conflict resolutions performed inside a merge commit are invisible, and repositories
that squash-merge attribute everything to the squashed commit's author.

## Ownership by author name, contributors by email

**Decision.** `analyze_ownership()` groups by `commit.author` (name);
`analyze_contributors()` groups by `commit.email`.

**Why.** Ownership output is read by humans looking for a person to talk to, where a display
name is most useful. Contributor counts want a stable identity, where the email is more
reliable.

**Cost.** The two views can disagree — one person with two emails is one owner but two
contributors, while two people sharing a display name merge in ownership. Documented in
[Terminology](../concepts/terminology.md#contributor).

## Threshold-based hotspot scoring

**Decision.** Fixed, hard-coded thresholds (50/20 modifications, 3000/1000 lines, 5/2
contributors, +15 for no owner), capped at 100.

**Why.** The rules are transparent and explainable — every point can be traced to a condition,
and the top tiers emit a human-readable reason. A statistical model would be harder to justify
in a review conversation and would behave unpredictably on small repositories.

**Cost.** The thresholds are absolute rather than relative to the repository, so a young
project produces mostly low scores and a decade-old monolith produces mostly high ones. They
are not configurable today.

## Three output formats, one analysis

**Decision.** `--format table|json|markdown` selects a renderer over identical data.

**Why.** The same command serves a human at a terminal, a CI script, and a pull request comment
without a separate export path.

**Cost.** Three renderers per report must be kept in sync — a field added to JSON is easy to
forget in Markdown. Renderers also print through Rich, which soft-wraps machine-readable output
at the terminal width (see [Output formats](../guide/output-formats.md#piping-json-safely)).

## Cache remote clones, never refresh them

**Decision.** GitHub URLs are cloned into `~/.cache/gitintel/<owner>__<repo>` and reused as-is;
a directory that fails to open is deleted and re-cloned.

**Why.** Repeated analysis of the same public repository is fast and works offline, and
GitIntel never has to decide when a fetch is appropriate.

**Cost.** A cached clone silently ages. Users must refresh or delete it themselves — documented
in [Repository sources and cache](../concepts/repository-sources.md#the-clone-cache).

## Deleting only `gitintel_*` directories

**Decision.** `cleanup_repository()` checks the directory name prefix before removing anything.

**Why.** The cleanup path runs in a `finally` block on every command. A guard that cannot
delete a user-supplied path is worth more than the small amount of temp space it occasionally
leaks.

**Cost.** Temporary clones created with a non-standard prefix would never be cleaned up.

## No configuration file

**Decision.** No `.gitintelrc`, no `pyproject.toml` section, no ignore lists.

**Why.** Zero-configuration tools are adoptable in one command, and every current behaviour is
expressible in flags. Filtering is delegated to `jq` and shell pipelines.

**Cost.** Repository-specific policies (exclude lockfiles, tune thresholds) must be re-expressed
at every call site. If the same options start appearing in everyone's scripts, that is the
signal to add configuration.

## In-memory analysis

**Decision.** The entire commit list with per-file changes is held in memory; nothing is
streamed or persisted.

**Why.** It makes the metric functions pure list transformations and keeps the code readable.

**Cost.** Memory grows with history size, and there is no incremental mode: a repository with
hundreds of thousands of commits is analyzed from scratch on every run.
