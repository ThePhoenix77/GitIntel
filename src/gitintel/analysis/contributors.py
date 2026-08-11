from collections import defaultdict

from gitintel.models import (
    Commit,
    Contributor,
)


def analyze_contributors(
    commits: list[Commit],
) -> list[Contributor]:
    """
    Analyze contributor activity.

    Returns:
        Contributors sorted by commit count.
    """

    contributors = defaultdict(
        lambda: {
            "name": "",
            "email": "",
            "commits": 0,
            "files": set(),
            "additions": 0,
            "deletions": 0,
        }
    )

    for commit in commits:
        contributor = contributors[
            commit.email
        ]

        contributor["name"] = commit.author
        contributor["email"] = commit.email
        contributor["commits"] += 1

        for change in commit.changes:
            contributor["files"].add(
                change.path
            )

            contributor["additions"] += (
                change.additions
            )

            contributor["deletions"] += (
                change.deletions
            )

    return sorted(
        [
            Contributor(
                name=data["name"],
                email=data["email"],
                commits=data["commits"],
                files_changed=len(
                    data["files"]
                ),
                additions=data["additions"],
                deletions=data["deletions"],
            )
            for data in contributors.values()
        ],
        key=lambda contributor:
            contributor.commits,
        reverse=True,
    )