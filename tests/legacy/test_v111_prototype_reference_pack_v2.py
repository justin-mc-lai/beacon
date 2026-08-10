from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.main import app
from beacon.utils.artifact_paths import qa_matrix_output


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_legacy_contract_sources(tmp_path: Path, feature: str, version: str = "v1.1.11") -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    tc_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    tc_dir.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            f"# Requirement: {feature}",
            "",
            "prototype_mode: reference-pack-v2",
            "ui_visualization_required: true",
            "prototype_archetype: admin-workbench",
            "route_closure_required: true",
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


def test_v11111_legacy_reference_pack_inputs_should_collapse_to_wireframe_mode(tmp_path: Path):
    feature = "Prototype Reference Pack V2"
    version = "v1.1.11"
    _prepare_legacy_contract_sources(tmp_path, feature, version)

    plan = _invoke(["prototype", "plan", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert plan.exit_code == 0, plan.stdout
    plan_payload = json.loads(plan.stdout)
    assert plan_payload["prototype_mode"] == "wireframe"
    assert "management-overview" in plan_payload["required_pages"]

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["prototype_mode"] == "wireframe"

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "prototype-reference-pack-v2"
    assert (root / "wireframe-summary.md").exists()
    assert (root / "pages/management-overview.md").exists()
    assert not (root / "index.html").exists()


def test_v11111_wireframe_bundle_should_feed_test_case_and_gate(tmp_path: Path):
    feature = "Prototype Reference Pack V2"
    version = "v1.1.11"
    _prepare_legacy_contract_sources(tmp_path, feature, version)

    assert _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "bind", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    assert json.loads(review.stdout)["overall_status"] == "pass"
    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    tc = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", version])
    assert tc.exit_code == 0, tc.stdout
    matrix_path = qa_matrix_output(tmp_path, version, "prototype-reference-pack-v2", "ac-test-matrix")
    matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    sources = {item.get("source") for item in matrix_payload.get("entries", []) if isinstance(item, dict)}
    assert "prototype:page-specs" in sources
    assert "prototype:coverage-report" in sources

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    assert issues == []
