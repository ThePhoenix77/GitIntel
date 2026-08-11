from gitintel.models import (
    Commit,
    Contributor,
    RepositorySummary,
)


def create_summary(
    commits: list[Commit],
    contributors: list[Contributor],
) -> RepositorySummary:
    """
    Create repository summary statistics.
    """

    files = {
        change.path
        for commit in commits
        for change in commit.changes
    }

    return RepositorySummary(
        commits=len(commits),
        contributors=len(contributors),
        files_changed=len(files),
    )