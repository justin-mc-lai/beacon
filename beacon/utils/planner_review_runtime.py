"""Planner-only multi-reviewer runtime artifacts for beacon-pln-review."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, utc_compact_ts, write_json


ALWAYS_ON_REVIEWERS: tuple[dict[str, str], ...] = (
    {"reviewer": "correctness-reviewer", "role": "Check logic, state transitions, edge cases, and error propagation."},
    {"reviewer": "testing-reviewer", "role": "Check test coverage, assertion strength, mock-only risk, and evidence shape."},
    {"reviewer": "maintainability-reviewer", "role": "Check complexity, coupling, naming, duplication, and long-term maintainability."},
    {"reviewer": "project-standards-reviewer", "role": "Check AGENTS, skill-creator, Beacon harness, package truth, and path conventions."},
    {"reviewer": "intent-fidelity", "role": "Preserve user intent and strength words."},
    {"reviewer": "scope-mode", "role": "Classify full_parity, mvp, patch, research, brownfield, or compatibility scope."},
    {"reviewer": "coverage-shape", "role": "Check whether acceptance can become behavior evidence."},
    {"reviewer": "route-boundary", "role": "Keep planner inside research and route recommendations."},
    {"reviewer": "state-machine", "role": "Review lifecycle, transitions, recovery, terminal states, and axes."},
)

CONDITIONAL_REVIEWERS: tuple[dict[str, Any], ...] = (
    {"reviewer": "source-parity", "signals": ("source", "oss", "完整复刻", "同等能力", "same capability", "full parity", "做全", "parity")},
    {"reviewer": "source-parity-reviewer", "signals": ("source", "oss", "完整复刻", "同等能力", "same capability", "full parity", "做全", "parity", "不要 mvp")},
    {"reviewer": "diff-scope-reviewer", "signals": ("diff", "pr", "branch", "base", "worktree", "untracked", "generated", "projection", "变更范围")},
    {"reviewer": "deferral-sovereignty", "signals": ("mvp", "defer", "later", "延期", "裁剪", "partial", "未覆盖")},
    {"reviewer": "security-reviewer", "signals": ("auth", "permission", "secret", "public route", "权限", "密钥", "敏感")},
    {"reviewer": "security-boundary", "signals": ("auth", "permission", "secret", "public route", "权限", "密钥", "敏感")},
    {"reviewer": "performance-reviewer", "signals": ("long-running", "concurrency", "cache", "bulk", "token", "time budget", "并发", "缓存")},
    {"reviewer": "performance-boundary", "signals": ("long-running", "concurrency", "cache", "bulk", "token", "time budget", "并发", "缓存")},
    {"reviewer": "api-contract-reviewer", "signals": ("api", "cli", "schema", "json", "command contract", "version surface")},
    {"reviewer": "reliability-reviewer", "signals": ("retry", "resume", "rollback", "canary", "timeout", "failure recovery", "恢复", "回滚")},
    {"reviewer": "browser-ops-reviewer", "signals": ("browser", "playwright", "cdp", "attached session", "sso", "live", "ui evidence")},
    {"reviewer": "release-ops-reviewer", "signals": ("release", "install", "skill projection", "post-release", "canary", "rollback", "stale copy", "发布", "安装")},
    {"reviewer": "adversarial-reviewer", "signals": ("challenge", "doubt", "adversarial", "质疑", "反例", "高风险")},
    {"reviewer": "design-flow", "signals": ("ui", "ux", "design", "screen", "cross-screen", "界面", "设计")},
    {"reviewer": "brownfield-contract", "signals": ("brownfield", "legacy", "migration", "cutover", "旧", "迁移", "兼容")},
    {"reviewer": "evidence-proof-shape", "signals": ("qa", "release", "evidence", "benchmark", "验收", "证据", "发布")},
    {"reviewer": "simplification-risk", "signals": ("simplify", "精简", "简化")},
    {"reviewer": "founder-business", "signals": ("founder", "ceo", "business", "roi", "商业")},
    {"reviewer": "adversarial-doubt", "signals": ("challenge", "doubt", "adversarial", "质疑", "反例")},
    {"reviewer": "adr-documentation", "signals": ("adr", "architecture decision", "决策记录")},
    {"reviewer": "context-engineering", "signals": ("context", "prompt drift", "source order", "上下文")},
)

ROUTE_PRIORITY = (
    "beacon-gen-truth",
    "beacon-gen-change",
    "beacon-gen-refreeze",
    "beacon-pln-friction",
    "beacon-gen-implement",
    "beacon-eval-qa",
    "beacon-eval-release",
    "beacon-gov-doctor",
    "beacon-gov-hooks",
    "defer/queue",
)
SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
AUTHORITY_ORDER = {
    "user_quote": 0,
    "package_truth": 1,
    "source_evidence": 2,
    "implementation_evidence": 3,
    "runtime_evidence": 4,
    "assumption": 5,
}


def _lower_blob(*values: Any) -> str:
    parts: list[str] = []
    for value in values:
        if isinstance(value, (list, tuple, set)):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(str(item) for pair in value.items() for item in pair)
        elif value is not None:
            parts.append(str(value))
    return "\n".join(parts).lower()


def _contains_any(blob: str, signals: tuple[str, ...]) -> bool:
    return any(signal.lower() in blob for signal in signals)


def select_reviewers(
    *,
    prompt: str,
    truth_refs: list[str] | None = None,
    source_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Select always-on and conditional planner reviewers."""
    blob = _lower_blob(prompt, truth_refs or [], source_refs or [], evidence_refs or [])
    selected: list[dict[str, Any]] = [
        {
            "reviewer": item["reviewer"],
            "role": item["role"],
            "trigger_reason": "always_on",
            "conditional": False,
        }
        for item in ALWAYS_ON_REVIEWERS
    ]
    for item in CONDITIONAL_REVIEWERS:
        signals = tuple(str(signal) for signal in item["signals"])
        if _contains_any(blob, signals):
            selected.append(
                {
                    "reviewer": str(item["reviewer"]),
                    "role": f"Conditional review for {item['reviewer']}.",
                    "trigger_reason": ",".join(signal for signal in signals if signal.lower() in blob) or "conditional_signal",
                    "conditional": True,
                }
            )
    return selected


