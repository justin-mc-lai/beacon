from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_design_governed_requirements(root: Path, version: str, feature: str) -> None:
    slug = feature.lower().replace(" ", "-")
    us = root / "docs" / "beacon" / version / "user-story"
    prd = root / "docs" / "beacon" / version / "prd"
    tc = root / "docs" / "beacon" / version / "qa" / "test-cases"
    us.mkdir(parents=True, exist_ok=True)
    prd.mkdir(parents=True, exist_ok=True)
    tc.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "ui_visualization_required: true",
            "prototype_mode: reference-pack-v2",
            "design_governance_required: true",
            "interactive_prototype_required: true",
            "首页",
            "管理总览",
            "项目详情",
        ]
    )
    for directory in (us, prd, tc):
        (directory / f"{slug}.md").write_text(body, encoding="utf-8")


def test_gate_should_not_require_legacy_design_governance_artifacts_in_wireframe_mode(tmp_path: Path):
    feature = "Feature Proto"
    version = "v1.1.12"
    _write_design_governed_requirements(tmp_path, version, feature)
    assert _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_design_brief_missing" not in reason_codes
    assert "prototype_design_system_contract_missing" not in reason_codes
    assert "prototype_design_prompt_missing" not in reason_codes
    assert "prototype_web_guideline_review_missing" not in reason_codes


def test_gate_should_pass_when_wireframe_bundle_is_frozen_even_with_legacy_markers(tmp_path: Path):
    feature = "Feature Proto"
    version = "v1.1.12"
    _write_design_governed_requirements(tmp_path, version, feature)
    assert _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    assert json.loads(review.stdout)["overall_status"] == "pass"
    assert _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    assert issues == []
