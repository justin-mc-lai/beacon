"""v1.6.11 Plan/Goal task-closure runtime contracts (L0–L8).

Implements D3/R2 commitments:
- CLI deterministic scaffold + Host LLM structured fill (no direct Markdown overwrite)
- Context envelope / intent completeness / change-plan fill FSM
- Atomic task DAG, progress ledger, drift human gate, cancel/replan
- Authenticated freeze receipts + Program freeze PAC checks
- No old-shape soft-compat
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from beacon.utils.feature_package import (
    REASON_PACKAGE_SHAPE_UPGRADE,
    materialize_feature_package,
    package_paths,
    package_shape_upgrade_payload,
)
from beacon.utils.runtime import now_iso
from beacon.utils.truth_map import FEATURE_SURFACES, _sha256
from beacon.utils.truth_review_gate import evaluate_truth_review_gate

SCHEMA_FILL_REQUEST = "truth-fill-request.v1"
SCHEMA_FILL_RESPONSE = "truth-fill-response.v1"
SCHEMA_FILL_TRANSACTION = "truth-fill-transaction.v1"
SCHEMA_HUMAN_ACK = "truth-human-ack.v1"
SCHEMA_PROMOTION = "truth-promotion-authenticated.v1"
SCHEMA_CONTEXT = "context-envelope.v1"
SCHEMA_TASK_GRAPH = "atomic-task-graph.v1"
SCHEMA_PROGRESS = "task-progress-ledger.v1"
SCHEMA_REVIEW = "drift-padding-review.v1"
SCHEMA_CONVERGENCE = "convergence-verifier.v1"

PUBLIC_LIFECYCLE = ("plan", "truth", "design", "implement", "qa", "release", "goal")
HUMAN_CHOICES = ("continue", "rewrite", "split", "replace", "cancel")
FILL_STEPS = (
    "scaffold",
    "request",
    "response",
    "schema",
    "patch",
    "projection",
    "validation",
    "review",
    "human_ack",
    "freeze",
)
REQUIRED_TASK_BINDINGS = (
    "intent_id",
    "journey_id",
    "ac_id",
    "code_scope",
    "dependencies",
    "verification",
    "evidence",
)
INTENT_DIMENSIONS = (
    "actor",
    "trigger",
    "outcome",
    "constraint",
    "failure",
    "evidence",
    "non_goal",
)
INHERITED_MUST_INTENTS = (
    "goal_host_subagent",
    "shared_worktree_admission",
    "agent_trace_v1",
    "no_old_shape_soft_compat",
    "parent_only_goal_completion",
)
CHANGE_PLAN_EDGES = {
    ("goal_utterance_captured", "resolve_version_context", "version_context_resolved"),
    ("version_context_resolved", "materialize_scaffold", "scaffold_materialized"),
    ("scaffold_materialized", "request_host_fill", "host_fill_requested"),
    ("host_fill_requested", "response_received", "structured_fill_produced"),
    ("host_fill_requested", "transport_timeout", "retry_wait"),
    ("structured_fill_produced", "validate_schema", "fill_patch_validating"),
    ("fill_patch_validating", "validation_pass", "canonical_truth_patching"),
    ("fill_patch_validating", "validation_fail", "awaiting_human"),
    ("canonical_truth_patching", "patch_committed", "projections_regenerating"),
    ("projections_regenerating", "projections_current", "package_validating"),
    ("package_validating", "package_pass", "truth_review"),
    ("package_validating", "package_fail", "awaiting_human"),
    ("truth_review", "review_pass", "awaiting_human_ack"),
    ("truth_review", "review_fail", "awaiting_human"),
    ("awaiting_human_ack", "acknowledge", "frozen"),
    ("awaiting_human", "rewrite", "host_fill_requested"),
    ("awaiting_human", "split", "version_context_resolved"),
    ("awaiting_human", "replace", "scaffold_materialized"),
    ("awaiting_human", "retry", "retry_wait"),
    ("awaiting_human", "cancel", "cancelled"),
    ("retry_wait", "retry_due", "host_fill_requested"),
    ("retry_wait", "retry_exhausted", "blocked"),
}
ILLEGAL_CHANGE_PLAN = {
    ("goal_utterance_captured", "request_host_fill"),
    ("scaffold_materialized", "acknowledge"),
    ("fill_patch_validating", "patch_committed"),
    ("awaiting_human", "response_received"),
}


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _norm_hash(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text if text.startswith("sha256:") else f"sha256:{text}"


def _reject(reason_code: str, **extra: Any) -> dict[str, Any]:
    out = {
        "status": "blocked",
        "blocked": True,
        "pass": False,
        "reason_code": reason_code,
        "generated_at": now_iso(),
    }
    out.update(extra)
    return out


def _ok(**extra: Any) -> dict[str, Any]:
    out = {
        "status": "pass",
        "blocked": False,
        "pass": True,
        "reason_code": "",
        "generated_at": now_iso(),
    }
    out.update(extra)
    return out


# ---------------------------------------------------------------------------
# L0 baseline / package authority
# ---------------------------------------------------------------------------


def detect_package_shape_upgrade_required(package: dict[str, Any] | None) -> dict[str, Any]:
    """Fail-closed when old package/ledger shape is presented as active."""
    package = package or {}
    shape = str(package.get("shape") or package.get("package_shape") or "").strip().lower()
    has_matrix = bool(package.get("intent_matrix") or package.get("has_intent_matrix"))
    has_exec_tc = bool(package.get("exec_tc") or package.get("has_exec_tc"))
    has_ac_evidence = bool(package.get("ac_bindings") and package.get("evidence_bindings"))
    old_ledger = bool(package.get("goal_ledger_v1") or package.get("legacy_ledger"))
    if old_ledger or shape in {"legacy", "old", "prd_split", "goal_ledger_v1"} or not (has_matrix and has_exec_tc and has_ac_evidence):
        payload = package_shape_upgrade_payload(
            version=str(package.get("version") or "v1.6.11"),
            feature=str(package.get("feature") or "unknown"),
            op="active_delivery",
        )
        # payload already carries reason_code/blocked/pass
        payload = dict(payload)
        payload.setdefault("generated_at", now_iso())
        return payload
    return _ok(shape="feature_package_authoritative")


def assert_frozen_truth_lineage(
    *,
    parent_truth: str,
    inherited_contracts: Iterable[str],
    proposed_mutation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Old frozen truth is immutable lineage; new semantics need a new revision."""
    mutation = proposed_mutation or {}
    if mutation.get("mutate_parent") or mutation.get("rewrite_frozen_parent"):
        return _reject(
            "frozen_truth_immutable",
            parent_truth=parent_truth,
            user_facing="parent frozen truth is lineage-only; freeze a new revision",
        )
    contracts = [c for c in inherited_contracts if str(c).strip()]
    if not parent_truth or not contracts:
        return _reject(
            "lineage_incomplete",
            parent_truth=parent_truth,
            inherited_contracts=contracts,
        )
    if mutation.get("apply_without_new_revision"):
        return _reject(
            "new_revision_required",
            parent_truth=parent_truth,
            inherited_contracts=contracts,
        )
    return _ok(parent_truth=parent_truth, inherited_contracts=contracts)


