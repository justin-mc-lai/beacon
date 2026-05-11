from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands import qa as qa_command
from beacon.main import app
from beacon.utils.delivery_kernel import load_delivery_read_model
from beacon.utils.help_navigation import build_doctor_advise_payload
from beacon.utils.help_support import build_help_payload
from beacon.utils.material_audit import build_delivery_audit
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.semantic_runtime import write_semantic_layer
from beacon.utils.v115_delivery import repair_v115_delivery_package


runner = CliRunner()
FEATURE = "Beacon Delivery Kernel Feature"
SLUG = "beacon-delivery-kernel-feature"
OTHER_FEATURE = "beacon-v1.3.6-visual-management-console-and-material-viewer"
OTHER_SLUG = "beacon-v1.3.6-visual-management-console-and-material-viewer"
VERSION = "v1.3.6"


def _seed_feature_docs(root: Path, *, slug: str) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs / "user-story" / f"{SLUG}.md").write_text("# User Story\n", encoding="utf-8")
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    write_json(
        docs / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json",
        {"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}]},
    )


def _seed_docs(root: Path) -> None:
    _seed_feature_docs(root, slug=SLUG)


def _seed_support_projection_docs(root: Path) -> None:
    beacon_docs_root = root / "docs" / "beacon"
    beacon_docs_root.mkdir(parents=True, exist_ok=True)
    (beacon_docs_root / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    execution = root / "docs" / "beacon" / VERSION / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "index.md").write_text("# Execution Index\n", encoding="utf-8")
    (execution / "architecture-blueprint.md").write_text("# Architecture Blueprint\n", encoding="utf-8")


def _enable_prototype_requirement(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    marker = "\nprototype: true\n"
    for path in (
        docs / "prd" / f"{SLUG}.md",
        docs / "user-story" / f"{SLUG}.md",
        docs / "qa" / "test-cases" / f"{SLUG}.md",
    ):
        path.write_text(path.read_text(encoding="utf-8") + marker, encoding="utf-8")


def _seed_semantic_layer(root: Path) -> None:
    _enable_prototype_requirement(root)
    write_semantic_layer(
        root,
        version=VERSION,
        feature=FEATURE,
        stage="prototype",
        run_id="run-prototype-001",
        capability_snapshot={"host_runtime": "codex", "host_semantic_ready": True},
    )


def _seed_execution_state(root: Path) -> None:
    requirement_binding = {
        "source_of_truth_root": f"docs/beacon/{VERSION}",
        "prd": f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "user_story": f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        "test_case": f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "ac_matrix": f"docs/beacon/{VERSION}/.machine/qa/{SLUG}.ac-test-matrix.json",
    }
    write_json(
        root / ".beacon" / "implement" / "run-impl-001" / "state.json",
        {
            "schema_version": "1.0",
            "run_id": "run-impl-001",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "status": "completed",
            "mode": "team",
            "runner": "codex-subagents",
            "adapter_type": "native",
            "host_runtime": "codex",
            "subagent_prechecks": {
                "required": True,
                "host_runtime": "codex",
                "runtime_readiness": {"status": "pass"},
                "delegation_readiness": {"status": "pass"},
            },
            "requirement_traceability": requirement_binding,
            "traceability_refs": list(requirement_binding.values()),
            "execution_surface": "implement-team",
        },
    )
    feature_status = {
        "schema_version": "1.0",
        "run_id": "run-qa-001",
        "feature": FEATURE,
        "feature_slug": SLUG,
        "version": VERSION,
        "status": "passed",
        "execution_mode": "feature-aware",
        "execution_surface": "qa",
        "host_runtime": "codex",
        "subagent_prechecks": {
            "required": False,
            "host_runtime": "codex",
            "runtime_readiness": {"status": "pass"},
            "delegation_readiness": {"status": "pass"},
        },
        "feature_matrix_path": f".beacon/qa/features/{SLUG}/matrix.qa9.json",
        "canonical_matrix_path": f"docs/beacon/{VERSION}/.machine/qa/{SLUG}.qa9-matrix.json",
        "feature_scorecard_path": f".beacon/qa/features/{SLUG}/scorecard.json",
        "release_ready": True,
        "feature_scorecard": {
            "continue_decision": "ready_for_release",
            "release_ready": True,
        },
    }
    write_json(root / ".beacon" / "qa" / "features" / SLUG / "status.json", feature_status)
    write_json(root / ".beacon" / "qa" / "status.json", feature_status)
    write_json(
        root / ".beacon" / "qa" / "features" / SLUG / "scorecard.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "run_id": "run-qa-001",
            "continue_decision": "ready_for_release",
            "release_ready": True,
            "unresolved_closure_outcomes": [],
            "coverage_current": {"required_scenarios": 1, "executed_scenarios": 1, "coverage_rate": 1.0},
        },
    )
    write_json(
        root / ".beacon" / "qa" / "features" / SLUG / "exhaustiveness-report.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "run_id": "run-qa-001",
            "status": "passed",
            "score": 0.95,
            "threshold": 0.8,
        },
    )
    write_json(
        root / ".beacon" / "gate-report.json",
        {"status": "Pass", "version": VERSION, "run_id": "run-qa-001", "issues": []},
    )


