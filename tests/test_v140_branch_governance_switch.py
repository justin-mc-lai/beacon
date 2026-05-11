from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

from beacon.utils.git_alignment import ensure_expected_worktree_lane, switch_to_expected_branch


_IMPLEMENT_SPEC = importlib.util.spec_from_file_location(
    "beacon_commands_implement_file_v140_switch",
    Path(__file__).resolve().parents[1] / "beacon" / "commands" / "implement.py",
)
assert _IMPLEMENT_SPEC and _IMPLEMENT_SPEC.loader
_IMPLEMENT_MODULE = importlib.util.module_from_spec(_IMPLEMENT_SPEC)
_IMPLEMENT_SPEC.loader.exec_module(_IMPLEMENT_MODULE)
_run_branch_preflight = _IMPLEMENT_MODULE._run_branch_preflight


def _git(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_repo(root: Path, branch: str = "main") -> None:
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def test_switch_to_compliant_branch(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "main")
    payload = switch_to_expected_branch(tmp_path, "hotfix/BUG-1-v1.3.3", create_if_missing=True)
    assert payload["status"] == "switched"


def test_create_or_switch_worktree(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "main")
    target = tmp_path.parent / f"{tmp_path.name}-worktree-bugfix"
    payload = ensure_expected_worktree_lane(
        tmp_path,
        "hotfix/BUG-1-v1.3.3",
        worktree_path=str(target),
        base_branch="main",
    )
    assert payload["status"] == "created"
    assert target.exists()


def test_switch_action_explained(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "main")
    target = tmp_path.parent / f"{tmp_path.name}-worktree-bugfix"
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version="v1.4.0",
        run_id="run-test",
        feature="demo",
        auto_switch_branch=True,
        require_clean_worktree_for_switch=True,
        expected_branch="hotfix/BUG-1-v1.3.3",
        branch_prefix="hotfix/",
        base_branch="main",
        git_roots=["."],
        direct_delivery_services=["."],
        branch_governance={
            "template_name": "previous-hotfix-forward-port",
            "previous_version_baseline_branch": "feature/v1.3.3-all",
            "next_version_feature_branch": "feature/v1.3.4-all",
            "hotfix_branch_naming_rule": "hotfix/<ticket>-<version>",
            "worktree_mode": "dedicated-worktree",
            "worktree_path": str(target),
            "evidence_contract": [],
        },
    )
    assert "cd " in payload["recommended_command"]
    assert payload["worktree_attempt"]["status"] in {"created", "switched"}


def test_fail_closed_if_switch_not_safe(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "main")
    (tmp_path / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version="v1.4.0",
        run_id="run-test",
        feature="demo",
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch="hotfix/BUG-1-v1.3.3",
        branch_prefix="hotfix/",
        base_branch="main",
        git_roots=["."],
        direct_delivery_services=["."],
        branch_governance={},
    )
    assert payload["blocked"] is True
    assert "implement_branch_switch_dirty_worktree" in payload["reason_codes"]


def test_branch_preflight_preserves_service_repo_current_worktree(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    service_root = workspace / "marketing_sys"
    service_root.mkdir()
    _seed_repo(service_root, "feature/v1.3.5-mainline")
    payload = _run_branch_preflight(
        project_root=workspace,
        version="v1.3.5",
        run_id="run-test",
        feature="partner-rule-adjustment",
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch="feature/v1.3.5-mainline",
        branch_prefix="feature/",
        base_branch="master",
        git_roots=[str(service_root)],
        direct_delivery_services=["marketing_sys"],
        branch_governance={
            "template_name": "standard-feature",
            "worktree_mode": "dedicated-worktree",
            "repo_root": str(service_root),
            "worktree_path": str(service_root),
            "current_worktree_path": str(service_root),
            "evidence_contract": [],
        },
    )
    assert payload["blocked"] is False
    assert payload["branch_governance"]["blocked"] is False
    assert payload["branch_governance"]["current_worktree_path"] == str(service_root.resolve())
