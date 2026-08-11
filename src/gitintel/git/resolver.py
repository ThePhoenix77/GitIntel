from pathlib import Path

from gitintel.git.cache import (
    clone_or_open_cached_repository,
)
from gitintel.git.repository import (
    get_repository_metadata,
    open_repository,
)
from gitintel.models import (
    RepositoryContext,
)


def normalize_repository_url(
    source: str,
) -> str:
    """
    Normalize GitHub repository URLs.
    """

    source = source.rstrip("/")


    if not source.endswith(
        ".git"
    ):

        source += ".git"


    return source



def is_remote_repository(
    source: str,
) -> bool:
    """
    Check if source is a remote repository.
    """

    return (
        source.startswith(
            "https://github.com/"
        )
        or source.startswith(
            "http://github.com/"
        )
    )



def resolve_repository(
    source: str,
):
    """
    Resolve repository source.

    Supports:
    - local paths
    - GitHub URLs
    """

    if is_remote_repository(
        source
    ):

        url = normalize_repository_url(
            source
        )

        path, cached = clone_or_open_cached_repository(
            url
        )

        repository = open_repository(
            path
        )

        owner, repo_name, branch, remote_url, source_type = (
            get_repository_metadata(repository)
        )

        return (
            repository,
            RepositoryContext(
                path=Path(path),
                source=source,
                temporary=not cached,
                owner=owner,
                repo_name=repo_name,
                branch=branch,
                remote_url=remote_url,
                source_type=source_type,
            ),
        )

    repository = open_repository(
        Path(source)
    )

    owner, repo_name, branch, remote_url, source_type = (
        get_repository_metadata(repository)
    )

    return (
        repository,
        RepositoryContext(
            path=Path(source).resolve(),
            source=str(Path(source).resolve()),
            temporary=False,
            owner=owner,
            repo_name=repo_name,
            branch=branch,
            remote_url=remote_url,
            source_type=source_type,
        ),
    )
