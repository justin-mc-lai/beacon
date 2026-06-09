"""Full-range QA acceptance contracts for Beacon v1.4.10."""

from __future__ import annotations

import re
from typing import Any

from beacon.utils.qa_attribution import route_for_failure_family
from beacon.utils.qa9 import QA9_TYPES, normalize_qa_type


NON_BROWSER_QA_LAYERS: tuple[str, ...] = (
    "unit",
    "interface",
    "contract",
    "integration",
    "smoke",
    "functional",
    "regression",
    "exception",
    "compatibility",
)

BROWSER_QA_LAYER = "browser_e2e"

FULL_QA_LAYERS: tuple[str, ...] = (*NON_BROWSER_QA_LAYERS, BROWSER_QA_LAYER)

QA_PROFILES: dict[str, tuple[str, ...]] = {
    "basic": ("unit", "contract", "smoke"),
    "complete": NON_BROWSER_QA_LAYERS,
    "closure": NON_BROWSER_QA_LAYERS,
    "browser": (*NON_BROWSER_QA_LAYERS, BROWSER_QA_LAYER),
}

BROWSER_EVIDENCE_AXES: tuple[str, ...] = (
    "function",
    "ui",
    "ux",
    "compatibility",
    "session",
    "state_data",
)

BROWSER_RUNNER_REGISTRY: tuple[str, ...] = (
    "playwright",
    "playwright-cli",
    "playwright-cdp",
    "browser-use",
    "agent-browser",
    "attached-browser",
    "web-access",
    "obscura-cdp",
)

NON_ACCEPTANCE_EVIDENCE_KINDS: tuple[str, ...] = (
    "listing",
    "placeholder",
    "documentation_only",
    "dry_run",
)

FAILURE_ATTRIBUTION_ROUTES: dict[str, str] = {
    "product_bug": "beacon-implement",
    "implementation_gap": "beacon-implement",
    "test_script_bug": "beacon-test-case",
    "environment_blocker": "beacon-qa",
    "auth_session_blocker": "beacon-qa",
    "runner_admission_blocker": "blocked",
    "coverage_gap": "beacon-test-case",
    "truth_drift": "beacon-change",
    "evidence_insufficient": "beacon-qa",
}

PLACEHOLDER_EVIDENCE_TOKENS: tuple[str, ...] = (
    "placeholder",
    "task-only",
    "fallback-no-task",
    "missing-task",
    "documentation-only",
    "doc-only",
)


def normalize_qa_acceptance_layer(value: str | None) -> str:
    raw = str(value or "").strip().lower().replace("-", "_")
    if raw in {"browser", "browser_e2e", "browser_e2e_test", "e2e", "browser-e2e"}:
        return BROWSER_QA_LAYER
    normalized = normalize_qa_type(raw).replace("-", "_")
    if normalized in FULL_QA_LAYERS:
        return normalized
    if raw == "api_curl":
        return "interface"
    return normalized


