from __future__ import annotations

from beacon.utils.qa_acceptance import (
    BROWSER_RUNNER_REGISTRY,
    FULL_QA_LAYERS,
    NON_BROWSER_QA_LAYERS,
    bind_project_e2e_script,
    build_browser_evidence_contract,
    build_qa_acceptance_capability_summary,
    build_qa_acceptance_transaction,
    build_qa_profile_completeness,
    build_release_boundary_verdict,
    classify_evidence_kind,
    route_for_qa_failure,
    validate_qa_layer_taxonomy,
)
from beacon.utils.qa_feature import _resolve_entry_command
from beacon.utils.qa_feature import _qa_runtime_taxonomy


def test_qa_layer_taxonomy() -> None:
    payload = validate_qa_layer_taxonomy(list(FULL_QA_LAYERS))

    assert payload["status"] == "pass"
    assert payload["full_layers"] == [
        "unit",
        "interface",
        "contract",
        "integration",
        "smoke",
        "functional",
        "regression",
        "exception",
        "compatibility",
        "browser_e2e",
    ]

    blocked = validate_qa_layer_taxonomy(["unit", "unknown-layer"])
    assert blocked["blocked"] is True
    assert blocked["unknown_layers"] == ["unknown_layer"]


def test_qa_profiles_report_completeness() -> None:
    payload = build_qa_profile_completeness(
        profile="browser",
        executed_layers=list(FULL_QA_LAYERS),
        browser_required=True,
    )

    assert payload["status"] == "complete"
    assert payload["partial"] is False
    assert payload["required_layers"] == list(FULL_QA_LAYERS)
    assert payload["blocked_layers"] == []
    assert payload["not_applicable_layers"] == []


def test_human_selected_commands_are_partial_until_complete() -> None:
    payload = build_qa_profile_completeness(
        profile="closure",
        executed_layers=["unit", "contract"],
        browser_required=False,
    )

    assert payload["status"] == "partial"
    assert payload["partial"] is True
    assert "integration" in payload["missing_layers"]
    assert "compatibility" in payload["missing_layers"]


def test_non_browser_features_require_applicable_full_range() -> None:
    partial = build_qa_profile_completeness(
        profile="closure",
        executed_layers=["unit", "interface", "contract"],
        browser_required=False,
    )
    assert partial["partial"] is True

    complete = build_qa_profile_completeness(
        profile="closure",
        executed_layers=list(NON_BROWSER_QA_LAYERS),
        browser_required=False,
    )
    assert complete["status"] == "complete"


def test_browser_features_require_function_ui_ux_evidence() -> None:
    evidence = {
        "run_id": "run-browser-001",
        "source_command": "npx playwright test tests/e2e/create-match.spec.ts",
        "runner": "playwright",
        "target_url": "http://localhost:3000/matches",
        "result_status": "passed",
        "accepted_test_ids": ["TC-QA-FULL-005"],
        "evidence_refs": [
            "playwright-report/results.json",
            "test-results/create-match/function-screenshot.png",
            "test-results/create-match/ui-screenshot.png",
            "test-results/create-match/ux-trace.zip",
            "test-results/create-match/compatibility-chromium.json",
            "test-results/create-match/session-storage-state.json",
            "test-results/create-match/state_data-network.json",
        ],
        "axes": ["function", "ui", "ux", "compatibility", "session", "state_data"],
    }

    payload = build_browser_evidence_contract(evidence)

    assert payload["status"] == "valid"
    assert payload["missing_axes"] == []
    assert payload["runner_registered"] is True


def test_project_e2e_scripts_bind_to_ac_test_ids() -> None:
    payload = bind_project_e2e_script(
        command="npx playwright test tests/e2e/create-match.spec.ts --reporter=json",
        ac_ids=["AC-006"],
        test_ids=["TC-QA-FULL-006"],
        report_refs=["playwright-report/results.json"],
        runner="playwright-cli",
    )

    assert payload["status"] == "bound"
    assert payload["ac_ids"] == ["AC-006"]
    assert payload["test_ids"] == ["TC-QA-FULL-006"]


