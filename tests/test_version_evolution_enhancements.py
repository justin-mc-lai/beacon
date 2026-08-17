from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.workflow_memory import append_lifecycle_event


runner = CliRunner()


def test_version_create_with_bump_should_write_dual_docs_and_metadata(tmp_path: Path):
    # Establish an existing baseline version.
    (tmp_path / "docs" / "beacon" / "v1.0.1").mkdir(parents=True, exist_ok=True)

    result = runner.invoke(
        app,
        [
            "version",
            "create",
            "Search Upgrade",
            "--project",
            str(tmp_path),
            "--base-version",
            "v1.0.1",
            "--bump",
            "minor",
        ],
    )
    assert result.exit_code == 0

    slug = "search-upgrade"
    assert (tmp_path / "docs" / "beacon" / "v1.1.0" / "version" / f"{slug}.md").exists()
    assert not (tmp_path / "docs" / "product" / "v1.1.0" / "version" / f"{slug}.md").exists()

    meta_path = tmp_path / ".beacon" / "state" / "version-plans" / "v1.1.0" / f"{slug}.json"
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    assert payload["target_version"] == "v1.1.0"
    assert payload["base_version"] == "v1.0.1"
    assert payload["strategy"] == "bump:minor"


def test_evolution_summary_should_use_real_artifacts_not_tbd(tmp_path: Path):
    # previous/current stories
    prev_us = tmp_path / "docs" / "beacon" / "v1.0.0" / "user-story"
    curr_us = tmp_path / "docs" / "beacon" / "v1.0.1" / "user-story"
    curr_tc = tmp_path / "docs" / "beacon" / "v1.0.1" / "qa" / "test-cases"
    prev_us.mkdir(parents=True, exist_ok=True)
    curr_us.mkdir(parents=True, exist_ok=True)
    curr_tc.mkdir(parents=True, exist_ok=True)
    (prev_us / "legacy-login.md").write_text("# Legacy Login\n", encoding="utf-8")
    (curr_us / "new-login.md").write_text("# New Login\n", encoding="utf-8")

    # implementation marker + matrix evidence
    state_dir = tmp_path / ".beacon" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "implementation-new-login.json").write_text("{}", encoding="utf-8")
    evidence_file = tmp_path / ".beacon" / "evidence" / "cases" / "TC-001.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text('{"status":"passed"}', encoding="utf-8")
    matrix = {
        "entries": [
            {
                "ac_id": "AC-001",
                "tc_id": "TC-001",
                "layer": "unit",
                "command": "python3 -m pytest -q",
                "assertion": "returncode==0",
                "evidence_path": str(evidence_file.relative_to(tmp_path)),
            }
        ]
    }
    (curr_tc / "new-login.ac-test-matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # run state + release event
    run_state_path = tmp_path / ".beacon" / "runs" / "run-20260303T000000-aa" / "state.json"
    run_state_path.parent.mkdir(parents=True, exist_ok=True)
    run_state_path.write_text(
        json.dumps(
            {
                "run_id": "run-20260303T000000-aa",
                "workflow": "workflow.start",
                "feature": "New Login",
                "version": "v1.0.1",
                "status": "completed",
                "started_at": "2026-03-03T00:00:00Z",
                "ended_at": "2026-03-03T00:05:00Z",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    append_lifecycle_event(
        tmp_path,
        run_id="release:v1.0.1",
        stage="release",
        event="release_decision_recorded",
        source="workflow.release-profile",
        details={"version": "v1.0.1", "status": "completed", "reason": "ok"},
    )

    result = runner.invoke(
        app,
        ["evolution-summary", "create", "v1.0.1", "--project", str(tmp_path), "--previous", "v1.0.0"],
    )
    assert result.exit_code == 0

    summary_text = (tmp_path / "docs" / "beacon" / "v1.0.1" / "SUMMARY.md").read_text(encoding="utf-8")
    assert "TBD" not in summary_text
    assert "当前故事总数" in summary_text
    assert "运行闭环状态" in summary_text

    state_json = tmp_path / ".beacon" / "state" / "evolution-summary" / "v1.0.1.json"
    payload = json.loads(state_json.read_text(encoding="utf-8"))
    assert payload["coverage"]["current"]["implemented_story"] >= 1
    assert payload["coverage"]["current"]["executed_tc"] >= 1
