from __future__ import annotations

import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.implement.commands import _branch_guard_inputs, _run_branch_preflight
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


def _seed_forbidden_dual_version_metadata(root: Path) -> None:
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
            "feature/v1.3.4-all",
            "--branch-governance-template",
            "previous-hotfix-forward-port",
            "--previous-version-baseline-branch",
            "feature/v1.3.3-all",
            "--next-version-feature-branch",
            "feature/v1.3.4-all",
            "--hotfix-branch-naming-rule",
            "hotfix/<ticket>-<version>",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout


def test_implement_loads_contract(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/v1.3.4-all")
    _seed_forbidden_dual_version_metadata(tmp_path)
    inputs = _branch_guard_inputs(tmp_path, version="v1.4.0", feature="demo")
    assert inputs["branch_governance"]["template_name"] == "previous-hotfix-forward-port"


def test_implement_verifies_alignment(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/v1.3.4-all")
    _seed_forbidden_dual_version_metadata(tmp_path)
    inputs = _branch_guard_inputs(tmp_path, version="v1.4.0", feature="demo")
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version="v1.4.0",
        run_id="run-test",
        feature="demo",
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch=str(inputs["expected_branch"]),
        branch_prefix=str(inputs["branch_prefix"]),
        base_branch=str(inputs["base_branch"]),
        git_roots=list(inputs["git_roots"]),
        direct_delivery_services=list(inputs["direct_delivery_services"]),
        branch_governance=inputs["branch_governance"],
    )
    assert payload["branch_governance"]["blocked"] is True
    assert "branch_governance_forbidden_first_fix_lane" in payload["reason_codes"]


def test_evidence_contract_checked(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "hotfix/BUG-1-v1.3.3")
    result = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(tmp_path),
            "--topology-kind",
            "single_repo",
            "--default-execution-service",
            "beacon",
            "--service-key",
            "beacon",
            "--repo-root",
            str(tmp_path),
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
            "--evidence-contract",
            "source_commit",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    inputs = _branch_guard_inputs(tmp_path, version="v1.4.0", feature="demo")
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version="v1.4.0",
        run_id="run-test",
        feature="demo",
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch=str(inputs["expected_branch"]),
        branch_prefix=str(inputs["branch_prefix"]),
        base_branch=str(inputs["base_branch"]),
        git_roots=list(inputs["git_roots"]),
        direct_delivery_services=list(inputs["direct_delivery_services"]),
        branch_governance=inputs["branch_governance"],
    )
    assert "branch_governance_evidence_missing" in payload["reason_codes"]


def test_blocked_state_prevents_code_execution(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/v1.3.4-all")
    _seed_forbidden_dual_version_metadata(tmp_path)
    result = runner.invoke(
        app,
        [
            "implement",
            "check-branch",
            "--project",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--feature",
            "demo",
            "--json",
        ],
    )
    assert result.exit_code == 2, result.stdout
    assert "branch_governance_forbidden_first_fix_lane" in result.stdout