def _route_for_reviewer(reviewer: str, blob: str) -> str:
    if reviewer in {"intent-fidelity", "scope-mode", "source-parity", "source-parity-reviewer", "state-machine"}:
        return "beacon-gen-change"
    if reviewer in {"route-boundary", "deferral-sovereignty"}:
        return "beacon-gen-change" if "truth" in blob or "freeze" in blob or "mvp" in blob else "beacon-pln-friction"
    if reviewer == "coverage-shape":
        return "beacon-eval-qa" if "qa" in blob or "evidence" in blob else "beacon-gen-change"
    if reviewer in {"diff-scope-reviewer", "release-ops-reviewer"}:
        return "beacon-gov-doctor" if "install" in blob or "projection" in blob or "worktree" in blob else "beacon-pln-friction"
    if reviewer in {"browser-ops-reviewer", "evidence-proof-shape", "testing-reviewer"}:
        return "beacon-eval-qa"
    if reviewer in {"security-boundary", "security-reviewer", "performance-boundary", "performance-reviewer", "api-contract-reviewer", "reliability-reviewer", "design-flow", "brownfield-contract"}:
        return "beacon-gen-change"
    return "beacon-pln-friction"


def _owner_for_route(route: str) -> str:
    if route.startswith("beacon-gen"):
        return "generator"
    if route.startswith("beacon-eval-qa"):
        return "evaluator"
    if route.startswith("beacon-eval-release"):
        return "release"
    if route.startswith("beacon-gov"):
        return "governor"
    if route == "defer/queue":
        return "human"
    return "planner"


