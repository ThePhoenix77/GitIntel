from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.table import Table

from gitintel.models import (
    Commit,
    Contributor,
    FileOwnership,
    Hotspot,
    RepositoryContext,
    RepositorySummary,
)

VERBOSE = False
QUIET = False


def configure_console(
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Configure global console verbosity for the CLI.
    """
    global VERBOSE, QUIET

    if verbose and quiet:
        raise ValueError("Cannot use both --verbose and --quiet")

    VERBOSE = verbose
    QUIET = quiet


console = Console()

def print_health(
    commits: list[Commit],
    contributors: list[Contributor],
):
    """
    Display repository health indicators.
    """

    table = Table(
        title="Repository Health"
    )

    table.add_column(
        "Area"
    )

    table.add_column(
        "Status"
    )

    table.add_column(
        "Details"
    )


    # -------------------------
    # Activity
    # -------------------------

    commit_count = len(commits)

    if commit_count < 50:
        table.add_row(
            "Activity",
            "[green][OK][/green]",
            "Low change frequency",
        )

    elif commit_count < 500:
        table.add_row(
            "Activity",
            "[green][OK][/green]",
            "Normal development activity",
        )

    else:
        table.add_row(
            "Activity",
            "[yellow][!!][/yellow]",
            f"High activity ({commit_count} commits)",
        )


    # -------------------------
    # Contributors
    # -------------------------

    contributor_count = len(
        contributors
    )

    if contributor_count == 1:

        table.add_row(
            "Ownership",
            "[yellow][!!][/yellow]",
            "Single contributor repository",
        )

    elif contributor_count > 10:

        table.add_row(
            "Ownership",
            "[yellow][!!][/yellow]",
            f"{contributor_count} contributors",
        )

    else:

        table.add_row(
            "Ownership",
            "[green][OK][/green]",
            f"{contributor_count} contributors",
        )


    # -------------------------
    # Maintenance
    # -------------------------

    if commits:

        latest = max(
            commits,
            key=lambda commit: commit.date,
        )


        days = (
            datetime.now()
            - latest.date
        ).days


        if days <= 7:

            table.add_row(
                "Maintenance",
                "[green][OK][/green]",
                "Recently updated",
            )

        elif days <= 90:

            table.add_row(
                "Maintenance",
                "[green][OK][/green]",
                "Maintained",
            )

        else:

            table.add_row(
                "Maintenance",
                "[yellow][!!][/yellow]",
                f"No activity for {days} days",
            )


    console.print(table)



def run_with_progress(
    description: str,
    function,
    *args,
    **kwargs,
):
    """
    Execute a function while showing progress.
    """

    if QUIET:
        if VERBOSE:
            console.log(f"[blue]Running:[/blue] {description}")
        return function(*args, **kwargs)

    if VERBOSE:
        console.log(f"[blue]Running:[/blue] {description}")

    with Progress(
        SpinnerColumn(),
        TextColumn(
            "[progress.description]{task.description}"
        ),
    ) as progress:

        task = progress.add_task(
            description,
            total=None,
        )

        result = function(
            *args,
            **kwargs,
        )

        progress.update(
            task,
            completed=1,
        )

    return result


def get_file_activity(
    commits: list[Commit],
) -> dict[str, dict[str, int]]:
    files: dict[str, dict[str, int]] = {}

    for commit in commits:
        for change in commit.changes:
            if change.path not in files:
                files[change.path] = {
                    "changes": 0,
                    "lines": 0,
                }

            files[change.path]["changes"] += 1
            files[change.path]["lines"] += (
                change.additions + change.deletions
            )

    return files


def get_repository_health_data(
    commits: list[Commit],
    contributors: list[Contributor],
) -> list[dict[str, str]]:
    health = []
    commit_count = len(commits)

    if commit_count < 50:
        health.append(
            {
                "area": "Activity",
                "status": "OK",
                "details": "Low change frequency",
            }
        )
    elif commit_count < 500:
        health.append(
            {
                "area": "Activity",
                "status": "OK",
                "details": "Normal development activity",
            }
        )
    else:
        health.append(
            {
                "area": "Activity",
                "status": "WARN",
                "details": f"High activity ({commit_count} commits)",
            }
        )

    contributor_count = len(contributors)

    if contributor_count == 1:
        health.append(
            {
                "area": "Ownership",
                "status": "WARN",
                "details": "Single contributor repository",
            }
        )
    elif contributor_count > 10:
        health.append(
            {
                "area": "Ownership",
                "status": "WARN",
                "details": f"{contributor_count} contributors",
            }
        )
    else:
        health.append(
            {
                "area": "Ownership",
                "status": "OK",
                "details": f"{contributor_count} contributors",
            }
        )

    if commits:
        latest = max(commits, key=lambda commit: commit.date)
        days = (datetime.now() - latest.date).days

        if days <= 7:
            health.append(
                {
                    "area": "Maintenance",
                    "status": "OK",
                    "details": "Recently updated",
                }
            )
        elif days <= 90:
            health.append(
                {
                    "area": "Maintenance",
                    "status": "OK",
                    "details": "Maintained",
                }
            )
        else:
            health.append(
                {
                    "area": "Maintenance",
                    "status": "WARN",
                    "details": f"No activity for {days} days",
                }
            )

    return health


def print_banner():
    console.print(
        Panel(
            "[bold cyan]GitIntel[/bold cyan]\n"
            "Git repository intelligence & analytics",
            title="Welcome",
        )
    )


console = Console()


def get_display_name(
    context: RepositoryContext,
) -> str:
    """
    Get readable repository name.
    """

    if context.repo_name:
        return context.repo_name

    if context.temporary:

        return (
            context.source
            .rstrip("/")
            .split("/")[-1]
            .replace(".git", "")
        )


    return context.path.name



def print_analysis(
    context: RepositoryContext,
    summary: RepositorySummary,
    commits: list[Commit],
    contributors: list[Contributor],
    output_format: str = "table",
):
    """
    Display repository analysis dashboard.
    """

    output_format = output_format.lower()

    if output_format == "json":
        print_analysis_json(
            context,
            summary,
            commits,
            contributors,
        )
        return

    if output_format == "markdown":
        print_analysis_markdown(
            context,
            summary,
            commits,
            contributors,
        )
        return

    print_analysis_table(
        context,
        summary,
        commits,
        contributors,
    )


def print_analysis_json(
    context: RepositoryContext,
    summary: RepositorySummary,
    commits: list[Commit],
    contributors: list[Contributor],
):
    import json

    data = {
        "repository": {
            "name": get_display_name(context),
            "owner": context.owner or "Unknown",
            "branch": context.branch or "Unknown",
            "path": str(context.path),
            "source": context.source_type,
            "remote": context.remote_url or "N/A",
        },
        "summary": {
            "commits": summary.commits,
            "contributors": summary.contributors,
            "files_changed": summary.files_changed,
            "last_commit": (
                max(commits, key=lambda commit: commit.date).date.isoformat()
                if commits else None
            ),
        },
        "contributors": [
            {
                "name": contributor.name,
                "commits": contributor.commits,
                "files_changed": contributor.files_changed,
                "share": (
                    contributor.commits
                    / sum(c.commits for c in contributors)
                    * 100
                    if contributors else 0
                ),
            }
            for contributor in sorted(
                contributors,
                key=lambda item: item.commits,
                reverse=True,
            )
        ],
    }

    data["most_changed_files"] = [
        {
            "file": path,
            "changes": info["changes"],
            "lines_changed": info["lines"],
        }
        for path, info in sorted(
            get_file_activity(commits).items(),
            key=lambda item: item[1]["changes"],
            reverse=True,
        )[:10]
    ]

    data["repository_health"] = get_repository_health_data(
        commits,
        contributors,
    )

    console.print(
        json.dumps(data, indent=2)
    )


def print_analysis_markdown(
    context: RepositoryContext,
    summary: RepositorySummary,
    commits: list[Commit],
    contributors: list[Contributor],
):
    lines = [
        f"# GitIntel Analysis for {get_display_name(context)}",
        "",
        "## Repository",
        f"- **Owner:** {context.owner or 'Unknown'}",
        f"- **Branch:** {context.branch or 'Unknown'}",
        f"- **Path:** {context.path}",
        f"- **Source:** {context.source_type}",
        f"- **Remote:** {context.remote_url or 'N/A'}",
        "",
        "## Summary",
        f"- Commits: {summary.commits}",
        f"- Contributors: {summary.contributors}",
        f"- Files Changed: {summary.files_changed}",
    ]

    if commits:
        latest_commit = max(
            commits,
            key=lambda commit: commit.date,
        )
        lines.append(
            f"- Last Commit: {latest_commit.date.strftime('%Y-%m-%d %H:%M')}"
        )

    lines.append("\n## Top Contributors")
    lines.append("| Contributor | Commits | Files | Share |")
    lines.append("|---|---|---|---|")

    total_commits = sum(
        contributor.commits
        for contributor in contributors
    )

    for contributor in sorted(
        contributors,
        key=lambda item: item.commits,
        reverse=True,
    ):
        share = (
            contributor.commits
            / total_commits
            * 100
            if total_commits else 0
        )
        lines.append(
            f"| {contributor.name} | {contributor.commits} | {contributor.files_changed} | {share:.1f}% |"
        )

    lines.append("")
    lines.append("## Most Changed Files")
    lines.append("| File | Changes | Lines Changed |")
    lines.append("|---|---|---|")

    for path, info in sorted(
        get_file_activity(commits).items(),
        key=lambda item: item[1]["changes"],
        reverse=True,
    )[:10]:
        lines.append(
            f"| {path} | {info['changes']} | {info['lines']} |"
        )

    lines.append("")
    lines.append("## Repository Health")
    lines.append("| Area | Status | Details |")
    lines.append("|---|---|---|")

    for health_row in get_repository_health_data(commits, contributors):
        lines.append(
            f"| {health_row['area']} | {health_row['status']} | {health_row['details']} |"
        )

    console.print("\n".join(lines))


def print_analysis_table(
    context: RepositoryContext,
    summary: RepositorySummary,
    commits: list[Commit],
    contributors: list[Contributor],
):
    """
    Display repository analysis dashboard.
    """

    console.print(
        Panel(
            "\n".join(
                [
                    f"[bold]Repository:[/bold] {get_display_name(context)}",
                    f"[bold]Owner:[/bold] {context.owner or 'Unknown'}",
                    f"[bold]Branch:[/bold] {context.branch or 'Unknown'}",
                    f"[bold]Path:[/bold] {context.path}",
                    f"[bold]Source:[/bold] {context.source_type}",
                    f"[bold]Remote:[/bold] {context.remote_url or 'N/A'}",
                ]
            ),
            title="GitIntel Analysis",
        )
    )


    # -------------------------
    # Repository Summary
    # -------------------------

    summary_table = Table(
        title="Repository Summary"
    )

    summary_table.add_column(
        "Metric"
    )

    summary_table.add_column(
        "Value"
    )


    summary_table.add_row(
        "Commits",
        str(summary.commits),
    )

    summary_table.add_row(
        "Contributors",
        str(summary.contributors),
    )

    summary_table.add_row(
        "Files Changed",
        str(summary.files_changed),
    )


    if commits:
        latest_commit = max(
            commits,
            key=lambda commit: commit.date,
        )

        summary_table.add_row(
            "Last Commit",
            latest_commit.date.strftime(
                "%Y-%m-%d %H:%M"
            ),
        )


    console.print(summary_table)



    # -------------------------
    # Contributors
    # -------------------------

    contributor_table = Table(
        title="Top Contributors"
    )

    contributor_table.add_column(
        "Contributor"
    )

    contributor_table.add_column(
        "Commits"
    )

    contributor_table.add_column(
        "Files"
    )

    contributor_table.add_column(
        "Share"
    )


    total_commits = sum(
        contributor.commits
        for contributor in contributors
    )


    for contributor in sorted(
        contributors,
        key=lambda item: item.commits,
        reverse=True,
    ):

        percentage = (
            contributor.commits
            / total_commits
            * 100
            if total_commits
            else 0
        )

        contributor_table.add_row(
            contributor.name,
            str(contributor.commits),
            str(contributor.files_changed),
            f"{percentage:.1f}%",
        )


    console.print(contributor_table)

def print_file_activity(
    commits: list[Commit],
):
    """
    Display most changed files.
    """

    files = {}

    for commit in commits:
        for change in commit.changes:

            if change.path not in files:
                files[change.path] = {
                    "changes": 0,
                    "lines": 0,
                }

            files[change.path]["changes"] += 1

            files[change.path]["lines"] += (
                change.additions
                + change.deletions
            )


    table = Table(
        title="Most Changed Files"
    )


    table.add_column(
        "File"
    )

    table.add_column(
        "Changes"
    )

    table.add_column(
        "Lines Changed"
    )


    for path, data in sorted(
        files.items(),
        key=lambda item: item[1]["changes"],
        reverse=True,
    )[:10]:

        table.add_row(
            path,
            str(data["changes"]),
            str(data["lines"]),
        )


    console.print(table)


def print_ownership(
    ownership: list[FileOwnership],
    context: RepositoryContext,
    output_format: str = "table",
):
    """
    Display file ownership information.
    """

    output_format = output_format.lower()

    if output_format == "json":
        print_ownership_json(
            ownership,
            context,
        )
        return

    if output_format == "markdown":
        print_ownership_markdown(
            ownership,
            context,
        )
        return

    print_ownership_table(
        ownership,
        context,
    )


def print_ownership_json(
    ownership: list[FileOwnership],
    context: RepositoryContext,
):
    import json

    data = {
        "repository": {
            "name": get_display_name(context),
            "owner": context.owner or "Unknown",
            "branch": context.branch or "Unknown",
            "path": str(context.path),
            "source": context.source_type,
            "remote": context.remote_url or "N/A",
        },
        "ownership": [
            {
                "file": item.path,
                "contributor": contributor,
                "modifications": item.modifications.get(contributor, 0),
                "modify_percent": (
                    item.modifications.get(contributor, 0)
                    / sum(item.modifications.values())
                    * 100
                    if item.modifications else 0
                ),
                "lines_changed": item.lines_changed.get(contributor, 0),
                "lines_percent": (
                    item.lines_changed.get(contributor, 0)
                    / sum(item.lines_changed.values())
                    * 100
                    if item.lines_changed else 0
                ),
                "last_modified_by": item.last_modified_by,
                "last_modified_at": (
                    item.last_modified_at.isoformat()
                    if item.last_modified_at else None
                ),
            }
            for item in ownership
            for contributor in sorted(
                set(item.modifications).union(item.lines_changed),
                key=lambda name: item.modifications.get(name, 0),
                reverse=True,
            )
        ],
    }

    console.print(json.dumps(data, indent=2))


def print_ownership_markdown(
    ownership: list[FileOwnership],
    context: RepositoryContext,
):
    if not ownership:
        console.print("[yellow]No ownership data found.[/yellow]")
        return

    lines = [
        f"# Ownership Analysis for {get_display_name(context)}",
        "",
        "## Repository",
        f"- **Owner:** {context.owner or 'Unknown'}",
        f"- **Branch:** {context.branch or 'Unknown'}",
        f"- **Path:** {context.path}",
        f"- **Source:** {context.source_type}",
        f"- **Remote:** {context.remote_url or 'N/A'}",
        "",
        "## File Ownership",
        "| File | Contributor | Modifications | Modify % | Lines Changed | Lines % | Last Modified |",
        "|---|---|---|---|---|---|---|",
    ]

    for item in ownership:
        modification_total = sum(item.modifications.values())
        lines_total = sum(item.lines_changed.values())
        contributors = sorted(
            set(item.modifications).union(item.lines_changed),
            key=lambda name: item.modifications.get(name, 0),
            reverse=True,
        )

        for contributor in contributors:
            modifications = item.modifications.get(contributor, 0)
            lines_changed = item.lines_changed.get(contributor, 0)
            mod_percent = (
                modifications / modification_total * 100
                if modification_total else 0
            )
            lines_percent = (
                lines_changed / lines_total * 100
                if lines_total else 0
            )
            last_modified = (
                f"{item.last_modified_by} {item.last_modified_at}"
                if contributor == item.last_modified_by else ""
            )
            lines.append(
                f"| {item.path} | {contributor} | {modifications} | {mod_percent:.1f}% | {lines_changed} | {lines_percent:.1f}% | {last_modified} |"
            )

    console.print("\n".join(lines))


def print_ownership_table(
    ownership: list[FileOwnership],
    context: RepositoryContext,
):
    """
    Display file ownership information.
    """

    if not ownership:
        console.print(
            "[yellow]No ownership data found.[/yellow]"
        )
        return

    console.print(
        Panel(
            "\n".join(
                [
                    f"[bold]Repository:[/bold] {get_display_name(context)}",
                    f"[bold]Owner:[/bold] {context.owner or 'Unknown'}",
                    f"[bold]Branch:[/bold] {context.branch or 'Unknown'}",
                    f"[bold]Path:[/bold] {context.path}",
                    f"[bold]Source:[/bold] {context.source_type}",
                    f"[bold]Remote:[/bold] {context.remote_url or 'N/A'}",
                ]
            ),
            title="Ownership Analysis",
        )
    )

    table = Table(
        title="File Ownership"
    )

    table.add_column(
        "File"
    )

    table.add_column(
        "Contributor"
    )

    table.add_column(
        "Modifications"
    )

    table.add_column(
        "Modify %"
    )

    table.add_column(
        "Lines Changed"
    )

    table.add_column(
        "Lines %"
    )

    table.add_column(
        "Last Modified"
    )


    for file in ownership:

        modification_total = sum(
            file.modifications.values()
        )

        lines_total = sum(
            file.lines_changed.values()
        )

        contributors = set(
            file.modifications
        ).union(
            file.lines_changed
        )


        for contributor in sorted(
            contributors,
            key=lambda name:
                file.modifications.get(
                    name,
                    0,
                ),
            reverse=True,
        ):

            modifications = (
                file.modifications.get(
                    contributor,
                    0,
                )
            )

            lines = (
                file.lines_changed.get(
                    contributor,
                    0,
                )
            )

            modification_percent = (
                modifications
                / modification_total
                * 100
                if modification_total
                else 0
            )

            lines_percent = (
                lines
                / lines_total
                * 100
                if lines_total
                else 0
            )


            last_modified = ""

            if (
                contributor
                == file.last_modified_by
            ):
                last_modified = (
                    f"{file.last_modified_by}\n"
                    f"{file.last_modified_at}"
                )


            table.add_row(
                file.path,
                contributor,
                str(modifications),
                f"{modification_percent:.1f}%",
                str(lines),
                f"{lines_percent:.1f}%",
                last_modified,
            )

    console.print(table)


def print_hotspots(
    hotspots: list[Hotspot],
    context: RepositoryContext,
    output_format: str = "table",
):
    output_format = output_format.lower()

    if output_format == "json":
        print_hotspots_json(hotspots, context)
        return

    if output_format == "markdown":
        print_hotspots_markdown(hotspots, context)
        return

    print_hotspots_table(hotspots, context)


def print_hotspots_json(
    hotspots: list[Hotspot],
    context: RepositoryContext,
):
    import json

    data = {
        "repository": {
            "name": get_display_name(context),
            "owner": context.owner or "Unknown",
            "branch": context.branch or "Unknown",
            "path": str(context.path),
            "source": context.source_type,
            "remote": context.remote_url or "N/A",
        },
        "hotspots": [
            {
                "file": hotspot.file_path,
                "risk_score": hotspot.risk_score,
                "changes": hotspot.lines_changed,
                "contributors": hotspot.contributors,
                "owner": hotspot.owner,
                "reasons": hotspot.reasons,
            }
            for hotspot in hotspots[:10]
        ],
    }

    console.print(json.dumps(data, indent=2))


def print_hotspots_markdown(
    hotspots: list[Hotspot],
    context: RepositoryContext,
):
    lines = [
        f"# Repository Hotspots for {get_display_name(context)}",
        "",
        "## Hotspot Files",
        "| File | Risk | Changes | Contributors | Owner |",
        "|---|---|---|---|---|",
    ]

    for hotspot in hotspots[:10]:
        level = (
            "HIGH" if hotspot.risk_score >= 70 else "MED"
        )
        lines.append(
            f"| {hotspot.file_path} | {level} {hotspot.risk_score:.0f} | {hotspot.lines_changed} | {hotspot.contributors} | {hotspot.owner or '-'} |"
        )

    console.print("\n".join(lines))


def print_hotspots_table(
    hotspots: list[Hotspot],
    context: RepositoryContext,
):

    table = Table(
        title="Repository Hotspots"
    )


    table.add_column(
        "File"
    )

    table.add_column(
        "Risk"
    )

    table.add_column(
        "Changes"
    )

    table.add_column(
        "Contributors"
    )

    table.add_column(
        "Owner"
    )


    for hotspot in hotspots[:10]:

        level = (
            "[red]HIGH[/red]"
            if hotspot.risk_score >= 70
            else "[yellow]MED[/yellow]"
        )


        table.add_row(
            hotspot.file_path,
            f"{level} {hotspot.risk_score:.0f}",
            str(
                hotspot.lines_changed
            ),
            str(
                hotspot.contributors
            ),
            hotspot.owner or "-",
        )


    console.print(table)

    table = Table(
        title="Repository Hotspots"
    )


    table.add_column(
        "File"
    )

    table.add_column(
        "Risk"
    )

    table.add_column(
        "Changes"
    )

    table.add_column(
        "Contributors"
    )

    table.add_column(
        "Owner"
    )


    for hotspot in hotspots[:10]:

        level = (
            "[red]HIGH[/red]"
            if hotspot.risk_score >= 70
            else "[yellow]MED[/yellow]"
        )


        table.add_row(
            hotspot.file_path,
            f"{level} {hotspot.risk_score:.0f}",
            str(
                hotspot.lines_changed
            ),
            str(
                hotspot.contributors
            ),
            hotspot.owner or "-",
        )


    console.print(table)
