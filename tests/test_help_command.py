from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_workflow_run(project_root: Path, *, version: str = "v1.1.5", feature: str = "My Feature") -> str:
    result = _invoke(["workflow", "start", feature, "--project", str(project_root), "--version", version])
    assert result.exit_code == 0, result.stdout
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def test_help_json_without_run_should_recommend_freeze_before_implementation(tmp_path: Path):
    result = _invoke(["help", "--json", "--project-root", str(tmp_path), "--version", "v1.1.5", "--feature", "My Feature"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["next_step"]["action"] == "freeze"
    assert "beacon freeze" in payload["next_step"]["command"]
    assert isinstance(payload.get("scores"), dict)


def test_help_json_with_planned_workflow_should_recommend_freeze_until_revision_is_frozen(tmp_path: Path):
    run_id = _seed_workflow_run(tmp_path)
    result = _invoke(["help", "--json", "--project-root", str(tmp_path), "--version", "v1.1.5", "--feature", "My Feature", "--run-id", run_id])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["run_id"] == run_id
    assert payload["next_step"]["action"] == "freeze"
    assert "beacon freeze" in payload["next_step"]["command"]
    assert payload["current_stage"] == "prd"


def test_help_human_output_should_include_scores_and_next_step(tmp_path: Path):
    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.1.5", "--feature", "My Feature"])
    assert result.exit_code == 0, result.stdout
    assert "Beacon Help / Next Step" in result.stdout
    assert "test_score" in result.stdout
    assert "command :" in result.stdout


def test_help_should_surface_ceo_review_challenge_axes(tmp_path: Path):
    version = "v1.4.7"
    feature = "beacon-v1.4.7-help-surface-ceo-review-axes"
    slug = "beacon-v1.4.7-help-surface-ceo-review-axes"
    for rel in (
        "docs/beacon/global-boundaries.md",
        f"docs/beacon/{version}/SUMMARY.md",
        f"docs/beacon/{version}/execution/index.md",
        f"docs/beacon/{version}/execution/architecture-blueprint.md",
        f"docs/beacon/{version}/prd/{slug}.md",
        f"docs/beacon/{version}/user-story/{slug}.md",
        f"docs/beacon/{version}/qa/test-cases/{slug}.md",
    ):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# seeded\n", encoding="utf-8")

    review_result = _invoke(["review", "ceo", feature, "--project", str(tmp_path), "--version", version, "--decision", "reframe"])
    assert review_result.exit_code == 0, review_result.stdout

    json_result = _invoke(["help", "--json", "--project-root", str(tmp_path), "--version", version, "--feature", feature])
    assert json_result.exit_code == 0, json_result.stdout
    payload = json.loads(json_result.stdout)
    ceo_review = payload["support_reviews"]["ceo_review"]
    assert ceo_review["challenge_axis_codes"] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]

    human_result = _invoke(["help", "--project-root", str(tmp_path), "--version", version, "--feature", feature])
    assert human_result.exit_code == 0, human_result.stdout
    assert "axes=too_smooth_path,buried_landmine,truth_freeze_destabilization,stage_boundary_sprawl,false_closure_signal,operator_cost_underpricing" in human_result.stdout
