from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_sources(tmp_path: Path, feature_slug: str, version: str) -> None:
    content = """# Feature

AC-001 prototype mode must be wireframe
AC-002 pages and navigation are frozen
TC-001 verify mode and files
TC-002 verify state and component mapping
首页
管理总览
项目详情
运行中心
恢复诊断
项目物料查看器
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def test_v135_create_review_freeze_should_emit_projection_consistency_payload(tmp_path: Path):
    version = "v1.3.5"
    feature_slug = "projection-consistency-demo"
    feature = "Projection Consistency Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["prototype_mode"] == "wireframe"

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    assert (root / "canonical-envelope.json").exists()
    assert (root / "state-flow-map.json").exists()
    assert (root / "state-flow-map.md").exists()
    assert (root / "component-catalog.json").exists()
    assert (root / "component-catalog.md").exists()

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"
    assert review_payload["human_view_status"] == "pass"
    assert review_payload["machine_contract_status"] == "pass"
    assert review_payload["sqlite_projection_status"] == "pass"
    assert review_payload["drift_status"] == "consistent"

    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    freeze_payload = json.loads(freeze.stdout)
    assert freeze_payload["status"] == "frozen"
    assert freeze_payload["transaction"]["transaction_id"]

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["gate_ready"] is True
    assert status_payload["drift_status"] == "consistent"

