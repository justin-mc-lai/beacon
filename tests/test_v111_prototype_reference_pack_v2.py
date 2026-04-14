from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.utils.artifact_paths import machine_execution_dir, qa_matrix_output
from beacon.utils.doctor_diagnostics import build_doctor_payload
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import compute_workflow_progress
from beacon.utils.writeback import record_implementation_writeback, record_verification_writeback
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_v2_contract_sources(tmp_path: Path, feature: str, version: str = "v1.1.11") -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            f"# User Story: {feature}",
            "",
            "**As a** product owner，",
            "**I want** a truthful reference pack，",
            "**So that** implementation and QA can consume it.",
            "",
            "prototype_mode: reference-pack-v2",
            "ui_visualization_required: true",
            "coverage_mode: all-existing-routes",
            "prototype_archetype: admin-workbench",
            "target_user: 产品负责人",
            "theme_mood: disciplined",
            "theme_primary: #2563eb",
            "theme_secondary: #0f172a",
            "sections: Overview；Page Inventory；Route Closure；Baseline Protection；Delivery Readiness",
            "navigation: Overview；Page Inventory；Route Closure；Delivery Readiness",
            "primary_entry: Overview",
            "primary_exit: Delivery Readiness",
            "primary_cta: Generate Reference Pack",
            "secondary_cta: Inspect pages",
            "jump_map: Overview->Page Inventory：inventory review；Page Inventory->Route Closure：check routes；Route Closure->Delivery Readiness：ready gate",
            "states: empty；loading；error；auth-required；completed",
            "required_states:",
            "  - empty",
            "  - loading",
            "  - error",
            "  - auth-required",
            "  - completed",
            "baseline_protection:",
            "  - page: Overview",
            "    preserve:",
            "      - headline",
            "      - primary-cta",
            "  - page: Page Inventory",
            "    preserve:",
            "      - required-pages",
            "      - state-matrix",
            "route_closure_required: true",
        ]
    )
    (us_dir / f"{slug}.md").write_text(body, encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# PRD: {feature}",
                "",
                "prototype_mode: reference-pack-v2",
                "ui_visualization_required: true",
                "coverage_mode: all-existing-routes",
                "prototype_archetype: admin-workbench",
                "theme_mood: disciplined",
                "theme_primary: #1d4ed8",
                "theme_secondary: #111827",
                "sections: Overview；Page Inventory；Route Closure；Baseline Protection；Delivery Readiness",
                "navigation: Overview；Page Inventory；Route Closure；Delivery Readiness",
                "primary_entry: Overview",
                "primary_exit: Delivery Readiness",
                "primary_cta: Generate Reference Pack",
                "secondary_cta: Inspect pages",
                "jump_map: Overview->Page Inventory：inventory review；Page Inventory->Route Closure：check routes；Route Closure->Delivery Readiness：ready gate",
                "states: empty；loading；error；auth-required；completed",
                "required_states:",
                "  - empty",
                "  - loading",
                "  - error",
                "  - auth-required",
                "  - completed",
                "baseline_protection:",
                "  - page: Overview",
                "    preserve:",
                "      - headline",
                "      - primary-cta",
                "  - page: Page Inventory",
                "    preserve:",
                "      - required-pages",
                "      - state-matrix",
                "route_closure_required: true",
            ]
        ),
        encoding="utf-8",
    )