def test_v136_delivery_read_model_should_merge_implement_and_qa_state(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)

    payload = load_delivery_read_model(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["contract"]["host_runtime"] == "codex"
    assert payload["implement"]["delivery_contract"]["runner"] == "codex-subagents"
    assert payload["qa"]["delivery_contract"]["execution_mode"] == "feature-aware"
    assert payload["traceability"]["requirement_binding"]["prd"].endswith(f"{SLUG}.md")


def test_v136_release_scorecard_should_include_host_native_delivery_aggregate(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _seed_semantic_layer(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    scorecard = build_release_scorecard(tmp_path, version=VERSION)

    assert "delivery_read_model" in scorecard
    assert scorecard["delivery_read_model"]["contract"]["host_runtime"] == "codex"
    assert scorecard["host_native_delivery"]["implement"]["runner"] == "codex-subagents"
    assert scorecard["host_native_delivery"]["qa"]["execution_mode"] == "feature-aware"
    assert scorecard["semantic"]["status"] == "pass"
    assert scorecard["delivery_read_model"]["release"]["semantic"]["reason_code"] == "semantic_contract_ok"


def test_v136_release_scorecard_should_fallback_to_revision_feature_when_qa_version_mismatches(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "version": "v1.3.5",
            "status": "passed",
        },
    )
    write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"status": "Pass", "version": VERSION, "run_id": "run-scorecard-001", "issues": []},
    )

    scorecard = build_release_scorecard(tmp_path, version=VERSION)

    assert scorecard["delivery"]["revision_id"] == "R1"
    assert scorecard["change_documents"]["current_feature_slug"] == SLUG


def test_v136_release_scorecard_should_prefer_latest_frozen_revision_feature_over_lexicographic_sort(
    tmp_path: Path,
) -> None:
    _seed_docs(tmp_path)
    _seed_feature_docs(tmp_path, slug=OTHER_SLUG)
    write_json(
        tmp_path / ".beacon" / "implement" / "run-impl-other" / "state.json",
        {
            "schema_version": "1.0",
            "run_id": "run-impl-other",
            "feature": OTHER_FEATURE,
            "version": VERSION,
            "status": "completed",
        },
    )
    freeze_revision_state(tmp_path, version=VERSION, feature=OTHER_FEATURE)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "schema_version": "1.0",
            "feature": OTHER_FEATURE,
            "version": "v1.3.5",
            "status": "passed",
        },
    )
    write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"status": "Pass", "version": VERSION, "run_id": "run-scorecard-002", "issues": []},
    )

    scorecard = build_release_scorecard(tmp_path, version=VERSION)

    assert scorecard["change_documents"]["current_feature_slug"] == SLUG
    assert scorecard["delivery_read_model"]["feature"] == FEATURE


