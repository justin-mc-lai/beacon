"""Tests for admission code-level merge-main (UD-020, AC-017 code impl).

R4 truth §4.2: implement must merge main into the dev branch before writing.
This tests the code-level enforcement in run_workspace_admit.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from beacon.utils.workspace_admission import run_workspace_admit


def _contract(require_admission: bool = True, canonical_branch: str = "beacon/v1.6.3", baseline: str = "main"):
    return {
        "require_workspace_admission": require_admission,
        "canonical_branch": canonical_branch,
        "previous_version_baseline_branch": baseline,
        "admission_invalidation": "dirty_only",
        "worktree_mode": "dedicated",
        "feature_branch_pattern": "beacon/v1.6.3/<feature-slug>",
        "worktree_root": ".beacon/worktrees/v1.6.3/<feature-slug>/",
    }


# ---- AC-017 code: merge-main executed on implement admission ----

def test_admission_merges_main_for_implement(tmp_path: Path) -> None:
    """run_workspace_admit merges main into the feature branch (code-level)."""
    contract = _contract()
    with patch("beacon.utils.workspace_admission.load_admission_contract", return_value=contract), \
         patch("beacon.utils.workspace_admission.ensure_expected_worktree_lane", return_value={
             "status": "created", "worktree_path": str(tmp_path / "wt"),
         }), \
         patch("beacon.utils.workspace_admission.git_output", side_effect=_git_stub), \
         patch("beacon.utils.workspace_admission._merge_main_into_feature_branch", return_value={
             "status": "merged", "base_branch": "main", "stdout": "Fast-forward",
         }) as merge_mock, \
         patch("beacon.utils.workspace_admission.write_admission_artifact"):
        payload = run_workspace_admit(tmp_path, version="v1.6.3", feature="demo-feat")
    # merge-main must have been invoked
    merge_mock.assert_called_once()
    # payload must carry the merge result
    assert payload.get("merge_main") is not None
    assert payload["merge_main"]["status"] == "merged"


def test_admission_merge_main_blocked_on_conflict(tmp_path: Path) -> None:
    """When merge-main conflicts, admission blocks with merge_main_conflict."""
    contract = _contract()
    with patch("beacon.utils.workspace_admission.load_admission_contract", return_value=contract), \
         patch("beacon.utils.workspace_admission.ensure_expected_worktree_lane", return_value={
             "status": "created", "worktree_path": str(tmp_path / "wt"),
         }), \
         patch("beacon.utils.workspace_admission.git_output", side_effect=_git_stub), \
         patch("beacon.utils.workspace_admission._merge_main_into_feature_branch", return_value={
             "status": "conflict", "base_branch": "main", "stderr": "CONFLICT",
         }), \
         patch("beacon.utils.workspace_admission.write_admission_artifact"):
        payload = run_workspace_admit(tmp_path, version="v1.6.3", feature="demo-feat")
    assert payload.get("status") == "blocked"
    assert "merge_main_conflict" in payload.get("reason_codes", [])


def test_admission_skips_merge_when_not_required(tmp_path: Path) -> None:
    """When workspace admission not required, merge-main is skipped."""
    contract = _contract(require_admission=False)
    with patch("beacon.utils.workspace_admission.load_admission_contract", return_value=contract), \
         patch("beacon.utils.workspace_admission._merge_main_into_feature_branch") as merge_mock:
        payload = run_workspace_admit(tmp_path, version="v1.6.3", feature="demo-feat")
    merge_mock.assert_not_called()
    assert payload.get("skipped") is True


def _git_stub(project_root: Path, *args: str, timeout: float = 5) -> str:
    # stub for git_output calls (rev-parse HEAD, branch --show-current)
    if "rev-parse" in args and "HEAD" in args:
        return "abc1234"
    if "branch" in args and "--show-current" in args:
        return "beacon/v1.6.3/demo-feat"
    return ""
