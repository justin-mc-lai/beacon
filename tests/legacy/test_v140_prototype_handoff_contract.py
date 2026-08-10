from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "beacon" / "v1.4.0" / "SUMMARY.md"
GLOBAL = ROOT / "docs" / "beacon" / "global-boundaries.md"
PROTOTYPE_ROOT = ROOT / "docs" / "beacon" / "v1.4.0" / "prototype" / "beacon-v1-4-0-llm-decision-surface-and-learning-loop-evolution"


def _read_json(name: str) -> dict:
    return json.loads((PROTOTYPE_ROOT / name).read_text(encoding="utf-8"))


def test_prototype_stage_is_conditionally_required_before_implement():
    global_text = GLOBAL.read_text(encoding="utf-8")
    summary_text = SUMMARY.read_text(encoding="utf-8")
    assert "`prototype` 不是默认必经主链，而是条件触发层" in global_text
    assert "prototype 已被条件触发并完成冻结" in summary_text


def test_route_surface_is_frozen_in_prototype_scope():
    plan = _read_json("prototype-plan.json")
    assert "intent-router" in plan.get("required_pages", [])
    assert "learning-disclosure-center" in plan.get("required_pages", [])
    assert "当前 route 推荐原因" in (plan.get("ux_contract", {}) or {}).get("required_feedback", [])


def test_state_navigation_and_interaction_contracts_are_required():
    manifest = _read_json("manifest.json")
    coverage = _read_json("coverage-report.json")
    assert manifest.get("status") == "frozen"
    assert coverage.get("navigation_contract_complete") is True
    assert coverage.get("interaction_contract_complete") is True
    assert coverage.get("route_closure_complete") is True


def test_cannot_claim_implement_ready_before_prototype_freeze():
    summary_text = SUMMARY.read_text(encoding="utf-8")
    freeze = _read_json("freeze.json")
    assert freeze.get("status") == "frozen"
    assert "prototype-frozen / implementation-not-started" in summary_text