def test_v11111_prototype_plan_create_and_bind_emit_v2_artifacts(tmp_path: Path):
    feature = "Prototype Reference Pack V2"
    version = "v1.1.11"
    _prepare_v2_contract_sources(tmp_path, feature, version)

    plan = _invoke(["prototype", "plan", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert plan.exit_code == 0, plan.stdout
    plan_payload = json.loads(plan.stdout)
    assert plan_payload["prototype_mode"] == "reference-pack-v2"
    assert "overview" in plan_payload["required_pages"]
    assert "completed" in plan_payload["required_states"]

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["prototype_mode"] == "reference-pack-v2"

    tc = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", version])
    assert tc.exit_code == 0, tc.stdout
    feature_slug = feature.lower().replace(" ", "-")
    matrix_path = qa_matrix_output(tmp_path, version, feature_slug, "ac-test-matrix")
    matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    sources = {item.get("source") for item in matrix_payload.get("entries", []) if isinstance(item, dict)}
    assert "prototype:page-specs" in sources
    assert "prototype:coverage-report" in sources

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "prototype-reference-pack-v2"
    for rel in [
        "prototype-plan.json",
        "coverage-report.json",
        "tokens.css",
        "page-specs/overview.json",
        "pages/overview.html",
        "states/overview--loading.html",
    ]:
        assert (root / rel).exists(), rel
    index_html = (root / "index.html").read_text(encoding="utf-8")
    assert 'href="pages/overview.html"' in index_html
    assert 'href="states/overview--loading.html"' in index_html

    review_before = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review_before.exit_code == 0, review_before.stdout
    review_before_payload = json.loads(review_before.stdout)
    assert review_before_payload["overall_status"] == "fail"
    failed_before = {item["name"] for item in review_before_payload["checks"] if item["status"] == "fail"}
    assert "route_closure_binding_complete" in failed_before

    bind = _invoke(["prototype", "bind", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert bind.exit_code == 0, bind.stdout
    bind_payload = json.loads(bind.stdout)
    assert bind_payload["bound_cases"] > 0

    review_after = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review_after.exit_code == 0, review_after.stdout
    review_after_payload = json.loads(review_after.stdout)
    assert review_after_payload["overall_status"] == "pass"
    passed_checks = {item["name"] for item in review_after_payload["checks"] if item["status"] == "pass"}
    assert "prototype_required_page_missing" in passed_checks
    assert "prototype_required_state_missing" in passed_checks
    assert "prototype_artifact_inconsistent" in passed_checks

    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    freeze_payload = json.loads(freeze.stdout)
    assert freeze_payload["status"] == "frozen"

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["status"] == "frozen"
    assert status_payload["gate_ready"] is True

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    assert issues == []


def test_v11111_cjk_parser_and_coverage_report_are_truthful(tmp_path: Path):
    feature = "CJK Prototype"
    version = "v1.1.11"
    _prepare_v2_contract_sources(tmp_path, feature, version)

    plan = _invoke(["prototype", "plan", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert plan.exit_code == 0, plan.stdout
    payload = json.loads(plan.stdout)
    assert payload["prototype_mode"] == "reference-pack-v2"

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "cjk-prototype"
    plan_file = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    coverage_file = json.loads((root / "coverage-report.json").read_text(encoding="utf-8"))
    assert plan_file["parser"]["cjk_detected"] is True
    assert plan_file["parser"]["cjk_parse_failed"] is False
    assert coverage_file["compact_mode_detected"] is False
    assert "overview" in coverage_file["required_pages"]


def test_v11111_review_accept_should_close_workflow_lifecycle_from_delivery_artifacts(tmp_path: Path):
    feature = "Prototype Reference Pack V2"
    version = "v1.1.11"
    slug = feature.lower().replace(" ", "-")
    _prepare_v2_contract_sources(tmp_path, feature, version)

    assert _invoke(["prototype", "plan", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "bind", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    assert _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", version]).exit_code == 0
    freeze_revision_state(tmp_path, version=version, feature=feature)

    run_id = "run-accept-v11111"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": slug,
            "version": version,
            "prototype_enabled": True,
            "status": "planned",
            "events": [
                {"event": "workflow_started", "ts": "2026-03-31T00:00:00Z"},
                {"event": "workflow_planned", "ts": "2026-03-31T00:00:01Z"},
            ],
        },
    )

    execution = tmp_path / "docs" / "beacon" / version / "execution"
    machine_execution = machine_execution_dir(tmp_path, version)
    execution.mkdir(parents=True, exist_ok=True)
    machine_execution.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / version / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (execution / "index.md").write_text("# Execution Index\n", encoding="utf-8")
    (execution / "architecture-blueprint.md").write_text("# Architecture Blueprint\n", encoding="utf-8")
    (execution / f"technical-implementation-{slug}.md").write_text("# Technical Implementation\n", encoding="utf-8")
    (machine_execution / f"technical-implementation-{slug}.json").write_text("{}", encoding="utf-8")
    (execution / f"implementation-summary-{slug}.md").write_text("# Implementation Summary\n", encoding="utf-8")
    (machine_execution / f"implementation-summary-{slug}.json").write_text("{}", encoding="utf-8")

    beacon_root = tmp_path / ".beacon"
    (beacon_root / "state").mkdir(parents=True, exist_ok=True)
    (beacon_root / "state" / f"implementation-{slug}.json").write_text("{}", encoding="utf-8")
    (beacon_root / "qa").mkdir(parents=True, exist_ok=True)
    (beacon_root / "qa" / "status.json").write_text(json.dumps({"status": "passed", "evidence_done": True}), encoding="utf-8")
    (beacon_root / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "version": version, "run_id": run_id}),
        encoding="utf-8",
    )
    (beacon_root / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "stage": "release", "version": version, "run_id": run_id}),
        encoding="utf-8",
    )
    (beacon_root / "evidence-manifest.json").write_text(
        json.dumps({"version": version, "run_id": run_id, "entries": [{"path": ".beacon/auto-test-status.json", "sha256": "x"}]}),
        encoding="utf-8",
    )
    (machine_execution / "terminal.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": run_id, "traceability": {}}),
        encoding="utf-8",
    )

    record_implementation_writeback(
        tmp_path,
        version=version,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=["AC-001"],
        changed_files=["beacon/commands/prototype.py"],
    )
    record_verification_writeback(
        tmp_path,
        version=version,
        feature=feature,
        run_id="review.accept",
        verified_item_ids=["AC-001", "TEST-001"],
        failed_item_ids=[],
        evidence_ref=[".beacon/auto-test-status.json"],
    )

    accept = _invoke(["review", "accept", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert accept.exit_code == 0, accept.stdout
    accept_payload = json.loads(accept.stdout)
    assert accept_payload["status"] == "accepted"
    assert accept_payload["workflow_closure_complete"] is True
    assert accept_payload["workflow_gate_pass"] is True
    assert accept_payload["workflow_missing_stages"] == []
    assert set(accept_payload["workflow_synced_stages"]) == {
        "think",
        "user-story",
        "prd",
        "prototype",
        "test-case",
        "implementation",
        "verify",
        "gate",
    }

    progress = compute_workflow_progress(tmp_path, version=version, feature=feature)
    assert progress["run_id"] == run_id
    assert progress["closure_complete"] is True
    assert progress["gate_pass"] is True
    assert progress["missing_closure_stages"] == []

    diagnostics = build_doctor_payload(tmp_path, strict=True)
    incompatibility_codes = {item["code"] for item in diagnostics.get("incompatibilities", [])}
    assert "COMP-202" not in incompatibility_codes
