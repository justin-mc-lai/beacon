"""v1.0.3 feedback extract/apply contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_run(project_root: Path, run_id: str) -> None:
    run_dir = project_root / ".beacon" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "state.json").write_text(
        json.dumps({"run_id": run_id, "status": "blocked", "reason": "verify_failed"}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_feedback_extract_should_collect_reason_codes(tmp_path: Path):
    run_id = "run-feedback-001"
    _prepare_run(tmp_path, run_id)
    gate_report = tmp_path / ".beacon" / "gate-report.json"
    gate_report.parent.mkdir(parents=True, exist_ok=True)
    gate_report.write_text(
        json.dumps(
            {
                "status": "Blocked",
                "issues": [
                    {"reason_code": "verify_not_passed"},
                    {"reason_code": "evidence_manifest_missing"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _invoke(["feedback", "extract", run_id, "--source", "gate", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    codes = {row.get("reason_code") for row in payload.get("feedback", [])}
    assert "verify_not_passed" in codes
    assert "evidence_manifest_missing" in codes

    out = tmp_path / ".beacon" / "state" / "feedback-candidates" / f"{run_id}.json"
    assert out.exists()


def test_feedback_apply_should_write_feedback_memory_and_report(tmp_path: Path):
    run_id = "run-feedback-002"
    _prepare_run(tmp_path, run_id)
    candidates_dir = tmp_path / ".beacon" / "state" / "feedback-candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = candidates_dir / f"{run_id}.json"
    candidate_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "feedback": [
                    {"reason_code": "verify_not_passed", "note": "Need stable verify evidence"},
                    {"reason_code": "scope_guard_violation", "note": "Scope guard not acknowledged"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _invoke(["feedback", "apply", run_id, "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert int(report.get("applied_count", 0)) >= 2

    apply_report = tmp_path / ".beacon" / "state" / "feedback-apply-report" / f"{run_id}.json"
    assert apply_report.exists()

    memory_v1 = tmp_path / ".beacon" / "memory" / "memory-v1.json"
    assert memory_v1.exists()
    rows = json.loads(memory_v1.read_text(encoding="utf-8")).get("items", [])
    feedback_rows = [row for row in rows if row.get("type") == "feedback" and row.get("source") == "feedback.apply"]
    assert feedback_rows
    all_codes = {code for row in feedback_rows for code in (row.get("reason_codes") or [])}
    assert {"verify_not_passed", "scope_guard_violation"} <= all_codes
