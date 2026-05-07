"""Git workflow contract for implement command."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.git_alignment import (
    build_implement_branch_guard_payload,
    switch_to_expected_branch,
)
from beacon.utils.implementation_plan import (
    ensure_implementation_git_workflow_contract,
    load_or_seed_implementation_git_workflow_contract,
)


def get_git_commit(project_root: Path) -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def run_branch_preflight(
    project_root: Path,
    *,
    feature: str,
    version: str,
    auto_switch_branch: bool,
    expected_branch: str = "",
    branch_prefix: str = "beacon/",
) -> tuple[bool, dict[str, Any]]:
    """Run branch preflight checks."""
    # Load or seed git workflow contract
    workflow_contract = load_or_seed_implementation_git_workflow_contract(
        project_root,
        feature=feature,
        version=version,
    )

    # Build branch guard payload
    guard_payload = build_implement_branch_guard_payload(
        project_root,
        version=version,
        expected_branch=expected_branch or f"{branch_prefix}{version}",
    )

    # Check if branch switch is needed
    current_branch = guard_payload.get("current_branch", "")
    expected = guard_payload.get("expected_branch", "")

    if current_branch != expected:
        if auto_switch_branch:
            # Switch to expected branch
            switch_result = switch_to_expected_branch(
                project_root,
                expected_branch=expected,
            )

            if not switch_result.get("success", False):
                return False, {
                    "error": "branch_switch_failed",
                    "current_branch": current_branch,
                    "expected_branch": expected,
                    "switch_result": switch_result,
                }
        else:
            return False, {
                "error": "branch_mismatch",
                "current_branch": current_branch,
                "expected_branch": expected,
            }

    # Ensure git workflow contract
    ensure_implementation_git_workflow_contract(
        project_root,
        feature=feature,
        version=version,
    )

    return True, {
        "success": True,
        "current_branch": current_branch,
        "expected_branch": expected,
        "workflow_contract": workflow_contract,
    }


def validate_git_workflow(
    project_root: Path,
    *,
    feature: str,
    version: str,
) -> tuple[bool, str]:
    """Validate git workflow contract."""
    workflow_contract = load_or_seed_implementation_git_workflow_contract(
        project_root,
        feature=feature,
        version=version,
    )

    if not workflow_contract:
        return False, "Git workflow contract not found"

    # Check if implementation plan is required
    plan_required = workflow_contract.get("implementation_plan_required", False)

    if plan_required:
        # Check if plan exists
        from beacon.utils.implementation_plan import implementation_plan_supported

        if not implementation_plan_supported(project_root, feature=feature, version=version):
            return False, "Implementation plan required but not found"

    return True, "Git workflow contract valid"
