import tempfile
from pathlib import Path
from urllib.parse import urlparse

import pygit2
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
)

console = Console()


def get_repository_name(
    url: str,
) -> str:
    """
    Extract repository name.
    """

    parsed = urlparse(url)

    return (
        parsed.path
        .strip("/")
        .replace(".git", "")
    )


def clone_repository(
    url: str,
    destination: Path | None = None,
) -> Path:
    """
    Clone repository with progress.
    """

    repository_name = get_repository_name(
        url
    )

    destination_is_temp = False

    if destination is None:
        destination = Path(
            tempfile.mkdtemp(
                prefix="gitintel_"
            )
        )
        destination_is_temp = True
    else:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)


    with Progress(
        TextColumn(
            "{task.description}"
        ),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:


        task = progress.add_task(
            f"Cloning {repository_name}",
            total=100,
        )


        cancelled = {"flag": False}

        def transfer_progress(
            stats,
        ):
            """
            Clone download progress callback.
            """
            try:
                if stats.total_objects > 0:

                    percentage = (
                        stats.received_objects
                        /
                        stats.total_objects
                    ) * 100

                    try:
                        progress.update(
                            task,
                            completed=percentage,
                        )
                    except Exception:
                        # Ignore progress rendering errors
                        pass

                return 0

            except KeyboardInterrupt:
                # Signal cancellation to libgit2 by returning non-zero
                cancelled["flag"] = True
                return 1

            except Exception:
                # Any other exception should not raise inside the C callback
                # Return non-zero to abort clone and let the outer code handle it
                cancelled["flag"] = True
                return 1



        callbacks = pygit2.RemoteCallbacks()
        callbacks.transfer_progress = transfer_progress


        try:
            pygit2.clone_repository(
                url,
                str(destination),
                callbacks=callbacks,
            )

            if cancelled["flag"]:
                # User cancelled via Ctrl+C inside callback
                raise KeyboardInterrupt()

        except KeyboardInterrupt:
            # Cleanup temporary destination if we created it
            if destination_is_temp and destination.exists():
                try:
                    import shutil

                    shutil.rmtree(destination, ignore_errors=True)
                except Exception:
                    pass

            raise ValueError("Cloning cancelled by user")

        except Exception as error:
            # On any error, cleanup temp destination we created
            if destination_is_temp and destination.exists():
                try:
                    import shutil

                    shutil.rmtree(destination, ignore_errors=True)
                except Exception:
                    pass

            raise ValueError(
                f"Unable to clone repository: {url}"
            ) from error


    console.print(
        f"[green][OK][/green] "
        f"Repository cloned: {repository_name}"
    )


    return destination