from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from beacon.adapters import agent_browser_runner, browser_use_runner
from beacon.main import app
from beacon.utils.browser_task_compiler import build_browser_task, write_browser_task


runner = CliRunner()
VERSION = "v1.1.9"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_state(root: Path) -> None:
    (root / ".beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION).mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "evo" / "scorecards").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "evo" / "experiments").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "qa" / "features" / "browser-story-feature").mkdir(parents=True, exist_ok=True)

    (root / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": VERSION, "run_id": "run-release-001", "issues": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (root / ".beacon" / "qa" / "status.json").write_text(
        json.dumps(
            {
                "feature": "Browser Story Feature",
                "feature_slug": "browser-story-feature",
                "version": VERSION,
                "status": "passed",
                "evidence_done": True,
                "execution_mode": "story-exhaustive",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "qa" / "features" / "browser-story-feature" / "exhaustiveness-report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": "Browser Story Feature",
                "feature_slug": "browser-story-feature",
                "run_id": "run-release-001",
                "generated_at": "2026-03-28T00:00:00+00:00",
                "status": "passed",
                "score": 0.95,
                "threshold": 0.8,
                "missing_axes": [],
                "missing_replay_scenarios": [],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "qa" / "features" / "browser-story-feature" / "scorecard.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": "Browser Story Feature",
                "feature_slug": "browser-story-feature",
                "run_id": "run-release-001",
                "release_confidence_min": 0.95,
                "release_confidence_avg": 0.97,
                "review_required_count": 0,
                "needs_replay_count": 0,
                "continue_decision": "ready_for_release",
                "test_case_backfill_required": False,
                "unresolved_closure_outcomes": [],
                "release_ready": True,
                "coverage_current": {"required_scenarios": 7, "executed_scenarios": 7, "coverage_rate": 1.0},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "evo" / "scorecards" / "latest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generated_at": "2026-03-28T00:00:00+00:00",
                "main_kpi": "false_complete_rate",
                "counts": {"keep": 2, "review": 1, "discard": 0},
                "candidates": [{"candidate_id": "c1"}, {"candidate_id": "c2"}, {"candidate_id": "c3"}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "evo" / "experiments" / "latest.json").write_text(
        json.dumps(
            {
                "run_id": "run-exp-001",
                "main_kpi_score": 88,
                "score_delta": {"main_kpi_score": 5, "false_complete_rate": -0.1},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_pass_script(root: Path, name: str) -> Path:
    script = root / name
    script.write_text("#!/bin/sh\nset -eu\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    return script


def test_v119_release_scorecard_should_render_json_payload(tmp_path: Path):
    _seed_release_state(tmp_path)

    result = _invoke(["release", "scorecard", VERSION, "--project", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["release_ready"] is True
    assert payload["gate"]["status"] == "Pass"
    assert payload["qa"]["execution_mode"] == "story-exhaustive"
    assert payload["exhaustiveness"]["score"] == 0.95
    assert payload["learning_scorecard"]["decision_summary"]["keep"] == 2
    assert payload["latest_experiment"]["main_kpi_score"] == 88


def test_v119_release_scorecard_should_not_reuse_cross_version_qa_status(tmp_path: Path):
    _seed_release_state(tmp_path)

    result = _invoke(["release", "scorecard", "v9.9.9", "--project", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == "v9.9.9"
    assert payload["release_ready"] is False
    assert payload["qa"]["feature"] == ""
    assert payload["qa"]["status"] == "unknown"
    assert payload["qa"]["version_match"] is False


def test_v119_browser_task_compiler_and_runners_should_accept_compiled_task(tmp_path: Path):
    tc_dir = tmp_path / "evidence" / "tc"
    fallback = _write_pass_script(tmp_path, "fallback.sh")
    layer_dir = tc_dir / "explore"
    layer_dir.mkdir(parents=True, exist_ok=True)
    task = build_browser_task(
        item={
            "feature": "Browser Story Feature",
            "ac_id": "AC-001",
            "tc_id": "TC-001-HAPPY",
            "source_tc_id": "TC-001",
            "scenario_id": "SC-001",
            "scenario_family": "happy",
            "assertion": "用户登录成功并进入 dashboard",
            "exploratory_runner": "agent-browser",
            "deterministic_runner": "playwright",
            "replay_required": True,
        },
        qa_type="functional",
        mode="functional",
        project_root=tmp_path,
    )
    task_path = write_browser_task(tc_dir=tc_dir, payload=task)
    assert task_path.exists()
    assert "dashboard" in task["instruction"]

    original_layer_dir = os.environ.get("BEACON_LAYER_DIR")
    os.environ["BEACON_LAYER_DIR"] = str(layer_dir)
    try:
        agent_code = agent_browser_runner.main(
            [
                "--mode",
                "functional",
                "--task-file",
                str(task_path),
                "--fallback-cmd",
                f"sh {fallback}",
                "--project-root",
                str(tmp_path),
            ]
        )
        browser_use_code = browser_use_runner.main(
            [
                "--mode",
                "functional",
                "--task-file",
                str(task_path),
                "--fallback-cmd",
                f"sh {fallback}",
                "--project-root",
                str(tmp_path),
            ]
        )
    finally:
        if original_layer_dir is None:
            os.environ.pop("BEACON_LAYER_DIR", None)
        else:
            os.environ["BEACON_LAYER_DIR"] = original_layer_dir
    assert agent_code == 0
    assert browser_use_code == 0
    report = json.loads((layer_dir / "browser-runner-report.json").read_text(encoding="utf-8"))
    assert report["target_url"] == "/"
    assert report["artifact_refs"]["task_ref"]
    assert (layer_dir / "action-transcript.json").exists()


def test_v119_browser_runners_should_tolerate_project_root_realpath_alias(tmp_path: Path):
    tc_dir = tmp_path / "evidence" / "tc"
    fallback = _write_pass_script(tmp_path, "fallback-alias.sh")
    layer_dir = tc_dir / "explore"
    layer_dir.mkdir(parents=True, exist_ok=True)
    task = build_browser_task(
        item={
            "feature": "Browser Story Feature",
            "ac_id": "AC-001",
            "tc_id": "TC-001-HAPPY",
            "source_tc_id": "TC-001",
            "scenario_id": "SC-001",
            "scenario_family": "happy",
            "assertion": "用户登录成功并进入 dashboard",
            "exploratory_runner": "agent-browser",
            "deterministic_runner": "playwright",
            "replay_required": False,
        },
        qa_type="functional",
        mode="functional",
        project_root=tmp_path.resolve(),
    )
    task_path = write_browser_task(tc_dir=tc_dir, payload=task)
    original_layer_dir = os.environ.get("BEACON_LAYER_DIR")
    os.environ["BEACON_LAYER_DIR"] = str(layer_dir)
    try:
        code = agent_browser_runner.main(
            [
                "--mode",
                "functional",
                "--task-file",
                str(task_path),
                "--fallback-cmd",
                f"sh {fallback}",
                "--project-root",
                str(tmp_path.resolve()),
            ]
        )
    finally:
        if original_layer_dir is None:
            os.environ.pop("BEACON_LAYER_DIR", None)
        else:
            os.environ["BEACON_LAYER_DIR"] = original_layer_dir
    assert code == 0
    report = json.loads((layer_dir / "browser-runner-report.json").read_text(encoding="utf-8"))
    assert report["artifact_refs"]["task_ref"].endswith("browser-runner-task.json")


def test_v119_release_scorecard_should_surface_in_report_and_status_main_views(tmp_path: Path):
    _seed_release_state(tmp_path)

    report = _invoke(["report", "--human", "--project-root", str(tmp_path), "latest"])
    assert report.exit_code == 0, report.stdout
    assert "## Release Readiness" in report.stdout
    assert "- Release Ready: `True`" in report.stdout
    assert "- QA Mode: `story-exhaustive`" in report.stdout

    status = _invoke(["status", "--project-root", str(tmp_path), "--version", VERSION, "--board"])
    assert status.exit_code == 0, status.stdout
    assert "- release.ready: True" in status.stdout
    assert "- release.qa: passed (story-exhaustive, evidence_done=True)" in status.stdout
    assert "- release.learning: false_complete_rate=88 keep/review/discard=2/1/0" in status.stdout
