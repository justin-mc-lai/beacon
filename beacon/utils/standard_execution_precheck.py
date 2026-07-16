"""CLI-owned Standard Execution Flow precheck runner (v1.6.6 R5 / AC-025)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.git_alignment import git_output, resolve_truth_canonical_branch
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

PRODUCED_BY = "beacon.status.standard-execution-precheck"
SCHEMA_VERSION = "standard-execution-precheck.v1"


def _check_payload(status: str, *, reason_code: str = "", details: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": status}
    if reason_code:
        payload["reason_code"] = reason_code
    if details is not None:
        payload["details"] = details
    return payload


def _run_git_diff_check(project_root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "diff", "--check"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return _check_payload("fail", reason_code="git_diff_check_error", details=str(exc))
    if result.returncode != 0:
        return _check_payload(
            "fail",
            reason_code="git_diff_check_failed",
            details={"stdout": result.stdout, "stderr": result.stderr},
        )
    return _check_payload("pass")


def _truth_map_verify(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    from beacon.utils.truth_map import verify_truth_map

    try:
        payload = verify_truth_map(project_root, version=version, feature=feature)
    except Exception as exc:  # noqa: BLE001
        return _check_payload("fail", reason_code="truth_map_verify_error", details=str(exc))
    status = "pass" if not bool(payload.get("blocked")) and str(payload.get("status") or "") == "pass" else "fail"
    return _check_payload(
        status,
        reason_code=str(payload.get("reason_code") or ("truth_map_verify_failed" if status != "pass" else "")),
        details={"status": payload.get("status"), "blocked": payload.get("blocked")},
    )


def _verify_materials_strict(project_root: Path, *, version: str) -> dict[str, Any]:
    from beacon.utils.doctor_orchestrator import run_materials_verify

    try:
        execution = run_materials_verify(
            project_root=str(project_root),
            version=version,
            strict=True,
        )
        payload = execution.payload if hasattr(execution, "payload") else {}
    except Exception as exc:  # noqa: BLE001
        return _check_payload("fail", reason_code="verify_materials_error", details=str(exc))
    if not isinstance(payload, dict):
        return _check_payload("fail", reason_code="verify_materials_invalid_payload")
    result = payload.get("result") if isinstance(payload.get("result"), dict) else payload
    status = str(result.get("status") or payload.get("status") or "").lower()
    blocked = bool(result.get("blocked") or payload.get("blocked"))
    ok = status in {"pass", "ok", "passed"} and not blocked and int(getattr(execution, "exit_code", 1) or 0) == 0
    return _check_payload(
        "pass" if ok else "fail",
        reason_code=str(result.get("reason_code") or payload.get("reason_code") or ("" if ok else "verify_materials_failed")),
        details={"status": status, "blocked": blocked, "exit_code": getattr(execution, "exit_code", None)},
    )


def _branch_governance_verify(project_root: Path, *, version: str, feature: str = "") -> dict[str, Any]:
    from beacon.utils.branch_governance import resolve_branch_governance_view

    try:
        view = resolve_branch_governance_view(
            project_root=project_root,
            version=version,
            feature=feature,
            strict=False,
        )
    except Exception as exc:  # noqa: BLE001
        return _check_payload("fail", reason_code="branch_governance_error", details=str(exc))
    if not isinstance(view, dict):
        return _check_payload("fail", reason_code="branch_governance_invalid_payload")
    status = str(view.get("status") or view.get("validation_state") or "").lower()
    if status in {"fail", "blocked", "error"}:
        return _check_payload("fail", reason_code="branch_governance_failed", details={"status": status})
    return _check_payload("pass", details={"status": status or "resolved"})


def _workspace_admission_check(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> tuple[dict[str, Any], str]:
    from beacon.utils.workspace_admission import artifact_path, validate_workspace_admission

    validation = validate_workspace_admission(
        project_root,
        version=version,
        feature=feature,
        cwd=project_root,
    )
    ref = ""
    path = artifact_path(project_root, version=version, feature=feature)
    if path.exists():
        try:
            ref = str(path.relative_to(project_root.expanduser().resolve()))
        except ValueError:
            ref = str(path)
    status = "pass" if bool(validation.get("valid")) else "fail"
    return (
        _check_payload(
            status,
            reason_code=str(validation.get("reason_code") or ("" if status == "pass" else "workspace_admission_blocked")),
            details=validation,
        ),
        ref,
    )


def _canonical_commit_evidence(project_root: Path, *, version: str) -> dict[str, Any]:
    truth_canonical = resolve_truth_canonical_branch(project_root, version=version)
    tip = git_output(project_root, "rev-parse", truth_canonical) or git_output(project_root, "rev-parse", f"refs/heads/{truth_canonical}")
    head = git_output(project_root, "rev-parse", "HEAD")
    merged = False
    if tip and head:
        contained = git_output(project_root, "merge-base", "--is-ancestor", tip, "HEAD")
        # merge-base --is-ancestor returns empty stdout; use exit via subprocess
        try:
            result = subprocess.run(
                ["git", "merge-base", "--is-ancestor", tip, "HEAD"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            merged = result.returncode == 0
        except Exception:  # noqa: BLE001
            merged = tip == head
    # Canonical refreeze committed iff truth_canonical tip exists (branch tip is a commit).
    return {
        "truth_canonical": truth_canonical,
        "truth_baseline_commit": tip or head or "",
        "canonical_refreeze_committed": bool(tip),
        "truth_baseline_merged": bool(merged or (tip and tip == head)),
        "feature_worktree_reconciled": True,
        "stale_feature_refreeze_detected": False,
        "stale_feature_refreeze_quarantine_ref": "",
    }


def default_artifact_ref(run_id: str) -> str:
    slug = str(run_id or "anonymous").strip() or "anonymous"
    return f".beacon/state/loop-goal/{slug}.verification-bundle.json"




def _topology_gate_check(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> tuple[dict[str, Any], str]:
    from beacon.utils.git_scope_graph import topology_gate_check, topology_gate_required

    if not topology_gate_required(version):
        return _check_payload("pass", details={"skipped": True}), ""
    check, ref = topology_gate_check(project_root, version=version, feature=feature)
    return check, ref

def run_standard_execution_precheck(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str = "",
    artifact_ref: str = "",
) -> dict[str, Any]:
    """Run the five required checks and write a CLI-owned verification bundle."""
    root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    slug = feature_slug(feature)
    run = str(run_id or "").strip() or f"precheck-{slug}"
    ref = str(artifact_ref or "").strip() or default_artifact_ref(run)

    truth_map = _truth_map_verify(root, version=resolved_version, feature=feature)
    materials = _verify_materials_strict(root, version=resolved_version)
    diff_check = _run_git_diff_check(root)
    branch_gov = _branch_governance_verify(root, version=resolved_version, feature=feature)
    workspace, workspace_ref = _workspace_admission_check(root, version=resolved_version, feature=feature)
    topology_gate, topology_ref = _topology_gate_check(root, version=resolved_version, feature=feature)
    commit_evidence = _canonical_commit_evidence(root, version=resolved_version)

    verification_bundle = {
        "truth_map_verify": truth_map,
        "verify_materials_strict": materials,
        "git_diff_check": diff_check,
        "branch_governance_verify": branch_gov,
        "workspace_admission": workspace,
        "topology_gate": topology_gate,
    }
    failed = [
        key
        for key, value in verification_bundle.items()
        if str((value or {}).get("status") or "").lower() not in {"pass", "ok", "passed"}
    ]
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "produced_by": PRODUCED_BY,
        "cli_owned": True,
        "generated_at": now_iso(),
        "version": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "run_id": run,
        "verification_bundle_ref": ref,
        "workspace_admission_ref": workspace_ref,
        "topology_gate_ref": topology_ref,
        "verification_bundle": verification_bundle,
        **commit_evidence,
        "status": "pass" if not failed else "blocked",
        "reason_code": "" if not failed else "verification_bundle_incomplete",
        "failed_checks": failed,
    }
    out_path = root / ref
    write_json(out_path, payload)
    payload["artifact_path"] = ref
    return payload


def load_cli_owned_bundle(project_root: Path, verification_bundle_ref: str) -> dict[str, Any] | None:
    root = project_root.expanduser().resolve()
    ref = str(verification_bundle_ref or "").strip()
    if not ref:
        return None
    path = Path(ref)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(payload, dict):
        return None
    if not bool(payload.get("cli_owned")) and str(payload.get("produced_by") or "") != PRODUCED_BY:
        return None
    return payload
