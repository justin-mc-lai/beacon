from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.command_catalog import SUPPORTED_SUBCOMMANDS
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()
PROTOTYPE_ENABLED = "prototype" in SUPPORTED_SUBCOMMANDS


@pytest.mark.parametrize(
    "relative_path",
    [
        "docs/beacon/v1.1.2/SUMMARY.md",
        "docs/beacon/v1.1.2/user-story/beacon-ui-prototype-lifecycle.md",
        "docs/beacon/v1.1.2/prd/beacon-ui-prototype-lifecycle.md",
        "docs/beacon/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.md",
        "docs/beacon/v1.1.2/execution/boundaries.md",
        "docs/beacon/v1.1.2/execution/beacon-ui-prototype-bootstrap-stack-decision.md",
    ],
)
def test_v112_prototype_materials_should_exist(relative_path: str):
    assert (ROOT / relative_path).exists(), relative_path


def test_v112_summary_and_boundaries_should_close_the_requirement_loop():
    summary = (ROOT / "docs" / "beacon" / "v1.1.2" / "SUMMARY.md").read_text(encoding="utf-8")
    boundaries = (
        ROOT / "docs" / "beacon" / "v1.1.2" / "execution" / "boundaries.md"
    ).read_text(encoding="utf-8")

    assert "prototype" in summary
    assert "workflow" in summary and "gate" in summary
    assert "Prototype 层（Visual Prototype Layer）" in boundaries
    assert "docs/beacon/v1.1.2/prototype/<feature>/" in boundaries


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prototype_command_should_expose_help():
    result = runner.invoke(app, ["prototype", "--help"])
    assert result.exit_code == 0
    assert "create" in result.stdout
    assert "freeze" in result.stdout
    assert "review" in result.stdout


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prompt_optimize_should_route_prototype_keywords(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "prompt",
            "optimize",
            "请帮我生成 wireframe prototype 并冻结需求",
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "prototype"
    assert payload.get("recommended_args", [])[:2] == ["prototype", "create"]


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_workflow_stages_and_gate_reason_codes_should_cover_prototype_contract():
    from beacon.commands.gate import REASON_CODES
    from beacon.commands.workflow import WORKFLOW_STAGES

    assert any(stage[0] == "prototype" for stage in WORKFLOW_STAGES)
    for code in [
        "prototype_missing",
        "prototype_not_frozen",
        "prototype_stale",
        "prototype_source_untraceable",
    ]:
        assert code in REASON_CODES


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prototype_create_should_write_wireframe_contract_artifacts(tmp_path: Path):
    version = "v1.1.2"
    slug = "demo-ui-feature"
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    tc_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    tc_dir.mkdir(parents=True, exist_ok=True)
    body = """# Requirement

prototype_archetype: dashboard
ui_visualization_required: true
首页
管理总览
项目详情
"""
    for directory in (us_dir, prd_dir, tc_dir):
        (directory / f"{slug}.md").write_text(body, encoding="utf-8")

    result = runner.invoke(
        app,
        ["prototype", "create", "Demo UI Feature", "--project", str(tmp_path), "--version", version],
    )
    assert result.exit_code == 0, result.stdout

    proto_dir = tmp_path / "docs" / "beacon" / version / "prototype" / slug
    for name in [
        "wireframe-summary.md",
        "manifest.json",
        "source-map.json",
        "freeze.json",
        "prototype-brief.json",
        "theme.json",
        "navigation-map.json",
        "interaction-map.json",
    ]:
        assert (proto_dir / name).exists(), name
    assert (proto_dir / "pages/home.md").exists()
    assert not (proto_dir / "index.html").exists()


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prototype_review_command_should_write_reports(tmp_path: Path):
    version = "v1.1.2"
    slug = "demo-ui-feature"
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    tc_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    tc_dir.mkdir(parents=True, exist_ok=True)
    for directory in (us_dir, prd_dir, tc_dir):
        (directory / f"{slug}.md").write_text(
            """prototype_archetype: dashboard
ui_visualization_required: true
首页
管理总览
项目详情
""",
            encoding="utf-8",
        )
    create = runner.invoke(app, ["prototype", "create", "Demo UI Feature", "--project", str(tmp_path), "--version", version])
    assert create.exit_code == 0
    review = runner.invoke(app, ["prototype", "review", "Demo UI Feature", "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0
    payload = json.loads(review.stdout)
    assert payload.get("overall_status") == "pass"
    proto_dir = tmp_path / "docs" / "beacon" / version / "prototype" / slug
    assert (proto_dir / "prototype-review.json").exists()
    assert (proto_dir / "prototype-review.md").exists()
