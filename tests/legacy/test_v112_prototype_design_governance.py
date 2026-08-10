from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_design_governed_sources(
    tmp_path: Path,
    feature: str,
    version: str = "v1.1.12",
) -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    tc_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    tc_dir.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            f"# User Story: {feature}",
            "",
            "prototype_mode: reference-pack-v2",
            "design_governance_required: true",
            "interactive_prototype_required: true",
            "ui_visualization_required: true",
            "prototype_archetype: admin-workbench",
            "首页",
            "管理总览",
            "项目详情",
            "运行中心",
            "恢复诊断",
            "项目物料查看器",
        ]
    )
    for directory in (us_dir, prd_dir, tc_dir):
        (directory / f"{slug}.md").write_text(body, encoding="utf-8")


def test_design_governance_inputs_should_still_emit_wireframe_only_artifacts(tmp_path: Path):
    feature = "Design Governed Prototype"
    version = "v1.1.12"
    _prepare_design_governed_sources(tmp_path, feature, version)

    plan = _invoke(["prototype", "plan", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert plan.exit_code == 0, plan.stdout
    plan_payload = json.loads(plan.stdout)
    assert plan_payload["prototype_mode"] == "wireframe"

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "design-governed-prototype"
    assert (root / "wireframe-summary.md").exists()
    assert (root / "navigation-map.md").exists()
    assert (root / "wireframe-manifest.json").exists()
    assert not (root / "index.html").exists()
    assert not (root / "ui-style-analysis.json").exists()
    assert not (root / "design-brief.json").exists()


def test_directory_command_should_return_wireframe_summary_paths(tmp_path: Path):
    feature = "Design Governed Prototype"
    version = "v1.1.12"
    _prepare_design_governed_sources(tmp_path, feature, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    directory = _invoke(["prototype", "directory", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert directory.exit_code == 0, directory.stdout
    payload = json.loads(directory.stdout)
    assert payload["wireframe_summary_path"].endswith("wireframe-summary.md")
    assert payload["navigation_map_path"].endswith("navigation-map.md")
    assert "management-overview" in payload["generated_pages"]
