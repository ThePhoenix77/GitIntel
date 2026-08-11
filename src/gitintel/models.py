from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class FileChange:
    """
    Represents a file modification in a commit.
    """

    path: str
    additions: int
    deletions: int


@dataclass
class Commit:
    """
    Represents a Git commit inside GitIntel.
    """

    hash: str
    author: str
    email: str
    message: str
    date: datetime
    changes: list["FileChange"]


@dataclass
class Contributor:
    """
    Represents contributor activity.
    """

    name: str
    email: str
    commits: int
    files_changed: int
    additions: int
    deletions: int


@dataclass
class RepositorySummary:
    """
    High-level repository statistics.
    """

    commits: int
    contributors: int
    files_changed: int


@dataclass
class RepositoryContext:
    """
    Metadata about the repository being analyzed.
    """

    path: Path
    source: str
    temporary: bool
    owner: str
    repo_name: str
    branch: str
    remote_url: str
    source_type: str


@dataclass
class FileOwnership:
    """
    Represents ownership information for a file.

    modifications:
        Number of commits touching the file per contributor.

    lines_changed:
        Total added + deleted lines per contributor.

    last_modified_by:
        Last contributor who modified the file.

    last_modified_at:
        Timestamp of the latest modification.
    """

    path: str
    modifications: dict[str, int]
    lines_changed: dict[str, int]
    last_modified_by: str
    last_modified_at: datetime


@dataclass
class Hotspot:
    """
    Represents a risky repository file.
    """

    file_path: str

    risk_score: float

    modifications: int

    lines_changed: int

    contributors: int

    owner: str | None = None

    reasons: list[str] = field(
        default_factory=list
    )