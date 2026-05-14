"""v1.3.3 Ralph resume state refresh contracts."""

from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.ralph_runtime import finalize_ralph_state


runner = CliRunner()
implement_module = importlib.import_module("beacon.commands.implement")


def _write_ralph_state(tmp_path: Path, feature: str, payload: dict) -> Path:
    slug = "-".join(feature.strip().lower().split())
    path = tmp_path / ".beacon" / "ralph" / f"{slug}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_ralph_resume_should_promote_review_quality_gate_ready_to_release(monkeypatch, tmp_path: Path):
    feature = "beacon-v1.3.3-minimal-hud-scenarios-and-implementation"
    state_path = _write_ralph_state(
        tmp_path,
        feature,
        {
            "schema_version": "1.1",
            "feature": feature,
            "feature_slug": feature,
            "version": "v1.3.3",
            "next_action": "review_quality",
            "recommended_command": f'beacon review quality "{feature}" --project . --version v1.3.3',
            "stop_state": "human_blocked",
            "current_blocker": "review_quality_blocked",
            "review_gate_ready": False,
        },
    )

    monkeypatch.setattr(
        implement_module._legacy_cli,
        "_run_beacon_json_command",
        lambda project_root, command: (0, {"status": "warn", "gate_ready": True}),
    )

    result = runner.invoke(
        app,
        ["implement", "ralph-resume", feature, "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"

    updated = _read_json(state_path)
    assert updated["review_gate_ready"] is True
    assert updated["next_action"] == "release"
    assert updated["current_blocker"] == "gate_release_pending"
    assert "beacon gate check release" in updated["recommended_command"]


def test_ralph_resume_should_mark_release_ready_after_gate_pass(monkeypatch, tmp_path: Path):
    feature = "beacon-v1.3.3-minimal-hud-scenarios-and-implementation"
    state_path = _write_ralph_state(
        tmp_path,
        feature,
        {
            "schema_version": "1.1",
            "feature": feature,
            "feature_slug": feature,
            "version": "v1.3.3",
            "next_action": "release",
            "recommended_command": "beacon gate check release --project-root . --version v1.3.3",
            "stop_state": "human_blocked",
            "current_blocker": "gate_release_pending",
            "gate_release_status": "",
        },
    )

    monkeypatch.setattr(
        implement_module._legacy_cli,
        "_run_beacon_json_command",
        lambda project_root, command: (0, {"status": "pass"}),
    )

    result = runner.invoke(
        app,
        ["implement", "ralph-resume", feature, "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"

    updated = _read_json(state_path)
    assert updated["gate_release_status"] == "pass"
    assert updated["stop_state"] == "release_ready"
    assert updated["current_blocker"] == ""
    assert updated["next_action"] == "release"


def test_ralph_resume_should_mark_gate_release_blocked_when_gate_fails(monkeypatch, tmp_path: Path):
    feature = "beacon-v1.3.3-minimal-hud-scenarios-and-implementation"
    state_path = _write_ralph_state(
        tmp_path,
        feature,
        {
            "schema_version": "1.1",
            "feature": feature,
            "feature_slug": feature,
            "version": "v1.3.3",
            "next_action": "release",
            "recommended_command": "beacon gate check release --project-root . --version v1.3.3",
            "stop_state": "human_blocked",
            "current_blocker": "gate_release_pending",
            "gate_release_status": "",
        },
    )

    monkeypatch.setattr(
        implement_module._legacy_cli,
        "_run_beacon_json_command",
        lambda project_root, command: (2, {"status": "Blocked"}),
    )

    result = runner.invoke(
        app,
        ["implement", "ralph-resume", feature, "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"

    updated = _read_json(state_path)
    assert updated["gate_release_status"] == "blocked"
    assert updated["stop_state"] == "human_blocked"
    assert updated["current_blocker"] == "gate_release_blocked"
    assert updated["next_action"] == "release"


def test_ralph_resume_should_redirect_to_human_requirement_handoff_when_release_is_blocked_by_completeness(monkeypatch, tmp_path: Path):
    feature = "beacon-v1.3.12-requirement-completeness-human-handoff"
    state_path = _write_ralph_state(
        tmp_path,
        feature,
        {
            "schema_version": "1.1",
            "feature": feature,
            "feature_slug": feature,
            "version": "v1.3.12",
            "next_action": "release",
            "recommended_command": "beacon gate check release --project-root . --version v1.3.12",
            "stop_state": "human_blocked",
            "current_blocker": "gate_release_pending",
            "gate_release_status": "",
        },
    )

    monkeypatch.setattr(
        implement_module._legacy_cli,
        "_run_beacon_json_command",
        lambda project_root, command: (
            2,
            {
                "status": "Blocked",
                "requirement_completeness": {
                    "status": "blocked",
                    "blocked": True,
                    "reason_code": "requirement_completeness_blocked",
                    "recommended_command": "beacon-change",
                    "human_loop_handoff": {
                        "action": "human_review",
                        "recommended_command": "beacon-change",
                    },
                },
            },
        ),
    )

    result = runner.invoke(
        app,
        ["implement", "ralph-resume", feature, "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"

    updated = _read_json(state_path)
    assert updated["gate_release_status"] == "blocked"
    assert updated["stop_state"] == "human_blocked"
    assert updated["current_blocker"] == "requirement_completeness_blocked"
    assert updated["next_action"] == "human_review"
    assert updated["recommended_command"] == "beacon-change"


def test_finalize_ralph_state_should_use_canonical_review_quality_payload(tmp_path: Path):
    feature = "beacon-v1.3.3-minimal-hud-scenarios-and-implementation"
    _write_ralph_state(
        tmp_path,
        feature,
        {
            "schema_version": "1.1",
            "feature": feature,
            "feature_slug": feature,
            "version": "v1.3.3",
            "failure_streak": 0,
            "no_delta_streak": 0,
            "rounds": [],
        },
    )
    canonical = tmp_path / "docs" / "beacon" / "v1.3.3" / ".machine" / "execution" / f"review-quality-{feature}.json"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(json.dumps({"gate_ready": True, "status": "pass"}, ensure_ascii=False, indent=2), encoding="utf-8")

    result = finalize_ralph_state(
        tmp_path,
        feature=feature,
        run_id="run-test",
        review_quality={"payload": {"gate_ready": False}, "paths": {"json": str(canonical.relative_to(tmp_path))}},
        auto_qa={"payload": {"feature_scorecard": {"continue_decision": "ready_for_release"}}, "max_rounds": 0},
        gate_release={"payload": {"status": "fail"}},
    )

    assert result["review_gate_ready"] is True
    assert result["next_action"] == "release"
    assert result["current_blocker"] == "gate_release_blocked"


def test_ralph_status_should_reconcile_stale_gate_release_blocker_to_deep_release_blocker(monkeypatch, tmp_path: Path):
    feature = "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance"
    state_path = _write_ralph_state(
        tmp_path,
        feature,
        {
            "schema_version": "1.1",
            "feature": feature,
            "feature_slug": feature,
            "version": "v1.4.6",
            "phase": "completed",
            "stop_state": "human_blocked",
            "current_blocker": "gate_release_blocked",
            "next_action": "release",
            "recommended_command": "beacon gate check release --project-root . --version v1.4.6",
        },
    )

    monkeypatch.setattr(
        implement_module._legacy_cli,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "gate": {"status": "Pass", "reason_codes": []},
            "deep_release_supplement": {
                "blocked": True,
                "reason_code": "deep_loop_unclosed",
                "recommended_command": f'beacon deep run "{feature}" --project-root {tmp_path} --version v1.4.6 --json',
            },
        },
    )

    result = runner.invoke(
        app,
        ["implement", "ralph-status", feature, "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["current_blocker"] == "deep_loop_unclosed"
    assert "beacon deep run" in payload["recommended_command"]

    updated = _read_json(state_path)
    assert updated["current_blocker"] == "deep_loop_unclosed"
    assert "beacon deep run" in updated["recommended_command"]
