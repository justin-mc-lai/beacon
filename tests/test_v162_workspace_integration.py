from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.test_v162_workspace_admit import FEATURE, VERSION, _seed_governance, _seed_repo

from beacon.utils.workspace_admission import gate_workspace_admission_or_block, run_workspace_admit


def _invoke(args: list[str], *, cwd: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={"BEACON_ALLOW_CONTEXT_VERSION_DRIFT": "1", **dict(__import__("os").environ)},
    )
    payload: dict = {"_exit_code": proc.returncode, "_stderr": proc.stderr}
    if proc.stdout.strip():
        payload.update(json.loads(proc.stdout))
    return payload


def test_gate_implement_blocked_without_artifact(tmp_path: Path) -> None:
    """TC-WS-010 semantics: admission gate blocks when artifact missing."""
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    block = gate_workspace_admission_or_block(tmp_path, version=VERSION, feature=FEATURE, cwd=tmp_path)
    assert block is not None
    assert block.get("status") == "blocked"
    assert block.get("reason_code") == "workspace_admission_missing"


def test_check_branch_alias_passes_after_admit(tmp_path: Path) -> None:
    """TC-WS-090: check-branch delegates to workspace admit for v1.6.2."""
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    payload = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ],
        cwd=tmp_path,
    )
    assert payload.get("status") == "pass", payload


def test_qa_run_blocked_without_artifact(tmp_path: Path) -> None:
    """TC-WS-011: qa surface fail-closed without admission artifact."""
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    block = gate_workspace_admission_or_block(tmp_path, version=VERSION, feature=FEATURE, cwd=tmp_path)
    assert block is not None
    assert block.get("status") == "blocked"
    assert block.get("reason_code") == "workspace_admission_missing"

def test_branch_preflight_honors_workspace_admission_when_primary_branch_differs(tmp_path: Path) -> None:
    """Primary repo may stay on pre-main when agent cwd is the admitted feature worktree."""
    import importlib

    from tests.test_v162_workspace_admit import _git

    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    assert admit.get("status") == "pass"
    worktree = Path(str(admit.get("worktree_path")))
    assert worktree.is_dir()
    assert _git(["git", "branch", "--show-current"], cwd=tmp_path) == "pre-main"

    import os

    implement_cmd = importlib.import_module("beacon.commands.implement.commands")
    previous = os.getcwd()
    os.chdir(worktree)
    try:
        preflight = implement_cmd._run_branch_preflight(
            project_root=tmp_path,
            version=VERSION,
            run_id="run-test",
            feature=FEATURE,
            auto_switch_branch=False,
            require_clean_worktree_for_switch=True,
        )
    finally:
        os.chdir(previous)

    assert preflight.get("status") == "pass", preflight
    assert preflight.get("blocked") is False
    assert preflight.get("workspace_admission_branch_guard") is True
    assert preflight.get("expected_branch") == f"beacon/{VERSION}/{FEATURE}"



def test_governance_preflight_skips_metadata_branch_when_admission_valid(tmp_path: Path) -> None:
    import os

    from beacon.utils.truth_map import evaluate_implement_version_governance_preflight

    from tests.test_v162_workspace_admit import _git

    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(str(admit.get("worktree_path")))
    previous = os.getcwd()
    os.chdir(worktree)
    try:
        preflight = evaluate_implement_version_governance_preflight(
            tmp_path,
            version=VERSION,
            feature=FEATURE,
        )
    finally:
        os.chdir(previous)
    assert preflight.get("reason_code") != "implement_metadata_branch_mismatch", preflight
    assert _git(["git", "branch", "--show-current"], cwd=tmp_path) == "pre-main"
