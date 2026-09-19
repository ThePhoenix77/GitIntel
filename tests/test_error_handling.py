import tempfile
from pathlib import Path

import pytest

from gitintel.git.clone import clone_repository
from gitintel.git.repository import open_repository
from gitintel.git.resolver import (
    is_remote_repository,
    normalize_repository_url,
    resolve_repository,
)


def test_open_repository_error_nonexistent():
    """Test that opening a non-existent path raises ValueError."""
    with pytest.raises(ValueError, match="Invalid Git repository"):
        open_repository("/nonexistent/path/that/does/not/exist")


def test_open_repository_error_directory_not_git():
    """Test that opening a non-git directory raises ValueError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a regular directory, not a git repo
        test_path = Path(temp_dir) / "not_a_repo"
        test_path.mkdir()
        
        with pytest.raises(ValueError, match="Invalid Git repository"):
            open_repository(str(test_path))


def test_open_repository_error_file_instead_of_directory():
    """Test that opening a file instead of directory raises ValueError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file, not a directory
        test_file = Path(temp_dir) / "not_a_directory.txt"
        test_file.write_text("I am a file")
        
        with pytest.raises(ValueError, match="Invalid Git repository"):
            open_repository(str(test_file))


def test_clone_repository_error_invalid_url():
    """Test that cloning an invalid URL raises ValueError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_url = "https://nonexistent-repository-that-does-not-exist-12345.com/fake.git"
        
        with pytest.raises(ValueError, match="Unable to clone repository"):
            clone_repository(invalid_url, destination=Path(temp_dir) / "fake")


def test_clone_repository_error_permission_denied():
    """Test that cloning to a directory without permissions raises ValueError."""
    # This test is platform-dependent and may not work on all systems
    # Skip on Windows where permission handling is different
    import sys
    if sys.platform == "win32":
        pytest.skip("Permission test not applicable on Windows")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and make it read-only
        readonly_dir = Path(temp_dir) / "readonly"
        readonly_dir.mkdir()
        
        try:
            # Make directory read-only
            readonly_dir.chmod(0o444)
            
            # Try to clone to the read-only directory
            with pytest.raises(ValueError, match="Unable to clone repository"):
                clone_repository("https://github.com/ThePhoenix77/GitIntel.git", destination=readonly_dir)
                
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)


def test_is_remote_repository_github_https():
    """Test GitHub HTTPS URL detection."""
    assert is_remote_repository("https://github.com/user/repo") == True
    assert is_remote_repository("https://github.com/user/repo.git") == True


def test_is_remote_repository_github_http():
    """Test GitHub HTTP URL detection."""
    assert is_remote_repository("http://github.com/user/repo") == True
    assert is_remote_repository("http://github.com/user/repo.git") == True


def test_is_remote_repository_local_path():
    """Test that local paths are not detected as remote."""
    assert is_remote_repository("/local/path") == False
    assert is_remote_repository(".") == False
    assert is_remote_repository("../relative") == False


def test_is_remote_repository_non_github():
    """Test that non-GitHub URLs are not detected as remote."""
    assert is_remote_repository("https://gitlab.com/user/repo") == False
    assert is_remote_repository("https://bitbucket.org/user/repo") == False
    assert is_remote_repository("git@gitlab.com:user/repo.git") == False


def test_normalize_repository_url_adds_git_suffix():
    """Test that .git suffix is added if missing."""
    assert normalize_repository_url("https://github.com/user/repo") == "https://github.com/user/repo.git"
    assert normalize_repository_url("https://github.com/user/repo/") == "https://github.com/user/repo.git"


def test_normalize_repository_url_preserves_git_suffix():
    """Test that .git suffix is preserved if already present."""
    assert normalize_repository_url("https://github.com/user/repo.git") == "https://github.com/user/repo.git"


def test_resolve_repository_local_path():
    """Test resolving a local repository path."""
    # Should resolve the current repository
    repo, context = resolve_repository(".")
    
    assert repo is not None
    assert context.temporary == False
    assert context.source_type in ["Local", "GitHub"]


def test_resolve_repository_invalid_local_path():
    """Test that resolving an invalid local path raises ValueError."""
    with pytest.raises(ValueError, match="Invalid Git repository"):
        resolve_repository("/nonexistent/path")


def test_resolve_repository_github_url():
    """Test resolving a GitHub URL (would attempt to clone)."""
    # We'll mock the clone to avoid actual network operations
    from unittest.mock import patch
    
    with patch("gitintel.git.resolver.clone_or_open_cached_repository") as mock_clone:
        with patch("gitintel.git.resolver.open_repository") as mock_open:
            mock_clone.return_value = (Path("/fake/cache"), False)
            mock_open.return_value = "mock_repo"
            
            with patch("gitintel.git.resolver.get_repository_metadata") as mock_metadata:
                mock_metadata.return_value = ("user", "repo", "main", "https://github.com/user/repo.git", "GitHub")
                
                repo, context = resolve_repository("https://github.com/user/repo")
                
                assert context.temporary == True  # GitHub URLs are temporary unless cached
                assert context.source_type == "GitHub"


def test_error_message_includes_original_error():
    """Test that error messages include the original error type and message."""


    from gitintel.git.clone import clone_repository
    
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_url = "https://invalid-url-that-will-fail.com/repo.git"
        
        try:
            clone_repository(invalid_url, destination=Path(temp_dir) / "fake")
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            # Error message should include URL and error type
            error_str = str(e)
            assert invalid_url in error_str
            assert "GitError" in error_str or "Exception" in error_str


def test_error_message_truncation():
    """Test that very long error messages are truncated."""
    from unittest.mock import patch

    from gitintel.git.clone import clone_repository
    
    # Create a mock error with a very long message
    long_message = "a" * 300
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("pygit2.clone_repository") as mock_clone:
            mock_clone.side_effect = Exception(long_message)
            
            try:
                clone_repository("https://github.com/user/repo.git", destination=Path(temp_dir) / "fake")
                pytest.fail("Should have raised ValueError")
            except ValueError as e:
                error_str = str(e)
                # Should be truncated to around 200 characters
                assert len(error_str) < 300  # Allow some overhead for URL and error type


def test_cli_error_handling_invalid_repository():
    """Test CLI error handling for invalid repository."""
    from typer.testing import CliRunner

    from gitintel.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["analyze", "/nonexistent/path"])
    
    assert result.exit_code == 1
    assert "Error" in result.stdout


def test_cli_error_handling_file_not_found():
    """Test CLI error handling when file not found in ownership."""
    from typer.testing import CliRunner

    from gitintel.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["ownership", ".", "--file", "/nonexistent/file.py"])
    
    assert result.exit_code == 1
    assert "File not found" in result.stdout


def test_repository_metadata_exception_handling():
    """Test that repository metadata extraction handles exceptions gracefully."""
    import pygit2

    from gitintel.git.repository import get_repository_metadata
    
    # Create a repository and test exception handling
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()
        
        # Initialize a git repo
        test_repo = pygit2.init_repository(repo_path)
        
        # Create a commit to have a HEAD
        signature = pygit2.Signature("Test User", "test@example.com")
        (repo_path / "test.txt").write_text("test content")
        test_repo.index.add("test.txt")
        test_repo.index.write()
        
        tree = test_repo.index.write_tree()
        test_repo.create_commit(
            "HEAD", signature, signature, "Initial commit", tree, []
        )
        
        # Should not raise even with minimal repository
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        # Should return empty strings for missing metadata
        assert isinstance(owner, str)
        assert isinstance(repo_name, str)
        assert isinstance(branch, str)
        assert isinstance(remote_url, str)
        assert isinstance(source_type, str)