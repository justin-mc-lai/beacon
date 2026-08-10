"""v1.1.0 report consistency + KPI contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.v110_baseline import generate_spec_fingerprint, record_baseline_snapshot

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    (root / "docs" / "beacon" / "v1.1.0" / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "prd").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "user-story" / "feature.md").write_text("# US\n", encoding="utf-8")
    (root / "docs" / "beacon" / "v1.1.0" / "prd" / "feature.md").write_text("# PRD\n", encoding="utf-8")
    (root / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "unit",
                        "evidence_path": ".beacon/evidence/auto-test/{run_id}/unit/result.json",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _seed_debug_feedback_assets(root: Path) -> None:
    debug_dir = root / ".beacon" / "state" / "debug-feedback"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "run-debug-001.jsonl").write_text(
        json.dumps(
            {
                "ts": "2026-03-07T00:00:00Z",
                "run_id": "run-debug-001",
                "source": "prompt.optimize",
                "goal": "请生成用户故事",
                "intent": "user-story",
                "confidence": 0.52,
                "boundary_state": "in_scope",
                "block_reason": "low-confidence",
                "recommended_command": "beacon user-story create ...",
                "executed": False,
                "exit_code": None,
                "note": "debug",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # Generate candidate + apply report through commands to keep payload realistic.
    extract = _invoke([
        "feedback",
        "extract",
        "run-debug-001",
        "--source",
        "debug",
        "--project-root",
        str(root),
    ])
    assert extract.exit_code == 0
    apply = _invoke([
        "feedback",
        "apply",
        "run-debug-001",
        "--project-root",
        str(root),
    ])
    assert apply.exit_code == 0


def test_report_write_summary_should_include_consistency_snapshot(tmp_path: Path):
    _seed_docs(tmp_path)
    fp = generate_spec_fingerprint(tmp_path, run_id="run-fp-001", version="v1.1.0")
    record_baseline_snapshot(
        tmp_path,
        run_id="run-baseline-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="completed",
    )

    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "spec_fingerprint_hash": fp.get("fingerprint_hash"),
                "execution": {
                    "run_id": "run-auto-001",
                    "layers": [],
                    "spec_fingerprint": {"fingerprint_hash": fp.get("fingerprint_hash")},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _invoke([
        "report",
        "--machine",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--write-summary",
        "latest",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    snapshot = payload.get("consistency_snapshot", {})
    assert snapshot.get("status") == "pass"
    assert snapshot.get("expected_spec_fingerprint") == fp.get("fingerprint_hash")
    assert snapshot.get("actual_spec_fingerprint") == fp.get("fingerprint_hash")

    summary_md = tmp_path / "docs" / "beacon" / "v1.1.0" / "execution" / "summary.md"
    assert summary_md.exists()
    summary_text = summary_md.read_text(encoding="utf-8")
    assert "Consistency Snapshot" in summary_text


def test_report_should_include_baseline_drift_and_memory_kpi(tmp_path: Path):
    _seed_docs(tmp_path)
    fp = generate_spec_fingerprint(tmp_path, run_id="run-fp-002", version="v1.1.0")
    record_baseline_snapshot(
        tmp_path,
        run_id="run-baseline-002",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="running",
    )

    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "failed",
                "execution": {
                    "run_id": "run-auto-002",
                    "layers": [],
                    "spec_fingerprint": {"fingerprint_hash": fp.get("fingerprint_hash")},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    _seed_debug_feedback_assets(tmp_path)

    result = _invoke([
        "report",
        "--machine",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "latest",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    memory_governance = payload.get("memory_governance", {})
    assert memory_governance.get("raw_debug_files", 0) >= 1
    assert memory_governance.get("candidate_files", 0) >= 1
    assert memory_governance.get("apply_reports", 0) >= 1

    baseline_drift = payload.get("baseline_drift", {})
    assert baseline_drift.get("has_baseline") is True
    assert baseline_drift.get("baseline_id")
