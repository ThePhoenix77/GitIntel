from gitintel.git.commits import get_commits
from gitintel.git.repository import open_repository


def test_get_commits():
    repository = open_repository(".")

    commits = get_commits(repository)

    print(commits[0])

    assert len(commits) > 0
    assert commits[0].hash
    assert commits[0].message