def validate_qa_layer_taxonomy(layers: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    requested = [normalize_qa_acceptance_layer(item) for item in (layers or FULL_QA_LAYERS)]
    unknown = sorted({item for item in requested if item not in FULL_QA_LAYERS})
    return {
        "schema_version": "1.0",
        "status": "blocked" if unknown else "pass",
        "blocked": bool(unknown),
        "full_layers": list(FULL_QA_LAYERS),
        "non_browser_layers": list(NON_BROWSER_QA_LAYERS),
        "browser_layer": BROWSER_QA_LAYER,
        "qa9_layers": list(QA9_TYPES),
        "requested_layers": requested,
        "unknown_layers": unknown,
    }


def required_layers_for_profile(profile: str, *, browser_required: bool = False) -> list[str]:
    profile_key = str(profile or "complete").strip().lower().replace("_", "-")
    required = list(QA_PROFILES.get(profile_key, QA_PROFILES["complete"]))
    if browser_required and BROWSER_QA_LAYER not in required:
        required.append(BROWSER_QA_LAYER)
    return required


def build_qa_profile_completeness(
    *,
    profile: str,
    required_layers: list[str] | None = None,
    executed_layers: list[str] | None = None,
    skipped_layers: list[str] | None = None,
    blocked_layers: list[str] | None = None,
    not_applicable_layers: dict[str, str] | None = None,
    browser_required: bool = False,
) -> dict[str, Any]:
    required = [
        item
        for item in (normalize_qa_acceptance_layer(layer) for layer in (required_layers or required_layers_for_profile(profile, browser_required=browser_required)))
        if item in FULL_QA_LAYERS
    ]
    executed = sorted({normalize_qa_acceptance_layer(layer) for layer in (executed_layers or []) if normalize_qa_acceptance_layer(layer) in FULL_QA_LAYERS})
    skipped = sorted({normalize_qa_acceptance_layer(layer) for layer in (skipped_layers or []) if normalize_qa_acceptance_layer(layer) in FULL_QA_LAYERS})
    blocked = sorted({normalize_qa_acceptance_layer(layer) for layer in (blocked_layers or []) if normalize_qa_acceptance_layer(layer) in FULL_QA_LAYERS})
    na_reasons = {
        normalize_qa_acceptance_layer(layer): str(reason or "").strip()
        for layer, reason in (not_applicable_layers or {}).items()
        if normalize_qa_acceptance_layer(layer) in FULL_QA_LAYERS
    }
    satisfied = set(executed) | {layer for layer, reason in na_reasons.items() if reason}
    missing = sorted(layer for layer in required if layer not in satisfied and layer not in blocked)
    not_applicable = sorted(layer for layer in required if layer in na_reasons and na_reasons[layer])
    partial = bool(missing or blocked or skipped)
    return {
        "schema_version": "1.0",
        "profile": str(profile or "complete").strip().lower() or "complete",
        "browser_required": bool(browser_required),
        "required_layers": required,
        "executed_layers": executed,
        "skipped_layers": skipped,
        "blocked_layers": blocked,
        "not_applicable_layers": not_applicable,
        "not_applicable_reasons": na_reasons,
        "missing_layers": missing,
        "is_complete": not partial,
        "partial": partial,
        "status": "complete" if not partial else "partial",
    }


def classify_evidence_kind(command: str = "", evidence_refs: list[str] | None = None, notes: str = "") -> str:
    text = " ".join([str(command or ""), str(notes or ""), " ".join(str(ref) for ref in (evidence_refs or []))]).lower()
    if re.search(r"\b(playwright|npx\s+playwright)\s+test\s+--list\b", text):
        return "listing"
    if any(token in text for token in PLACEHOLDER_EVIDENCE_TOKENS):
        return "placeholder"
    if "dry-run" in text or "dry run" in text:
        return "dry_run"
    if "passed in docs" in text or "manual note only" in text or "documentation only" in text:
        return "documentation_only"
    return "execution"


def evidence_kind_accepts(kind: str) -> bool:
    return str(kind or "").strip() not in NON_ACCEPTANCE_EVIDENCE_KINDS


def build_browser_evidence_contract(evidence: dict[str, Any] | None) -> dict[str, Any]:
    payload = evidence if isinstance(evidence, dict) else {}
    evidence_refs = [str(item).strip() for item in (payload.get("evidence_refs") or payload.get("evidence_ref") or []) if str(item).strip()]
    source_command = str(payload.get("source_command") or payload.get("command") or "").strip()
    kind = classify_evidence_kind(source_command, evidence_refs, str(payload.get("notes") or ""))
    runner = normalize_browser_runner(str(payload.get("runner") or payload.get("browser_runner") or ""))
    present_axes = sorted(
        {
            axis
            for axis in BROWSER_EVIDENCE_AXES
            if bool(payload.get(axis))
            or bool(payload.get(f"{axis}_ref"))
            or axis in {str(item).strip() for item in (payload.get("axes") or [])}
        }
    )
    missing_axes = sorted(axis for axis in BROWSER_EVIDENCE_AXES if axis not in present_axes)
    required_fields = {
        "run_id": str(payload.get("run_id") or "").strip(),
        "source_command": source_command,
        "runner": runner,
        "target": str(payload.get("target_url") or payload.get("route") or "").strip(),
        "result_status": str(payload.get("result_status") or payload.get("status") or "").strip(),
    }
    missing_fields = sorted(field for field, value in required_fields.items() if not value)
    accepted_test_ids = [str(item).strip() for item in (payload.get("accepted_test_ids") or []) if str(item).strip()]
    if not accepted_test_ids:
        missing_fields.append("accepted_test_ids")
    if not evidence_refs:
        missing_fields.append("evidence_refs")
    if runner and runner not in BROWSER_RUNNER_REGISTRY:
        missing_fields.append("registered_runner")
    valid = not missing_fields and not missing_axes and evidence_kind_accepts(kind)
    return {
        "schema_version": "1.0",
        "status": "valid" if valid else "invalid",
        "blocked": not valid,
        "runner": runner,
        "runner_registered": bool(runner and runner in BROWSER_RUNNER_REGISTRY),
        "browser_runner_registry": list(BROWSER_RUNNER_REGISTRY),
        "evidence_kind": kind,
        "non_acceptance_evidence": not evidence_kind_accepts(kind),
        "required_fields": required_fields,
        "accepted_test_ids": accepted_test_ids,
        "evidence_refs": evidence_refs,
        "present_axes": present_axes,
        "missing_axes": missing_axes,
        "missing_fields": sorted(set(missing_fields)),
    }


def normalize_browser_runner(value: str) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    if raw in {"attached-chrome", "attached-browser", "chrome-cdp"}:
        return "attached-browser" if raw == "attached-browser" else raw
    if raw in {"playwright-cli-cdp", "playwright-attach", "playwright-cdp"}:
        return "playwright-cdp"
    if raw in {"obscura", "obscura-cdp"}:
        return "obscura-cdp"
    return raw


def bind_project_e2e_script(
    *,
    command: str,
    ac_ids: list[str] | None = None,
    test_ids: list[str] | None = None,
    report_refs: list[str] | None = None,
    runner: str = "playwright",
) -> dict[str, Any]:
    evidence_kind = classify_evidence_kind(command, report_refs or [])
    missing: list[str] = []
    if not str(command or "").strip():
        missing.append("command")
    if not [item for item in (ac_ids or []) if str(item).strip()]:
        missing.append("ac_ids")
    if not [item for item in (test_ids or []) if str(item).strip()]:
        missing.append("test_ids")
    return {
        "schema_version": "1.0",
        "status": "bound" if not missing and evidence_kind_accepts(evidence_kind) else "blocked",
        "blocked": bool(missing or not evidence_kind_accepts(evidence_kind)),
        "command": str(command or "").strip(),
        "runner": normalize_browser_runner(runner),
        "ac_ids": [str(item).strip() for item in (ac_ids or []) if str(item).strip()],
        "test_ids": [str(item).strip() for item in (test_ids or []) if str(item).strip()],
        "report_refs": [str(item).strip() for item in (report_refs or []) if str(item).strip()],
        "evidence_kind": evidence_kind,
        "missing_fields": sorted(set(missing)),
    }


def route_for_qa_failure(failure_kind: str) -> str:
    normalized = str(failure_kind or "").strip()
    if normalized in FAILURE_ATTRIBUTION_ROUTES:
        return FAILURE_ATTRIBUTION_ROUTES[normalized]
    return route_for_failure_family(normalized)


def build_qa_acceptance_transaction(
    *,
    run_id: str,
    source_commands: list[str],
    accepted_test_ids: list[str],
    evidence_refs: list[str],
    runner: str = "",
    browser: str = "",
    attributions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_commands = [str(item).strip() for item in source_commands if str(item).strip()]
    normalized_tests = [str(item).strip() for item in accepted_test_ids if str(item).strip()]
    normalized_refs = [str(item).strip() for item in evidence_refs if str(item).strip()]
    missing = []
    if not str(run_id or "").strip():
        missing.append("run_id")
    if not normalized_commands:
        missing.append("source_commands")
    if not normalized_tests:
        missing.append("accepted_test_ids")
    if not normalized_refs:
        missing.append("evidence_refs")
    if attributions is None:
        missing.append("failure_attribution")
    return {
        "schema_version": "1.0",
        "status": "recorded" if not missing else "blocked",
        "blocked": bool(missing),
        "run_id": str(run_id or "").strip(),
        "source_commands": normalized_commands,
        "accepted_test_ids": normalized_tests,
        "evidence_refs": normalized_refs,
        "runner": normalize_browser_runner(runner),
        "browser": str(browser or "").strip(),
        "failure_attribution": attributions or [],
        "missing_fields": sorted(set(missing)),
        "truth_authority": False,
        "release_pass_evidence": False,
    }


def build_release_boundary_verdict(
    *,
    formal_qa_closure: dict[str, Any] | None = None,
    raw_runner_output: dict[str, Any] | None = None,
    support_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    closure = formal_qa_closure if isinstance(formal_qa_closure, dict) else {}
    formal_ready = bool(closure.get("release_ready")) and str(closure.get("continue_decision") or "") == "ready_for_release"
    raw_claim = bool(raw_runner_output and raw_runner_output.get("passed"))
    support_claim = bool(support_evidence and support_evidence.get("passed"))
    return {
        "schema_version": "1.0",
        "status": "pass" if formal_ready else "blocked",
        "blocked": not formal_ready,
        "formal_qa_source": "feature_qa_scorecard" if closure else "",
        "raw_runner_output_ignored": raw_claim,
        "support_evidence_ignored": support_claim,
        "release_pass_evidence": formal_ready,
    }


def build_qa_acceptance_capability_summary(
    *,
    profile: str = "complete",
    required_layers: list[str] | None = None,
    browser_required: bool = False,
    executed_layers: list[str] | None = None,
    blocked_layers: list[str] | None = None,
    not_applicable_layers: dict[str, str] | None = None,
    browser_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    taxonomy = validate_qa_layer_taxonomy(required_layers or None)
    completeness = build_qa_profile_completeness(
        profile=profile,
        required_layers=required_layers,
        executed_layers=executed_layers or [],
        blocked_layers=blocked_layers or [],
        not_applicable_layers=not_applicable_layers or {},
        browser_required=browser_required,
    )
    browser_contract = build_browser_evidence_contract(browser_evidence) if browser_required else {"status": "not_required", "blocked": False}
    blocked = bool(taxonomy["blocked"] or completeness["partial"] or browser_contract.get("blocked"))
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "taxonomy": taxonomy,
        "profile_completeness": completeness,
        "browser_evidence_contract": browser_contract,
        "browser_runner_registry": list(BROWSER_RUNNER_REGISTRY),
        "non_acceptance_evidence_kinds": list(NON_ACCEPTANCE_EVIDENCE_KINDS),
        "failure_attribution_routes": dict(FAILURE_ATTRIBUTION_ROUTES),
        "truth_authority": False,
        "release_pass_evidence": False,
    }
