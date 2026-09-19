import pygit2
import pytest

from gitintel.git.repository import get_repository_metadata, open_repository


def test_open_repository_valid_path():
    """Test opening a valid repository."""
    # Open the current repository (GitIntel itself)
    repo = open_repository(".")
    
    assert repo is not None
    assert isinstance(repo, pygit2.Repository)


def test_open_repository_invalid_path():
    """Test opening an invalid repository raises ValueError."""
    with pytest.raises(ValueError, match="Invalid Git repository"):
        open_repository("/nonexistent/path")


def test_open_repository_non_git_directory():
    """Test opening a directory that exists but is not a git repository."""
    with pytest.raises(ValueError, match="Invalid Git repository"):
        open_repository("/tmp")


def test_get_repository_metadata_current_repo():
    """Test extracting metadata from the current repository."""
    repo = open_repository(".")
    owner, repo_name, branch, remote_url, source_type = get_repository_metadata(repo)
    
    # Basic validation that we get strings back
    assert isinstance(owner, str)
    assert isinstance(repo_name, str)
    assert isinstance(branch, str)
    assert isinstance(remote_url, str)
    assert isinstance(source_type, str)
    
    # The current repo should have some metadata
    assert source_type in ["Local", "GitHub", "GitLab", "Bitbucket", ""]


def test_get_repository_metadata_no_remotes():
    """Test repository metadata when no remotes exist."""
    # Create a temporary repository with no remotes
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
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
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        # Should still work but with empty remote info
        assert owner == ""
        assert repo_name == ""
        assert branch in ["main", "master"]  # Default branch name varies by git version
        assert remote_url == ""
        assert source_type == "Local"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_repository_metadata_unborn_head():
    """Test repository metadata when HEAD is unborn (no commits)."""
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
        repo_path = Path(temp_dir) / "empty_repo"
        repo_path.mkdir()
        
        # Initialize a git repo with no commits
        test_repo = pygit2.init_repository(repo_path)
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        # Should handle unborn head gracefully
        assert owner == ""
        assert repo_name == ""
        assert branch == ""  # No branch yet
        assert remote_url == ""
        assert source_type == "Local"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_repository_metadata_github_url():
    """Test metadata extraction from GitHub URL."""
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
        repo_path = Path(temp_dir) / "github_repo"
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
        
        # Add a GitHub remote
        test_repo.remotes.create("origin", "https://github.com/user/repo.git")
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        assert owner == "user"
        assert repo_name == "repo"
        assert branch in ["main", "master"]  # Default branch name varies by git version
        assert remote_url == "https://github.com/user/repo.git"
        assert source_type == "GitHub"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_repository_metadata_ssh_github_url():
    """Test metadata extraction from SSH GitHub URL."""
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
        repo_path = Path(temp_dir) / "ssh_repo"
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
        
        # Add an SSH GitHub remote
        test_repo.remotes.create("origin", "git@github.com:user/repo.git")
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        assert owner == "user"
        assert repo_name == "repo"
        assert branch in ["main", "master"]  # Default branch name varies by git version
        assert remote_url == "git@github.com:user/repo.git"
        assert source_type == "GitHub"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_repository_metadata_non_github_url():
    """Test metadata extraction from non-GitHub URL."""
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
        repo_path = Path(temp_dir) / "other_repo"
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
        
        # Add a non-GitHub remote
        test_repo.remotes.create("origin", "https://gitlab.com/user/repo.git")
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        assert owner == "user"
        assert repo_name == "repo"
        assert branch in ["main", "master"]  # Default branch name varies by git version
        assert remote_url == "https://gitlab.com/user/repo.git"
        assert source_type == "Local"  # Not GitHub
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_repository_metadata_fallback_remote():
    """Test metadata extraction when origin doesn't exist but other remotes do."""
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
        repo_path = Path(temp_dir) / "fallback_repo"
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
        
        # Add a non-origin remote
        test_repo.remotes.create("upstream", "https://github.com/user/repo.git")
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        # Should fall back to the first available remote
        assert owner == "user"
        assert repo_name == "repo"
        assert branch in ["main", "master"]  # Default branch name varies by git version
        assert remote_url == "https://github.com/user/repo.git"
        assert source_type == "GitHub"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_repository_metadata_url_with_git_suffix():
    """Test that .git suffix is properly stripped from repo name."""
    import shutil
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    try:
        repo_path = Path(temp_dir) / "suffix_repo"
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
        
        # Add a remote with .git suffix
        test_repo.remotes.create("origin", "https://github.com/user/repo.git")
        
        owner, repo_name, branch, remote_url, source_type = get_repository_metadata(test_repo)
        
        assert owner == "user"
        assert repo_name == "repo"  # .git should be stripped
        assert branch in ["main", "master"]  # Default branch name varies by git version
        assert remote_url == "https://github.com/user/repo.git"  # Original URL preserved
        assert source_type == "GitHub"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)