"""Browser QA memory and SkillEvolver advisory contracts for Beacon v1.4.10."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from beacon.utils.qa_acceptance import (
    NON_ACCEPTANCE_EVIDENCE_KINDS,
    build_browser_evidence_contract,
    classify_evidence_kind,
    normalize_browser_runner,
)

BROWSER_MEMORY_SCHEMA = "1.0"
BROWSER_MEMORY_AUTHORITY = {
    "support_evidence_only": True,
    "runtime_evidence_only": True,
    "truth_authority": False,
    "verdict_authority": False,
    "release_pass_evidence": False,
}
BROWSER_MEMORY_LIFECYCLE = (
    "discovered",
    "admitted",
    "reusable",
    "applied",
    "validated",
    "expired",
    "conflicted",
)
MEMORY_INFLUENCE_FIELDS = (
    "runner",
    "session_bridge",
    "selector_hints",
    "action_hints",
    "repeated_failure",
    "task_hints",
)
REFLECTION_FAMILIES = ("Discovery", "Optimization", "SkillDefect", "ExecutionLapse")
PROPOSAL_AUDIT_CHECKS = (
    "authority_bypass",
    "support_evidence_promoted_to_verdict",
    "single_project_overfitting",
    "missing_evidence_binding",
    "silent_bypass",
    "lifecycle_stage_sprawl",
)
PROPOSAL_ALLOWED_STATUSES = ("proposed", "audited", "accepted_for_change", "rejected", "deferred")
PROPOSAL_ROUTE_BY_STATUS = {
    "accepted_for_change": "beacon-change/refreeze",
    "audited": "beacon-change/refreeze",
    "proposed": "beacon-change/refreeze",
    "rejected": "support-evidence-only",
    "deferred": "support-evidence-only",
}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _host_from_target(value: str) -> str:
    raw = str(value or "").strip()
    parsed = urlparse(raw)
    return parsed.netloc or parsed.path.split("/")[0]


def _memory_id(seed: dict[str, Any]) -> str:
    canonical = "|".join(
        [
            str(seed.get("feature") or ""),
            str(seed.get("version") or ""),
            str(seed.get("target_host") or ""),
            str(seed.get("route_or_url") or ""),
            str(seed.get("browser") or ""),
            str(seed.get("runner") or ""),
            str(seed.get("source_run_id") or ""),
        ]
    )
    return "browser-memory-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def build_browser_memory_candidate(
    evidence: dict[str, Any],
    *,
    feature: str,
    version: str,
    project_id: str = "",
    auth_mode: str = "",
    session_ref: str = "",
    ac_ids: list[str] | None = None,
    test_ids: list[str] | None = None,
    selector_hints: list[str] | None = None,
    action_hints: list[str] | None = None,
    task_hints: list[str] | None = None,
    expires_at: str = "",
) -> dict[str, Any]:
    source = evidence if isinstance(evidence, dict) else {}
    evidence_refs = _string_list(source.get("evidence_refs") or source.get("evidence_ref") or [])
    test_refs = _string_list(test_ids or source.get("accepted_test_ids") or [])
    route_or_url = str(source.get("target_url") or source.get("route") or source.get("url") or "").strip()
    runner = normalize_browser_runner(str(source.get("runner") or source.get("browser_runner") or ""))
    payload = {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "memory_id": "",
        "lifecycle_status": "discovered",
        "project_id": str(project_id or "").strip(),
        "feature": str(feature or "").strip(),
        "version": str(version or "").strip(),
        "target_host": _host_from_target(route_or_url),
        "route_or_url": route_or_url,
        "browser": str(source.get("browser") or "").strip(),
        "runner": runner,
        "auth_mode": str(auth_mode or source.get("auth_mode") or "").strip(),
        "session_ref": str(session_ref or source.get("session_ref") or source.get("storage_state_ref") or "").strip(),
        "ac_ids": _string_list(ac_ids or source.get("ac_ids") or []),
        "test_ids": test_refs,
        "source_run_id": str(source.get("run_id") or source.get("source_run_id") or "").strip(),
        "source_command": str(source.get("source_command") or source.get("command") or "").strip(),
        "evidence_refs": evidence_refs,
        "outcome": str(source.get("result_status") or source.get("status") or "").strip(),
        "admission_status": "pending",
        "expires_at": str(expires_at or source.get("expires_at") or "").strip(),
        "influence_allowed": True,
        "selector_hints": _string_list(selector_hints or source.get("selector_hints") or []),
        "action_hints": _string_list(action_hints or source.get("action_hints") or []),
        "task_hints": _string_list(task_hints or source.get("task_hints") or []),
        "evidence_kind": classify_evidence_kind(
            str(source.get("source_command") or source.get("command") or ""),
            evidence_refs,
            str(source.get("notes") or ""),
        ),
        **BROWSER_MEMORY_AUTHORITY,
    }
    payload["memory_id"] = _memory_id(payload)
    payload["browser_evidence_contract"] = build_browser_evidence_contract(source)
    payload["validation"] = validate_browser_memory_candidate(payload)
    return payload


def validate_browser_memory_candidate(candidate: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    item = candidate if isinstance(candidate, dict) else {}
    issues: list[dict[str, Any]] = []
    required_fields = (
        "feature",
        "version",
        "target_host",
        "route_or_url",
        "browser",
        "runner",
        "auth_mode",
        "source_run_id",
        "outcome",
    )
    missing = [field for field in required_fields if not str(item.get(field) or "").strip()]
    if not _string_list(item.get("ac_ids") or []):
        missing.append("ac_ids")
    if not _string_list(item.get("test_ids") or []):
        missing.append("test_ids")
    if not _string_list(item.get("evidence_refs") or []):
        missing.append("evidence_refs")
    if missing:
        issues.append({"reason_code": "browser_memory_required_fields_missing", "missing_fields": sorted(set(missing))})
    evidence_contract = item.get("browser_evidence_contract") if isinstance(item.get("browser_evidence_contract"), dict) else {}
    if bool(evidence_contract.get("blocked")):
        issues.append({"reason_code": "browser_memory_current_browser_evidence_invalid", "contract": evidence_contract})
    evidence_kind = str(item.get("evidence_kind") or "").strip()
    if evidence_kind in NON_ACCEPTANCE_EVIDENCE_KINDS:
        issues.append({"reason_code": f"browser_memory_{evidence_kind}_evidence_rejected"})
    if str(item.get("outcome") or "").strip().lower() not in {"passed", "pass", "accepted", "valid"}:
        issues.append({"reason_code": "browser_memory_non_passing_outcome_rejected"})
    expires_at = _parse_time(str(item.get("expires_at") or ""))
    if expires_at and expires_at <= (now or _utc_now()):
        issues.append({"reason_code": "browser_memory_expired"})
    if bool(item.get("truth_authority")) or bool(item.get("verdict_authority")) or bool(item.get("release_pass_evidence")):
        issues.append({"reason_code": "browser_memory_authority_bypass"})
    status = "rejected" if issues else "admitted"
    return {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "status": status,
        "blocked": bool(issues),
        "reason_codes": [str(issue.get("reason_code") or "") for issue in issues],
        "issues": issues,
    }


def admit_browser_memory(candidate: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    payload = dict(candidate if isinstance(candidate, dict) else {})
    validation = validate_browser_memory_candidate(payload, now=now)
    payload["validation"] = validation
    payload["admission_status"] = "rejected" if validation["blocked"] else "admitted"
    payload["lifecycle_status"] = "conflicted" if validation["blocked"] else "admitted"
    payload.update(BROWSER_MEMORY_AUTHORITY)
    return payload


def retrieve_browser_memory(
    memories: list[dict[str, Any]],
    *,
    feature: str,
    version: str,
    target_host: str = "",
    route_or_url: str = "",
    browser: str = "",
    runner: str = "",
    auth_mode: str = "",
    protected_surface: bool | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    host = str(target_host or _host_from_target(route_or_url)).strip()
    normalized_runner = normalize_browser_runner(runner)
    for raw in memories or []:
        item = raw if isinstance(raw, dict) else {}
        validation = validate_browser_memory_candidate(item, now=now)
        reason_codes = list(validation.get("reason_codes") or [])
        if validation["blocked"]:
            rejected.append({"memory_id": str(item.get("memory_id") or ""), "reason_codes": reason_codes})
            continue
        checks = {
            "feature": (str(item.get("feature") or "").strip(), str(feature or "").strip()),
            "version": (str(item.get("version") or "").strip(), str(version or "").strip()),
            "target_host": (str(item.get("target_host") or "").strip(), host),
            "browser": (str(item.get("browser") or "").strip(), str(browser or "").strip()),
            "runner": (normalize_browser_runner(str(item.get("runner") or "")), normalized_runner),
            "auth_mode": (str(item.get("auth_mode") or "").strip(), str(auth_mode or "").strip()),
        }
        mismatch_codes = [
            f"browser_memory_{field}_mismatch"
            for field, pair in checks.items()
            if pair[1] and pair[0] and pair[0] != pair[1]
        ]
        if protected_surface is True and not str(item.get("session_ref") or "").strip():
            mismatch_codes.append("browser_memory_protected_surface_session_missing")
        if mismatch_codes:
            rejected.append({"memory_id": str(item.get("memory_id") or ""), "reason_codes": mismatch_codes})
            continue
        matched = dict(item)
        matched["lifecycle_status"] = "reusable"
        matched["admission_status"] = "admitted"
        matched.update(BROWSER_MEMORY_AUTHORITY)
        matches.append(matched)
    return {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "status": "matched" if matches else "blocked",
        "blocked": not bool(matches),
        "matches": matches,
        "rejected": rejected,
        "reason_codes": [] if matches else sorted({code for row in rejected for code in row.get("reason_codes", [])}),
        **BROWSER_MEMORY_AUTHORITY,
    }


def build_memory_influence(memory: dict[str, Any]) -> dict[str, Any]:
    item = memory if isinstance(memory, dict) else {}
    influence = {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "memory_id": str(item.get("memory_id") or "").strip(),
        "lifecycle_status": "applied",
        "runner": str(item.get("runner") or "").strip(),
        "session_bridge": str(item.get("session_ref") or "").strip(),
        "selector_hints": _string_list(item.get("selector_hints") or []),
        "action_hints": _string_list(item.get("action_hints") or []),
        "repeated_failure": str(item.get("outcome") or "").strip().lower() not in {"passed", "pass", "accepted", "valid"},
        "task_hints": _string_list(item.get("task_hints") or []),
        "current_run_required": True,
        "counts_as_pass_evidence": False,
        **BROWSER_MEMORY_AUTHORITY,
    }
    influence["influence_fields"] = [field for field in MEMORY_INFLUENCE_FIELDS if influence.get(field) not in ("", [], False)]
    return influence


def apply_browser_memory_to_task(task: dict[str, Any], memory: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(task if isinstance(task, dict) else {})
    if not memory:
        payload["browser_memory_influence"] = {"status": "not_applied", "blocked": False, **BROWSER_MEMORY_AUTHORITY}
        return payload
    influence = build_memory_influence(memory)
    payload["browser_memory_influence"] = influence
    contract = payload.get("runner_contract") if isinstance(payload.get("runner_contract"), dict) else {}
    if influence.get("runner") and not contract.get("memory_runner_hint"):
        contract["memory_runner_hint"] = influence["runner"]
    if influence.get("session_bridge"):
        payload.setdefault("session", {})
        if isinstance(payload["session"], dict):
            payload["session"].setdefault("memory_session_ref", influence["session_bridge"])
    hints = [*influence.get("selector_hints", []), *influence.get("action_hints", []), *influence.get("task_hints", [])]
    if hints:
        payload["memory_hints"] = hints
    payload["runner_contract"] = contract
    return payload


def classify_reflection_family(observation: dict[str, Any] | str) -> str:
    text = observation if isinstance(observation, str) else " ".join(str(value) for value in observation.values())
    lowered = str(text or "").lower()
    if any(token in lowered for token in ("skill", "instruction", "routing", "admission rule", "prompt")):
        return "SkillDefect"
    if any(token in lowered for token in ("timeout", "missed", "flaky", "execution", "lapse", "forgot")):
        return "ExecutionLapse"
    if any(token in lowered for token in ("faster", "optimize", "optimization", "reuse", "selector", "session")):
        return "Optimization"
    return "Discovery"


def build_skill_evolution_proposal(
    *,
    observation: dict[str, Any] | str,
    failure_family: str,
    trace_refs: list[str],
    affected_ac_ids: list[str],
    affected_test_ids: list[str],
    evidence_refs: list[str],
    target_surface: str,
    risk: str = "medium",
    patch_draft_refs: list[str] | None = None,
    eval_case_refs: list[str] | None = None,
    status: str = "proposed",
) -> dict[str, Any]:
    normalized_status = str(status or "proposed").strip()
    if normalized_status not in PROPOSAL_ALLOWED_STATUSES:
        normalized_status = "proposed"
    proposal_seed = "|".join([*trace_refs, *affected_ac_ids, *affected_test_ids, target_surface, failure_family])
    payload = {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "proposal_id": "skill-evolution-" + hashlib.sha256(proposal_seed.encode("utf-8")).hexdigest()[:16],
        "lifecycle_status": normalized_status,
        "reflection_family": classify_reflection_family(observation),
        "failure_family": str(failure_family or "").strip(),
        "trace_refs": _string_list(trace_refs),
        "affected_ac_ids": _string_list(affected_ac_ids),
        "affected_test_ids": _string_list(affected_test_ids),
        "evidence_refs": _string_list(evidence_refs),
        "target_surface": str(target_surface or "").strip(),
        "patch_draft_refs": _string_list(patch_draft_refs or []),
        "eval_case_refs": _string_list(eval_case_refs or []),
        "risk": str(risk or "medium").strip(),
        "auditor_status": "pending",
        "recommended_route": PROPOSAL_ROUTE_BY_STATUS[normalized_status],
        "mutation_executed": False,
        **BROWSER_MEMORY_AUTHORITY,
    }
    payload["audit"] = audit_skill_evolution_proposal(payload)
    payload["auditor_status"] = "blocked" if payload["audit"]["blocked"] else "pass"
    return payload


def audit_skill_evolution_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    item = proposal if isinstance(proposal, dict) else {}
    issues: list[dict[str, Any]] = []
    if bool(item.get("truth_authority")) or bool(item.get("verdict_authority")) or bool(item.get("release_pass_evidence")):
        issues.append({"reason_code": "authority_bypass"})
    if bool(item.get("mutation_executed")):
        issues.append({"reason_code": "silent_bypass"})
    if not _string_list(item.get("trace_refs") or []) or not _string_list(item.get("evidence_refs") or []):
        issues.append({"reason_code": "missing_evidence_binding"})
    if not _string_list(item.get("affected_ac_ids") or []) or not _string_list(item.get("affected_test_ids") or []):
        issues.append({"reason_code": "missing_ac_test_binding"})
    if str(item.get("target_surface") or "").strip() in {"prd_truth", "user_story_truth", "test_case_truth", "freeze_state", "qa_verdict", "release_verdict", "gate_verdict"}:
        issues.append({"reason_code": "lifecycle_stage_sprawl"})
    if bool(item.get("support_evidence_promoted_to_verdict")):
        issues.append({"reason_code": "support_evidence_promoted_to_verdict"})
    if bool(item.get("single_project_overfit")):
        issues.append({"reason_code": "single_project_overfitting"})
    return {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "status": "blocked" if issues else "pass",
        "blocked": bool(issues),
        "checks": list(PROPOSAL_AUDIT_CHECKS),
        "reason_codes": [str(issue.get("reason_code") or "") for issue in issues],
        "issues": issues,
    }


def build_qa_memory_release_support(
    *,
    memories: list[dict[str, Any]] | None = None,
    proposals: list[dict[str, Any]] | None = None,
    formal_qa_closure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    memory_items = [admit_browser_memory(item) for item in (memories or []) if isinstance(item, dict)]
    proposal_items = [dict(item) for item in (proposals or []) if isinstance(item, dict)]
    audited = []
    for item in proposal_items:
        proposal = dict(item)
        proposal["audit"] = audit_skill_evolution_proposal(proposal)
        proposal["auditor_status"] = "blocked" if proposal["audit"]["blocked"] else "pass"
        audited.append(proposal)
    closure = formal_qa_closure if isinstance(formal_qa_closure, dict) else {}
    return {
        "schema_version": BROWSER_MEMORY_SCHEMA,
        "status": "recorded" if memory_items or audited else "not_applicable",
        "support_evidence_only": True,
        "runtime_evidence_only": True,
        "truth_authority": False,
        "verdict_authority": False,
        "release_pass_evidence": False,
        "formal_qa_required": True,
        "formal_qa_release_ready": bool(closure.get("release_ready")) and str(closure.get("continue_decision") or "") == "ready_for_release",
        "memory_count": len(memory_items),
        "admitted_memory_count": len([item for item in memory_items if item.get("admission_status") == "admitted"]),
        "proposal_count": len(audited),
        "proposal_blocked_count": len([item for item in audited if (item.get("audit") or {}).get("blocked")]),
        "accepted_for_change_count": len([item for item in audited if str(item.get("lifecycle_status") or "") == "accepted_for_change"]),
        "memories": memory_items,
        "proposals": audited,
    }
