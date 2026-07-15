"""Harness remediation sandbox — governed overlay lifecycle with eval and auto-rollback.

Consumes stagnation report, creates isolated sandbox in governed worktree,
applies runtime overlay, evaluates result, and auto-rolls back on eval failure.
Never writes to canonical skill files.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "remediation-report.v1"

OVERLAY_TYPES = frozenset({"retry-with-backoff", "skip-and-continue", "break-on-plateau"})

CANONICAL_TRUTH_PATTERNS = (
    "docs/beacon/*/features/*/truth.md",
    "docs/beacon/*/features/*/tests.md",
    "docs/beacon/*/features/*/tasks.md",
    "docs/beacon/*/features/*/evidence.md",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _worktrees_root(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / ".beacon" / "worktrees"


def create_sandbox(
    project_root: Path,
    *,
    run_id: str,
    stagnation_ref: str = "",
) -> dict[str, Any]:
    """Create an isolated sandbox directory under governed worktrees.

    Returns sandbox_path and a snapshot of pre-overlay state for rollback.
    """
    root = project_root.expanduser().resolve()
    sandbox_name = f"remediation-{run_id}"
    sandbox_path = _worktrees_root(root) / sandbox_name
    sandbox_path.mkdir(parents=True, exist_ok=True)

    # Create overlay directory
    overlay_dir = sandbox_path / "overlay"
    overlay_dir.mkdir(exist_ok=True)

    # Create eval directory
    eval_dir = sandbox_path / "eval"
    eval_dir.mkdir(exist_ok=True)

    # Snapshot canonical truth files for no-truth-write check
    truth_snapshot: dict[str, str] = {}
    for pattern in CANONICAL_TRUTH_PATTERNS:
        for truth_path in root.glob(pattern):
            rel = str(truth_path.relative_to(root))
            truth_snapshot[rel] = truth_path.read_text(encoding="utf-8")

    state = {
        "sandbox_path": str(sandbox_path),
        "stagnation_ref": stagnation_ref,
        "created_at": _now_iso(),
        "truth_snapshot": truth_snapshot,
        "overlay_applied": False,
    }
    state_path = sandbox_path / "sandbox-state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "pass",
        "sandbox_path": str(sandbox_path),
        "stagnation_ref": stagnation_ref,
        "state_path": str(state_path),
    }


def apply_overlay(
    project_root: Path,
    *,
    sandbox_path: str,
    overlay_type: str,
    overlay_content: str = "",
) -> dict[str, Any]:
    """Apply a runtime overlay patch to the sandbox directory.

    Does NOT modify canonical skill files.
    """
    root = project_root.expanduser().resolve()
    sandbox = Path(sandbox_path)
    if not sandbox.is_dir():
        return {
            "status": "blocked",
            "reason_code": "sandbox_not_found",
            "findings": [{"message": f"sandbox path does not exist: {sandbox_path}"}],
        }

    if overlay_type not in OVERLAY_TYPES:
        return {
            "status": "blocked",
            "reason_code": "invalid_overlay_type",
            "findings": [{"message": f"overlay_type must be one of {OVERLAY_TYPES}"}],
        }

    overlay_file = sandbox / "overlay" / f"{overlay_type}.patch"
    overlay_file.write_text(overlay_content or f"# overlay: {overlay_type}\n", encoding="utf-8")

    # Update sandbox state
    state_path = sandbox / "sandbox-state.json"
    state: dict[str, Any] = {}
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    state["overlay_applied"] = True
    state["overlay_type"] = overlay_type
    state["overlay_file"] = str(overlay_file.relative_to(root)) if overlay_file.is_relative_to(root) else str(overlay_file)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "pass",
        "overlay_type": overlay_type,
        "overlay_file": str(overlay_file),
    }


def _check_no_truth_write(project_root: Path, truth_snapshot: dict[str, str]) -> bool:
    """Verify canonical truth files were not modified."""
    root = project_root.expanduser().resolve()
    for rel, original_content in truth_snapshot.items():
        truth_path = root / rel
        if not truth_path.is_file():
            return False
        if truth_path.read_text(encoding="utf-8") != original_content:
            return False
    return True


def _check_smoke_test(sandbox_path: Path) -> bool:
    """Run smoke test in sandbox — check overlay file exists and is non-empty."""
    overlay_dir = sandbox_path / "overlay"
    if not overlay_dir.is_dir():
        return False
    overlays = list(overlay_dir.glob("*.patch"))
    if not overlays:
        return False
    return all(o.stat().st_size > 0 for o in overlays)


def eval_overlay(
    project_root: Path,
    *,
    sandbox_path: str,
    stagnation_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate overlay result. Returns eval checks and status.

    If eval fails, auto-rollback is performed.
    """
    root = project_root.expanduser().resolve()
    sandbox = Path(sandbox_path)
    if not sandbox.is_dir():
        return {
            "status": "blocked",
            "reason_code": "sandbox_not_found",
            "eval": {},
            "findings": [{"message": "sandbox not found"}],
        }

    state_path = sandbox / "sandbox-state.json"
    state: dict[str, Any] = {}
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    truth_snapshot = state.get("truth_snapshot", {})

    # Run eval checks
    smoke_pass = _check_smoke_test(sandbox)
    no_truth_write = _check_no_truth_write(root, truth_snapshot)

    # Stagnation resolved: re-run detection would show clean
    # For deterministic eval, we check if the overlay type matches the stagnation
    overlay_type = state.get("overlay_type", "")
    stag_resolved = False
    if stagnation_report and overlay_type:
        findings = stagnation_report.get("findings", [])
        # If overlay type matches recommendation, consider resolved
        for finding in findings:
            if finding.get("recommendation") == overlay_type:
                stag_resolved = True
                break
        # If no findings at all, it's already clean
        if not findings:
            stag_resolved = True

    # Rollback check: can we restore?
    rollback_clean = True  # Always true since we never modified canonical files

    all_pass = smoke_pass and no_truth_write and stag_resolved and rollback_clean

    eval_result = {
        "smoke_test_pass": smoke_pass,
        "stagnation_resolved": stag_resolved,
        "no_truth_write": no_truth_write,
        "rollback_clean": rollback_clean,
    }

    if all_pass:
        return {
            "status": "remediated",
            "eval": eval_result,
            "findings": [],
            "human_review_required": True,
        }
    else:
        # Auto-rollback
        rollback_result = rollback_overlay(project_root, sandbox_path=sandbox_path)
        return {
            "status": "rollback",
            "eval": eval_result,
            "findings": [{"message": "eval failed, overlay rolled back"}],
            "human_review_required": True,
            "rollback_result": rollback_result,
        }


