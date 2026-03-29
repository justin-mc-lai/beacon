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


def _prepare_contract_sources(tmp_path: Path, feature: str, version: str = "v1.1.10") -> None:
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
tab_map: Overview, Queue, States
states: empty, loading, error, success, blocked
route_closure_required: true
drift_guardrails: isolated-page, fragile-route, legacy-only-entry, fake-jump, tab-route-drift
"""
    (us_dir / f"{slug}.md").write_text("# User Story\n" + body, encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text("# PRD\n" + body, encoding="utf-8")


def test_v110_prototype_create_should_emit_route_closure_contract_and_impl_map(tmp_path: Path):
    feature = "Frontend Route Closure"
    version = "v1.1.10"
    _prepare_contract_sources(tmp_path, feature, version)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert "route_closure_contract" in payload["paths"]
    assert "implementation_map" in payload["paths"]
    root = tmp_path / "docs" / "beacon" / version / "prototype" / "frontend-route-closure"
    route_contract = json.loads((root / "route-closure-contract.json").read_text(encoding="utf-8"))
    implementation_map = json.loads((root / "implementation-map.json").read_text(encoding="utf-8"))
    assert route_contract["required"] is True
    assert route_contract["closure_cases"]
    assert implementation_map["closure_bindings"]


def test_v110_prototype_review_should_fail_until_route_closure_is_bound(tmp_path: Path):
    feature = "Frontend Route Closure"
    version = "v1.1.10"
    _prepare_contract_sources(tmp_path, feature, version)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    payload = json.loads(review.stdout)
    assert payload["overall_status"] == "fail"
    failed = {item["name"] for item in payload["checks"] if item["status"] == "fail"}
    assert "route_closure_binding_complete" in failed

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "frontend-route-closure"
    impl = json.loads((root / "implementation-map.json").read_text(encoding="utf-8"))
    for binding in impl["closure_bindings"]:
        binding["binding_status"] = "bound"
        binding["runtime_target"] = f"/{binding['case_id'].lower()}"
        if binding.get("context_contract"):
            binding["state_target"] = "queue"
        binding["drift_status"] = "closed"
    (root / "implementation-map.json").write_text(json.dumps(impl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    review_after = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review_after.exit_code == 0, review_after.stdout
    payload_after = json.loads(review_after.stdout)
    assert payload_after["overall_status"] == "pass"


def test_v110_gate_should_surface_route_closure_reason_codes(tmp_path: Path):
    feature = "Frontend Route Closure"
    version = "v1.1.10"
    _prepare_contract_sources(tmp_path, feature, version)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])
    _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version])
    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    reason_codes = {item.get("reason_code") for item in issues}
    assert "prototype_review_failed" in reason_codes
    assert "prototype_surface_unbound" in reason_codes


def test_v110_test_case_should_consume_route_closure_contract(tmp_path: Path):
    feature = "Frontend Route Closure"
    version = "v1.1.10"
    _prepare_contract_sources(tmp_path, feature, version)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version])
    tc = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", version, "--output", "/tmp/route-closure.md"])
    assert tc.exit_code == 0, tc.stdout
    matrix_path = qa_matrix_output(tmp_path, version, "frontend-route-closure", "ac-test-matrix")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    sources = {item.get("source") for item in matrix.get("entries", [])}
    assert "prototype:route-closure-contract" in sources
