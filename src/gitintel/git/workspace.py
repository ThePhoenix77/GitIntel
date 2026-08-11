import shutil
from pathlib import Path


def cleanup_repository(
    path: Path,
):
    """
    Remove temporary cloned repository.
    """

    if (
        path.exists()
        and path.name.startswith(
            "gitintel_"
        )
    ):

        shutil.rmtree(
            path,
            ignore_errors=True,
        )