from __future__ import annotations

import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.branch_governance import DUAL_VERSION_TEMPLATE, resolve_branch_governance_view
from beacon.utils.project_metadata import resolve_project_metadata_view


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


def _seed_metadata(root: Path) -> None:
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
            "feature/v1.4.0-all",
            "--branch-governance-template",
            "standard-feature",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout


def _metadata_view(root: Path) -> dict:
    return resolve_project_metadata_view(root, version="v1.4.0")


def _task_override_workflow(root: Path, *, target_branch: str = "hotfix/BUG-1-v1.3.3") -> dict:
    return {
        "expected_branch": target_branch,
        "base_branch": "feature/v1.3.3-all",
        "worktree_root": str(root),
        "worktree_path": str(root),
        "use_git_worktree": False,
        "branch_governance_override": {
            "template_name": DUAL_VERSION_TEMPLATE,
            "previous_version_baseline_branch": "feature/v1.3.3-all",
            "next_version_feature_branch": "feature/v1.4.0-all",
            "hotfix_branch_naming_rule": "hotfix/<ticket>-<version>",
            "evidence": {
                "source_commit": "abc123",
                "forward_port_commit": "def456",
                "origin_uat_head": "uat789",
                "pipeline_run_id": "pipe-001",
            },
        },
    }


def test_project_default_template_supported(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/v1.4.0-all")
    _seed_metadata(tmp_path)
    payload = resolve_branch_governance_view(
        project_root=tmp_path,
        version="v1.4.0",
        feature="demo",
        metadata_view=_metadata_view(tmp_path),
        git_workflow={
            "expected_branch": "feature/v1.4.0-all",
            "base_branch": "feature/v1.4.0-all",
            "worktree_root": str(tmp_path),
            "worktree_path": str(tmp_path),
        },
    )
    assert payload["template_name"] == "standard-feature"
    assert payload["template_source"] == "project_metadata"


def test_task_override_template_supported(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    _seed_metadata(tmp_path)
    payload = resolve_branch_governance_view(
        project_root=tmp_path,
        version="v1.4.0",
        feature="demo",
        metadata_view=_metadata_view(tmp_path),
        git_workflow=_task_override_workflow(tmp_path),
    )
    assert payload["template_name"] == DUAL_VERSION_TEMPLATE
    assert payload["template_source"] == "task_override"


def test_override_cannot_break_hard_rules(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/v1.4.0-all")
    _seed_metadata(tmp_path)
    payload = resolve_branch_governance_view(
        project_root=tmp_path,
        version="v1.4.0",
        feature="demo",
        metadata_view=_metadata_view(tmp_path),
        git_workflow=_task_override_workflow(tmp_path, target_branch="feature/v1.4.0-all"),
    )
    assert payload["blocked"] is True
    assert "branch_governance_forbidden_first_fix_lane" in payload["reason_codes"]


def test_selected_template_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    _seed_metadata(tmp_path)
    payload = resolve_branch_governance_view(
        project_root=tmp_path,
        version="v1.4.0",
        feature="demo",
        metadata_view=_metadata_view(tmp_path),
        git_workflow=_task_override_workflow(tmp_path),
    )
    assert payload["template_source"] == "task_override"
    assert "- template_source: `task_override`" in payload["human_markdown"]


def test_monorepo_selected_service_uses_repo_root_as_current_worktree(tmp_path: Path) -> None:
    workspace = tmp_path / "rolo"
    workspace.mkdir()
    service_root = workspace / "marketing_sys"
    service_root.mkdir()
    _seed_repo(service_root, "feature/v1.3.5-mainline")
    metadata_root = workspace / ".beacon" / "metadata"
    metadata_root.mkdir(parents=True)
    (metadata_root / "project-version-metadata.json").write_text(
        """
{
  "schema_version": "1.0",
  "project_root": "__PROJECT_ROOT__",
  "global_project_metadata": {
    "project_root": "__PROJECT_ROOT__",
    "topology_kind": "monorepo",
    "default_execution_service": "marketing_sys",
    "service_bindings": [
      {
        "service_key": "marketing_sys",
        "repo_root": "__SERVICE_ROOT__",
        "repo_root_relative": "marketing_sys",
        "role": "service",
        "writable": true,
        "worktree_path_policy": "follow-repo-root"
      }
    ]
  },
  "version_scoped_metadata": {
    "v1.3.5": {
      "participating_services": ["marketing_sys"],
      "per_service_canonical_branch": {
        "marketing_sys": "feature/v1.3.5-mainline"
      }
    }
  },
  "transaction": {}
}
        """.strip()
        .replace("__PROJECT_ROOT__", str(workspace.resolve()))
        .replace("__SERVICE_ROOT__", str(service_root.resolve())),
        encoding="utf-8",
    )
    payload = resolve_branch_governance_view(
        project_root=workspace,
        version="v1.3.5",
        feature="partner-rule-adjustment",
        metadata_view=resolve_project_metadata_view(workspace, version="v1.3.5"),
        git_workflow={
            "expected_branch": "feature/v1.3.5-mainline",
            "base_branch": "master",
            "use_git_worktree": True,
            "worktree_mode": "dedicated-worktree",
            "worktree_root": str(workspace),
            "worktree_path": str(service_root),
        },
    )
    assert payload["repo_root"] == str(service_root.resolve())
    assert payload["current_worktree_path"] == str(service_root.resolve())
    assert payload["worktree_path"] == str(service_root.resolve())
    assert payload["blocked"] is False
