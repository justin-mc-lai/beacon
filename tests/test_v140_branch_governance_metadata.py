from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.project_metadata import resolve_project_metadata_view


runner = CliRunner()


def _create_metadata(root: Path) -> None:
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
            "--allow-worktree-when-feature-dirty",
            "--merge-direction-policy",
            "previous_baseline->hotfix",
            "--merge-direction-policy",
            "hotfix->uat",
            "--forbidden-direction",
            "next_feature->first_production_fix",
            "--evidence-contract",
            "source_commit",
            "--evidence-field",
            "source_commit=abc123",
            "--worktree-mode",
            "dedicated-worktree",
            "--worktree-path",
            str(root / ".." / "worktrees" / "bugfix-lane"),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout


def test_previous_baseline_field_supported(tmp_path: Path) -> None:
    _create_metadata(tmp_path)
    view = resolve_project_metadata_view(tmp_path, version="v1.4.0")
    assert view["version_contract"]["previous_version_baseline_branch"] == "feature/v1.3.3-all"


def test_next_feature_field_supported(tmp_path: Path) -> None:
    _create_metadata(tmp_path)
    view = resolve_project_metadata_view(tmp_path, version="v1.4.0")
    assert view["version_contract"]["next_version_feature_branch"] == "feature/v1.3.4-all"


def test_hotfix_and_worktree_fields_supported(tmp_path: Path) -> None:
    _create_metadata(tmp_path)
    view = resolve_project_metadata_view(tmp_path, version="v1.4.0")
    contract = view["version_contract"]
    assert contract["hotfix_branch_naming_rule"] == "hotfix/<ticket>-<version>"
    assert contract["allow_worktree_when_feature_dirty"] is True
    assert contract["branch_governance"]["worktree_mode"] == "dedicated-worktree"


def test_merge_and_evidence_fields_supported(tmp_path: Path) -> None:
    _create_metadata(tmp_path)
    payload = json.loads((tmp_path / ".beacon" / "metadata" / "project-version-metadata.json").read_text(encoding="utf-8"))
    contract = payload["version_scoped_metadata"]["v1.4.0"]
    assert "previous_baseline->hotfix" in contract["merge_direction_policy"]
    assert contract["evidence_contract"] == ["source_commit"]
    assert contract["evidence"]["source_commit"] == "abc123"
