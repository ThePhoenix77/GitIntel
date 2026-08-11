from pathlib import Path
from urllib.parse import urlparse

import pygit2


def open_repository(path: str):
    """
    Open a Git repository.

    Args:
        path: Path to the repository.

    Returns:
        pygit2.Repository instance.

    Raises:
        ValueError: If the path is not a valid Git repository.
    """

    repository_path = Path(path).resolve()

    try:
        return pygit2.Repository(str(repository_path))

    except pygit2.GitError:
        raise ValueError(
            f"Invalid Git repository: {path}"
        )


def get_repository_metadata(repository):
    """
    Extract metadata from an open repository.
    """

    owner = ""
    repo_name = ""
    branch = ""
    remote_url = ""
    source_type = "Local"

    try:
        if not repository.head_is_unborn:
            branch = repository.head.shorthand or ""
    except Exception:
        branch = ""

    remote = None

    try:
        if "origin" in repository.remotes:
            remote = repository.remotes["origin"]
        elif len(repository.remotes) > 0:
            remote = repository.remotes[0]
    except Exception:
        remote = None

    if remote is not None:
        remote_url = remote.url or ""

        normalized_url = remote_url
        if normalized_url.startswith("git@"):
            normalized_url = normalized_url.replace(
                ":", "/"
            ).replace(
                "git@", "ssh://"
            )

        parsed = urlparse(normalized_url)
        path = parsed.path.strip("/")

        if path.endswith(".git"):
            path = path[: -len(".git")]

        if "/" in path:
            owner, repo_name = path.split("/", 1)

        if parsed.netloc.endswith("github.com"):
            source_type = "GitHub"

    return owner, repo_name, branch, remote_url, source_type