# Automation and CI

GitIntel needs no configuration or credentials, which makes it easy to run in CI. The only
requirement worth remembering: **it needs the full commit history**.

!!! danger "Shallow clones produce misleading numbers"
    `actions/checkout` fetches a single commit by default. Set `fetch-depth: 0` or every report
    will describe one commit.

## Repository report on every pull request

```yaml title=".github/workflows/repo-report.yml"
name: Repository report

on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install GitIntel
        run: python -m pip install gitintel

      - name: Build report
        env:
          COLUMNS: "200"
        run: |
          {
            gitintel --quiet analyze . --format markdown
            echo
            gitintel --quiet hotspots . --format markdown
          } > report.md

      - name: Comment on the pull request
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh pr comment "${{ github.event.number }}" --body-file report.md
```

## Reviewer suggestions for changed files

```yaml
      - name: Suggest reviewers
        run: |
          for file in $(git diff --name-only "origin/${{ github.base_ref }}...HEAD"); do
            gitintel --quiet ownership . --file "$file" --format json 2>/dev/null \
              | jq -r --arg f "$file" \
                  '.ownership | max_by(.modifications) | "\($f): \(.contributor)"' || true
          done
```

`gitintel ownership --file` exits with code `1` when the path has no history (a brand-new
file), so guard the loop with `|| true`.

## Risk gate

Fail the build when a high-risk hotspot appears:

```yaml
      - name: Enforce hotspot budget
        run: |
          gitintel --quiet hotspots . --format json > hotspots.json
          count=$(jq '[.hotspots[] | select(.risk_score >= 70)] | length' hotspots.json)
          echo "High-risk files: $count"
          test "$count" -eq 0
```

Start by only reporting the number; turn it into a hard gate once you know the baseline.

## Scheduled history snapshots

Trend data requires storing results yourself:

```yaml
name: Weekly repository snapshot

on:
  schedule:
    - cron: "0 6 * * 1"
  workflow_dispatch:

jobs:
  snapshot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install gitintel
      - run: |
          mkdir -p snapshots
          COLUMNS=200 gitintel --quiet analyze . --format json \
            > "snapshots/$(date +%F).json"
      - uses: actions/upload-artifact@v4
        with:
          name: gitintel-snapshot
          path: snapshots/
```

## Pre-commit / local hooks

GitIntel analyzes committed history, so a `pre-commit` hook adds little value. A `post-merge`
hook that refreshes a local report is more useful:

```bash title=".git/hooks/post-merge"
#!/usr/bin/env bash
COLUMNS=200 gitintel --quiet hotspots . --format markdown > .git/gitintel-hotspots.md
```

## Running against another repository from CI

```bash
gitintel --quiet analyze https://github.com/owner/repo --format json
```

The clone is written to `$XDG_CACHE_HOME/gitintel` (or `~/.cache/gitintel`). Cache that
directory between runs to avoid re-cloning, and remember GitIntel never refreshes a cached
clone — see [Repository sources and cache](../concepts/repository-sources.md).

## Checklist for automated runs

- [x] `fetch-depth: 0` (or a full clone)
- [x] Global `--quiet` before the subcommand
- [x] `COLUMNS=200` (or larger) so long paths are not wrapped
- [x] `--format json` for logic, `--format markdown` for humans
- [x] Handle exit code `1` (invalid repository, unknown `--file`)
