import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

from gitintel.git.clone import clone_repository
from gitintel.git.repository import open_repository


def get_cache_root() -> Path:
    cache_home = os.environ.get("XDG_CACHE_HOME")
    if cache_home:
        return Path(cache_home).expanduser() / "gitintel"

    return Path.home() / ".cache" / "gitintel"


def normalize_cache_dir_name(url: str) -> str:
    if url.startswith("git@"):
        url = url.replace(":", "/")
        url = url.replace("git@", "ssh://")

    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if path.endswith(".git"):
        path = path[: -len(".git")]

    return path.replace("/", "__")


def get_cache_repo_path(url: str) -> Path:
    return get_cache_root() / normalize_cache_dir_name(url)


def clone_or_open_cached_repository(url: str) -> tuple[Path, bool]:
    cache_path = get_cache_repo_path(url)

    if cache_path.exists():
        try:
            open_repository(cache_path)
            return cache_path, True
        except ValueError:
            shutil.rmtree(cache_path, ignore_errors=True)

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    clone_repository(
        url,
        destination=cache_path,
    )

    return cache_path, False
