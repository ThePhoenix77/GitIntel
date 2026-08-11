from dataclasses import dataclass, field
from typing import Any

from gitintel.analysis.contributors import analyze_contributors
from gitintel.analysis.hotspots import calculate_hotspots
from gitintel.analysis.ownership import analyze_ownership
from gitintel.analysis.summary import create_summary
from gitintel.git.commits import get_commits
from gitintel.models import (
    Commit,
    FileOwnership,
    Hotspot,
    RepositoryContext,
    RepositorySummary,
)


@dataclass
class AnalysisContext:
    repository: Any
    repository_context: RepositoryContext
    _commits: list[Commit] | None = field(default=None, init=False)
    _contributors: list[Any] | None = field(default=None, init=False)
    _summary: RepositorySummary | None = field(default=None, init=False)
    _ownership: list[FileOwnership] | None = field(default=None, init=False)
    _changes: dict[str, dict[str, Any]] | None = field(default=None, init=False)
    _hotspots: list[Hotspot] | None = field(default=None, init=False)

    @property
    def commits(self) -> list[Commit]:
        if self._commits is None:
            self._commits = get_commits(self.repository)
        return self._commits

    @property
    def contributors(self) -> list[Any]:
        if self._contributors is None:
            self._contributors = analyze_contributors(
                self.commits
            )
        return self._contributors

    @property
    def summary(self) -> RepositorySummary:
        if self._summary is None:
            self._summary = create_summary(
                self.commits,
                self.contributors,
            )
        return self._summary

    @property
    def ownership(self) -> list[FileOwnership]:
        if self._ownership is None:
            self._ownership = analyze_ownership(
                self.commits
            )
        return self._ownership

    @property
    def changes(self) -> dict[str, dict[str, Any]]:
        if self._changes is None:
            file_stats: dict[str, dict[str, Any]] = {}

            for commit in self.commits:
                for change in commit.changes:
                    stats = file_stats.setdefault(
                        change.path,
                        {
                            "modifications": 0,
                            "lines_changed": 0,
                            "contributors": set(),
                        },
                    )

                    stats["modifications"] += 1
                    stats["lines_changed"] += (
                        change.additions + change.deletions
                    )
                    stats["contributors"].add(commit.author)

            for stats in file_stats.values():
                stats["contributors"] = len(stats["contributors"])

            self._changes = file_stats

        return self._changes

    @property
    def ownership_map(self) -> dict[str, str]:
        return {
            item.path: item.last_modified_by
            for item in self.ownership
        }

    @property
    def hotspots(self) -> list[Hotspot]:
        if self._hotspots is None:
            self._hotspots = calculate_hotspots(
                self.commits,
                self.changes,
                self.ownership_map,
            )
        return self._hotspots


def analyze_repository(
    repository: Any,
    repository_context: RepositoryContext,
) -> AnalysisContext:
    """
    Create a unified analysis pipeline for the requested repository.

    The returned AnalysisContext caches expensive computations and exposes
    shared results for CLI presentation wrappers.
    """

    return AnalysisContext(
        repository=repository,
        repository_context=repository_context,
    )
