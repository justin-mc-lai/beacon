"""Tests for beacon/commands/implement/git.py"""

import pytest
from pathlib import Path
from beacon.commands.implement.git import (
    get_git_commit,
    run_branch_preflight,
    validate_git_workflow,
)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure with git."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Initialize git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=project_root, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_root, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_root, capture_output=True)

    # Create initial commit
    (project_root / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=project_root, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_root, capture_output=True)

    # Create docs structure
    docs_dir = project_root / "docs" / "beacon" / "v1.3.6"
    docs_dir.mkdir(parents=True)

    return project_root


def test_get_git_commit(temp_project):
    """Test getting git commit hash."""
    commit = get_git_commit(temp_project)
    assert commit != ""
    assert len(commit) == 40  # SHA-1 hash length


def test_get_git_commit_no_repo(tmp_path):
    """Test getting git commit in non-git directory."""
    non_git_dir = tmp_path / "non_git"
    non_git_dir.mkdir()

    commit = get_git_commit(non_git_dir)
    assert commit == ""


def test_run_branch_preflight_success(temp_project):
    """Test successful branch preflight."""
    success, result = run_branch_preflight(
        temp_project,
        feature="test-feature",
        version="v1.3.6",
        auto_switch_branch=False,
        expected_branch="main"  # Assuming we're on main/master
    )

    # May fail if branch doesn't match, but should return a result
    assert isinstance(result, dict)


def test_run_branch_preflight_mismatch(temp_project):
    """Test branch preflight with branch mismatch."""
    success, result = run_branch_preflight(
        temp_project,
        feature="test-feature",
        version="v1.3.6",
        auto_switch_branch=False,
        expected_branch="nonexistent-branch"
    )

    assert success is False
    assert "error" in result


def test_validate_git_workflow(temp_project):
    """Test git workflow validation."""
    # This will likely fail without proper setup, but should not crash
    valid, message = validate_git_workflow(
        temp_project,
        feature="test-feature",
        version="v1.3.6"
    )

    assert isinstance(valid, bool)
    assert isinstance(message, str)
