"""Shared delivery contract and read-model helpers for Beacon v1.3.6."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import execution_file_candidates
from beacon.utils.host_prompt_trace import load_host_prompt_trace
from beacon.utils.implement_prompt_boundary import evaluate_implement_prompt_boundary
from beacon.utils.implement_prompt_boundary import implement_prompt_boundary_supported
from beacon.utils.qa_feature import load_feature_qa_status
from beacon.utils.runtime import read_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def _clean_str(value: Any) -> str:
    return str(value or "").strip()


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _clean_str(value)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _clean_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _readiness_status(prechecks: dict[str, Any], key: str) -> str:
    check = _clean_dict(prechecks.get(key))
    return _clean_str(check.get("status"))


def build_execution_capability_snapshot(
    *,
    host_runtime: str,
    subagent_prechecks: dict[str, Any] | None,
    base_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    snapshot = dict(_clean_dict(base_snapshot))
    prechecks = _clean_dict(subagent_prechecks)
    runtime_status = _readiness_status(prechecks, "runtime_readiness")
    delegation_status = _readiness_status(prechecks, "delegation_readiness")
    snapshot.setdefault("schema_version", "1.0")
    snapshot["host_runtime"] = _clean_str(
        host_runtime or snapshot.get("host_runtime") or prechecks.get("host_runtime")
    )
    snapshot["subagent_required"] = bool(prechecks.get("required", False))
    snapshot["subagent_runtime_status"] = runtime_status or _clean_str(snapshot.get("subagent_runtime_status"))
    snapshot["subagent_delegation_status"] = delegation_status or _clean_str(
        snapshot.get("subagent_delegation_status")
    )
    snapshot["host_semantic_ready"] = bool(snapshot.get("host_semantic_ready", False))
    snapshot["provider_available"] = bool(snapshot.get("provider_available", False))
    return snapshot


def build_delivery_contract(
    *,
    feature: str,
    version: str,
    requested_mode: str = "",
    effective_mode: str = "",
    execution_mode: str = "",
    generator_mode: str = "",
    runner_mode: str = "",
    host_runtime: str = "",
    fallback_reason: str = "",
    capability_snapshot: dict[str, Any] | None = None,
    subagent_prechecks: dict[str, Any] | None = None,
    requirement_binding: dict[str, Any] | None = None,
    traceability_refs: list[str] | None = None,
    runner: str = "",
    adapter_type: str = "",
    execution_surface: str = "",
    team_mode: bool | None = None,
    qa_status: str = "",
    gate_status: str = "",
    release_ready: bool | None = None,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    prechecks = _clean_dict(subagent_prechecks)
    snapshot = build_execution_capability_snapshot(
        host_runtime=host_runtime,
        subagent_prechecks=prechecks,
        base_snapshot=capability_snapshot,
    )
    risk_list = _clean_list(risk_flags or [])
    if _readiness_status(prechecks, "runtime_readiness") not in {"", "pass"}:
        risk_list.append("runtime_not_ready")
    if _readiness_status(prechecks, "delegation_readiness") not in {"", "pass"}:
        risk_list.append("delegation_not_ready")
    if _clean_str(fallback_reason):
        risk_list.append(_clean_str(fallback_reason))
    return {
        "schema_version": "1.0",
        "feature": _clean_str(feature),
        "version": _clean_str(version),
        "requested_mode": _clean_str(requested_mode),
        "effective_mode": _clean_str(effective_mode or execution_mode),
        "generator_mode": _clean_str(generator_mode or effective_mode or execution_mode),
        "execution_mode": _clean_str(execution_mode or effective_mode),
        "runner_mode": _clean_str(runner_mode or runner or adapter_type),
        "host_runtime": _clean_str(host_runtime or snapshot.get("host_runtime")),
        "fallback_reason": _clean_str(fallback_reason),
        "capability_snapshot": snapshot,
        "subagent_prechecks": prechecks,
        "requirement_binding": _clean_dict(requirement_binding),
        "traceability_refs": _clean_list(traceability_refs or []),
        "runner": _clean_str(runner),
        "adapter_type": _clean_str(adapter_type),
        "execution_surface": _clean_str(execution_surface),
        "team_mode": bool(team_mode) if team_mode is not None else False,
        "qa_status": _clean_str(qa_status),
        "gate_status": _clean_str(gate_status),
        "release_ready": bool(release_ready) if release_ready is not None else False,
        "risk_flags": _clean_list(risk_list),
    }


def build_surface_explanation(
    *,
    delivery_contract: dict[str, Any],
    selected_surface: str,
    blocked: bool,
    blocking_reasons: list[str] | None = None,
    diagnostics_status: str = "",
    next_action: str = "",
    next_command: str = "",
    fallback_allowed: bool = False,
    fallback_reason_code: str = "",
) -> dict[str, Any]:
    contract = _clean_dict(delivery_contract)
    snapshot = _clean_dict(contract.get("capability_snapshot"))
    reasons = _clean_list(blocking_reasons or [])
    runtime_status = _clean_str(snapshot.get("subagent_runtime_status"))
    delegation_status = _clean_str(snapshot.get("subagent_delegation_status"))
    primary_reason = reasons[0] if reasons else _clean_str(fallback_reason_code)
    risk_level = "blocked" if blocked else "warn" if any(
        status not in {"", "pass"} for status in (runtime_status, delegation_status)
    ) else "ok"
    return {
        "capability": {
            "selected_surface": _clean_str(selected_surface),
            "host_runtime": _clean_str(contract.get("host_runtime")),
            "subagent_runtime_status": runtime_status,
            "subagent_delegation_status": delegation_status,
            "summary": (
                f"Using {_clean_str(selected_surface) or 'native-default'} via "
                f"{_clean_str(contract.get('host_runtime')) or 'unknown-host'} runtime."
            ),
        },
        "fallback": {
            "allowed": bool(fallback_allowed),
            "reason_code": _clean_str(fallback_reason_code or contract.get("fallback_reason")),
            "target_action": _clean_str(next_action),
            "target_command": _clean_str(next_command),
            "summary": (
                "Fallback remains available through the native/default execution path."
                if fallback_allowed
                else "No fallback surface is currently available without clearing blockers."
            ),
        },
        "risk": {
            "level": risk_level,
            "primary_reason_code": primary_reason,
            "workflow_reason_codes": reasons,
            "diagnostic_status": _clean_str(diagnostics_status),
            "diagnostic_codes": _clean_list(contract.get("risk_flags")),
            "summary": (
                f"Workflow is blocked by {primary_reason}."
                if blocked and primary_reason
                else "Workflow is runnable with current capability checks."
            ),
        },
    }


def _load_latest_implement_state(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    root = project_root / ".beacon" / "implement"
    if not root.exists():
        return {}
    slug = feature_slug(feature)
    candidates: list[tuple[str, dict[str, Any]]] = []
    for state_path in sorted(root.glob("*/state.json"), reverse=True):
        payload = read_json(state_path, {})
        if not isinstance(payload, dict):
            continue
        if _clean_str(payload.get("feature_slug")) != slug:
            continue
        payload_version = _clean_str(payload.get("version"))
        if payload_version and payload_version != version:
            continue
        key = _clean_str(payload.get("generated_at")) or state_path.parent.name
        candidates.append((key, payload))
    if not candidates:
        return {}
    return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def _load_authoritative_implementation_summary(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    slug = feature_slug(feature)
    for path in execution_file_candidates(project_root, version, f"implementation-summary-{slug}.json"):
        payload = read_json(path, {})
        if isinstance(payload, dict) and payload:
            return payload
    return {}


def _merge_implement_state(authoritative: dict[str, Any], runtime_state: dict[str, Any]) -> dict[str, Any]:
    summary = _clean_dict(authoritative)
    runtime = _clean_dict(runtime_state)
    if not summary:
        return runtime
    if not runtime:
        return summary

    merged = dict(summary)
    for key, value in runtime.items():
        if key in {"prompt_boundary", "delivery_contract", "requirement_traceability", "traceability_refs"}:
            if not merged.get(key):
                merged[key] = value
            continue
        if key in {"status", "run_id", "request_path", "result_path", "stdout_path", "stderr_path", "reason_code", "generated_at"}:
            if _clean_str(value):
                merged[key] = value
            continue
        if key in {"plan_preflight", "branch_preflight", "subagent_prechecks", "semantic_layer", "host_native_delivery"}:
            if value:
                merged[key] = value
            continue
        if key in {"mode", "host_runtime", "runner", "adapter_type", "phase", "next_action", "team_surface"}:
            if _clean_str(value):
                merged[key] = value
            continue
        if key not in merged:
            merged[key] = value
    return merged


def _default_requirement_binding(payload: dict[str, Any]) -> dict[str, Any]:
    binding = _clean_dict(payload.get("requirement_traceability"))
    if binding:
        return binding
    return _clean_dict(payload.get("requirement_binding"))


def _default_traceability_refs(payload: dict[str, Any]) -> list[str]:
    refs = _clean_list(payload.get("traceability_refs"))
    requirement_binding = _default_requirement_binding(payload)
    for key in ("prd", "user_story", "test_case", "ac_matrix"):
        value = _clean_str(requirement_binding.get(key))
        if value:
            refs.append(value)
    return _clean_list(refs)


def _normalize_prompt_boundary(payload: dict[str, Any] | None, *, version: str) -> dict[str, Any]:
    required = implement_prompt_boundary_supported(version)
    raw = _clean_dict(payload)
    normalized = {
        "required": required,
        "status": "not_required" if not required else "missing",
        "blocked": False if not required else True,
        "classification": "",
        "reason_code": "",
        "next_action": "",
        "recommended_command": "",
        "surface": "",
        "prompt": "",
        "matched_signals": [],
    }
    if not required:
        return normalized
    if not raw:
        normalized["reason_code"] = "implement_prompt_boundary_missing"
        return normalized

    classification = _clean_str(raw.get("classification"))
    blocked = bool(raw.get("blocked", False))
    status = _clean_str(raw.get("status")) or ("blocked" if blocked else "pass")
    reason_code = _clean_str(raw.get("reason_code"))
    allowed_classes = {"in_scope_implementation", "clarification_within_scope"}
    if classification and classification not in allowed_classes and not blocked:
        blocked = True
        status = "blocked"
        reason_code = reason_code or "implement_prompt_boundary_invalid"

    normalized.update(
        {
            "status": status or ("blocked" if blocked else "pass"),
            "blocked": blocked,
            "classification": classification,
            "reason_code": reason_code or ("implement_prompt_boundary_missing" if not classification else ""),
            "next_action": _clean_str(raw.get("next_action")),
            "recommended_command": _clean_str(raw.get("recommended_command")),
            "surface": _clean_str(raw.get("surface")) or "host_prompt",
            "prompt": _clean_str(raw.get("prompt")),
            "matched_signals": _clean_list(raw.get("matched_signals")),
        }
    )
    return normalized


def _resolve_prompt_boundary(
    project_root: Path,
    *,
    version: str,
    feature: str,
    implement_state: dict[str, Any],
) -> dict[str, Any]:
    prompt_boundary = _normalize_prompt_boundary(implement_state.get("prompt_boundary"), version=version)
    if not bool(prompt_boundary.get("required", False)):
        return prompt_boundary
    prompt = _clean_str(prompt_boundary.get("prompt"))
    if prompt:
        return prompt_boundary

    host_trace = load_host_prompt_trace(project_root, version=version, feature=feature)
    latest_event = host_trace.get("latest_event") if isinstance(host_trace.get("latest_event"), dict) else {}
    host_prompt = _clean_str(latest_event.get("original_host_prompt"))
    if not host_prompt:
        return prompt_boundary

    reevaluated = evaluate_implement_prompt_boundary(
        project_root,
        version=version,
        feature=feature,
        host_prompt=host_prompt,
    )
    if not isinstance(reevaluated, dict) or not reevaluated:
        return prompt_boundary
    reevaluated["surface"] = _clean_str(latest_event.get("surface")) or _clean_str(prompt_boundary.get("surface")) or "host_prompt_trace"
    return _normalize_prompt_boundary(reevaluated, version=version)


def build_delivery_read_model(
    *,
    feature: str,
    version: str,
    project_root: Path | None = None,
    implement_payload: dict[str, Any] | None = None,
    qa_payload: dict[str, Any] | None = None,
    release_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    implement_state = _clean_dict(implement_payload)
    qa_state = _clean_dict(qa_payload)
    release_state = _clean_dict(release_payload)

    implement_contract = _clean_dict(implement_state.get("delivery_contract"))
    if not implement_contract and implement_state:
        implement_contract = build_delivery_contract(
            feature=feature or _clean_str(implement_state.get("feature")),
            version=version or _clean_str(implement_state.get("version")),
            requested_mode=_clean_str(implement_state.get("mode")),
            effective_mode=_clean_str(implement_state.get("mode")),
            execution_mode=_clean_str(implement_state.get("mode")),
            runner_mode=_clean_str(implement_state.get("runner")),
            host_runtime=_clean_str(implement_state.get("host_runtime")),
            capability_snapshot=_clean_dict(implement_state.get("capability_snapshot")),
            subagent_prechecks=_clean_dict(implement_state.get("subagent_prechecks")),
            requirement_binding=_default_requirement_binding(implement_state),
            traceability_refs=_default_traceability_refs(implement_state),
            runner=_clean_str(implement_state.get("runner")),
            adapter_type=_clean_str(implement_state.get("adapter_type")),
            execution_surface=_clean_str(implement_state.get("execution_surface")),
            team_mode=bool(implement_state.get("team_mode", False)),
            risk_flags=_clean_list(implement_state.get("reason_codes")) or [_clean_str(implement_state.get("reason_code"))],
        )

    qa_contract = _clean_dict(qa_state.get("delivery_contract"))
    if not qa_contract and qa_state:
        qa_contract = build_delivery_contract(
            feature=feature or _clean_str(qa_state.get("feature")),
            version=version or _clean_str(qa_state.get("version")),
            requested_mode=_clean_str(qa_state.get("execution_mode")),
            effective_mode=_clean_str(qa_state.get("execution_mode")),
            execution_mode=_clean_str(qa_state.get("execution_mode")),
            runner_mode=_clean_str(qa_state.get("execution_surface")),
            host_runtime=_clean_str(qa_state.get("host_runtime")),
            capability_snapshot=_clean_dict(qa_state.get("capability_snapshot")),
            subagent_prechecks=_clean_dict(qa_state.get("subagent_prechecks")),
            requirement_binding=_default_requirement_binding(qa_state) or _default_requirement_binding(implement_state),
            traceability_refs=_default_traceability_refs(qa_state) or _default_traceability_refs(implement_state),
            execution_surface=_clean_str(qa_state.get("execution_surface")),
            team_mode=bool(qa_state.get("team_mode", False)),
            qa_status=_clean_str(qa_state.get("status")),
            release_ready=bool(qa_state.get("release_ready", False)),
            risk_flags=_clean_list(qa_state.get("reason_codes")),
        )

    authoritative_contract = qa_contract or implement_contract
    feature_name = _clean_str(feature) or _clean_str(authoritative_contract.get("feature"))
    resolved_version = _clean_str(version) or _clean_str(authoritative_contract.get("version"))
    release_ready = bool(release_state.get("release_ready", qa_contract.get("release_ready", False)))
    gate = _clean_dict(release_state.get("gate"))
    qa_release = _clean_dict(release_state.get("qa"))
    semantic = _clean_dict(release_state.get("semantic"))
    revision_binding = _clean_dict(release_state.get("revision_binding"))
    prompt_boundary = (
        _resolve_prompt_boundary(
            project_root,
            version=resolved_version,
            feature=feature_name,
            implement_state=implement_state,
        )
        if project_root is not None
        else _normalize_prompt_boundary(implement_state.get("prompt_boundary"), version=resolved_version)
    )
    risk_flags = _clean_list(authoritative_contract.get("risk_flags"))
    risk_flags.extend(_clean_list(release_state.get("risk_flags")))
    if qa_state and _clean_str(qa_state.get("status")).lower() not in {"", "passed"}:
        risk_flags.append("qa_not_ready")
    if semantic and _clean_str(semantic.get("status")).lower() not in {"", "pass"}:
        risk_flags.append(_clean_str(semantic.get("reason_code")) or "semantic_not_ready")
    if release_state and not release_ready:
        risk_flags.append("release_not_ready")
    if revision_binding and not bool(revision_binding.get("gate_bound_to_latest_revision", False)):
        risk_flags.append(_clean_str(revision_binding.get("reason_code")) or "revision_not_bound")
    if prompt_boundary.get("required") and (
        bool(prompt_boundary.get("blocked", False))
        or _clean_str(prompt_boundary.get("status")) not in {"pass", "not_required"}
    ):
        risk_flags.append(_clean_str(prompt_boundary.get("reason_code")) or "implement_prompt_boundary_missing")

    requirement_binding = _clean_dict(authoritative_contract.get("requirement_binding"))
    requirement_refs = _clean_list(authoritative_contract.get("traceability_refs"))
    runtime_refs = _clean_list([
        _clean_str(implement_state.get("request_path")),
        _clean_str(implement_state.get("result_path")),
        _clean_str(implement_state.get("implement_to_qa_handoff")),
        _clean_str(qa_state.get("feature_matrix_path")),
        _clean_str(qa_state.get("feature_scorecard_path")),
    ])

    return {
        "schema_version": "1.0",
        "feature": feature_name,
        "version": resolved_version,
        "contract": authoritative_contract,
        "implement": {
            "status": _clean_str(implement_state.get("status")),
            "run_id": _clean_str(implement_state.get("run_id")),
            "delivery_contract": implement_contract,
            "prompt_boundary": prompt_boundary,
        },
        "qa": {
            "status": _clean_str(qa_state.get("status") or qa_release.get("status")),
            "run_id": _clean_str(qa_state.get("run_id")),
            "release_ready": bool(qa_state.get("release_ready", release_ready)),
            "continue_decision": _clean_str((_clean_dict(qa_state.get("feature_scorecard"))).get("continue_decision")),
            "delivery_contract": qa_contract,
        },
        "release": {
            "gate_status": _clean_str(gate.get("status")),
            "release_ready": release_ready,
            "semantic": semantic,
            "revision_binding": revision_binding,
            "prompt_boundary": prompt_boundary,
        },
        "traceability": {
            "requirement_binding": requirement_binding,
            "requirement_refs": requirement_refs,
            "runtime_refs": runtime_refs,
        },
        "risk_flags": _clean_list(risk_flags),
    }


def load_delivery_read_model(
    project_root: Path,
    *,
    version: str,
    feature: str,
    release_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    authoritative_summary = _load_authoritative_implementation_summary(project_root, version=resolved_version, feature=feature)
    latest_runtime_state = _load_latest_implement_state(project_root, version=resolved_version, feature=feature)
    implement_state = _merge_implement_state(authoritative_summary, latest_runtime_state)
    qa_state = load_feature_qa_status(project_root, feature=feature) if _clean_str(feature) else {}
    if qa_state and _clean_str(qa_state.get("version")) not in {"", resolved_version}:
        qa_state = {}
    return build_delivery_read_model(
        feature=feature,
        version=resolved_version,
        project_root=project_root,
        implement_payload=implement_state,
        qa_payload=qa_state,
        release_payload=release_payload,
    )
