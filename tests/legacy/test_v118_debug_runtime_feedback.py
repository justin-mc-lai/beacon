from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def test_debug_capture_should_write_canonical_debug_run_artifacts(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "debug",
            "capture",
            "Implement qa primary surface",
            "--project-root",
            str(tmp_path),
            "--run-id",
            "run-debug-v118",
            "--intent",
            "qa",
            "--confidence",
            "0.61",
            "--boundary-state",
            "in_scope",
            "--block-reason",
            "qa_primary_surface_missing",
            "--recommended-command",
            "beacon qa run qa9",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout

    legacy = tmp_path / ".beacon" / "state" / "debug-feedback" / "run-debug-v118.jsonl"
    canonical = tmp_path / ".beacon" / "debug" / "runs" / "run-debug-v118" / "events.jsonl"
    summary = tmp_path / ".beacon" / "debug" / "runs" / "run-debug-v118" / "summary.json"
    index = tmp_path / ".beacon" / "debug" / "index.json"

    assert legacy.exists()
    assert canonical.exists()
    assert summary.exists()
    assert index.exists()

    event = json.loads(canonical.read_text(encoding="utf-8").splitlines()[-1])
    assert event["feedback_target"] == "beacon-core"
    assert event["reason_code"] == "qa_primary_surface_missing"
    assert event["result"] in {"degraded", "succeeded-with-friction"}


def test_debug_harvest_and_export_ideas_should_generate_issue_files(tmp_path: Path):
    for idx in range(2):
        runner.invoke(
            app,
            [
                "debug",
                "capture",
                "Need browser session reuse",
                "--project-root",
                str(tmp_path),
                "--run-id",
                f"run-debug-{idx}",
                "--intent",
                "qa",
                "--confidence",
                "0.55",
                "--boundary-state",
                "in_scope",
                "--block-reason",
                "qa_session_persistence_missing",
                "--recommended-command",
                "beacon qa session save uat-admin",
            ],
        )

    harvest = runner.invoke(app, ["debug", "harvest", "--project-root", str(tmp_path), "--json"])
    assert harvest.exit_code == 0, harvest.stdout
    harvest_payload = json.loads(harvest.stdout)
    assert harvest_payload["issue_count"] >= 1

    ideas = runner.invoke(app, ["debug", "export-ideas", "--project-root", str(tmp_path), "--json"])
    assert ideas.exit_code == 0, ideas.stdout
    ideas_payload = json.loads(ideas.stdout)
    assert ideas_payload["idea_count"] >= 1

    issues_dir = tmp_path / ".beacon" / "debug" / "issues"
    ideas_dir = tmp_path / ".beacon" / "debug" / "ideas"
    assert any(path.suffix == ".json" for path in issues_dir.glob("*.json"))
    assert any(path.suffix == ".md" for path in ideas_dir.glob("*.md"))
