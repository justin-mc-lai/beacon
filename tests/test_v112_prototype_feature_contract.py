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
    decision = (
        ROOT / "docs" / "beacon" / "v1.1.2" / "execution" / "beacon-ui-prototype-bootstrap-stack-decision.md"
    ).read_text(encoding="utf-8")

    assert "prototype" in summary
    assert "Bootstrap 5.3.x" in summary
    assert "workflow" in summary and "gate" in summary
    assert "Prototype 层（Visual Prototype Layer）" in boundaries
    assert "docs/beacon/v1.1.2/prototype/<feature>/" in boundaries
    assert "Bootstrap 5.3.x" in decision
    assert "可冻结" in decision and "可治理" in decision


def test_v121_requirement_materials_should_have_been_removed():
    assert not (ROOT / "docs" / "beacon" / "v1.2.1").exists()


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prototype_command_should_expose_help():
    result = runner.invoke(app, ["prototype", "--help"])
    assert result.exit_code == 0
    assert "create" in result.stdout
    assert "freeze" in result.stdout


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prompt_optimize_should_route_prototype_keywords(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "prompt",
            "optimize",
            "生成交互原型并冻结需求",
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
def test_prototype_create_should_write_static_single_page_artifacts(tmp_path: Path):
    version = "v1.1.2"
    slug = "demo-ui-feature"
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text(
        "# User Story\n\nui_visualization_required: true\n", encoding="utf-8"
    )
    (prd_dir / f"{slug}.md").write_text(
        "# PRD\n\nprototype_ui_kit: bootstrap-5.3.x\n", encoding="utf-8"
    )

    result = runner.invoke(
        app,
        ["prototype", "create", "Demo UI Feature", "--project", str(tmp_path), "--version", version],
    )
    assert result.exit_code == 0, result.stdout

    proto_dir = tmp_path / "docs" / "beacon" / version / "prototype" / slug
    assert (proto_dir / "index.html").exists()
    assert (proto_dir / "manifest.json").exists()
    assert (proto_dir / "source-map.json").exists()
    assert (proto_dir / "freeze.json").exists()

    html = (proto_dir / "index.html").read_text(encoding="utf-8")
    assert "bootstrap" in html.lower()
    assert "alpine" in html.lower() or "x-data" in html.lower()


@pytest.mark.skipif(not PROTOTYPE_ENABLED, reason="prototype command not yet registered")
def test_prototype_preview_status_and_list_should_work_after_create(tmp_path: Path):
    version = "v1.1.2"
    slug = "demo-ui-feature"
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    create = runner.invoke(
        app,
        ["prototype", "create", "Demo UI Feature", "--project", str(tmp_path), "--version", version],
    )
    assert create.exit_code == 0

    preview = runner.invoke(
        app,
        ["prototype", "preview", "Demo UI Feature", "--project", str(tmp_path), "--version", version],
    )
    assert preview.exit_code == 0

    status = runner.invoke(
        app,
        ["prototype", "status", "Demo UI Feature", "--project", str(tmp_path), "--version", version],
    )
    assert status.exit_code == 0

    listing = runner.invoke(app, ["prototype", "list", "--project", str(tmp_path), "--version", version])
    assert listing.exit_code == 0
    assert slug in listing.stdout or "Demo UI Feature" in listing.stdout
