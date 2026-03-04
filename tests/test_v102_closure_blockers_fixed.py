"""Regression tests for v1.0.2 closure blockers."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


PASS_WITH_JUNIT_AND_ASSERT = (
    "python3 -c \"import os,pathlib; "
    "p=pathlib.Path(os.environ.get('BEACON_JUNIT_PATH','.beacon/junit.xml')); "
    "p.parent.mkdir(parents=True,exist_ok=True); "
    "p.write_text('<testsuite tests=\\\"1\\\" failures=\\\"0\\\"></testsuite>', encoding='utf-8'); "
    "print('BEACON_ASSERTIONS=1')\""
)


def _write_matrix(tmp_path: Path, *, qa_types: list[str], entries: list[dict], compatibility_required_pairs: list[dict] | None = None) -> Path:
    matrix_path = tmp_path / "docs" / "product" / "v1.0.2" / "qa" / "test-cases" / "closure.qa9-matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0.2",
        "feature": "closure",
        "feature_slug": "closure",
        "version": "v1.0.2",
        "qa_profile": "web-full",
        "qa_types": qa_types,
        "llm_plan": {
            "mode": "rule",
            "model": "beacon-rule-llm-v1",
            "project_scan": {"language": "python", "framework": "pytest", "frontend": "web", "api_spec_refs": [], "risk_points": []},
        },
        "qa_requirements": [
            {
                "qa_type": qa_type,
                "required": True,
                "automation_required": True,
                "min_cases": 1,
                "applicability": "required",
                "waiver": {},
            }
            for qa_type in qa_types
        ],
        "entries": entries,
        "compatibility_matrix": {
            "browsers": ["chromium"],
            "devices": ["desktop"],
            "required_pairs": compatibility_required_pairs or [{"browser": "chromium", "device": "desktop"}],
        },
    }
    matrix_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return matrix_path


def test_junit_path_contract_should_pass_when_command_writes_beacon_junit(tmp_path: Path):
    matrix_path = _write_matrix(
        tmp_path,
        qa_types=["unit"],
        entries=[
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "qa_type": "unit",
                "automation": "auto",
                "command": PASS_WITH_JUNIT_AND_ASSERT,
                "assertion": "unit assertion",
                "evidence_path": ".beacon/evidence/test-results/closure/{run_id}/TC-001.json",
                "status": "pending",
            }
        ],
    )

    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--qa-matrix-path",
            str(matrix_path),
            "--require-junit",
            "--require-assertion-count",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload.get("quality_issues", []) == []


def test_assertion_count_should_not_accept_plain_print_passed(tmp_path: Path):
    matrix_path = _write_matrix(
        tmp_path,
        qa_types=["unit"],
        entries=[
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "qa_type": "unit",
                "automation": "auto",
                "command": "python3 -c \"print('1 passed')\"",
                "assertion": "unit assertion",
                "evidence_path": ".beacon/evidence/test-results/closure/{run_id}/TC-001.json",
                "status": "pending",
            }
        ],
    )

    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--qa-matrix-path",
            str(matrix_path),
            "--require-assertion-count",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    codes = {str(item.get("reason_code")) for item in payload.get("quality_issues", []) if isinstance(item, dict)}
    assert payload["status"] == "failed"
    assert "assertion_count_zero_pass" in codes


def test_compatibility_should_require_real_pair_evidence(tmp_path: Path):
    matrix_path = _write_matrix(
        tmp_path,
        qa_types=["compatibility"],
        entries=[
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "qa_type": "compatibility",
                "automation": "auto",
                "command": PASS_WITH_JUNIT_AND_ASSERT,
                "assertion": "compat assertion",
                "evidence_path": ".beacon/evidence/test-results/closure/{run_id}/TC-001.json",
                "status": "pending",
            }
        ],
        compatibility_required_pairs=[{"browser": "chromium", "device": "desktop"}],
    )

    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--qa-matrix-path",
            str(matrix_path),
            "--require-junit",
            "--require-assertion-count",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    codes = {str(item.get("reason_code")) for item in payload.get("quality_issues", []) if isinstance(item, dict)}
    executed_pairs = payload.get("qa9", {}).get("compatibility", {}).get("executed_pairs", [])
    assert payload["status"] == "failed"
    assert executed_pairs == []
    assert "compatibility_execution_missing" in codes


def test_tc_backfill_should_use_tc_level_execution_not_only_layer_rollup(tmp_path: Path):
    matrix_path = _write_matrix(
        tmp_path,
        qa_types=["unit"],
        entries=[
            {
                "tc_id": "TC-001",
                "ac_id": "AC-001",
                "qa_type": "unit",
                "automation": "auto",
                "command": PASS_WITH_JUNIT_AND_ASSERT,
                "assertion": "unit assertion 1",
                "evidence_path": ".beacon/evidence/test-results/closure/{run_id}/TC-001.json",
                "status": "pending",
            },
            {
                "tc_id": "TC-002",
                "ac_id": "AC-002",
                "qa_type": "unit",
                "automation": "auto",
                "command": "python3 -c \"import sys; sys.exit(1)\"",
                "assertion": "unit assertion 2",
                "evidence_path": ".beacon/evidence/test-results/closure/{run_id}/TC-002.json",
                "status": "pending",
            },
        ],
    )

    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "qa9",
            "--project",
            str(tmp_path),
            "--qa-matrix-path",
            str(matrix_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    tc_results = payload.get("qa9", {}).get("tc_results", [])
    summary = payload.get("qa9", {}).get("summary", {})
    status_by_tc = {str(item.get("tc_id")): str(item.get("status")) for item in tc_results if isinstance(item, dict)}
    assert status_by_tc.get("TC-001") == "passed"
    assert status_by_tc.get("TC-002") == "failed"
    assert int(summary.get("failed", 0) or 0) == 1
    assert payload.get("status") == "failed"

