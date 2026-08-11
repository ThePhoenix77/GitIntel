import typer
from rich.console import Console
from rich.panel import Panel

from gitintel import __version__
from gitintel.analysis.pipeline import (
    analyze_repository,
)
from gitintel.git.resolver import (
    resolve_repository,
)
from gitintel.git.workspace import (
    cleanup_repository,
)
from gitintel.reports.terminal import (
    configure_console,
    print_analysis,
    print_file_activity,
    print_health,
    print_hotspots,
    print_ownership,
    run_with_progress,
)

console = Console()


def _show_help(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    typer.echo(ctx.get_help())
    raise typer.Exit()


def _show_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    typer.echo(__version__)
    raise typer.Exit()


app = typer.Typer(
    name="gitintel",
    help="""
GitIntel - Git repository intelligence & analytics tool.

Analyze repositories, understand contribution patterns,
and discover ownership insights.
""",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    context_settings={"help_option_names": []},
)


@app.callback(invoke_without_command=True)
def main(
    show_help: bool = typer.Option(
        False,
        "--help",
        help="Show this message and exit.",
        is_eager=True,
        callback=_show_help,
        expose_value=False,
    ),
    show_version: bool = typer.Option(
        False,
        "--version",
        help="Show the installed GitIntel version and exit.",
        is_eager=True,
        callback=_show_version,
        expose_value=False,
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress output.",
    ),
):
    """
    Configure global CLI output verbosity.
    """
    # if verbose and quiet:
    #     raise typer.BadParameter(
    #         "Cannot use both --verbose and --quiet."
    #     )

    configure_console(
        # verbose=verbose,
        quiet=quiet,
    )

def handle_error(error: Exception):
    console.print(
        Panel(
            str(error),
            title="Error",
            border_style="red",
        )
    )

    raise typer.Exit(code=1)

@app.command(context_settings={"help_option_names": ["--help"]})
def version():
    """
    Show GitIntel version.
    """

    typer.echo(__version__)


@app.command(context_settings={"help_option_names": ["--help"]})
def analyze(
    path: str = typer.Argument(
        ".",
        help="Local repository path or GitHub URL",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        case_sensitive=False,
        help="Output format: table, json, or markdown",
    ),
):
    """
    Analyze a Git repository.
    """

    analysis = None
    context = None

    try:
        repository, context = run_with_progress(
            "Preparing repository...",
            resolve_repository,
            path,
        )

        analysis = run_with_progress(
            "Building analysis pipeline...",
            analyze_repository,
            repository,
            context,
        )

        print_analysis(
            context,
            analysis.summary,
            analysis.commits,
            analysis.contributors,
            output_format=format,
        )

        if format.lower() == "table":
            print_file_activity(
                analysis.commits,
            )

            print_health(
                analysis.commits,
                analysis.contributors,
            )

    except ValueError as error:
        handle_error(error)

        raise typer.Exit(
            code=1
        )

    finally:
        if context is not None and context.temporary:
            cleanup_repository(context.path)


@app.command(context_settings={"help_option_names": ["--help"]})
def ownership(
    path: str = typer.Argument(
        ".",
        help="Local repository path or GitHub URL",
    ),
    all_files: bool = typer.Option(
        False,
        "--all",
        help="Show all files instead of top files",
    ),
    file: str | None = typer.Option(
        None,
        "--file",
        help="Show ownership for a specific file",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        case_sensitive=False,
        help="Output format: table, json, or markdown",
    ),
):
    """
    Analyze file ownership.
    """

    analysis = None

    try:
        repository, context = run_with_progress(
            "Preparing repository...",
            resolve_repository,
            path,
        )

        analysis = run_with_progress(
            "Building analysis pipeline...",
            analyze_repository,
            repository,
            context,
        )

        ownership = analysis.ownership

        if file:
            ownership = [
                item
                for item in ownership
                if item.path == file
            ]

            if not ownership:
                typer.echo(
                    f"File not found: {file}"
                )

                raise typer.Exit(
                    code=1
                )

        elif not all_files:
            ownership = sorted(
                ownership,
                key=lambda item:
                    sum(
                        item.modifications.values()
                    ),
                reverse=True,
            )[:20]

        print_ownership(
            ownership,
            context,
            output_format=format,
        )

    except ValueError as error:
        handle_error(error)

        raise typer.Exit(
            code=1
        )

    finally:
        if context is not None and context.temporary:
            cleanup_repository(context.path)


@app.command(context_settings={"help_option_names": ["--help"]})
def hotspots(
    source: str = typer.Argument(
        ".",
        help="Repository path or GitHub URL",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        case_sensitive=False,
        help="Output format: table, json, or markdown",
    ),
):
    """
    Analyze repository hotspots.
    """
    context = None

    try:
        repository, context = run_with_progress(
            "Preparing repository...",
            resolve_repository,
            source,
        )

        analysis = run_with_progress(
            "Building analysis pipeline...",
            analyze_repository,
            repository,
            context,
        )

        print_hotspots(
            analysis.hotspots,
            context,
            output_format=format,
        )

    except ValueError as error:
        handle_error(error)

        raise typer.Exit(code=1)

    finally:
        if context is not None and context.temporary:
            cleanup_repository(context.path)
