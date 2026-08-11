from gitintel.analysis.contributors import analyze_contributors
from gitintel.git.commits import get_commits
from gitintel.git.repository import open_repository


def test_analyze_contributors():
    repository = open_repository(".")

    commits = get_commits(
        repository,
    )

    contributors = analyze_contributors(
        commits,
    )

    assert len(contributors) > 0

    contributor = contributors[0]

    assert contributor.commits > 0
    assert contributor.files_changed >= 0