def _autofix_class_for_reviewer(reviewer: str, route: str) -> str:
    if reviewer in {"maintainability-reviewer"} and route == "beacon-gen-implement":
        return "safe_auto"
    if reviewer in {"api-contract-reviewer", "security-reviewer", "security-boundary", "source-parity", "source-parity-reviewer"}:
        return "gated_auto"
    if reviewer in {"release-ops-reviewer"}:
        return "release"
    if reviewer in {"founder-business", "adversarial-doubt", "adversarial-reviewer"}:
        return "human"
    if route == "beacon-pln-friction" or route == "defer/queue":
        return "advisory"
    return "manual"


def _finding_for_lane(
    *,
    lane_id: str,
    reviewer: str,
    prompt: str,
    truth_refs: list[str],
    source_refs: list[str],
    evidence_refs: list[str],
) -> dict[str, Any] | None:
    blob = _lower_blob(prompt, truth_refs, source_refs, evidence_refs)
    issue_by_reviewer = {
        "correctness-reviewer": "Logic, state, edge-case, and error propagation risks need review.",
        "testing-reviewer": "Test coverage, assertion strength, and evidence shape need review.",
        "maintainability-reviewer": "Complexity, coupling, duplication, and naming risks need review.",
        "project-standards-reviewer": "AGENTS, skill-creator, Beacon harness, package truth, and path conventions need review.",
        "intent-fidelity": "Verify that strong user intent is not weakened into MVP.",
        "scope-mode": "Scope mode must be explicit before truth/change routing.",
        "coverage-shape": "Acceptance must map to behavior evidence, not static-only proof.",
        "route-boundary": "Planner must route instead of writing truth, code, .machine, QA, or release verdicts.",
        "state-machine": "State-machine implications must be reflected in truth and coverage.",
        "source-parity": "Source parity requires inventory and parity matrix before freeze or implement.",
        "source-parity-reviewer": "Source parity requires inventory, parity matrix, coverage mapping, and deferral ledger.",
        "diff-scope-reviewer": "Diff, PR, and worktree scope must be explicit before claiming complete review.",
        "deferral-sovereignty": "Scope cuts, MVP downgrade, or deferred capabilities require user decision.",
        "security-reviewer": "Security and permission boundaries need fail-closed review.",
        "security-boundary": "Security and permission boundaries need fail-closed review.",
        "performance-reviewer": "Long task and concurrency risks need bounded runtime evidence.",
        "performance-boundary": "Long task and concurrency risks need bounded runtime evidence.",
        "api-contract-reviewer": "CLI/API schema and version surface changes need contract review.",
        "reliability-reviewer": "Retries, resume, rollback, canary, and failure recovery need reliability review.",
        "browser-ops-reviewer": "Browser, SSO, CDP, attached-session, and live evidence admission need review.",
        "release-ops-reviewer": "Install, projection, stale copy, post-release hook, canary, and rollback evidence need review.",
        "adversarial-reviewer": "High-risk assumptions need adversarial review.",
        "design-flow": "Design and cross-screen state need flow coverage.",
        "brownfield-contract": "Brownfield or legacy migration requires authority map and cutover boundary.",
        "evidence-proof-shape": "Evidence and benchmark claims need proof-shape classification.",
        "simplification-risk": "Simplification must not erase parity or state branches.",
        "founder-business": "Business-level assumptions need explicit challenge.",
        "adversarial-doubt": "Assumptions need counterexample review.",
        "adr-documentation": "Durable architecture decisions need ADR-shaped capture.",
        "context-engineering": "Context/source order drift can change planner output.",
    }
    no_finding_signals = {"coverage-shape": ("static-only", "mock-only"), "route-boundary": ("write code", "qa pass", "release pass", ".machine")}
    if reviewer in no_finding_signals and not _contains_any(blob, no_finding_signals[reviewer]):
        return None
    severity = "P1" if reviewer in {"intent-fidelity", "source-parity", "source-parity-reviewer", "state-machine", "route-boundary"} else "P2"
    authority = "user_quote" if reviewer in {"intent-fidelity", "scope-mode", "deferral-sovereignty"} else "source_evidence" if source_refs else "package_truth"
    route = _route_for_reviewer(reviewer, blob)
    dedup_surface = "truth" if route.startswith("beacon-gen") or reviewer in {"intent-fidelity", "scope-mode", "state-machine"} else "support"
    digest = hashlib.sha256(f"{reviewer}:{dedup_surface}:{route}".encode("utf-8")).hexdigest()[:10]
    owner = _owner_for_route(route)
    autofix_class = _autofix_class_for_reviewer(reviewer, route)
    return {
        "finding_id": f"finding-{digest}",
        "reviewer": reviewer,
        "lane_id": lane_id,
        "severity": severity,
        "confidence": 75 if reviewer in {"intent-fidelity", "source-parity", "source-parity-reviewer", "state-machine"} else 50,
        "authority_level": authority,
        "issue": issue_by_reviewer.get(reviewer, "Planner reviewer finding."),
        "evidence_refs": [*truth_refs, *source_refs, *evidence_refs],
        "affected_truth_surface": dedup_surface,
        "affected_surface": dedup_surface,
        "recommended_route": route,
        "user_decision_required": reviewer in {"intent-fidelity", "scope-mode", "source-parity", "source-parity-reviewer", "deferral-sovereignty"},
        "autofix_allowed": False,
        "owner": owner,
        "autofix_class": autofix_class,
        "requires_verification": route in {"beacon-gen-implement", "beacon-eval-qa", "beacon-eval-release"} or autofix_class in {"safe_auto", "gated_auto"},
        "merged_from": [],
        "dedup_key": f"{dedup_surface}:{route}:{reviewer.split('-', 1)[0]}",
        "conflict_group": "",
    }


