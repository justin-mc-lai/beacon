from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.cli_factory import build_app
from beacon.utils.project_hooks import (
    build_lifecycle_hook_advisory,
    discover_hooks_for_boundary,
    run_hook,
)


VERSION = "v1.4.10"
FEATURE = "lifecycle-boundary-hook-advisory-and-confirmed-execution"


def _write_post_release_hook(root: Path) -> None:
    path = root / "docs" / "beacon" / "hooks" / "beacon-post-release-local-install.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """---
hook_id: beacon-post-release-local-install
hook_code: post_release
project: beacon
enabled: true
trigger_policy: manual_confirmed
skill: beacon-project-hooks
command_template: "beacon hooks run beacon-post-release-local-install --project . --version {version} --feature {feature} --hook-code post_release --confirm"
produces_evidence:
  - local_installation_status
  - global_beacon_cli_version
failure_route: release
---

# Beacon Post Release Local Install

## Purpose

Advise the operator to install and verify local Beacon surfaces after release.

## Admission

- Release readiness has passed.
- Operator confirms the side-effect action.

## Evidence

- Local installation status.
- CLI version output.

## Failure Route

Return to release follow-up repair.
""",
        encoding="utf-8",
    )


def _write_release_artifacts(root: Path) -> None:
    (root / ".beacon").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "version": VERSION, "run_id": "run-release"}),
        encoding="utf-8",
    )
    (root / ".beacon" / "release-gate-report.json").write_text(
        json.dumps({"status": "pass", "stage": "release", "version": VERSION, "run_id": "run-release"}),
        encoding="utf-8",
    )
    (root / ".beacon" / "evidence-manifest.json").write_text(
        json.dumps({"version": VERSION, "run_id": "run-release", "entries": [{"path": "evidence.txt"}]}),
        encoding="utf-8",
    )
    (root / ".beacon" / "coverage-summary.json").write_text(
        json.dumps({"version": VERSION, "run_id": "run-release", "coverage_rate": 1.0}),
        encoding="utf-8",
    )


def _scorecard() -> dict:
    return {
        "release_ready": True,
        "gate": {"status": "pass", "run_id": "run-release", "artifact_version": VERSION},
        "qa": {"feature": FEATURE, "release_ready": True, "status": "passed"},
        "feature_qa_scorecard": {
            "release_ready": True,
            "continue_decision": "ready_for_release",
            "coverage_current": {"required_scenarios": 1, "executed_scenarios": 1, "coverage_rate": 1.0},
        },
        "change_documents": {
            "markdown_exists": True,
            "json_exists": True,
            "version_match": True,
            "includes_current_feature": True,
            "markdown_path": "docs/beacon/v1.4.10/change/v1.4.10.md",
            "json_path": "docs/beacon/v1.4.10/.machine/change/v1.4.10.json",
            "feature_count": 1,
            "current_feature_slug": FEATURE,
        },
        "semantic": {"status": "pass", "reason_code": ""},
        "ceo_challenge_coverage": {"needs_challenge": False, "status": "pass", "missing_axes": [], "decision": "not_required"},
        "version_surface_governance": {"configured": False},
        "prompt_boundary": {"status": "pass", "blocked": False, "reason_code": "", "classification": "", "surface": ""},
        "acceptance": {"feature": FEATURE},
    }


def test_discover_post_release_hooks(tmp_path: Path) -> None:
    _write_post_release_hook(tmp_path)

    payload = discover_hooks_for_boundary(tmp_path, "post_release", feature=FEATURE)

    assert payload["status"] == "ready"
    assert payload["hook_count"] == 1
    assert payload["hooks"][0]["hook_id"] == "beacon-post-release-local-install"
    assert payload["truth_authority"] is False
    assert payload["runtime_evidence_only"] is True


def test_advisory_plan_has_no_side_effect(tmp_path: Path) -> None:
    _write_post_release_hook(tmp_path)

    payload = build_lifecycle_hook_advisory(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        hook_code="post_release",
        boundary_stage="release",
    )

    assert payload["status"] == "ready"
    assert payload["side_effect_executed"] is False
    hook = payload["hooks"][0]
    assert hook["plan_status"] == "planned"
    assert hook["dry_run"]["attempted"] is True
    assert hook["dry_run"]["side_effect_executed"] is False
    assert "--dry-run" in hook["dry_run_command"]
    assert "--confirm" in hook["recommended_command"]


def test_hook_advisory_has_no_truth_authority(tmp_path: Path) -> None:
    _write_post_release_hook(tmp_path)

    before_release_ready = True
    payload = build_lifecycle_hook_advisory(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        hook_code="post_release",
        boundary_stage="release",
    )
    after_release_ready = before_release_ready

    assert payload["truth_authority"] is False
    assert payload["runtime_evidence_only"] is True
    assert payload["support_evidence_only"] is True
    assert payload["verdict_authority"] == "none"
    assert before_release_ready is after_release_ready


def test_release_check_surfaces_post_release_advisory(tmp_path: Path, monkeypatch) -> None:
    _write_post_release_hook(tmp_path)
    _write_release_artifacts(tmp_path)
    monkeypatch.setattr("beacon.commands.release.build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr("beacon.commands.release.build_release_scorecard", lambda *_args, **_kwargs: _scorecard())
    monkeypatch.setattr("beacon.commands.release.project_release_feature_enabled", lambda *_args, **_kwargs: False)
    monkeypatch.setattr("beacon.commands.release.project_runtime_feature_enabled", lambda *_args, **_kwargs: False)

    result = CliRunner().invoke(
        build_app(package_version="0-test"),
        ["release", "check", VERSION, "--project", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "pass"
    assert payload["release_ready"] is True
    advisory = payload["lifecycle_hook_advisory"]
    assert advisory["status"] == "ready"
    assert advisory["support_evidence_only"] is True
    assert advisory["hooks"][0]["side_effect_executed"] is False
    assert "beacon hooks run beacon-post-release-local-install" in advisory["recommended_command"]
    assert "--confirm" in advisory["recommended_command"]


def test_help_status_can_project_hook_advisory(tmp_path: Path, monkeypatch) -> None:
    _write_post_release_hook(tmp_path)
    monkeypatch.chdir(tmp_path)
    status_module = importlib.import_module("beacon.commands.status")
    monkeypatch.setattr("beacon.utils.help_support.build_release_scorecard", lambda *_args, **_kwargs: _scorecard())
    monkeypatch.setattr(status_module, "build_release_scorecard", lambda *_args, **_kwargs: _scorecard())

    app = build_app(package_version="0-test")
    help_result = CliRunner().invoke(
        app,
        ["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"],
    )
    status_result = CliRunner().invoke(
        app,
        ["status", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE],
    )

    assert help_result.exit_code == 0, help_result.output
    help_payload = json.loads(help_result.output)
    assert help_payload["lifecycle_hook_advisory"]["hook_count"] == 1
    assert help_payload["lifecycle"]["current_stage"] != "hook"
    assert status_result.exit_code == 0, status_result.output
    status_payload = json.loads(status_result.output)
    assert status_payload["lifecycle_hook_advisory"]["hook_count"] == 1
    assert status_payload["lifecycle_hook_advisory"]["hook_code"] == "post_release"
    assert "support_evidence_only" not in help_payload["lifecycle"]


def test_manual_confirmed_hook_without_confirm_remains_blocked(tmp_path: Path) -> None:
    _write_post_release_hook(tmp_path)

    payload = run_hook(tmp_path, "beacon-post-release-local-install", version=VERSION, feature=FEATURE, hook_code="post_release")

    assert payload["blocked"] is True
    assert payload["reason_code"] == "manual_confirmation_required"
    assert payload["side_effect_executed"] is False
