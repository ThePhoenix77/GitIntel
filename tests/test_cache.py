import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from gitintel.git.cache import (
    clone_or_open_cached_repository,
    get_cache_repo_path,
    get_cache_root,
    normalize_cache_dir_name,
)


def test_get_cache_root_default():
    """Test default cache root location."""
    with patch.dict("os.environ", {}, clear=True):
        cache_root = get_cache_root()
        # Should default to ~/.cache/gitintel
        assert cache_root.name == "gitintel"
        assert cache_root.parent.name == ".cache"


def test_get_cache_root_custom():
    """Test custom cache root via XDG_CACHE_HOME."""
    with patch.dict("os.environ", {"XDG_CACHE_HOME": "/custom/cache"}):
        cache_root = get_cache_root()
        assert str(cache_root) == "/custom/cache/gitintel"


def test_normalize_cache_dir_name_github_https():
    """Test normalizing GitHub HTTPS URLs."""
    url = "https://github.com/user/repo.git"
    normalized = normalize_cache_dir_name(url)
    assert normalized == "user__repo"


def test_normalize_cache_dir_name_github_ssh():
    """Test normalizing GitHub SSH URLs."""
    url = "git@github.com:user/repo.git"
    normalized = normalize_cache_dir_name(url)
    assert normalized == "user__repo"


def test_normalize_cache_dir_name_without_git():
    """Test normalizing URLs without .git suffix."""
    url = "https://github.com/user/repo"
    normalized = normalize_cache_dir_name(url)
    assert normalized == "user__repo"


def test_normalize_cache_dir_name_nested_path():
    """Test normalizing URLs with nested paths."""
    url = "https://github.com/org/nested/repo.git"
    normalized = normalize_cache_dir_name(url)
    assert normalized == "org__nested__repo"


def test_get_cache_repo_path():
    """Test getting cache path for a repository."""
    url = "https://github.com/user/repo.git"
    with patch.dict("os.environ", {}, clear=True):
        cache_path = get_cache_repo_path(url)
        assert cache_path.name == "user__repo"
        assert cache_path.parent.name == "gitintel"


def test_clone_or_open_cached_repository_new_clone():
    """Test cloning a repository for the first time."""
    
    # Create a temporary cache directory
    temp_cache = tempfile.mkdtemp()
    temp_cache_path = Path(temp_cache)
    
    # Create a temporary source repository to clone from
    temp_source = tempfile.mkdtemp()
    source_path = Path(temp_source) / "source_repo"
    source_path.mkdir()
    
    try:
        # Initialize source repository
        import pygit2
        source_repo = pygit2.init_repository(source_path)
        
        # Create a commit to have a HEAD
        signature = pygit2.Signature("Test User", "test@example.com")
        (source_path / "test.txt").write_text("test content")
        source_repo.index.add("test.txt")
        source_repo.index.write()
        
        tree = source_repo.index.write_tree()
        source_repo.create_commit(
            "HEAD", signature, signature, "Initial commit", tree, []
        )
        
        # Test cloning (we'll mock the actual clone to avoid network operations)
        with patch("gitintel.git.cache.get_cache_root", return_value=temp_cache_path):
            with patch("gitintel.git.cache.clone_repository") as mock_clone:
                mock_clone.return_value = temp_cache_path / "user__repo"
                
                cache_path, was_cached = clone_or_open_cached_repository("file://" + str(source_path))
                
                assert was_cached == False
                mock_clone.assert_called_once()
                
    finally:
        shutil.rmtree(temp_cache, ignore_errors=True)
        shutil.rmtree(temp_source, ignore_errors=True)


def test_clone_or_open_cached_repository_existing_cache():
    """Test opening an existing cached repository."""
    
    # Create a temporary cache directory
    temp_cache = tempfile.mkdtemp()
    temp_cache_path = Path(temp_cache)
    cache_repo_path = temp_cache_path / "user__repo"
    cache_repo_path.mkdir(parents=True)
    
    try:
        # Initialize cached repository
        import pygit2
        cached_repo = pygit2.init_repository(cache_repo_path)
        
        # Create a commit to have a HEAD
        signature = pygit2.Signature("Test User", "test@example.com")
        (cache_repo_path / "test.txt").write_text("test content")
        cached_repo.index.add("test.txt")
        cached_repo.index.write()
        
        tree = cached_repo.index.write_tree()
        cached_repo.create_commit(
            "HEAD", signature, signature, "Initial commit", tree, []
        )
        
        with patch("gitintel.git.cache.get_cache_root", return_value=temp_cache_path):
            cache_path, was_cached = clone_or_open_cached_repository("https://github.com/user/repo.git")
            
            assert cache_path == cache_repo_path
            assert was_cached == True
            
    finally:
        shutil.rmtree(temp_cache, ignore_errors=True)


def test_clone_or_open_cached_repository_invalid_cache():
    """Test that invalid cache is cleaned up and re-cloned."""
    
    # Create a temporary cache directory with invalid content
    temp_cache = tempfile.mkdtemp()
    temp_cache_path = Path(temp_cache)
    cache_repo_path = temp_cache_path / "user__repo"
    cache_repo_path.mkdir(parents=True)
    
    # Create an invalid cache (not a git repository)
    (cache_repo_path / "not_a_git_file.txt").write_text("invalid")
    
    try:
        with patch("gitintel.git.cache.get_cache_root", return_value=temp_cache_path):
            with patch("gitintel.git.cache.clone_repository") as mock_clone:
                mock_clone.return_value = cache_repo_path
                
                cache_path, was_cached = clone_or_open_cached_repository("https://github.com/user/repo.git")
                
                # Should have cleaned up and re-cloned
                assert was_cached == False
                mock_clone.assert_called_once()
                
    finally:
        shutil.rmtree(temp_cache, ignore_errors=True)


def test_cache_directory_creation():
    """Test that cache directories are created if they don't exist."""
    
    temp_cache = tempfile.mkdtemp()
    temp_cache_path = Path(temp_cache)
    # Remove the gitintel subdirectory to test creation
    gitintel_cache = temp_cache_path / "gitintel"
    
    try:
        with patch("gitintel.git.cache.get_cache_root", return_value=gitintel_cache):
            with patch("gitintel.git.cache.clone_repository") as mock_clone:
                mock_clone.return_value = gitintel_cache / "user__repo"
                
                clone_or_open_cached_repository("https://github.com/user/repo.git")
                
                # Cache directory should have been created
                assert gitintel_cache.exists()
                
    finally:
        shutil.rmtree(temp_cache, ignore_errors=True)