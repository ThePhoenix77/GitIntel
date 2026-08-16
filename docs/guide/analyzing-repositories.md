# Analyzing repositories

`gitintel analyze` is the repository-wide overview: history size, contributors, the files that
change most, and three health signals.

```bash
gitintel analyze [PATH] [--format table|json|markdown]
```

`PATH` defaults to `.` and may be a local path or a public GitHub URL.

## Typical runs

```bash
# current repository
gitintel analyze .

# another checkout
gitintel analyze /srv/projects/api

# a public GitHub project (cloned into the cache on first use)
gitintel analyze https://github.com/ThePhoenix77/GitIntel

# machine-readable, no spinners
gitintel --quiet analyze . --format json
```

## What you get

| Section | Contents | Available in |
| --- | --- | --- |
| Repository panel | name, owner, branch, path, source type, remote | table, markdown, json (`repository`) |
| Repository Summary | commits, contributors, files changed, last commit | all formats |
| Top Contributors | commits, distinct files, share of commits | all formats |
| Most Changed Files | top 10 files by number of touching commits | all formats |
| Repository Health | Activity, Ownership, Maintenance signals | all formats |

Definitions for each field are in [Metrics and scoring](../concepts/metrics.md).

## Analyzing a specific branch or tag

Analysis always follows `HEAD`, so select the history you want with Git first:

```bash
git checkout release/2.0
gitintel analyze .
```

To compare two branches, run the command twice and diff the JSON:

```bash
git checkout main    && gitintel --quiet analyze . --format json > main.json
git checkout develop && gitintel --quiet analyze . --format json > develop.json
diff <(jq .summary main.json) <(jq .summary develop.json)
```

## Extracting single values

```bash
# how many commits are in this history?
gitintel --quiet analyze . --format json | jq '.summary.commits'

# contributors above a 10% share
gitintel --quiet analyze . --format json \
  | jq -r '.contributors[] | select(.share > 10) | "\(.name)\t\(.share | floor)%"'

# fail a script if the repository has a single contributor
gitintel --quiet analyze . --format json \
  | jq -e '.repository_health[] | select(.area == "Ownership" and .status == "WARN")' \
  && echo "ownership warning raised"
```

## Interpreting the result

- **Few commits, many files changed** — the history probably starts from an import commit.
  Numbers before that import do not exist; ownership will look concentrated.
- **One contributor with most commits but few files** — deep, focused work; a good person to
  ask about that area.
- **Most Changed Files dominated by docs or lockfiles** — expected; these churn constantly and
  rarely represent risk. Use [`hotspots`](hotspot-analysis.md) to weight risk instead.
- **Maintenance `WARN`** — no commit in the last 90 days. For an intentionally finished library
  this is fine; for an actively used service it deserves a look.

## Limitations

- No date filtering (`--since`/`--until`) and no commit limit in the CLI today; the full
  history reachable from `HEAD` is analyzed.
- Merge commits are diffed against their first parent only.
- Author identities are not deduplicated through `.mailmap`.

See [Documentation roadmap](../roadmap.md) for how these are tracked.