def _lane_result(
    *,
    reviewer_payload: dict[str, Any],
    prompt: str,
    truth_refs: list[str],
    source_refs: list[str],
    evidence_refs: list[str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    reviewer = str(reviewer_payload["reviewer"])
    lane_id = f"lane-{reviewer}"
    finding = _finding_for_lane(
        lane_id=lane_id,
        reviewer=reviewer,
        prompt=prompt,
        truth_refs=truth_refs,
        source_refs=source_refs,
        evidence_refs=evidence_refs,
    )
    lane = {
        "reviewer": reviewer,
        "lane_id": lane_id,
        "role": str(reviewer_payload.get("role") or ""),
        "trigger_reason": str(reviewer_payload.get("trigger_reason") or ""),
        "input_refs": [*truth_refs, *source_refs, *evidence_refs],
        "output_status": "finding" if finding else "no_findings",
        "finding_ids": [finding["finding_id"]] if finding else [],
        "confidence": finding["confidence"] if finding else 50,
        "authority_level": finding["authority_level"] if finding else "runtime_evidence",
        "runtime_evidence_ref": "",
    }
    return lane, finding


def synthesize_findings(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge duplicate reviewer findings and choose a conservative route."""
    merged: dict[str, dict[str, Any]] = {}
    for finding in findings:
        key = str(finding.get("dedup_key") or finding.get("finding_id") or "")
        if key not in merged:
            merged[key] = dict(finding)
            merged[key]["merged_from"] = [finding.get("lane_id")]
            continue
        existing = merged[key]
        existing["merged_from"] = sorted({*existing.get("merged_from", []), finding.get("lane_id")})
        if SEVERITY_ORDER.get(str(finding.get("severity")), 99) < SEVERITY_ORDER.get(str(existing.get("severity")), 99):
            existing["severity"] = finding.get("severity")
        if AUTHORITY_ORDER.get(str(finding.get("authority_level")), 99) < AUTHORITY_ORDER.get(str(existing.get("authority_level")), 99):
            existing["authority_level"] = finding.get("authority_level")
        existing["confidence"] = max(int(existing.get("confidence") or 0), int(finding.get("confidence") or 0))
        existing["user_decision_required"] = bool(existing.get("user_decision_required") or finding.get("user_decision_required"))
        existing_route = str(existing.get("recommended_route") or "")
        finding_route = str(finding.get("recommended_route") or "")
        if ROUTE_PRIORITY.index(finding_route) < ROUTE_PRIORITY.index(existing_route):
            existing["recommended_route"] = finding_route
            existing["owner"] = finding.get("owner")
        existing["requires_verification"] = bool(existing.get("requires_verification") or finding.get("requires_verification"))

    merged_findings = list(merged.values())
    routes = {str(item.get("recommended_route") or "") for item in merged_findings if str(item.get("recommended_route") or "")}
    conflict_group = ""
    if len(routes) > 1:
        conflict_group = "conflict-route-001"
        for item in merged_findings:
            item["conflict_group"] = conflict_group
    recommended_route = "beacon-pln-friction"
    for route in ROUTE_PRIORITY:
        if route in routes:
            recommended_route = route
            break
    highest_severity = "P3"
    for item in merged_findings:
        severity = str(item.get("severity") or "P3")
        if SEVERITY_ORDER.get(severity, 99) < SEVERITY_ORDER.get(highest_severity, 99):
            highest_severity = severity
    return {
        "status": "pass",
        "merged_findings": merged_findings,
        "finding_count": len(merged_findings),
        "conflict_groups": [conflict_group] if conflict_group else [],
        "highest_severity": highest_severity,
        "user_decision_required": any(bool(item.get("user_decision_required")) for item in merged_findings),
        "recommended_route": recommended_route,
        "route_rationale": "selected most conservative route from reviewer lane findings",
    }


def _scope_mode(prompt: str, source_refs: list[str]) -> str:
    blob = _lower_blob(prompt, source_refs)
    if _contains_any(blob, ("完整复刻", "同等能力", "same capability", "full parity", "做全", "parity", "不要 mvp")):
        return "full_parity"
    if _contains_any(blob, ("mvp", "最小", "minimal")):
        return "mvp"
    if _contains_any(blob, ("patch", "hotfix", "修复")):
        return "patch"
    if source_refs:
        return "brownfield_takeover"
    return "research"


def _intent_snapshot(prompt: str) -> dict[str, Any]:
    strength_words = [
        word
        for word in ("完整复刻", "同等能力", "做全", "不要 MVP", "不要 mvp", "full parity", "same capability", "parity")
        if word.lower() in prompt.lower()
    ]
    return {
        "user_prompt": prompt,
        "strength_words": strength_words,
        "silent_scope_change_allowed": False,
    }


def _source_capability_inventory(prompt: str, source_refs: list[str], scope_mode: str) -> list[dict[str, Any]]:
    from beacon.utils.oss_sync_inventory import build_source_capability_inventory

    return build_source_capability_inventory(prompt, source_refs, scope_mode)


def _parity_matrix(inventory: list[dict[str, Any]], scope_mode: str) -> list[dict[str, Any]]:
    if scope_mode != "full_parity":
        return []
    rows: list[dict[str, Any]] = []
    for item in inventory:
        for capability in item.get("capabilities", []):
            rows.append(
                {
                    "source_capability": capability,
                    "target_surface": "beacon-pln-review",
                    "truth_required": True,
                    "tests_required": True,
                    "status": "mapped",
                }
            )
    return rows


def _deferral_ledger(prompt: str, scope_mode: str) -> list[dict[str, Any]]:
    blob = prompt.lower()
    if scope_mode == "full_parity" and _contains_any(blob, ("mvp", "defer", "later", "延期", "裁剪", "partial")):
        return [
            {
                "capability": "unapproved_scope_reduction",
                "status": "blocked",
                "user_decision_required": True,
                "reason": "full parity cannot be silently reduced to MVP or deferred scope",
            }
        ]
    return []


def _diff_scope(project_root: Path) -> dict[str, Any]:
    git_dir = project_root / ".git"
    return {
        "base_ref": "",
        "base_reason": "base_ref_not_provided",
        "changed_files": [],
        "untracked_files": [],
        "generated_projection_files": [],
        "deleted_files": [],
        "touched_harness_surfaces": [],
        "high_risk_file_categories": [],
        "scope_confidence": 50 if git_dir.exists() else 0,
        "degraded": True,
    }


def _coverage_mapping(findings: list[dict[str, Any]], parity_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "source": row.get("source_capability"),
            "test_axis": "behavior",
            "required": bool(row.get("tests_required")),
            "status": "mapped",
        }
        for row in parity_rows
    ]
    if any(str(item.get("reviewer")) in {"testing-reviewer", "coverage-shape"} for item in findings):
        rows.append({"source": "qa_evidence_hygiene", "test_axis": "evidence_shape", "required": True, "status": "mapped"})
    return rows


def _autofix_routing(findings: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[str]] = {key: [] for key in ("safe_auto", "gated_auto", "manual", "advisory", "human", "release")}
    for finding in findings:
        buckets.setdefault(str(finding.get("autofix_class") or "manual"), []).append(str(finding.get("finding_id") or ""))
    return {
        "planner_executes_repairs": False,
        "generator_required_for_safe_auto": True,
        "buckets": buckets,
    }


def _release_ops_review(prompt: str) -> dict[str, Any]:
    blob = prompt.lower()
    triggered = _contains_any(blob, ("release", "install", "skill projection", "post-release", "canary", "rollback", "发布", "安装"))
    checks = [
        "repo_source_skill",
        "project_agents_skills_projection",
        "global_agent_skill_projection",
        "stale_duplicate_skill_copies",
        "post_release_hook_evidence",
        "canary_or_smoke_install_evidence",
        "rollback_or_cleanup_route",
        "version_surface_alignment",
    ]
    return {
        "triggered": triggered,
        "checks": checks,
        "missing_evidence_route": "beacon-eval-release or beacon-gov-doctor",
        "release_ready_authority": False,
    }


def _qa_evidence_hygiene(prompt: str) -> dict[str, Any]:
    blob = prompt.lower()
    trigger = _contains_any(blob, ("qa", "benchmark", "browser", "compatibility", "junit", "assertion", "fake runner", "placeholder"))
    checks = [
        "real_command",
        "junit_xml",
        "assertion_count_gt_zero",
        "fake_runner_absent",
        "placeholder_evidence_absent",
        "browser_admission_explained",
        "compatibility_pair_evidence",
        "benchmark_metadata_grading_analysis",
    ]
    reason_codes = []
    if trigger:
        if "junit" in blob:
            reason_codes.append("junit_required")
        if "assertion" in blob:
            reason_codes.append("assertion_count_required")
        if "fake runner" in blob:
            reason_codes.append("fake_runner_blocked")
        if "placeholder" in blob:
            reason_codes.append("placeholder_evidence_blocked")
    return {
        "triggered": trigger,
        "checks": checks,
        "reason_codes": reason_codes,
        "recommended_route": "beacon-eval-qa",
    }


def review_state_model() -> dict[str, Any]:
    return {
        "required": True,
        "states": [
            "ReviewRequested",
            "ContextResolved",
            "ScopeResolved",
            "SourceParityResolved",
            "ReviewerSelection",
            "LaneExecution",
            "FindingSynthesis",
            "RouteRecommendation",
            "Terminal",
        ],
        "allowed_transitions": [
            "ReviewRequested->ContextResolved",
            "ContextResolved->ScopeResolved",
            "ScopeResolved->SourceParityResolved",
            "SourceParityResolved->ReviewerSelection",
            "ContextResolved->ReviewerSelection",
            "ReviewerSelection->LaneExecution",
            "LaneExecution->FindingSynthesis",
            "FindingSynthesis->RouteRecommendation",
            "RouteRecommendation->Terminal",
        ],
        "invalid_transitions": [
            "ReviewRequested->LaneExecution",
            "ReviewRequested->ReviewerSelection",
            "SourceParityResolved->RouteRecommendation",
            "ReviewerSelection->FindingSynthesis",
            "LaneExecution->FindingSynthesis_without_lane_outputs",
            "FindingSynthesis->truth_write",
            "FindingSynthesis->code_write",
            "RouteRecommendation->Terminal_without_owner_or_route",
            "fallback->parallel_subagent_claim",
        ],
        "recovery_paths": [
            "missing_input_refs->beacon-pln-source",
            "missing_lane_output->conservative_synthesis",
            "subagent_unavailable->single_process_multi_reviewer",
            "schema_invalid->beacon-gen-implement",
        ],
        "terminal_states": [
            "review_ready_for_truth_change",
            "review_ready_for_implementation",
            "review_blocked_needs_user_decision",
            "review_degraded_scope_unknown",
            "review_queued_or_deferred",
        ],
        "state_axes": ["scope_resolution", "source_parity_resolution", "reviewer_selection", "lane_execution", "synthesis", "fallback"],
        "coverage_implications": [
            "lane selection",
            "independent findings",
            "synthesis arbitration",
            "fallback transparency",
            "planner boundary",
        ],
    }


def build_planner_review_runtime_artifact(
    *,
    project_root: Path,
    feature: str,
    version: str,
    prompt: str,
    truth_refs: list[str] | None = None,
    source_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    host_runtime: str = "codex",
    subagent_runtime_available: bool = False,
    write: bool = True,
) -> dict[str, Any]:
    """Build deterministic planner-only multi-reviewer runtime evidence."""
    truth_ref_list = list(truth_refs or [])
    source_ref_list = list(source_refs or [])
    evidence_ref_list = list(evidence_refs or [])
    selected = select_reviewers(prompt=prompt, truth_refs=truth_ref_list, source_refs=source_ref_list, evidence_refs=evidence_ref_list)
    lanes: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for reviewer_payload in selected:
        lane, finding = _lane_result(
            reviewer_payload=reviewer_payload,
            prompt=prompt,
            truth_refs=truth_ref_list,
            source_refs=source_ref_list,
            evidence_refs=evidence_ref_list,
        )
        lanes.append(lane)
        if finding:
            findings.append(finding)
    synthesis = synthesize_findings(findings)
    scope_mode = _scope_mode(prompt, source_ref_list)
    inventory = _source_capability_inventory(prompt, source_ref_list, scope_mode)
    parity_rows = _parity_matrix(inventory, scope_mode)
    review_id = f"pln-review-{utc_compact_ts().lower()}"
    execution_mode = "parallel_subagent_review" if subagent_runtime_available else "single_process_multi_reviewer"
    fallback_reason = "" if subagent_runtime_available else "subagent_runtime_unavailable_explicit_deterministic_fallback"
    artifact_rel = Path(".beacon") / "state" / "planner-review" / feature / f"{review_id}.json"
    artifact_path = project_root / artifact_rel
    for lane in lanes:
        lane["runtime_evidence_ref"] = str(artifact_rel)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "review_id": review_id,
        "execution_mode": execution_mode,
        "host_runtime": host_runtime,
        "subagent_runtime_available": subagent_runtime_available,
        "fallback_reason": fallback_reason,
        "input_context": {
            "prompt": prompt,
            "truth_refs": truth_ref_list,
            "source_refs": source_ref_list,
            "evidence_refs": evidence_ref_list,
        },
        "intent_snapshot": _intent_snapshot(prompt),
        "scope_mode": scope_mode,
        "diff_scope": _diff_scope(project_root),
        "source_capability_inventory": inventory,
        "selected_reviewers": [item["reviewer"] for item in selected],
        "reviewer_lanes": lanes,
        "findings": findings,
        "synthesis": synthesis,
        "coverage_mapping": _coverage_mapping(findings, parity_rows),
        "autofix_routing": _autofix_routing(findings),
        "release_ops_review": _release_ops_review(prompt),
        "qa_evidence_hygiene": _qa_evidence_hygiene(prompt),
        "state_model": review_state_model(),
        "parity_matrix": parity_rows,
        "deferral_ledger": _deferral_ledger(prompt, scope_mode),
        "recommended_route": synthesis.get("recommended_route"),
        "user_decision_required": bool(synthesis.get("user_decision_required")),
        "planner_boundary": {
            "truth_write_allowed": False,
            "code_write_allowed": False,
            "machine_write_allowed": False,
            "qa_verdict_allowed": False,
            "release_verdict_allowed": False,
        },
        "evidence_paths": {"runtime": str(artifact_rel)},
        "runtime_evidence_only": True,
        "requirement_truth": False,
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
        "generated_at": now_iso(),
    }
    if write:
        write_json(artifact_path, payload)
    return payload
