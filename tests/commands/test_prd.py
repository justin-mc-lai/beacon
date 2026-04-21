"""Tests for beacon/commands/prd.py"""

import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from beacon.commands.prd import app


runner = CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create docs structure
    docs_dir = project_root / "docs" / "beacon" / "v1.3.6" / "prd"
    docs_dir.mkdir(parents=True)

    # Create .beacon structure
    beacon_dir = project_root / ".beacon" / "prd"
    beacon_dir.mkdir(parents=True)

    return project_root


def test_prd_create_basic(temp_project):
    """Test basic PRD creation."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0

    # Check human markdown output
    prd_md = temp_project / "docs" / "beacon" / "v1.3.6" / "prd" / "test-feature.md"
    assert prd_md.exists()

    # Check machine JSON output
    prd_json = temp_project / ".beacon" / "prd" / "test-feature.json"
    assert prd_json.exists()

    # Verify JSON structure
    with open(prd_json) as f:
        data = json.load(f)
        assert "metadata" in data
        assert "content" in data
        assert data["metadata"]["feature"] == "test-feature"
        assert data["metadata"]["version"] == "v1.3.6"


def test_prd_semantic_compilation(temp_project):
    """Test semantic PRD compilation."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--semantic"
    ])

    assert result.exit_code == 0

    # Check semantic payload
    prd_json = temp_project / ".beacon" / "prd" / "test-feature.json"
    with open(prd_json) as f:
        data = json.load(f)
        assert "semantic_payload" in data
        assert "track" in data["semantic_payload"]
        assert "family" in data["semantic_payload"]


def test_prd_track_classification(temp_project):
    """Test PRD track classification."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--track", "main"
    ])

    assert result.exit_code == 0

    prd_json = temp_project / ".beacon" / "prd" / "test-feature.json"
    with open(prd_json) as f:
        data = json.load(f)
        assert data["semantic_payload"]["track"] == "main"


def test_prd_family_classification(temp_project):
    """Test PRD family classification."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--family", "tooling_surface"
    ])

    assert result.exit_code == 0

    prd_json = temp_project / ".beacon" / "prd" / "test-feature.json"
    with open(prd_json) as f:
        data = json.load(f)
        assert data["semantic_payload"]["family"] == "tooling_surface"


def test_prd_contract_validation(temp_project):
    """Test PRD contract validation."""
    # Create a PRD first
    runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    # Validate contract
    result = runner.invoke(app, [
        "validate",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0
    assert "Contract valid" in result.stdout


def test_prd_transaction_consistency(temp_project):
    """Test transaction-based writes consistency."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0

    # Check transaction log
    transaction_log = temp_project / ".beacon" / "transactions" / "prd-test-feature.json"
    assert transaction_log.exists()

    with open(transaction_log) as f:
        data = json.load(f)
        assert "canonical_envelope" in data
        assert "sinks" in data
        assert len(data["sinks"]) == 2  # human + machine


def test_prd_anti_drift_audit(temp_project):
    """Test anti-drift auditability."""
    # Create PRD
    runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    # Audit for drift
    result = runner.invoke(app, [
        "audit",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code == 0
    assert "No drift detected" in result.stdout


def test_prd_mode_contract(temp_project):
    """Test mode contract tracking."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--mode", "auto"
    ])

    assert result.exit_code == 0

    prd_json = temp_project / ".beacon" / "prd" / "test-feature.json"
    with open(prd_json) as f:
        data = json.load(f)
        assert "mode_contract" in data
        assert data["mode_contract"]["compilation_mode"] == "auto"


def test_prd_missing_version(temp_project):
    """Test error handling for missing version."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--project-root", str(temp_project)
    ])

    assert result.exit_code != 0
    assert "version" in result.stdout.lower()


def test_prd_invalid_track(temp_project):
    """Test error handling for invalid track."""
    result = runner.invoke(app, [
        "create",
        "test-feature",
        "--version", "v1.3.6",
        "--project-root", str(temp_project),
        "--track", "invalid"
    ])

    assert result.exit_code != 0
    assert "track" in result.stdout.lower()
