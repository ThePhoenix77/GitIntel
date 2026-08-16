# Common issues

Symptom-first troubleshooting. Exit codes and error message reference:
[Exit codes and errors](../reference/errors.md).

## Installation

### `gitintel: command not found`

The package installed, but its script directory is not on `PATH`.

```bash
python -m gitintel version        # works regardless of PATH
python -m pip show -f gitintel    # find where the script landed
```

Fixes:

- **pipx** — run `pipx ensurepath`, then open a new shell.
- **pip --user** — add `~/.local/bin` (Linux/macOS) or the printed `Scripts` directory (Windows)
  to `PATH`.
- **virtual environment** — activate it: `source .venv/bin/activate`.

### Install hangs or fails resolving dependencies

Almost always Python < 3.11. Check first:

```bash
python -V
```

GitIntel requires 3.11+. Under 3.10 pip backtracks through incompatible releases and can appear
to hang for many minutes. Install with a newer interpreter:

```bash
python3.12 -m pip install gitintel
# or
uv tool install gitintel --python 3.12
```

### `pygit2` fails to build

No prebuilt wheel exists for your platform/Python combination, so pip is compiling libgit2
bindings. Either use a Python version that has a wheel (3.11–3.13 on common platforms), or
install libgit2 development headers first (`libgit2-dev` on Debian/Ubuntu, `brew install
libgit2` on macOS).

## Running an analysis

### `Invalid Git repository: <path>`

The path is not a Git repository, or the "URL" you passed was not recognised as a GitHub URL and
was treated as a path.

```bash
git -C <path> rev-parse --git-dir
```

Only `https://github.com/...` (and `github.com/...`) forms are cloned. SSH remotes
(`git@github.com:...`), GitLab, Bitbucket, and self-hosted servers must be cloned manually and
analyzed as a local path — see
[Repository sources and cache](../concepts/repository-sources.md).

### `Unable to clone repository: <url>`

Private repository, wrong URL, or no network. GitIntel clones anonymously and has no credential
support. For a private repository:

```bash
git clone git@github.com:owner/private-repo.git
gitintel analyze private-repo
```

### The command hangs on a large repository

GitIntel diffs every commit reachable from `HEAD`; a repository with tens of thousands of
commits takes minutes. Confirm progress with the spinner (do not pass `--quiet` while
diagnosing), and consider analyzing a smaller clone:

```bash
git clone --depth 2000 https://github.com/owner/repo shallow-repo
gitintel analyze shallow-repo
```

Depth-limited clones give faster but partial results.

## Unexpected results

### Numbers look stale for a GitHub URL

The clone cache is never refreshed. Delete the entry and rerun:

```bash
rm -rf ~/.cache/gitintel/owner__repo
gitintel analyze https://github.com/owner/repo
```

### Only one commit is reported

You are analyzing a shallow clone. CI checkouts default to depth 1:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

Locally: `git fetch --unshallow`.

### The results are for the wrong branch

Analysis always starts at `HEAD`. Check out the branch you want first:

```bash
git checkout main
gitintel analyze .
```

### One person appears twice

Contributors are grouped by author email, and GitIntel does not read `.mailmap`. Commits made
with different emails count as different contributors. Normalising the history's identities (or
your local `git config user.email`) is the only fix today.

### `File not found: <path>` from `ownership --file`

The path must match a path recorded in history exactly — repository-relative, forward slashes,
no `./` prefix, and it must appear in at least one commit.

```bash
gitintel --quiet ownership . --all --format json | jq -r '.ownership[].file' | sort -u
```

### `hotspots` prints nothing

Correct behaviour when no file crosses a scoring threshold — common on young or small
repositories. Files with a score of zero are omitted entirely. Thresholds:
[Metrics and scoring](../concepts/metrics.md#hotspot-risk-score).

### The hotspots table prints twice

A known defect in `print_hotspots_table()`: the table is constructed and printed twice. JSON and
Markdown output are unaffected, so use `--format json` when the duplication matters.

## Output

### JSON is wrapped across lines

Rich soft-wraps output at the terminal width. The document is still valid JSON when piped, but
if a consumer is confused by the wrapping:

```bash
COLUMNS=200 gitintel --quiet analyze . --format json > report.json
```

### Extra spinners or banners in captured output

Use the global `--quiet` flag — **before** the subcommand:

```bash
gitintel --quiet analyze . --format json
```

`gitintel analyze . --quiet` exits with code `2`, because `--quiet` is not a command option.

### Colour codes in a file or CI log

Rich disables styling when stdout is not a terminal. If something still injects colour, set:

```bash
NO_COLOR=1 TERM=dumb gitintel --quiet analyze . --format markdown > report.md
```

## Still stuck?

Check the [FAQ](faq.md), then
[open an issue](https://github.com/ThePhoenix77/GitIntel/issues) with the exact command, the
full output, `gitintel version`, `python -V`, and your operating system.
