"""Tests for beacon/commands/test_case.py"""

import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from beacon.commands.test_case import app


runner = CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create docs structure
    docs_dir = project_root / "docs" / "beacon" / "v1.3.6"
    (docs_dir / "user-story").mkdir(parents=True)
    (docs_dir / "qa" / "test-cases").mkdir(parents=True)

    # Create .beacon structure
    beacon_dir = project_root / ".beacon"
    (beacon_dir / "user-story").mkdir(parents=True)
    (beacon_dir / "qa").mkdir(parents=True)

    # Create a sample user story
    story_md = docs_dir / "user-story" / "test-feature.md"
    story_md.write_text("# User Story: Test Feature\n\n## Acceptance Criteria\n- AC1\n- AC2")

    story_json = beacon_dir / "user-story" / "test-feature.json"
    story_json.write_text(json.dumps({
        "feature": "test-feature",
        "acceptance_criteria": {
            "functionality": ["AC1", "AC2"]
        }
    }))

    return project_root


def test_test_case_create_basic(temp_project):
    """Test basic test case creation."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0

    # Check test case markdown
    tc_md = temp_project / "docs" / "beacon" / "v1.3.6" / "qa" / "test-cases" / "test-feature.md"
    assert tc_md.exists()


def test_test_case_qa9_matrix(temp_project):
    """Test QA9 matrix generation."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--qa9"
    ])

    assert result.exit_code == 0

    # Check QA9 matrix
    qa9_json = temp_project / ".beacon" / "qa" / "test-feature-qa9-matrix.json"
    assert qa9_json.exists()

    with open(qa9_json) as f:
        data = json.load(f)
        assert "qa_types" in data
        qa_types = data["qa_types"]

        # Check all 9 QA types
        assert "functional" in qa_types
        assert "smoke" in qa_types
        assert "unit" in qa_types
        assert "interface" in qa_types
        assert "contract" in qa_types
        assert "integration" in qa_types
        assert "regression" in qa_types
        assert "exception" in qa_types
        assert "compatibility" in qa_types


def test_test_case_ac_to_tc_mapping(temp_project):
    """Test AC-to-TC mapping."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0

    tc_json = temp_project / ".beacon" / "qa" / "test-feature.json"
    with open(tc_json) as f:
        data = json.load(f)
        assert "ac_to_tc_mapping" in data
        mapping = data["ac_to_tc_mapping"]

        # Each AC should map to at least one TC
        assert len(mapping) > 0


def test_test_case_story_scenario_expansion(temp_project):
    """Test story scenario expansion."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--expand-scenarios"
    ])

    assert result.exit_code == 0

    tc_json = temp_project / ".beacon" / "qa" / "test-feature.json"
    with open(tc_json) as f:
        data = json.load(f)
        assert "scenarios" in data
        assert len(data["scenarios"]) > 0


def test_test_case_prototype_contract(temp_project):
    """Test prototype contract integration."""
    # Create a prototype contract
    prototype_dir = temp_project / "docs" / "beacon" / "v1.3.6" / "prototype" / "test-feature"
    prototype_dir.mkdir(parents=True)

    contract_json = prototype_dir / "contract.json"
    contract_json.write_text(json.dumps({
        "navigation": ["route1", "route2"],
        "interaction": ["click", "input"],
        "route_closure": True
    }))

    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--prototype-contract"
    ])

    assert result.exit_code == 0

    tc_json = temp_project / ".beacon" / "qa" / "test-feature.json"
    with open(tc_json) as f:
        data = json.load(f)
        assert "prototype_contract" in data


def test_test_case_missing_user_story(temp_project):
    """Test error handling when user story is missing."""
    result = runner.invoke(app, [
        "create",
        "nonexistent-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code != 0
    assert "user story" in result.stdout.lower() or "user-story" in result.stdout.lower()
