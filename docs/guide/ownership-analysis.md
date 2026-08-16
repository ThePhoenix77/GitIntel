# Ownership analysis

`gitintel ownership` answers "who has worked on this file, and how much?" for every file in
history.

```bash
gitintel ownership [PATH] [--all] [--file FILE] [--format table|json|markdown]
```

## Three modes

=== "Top files (default)"

    ```bash
    gitintel ownership .
    ```

    Reports the **20 files with the most modifications**, each with one row per contributor.
    This is the view to start from.

=== "Every file"

    ```bash
    gitintel ownership . --all
    ```

    Reports every file that appears anywhere in history, in the order files were first seen —
    not sorted. Expect long output; pair it with `--format json` and a filter.

=== "One file"

    ```bash
    gitintel ownership . --file src/gitintel/cli.py
    ```

    Reports one file. The path must match the path recorded in the commit diffs **exactly**:
    repository-relative, forward slashes, no `./` prefix. A non-matching value prints
    `File not found: <path>` and exits with code `1`.

!!! note "`--file` wins over `--all`"
    When `--file` is given, `--all` has no effect — the filter is applied first and the result
    is never truncated.

## Reading the columns

```text
| File                | Contributor    | Modifications | Modify % | Lines Changed | Lines % | Last Modified                      |
|---------------------|----------------|---------------|----------|---------------|---------|------------------------------------|
| README.md           | Boussaden Taha | 1             | 50.0%    | 5             | 2.8%    | Boussaden Taha 2026-08-15 14:10:10 |
| README.md           | ThePhoenix77   | 1             | 50.0%    | 176           | 97.2%   |                                    |
```

| Column | Meaning |
| --- | --- |
| `Contributor` | Author **name** (ownership groups by name, unlike contributor statistics which group by email) |
| `Modifications` | Commits by that author touching the file |
| `Modify %` | Share of the file's commits |
| `Lines Changed` | Additions + deletions by that author in that file |
| `Lines %` | Share of the file's total churn |
| `Last Modified` | Filled only on the row of the author who touched the file most recently |

In the example above the two authors have an equal *commit* share but very different *line*
shares: one wrote the file, the other made a small edit — and made it last.

## Practical recipes

**Pick a reviewer for the files a branch touches**

```bash
for f in $(git diff --name-only origin/main...HEAD); do
  gitintel --quiet ownership . --file "$f" --format json \
    | jq -r --arg f "$f" '.ownership | max_by(.modifications) | "\($f)\t\(.contributor)"'
done
```

**List single-owner files (bus-factor risk)**

```bash
gitintel --quiet ownership . --all --format json \
  | jq -r '.ownership[] | select(.modify_percent == 100) | .file' | sort -u
```

**Find files nobody has touched recently**

```bash
gitintel --quiet ownership . --all --format json \
  | jq -r '.ownership[] | "\(.last_modified_at)\t\(.file)"' | sort -u | head -20
```

**Produce an ownership section for a wiki page**

```bash
gitintel --quiet ownership . --format markdown > docs/ownership.md
```

## Caveats

- Ownership is computed from commit diffs, not `git blame`; it describes *work done*, not
  *lines currently present*. See
  [Metrics → what ownership does not measure](../concepts/metrics.md#what-ownership-does-not-measure).
- Deleted and renamed files remain in the report because they exist in history. Rename
  detection is enabled when diffing, so a rename is attributed to the new path.
- Authors are identified by the name in the commit; inconsistent names (`Jane D.` vs
  `Jane Doe`) appear as separate contributors.
- Very large repositories produce very large `--all` output; prefer JSON plus a filter.
