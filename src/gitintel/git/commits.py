from datetime import datetime

import pygit2

from gitintel.git.diff import get_commit_diff
from gitintel.models import Commit


def get_commits(repository, limit: int | None = None):
    """
    Extract commits from a Git repository.

    Args:
        repository: pygit2.Repository instance.
        limit: Maximum number of commits to return.

    Returns:
        List of GitIntel Commit objects.
    """

    commits = []

    walker = repository.walk(
        repository.head.target,
        pygit2.GIT_SORT_TIME,
    )

    for index, commit in enumerate(walker):
        if limit and index >= limit:
            break

        changes = get_commit_diff(
            repository,
            commit,
        )

        commits.append(
            Commit(
                hash=str(commit.id),
                author=commit.author.name,
                email=commit.author.email,
                message=commit.message.strip(),
                date=datetime.fromtimestamp(commit.commit_time),
                changes=changes,
            )
        )

    return commits