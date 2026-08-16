# Exit codes and errors

## Exit codes

| Code | Meaning | Typical cause |
| --- | --- | --- |
| `0` | Success | Report printed, or `--help` / `--version` requested |
| `1` | Analysis failure | Invalid repository, clone failure, cancelled clone, `--file` matched nothing |
| `2` | Usage error | Unknown option or command, or no command given |

Scripts should treat `1` as "GitIntel could not answer the question" and `2` as "the command
line was wrong".

## Error messages

Errors raised as `ValueError` during resolution or analysis are rendered inside a red `Error`
panel and exit with code `1`:

```text
╭─────────────────────────────────── Error ────────────────────────────────────╮
│ Invalid Git repository: /tmp                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### `Invalid Git repository: <path>`

**Commands:** all · **Exit code:** `1`

libgit2 could not open the path. Usual causes:

- the path is not inside a Git repository
- the path does not exist or has a typo
- you passed a non-GitHub URL (for example an SSH remote or a GitLab URL), which GitIntel
  treats as a filesystem path

```bash
git -C <path> rev-parse --git-dir     # confirm it is a repository
```

For non-GitHub or SSH remotes, clone first and analyze the local clone — see
[Repository sources and cache](../concepts/repository-sources.md#recognized-url-forms).

### `Unable to clone repository: <url>`

**Commands:** all, when given a GitHub URL · **Exit code:** `1`

The clone failed. Common reasons: the repository is private (GitIntel clones without
credentials), the URL is misspelled, there is no network access, or a proxy blocks the request.
Verify with plain Git:

```bash
git clone --depth 1 https://github.com/owner/repo /tmp/probe
```

If that works but GitIntel does not, remove a possibly broken cache entry:

```bash
rm -rf ~/.cache/gitintel/owner__repo
```

### `Cloning cancelled by user`

**Commands:** all, when cloning · **Exit code:** `1`

You interrupted the clone with ++ctrl+c++. The partially downloaded temporary directory is
removed automatically. A partially written *cache* directory is detected and re-cloned on the
next run.

### `File not found: <path>`

**Command:** `ownership --file` · **Exit code:** `1`

No file with that exact path exists in the analyzed history. The path must be
repository-relative with forward slashes and no `./` prefix, and it must appear in a commit —
a file that is only staged or untracked will not match.

```bash
# list the paths GitIntel knows about
gitintel --quiet ownership . --all --format json | jq -r '.ownership[].file' | sort -u
```

### `No ownership data found.`

**Command:** `ownership` · **Exit code:** `0`

Printed (in yellow) when the analysis produced no ownership rows at all — typically an empty
repository. This is a message, not an error, so the exit code stays `0`.

## Unhandled exceptions

`pretty_exceptions_enable=False` is set on the Typer application, so anything not converted to
a `ValueError` surfaces as a normal Python traceback. Two known cases:

| Trigger | Symptom |
| --- | --- |
| Repository with no commits (`HEAD` unborn) | `pygit2.GitError` traceback from the commit walk |
| Corrupted object database | libgit2 error traceback |

Please [open an issue](https://github.com/ThePhoenix77/GitIntel/issues) with the traceback and
the command you ran if you hit one of these.

## Silent behaviours worth knowing

| Behaviour | Detail |
| --- | --- |
| Unknown `--format` value | Falls back to `table` with no warning |
| `--all` combined with `--file` | `--file` wins; `--all` is ignored |
| Empty hotspot report | Correct output when no file triggers a scoring rule |
| Cached remote clone | Reused as-is; GitIntel never fetches new commits for it |
