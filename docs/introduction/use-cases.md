# Use cases

Each scenario below is a complete, copy-paste workflow built from the three GitIntel commands.

## Onboarding onto an unfamiliar codebase

Start with the shape of the repository, then find the files that carry the most history.

```bash
gitintel analyze https://github.com/ThePhoenix77/GitIntel
```

Read the output top to bottom:

1. **Repository Summary** — how large the history is and when it was last touched.
2. **Top Contributors** — who to ask questions.
3. **Most Changed Files** — the files where the project's real work happens.
4. **Repository Health** — activity, ownership concentration, and maintenance signals.

Then find who to ask about a specific file:

```bash
gitintel ownership . --file src/gitintel/cli.py
```

## Choosing a reviewer for a pull request

Ownership answers "who has the most context on this file" without guessing.

```bash
for file in $(git diff --name-only origin/main...HEAD); do
  gitintel ownership . --file "$file" --format markdown
done
```

The `Last Modified` column identifies the most recent toucher; the `Modify %` column
identifies the historical owner. Both are useful, and they are frequently different people.

## Risk review before a refactor

Hotspots rank files by change frequency, churn, contributor spread, and ownership clarity.

```bash
gitintel hotspots . --format table
```

Files scoring `HIGH` (≥ 70) are the ones where a refactor is most likely to conflict with
other work in flight and most likely to need more than one reviewer. The `reasons` field in
the JSON output tells you *why* each file scored the way it did:

```bash
gitintel hotspots . --format json | jq '.hotspots[] | {file, risk_score, reasons}'
```

## Bus-factor and ownership-concentration audit

A file whose entire history belongs to one contributor is a continuity risk.

```bash
gitintel ownership . --all --format json \
  | jq '[.ownership[] | select(.modify_percent == 100)] | map(.file) | unique'
```

At the repository level, the `Ownership` row of the health table in `analyze` flags both
single-contributor repositories and repositories with more than ten contributors.

## Posting a repository report on a pull request

Markdown output is designed to be pasted or piped straight into a comment.

```bash
gitintel analyze . --format markdown > analysis.md
gh pr comment "$PR_NUMBER" --body-file analysis.md
```

See [Automation and CI](../guide/automation.md) for a complete GitHub Actions job.

## Tracking a repository over time

GitIntel does not store history between runs, so snapshot the JSON output yourself:

```bash
gitintel analyze . --format json --quiet > "reports/$(date +%F).json"
```

Committing these snapshots (or uploading them as CI artifacts) gives you a trend line for
commit volume, contributor count, and hotspot scores.

!!! tip "Use `--quiet` in scripts"
    `--quiet` suppresses the progress spinners so only the report reaches stdout. It is a
    global option and must be placed before the subcommand: `gitintel --quiet analyze .`
