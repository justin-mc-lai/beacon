from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.0.0"
FEATURE = "miniapp-ui-visual-refresh"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_v147_status_board_should_hide_new_release_governance_noise_for_historical_docs_line(
    tmp_path: Path,
) -> None:
    docs_root = tmp_path / "docs" / "beacon" / VERSION
    (tmp_path / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs_root / "SUMMARY.md").parent.mkdir(parents=True, exist_ok=True)
    (docs_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (docs_root / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (docs_root / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / "change").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "change" / f"{VERSION}.json").write_text(
        json.dumps({"version": VERSION, "features": [{"feature_slug": FEATURE}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (docs_root / "change" / f"{VERSION}.md").write_text("# change\n", encoding="utf-8")
    _write_json(
        tmp_path / ".beacon" / "state" / "project-onboarding.json",
        {
            "schema_version": "1.0",
            "project_mode": "takeover",
            "docs_version": VERSION,
            "runtime_version": "v1.4.6",
            "qa_managed": False,
            "gate_managed": False,
            "runtime_capability_lines": ["v1.3.3", "v1.3.6", "v1.3.7", "v1.3.9", "v1.4.2", "v1.4.6"],
        },
    )
    _write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "version": VERSION,
            "status": "passed",
            "evidence_done": True,
            "execution_mode": "feature-aware",
            "release_ready": True,
            "project_profile_gate": {"status": "pass"},
        },
    )
    _write_json(
        tmp_path / ".beacon" / "qa" / "features" / FEATURE / "scorecard.json",
        {
            "feature": FEATURE,
            "feature_slug": FEATURE,
            "run_id": "run-qa-001",
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "unresolved_closure_outcomes": [],
            "project_profile_gate_status": "pass",
            "release_confidence_min": 1.0,
            "release_confidence_avg": 1.0,
            "review_required_count": 0,
            "needs_replay_count": 0,
            "coverage_current": {
                "required_scenarios": 76,
                "executed_scenarios": 76,
                "coverage_rate": 1.0,
            },
        },
    )
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"stage": "verify", "status": "Pass", "version": VERSION, "run_id": "run-qa-001", "issues": []},
    )
    _write_json(
        tmp_path / ".beacon" / "release-gate-report.json",
        {"stage": "release", "status": "Pass", "version": VERSION, "run_id": "run-qa-001", "issues": [], "blocked_count": 0},
    )
    _write_json(
        docs_root / ".machine" / "execution" / f"{FEATURE}.revision.json",
        {
            "feature": FEATURE,
            "version": VERSION,
            "revision_id": "R3",
            "source_revision_id": "R2",
            "doc_status": "frozen",
            "delivery_status": "accepted",
        },
    )
    _write_json(
        docs_root / ".machine" / "execution" / f"qa-acceptance-{FEATURE}.json",
        {
            "feature": FEATURE,
            "feature_slug": FEATURE,
            "version": VERSION,
            "verdict": "passed",
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "project_profile_gate_status": "pass",
            "unresolved_closure_outcomes": [],
        },
    )

    result = _invoke(
        [
            "status",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--board",
        ]
    )

    assert result.exit_code == 0, result.stdout
    assert "- release.ready: True" in result.stdout
    assert "- semantic:" not in result.stdout
    assert "- technical_review:" not in result.stdout
    assert "- release.exhaustiveness:" not in result.stdout