def test_browser_runner_registry_contains_supported_candidates() -> None:
    assert set(BROWSER_RUNNER_REGISTRY) == {
        "playwright",
        "playwright-cli",
        "playwright-cdp",
        "browser-use",
        "agent-browser",
        "attached-browser",
        "web-access",
        "obscura-cdp",
    }


def test_listing_and_placeholder_evidence_cannot_pass() -> None:
    assert classify_evidence_kind("npx playwright test --list", []) == "listing"

    payload = build_browser_evidence_contract(
        {
            "run_id": "run-x",
            "source_command": "npx playwright test --list",
            "runner": "playwright",
            "target_url": "http://localhost:3000",
            "result_status": "passed",
            "accepted_test_ids": ["TC-QA-FULL-008"],
            "evidence_refs": ["playwright-list.txt"],
            "axes": ["function", "ui", "ux", "compatibility", "session", "state_data"],
        }
    )

    assert payload["blocked"] is True
    assert payload["evidence_kind"] == "listing"
    assert payload["non_acceptance_evidence"] is True


def test_placeholder_named_pytest_selector_remains_executable_command() -> None:
    command = (
        'python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py '
        '-k "listing_and_placeholder_evidence_cannot_pass"'
    )

    resolved = _resolve_entry_command(
        qa_type="contract",
        command=command,
        ui_runner="playwright",
    )

    assert resolved == command
    assert "pytest -q -k contract" not in resolved


def test_acceptance_transaction_records_executable_evidence() -> None:
    payload = build_qa_acceptance_transaction(
        run_id="run-qa-001",
        source_commands=["npx playwright test tests/e2e/create-match.spec.ts"],
        runner="playwright",
        browser="chromium",
        accepted_test_ids=["TC-QA-FULL-009"],
        evidence_refs=["playwright-report/results.json", "test-results/trace.zip"],
        attributions=[],
    )

    assert payload["status"] == "recorded"
    assert payload["truth_authority"] is False
    assert payload["release_pass_evidence"] is False


def test_missing_browser_evidence_blocks_release() -> None:
    payload = build_qa_acceptance_capability_summary(
        profile="browser",
        browser_required=True,
        executed_layers=list(NON_BROWSER_QA_LAYERS),
        browser_evidence={},
    )

    assert payload["blocked"] is True
    assert payload["browser_evidence_contract"]["status"] == "invalid"
    assert "browser_e2e" in payload["profile_completeness"]["missing_layers"]


def test_qa_failure_attribution_routes_deterministically() -> None:
    assert route_for_qa_failure("product_bug") == "beacon-implement"
    assert route_for_qa_failure("implementation_gap") == "beacon-implement"
    assert route_for_qa_failure("test_script_bug") == "beacon-test-case"
    assert route_for_qa_failure("environment_blocker") == "beacon-qa"
    assert route_for_qa_failure("auth_session_blocker") == "beacon-qa"
    assert route_for_qa_failure("runner_admission_blocker") == "blocked"
    assert route_for_qa_failure("coverage_gap") == "beacon-test-case"
    assert route_for_qa_failure("truth_drift") == "beacon-change"


def test_non_browser_taxonomy_text_does_not_create_auth_blocker() -> None:
    payload = {
        "qa9": {
            "tc_results": [
                {
                    "tc_id": "TC-001",
                    "status": "blocked",
                    "qa_type": "contract",
                    "browser_required": False,
                    "reason_code": "coverage_gap",
                    "stdout": "stable taxonomy includes auth_session_blocked as a known class",
                }
            ]
        }
    }

    taxonomy = _qa_runtime_taxonomy(payload)

    assert taxonomy["primary_class"] == "coverage_gap"
    assert "auth_session_blocked" not in taxonomy["failure_classes"]


def test_release_consumes_formal_qa_closure_only() -> None:
    blocked = build_release_boundary_verdict(
        formal_qa_closure={},
        raw_runner_output={"passed": True},
        support_evidence={"passed": True},
    )
    assert blocked["blocked"] is True
    assert blocked["raw_runner_output_ignored"] is True
    assert blocked["support_evidence_ignored"] is True

    passed = build_release_boundary_verdict(
        formal_qa_closure={"release_ready": True, "continue_decision": "ready_for_release"},
        raw_runner_output={"passed": False},
        support_evidence={"passed": False},
    )
    assert passed["status"] == "pass"
