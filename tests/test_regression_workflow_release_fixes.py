"""Regression tests for workflow/gate/release fixes."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import append_lifecycle_event, compute_workflow_progress


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_artifacts(project_root: Path, *, version: str, run_id: str) -> None:
    beacon_dir = project_root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "version": version,
                "run_id": run_id,
                "execution": {"run_id": run_id, "version": version},
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps(
            {
                "stage": "release",
                "mode": "strict",
                "status": "Pass",
                "issues": [],
                "version": version,
                "run_id": run_id,
                "coverage": {"full_coverage": True},
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": run_id,
                "entries": [{"path": ".beacon/auto-test-status.json", "sha256": "x"}],
            }
        ),
        encoding="utf-8",
    )


def test_run_workflow_strict_flag_should_enable_effective_strict_mode(tmp_path: Path):
    result = _invoke(
        [
            "run",
            "workflow",
            "--strict",
            "--feature",
            "demo",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "missing_user_story_for_strict_mode"


def test_workflow_run_should_auto_route_think_start_and_parse_options(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "run",
            "think",
            "Demo Feature",
            "--project",
            str(tmp_path),
            "--options",
            '{"qa_profile":"web-core"}',
        ]
    )
    assert result.exit_code == 0
    think_progress_dir = tmp_path / ".beacon" / "state" / "think-progress"
    files = sorted(think_progress_dir.glob("*.json"))
    assert files
    payload = json.loads(files[-1].read_text(encoding="utf-8"))
    assert payload.get("topic") == "Demo Feature"
    assert payload.get("qa_profile") == "web-core"


def test_gate_should_fallback_when_gate_config_json_is_malformed(tmp_path: Path):
    config_path = tmp_path / ".beacon" / "gate-config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{invalid json", encoding="utf-8")

    result = _invoke(
        [
            "gate",
            "check",
            "think",
            "--mode",
            "normal",
            "--json",
            "--project-root",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0
    assert "Traceback" not in result.stdout


def test_release_create_should_use_resolved_version_in_file_content(tmp_path: Path):
    (tmp_path / "docs" / "beacon" / "v2.0.0").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.0.0").mkdir(parents=True, exist_ok=True)

    result = _invoke(["release", "create", "latest", "--project", str(tmp_path)])
    assert result.exit_code == 0

    out = tmp_path / "docs" / "beacon" / "v2.0.0" / "release" / "v2.0.0.md"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "# Release Checklist: v2.0.0" in text
    assert "**Version**: v2.0.0" in text
    assert "latest" not in text


def test_release_check_should_fail_when_artifacts_version_mismatch(tmp_path: Path):
    _seed_release_artifacts(tmp_path, version="v1.2.3", run_id="run-20260306T000000000000")

    mismatch = _invoke(["release", "check", "v9.9.9", "--project", str(tmp_path)])
    assert mismatch.exit_code == 1
    assert "expected=v9.9.9" in mismatch.stdout

    matched = _invoke(["release", "check", "v1.2.3", "--project", str(tmp_path)])
    assert matched.exit_code == 0


def test_compute_workflow_progress_should_not_read_gate_pass_from_other_run(tmp_path: Path):
    run_a = "run-aaa"
    run_b = "run-bbb"
    save_run_state(tmp_path, run_a, {"run_id": run_a, "workflow": "workflow.start", "feature": "A", "version": "v1.0.0"})
    save_run_state(tmp_path, run_b, {"run_id": run_b, "workflow": "workflow.start", "feature": "B", "version": "v1.0.0"})

    for event in ("stage_started", "stage_context_injected", "stage_finished", "memory_writeback"):
        append_lifecycle_event(tmp_path, run_id=run_a, stage="gate", event=event, source="test")

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "run_id": run_a, "version": "v1.0.0"}),
        encoding="utf-8",
    )

    progress_b = compute_workflow_progress(tmp_path, run_id=run_b)
    assert progress_b.get("gate_pass") is False
    assert progress_b.get("gate_status") == "unknown"
