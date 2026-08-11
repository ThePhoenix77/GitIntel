from gitintel.analysis.ownership import analyze_ownership
from gitintel.git.commits import get_commits
from gitintel.git.repository import open_repository


def test_analyze_ownership():
    repository = open_repository(".")

    commits = get_commits(
        repository,
    )

    ownership = analyze_ownership(
        commits,
    )

    assert isinstance(
        ownership,
        list,
    )

    assert len(ownership) > 0

    file = ownership[0]

    assert file.path
    assert isinstance(
        file.modifications,
        dict,
    )

    assert isinstance(
        file.lines_changed,
        dict,
    )