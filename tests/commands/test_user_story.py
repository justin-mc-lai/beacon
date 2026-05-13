"""Tests for beacon/commands/user_story.py"""

import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from beacon.commands.user_story import app


runner = CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create docs structure
    docs_dir = project_root / "docs" / "beacon" / "v1.3.6"
    (docs_dir / "prd").mkdir(parents=True)
    (docs_dir / "user-story").mkdir(parents=True)

    # Create .beacon structure
    beacon_dir = project_root / ".beacon"
    (beacon_dir / "prd").mkdir(parents=True)
    (beacon_dir / "user-story").mkdir(parents=True)

    # Create a sample PRD
    prd_md = docs_dir / "prd" / "test-feature.md"
    prd_md.write_text("# PRD: Test Feature\n\n## Overview\nTest feature description")

    return project_root


def test_user_story_create_basic(temp_project):
    """Test basic user story creation."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0

    # Check human markdown output
    story_md = temp_project / "docs" / "beacon" / "v1.3.6" / "user-story" / "test-feature.md"
    assert story_md.exists()

    # Check machine JSON output
    story_json = temp_project / ".beacon" / "user-story" / "test-feature.json"
    assert story_json.exists()


def test_user_story_acceptance_criteria_structure(temp_project):
    """Test acceptance criteria structure."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0

    story_json = temp_project / ".beacon" / "user-story" / "test-feature.json"
    with open(story_json) as f:
        data = json.load(f)
        assert "acceptance_criteria" in data
        ac = data["acceptance_criteria"]

        # Check AC structure
        assert "functionality" in ac
        assert "data" in ac
        assert "ux" in ac
        assert "performance" in ac
        assert "security" in ac
        assert "compatibility" in ac
        assert "error_handling" in ac


def test_user_story_semantic_payload(temp_project):
    """Test semantic payload support."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--semantic"
    ])

    assert result.exit_code == 0

    story_json = temp_project / ".beacon" / "user-story" / "test-feature.json"
    with open(story_json) as f:
        data = json.load(f)
        assert "semantic_payload" in data


def test_user_story_state_sync(temp_project):
    """Test story state synchronization."""
    # Create user story
    runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    # Sync state
    result = runner.invoke(app, [
        "sync-state",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0


def test_user_story_missing_prd(temp_project):
    """Test error handling when PRD is missing."""
    result = runner.invoke(app, [
        "create",
        "nonexistent-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code != 0
    assert "prd" in result.stdout.lower()


def test_user_story_should_consume_research_closure_sections(temp_project):
    docs_dir = temp_project / "docs" / "beacon" / "v1.3.6"
    (docs_dir / "research").mkdir(parents=True, exist_ok=True)
    (docs_dir / "research" / "test-feature.md").write_text(
        "\n".join(
            [
                "# Research Closure",
                "",
                "## Business Flow",
                "- 用户提交申请后，系统必须进入人工审核流程。",
                "",
                "## State Machine",
                "- 状态必须支持 draft -> reviewing -> approved -> rejected。",
                "",
                "## Decision Priority",
                "- 当审核失败时，必须提示错误并允许恢复重试。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "create",
            "test-feature",
            "--version",
            "v1.3.6",
            "--project-root",
            str(temp_project),
        ],
    )
    assert result.exit_code == 0

    story_json = temp_project / ".beacon" / "user-story" / "test-feature.json"
    with open(story_json) as f:
        data = json.load(f)
    flat_values = []
    for values in data["acceptance_criteria"].values():
        if isinstance(values, list):
            flat_values.extend(values)
    assert any("人工审核流程" in item for item in flat_values)
    assert any("draft -> reviewing -> approved -> rejected" in item for item in flat_values)
    assert any("恢复重试" in item for item in flat_values)
