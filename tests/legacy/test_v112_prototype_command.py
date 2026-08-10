"""Prototype command contracts for wireframe-only Beacon prototype generation."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_contract_sources(tmp_path: Path, feature: str, version: str = "v1.1.2") -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    tc_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    tc_dir.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            f"# Feature: {feature}",
            "",
            "ui_visualization_required: true",
            "prototype_archetype: management-board",
            "theme_primary: #2563eb",
            "theme_secondary: #0f172a",
            "首页",
            "管理总览",
            "项目详情",
            "运行中心",
            "恢复诊断",
            "项目物料查看器",
        ]
    )
    for root in (us_dir, prd_dir, tc_dir):
        (root / f"{slug}.md").write_text(body, encoding="utf-8")


def test_prototype_help():
    result = _invoke(["prototype", "--help"])
    assert result.exit_code == 0
    assert "wireframe" in result.stdout.lower()
    assert "review" in result.stdout


def test_prototype_create_generates_wireframe_bundle(tmp_path: Path):
    feature = "Login Feature"
    _prepare_contract_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0, result.stdout
    root = tmp_path / "docs" / "beacon" / "v1.1.2" / "prototype" / "login-feature"
    for rel in [
        "wireframe-summary.md",
        "wireframe-manifest.json",
        "navigation-map.json",
        "navigation-map.md",
        "interaction-map.json",
        "coverage-report.json",
        "prototype-review.json",
        "prototype-review.md",
        "pages/home.md",
        "page-specs/home.json",
    ]:
        assert (root / rel).exists(), rel
    assert not (root / "index.html").exists()


def test_prototype_outputs_only_under_docs_beacon(tmp_path: Path):
    feature = "Orders Dashboard"
    _prepare_contract_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["paths"]["wireframe_summary"].startswith("docs/beacon/v1.1.2/prototype/")
    assert "index_html" in payload["paths"]
    assert "docs/product" not in result.stdout
    assert payload["prototype_mode"] == "wireframe"


def test_prototype_review_freeze_and_status_gate_ready(tmp_path: Path):
    feature = "Settings Screen"
    _prepare_contract_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"
    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    freeze_payload = json.loads(freeze.stdout)
    assert freeze_payload["status"] == "frozen"
    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    status_payload = json.loads(status.stdout)
    assert status_payload["prototype_mode"] == "wireframe"
    assert status_payload["review_status"] == "pass"
    assert status_payload["gate_ready"] is True


def test_prototype_create_requires_test_case_truth(tmp_path: Path):
    version = "v1.1.2"
    slug = "missing-feature"
    feat_dir = tmp_path / "docs" / "beacon" / version / "features" / slug
    feat_dir.mkdir(parents=True, exist_ok=True)
    # Package-authoritative truth: user-story/prd live in truth.md; test-case
    # lives in tests.md. Keep tests.md missing to exercise the gate.
    (feat_dir / "truth.md").write_text(
        "# Truth\nui_visualization_required: true\n",
        encoding="utf-8",
    )
    result = _invoke(["prototype", "create", "Missing Feature", "--project", str(tmp_path), "--version", version])
    assert result.exit_code == 2
    assert "missing: test-case" in result.output
