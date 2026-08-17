"""Gate contracts for wireframe-only prototype lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.commands.gate import GateMode, check_prototype_contract


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_ui_requirements(root: Path, version: str, feature: str) -> None:
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
            "prototype_archetype: management-board",
            "首页",
            "管理总览",
            "项目详情",
        ]
    )
    for directory in (us, prd, tc):
        (directory / f"{slug}.md").write_text(body, encoding="utf-8")


def test_gate_should_flag_missing_prototype_when_ui_visualization_required(tmp_path: Path):
    _write_ui_requirements(tmp_path, "v1.1.2", "Feature Proto")
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version="v1.1.2")
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_missing" in reason_codes


def test_gate_should_require_review_before_release(tmp_path: Path):
    feature = "Feature Proto"
    version = "v1.1.2"
    _write_ui_requirements(tmp_path, version, feature)
    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])
    assert create.exit_code == 0, create.stdout
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_not_frozen" in reason_codes
    assert "prototype_review_missing" in reason_codes


def test_gate_should_accept_frozen_wireframe_contract(tmp_path: Path):
    feature = "Feature Proto"
    version = "v1.1.2"
    _write_ui_requirements(tmp_path, version, feature)
    assert _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    assert json.loads(review.stdout)["overall_status"] == "pass"
    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    assert issues == []
