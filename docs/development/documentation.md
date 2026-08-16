# Working on the docs

This site is built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, from Markdown files
in `docs/`, and deployed to GitHub Pages by `.github/workflows/docs.yml`.

## Install the tooling

Documentation tools are not part of the `dev` extra:

```bash
source .venv/bin/activate
python -m pip install mkdocs-material
```

`mkdocs-material` pulls in `mkdocs`, `pymdown-extensions` and the rest of the required stack.

## Preview locally

```bash
mkdocs serve
```

Open <http://127.0.0.1:8000/GitIntel/>. The server rebuilds and reloads on save.

## Build the way CI does

```bash
mkdocs build --strict
```

`--strict` turns warnings — broken internal links, pages missing from `nav`, bad configuration —
into failures. The docs workflow runs it, so a broken link blocks deployment. The output goes to
`site/`, which is git-ignored.

## Configuration

Everything lives in `mkdocs.yml`:

| Section | Purpose |
| --- | --- |
| `site_*`, `repo_*`, `edit_uri` | Metadata, header repo link, and the per-page "edit" pencil |
| `theme.features` | Tabs, sections, instant navigation, code copy buttons |
| `theme.palette` | Automatic light/dark switching following the OS preference |
| `plugins: [search]` | Built-in client-side search — no external service |
| `markdown_extensions` | Admonitions, tabbed content, code highlighting, footnotes, task lists |
| `nav` | The complete navigation tree |

Mermaid diagrams are rendered through a `pymdownx.superfences` custom fence, so a fenced block
tagged `mermaid` becomes a diagram.

## Adding a page

1. Create the Markdown file under the appropriate directory in `docs/`.
2. Add it to `nav` in `mkdocs.yml` — a page not in `nav` is reachable only by URL.
3. Link to it from the section index page so readers can find it by browsing.
4. Run `mkdocs build --strict`.

Use relative links between pages, including the `.md` extension — MkDocs rewrites them and
validates them:

```markdown
See [Metrics and scoring](../concepts/metrics.md#hotspot-risk-score).
```

## Writing style

- Document behaviour that exists in the code today. If you cannot run the command and see it,
  do not write it.
- Paste real output rather than plausible-looking output.
- Keep commands copy-pasteable — one command per block, no shell prompts.
- Prefer tables for options, thresholds, and field lists.
- State limitations explicitly; a documented quirk is worth more than a silent one.
- Avoid marketing adjectives and avoid repeating content that already exists on another page —
  link to it instead.
- Terminology is defined in [Core concepts → Terminology](../concepts/terminology.md); use those
  words consistently.

Useful Material features:

```markdown
!!! warning "Global options come first"
    `gitintel --quiet analyze .` works; `gitintel analyze . --quiet` exits with code 2.
```

## Keeping docs and code in sync

| When you change… | Update… |
| --- | --- |
| A command, option, or help text | [CLI reference](../reference/cli.md) |
| A JSON field | [JSON output schema](../reference/json-schema.md) |
| A scoring threshold or formula | [Metrics and scoring](../concepts/metrics.md) |
| Module layout | [Components](../architecture/components.md), [Project structure](project-structure.md) |
| Public Python functions | [Python API](../reference/python-api.md) |
| Anything user-visible | `CHANGELOG.md` |

## Deployment

`.github/workflows/docs.yml` runs on every push to `main` that touches `docs/`, `mkdocs.yml`, or
the workflow itself. It builds with `--strict`, uploads the `site/` directory as a Pages
artifact, and deploys it to <https://thephoenix77.github.io/GitIntel/>. Pull requests build the
site but do not deploy, so link breakage is caught before merge.

GitHub Pages must be configured once, in **Settings → Pages → Build and deployment → Source →
GitHub Actions**.