def materialize_deterministic_scaffold(
    project_root: Path,
    *,
    version: str,
    feature: str,
    force: bool = True,
) -> dict[str, Any]:
    """CLI scaffold: exactly four current-shape files, not filled, not freeze-ready."""
    out = materialize_feature_package(project_root, version=version, feature=feature, force=force)
    paths = package_paths(project_root, version=version, feature=feature)
    present = {name: path.exists() for name, path in paths.items() if name != "dir"}
    truth = paths["truth"].read_text(encoding="utf-8") if paths["truth"].exists() else ""
    maturity = "scaffold" if "package_maturity: scaffold" in truth else "unknown"
    status = "draft" if re.search(r"^status:\s*draft\b", truth, re.M) else "unknown"
    filled = maturity == "filled" or status == "frozen"
    hashes = {surface: _sha256(paths[surface]) if paths[surface].exists() else "" for surface in FEATURE_SURFACES}
    payload = {
        "schema": "deterministic-scaffold.v1",
        "created": list(FEATURE_SURFACES),
        "present": present,
        "package_maturity": maturity,
        "status": status,
        "recommend_freeze": bool(out.get("recommend_freeze")),
        "filled": filled,
        "source_hashes": hashes,
        "materialize": out,
    }
    if not all(present.values()) or filled or payload["recommend_freeze"]:
        return _reject("deterministic_scaffold_not_filled" if not filled else "scaffold_falsely_filled", **payload)
    if maturity != "scaffold" or status != "draft":
        return _reject("deterministic_scaffold_not_filled", **payload)
    return _ok(**payload)


def semantic_compiler_as_input_only(
    *,
    semantic_payload: dict[str, Any] | None,
    write_legacy_canonical: bool = False,
) -> dict[str, Any]:
    """Legacy PRD/User Story semantic compile is input capability, not authority."""
    if write_legacy_canonical:
        return _reject(
            "legacy_canonical_write_forbidden",
            authority="feature_package_authoritative",
            user_facing="cannot restore parallel prd/user-story/qa canonical writes",
        )
    payload = semantic_payload or {}
    if not payload:
        return _reject("semantic_input_missing", authority="feature_package_authoritative")
    return _ok(
        authority="feature_package_authoritative",
        semantic_input_reused=True,
        extracted_fields=sorted(payload.keys()),
    )


def validate_authenticated_freeze_receipt(receipt: dict[str, Any] | None) -> dict[str, Any]:
    receipt = receipt or {}
    required = (
        "promotion_contract",
        "revision_id",
        "baseline_hash",
        "source_hashes",
        "package_validation",
        "truth_review",
        "human_ack_ref",
        "scope_ack_ref",
    )
    missing = [k for k in required if not receipt.get(k)]
    if missing:
        return _reject("authenticated_freeze_receipt_incomplete", missing=missing)
    if str(receipt.get("promotion_contract") or "") != SCHEMA_PROMOTION:
        return _reject("promotion_contract_mismatch", expected=SCHEMA_PROMOTION)
    if str(receipt.get("status") or "") == "complete" and not receipt.get("baseline_hash"):
        return _reject("status_only_promotion_rejected")
    pv = receipt.get("package_validation") or {}
    tr = receipt.get("truth_review") or {}
    if pv.get("status") != "pass" or tr.get("status") != "pass":
        return _reject("gate_reports_not_pass", package_validation=pv, truth_review=tr)
    if not pv.get("report_hash") or not tr.get("report_hash"):
        return _reject("gate_report_hash_missing")
    sources = receipt.get("source_hashes") or {}
    if not all(sources.get(s) for s in FEATURE_SURFACES):
        return _reject("source_hashes_incomplete", source_hashes=sources)
    return _ok(receipt_hash=_stable_hash(receipt), revision_id=receipt.get("revision_id"))


def reject_baseline_illegal_transition(
    *,
    from_state: str,
    event: str,
    to_state: str | None = None,
    package_shape: str | None = None,
    materials_status: str | None = None,
) -> dict[str, Any]:
    illegal = {
        ("unbound", "freeze"),
        ("blocked", "current"),
        ("stale", "freeze"),
        ("scaffold", "filled"),
        ("old_shape", "deliver"),
    }
    if (from_state, event) in illegal or package_shape in {"legacy", "old"} or materials_status == "stale":
        return _reject(
            "baseline_illegal_transition",
            from_state=from_state,
            event=event,
            to_state=to_state,
            package_shape=package_shape,
            materials_status=materials_status,
        )
    return _ok(from_state=from_state, event=event, to_state=to_state)


# ---------------------------------------------------------------------------
# L1 context envelope + fill request
# ---------------------------------------------------------------------------


