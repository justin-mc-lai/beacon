from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon import __toolkit_version__, __version__
from beacon.main import app
from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import resolve_workflow_run_id


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_v120_version_truth_should_promote_v120_to_current_runtime_release():
    payload = json.loads((ROOT / "beacon" / "version-truth.json").read_text(encoding="utf-8"))
    assert payload["package_version"] == __version__
    assert payload["runtime_version"] == __toolkit_version__
    assert payload["docs_default_line"] == __toolkit_version__
    assert payload["current_runtime_release_line"] == __toolkit_version__
    assert payload["planning_lines"] == []
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


def test_v120_current_release_gate_should_pass():
    result = _invoke(["gate", "check", "release", "--project-root", str(ROOT), "--version", __toolkit_version__, "--json"])
    assert result.exit_code in {0, 2}, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] in {"Pass", "Blocked"}
    if payload["status"] == "Pass":
        assert payload["blocked_count"] == 0
    else:
        reason_codes = {item["reason_code"] for item in payload.get("issues", []) if isinstance(item, dict)}
        assert reason_codes <= {
            "ac_tc_evidence_chain_broken",
            "git_alignment_blocked",
            "git_workflow_contract_missing",
            "evidence_sha256_manifest_mismatch",
            "gate_consistency_conflict",
            "implementation_plan_blocked",
            "implementation_plan_incomplete",
            "unresolved_closure_outcome",
            "review_required_open",
            "release_confidence_below_threshold",
            "feature_release_not_ready",
            "spec_impl_drift_detected",
        }
