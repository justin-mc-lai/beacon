from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.commands.gate import GateMode, check_prototype_contract


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_contract_sources(tmp_path: Path, feature: str, version: str = "v1.1.3") -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    body = """ui_visualization_required: true
prototype_archetype: admin-workbench
target_user: ops lead
theme_mood: trusted
theme_primary: #2563eb
theme_secondary: #111827
brand_keywords: trust, delivery, visibility
surface_style: elevated-clean
sections: Overview, Queue, Escalations
navigation: Overview, Queue, Escalations
primary_entry: Overview
primary_exit: Escalations
primary_cta: Review blockers
secondary_cta: Export report
jump_map: Overview->Queue: Review pending blockers; Queue->Escalations: Escalate failures
modal_map: Review blockers modal
drawer_map: Escalation drawer
tab_map: Overview, Queue, States
states: empty, loading, error, success, blocked
"""
    (us_dir / f"{slug}.md").write_text("# User Story\n" + body, encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text("# PRD\n" + body, encoding="utf-8")


def test_gate_should_require_review_and_contract_artifacts(tmp_path: Path):
    feature = "Ops Console"
    version = "v1.1.3"
    _prepare_contract_sources(tmp_path, feature, version)
    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])
    assert create.exit_code == 0
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_review_missing" in reason_codes


def test_test_case_should_consume_prototype_contract_maps(tmp_path: Path):
    feature = "Ops Console"
    version = "v1.1.3"
    _prepare_contract_sources(tmp_path, feature, version)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])
    tc = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", version])
    assert tc.exit_code == 0
    matrix = json.loads(
        (tmp_path / "docs" / "beacon" / version / "qa" / "test-cases" / "ops-console.ac-test-matrix.json").read_text(
            encoding="utf-8"
        )
    )
    sources = {item.get("source") for item in matrix.get("entries", [])}
    assert "prototype:navigation-map" in sources
    assert "prototype:interaction-map" in sources