def test_v136_help_status_and_doctor_advise_should_share_surface_explanation(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_support_projection_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _seed_semantic_layer(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    help_payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    advise_payload = build_doctor_advise_payload(tmp_path, version=VERSION, feature=FEATURE)
    status_result = runner.invoke(
        app,
        ["status", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE],
    )

    assert status_result.exit_code == 0, status_result.stdout
    status_payload = json.loads(status_result.stdout)
    assert help_payload["surface_explanation"]["capability"]["host_runtime"] == "codex"
    assert advise_payload["surface_explanation"] == help_payload["surface_explanation"]
    assert status_payload["surface_explanation"] == help_payload["surface_explanation"]
    assert status_payload["delivery_read_model"]["contract"]["host_runtime"] == "codex"
    assert advise_payload["support_surface_projection"] == help_payload["support_surface_projection"]
    assert status_payload["support_surface_projection"] == help_payload["support_surface_projection"]
    taxonomy = help_payload["support_surface_projection"]["artifact_taxonomy"]
    assert help_payload["support_surface_projection"]["support_mode"] == "explanation-layer"
    assert help_payload["support_surface_projection"]["primary_operator_doc_ref"] == f"docs/beacon/{VERSION}/execution/index.md"
    assert taxonomy["required_human_projection"]["refs"][0] == "docs/beacon/global-boundaries.md"
    assert f"docs/beacon/{VERSION}/execution/architecture-blueprint.md" in taxonomy["required_human_projection"]["refs"]


def test_v136_archive_support_surfaces_should_expose_shared_operator_projection(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_support_projection_docs(tmp_path)

    explain_result = runner.invoke(
        app,
        ["archive", "explain", "--project-root", str(tmp_path), "--version", VERSION, "--json"],
    )
    status_result = runner.invoke(
        app,
        ["archive", "status", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"],
    )

    assert explain_result.exit_code == 0, explain_result.stdout
    assert status_result.exit_code == 0, status_result.stdout
    explain_payload = json.loads(explain_result.stdout)
    status_payload = json.loads(status_result.stdout)
    assert explain_payload["support_surface_projection"]["support_mode"] == "explanation-layer"
    assert status_payload["support_surface_projection"]["primary_operator_doc_ref"] == f"docs/beacon/{VERSION}/execution/index.md"
    assert status_payload["support_surface_projection"]["artifact_taxonomy"]["canonical_envelope"]["default_root"] == f"docs/beacon/{VERSION}/.machine/execution"


def test_v136_release_scorecard_should_block_release_when_semantic_contract_missing(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _seed_semantic_layer(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    semantic_root = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "trace" / "semantic" / SLUG
    (semantic_root / "semantic-contract.json").unlink()

    scorecard = build_release_scorecard(tmp_path, version=VERSION)

    assert scorecard["release_ready"] is False
    assert scorecard["semantic"]["reason_code"] == "semantic_contract_missing"
    assert "semantic_contract_missing" in scorecard["delivery_read_model"]["risk_flags"]
    assert "semantic_contract_missing" in scorecard["host_native_delivery"]["reason_codes"]


def test_v136_release_scorecard_should_block_release_when_default_taste_bridge_drifts(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _seed_semantic_layer(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    semantic_contract = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "trace" / "semantic" / SLUG / "semantic-contract.json"
    payload = json.loads(semantic_contract.read_text(encoding="utf-8"))
    payload["default_design_bridge"]["repo"] = "https://example.com/not-official"
    semantic_contract.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    scorecard = build_release_scorecard(tmp_path, version=VERSION)

    assert scorecard["release_ready"] is False
    assert scorecard["semantic"]["reason_code"] == "semantic_default_taste_bridge_drift"
    assert "semantic_default_taste_bridge_drift" in scorecard["delivery_read_model"]["risk_flags"]


def test_v136_help_should_route_to_prototype_when_semantic_contract_missing(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _enable_prototype_requirement(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert "semantic_contract_missing" in payload["blocking_reasons"]
    assert payload["next_step"]["action"] == "prototype"
    assert payload["next_step"]["command"] == f"beacon prototype create {json.dumps(FEATURE, ensure_ascii=False)} --project {tmp_path} --version {VERSION} --json"


def test_v136_help_should_route_to_prototype_review_when_semantic_review_missing(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _seed_semantic_layer(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    semantic_review = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "trace" / "semantic" / SLUG / "semantic-review.json"
    payload = json.loads(semantic_review.read_text(encoding="utf-8"))
    payload["overall_status"] = "draft"
    semantic_review.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    help_payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert "semantic_review_missing" in help_payload["blocking_reasons"]
    assert help_payload["next_step"]["action"] == "prototype-review"
    assert help_payload["next_step"]["command"] == f"beacon prototype review {json.dumps(FEATURE, ensure_ascii=False)} --project {tmp_path} --version {VERSION} --json"


def test_v136_help_should_not_route_to_release_when_accepted_revision_is_semantic_blocked(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _enable_prototype_requirement(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    revision_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{SLUG}.revision.json"
    revision_state = json.loads(revision_path.read_text(encoding="utf-8"))
    revision_state["delivery_status"] = "accepted"
    write_json(revision_path, revision_state)

    help_payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert "semantic_contract_missing" in help_payload["blocking_reasons"]
    assert help_payload["next_step"]["action"] == "prototype"
    assert "beacon prototype create" in help_payload["next_step"]["command"]


def test_v136_help_should_not_block_on_missing_user_story_when_authoritative_scorecard_is_ready(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_execution_state(tmp_path)
    _seed_semantic_layer(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    revision_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{SLUG}.revision.json"
    revision_state = json.loads(revision_path.read_text(encoding="utf-8"))
    revision_state["delivery_status"] = "accepted"
    write_json(revision_path, revision_state)

    help_payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert "missing_user_story" not in help_payload["blocking_reasons"]


def test_v136_feature_aware_qa_up_to_date_should_emit_delivery_contract(tmp_path: Path, monkeypatch) -> None:
    matrix_path = tmp_path / ".beacon" / "qa" / "features" / "feature" / "matrix.qa9.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text('{"entries":[]}\n', encoding="utf-8")
    captured: dict[str, object] = {}
    manifest_capture: dict[str, object] = {}

    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {"runner_type": "browser-use"})
    monkeypatch.setattr(
        qa_command,
        "build_feature_qa_plan",
        lambda *args, **kwargs: {
            "schema_version": "1.0",
            "feature": "Beacon Feature",
            "feature_slug": "feature",
            "version": VERSION,
            "status": "up_to_date",
            "implementation_done": True,
            "implementation_run_id": "impl-run-1",
        },
    )
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_implement_to_qa_handoff", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        qa_command,
        "load_feature_qa_status",
        lambda *_args, **_kwargs: {
            "status": "passed",
            "execution_mode": "feature-aware",
            "release_ready": True,
            "reason_codes": ["previous_feature_qa_not_passed"],
        },
    )
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(
        qa_command,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: captured.update({"payload": payload}) or (tmp_path / "feature-status.json"),
    )
    monkeypatch.setattr(qa_command, "load_qa_status", lambda *_args, **_kwargs: {"run_id": "impl-run-1"})
    monkeypatch.setattr(
        qa_command,
        "_update_evidence_manifest",
        lambda _project_root, refs, run_id, version: manifest_capture.update(
            {"refs": list(refs), "run_id": run_id, "version": version}
        ),
    )

    exit_code, payload = qa_command._run_feature_aware_qa(
        ["Beacon Feature", "--project", str(tmp_path), "--version", VERSION, "--json"]
    )

    assert exit_code == 0
    assert payload["delivery_contract"]["host_runtime"] == "codex"
    assert payload["host_native_delivery"]["execution_mode"] == "feature-aware"
    assert captured["payload"]["delivery_contract"]["runner"] == "browser-use"
    assert captured["payload"]["reason_codes"] == []
    assert ".beacon/qa/features/beacon-feature/plan.json" in manifest_capture["refs"]


def test_v136_repair_package_should_synthesize_execution_governance_artifacts(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    result = repair_v115_delivery_package(tmp_path, version=VERSION, apply=True)
    audit = build_delivery_audit(tmp_path, version=VERSION)
    checks = {
        item.get("name"): item
        for item in audit.get("checks", [])
        if isinstance(item, dict) and item.get("name")
    }

    assert result["governance"]
    assert (tmp_path / "docs" / "beacon" / VERSION / "execution" / "boundaries.md").exists()
    assert (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "config.json").exists()
    assert (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "delivery-manifest.json").exists()
    assert audit["status"] in {"pass", "warn"}
    assert checks["execution_required_files_present"]["status"] == "pass"
    assert checks["execution_config_schema"]["status"] == "pass"
    assert checks["execution_source_schema"]["status"] == "pass"
    assert checks["change_impact_schema_and_closure"]["status"] == "pass"
    assert checks["delivery_manifest_schema"]["status"] == "pass"


def test_v136_repair_package_should_prefer_latest_frozen_revision_feature_for_governance(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_feature_docs(tmp_path, slug=OTHER_SLUG)
    freeze_revision_state(tmp_path, version=VERSION, feature=OTHER_FEATURE)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    result = repair_v115_delivery_package(tmp_path, version=VERSION, apply=True)

    assert result["governance"]
    assert all(item["source"] == f"workflow_governance:{FEATURE}" for item in result["governance"])


def test_v136_repair_package_should_rewrite_governance_when_existing_feature_mismatches_latest_revision(
    tmp_path: Path,
) -> None:
    _seed_docs(tmp_path)
    _seed_feature_docs(tmp_path, slug=OTHER_SLUG)
    freeze_revision_state(tmp_path, version=VERSION, feature=OTHER_FEATURE)
    repair_v115_delivery_package(tmp_path, version=VERSION, apply=True)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)

    result = repair_v115_delivery_package(tmp_path, version=VERSION, apply=True)
    source_payload = json.loads(
        (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "source.json").read_text(encoding="utf-8")
    )

    assert result["governance"]
    assert all(item["action"] == "rewritten" for item in result["governance"])
    assert source_payload["feature"] == FEATURE
