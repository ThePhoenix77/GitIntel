from gitintel.git.commits import get_commits
from gitintel.git.repository import open_repository


def test_commit_changes():
    repository = open_repository(".")

    commits = get_commits(
        repository,
        limit=1,
    )

    assert len(commits) == 1

    commit = commits[0]

    assert isinstance(
        commit.changes,
        list,
    )