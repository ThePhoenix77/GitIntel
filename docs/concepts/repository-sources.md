# Repository sources and cache

Every command accepts one repository argument. How GitIntel handles it depends on whether it
looks like a GitHub URL.

```mermaid
flowchart TD
    S[source argument] --> Q{starts with<br/>http(s)://github.com/ ?}
    Q -- no --> L[open path with pygit2]
    Q -- yes --> N[normalize URL → append .git]
    N --> C{cache directory exists<br/>and opens cleanly?}
    C -- yes --> R[reuse cached clone]
    C -- no --> K[clone into cache]
    K --> R
    L --> X[RepositoryContext]
    R --> X
```

## Local repositories

```bash
gitintel analyze .
gitintel analyze /srv/projects/api
gitintel ownership ~/code/service --all
```

The path is opened in place — nothing is copied, fetched, or modified. Any path libgit2 can
open works, including a bare repository or a worktree. If the path is not a repository the
command fails with `Invalid Git repository: <path>` and exit code `1`.

Because analysis follows `HEAD`, the currently checked-out branch determines the result:

```bash
git checkout release/2.0
gitintel analyze .          # analyzes release/2.0 history
```

!!! note "Uncommitted work is invisible"
    GitIntel reads committed history only. Staged and unstaged changes never appear in any
    report.

## Remote GitHub repositories

```bash
gitintel analyze https://github.com/ThePhoenix77/GitIntel
gitintel hotspots https://github.com/ThePhoenix77/GitIntel.git
```

Handling:

1. Trailing slashes are stripped and `.git` is appended if missing.
2. The URL is mapped to a cache directory (see below).
3. If that directory exists and opens as a repository, it is reused as-is.
   Otherwise it is cloned, with a progress bar showing transfer percentage.
4. The clone is analyzed exactly like a local repository.

### Recognized URL forms

| Source | Treated as |
| --- | --- |
| `https://github.com/owner/repo` | remote (cloned) |
| `https://github.com/owner/repo.git` | remote (cloned) |
| `http://github.com/owner/repo` | remote (cloned) |
| `git@github.com:owner/repo.git` | **local path** — will fail to open |
| `https://gitlab.com/owner/repo` | **local path** — will fail to open |

Only `github.com` over HTTP(S) is detected as remote. To analyze a repository hosted anywhere
else — including GitHub over SSH — clone it yourself and pass the local path:

```bash
git clone git@gitlab.com:owner/repo.git /tmp/repo
gitintel analyze /tmp/repo
```

### Authentication

Cloning uses libgit2 without credential callbacks, so **only public repositories** can be
fetched by URL. For private repositories, clone locally with your normal Git credentials and
analyze the resulting directory.

## The clone cache

| Aspect | Value |
| --- | --- |
| Root | `$XDG_CACHE_HOME/gitintel` if set, otherwise `~/.cache/gitintel` |
| Directory name | remote path with `/` replaced by `__`, `.git` stripped — e.g. `ThePhoenix77__GitIntel` |
| Reuse | An existing, openable clone is reused without fetching |
| Cleanup | Never removed automatically |

```bash
ls ~/.cache/gitintel
# ThePhoenix77__GitIntel
```

!!! warning "Cached clones are not refreshed"
    A cached repository is analyzed as of the moment it was cloned. GitIntel never runs a
    fetch or pull. To pick up new commits, update or delete the cache entry:

    ```bash
    git -C ~/.cache/gitintel/ThePhoenix77__GitIntel pull --ff-only
    # or
    rm -rf ~/.cache/gitintel/ThePhoenix77__GitIntel
    ```

If a cache directory exists but cannot be opened as a repository (a partial or corrupted
clone), GitIntel deletes it and clones again.

### Temporary clones

When a clone destination is not provided, `clone_repository()` falls back to a temporary
directory named `gitintel_*` under the system temp directory, and cleanup deletes only
directories whose name starts with that prefix. This is the mechanism that guarantees GitIntel
never deletes a directory you passed in yourself.

## Choosing between local and remote

| Situation | Recommendation |
| --- | --- |
| Repository already checked out | Pass the local path — no network, always current |
| Public repository you do not have | Pass the URL and let GitIntel cache it |
| Private repository | Clone with your credentials, then pass the path |
| CI job | Pass `.` after `actions/checkout` with `fetch-depth: 0` |
| Repeated runs over the same remote | Cached clone makes runs after the first one fast |
