# Documentation roadmap

What exists today, what is planned, and how the documentation is maintained. Product features
are tracked in [issues](https://github.com/ThePhoenix77/GitIntel/issues); this page is about the
docs.

## Shipped

- Information architecture covering introduction, onboarding, concepts, task guides, reference,
  architecture, developer guide, troubleshooting, and project process.
- MkDocs Material site with client-side search, dark/light themes, code copy buttons, Mermaid
  diagrams, and per-page edit links.
- Automated GitHub Pages deployment, with `mkdocs build --strict` enforced on pull requests.
- CLI reference, JSON schema reference, and error/exit-code reference derived from the code and
  verified against real command output.

## Next

| Item | Why |
| --- | --- |
| Real terminal recordings or screenshots of each command | Static text under-sells what the reports look like |
| A copy-pasteable end-to-end tutorial on a well-known public repository | Gives readers reproducible numbers to compare against |
| Per-page "last reviewed" metadata (`mkdocs-git-revision-date-localized-plugin`) | Signals staleness to readers |
| Automated link checking in CI beyond `--strict` (external URLs) | Catches rot in outbound links |
| A short "interpreting the numbers responsibly" primer for managers | Metrics get misused; make the limits prominent |

## Later

| Item | Depends on |
| --- | --- |
| Versioned documentation with `mike` | The first 1.0 release, when older versions need their own docs |
| Generated CLI reference from the Typer app | A stable enough CLI that generation is cheaper than hand-writing |
| Generated API reference with `mkdocstrings` | Docstring coverage across the package, and a stable Python API |
| Recipes section (custom dashboards, Slack reports, exporters) | Real user workflows to document |
| Translations | Sustained non-English demand |

## Not planned

- A marketing landing page — the introduction serves that purpose.
- A blog or news section — the [changelog](changelog.md) covers what is new.
- Documentation for behaviour that does not exist yet.

## Maintenance rules

- A pull request that changes user-visible behaviour also changes the documentation; CI builds
  the site on every pull request.
- The pages listed in [Working on the docs](development/documentation.md#keeping-docs-and-code-in-sync)
  map each kind of code change to the page that must be updated.
- Examples are verified against real command output before being written down. If a value cannot
  be reproduced, it does not belong on the site.
- Known defects are documented explicitly — see the known issues table in the
  [changelog](changelog.md#known-issues) — and removed from the docs only when they are fixed.

## Contributing to the docs

Every page has an edit pencil in the header that opens the source file on GitHub. For larger
changes, follow [Working on the docs](development/documentation.md) and
[Contributing](contributing.md).
