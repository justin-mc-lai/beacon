from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard


runner = CliRunner()
VERSION = "v1.4.7"
FEATURE = "beacon-v1.4.7-release-report-ceo-axes"
SLUG = "beacon-v1.4.7-release-report-ceo-axes"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/release/{VERSION}.md", "# release\n")
    _write(root, f"docs/beacon/{VERSION}/prd/{SLUG}.md", "# prd\n")
    _write(root, f"docs/beacon/{VERSION}/user-story/{SLUG}.md", "# story\n")
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", "# test\n")


def test_v147_release_scorecard_summary_should_surface_ceo_review_axes(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    review_result = runner.invoke(
        app,
        ["review", "ceo", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--decision", "reframe"],
    )
    assert review_result.exit_code == 0, review_result.stdout

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)

    assert scorecard["ceo_review"]["challenge_axis_codes"] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]
    assert summary["ceo_review_status"] == "accepted_for_writeback"
    assert summary["ceo_review_decision"] == "reframe"
    assert summary["ceo_review_challenge_axis_codes"] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]
    assert summary["ceo_challenge_gap_status"] == "pass"
    assert summary["ceo_challenge_missing_axes"] == []
    assert summary["ceo_challenge_needs_challenge"] is False
    assert summary["ceo_challenge_promotion_status"] == "pass"
    assert summary["ceo_challenge_promotion_decision"] == "challenge_coverage_current"
    assert summary["ceo_challenge_recommended_action"] == "none"


def test_v147_release_scorecard_summary_should_surface_ceo_challenge_gap_when_review_missing(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)

    assert summary["ceo_review_status"] == ""
    assert summary["ceo_challenge_gap_status"] == "warn"
    assert summary["ceo_challenge_needs_challenge"] is True
    assert summary["ceo_challenge_reason_code"] == "ceo_challenge_gap"
    assert summary["ceo_challenge_promotion_status"] == "warn"
    assert summary["ceo_challenge_promotion_decision"] == "challenge_refresh_recommended"
    assert summary["ceo_challenge_recommended_action"] == "rerun_ceo_review"
    assert summary["ceo_challenge_missing_axes"] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]


def test_v147_report_should_surface_ceo_review_axes_in_machine_and_human_views(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    review_result = runner.invoke(
        app,
        ["review", "ceo", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--decision", "reframe"],
    )
    assert review_result.exit_code == 0, review_result.stdout

    machine_result = runner.invoke(
        app,
        ["report", "--machine", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "latest"],
    )
    assert machine_result.exit_code == 0, machine_result.stdout
    machine_payload = json.loads(machine_result.stdout)
    release_summary = machine_payload["release_summary"]
    assert release_summary["ceo_review_challenge_axis_codes"] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]

    human_result = runner.invoke(
        app,
        ["report", "--human", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "latest"],
    )
    assert human_result.exit_code == 0, human_result.stdout
    assert "## CEO Challenge Coverage" in human_result.stdout
    assert "ceo_review_challenge_axes" in human_result.stdout
    assert "truth_freeze_destabilization" in human_result.stdout
    assert "ceo_challenge_promotion_decision" in human_result.stdout
