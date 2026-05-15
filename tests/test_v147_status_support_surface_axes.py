from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.4.7"
FEATURE = "beacon-v1.4.7-status-surface-ceo-review-axes"
SLUG = "beacon-v1.4.7-status-surface-ceo-review-axes"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/prd/{SLUG}.md", "# prd\n")
    _write(root, f"docs/beacon/{VERSION}/user-story/{SLUG}.md", "# story\n")
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", "# test\n")


def test_v147_status_should_surface_ceo_review_challenge_axes_in_json_and_human_output(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    review_result = runner.invoke(
        app,
        ["review", "ceo", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--decision", "reframe"],
    )
    assert review_result.exit_code == 0, review_result.stdout

    status_result = runner.invoke(
        app,
        ["status", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE],
    )
    assert status_result.exit_code == 0, status_result.stdout
    payload = json.loads(status_result.stdout)
    assert payload["ceo_review"]["challenge_axis_codes"] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]

    board_result = runner.invoke(
        app,
        ["status", "--board", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE],
    )
    assert board_result.exit_code == 0, board_result.stdout
    assert "axes=too_smooth_path,buried_landmine,truth_freeze_destabilization,stage_boundary_sprawl,false_closure_signal,operator_cost_underpricing" in board_result.stdout
    assert "release.ceo_challenge: pass promotion=challenge_coverage_current missing=none" in board_result.stdout
