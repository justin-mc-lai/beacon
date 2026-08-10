from __future__ import annotations

import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon import __toolkit_version__, __version__
from beacon.main import app
from beacon.utils.delivery_baseline import validate_projection_against_baseline
from beacon.utils.runtime import save_run_state
from beacon.utils.technical_review_contract import (
    materialize_technical_review_contract,
    validate_technical_review_contract,
)
from beacon.utils.workflow_memory import append_lifecycle_event, resolve_workflow_run_id


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()
gate_module = importlib.import_module("beacon.commands.gate")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_v120_version_truth_should_promote_v120_to_current_runtime_release():
    payload = json.loads((ROOT / "beacon" / "version-truth.json").read_text(encoding="utf-8"))
    assert payload["package_version"] == __version__
    assert payload["runtime_version"] == __toolkit_version__
    assert payload["docs_default_line"] == __toolkit_version__
    assert payload["current_runtime_release_line"] == __toolkit_version__
    assert __toolkit_version__ not in payload["planning_lines"]
    assert "v1.3.5" in payload["planning_lines"]
    for line in payload["planning_lines"]:
        assert payload["lines"][line]["status"] == "planning_only"
    assert "v1.3.4" in payload["partial_runtime_supplement_lines"]
    assert payload["lines"]["v1.3.4"]["status"] == "planning_with_partial_runtime_supplement"
    assert payload["lines"][__toolkit_version__]["status"] == "current_runtime_release"


def test_v120_workflow_run_resolution_should_fallback_for_release_feature_title(tmp_path: Path):
    run_id = "run-20260408T055114Z-1866"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "Beacon v1.2.0 - Command Simplification and Project-Skill Workflow Enhancement",
            "version": "v1.2.0",
            "status": "paused",
            "started_at": "2026-04-08T05:51:14.841049+00:00",
        },
    )

    resolved = resolve_workflow_run_id(
        tmp_path,
        version="v1.2.0",
        feature="beacon-v1.2.0-command-simplification-and-project-skill-workflow",
    )
    assert resolved == run_id


def test_v120_workflow_run_resolution_should_fallback_to_lifecycle_feature_details(tmp_path: Path):
    run_id = "run-20260421T081540Z-ad12"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "登录功能",
            "version": "v1.3.6",
            "prototype_enabled": True,
            "status": "planned",
            "started_at": "2026-04-21T08:15:40.860649+00:00",
        },
    )
    append_lifecycle_event(
        tmp_path,
        run_id=run_id,
        stage="think",
        event="stage_started",
        evidence_ref=["docs/beacon/v1.3.6/SUMMARY.md"],
        details={
            "feature": "beacon-v1.3.6-visual-management-console-and-material-viewer",
            "version": "v1.3.6",
        },
    )

    resolved = resolve_workflow_run_id(
        tmp_path,
        version="v1.3.6",
        feature="beacon-v1.3.6-visual-management-console-and-material-viewer",
    )
    assert resolved == run_id


def test_v120_workflow_run_resolution_should_include_repair_run_prefix(tmp_path: Path):
    run_id = "repair-v1.4.0-20260506T185413433584Z0000"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
            "version": "v1.4.0",
            "status": "completed",
            "started_at": "2026-05-06T18:54:13Z",
            "ended_at": "2026-05-06T18:54:14Z",
        },
    )

    resolved = resolve_workflow_run_id(
        tmp_path,
        version="v1.4.0",
        feature="beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    )
    assert resolved == run_id


def test_v120_technical_review_contract_should_backfill_reviewed_at_when_approved(tmp_path: Path):
    feature = "beacon-v1.3.6-visual-management-console-and-material-viewer"
    payload = materialize_technical_review_contract(
        tmp_path,
        version="v1.3.6",
        feature=feature,
        revision_id="R1",
        contract_overrides={
            "review_status": "approved",
            "approved_by": "codex",
            "reviewed_at": "",
        },
    )

    assert str(payload.get("reviewed_at") or "").strip()
    validation = validate_technical_review_contract(
        payload,
        version="v1.3.6",
        feature=feature,
        revision_id="R1",
    )
    assert validation["valid"] is True


def test_v120_current_release_gate_should_pass():
    result = _invoke(["gate", "check", "release", "--project-root", str(ROOT), "--version", __toolkit_version__, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "Pass"
    assert payload["blocked_count"] == 0


def test_v120_release_gate_should_ignore_runtime_projection_context_warn(monkeypatch, tmp_path: Path):
    version = "v1.3.8"
    monkeypatch.setattr(gate_module, "resolve_target_version", lambda *_args, **_kwargs: version)
    monkeypatch.setattr(
        gate_module,
        "runtime_projection_transaction_contract",
        lambda **_kwargs: {
            "status": "warn",
            "blocked": False,
            "reason_code": "runtime_projection_transaction_context_missing",
            "message": "runtime projection transaction for current context is missing; rebuild runtime ledger for this docs/feature context",
            "details": {"projection_seq": "ps-1"},
        },
    )

    release_issues = gate_module.check_runtime_projection_transaction_contract(
        tmp_path,
        gate_module.GateMode.STRICT,
        "release",
        version,
    )
    prototype_issues = gate_module.check_runtime_projection_transaction_contract(
        tmp_path,
        gate_module.GateMode.STRICT,
        "prototype",
        version,
    )

    assert release_issues == []
    assert len(prototype_issues) == 1
    assert prototype_issues[0]["reason_code"] == "runtime_projection_drift"
    assert prototype_issues[0]["blocked"] is False


def test_v120_projection_validation_should_treat_relative_and_absolute_worktree_root_as_same_path(tmp_path: Path):
    envelope = {
        "baseline_id": "baseline-1",
        "transaction_id": "tx-1",
        "source_hash": "sha256:abc",
        "projection_seq": 1,
        "base_branch": "main",
        "branch_prefix": "beacon/",
        "default_target_branch": "beacon/v1.3.8",
        "use_git_worktree": False,
        "worktree_root": ".",
        "direct_delivery_services": ["."],
        "writable_services": ["."],
        "reference_only_services": ["docs"],
    }
    projection = {
        "baseline_id": "baseline-1",
        "transaction_id": "tx-1",
        "source_hash": "sha256:abc",
        "projection_seq": 1,
        "base_branch": "main",
        "branch_prefix": "beacon/",
        "target_branch": "beacon/v1.3.8",
        "use_git_worktree": False,
        "worktree_root": str(tmp_path.resolve()),
        "direct_delivery_services": ["."],
        "writable_services": ["."],
        "reference_only_services": ["docs"],
    }

    issues = validate_projection_against_baseline(
        projection,
        envelope,
        projection_name="technical_review_contract",
        project_root=tmp_path,
    )

    assert issues == []
