from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.4.7"
FEATURE = "beacon-v1.4.7-ceo-review-cli-challenge-axes-alignment"
SLUG = "beacon-v1.4.7-ceo-review-cli-challenge-axes-alignment"


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


def test_v147_review_ceo_plain_output_should_print_default_challenge_axes(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    result = runner.invoke(
        app,
        ["review", "ceo", FEATURE, "--project", str(tmp_path), "--version", VERSION],
    )

    assert result.exit_code == 0, result.stdout
    assert "✓ CEO review complete: advisory" in result.stdout
    assert "✓ Challenge axes:" in result.stdout
    assert "too_smooth_path" in result.stdout
    assert "truth_freeze_destabilization" in result.stdout
    assert "operator_cost_underpricing" in result.stdout


def test_v147_review_ceo_json_output_should_keep_default_challenge_axes(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    result = runner.invoke(
        app,
        ["review", "ceo", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert [axis["code"] for axis in payload["challenge_axes"]] == [
        "too_smooth_path",
        "buried_landmine",
        "truth_freeze_destabilization",
        "stage_boundary_sprawl",
        "false_closure_signal",
        "operator_cost_underpricing",
    ]
