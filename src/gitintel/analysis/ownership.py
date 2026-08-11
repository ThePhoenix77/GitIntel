from collections import defaultdict

from gitintel.models import (
    Commit,
    FileOwnership,
)


def analyze_ownership(
    commits: list[Commit],
) -> list[FileOwnership]:
    """
    Analyze file ownership.

    Metrics:
    - modification count
    - lines changed
    - last modification information
    """

    ownership = defaultdict(
        lambda: {
            "modifications": defaultdict(int),
            "lines_changed": defaultdict(int),
            "last_modified_by": "",
            "last_modified_at": None,
        }
    )

    for commit in commits:
        author = commit.author

        for change in commit.changes:
            file_data = ownership[change.path]

            file_data["modifications"][author] += 1

            file_data["lines_changed"][author] += (
                change.additions
                + change.deletions
            )

            current_last = file_data[
                "last_modified_at"
            ]

            if (
                current_last is None
                or commit.date > current_last
            ):
                file_data[
                    "last_modified_by"
                ] = author

                file_data[
                    "last_modified_at"
                ] = commit.date

    return [
        FileOwnership(
            path=path,
            modifications=dict(
                data["modifications"]
            ),
            lines_changed=dict(
                data["lines_changed"]
            ),
            last_modified_by=data[
                "last_modified_by"
            ],
            last_modified_at=data[
                "last_modified_at"
            ],
        )
        for path, data in ownership.items()
    ]