from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _git(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_repo(root: Path, branch: str) -> None:
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_dual_version_metadata(root: Path) -> dict:
    result = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(root),
            "--topology-kind",
            "single_repo",
            "--default-execution-service",
            "beacon",
            "--service-key",
            "beacon",
            "--repo-root",
            str(root),
            "--version",
            "v1.4.0",
            "--branch",
            "hotfix/BUG-1-v1.3.3",
            "--branch-governance-template",
            "previous-hotfix-forward-port",
            "--previous-version-baseline-branch",
            "feature/v1.3.3-all",
            "--next-version-feature-branch",
            "feature/v1.3.4-all",
            "--hotfix-branch-naming-rule",
            "hotfix/<ticket>-<version>",
            "--merge-direction-policy",
            "previous_baseline->hotfix",
            "--merge-direction-policy",
            "hotfix->uat",
            "--merge-direction-policy",
            "hotfix->next_feature",
            "--forbidden-direction",
            "next_feature->first_production_fix",
            "--evidence-contract",
            "source_commit",
            "--evidence-contract",
            "forward_port_commit",
            "--evidence-contract",
            "origin_uat_head",
            "--evidence-contract",
            "pipeline_run_id",
            "--evidence-field",
            "source_commit=abc123",
            "--evidence-field",
            "forward_port_commit=def456",
            "--evidence-field",
            "origin_uat_head=uat789",
            "--evidence-field",
            "pipeline_run_id=pipe001",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    return json.loads(result.stdout)


def test_flow_diagram_required(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    _seed_dual_version_metadata(tmp_path)
    result = runner.invoke(
        app,
        ["doctor", "branch-governance", "show", "--project-root", str(tmp_path), "--version", "v1.4.0", "--json"],
    )
    payload = json.loads(result.stdout)
    assert "### Flow Diagram" in payload["result"]["human_markdown"]


def test_current_position_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    _seed_dual_version_metadata(tmp_path)
    result = runner.invoke(
        app,
        ["doctor", "branch-governance", "show", "--project-root", str(tmp_path), "--version", "v1.4.0", "--json"],
    )
    payload = json.loads(result.stdout)
    assert "[current]" in payload["result"]["human_markdown"]


def test_allowed_and_forbidden_paths_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    _seed_dual_version_metadata(tmp_path)
    result = runner.invoke(
        app,
        ["doctor", "branch-governance", "show", "--project-root", str(tmp_path), "--version", "v1.4.0", "--json"],
    )
    payload = json.loads(result.stdout)
    text = payload["result"]["human_markdown"]
    assert "### Allowed Paths" in text
    assert "### Forbidden Paths" in text
    assert "next_feature->first_production_fix" in text


def test_next_action_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    _seed_dual_version_metadata(tmp_path)
    result = runner.invoke(
        app,
        ["doctor", "branch-governance", "show", "--project-root", str(tmp_path), "--version", "v1.4.0", "--json"],
    )
    payload = json.loads(result.stdout)
    assert "recommended_action" in payload["result"]["human_markdown"]