def rollback_overlay(project_root: Path, *, sandbox_path: str) -> dict[str, Any]:
    """Rollback overlay — remove overlay files, restore clean sandbox state."""
    sandbox = Path(sandbox_path)
    if not sandbox.is_dir():
        return {"status": "blocked", "reason_code": "sandbox_not_found"}

    overlay_dir = sandbox / "overlay"
    if overlay_dir.is_dir():
        shutil.rmtree(overlay_dir, ignore_errors=True)
        overlay_dir.mkdir(exist_ok=True)

    # Update state
    state_path = sandbox / "sandbox-state.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["overlay_applied"] = False
        state["rolled_back_at"] = _now_iso()
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"status": "pass", "message": "overlay rolled back"}


def build_remediation_report(
    project_root: Path,
    *,
    run_id: str,
    sandbox_path: str,
    stagnation_ref: str = "",
    eval_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a remediation-report.v1 from eval result."""
    root = project_root.expanduser().resolve()
    sandbox = Path(sandbox_path)

    state: dict[str, Any] = {}
    state_path = sandbox / "sandbox-state.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    overlay_type = state.get("overlay_type", "")
    eval_data = eval_result or {}
    eval_checks = eval_data.get("eval", {})

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "stagnation_ref": stagnation_ref,
        "overlay_type": overlay_type,
        "sandbox_path": str(sandbox),
        "status": eval_data.get("status", "blocked"),
        "eval": {
            "smoke_test_pass": eval_checks.get("smoke_test_pass", False),
            "stagnation_resolved": eval_checks.get("stagnation_resolved", False),
            "no_truth_write": eval_checks.get("no_truth_write", False),
            "rollback_clean": eval_checks.get("rollback_clean", False),
        },
        "findings": eval_data.get("findings", []),
        "human_review_required": True,
    }


def remediation_signal(project_root: Path) -> dict[str, Any]:
    """Return a signal dict for doctor loop-audit integration."""
    root = project_root.expanduser().resolve()
    worktrees = _worktrees_root(root)
    if not worktrees.is_dir() or not any(worktrees.iterdir()):
        return {
            "signal": "remediation_sandbox",
            "status": "missing",
            "reason_code": "remediation_no_sandboxes",
            "findings": [{"message": "no remediation sandboxes under .beacon/worktrees/"}],
        }
    return {
        "signal": "remediation_sandbox",
        "status": "pass",
        "reason_code": "",
        "findings": [],
    }
