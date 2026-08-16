# Hotspot analysis

`gitintel hotspots` ranks files by a heuristic risk score so you can see where change,
churn, and people concentrate.

```bash
gitintel hotspots [PATH] [--format table|json|markdown]
```

## Running it

```bash
gitintel hotspots .
gitintel hotspots https://github.com/ThePhoenix77/GitIntel
gitintel --quiet hotspots . --format json | jq '.hotspots[] | {file, risk_score, reasons}'
```

Output is limited to the **top 10 files by risk score**. Files that trigger no rule score `0`
and are not reported at all.

## The report

```text
                              Repository Hotspots
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ File                          ┃ Risk    ┃ Changes ┃ Contributors ┃ Owner        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ src/gitintel/reports/termi…   │ MED 15  │ 1208    │ 1            │ ThePhoenix77 │
└───────────────────────────────┴─────────┴─────────┴──────────────┴──────────────┘
```

| Column | Meaning |
| --- | --- |
| `File` | Repository-relative path (truncated to fit the terminal) |
| `Risk` | `HIGH` at score ≥ 70, otherwise `MED`, followed by the numeric score |
| `Changes` | **Lines changed** (churn), not the number of commits — see the note below |
| `Contributors` | Distinct author names that touched the file |
| `Owner` | The **last** author to modify the file |

!!! warning "`Changes` is churn"
    In the hotspot report the `Changes` column (and the `changes` field in JSON) carries the
    file's *lines changed* total. The modification count that feeds the score is not displayed;
    read it from [`gitintel ownership`](ownership-analysis.md) if you need it.

## How the score is built

| Signal | Threshold | Points |
| --- | --- | --- |
| Modifications | `> 50` / `> 20` | +30 / +15 |
| Lines changed | `> 3000` / `> 1000` | +30 / +15 |
| Contributors | `> 5` / `> 2` | +25 / +10 |
| No owner resolved | — | +15 |

Capped at 100. The full table, including which rules record a human-readable reason, is in
[Metrics → hotspot risk score](../concepts/metrics.md#hotspot-risk-score).

Only the top tier of each signal records a reason, so a `MED 15` file legitimately shows an
empty `reasons` list in JSON:

```json
{
  "file": "src/gitintel/reports/terminal.py",
  "risk_score": 15,
  "changes": 1208,
  "contributors": 1,
  "owner": "ThePhoenix77",
  "reasons": []
}
```

## Acting on hotspots

| Pattern | What it usually means | Reasonable action |
| --- | --- | --- |
| High modifications + high churn + many contributors | A central file everyone edits | Split responsibilities, add tests, require two reviewers |
| High churn, one contributor | Deep single-owner work | Bus-factor risk — pair or document |
| High modifications, low churn | Small repeated edits (config, registries) | Usually benign |
| Generated files or lockfiles at the top | Machine-produced churn | Ignore, or exclude them from your review policy |

Hotspots are a **prompt for a conversation**, not a defect list. Nothing in the score inspects
code quality.

## Automating a risk gate

Fail CI when any file crosses a threshold you choose:

```bash
gitintel --quiet hotspots . --format json \
  | jq -e '[.hotspots[] | select(.risk_score >= 70)] | length == 0' > /dev/null \
  || { echo "High-risk hotspots detected"; exit 1; }
```

A full workflow is in [Automation and CI](automation.md).

## Known limitation

The terminal (`table`) renderer prints the hotspot table twice in version `0.1.0`. The data is
identical in both copies; JSON and Markdown output are unaffected. Tracked in
[Troubleshooting → known issues](../troubleshooting/index.md#the-hotspots-table-prints-twice).