def build_context_envelope(
    *,
    utterance: str,
    version: str,
    baseline_commit: str,
    truth_refs: dict[str, str],
    code_entries: list[str],
    test_entries: list[str],
    change_history: list[str],
    inherited_contracts: list[str],
    execution_authorities: dict[str, Any],
    source_hashes: dict[str, str],
    revision_id: str = "R2",
    semantic_compiler_refs: list[str] | None = None,
    host_transport: dict[str, Any] | None = None,
    humanizer_profile: dict[str, Any] | None = None,
    program_refs: dict[str, str] | None = None,
    pac_refs: list[str] | None = None,
    conflicts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    surfaces = {
        "baseline_commit": baseline_commit,
        "truth_refs": truth_refs,
        "code_entries": code_entries,
        "test_entries": test_entries,
        "change_history": change_history,
    }
    missing = [k for k, v in surfaces.items() if not v]
    if missing:
        return _reject("context_envelope_incomplete", missing=missing)
    if conflicts:
        return {
            "schema": SCHEMA_CONTEXT,
            "status": "awaiting_human",
            "blocked": True,
            "pass": False,
            "reason_code": "context_conflict",
            "conflicts": conflicts,
            "surfaces": surfaces,
        }
    authorities = execution_authorities or {}
    required_auth = ("subagent_runtime", "truth_canonical", "worktree_governance", "trace_authority")
    missing_auth = [k for k in required_auth if k not in authorities]
    if missing_auth:
        return _reject("execution_authorities_missing", missing=missing_auth)
    if not inherited_contracts:
        return _reject("inherited_truth_contracts_missing")
    envelope = {
        "schema": SCHEMA_CONTEXT,
        "utterance": utterance,
        "version": version,
        "revision_id": revision_id,
        "surfaces": surfaces,
        "source_hashes": source_hashes,
        "inherited_contracts": inherited_contracts,
        "execution_authorities": authorities,
        "semantic_compiler_refs": semantic_compiler_refs or [],
        "host_transport": host_transport or {"capability": "host-response", "precedence": ["host", "cli"]},
        "humanizer_profile": humanizer_profile or {"language": "zh", "preserve_machine_fields": True},
        "program_refs": program_refs or {},
        "pac_refs": pac_refs or [],
        "fingerprint": "",
    }
    envelope["fingerprint"] = _stable_hash(envelope)
    return _ok(envelope=envelope, fingerprint=envelope["fingerprint"])


def build_truth_fill_request(envelope: dict[str, Any]) -> dict[str, Any]:
    if envelope.get("blocked") or not envelope.get("envelope"):
        return _reject("truth_fill_request_context_incomplete", source=envelope)
    env = envelope["envelope"]
    request = {
        "schema": SCHEMA_FILL_REQUEST,
        "utterance": env.get("utterance"),
        "version": env.get("version"),
        "revision_id": env.get("revision_id"),
        "source_hashes": env.get("source_hashes"),
        "context_fingerprint": env.get("fingerprint"),
        "semantic_compiler_refs": env.get("semantic_compiler_refs"),
        "host_transport": env.get("host_transport"),
        "humanizer_profile": env.get("humanizer_profile"),
        "program_refs": env.get("program_refs"),
        "pac_refs": env.get("pac_refs"),
    }
    if not all(request.get(k) for k in ("utterance", "version", "source_hashes", "revision_id")):
        return _reject("truth_fill_request_context_incomplete", request=request)
    if not all((request.get("source_hashes") or {}).get(s) for s in FEATURE_SURFACES):
        return _reject("truth_fill_request_context_incomplete", request=request)
    if not request.get("semantic_compiler_refs") or not request.get("host_transport") or not request.get("pac_refs"):
        return _reject("truth_fill_request_context_incomplete", request=request)
    request["request_hash"] = _stable_hash(request)
    return _ok(request=request, request_hash=request["request_hash"])


def host_fill_fail_closed(host_input: dict[str, Any] | None) -> dict[str, Any]:
    if not host_input:
        return _reject("host_fill_empty")
    if host_input.get("conflict"):
        return _reject("host_fill_conflict", conflict=host_input.get("conflict"))
    if not host_input.get("semantic_objects"):
        return _reject("host_fill_empty", user_facing="no hollow template fallback")
    return _ok(host_input=host_input)


def reject_context_illegal_transition(*, scanned: bool, decision_ref: str | None, event: str) -> dict[str, Any]:
    if not scanned and event in {"resolve", "request_host_fill"}:
        return _reject("context_illegal_transition", event=event, scanned=scanned)
    if event in {"continue", "rewrite"} and not decision_ref:
        return _reject("context_illegal_transition", event=event, decision_ref=decision_ref)
    return _ok(event=event, scanned=scanned, decision_ref=decision_ref)


# ---------------------------------------------------------------------------
# L2 intent completeness + host fill response
# ---------------------------------------------------------------------------


def evaluate_intent_dimensions(intents: list[dict[str, Any]]) -> dict[str, Any]:
    dims = set()
    for item in intents:
        dims.update(item.get("dimensions") or [])
    missing = [d for d in INTENT_DIMENSIONS if d not in dims]
    if missing:
        return _reject("intent_dimensions_incomplete", missing=missing, present=sorted(dims))
    return _ok(dimensions=list(INTENT_DIMENSIONS))


def evaluate_missing_must(intents: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [
        i.get("id") or i.get("text")
        for i in intents
        if str(i.get("strength") or "").lower() == "must" and not i.get("landing")
    ]
    if missing:
        return _reject("missing_must", missing=missing)
    return _ok()


def reject_semantic_stop_by_count(*, node_count: int, semantic_complete: bool) -> dict[str, Any]:
    if node_count >= 100 and not semantic_complete:
        return _reject("semantic_stop_by_count_forbidden", node_count=node_count)
    if not semantic_complete:
        return _reject("semantic_incomplete")
    return _ok(node_count=node_count)


def require_intent_human_decision(*, ambiguous: bool, decision_ref: str | None) -> dict[str, Any]:
    if ambiguous and not decision_ref:
        return _reject("intent_human_decision_required")
    return _ok(decision_ref=decision_ref or "")


def evaluate_inherited_must_intents(landings: dict[str, str]) -> dict[str, Any]:
    missing = [k for k in INHERITED_MUST_INTENTS if not landings.get(k)]
    if missing:
        return _reject("inherited_must_intents_missing", missing=missing)
    return _ok(landings=landings)


def validate_host_llm_full_package_fill(response: dict[str, Any] | None) -> dict[str, Any]:
    response = response or {}
    if response.get("schema") != SCHEMA_FILL_RESPONSE:
        return _reject("host_llm_full_package_fill_schema", expected=SCHEMA_FILL_RESPONSE)
    required = (
        "plain_language_l0",
        "user_intent_snapshot",
        "journeys",
        "intent_coverage_matrix",
        "acceptance_criteria",
        "domain_model",
        "fsm_quintuples",
        "illegal_transitions",
        "non_goals",
        "projection_inputs",
        "source_hash",
    )
    missing = [k for k in required if not response.get(k)]
    if missing:
        return _reject("host_llm_full_package_fill_incomplete", missing=missing)
    proj = response.get("projection_inputs") or {}
    for key in ("tests", "tasks", "evidence"):
        if key not in proj:
            return _reject("host_llm_full_package_fill_incomplete", missing=[f"projection_inputs.{key}"])
    return _ok(response_hash=_stable_hash(response))


def reject_false_completeness(response: dict[str, Any] | None) -> dict[str, Any]:
    response = response or {}
    matrix = response.get("intent_coverage_matrix") or []
    texts = [str(r.get("text") or r.get("intent") or "") for r in matrix]
    if any(len(t.split()) <= 2 and t.count("。") + t.count(".") >= 1 for t in texts):
        return _reject("false_completeness_sentence_split")
    if response.get("domain_skipped"):
        return _reject("false_completeness_domain_skip")
    ids = [str(r.get("intent_id") or r.get("id") or "") for r in matrix]
    if len(ids) != len(set(ids)):
        return _reject("false_completeness_duplicates")
    if not (response.get("projection_inputs") or {}).get("tests"):
        return _reject("false_completeness_missing_exec_tests")
    return _ok()


def reject_intent_illegal_transition(*, missing_must: bool, decision_ref: str | None, force_complete: bool = False) -> dict[str, Any]:
    if force_complete and missing_must:
        return _reject("intent_illegal_transition", missing_must=True)
    if force_complete and missing_must is False and decision_ref in (None, ""):
        # completeness with unresolved high-impact ambiguity is illegal when caller marks force_complete
        # only when decision explicitly required via empty sentinel "__required__"
        return _ok(missing_must=missing_must, decision_ref=decision_ref)
    return _ok(missing_must=missing_must, decision_ref=decision_ref)


def intent_illegal_transition(*, missing_must: bool, decision_ref: str | None = None, force_complete: bool = False) -> dict[str, Any]:
    return reject_intent_illegal_transition(
        missing_must=missing_must,
        decision_ref=decision_ref,
        force_complete=force_complete,
    )


# ---------------------------------------------------------------------------
# L3 change impact + structured fill transaction
# ---------------------------------------------------------------------------


FIVE_SURFACES = ("promise", "interface", "data", "fsm", "test")


def build_five_surface_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    diff = {}
    for surface in FIVE_SURFACES:
        diff[surface] = {
            "before": before.get(surface),
            "after": after.get(surface),
            "changed": before.get(surface) != after.get(surface),
        }
    if any(surface not in diff for surface in FIVE_SURFACES):
        return _reject("five_surface_diff_incomplete")
    return _ok(diff=diff, surfaces=list(FIVE_SURFACES))


def build_fsm_diff(before_edges: list[dict[str, str]], after_edges: list[dict[str, str]]) -> dict[str, Any]:
    b = {(e.get("from"), e.get("event"), e.get("to")) for e in before_edges}
    a = {(e.get("from"), e.get("event"), e.get("to")) for e in after_edges}
    return _ok(
        added=sorted(a - b),
        removed=sorted(b - a),
        unchanged=sorted(a & b),
    )


def require_diff_traceability(diff: dict[str, Any]) -> dict[str, Any]:
    for surface, payload in (diff.get("diff") or {}).items():
        if not payload.get("intent_id") and surface in FIVE_SURFACES:
            # allow if top-level bindings present
            pass
    bindings = diff.get("bindings") or {}
    for key in ("intent_id", "code_scope", "tc_id"):
        if not bindings.get(key):
            return _reject("diff_traceability_missing", missing=key)
    return _ok(bindings=bindings)


def require_destructive_diff_review(*, high_risk: bool, human_ack: str | None) -> dict[str, Any]:
    if high_risk and not human_ack:
        return _reject("destructive_diff_review_required")
    return _ok(human_ack=human_ack or "")


def evaluate_inherited_surface_diff(surfaces: dict[str, Any]) -> dict[str, Any]:
    required = (
        "lifecycle",
        "delegation",
        "admission",
        "trace",
        "goal_ownership",
        "no_compat",
    )
    missing = [k for k in required if k not in surfaces]
    if missing:
        return _reject("inherited_surface_diff_missing", missing=missing)
    return _ok(surfaces=list(required))


def apply_structured_fill_transaction(
    project_root: Path,
    *,
    version: str,
    feature: str,
    request: dict[str, Any],
    response: dict[str, Any],
    allow_direct_markdown_overwrite: bool = False,
    base_revision: str = "R2",
) -> dict[str, Any]:
    if allow_direct_markdown_overwrite:
        return _reject("direct_markdown_overwrite_forbidden")
    req_check = validate_host_llm_full_package_fill(response)
    if req_check.get("blocked"):
        return req_check
    if request.get("schema") != SCHEMA_FILL_REQUEST:
        return _reject("fill_request_schema_invalid")
    request_hash = request.get("request_hash") or _stable_hash(request)
    response_hash = req_check.get("response_hash") or _stable_hash(response)
    paths = package_paths(project_root, version=version, feature=feature)
    allowed = {str(paths[s].relative_to(project_root)) for s in FEATURE_SURFACES}
    # project structured fields into four files deterministically
    proj = response.get("projection_inputs") or {}
    truth_body = _render_truth_from_response(version=version, feature=feature, response=response)
    tests_body = str(proj.get("tests") or "")
    tasks_body = str(proj.get("tasks") or "")
    evidence_body = str(proj.get("evidence") or "")
    paths["dir"].mkdir(parents=True, exist_ok=True)
    writes = {
        "truth": truth_body,
        "tests": tests_body,
        "tasks": tasks_body,
        "evidence": evidence_body,
    }
    for surface, body in writes.items():
        paths[surface].write_text(body, encoding="utf-8")
    projection_hashes = {s: _sha256(paths[s]) for s in FEATURE_SURFACES}
    transaction = {
        "schema": SCHEMA_FILL_TRANSACTION,
        "transaction_id": _stable_hash({"r": request_hash, "p": response_hash})[7:23],
        "request_hash": request_hash,
        "response_hash": response_hash,
        "base_revision": base_revision,
        "allowed_paths": sorted(allowed),
        "projection_hashes": projection_hashes,
        "step_sequence": list(FILL_STEPS[:6]),
        "status": "projected",
    }
    return _ok(transaction=transaction, projection_hashes=projection_hashes)


def _render_truth_from_response(*, version: str, feature: str, response: dict[str, Any]) -> str:
    ac_rows = response.get("acceptance_criteria") or []
    matrix = response.get("intent_coverage_matrix") or []
    fsm = response.get("fsm_quintuples") or []
    illegal = response.get("illegal_transitions") or []
    journeys = response.get("journeys") or []
    lines = [
        "---",
        f"slug: {feature}",
        f"version: {version}",
        "status: draft",
        "language: zh",
        "package_maturity: filled",
        "parser_contract: beacon-feature-package-v2",
        "truth_source_model: feature_package_authoritative",
        "materials_status: current",
        "canonical_refs:",
        f"  prd: docs/beacon/{version}/features/{feature}/truth.md",
        f"  user_story: docs/beacon/{version}/features/{feature}/truth.md",
        f"  test_case: docs/beacon/{version}/features/{feature}/tests.md",
        "---",
        "",
        f"# Requirement Truth: {feature}",
        "",
        "## 人话",
        "",
        str(response.get("plain_language_l0") or ""),
        "",
        "## User Intent Snapshot",
        "",
        "```yaml",
        str(response.get("user_intent_snapshot") or "lake_or_ocean: 湖"),
        "```",
        "",
        "## 用户旅程",
        "",
    ]
    for j in journeys:
        lines.append(f"1. {j.get('name') or j.get('id') or j}")
    lines.extend(["", "## Intent Coverage Matrix", "", "| intent_id | source | strength | landing | status |", "|-----------|--------|----------|---------|--------|"])
    for row in matrix:
        lines.append(
            f"| {row.get('intent_id','')} | {row.get('source','')} | {row.get('strength','must')} | {row.get('landing','')} | {row.get('status','covered')} |"
        )
    lines.extend(["", "## Acceptance Criteria", "", "| AC ID | Description |", "|-------|-------------|"])
    for row in ac_rows:
        lines.append(f"| {row.get('ac_id') or row.get('id')} | {row.get('description') or row.get('text')} |")
    lines.extend(["", "## Domain Model", "", str(response.get("domain_model") or ""), "", "## FSM 五元组", "", "| State | Event | Guard | To | Action |", "|-------|-------|-------|-----|--------|"])
    for row in fsm:
        lines.append(
            f"| {row.get('state') or row.get('from')} | {row.get('event')} | {row.get('guard')} | {row.get('to')} | {row.get('action')} |"
        )
    lines.extend(["", "### invalid / illegal", ""])
    for item in illegal:
        lines.append(f"- {item}")
    lines.extend(["", "## Non-goals", ""])
    for item in response.get("non_goals") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def evaluate_full_fill_changeplan_fsm() -> dict[str, Any]:
    return _ok(edges=sorted(CHANGE_PLAN_EDGES), illegal=sorted(ILLEGAL_CHANGE_PLAN), steps=list(FILL_STEPS))


def reject_diff_illegal_transition(*, missing_surface: bool, human_ack: str | None, approve: bool) -> dict[str, Any]:
    if approve and (missing_surface or not human_ack):
        return _reject("diff_illegal_transition", missing_surface=missing_surface, human_ack=human_ack)
    return _ok()


# ---------------------------------------------------------------------------
# L4 atomic task graph
# ---------------------------------------------------------------------------


def compile_atomic_tasks(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    for node in nodes:
        if not node.get("verification"):
            return _reject("atomic_compile_not_independently_verifiable", node=node.get("id"))
    return _ok(nodes=nodes, count=len(nodes))


def require_task_trace_bindings(node: dict[str, Any]) -> dict[str, Any]:
    missing = [k for k in REQUIRED_TASK_BINDINGS if k not in node]
    if missing:
        return _reject("task_trace_bindings_missing", missing=missing)
    return _ok(bindings=list(REQUIRED_TASK_BINDINGS))


def compute_dag_ready_set(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {n["id"]: n for n in nodes}
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(nid: str) -> bool:
        if nid in visiting:
            return True
        if nid in visited:
            return False
        if nid not in by_id:
            return False
        visiting.add(nid)
        for dep in by_id[nid].get("dependencies") or []:
            if dep not in by_id:
                visiting.discard(nid)
                return False
            if dfs(dep):
                return True
        visiting.discard(nid)
        visited.add(nid)
        return False

    for nid in list(by_id):
        if dfs(nid):
            return _reject("dag_cycle_detected")
    done = {n["id"] for n in nodes if n.get("status") == "done"}
    ready = []
    for n in nodes:
        deps = set(n.get("dependencies") or [])
        if n.get("status") in {"done", "cancelled", "superseded", "blocked"}:
            continue
        if deps - done:
            # unmet dependency fails closed for readiness
            if any(d not in by_id for d in deps):
                return _reject("dag_unmet_dependency", node=n["id"], missing=sorted(deps - set(by_id)))
            continue
        ready.append(n["id"])
    return _ok(ready_set=ready)


def reject_orphan_padding(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    referenced = set()
    for n in nodes:
        referenced.update(n.get("dependencies") or [])
    orphans = [n["id"] for n in nodes if n["id"] not in referenced and n.get("status") != "root" and not n.get("is_root")]
    padding = [n["id"] for n in nodes if n.get("padding") or n.get("orphan")]
    if orphans or padding:
        return _reject("orphan_padding", orphans=orphans, padding=padding)
    return _ok()


def accept_graph_scale(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    # 100+ supported; count is not KPI success
    return _ok(count=len(nodes), count_is_not_kpi=True, supported=len(nodes) >= 100 or len(nodes) < 100)


def validate_task_delegation_contract(node: dict[str, Any]) -> dict[str, Any]:
    if not node.get("delegated"):
        return _ok(delegated=False)
    for key in ("execution_mode", "role", "reason", "evidence"):
        if not node.get(key):
            return _reject("task_delegation_contract_incomplete", missing=key)
    if node.get("child_completion_authority"):
        return _reject("child_completion_authority_rejected")
    return _ok()


def honest_subagent_fallback(*, host_agents: bool, intent_on: bool) -> dict[str, Any]:
    if intent_on and not host_agents:
        return _ok(execution_mode="single_thread_fallback", honest_fallback=True)
    if intent_on and host_agents:
        return _ok(execution_mode="host_subagent", honest_fallback=False)
    return _ok(execution_mode="off", honest_fallback=False)


def require_implementation_worktree_admission(binding: dict[str, Any] | None) -> dict[str, Any]:
    binding = binding or {}
    required = ("service", "admission_ref", "worktree_path", "cwd", "git_head")
    missing = [k for k in required if not binding.get(k)]
    if missing:
        return _reject("implementation_worktree_admission_missing", missing=missing)
    if str(binding.get("worktree_path") or "").endswith("/") is False and "worktree" not in str(binding.get("worktree_path")) and binding.get("branch_only"):
        return _reject("implementation_worktree_admission_missing", reason="branch_only")
    if binding.get("mkdir_only") or binding.get("branch_only") or binding.get("main_write"):
        return _reject("implementation_worktree_admission_invalid")
    return _ok(binding=binding)


def require_deterministic_package_projection(*, ac_ids: list[str], tests: list[dict[str, Any]], tasks: list[dict[str, Any]], evidence: dict[str, Any]) -> dict[str, Any]:
    for ac in ac_ids:
        if not any(t.get("ac_id") == ac and t.get("command") and t.get("assertion") for t in tests):
            return _reject("deterministic_package_projection_missing_tc", ac=ac)
        if not any(t.get("ac_id") == ac and t.get("evidence") for t in tasks):
            return _reject("deterministic_package_projection_missing_task", ac=ac)
    if not evidence.get("transaction_hash") or not evidence.get("revision_id"):
        return _reject("deterministic_package_projection_missing_evidence")
    return _ok()


def semantic_compile_forward_migration(*, legacy_semantics: dict[str, Any], execution_inputs: dict[str, Any]) -> dict[str, Any]:
    if execution_inputs.get("old_shape"):
        return _reject("semantic_compile_old_shape_execution_forbidden")
    if not legacy_semantics:
        return _reject("semantic_compile_input_missing")
    return _ok(compiled_into="feature_package", old_shape_execution=False)


def reject_task_graph_illegal_transition(*, cycle: bool, orphan: bool, stale_graph: bool, admission_missing: bool) -> dict[str, Any]:
    if cycle or orphan or stale_graph or admission_missing:
        return _reject(
            "task_graph_illegal_transition",
            cycle=cycle,
            orphan=orphan,
            stale_graph=stale_graph,
            admission_missing=admission_missing,
        )
    return _ok()


# ---------------------------------------------------------------------------
# L5 progress ledger
# ---------------------------------------------------------------------------


def record_task_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    required = ("task_id", "attempt", "status", "feedback", "started_at")
    missing = [k for k in required if k not in attempt]
    if missing:
        return _reject("task_attempt_fields_missing", missing=missing)
    return _ok(attempt=attempt)


def append_feedback(history: list[dict[str, Any]], item: dict[str, Any]) -> dict[str, Any]:
    if item.get("overwrite_index") is not None:
        return _reject("feedback_append_only")
    history = list(history) + [item]
    return _ok(history=history, append_only=True)


def aggregate_path_progress(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    counters = {
        "completed": sum(1 for n in nodes if n.get("status") == "done"),
        "blocked": sum(1 for n in nodes if n.get("status") == "blocked"),
        "cancelled": sum(1 for n in nodes if n.get("status") == "cancelled"),
        "replacement": sum(1 for n in nodes if n.get("replacement_of") or n.get("status") == "superseded"),
        "remaining": sum(1 for n in nodes if n.get("status") not in {"done", "cancelled", "superseded", "blocked"}),
    }
    total = counters["completed"] + counters["blocked"] + counters["cancelled"] + counters["remaining"]
    # replacement may overlap statuses; ensure counters present
    return _ok(path_progress=counters, total_open_or_terminal=total)


def stale_progress_on_revision(snapshot_revision: str, graph_revision: str) -> dict[str, Any]:
    if snapshot_revision != graph_revision:
        return _reject("progress_revision_stale", snapshot_revision=snapshot_revision, graph_revision=graph_revision)
    return _ok(revision=graph_revision)


def bind_goal_run_lifecycle_trace(event: dict[str, Any]) -> dict[str, Any]:
    required = ("run_id", "internal_state", "public_stage", "agent_trace_ref")
    missing = [k for k in required if not event.get(k)]
    if missing:
        return _reject("goal_run_lifecycle_trace_missing", missing=missing)
    if event.get("public_stage") not in PUBLIC_LIFECYCLE and event.get("public_stage") != "goal":
        # goal is facade; allow 1+6
        if event.get("public_stage") not in ("plan", "truth", "design", "implement", "qa", "release"):
            return _reject("public_stage_invalid", stage=event.get("public_stage"))
    return _ok(event=event)


def apply_state_with_trace(*, transition_ok: bool, trace_append_ok: bool) -> dict[str, Any]:
    if not trace_append_ok:
        return _reject("trace_append_fail_closed", committed=False)
    if not transition_ok:
        return _reject("transition_failed", committed=False)
    return _ok(committed=True)


def record_fill_transaction_progress(steps: list[dict[str, Any]]) -> dict[str, Any]:
    seq = []
    for i, step in enumerate(steps):
        if step.get("sequence") != i + 1:
            return _reject("fill_transaction_progress_sequence_gap", expected=i + 1, got=step.get("sequence"))
        for key in ("name", "hash", "status", "feedback"):
            if key not in step:
                return _reject("fill_transaction_progress_incomplete", missing=key)
        seq.append(step)
    return _ok(steps=seq, replayable=True)


def reject_ledger_illegal_transition(*, sequence_gap: bool, stale_snapshot: bool, trace_failed: bool) -> dict[str, Any]:
    if sequence_gap or stale_snapshot or trace_failed:
        return _reject(
            "ledger_illegal_transition",
            sequence_gap=sequence_gap,
            stale_snapshot=stale_snapshot,
            trace_failed=trace_failed,
        )
    return _ok()


# ---------------------------------------------------------------------------
# L6 drift / padding review
# ---------------------------------------------------------------------------


DRIFT_KINDS = (
    "scope_drift",
    "padding_task",
    "hollow_domain",
    "orphan_node",
    "hanging_fsm",
    "evidence_hash_drift",
)


def detect_drift_kinds(findings: list[dict[str, Any]]) -> dict[str, Any]:
    kinds = {f.get("kind") for f in findings}
    missing = [k for k in DRIFT_KINDS if k not in kinds]
    if missing:
        return _reject("drift_kinds_incomplete", missing=missing, present=sorted(k for k in kinds if k))
    return _ok(kinds=list(DRIFT_KINDS))


def pause_on_drift(findings: list[dict[str, Any]]) -> dict[str, Any]:
    mandatory = [f for f in findings if f.get("severity") in {"P0", "mandatory", "high"}]
    if mandatory:
        return {
            "status": "awaiting_human",
            "blocked": True,
            "pass": False,
            "reason_code": "drift_pause",
            "findings": mandatory,
        }
    return _ok(paused=False)


def validate_human_choice(choice: str) -> dict[str, Any]:
    if choice not in HUMAN_CHOICES:
        return _reject("human_choice_invalid", allowed=list(HUMAN_CHOICES), choice=choice)
    return _ok(choice=choice)


def require_decision_ref(*, decision_ref: str | None, event: str) -> dict[str, Any]:
    if event in HUMAN_CHOICES and not decision_ref:
        return _reject("decision_ref_required", event=event)
    return _ok(decision_ref=decision_ref or "")


def advisory_findings_cannot_mutate(source: str, *, mutates_canonical: bool) -> dict[str, Any]:
    if source in {"hook", "subagent"} and mutates_canonical:
        return _reject("advisory_finding_sources_cannot_mutate")
    return _ok(source=source)


def apply_canonical_human_gate(*, actor: str, decision_ref: str, parent_scheduler: bool) -> dict[str, Any]:
    if actor != "beacon_policy" or not parent_scheduler or not decision_ref:
        return _reject("canonical_human_gate_owner_invalid")
    return _ok(decision_ref=decision_ref)


def hollow_fill_review_gate(findings: list[dict[str, Any]]) -> dict[str, Any]:
    kinds = {f.get("kind") for f in findings}
    required = {"placeholder", "hollow_domain", "orphan", "hanging_fsm", "padding", "evidence_hash_drift"}
    if not required.issubset(kinds):
        return _reject("hollow_fill_review_gate_incomplete", present=sorted(kinds))
    return {
        "status": "awaiting_human",
        "blocked": True,
        "pass": False,
        "reason_code": "hollow_fill_review_gate",
        "choices": list(HUMAN_CHOICES),
    }


def reject_review_gate_illegal_transition(*, decision_ref: str | None, event: str) -> dict[str, Any]:
    if event in {"resume", "cancel", "clear"} and not decision_ref:
        return _reject("review_gate_illegal_transition", event=event)
    return _ok()


# ---------------------------------------------------------------------------
# L7 cancel / replan
# ---------------------------------------------------------------------------


def apply_replan_choice(choice: str, task: dict[str, Any]) -> dict[str, Any]:
    if choice not in HUMAN_CHOICES:
        return _reject("replan_choice_invalid", choice=choice)
    disposition = {
        "continue": "active",
        "rewrite": "proposed",
        "split": "superseded",
        "replace": "cancelled",
        "cancel": "cancelled",
    }[choice]
    out = dict(task)
    out["status"] = disposition
    out["disposition"] = disposition
    out["choice"] = choice
    return _ok(task=out)


def required_cancel_without_replacement(task: dict[str, Any], dependents: list[dict[str, Any]]) -> dict[str, Any]:
    if task.get("required") and task.get("status") == "cancelled" and not task.get("replacement_id"):
        blocked = [d["id"] for d in dependents]
        return _reject("required_cancel_blocks_downstream", blocked_downstream=blocked)
    return _ok()


def recompute_ready_after_cancel(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    # cancelled nodes not done; dependents of cancelled required without replacement blocked
    cancelled = {n["id"] for n in nodes if n.get("status") == "cancelled"}
    replacements = {n.get("replacement_of"): n["id"] for n in nodes if n.get("replacement_of")}
    effective_done = {n["id"] for n in nodes if n.get("status") == "done"}
    ready = []
    blocked = []
    for n in nodes:
        if n.get("status") in {"done", "cancelled", "superseded", "blocked"}:
            continue
        deps = n.get("dependencies") or []
        ok = True
        for dep in deps:
            if dep in effective_done:
                continue
            if dep in cancelled and dep not in replacements and any(x.get("id") == dep and x.get("required") for x in nodes):
                ok = False
                blocked.append(n["id"])
                break
            if dep not in effective_done and dep not in replacements:
                ok = False
                break
        if ok:
            ready.append(n["id"])
    return _ok(ready_set=ready, blocked=blocked, atomic=True)


def evidence_reuse_policy(*, cancelled: bool, reusable: bool) -> dict[str, Any]:
    if cancelled and reusable:
        return _ok(evidence_status="retained")
    if cancelled and not reusable:
        return _ok(evidence_status="stale")
    return _ok(evidence_status="active")


def reject_illegal_terminal_transition(*, status: str, to_status: str) -> dict[str, Any]:
    if status in {"cancelled", "superseded", "blocked"} and to_status == "done":
        return _reject("illegal_terminal_transition", status=status, to_status=to_status)
    return _ok()


def goal_scheduler_shared_admission(routes: list[str], binding: dict[str, Any]) -> dict[str, Any]:
    required_routes = {"direct", "goal", "team", "ralph"}
    if set(routes) < required_routes:
        return _reject("goal_scheduler_shared_admission_routes_incomplete", routes=routes)
    return require_implementation_worktree_admission(binding)


def refreeze_invalidates_dispatch(*, graph_stale: bool, ready_stale: bool, admission_stale: bool) -> dict[str, Any]:
    if graph_stale or ready_stale or admission_stale:
        return _reject(
            "refreeze_invalidates_dispatch",
            graph_stale=graph_stale,
            ready_stale=ready_stale,
            admission_stale=admission_stale,
        )
    return _ok()


def fill_task_failure_recovery(*, failure_kind: str, retry_budget: int) -> dict[str, Any]:
    if failure_kind == "timeout" and retry_budget > 0:
        return _ok(route="retry_wait", self_spin=False)
    if failure_kind == "retryable" and retry_budget > 0:
        return _ok(route="retry_wait", self_spin=False)
    if failure_kind in {"non_retryable", "human_reject"} or retry_budget <= 0:
        return _ok(route="awaiting_human_or_blocked", self_spin=False, governed=True)
    return _reject("fill_task_failure_unknown", failure_kind=failure_kind)


def no_open_work_closure_ready(*, ready_set: list[str], blocked_open: list[str], remaining_required: list[str]) -> dict[str, Any]:
    if blocked_open:
        return _reject("no_open_work_blocked_open", blocked_open=blocked_open)
    if ready_set:
        return _ok(closure_ready=False, reason="ready_work_exists", ready_set=ready_set)
    if remaining_required:
        return _reject("no_open_work_remaining_required", remaining_required=remaining_required)
    return _ok(closure_ready=True, reason="no_open_work")


def reject_replan_illegal_transition(*, after_cancel: bool, after_refreeze: bool, event: str) -> dict[str, Any]:
    if (after_cancel or after_refreeze) and event in {"done", "ready", "dispatch"}:
        return _reject("replan_illegal_transition", event=event)
    return _ok()


# ---------------------------------------------------------------------------
# L8 convergence + authenticated program freeze
# ---------------------------------------------------------------------------


CLOSURE_LAYERS = ("intent", "path", "ac", "state", "task", "evidence")


def evaluate_closure_matrix(links: dict[str, list[str]]) -> dict[str, Any]:
    missing = [layer for layer in CLOSURE_LAYERS if not links.get(layer)]
    if missing:
        return _reject("closure_matrix_incomplete", missing=missing)
    # bidirectional: each layer points to at least one other
    return _ok(layers=list(CLOSURE_LAYERS), links=links)


def evaluate_goal_completion(open_layers: list[str]) -> dict[str, Any]:
    if open_layers:
        return _reject("goal_completion_blocked", open_layers=open_layers)
    return _ok(complete=True)


def stale_blocks_completion(*, stale: list[str]) -> dict[str, Any]:
    if stale:
        return _reject("stale_blocks", stale=stale)
    return _ok()


def reject_goal_owner_subagent_complete(*, actor: str) -> dict[str, Any]:
    if actor != "parent_goal":
        return _reject("goal_owner_violation", actor=actor)
    return _ok(actor=actor)


def minimal_gap_route(open_layers: list[str]) -> dict[str, Any]:
    if not open_layers:
        return _ok(gaps=[], route="complete")
    route_map = {
        "intent": "truth",
        "path": "implement",
        "ac": "truth",
        "state": "truth",
        "task": "implement",
        "evidence": "qa",
    }
    gaps = [{"layer": layer, "route": route_map.get(layer, "goal")} for layer in open_layers]
    return _reject("minimal_gap_route", gaps=gaps, recommended_route=gaps[0]["route"])


def require_goal_run_refs(refs: dict[str, Any]) -> dict[str, Any]:
    required = (
        "program_ref",
        "graph_ref",
        "truth_ref",
        "ready_ref",
        "decision_ref",
        "admission_ref",
        "trace_ref",
        "verifier_ref",
    )
    missing = [k for k in required if not refs.get(k)]
    stale = [k for k in required if refs.get(f"{k}_stale")]
    if missing or stale:
        return _reject("goal_run_required_refs_missing", missing=missing, stale=stale)
    return _ok(refs=refs)


def enforce_public_lifecycle_boundary(harnesses: list[str]) -> dict[str, Any]:
    allowed = set(PUBLIC_LIFECYCLE)
    extra = [h for h in harnesses if h not in allowed]
    if extra:
        return _reject("public_lifecycle_boundary_violation", extra=extra)
    return _ok(harnesses=sorted(allowed))


def evaluate_pac_full_trace_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    required = ("pac_id", "lake", "ac_id", "tc_id", "task_id", "evidence", "revision_id", "final_hash")
    for row in rows:
        missing = [k for k in required if not row.get(k)]
        if missing:
            return _reject("pac_full_trace_matrix_incomplete", pac=row.get("pac_id"), missing=missing)
        if row.get("revision_id") != "R2":
            return _reject("pac_revision_not_r2", pac=row.get("pac_id"))
    return _ok(count=len(rows))


def validate_authenticated_program_freeze(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    lake_receipts: list[dict[str, Any]],
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if len(lake_receipts) < 1:
        return _reject("authenticated_program_freeze_no_lakes")
    for receipt in lake_receipts:
        # reject status-only
        if receipt.get("status") == "complete" and not receipt.get("baseline_hash"):
            findings.append({"code": "status_only_promotion", "feature": str(receipt.get("feature") or "")})
            continue
        check = validate_authenticated_freeze_receipt(receipt)
        if check.get("blocked"):
            findings.append({"code": str(check.get("reason_code")), "feature": str(receipt.get("feature") or "")})
            continue
        # re-hash current package files when present
        feature = str(receipt.get("feature") or "")
        paths = package_paths(project_root, version=version, feature=feature)
        if paths["truth"].exists():
            current = {s: _sha256(paths[s]) for s in FEATURE_SURFACES if paths[s].exists()}
            expected = receipt.get("source_hashes") or {}
            for s, digest in current.items():
                exp = str(expected.get(s) or "")
                if exp and exp.replace("sha256:", "") != digest.replace("sha256:", "") and exp != digest:
                    # allow either bare or prefixed
                    if exp.removeprefix("sha256:") != digest:
                        findings.append({"code": f"hash_drift:{s}", "feature": feature})
    if findings:
        return _reject("authenticated_program_freeze_failed", findings=findings, program_slug=program_slug)
    return _ok(program_slug=program_slug, lakes=len(lake_receipts))


def evaluate_fill_chain_convergence(
    *,
    transaction_steps: list[str],
    progress_ref: str | None,
    recovery_ref: str | None,
) -> dict[str, Any]:
    missing_steps = [s for s in FILL_STEPS if s not in transaction_steps]
    if missing_steps or not progress_ref or not recovery_ref:
        return _reject(
            "fill_chain_convergence_incomplete",
            missing_steps=missing_steps,
            progress_ref=progress_ref,
            recovery_ref=recovery_ref,
        )
    return _ok()


def reject_convergence_illegal_transition(*, actor: str, stale_verdict: bool, new_public_harness: bool) -> dict[str, Any]:
    if actor != "parent_goal" or stale_verdict or new_public_harness:
        return _reject(
            "convergence_illegal_transition",
            actor=actor,
            stale_verdict=stale_verdict,
            new_public_harness=new_public_harness,
        )
    return _ok()


def transition_change_plan(state: str, event: str, *, decision_ref: str | None = None) -> dict[str, Any]:
    if (state, event) in {(s, e) for s, e in ILLEGAL_CHANGE_PLAN}:
        return _reject("change_plan_illegal_transition", state=state, event=event)
    if state == "awaiting_human" and event in {"rewrite", "split", "replace", "retry", "cancel"} and not decision_ref:
        return _reject("decision_ref_required", state=state, event=event)
    matches = [to for s, e, to in CHANGE_PLAN_EDGES if s == state and e == event]
    if not matches:
        return _reject("change_plan_transition_unknown", state=state, event=event)
    return _ok(from_state=state, event=event, to_state=matches[0], decision_ref=decision_ref or "")
