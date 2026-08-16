# Best practices

## Interpreting the metrics honestly

**Metrics describe code, not people.** Commit counts and line totals measure activity in files,
not productivity or value. A contributor who reviews, designs, or debugs appears nowhere in
GitIntel's output. Do not use these reports for performance evaluation.

**Churn is not quality.** A file with high churn may be under active, healthy development. The
hotspot score points at files worth a conversation — it does not claim they are defective.

**Ownership is historical.** It is derived from commit diffs, so it describes who has worked on
a file, not whose code survives in it today. When "who wrote the line that broke" matters, use
`git blame`.

**Aggregate views hide imports.** A repository that started with a squashed import commit
attributes tens of thousands of lines to whoever performed the import. Check the *Most Changed
Files* table for a single enormous commit before drawing conclusions.

## Getting accurate data

- **Analyze a full clone.** Shallow clones (`--depth 1`) truncate history and every metric with
  it.
- **Know which branch you are on.** Analysis follows `HEAD`.
- **Normalize author identities first.** GitIntel does not apply `.mailmap`. If the same person
  commits under several names, consolidate their Git configuration going forward; historical
  entries will still appear separately.
- **Exclude nothing manually.** There is no ignore mechanism, so generated files and lockfiles
  will appear. Filter them out downstream with `jq`:

  ```bash
  gitintel --quiet hotspots . --format json \
    | jq '[.hotspots[] | select(.file | test("(lock|\\.min\\.)") | not)]'
  ```

## Large repositories

Runtime scales with the number of commits and the size of each commit's diff, because every
commit is diffed against its first parent.

- Expect a repository with tens of thousands of commits to take minutes, not seconds.
- The commit walk happens once per process, so prefer **one** command per report rather than
  running `analyze`, `ownership`, and `hotspots` in a tight loop over the same repository.
- Redirect JSON to a file once and query it repeatedly instead of re-running GitIntel:

  ```bash
  COLUMNS=200 gitintel --quiet analyze . --format json > analysis.json
  jq '.summary' analysis.json
  jq '.contributors[:5]' analysis.json
  ```

- Memory holds the entire commit list with per-file changes. Very large histories therefore
  use noticeably more RAM; if that becomes a problem, analyze a narrower branch.

## Scripting

- Put global options first: `gitintel --quiet analyze . --format json`.
- Set `COLUMNS` to a large value so Rich does not wrap long paths.
- Treat exit code `1` as "GitIntel could not answer" — an invalid repository or an unknown
  `--file` path. See [Exit codes and errors](../reference/errors.md).
- Do not parse the `table` format; it is intentionally cosmetic and truncates paths.

## Team workflows that work well

| Cadence | Command | Purpose |
| --- | --- | --- |
| Per pull request | `ownership --file` for each changed file | Reviewer selection |
| Per pull request | `hotspots --format markdown` | Flag risky files during review |
| Monthly | `analyze --format json`, archived | Trend of activity and contributor spread |
| Before a refactor | `hotspots` + `ownership --file` | Identify conflict-prone files and their owners |
| Onboarding | `analyze` then `ownership` | Orient a new contributor in a day, not a week |

## Privacy considerations

Reports contain author names, and JSON output for `analyze` includes contributor names but not
email addresses. Ownership output identifies contributors by name. Treat generated reports the
same way you treat your commit history — if the repository is private, its reports are too.
