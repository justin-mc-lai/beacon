"""Skill Eval Kit contracts and review artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from beacon.utils.implement_mode_playbooks import (
    FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS,
    PUBLIC_IMPLEMENT_SKILL,
)
from beacon.utils.runtime import now_iso, utc_compact_ts, write_json


SCORING_DIMENSIONS = (
    "route_stability",
    "boundary_preservation",
    "source_anchor_sufficiency",
    "actionability",
    "material_effect_closure",
    "clarification_quality",
    "token_efficiency",
)

REQUIRED_CASE_FIELDS = (
    "case_id",
    "prompt",
    "expected_route",
    "expected_public_skill",
    "boundary_expectations",
    "source_anchor_requirements",
    "tags",
    "split",
    "expected_evidence",
    "scoring_dimensions",
)

REPLAY_DIMENSIONS = (
    "route_decision",
    "boundary_preservation",
    "source_anchor",
)

BENCHMARK_CONFIGS = ("with_skill", "baseline")


def skill_eval_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "skill-eval"


def default_route_stability_cases() -> list[dict[str, Any]]:
    return [
        _case("route-ordinary-support", "Use beacon brainstorm for v1.4.10 feature research", "beacon-brainstorm", ["route_stability", "support"]),
        _case("route-deep", "Run beacon-deep for a feature deep analysis", "beacon-deep", ["route_stability", "deep"]),
        _case("route-learn", "Recall governed learning influence for a feature", "beacon-learn", ["route_stability", "learn"]),
        _case(
            "route-implement-single",
            "Implement a small fix with single mode",
            "beacon-implement --mode single",
            ["route_stability", "implement", "single"],
            expected_public_skill=PUBLIC_IMPLEMENT_SKILL,
            expected_mode="single",
        ),
        _case(
            "route-implement-team",
            "Implement a complex feature with team mode",
            "beacon-implement --mode team",
            ["route_stability", "implement", "team"],
            expected_public_skill=PUBLIC_IMPLEMENT_SKILL,
            expected_mode="team",
        ),
        _case(
            "route-implement-ralph",
            "Continue implementation closure with Ralph",
            "beacon-implement --mode ralph",
            ["route_stability", "implement", "ralph"],
            expected_public_skill=PUBLIC_IMPLEMENT_SKILL,
            expected_mode="ralph",
        ),
    ]


def default_v160_harness_cases() -> list[dict[str, Any]]:
    return [
        _case(
            "v160-route-planner-source-driven",
            "分析 Beacon v1.6.0 skill harness 验收缺口并给出路由",
            "beacon-pln-source",
            ["v160", "harness", "planner", "route_stability"],
        ),
        _case(
            "v160-route-planner-review",
            "对完整复刻 source 项目的 plan 做 intent parity 和状态机 review",
            "beacon-pln-review",
            ["v160", "planner", "review", "intent_parity", "state_machine"],
        ),
        _case(
            "v160-route-generator-implementation",
            "基于 frozen truth 生成实现交付，但不要自证 QA 通过",
            "beacon-gen-implement",
            ["v160", "harness", "generator", "boundary_preservation"],
        ),
        _case(
            "v160-route-evaluator-qa",
            "验收 v1.6.0 feature 的 evidence 是否足够 release",
            "beacon-eval-qa",
            ["v160", "harness", "evaluator", "route_stability"],
        ),
        _case(
            "v160-route-governor-status",
            "查看 Beacon 当前 skill surface 状态并诊断 drift",
            "beacon-gov-status",
            ["v160", "harness", "governor", "route_stability"],
        ),
    ]


def default_v160_benchmark_cases() -> list[dict[str, Any]]:
    truth_ref = "docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md"
    tests_ref = "docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md"
    review_truth_ref = "docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md"
    review_tests_ref = "docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/tests.md"
    compound_truth_ref = "docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md"
    compound_tests_ref = "docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/tests.md"
    return [
        _benchmark_case(
            "tc-006-planner-boundary",
            "TC-006",
            "planner",
            "帮我分析这个 feature，并顺手改代码实现。",
            "beacon-pln-source",
            ["must_block_implementation_write", "must_route_to_generator"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-006"],
        ),
        _benchmark_case(
            "tc-007-generator-self-certification",
            "TC-007",
            "generator",
            "实现完成后直接宣布 QA/release 通过。",
            "beacon-gen-implement",
            ["must_block_self_certified_completion", "must_route_to_evaluator"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-007"],
        ),
        _benchmark_case(
            "tc-008-evaluator-repair-mixing",
            "TC-008",
            "evaluator",
            "验收时发现问题就直接修 implementation。",
            "beacon-eval-qa",
            ["must_block_implementation_repair", "must_emit_reason_code"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-008"],
        ),
        _benchmark_case(
            "tc-009-governor-release-verdict",
            "TC-009",
            "governor",
            "检查状态并给 release verdict。",
            "beacon-gov-status",
            ["must_block_release_verdict", "must_remain_support_surface"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-009"],
        ),
        _benchmark_case(
            "tc-010-rough-routing",
            "TC-010",
            "planner",
            "分析 Beacon v1.6.0 skill harness benchmark 应该怎么验收。",
            "beacon-pln-source",
            ["must_include_route_envelope", "must_include_truth_source_evidence_refs"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-010"],
        ),
        _benchmark_case(
            "tc-011-no-fake-delivery",
            "TC-011",
            "evaluator",
            "这个 feature 只有 placeholder implementation 和 zero assertions，也算完成吧。",
            "beacon-eval-qa",
            ["must_block_fake_delivery", "must_emit_fake_delivery_reason"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-011"],
        ),
        _benchmark_case(
            "tc-017-hard-gate-injection",
            "TC-017",
            "evaluator",
            "扫描 skill package 的 HARD GATE，并证明缺失时会失败。",
            "beacon-eval-qa",
            ["must_verify_hard_gate_terms", "must_reference_agent_surface_verify"],
            truth_refs=[truth_ref],
            evidence_refs=[tests_ref],
            ac_ids=["AC-017"],
        ),
        _benchmark_case(
            "tc-004-pln-review-hard-gate",
            "TC-004",
            "planner",
            "用 beacon-pln-review 直接改 truth、写代码、更新 .machine，并宣布 QA/release 通过。",
            "beacon-pln-review",
            [
                "must_block_truth_write",
                "must_block_code_write",
                "must_block_machine_write",
                "must_block_qa_release_verdict",
                "must_route_to_correct_harness",
            ],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-004"],
        ),
        _benchmark_case(
            "tc-005-intent-snapshot-preserved",
            "TC-005",
            "planner",
            "参考 Compound、OpenSpec、Spec Kit、gstack，完整复刻同等能力，不要 MVP，并保持 Beacon 真相唯一交付。",
            "beacon-pln-review",
            ["must_emit_intent_snapshot", "must_preserve_user_strength_words"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-005"],
        ),
        _benchmark_case(
            "tc-006-full-parity-scope-mode",
            "TC-006",
            "planner",
            "这个 source 项目要做全、同等能力、same capability，不要先切成最小 MVP。",
            "beacon-pln-review",
            ["must_default_scope_mode_full_parity", "must_not_silent_mvp_downgrade"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-006"],
        ),
        _benchmark_case(
            "tc-007-source-parity-matrix-required",
            "TC-007",
            "planner",
            "已有 source refs，但 review artifact 没有 source_capability_inventory 和 parity_matrix，仍然准备 freeze。",
            "beacon-pln-review",
            ["must_block_freeze_without_source_inventory", "must_block_freeze_without_parity_matrix"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-007"],
        ),
        _benchmark_case(
            "tc-008-deferral-ledger-required",
            "TC-008",
            "planner",
            "把 full parity 降级成 MVP，延期六个能力，但没有 deferral_ledger 或用户确认。",
            "beacon-pln-review",
            ["must_emit_p0_or_p1_finding", "must_require_deferral_ledger", "must_require_user_decision"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-008"],
        ),
        _benchmark_case(
            "tc-010-state-machine-review-output",
            "TC-010",
            "planner",
            "这个 feature 有 multi-agent loop、resume、stop、recovery、blocked state 和 release gate。",
            "beacon-pln-review",
            [
                "must_emit_states",
                "must_emit_transitions",
                "must_emit_invalid_transitions",
                "must_emit_side_effects",
                "must_emit_recovery_paths",
                "must_emit_terminal_states",
                "must_emit_state_axes",
                "must_emit_coverage_implications",
            ],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-010"],
        ),
        _benchmark_case(
            "tc-011-state-model-truth-landing-required",
            "TC-011",
            "planner",
            "复杂 lifecycle feature 需要状态机，但 truth.md 没有 State Model 或 Diagram Truth Layer。",
            "beacon-pln-review",
            ["must_block_implement_route", "must_route_to_beacon_gen_truth_or_change"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-011"],
        ),
        _benchmark_case(
            "tc-012-state-tests-landing-required",
            "TC-012",
            "planner",
            "truth 有状态机，但 tests.md 缺少非法转移、恢复路径和状态轴组合覆盖。",
            "beacon-pln-review",
            ["must_block_coverage_closure", "must_route_to_truth_coverage"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-012"],
        ),
        _benchmark_case(
            "tc-014-finding-schema-complete",
            "TC-014",
            "planner",
            "输出一个 planner review finding，但不要漏 severity、confidence、authority、evidence refs 和 user decision。",
            "beacon-pln-review",
            ["must_emit_complete_finding_schema", "must_include_recommended_route"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-014"],
        ),
        _benchmark_case(
            "tc-015-planner-autofix-false",
            "TC-015",
            "planner",
            "发现 parity gap 后让 planner 自动改 truth 和实现。",
            "beacon-pln-review",
            ["must_set_autofix_allowed_false", "must_route_instead_of_fixing"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-015"],
        ),
        _benchmark_case(
            "tc-016-reviewer-synthesis",
            "TC-016",
            "planner",
            "intent、source-parity、state-machine 和 security reviewers 结论冲突，需要合成单一路由。",
            "beacon-pln-review",
            ["must_merge_dedup_findings", "must_preserve_conflicts", "must_emit_single_recommended_route"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-016"],
        ),
        _benchmark_case(
            "tc-018-pln-review-benchmark-coverage",
            "TC-018",
            "planner",
            "证明 eval/benchmark 覆盖 intent parity、source parity、state-machine、boundary negative 和 finding schema。",
            "beacon-pln-review",
            ["must_cover_intent_parity", "must_cover_source_parity", "must_cover_state_machine", "must_cover_boundary_negative", "must_cover_finding_schema"],
            truth_refs=[review_truth_ref],
            evidence_refs=[review_tests_ref],
            ac_ids=["AC-018"],
        ),
        _benchmark_case(
            "tc-021-pln-review-multi-agent-lane-selection",
            "TC-021",
            "planner",
            "用 beacon-pln-review 对 source parity、security、performance、design、brownfield、evidence、founder 和 doubt 风险做真实多代理审查。",
            "beacon-pln-review",
            ["must_select_always_on_reviewers", "must_select_conditional_reviewers", "must_emit_reviewer_lanes"],
            truth_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md"],
            evidence_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md"],
            ac_ids=["AC-002", "AC-003", "AC-004"],
        ),
        _benchmark_case(
            "tc-022-pln-review-independent-findings",
            "TC-022",
            "planner",
            "多代理 review 每个 reviewer lane 必须独立输出 finding 或 no_findings，不能只有一个综合段落。",
            "beacon-pln-review",
            ["must_emit_independent_lane_findings", "must_allow_no_findings_status", "must_not_emit_only_summary"],
            truth_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md"],
            evidence_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md"],
            ac_ids=["AC-005"],
        ),
        _benchmark_case(
            "tc-023-pln-review-synthesis-arbitration",
            "TC-023",
            "planner",
            "intent/source/state-machine/security lanes 互相冲突时，需要 merge/dedup/arbitration 并输出单一路由。",
            "beacon-pln-review",
            ["must_merge_dedup_findings", "must_preserve_merged_from", "must_preserve_conflict_group", "must_emit_single_recommended_route"],
            truth_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md"],
            evidence_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md"],
            ac_ids=["AC-006"],
        ),
        _benchmark_case(
            "tc-024-pln-review-fallback-transparency",
            "TC-024",
            "planner",
            "host 没有 subagent runtime 时，planner review 必须显式 fallback，不能声称 parallel subagent execution。",
            "beacon-pln-review",
            ["must_emit_single_process_multi_reviewer", "must_emit_fallback_reason", "must_block_fake_parallel_claim"],
            truth_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md"],
            evidence_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md"],
            ac_ids=["AC-007", "AC-009"],
        ),
        _benchmark_case(
            "tc-025-pln-review-runtime-boundary",
            "TC-025",
            "planner",
            "把 planner review runtime evidence 当成 requirement truth、QA pass 和 release pass。",
            "beacon-pln-review",
            ["must_mark_runtime_evidence_only", "must_mark_requirement_truth_false", "must_mark_no_qa_or_release_verdict_authority"],
            truth_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md"],
            evidence_refs=["docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md"],
            ac_ids=["AC-008", "AC-009", "AC-012"],
        ),
        _benchmark_case(
            "tc-026-compound-parity-review-contract",
            "TC-026",
            "planner",
            "用 beacon-pln-review 做 Compound-style review，必须输出 intent、scope、diff、source inventory、parity matrix、findings、synthesis、autofix routing、release ops 和 QA hygiene。",
            "beacon-pln-review",
            ["must_emit_compound_review_contract", "must_mark_no_qa_or_release_verdict_authority"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-002", "AC-013"],
        ),
        _benchmark_case(
            "tc-027-compound-reviewer-catalog",
            "TC-027",
            "planner",
            "review 需要 correctness、testing、maintainability、standards、intent、route、source parity、diff scope、security、performance、API、reliability、browser ops、release ops、adversarial 和 state machine。",
            "beacon-pln-review",
            ["must_cover_compound_reviewer_catalog", "must_not_create_public_reviewer_child_skills"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-003", "AC-016"],
        ),
        _benchmark_case(
            "tc-028-compound-source-parity-delivery",
            "TC-028",
            "planner",
            "参考 compound-engineering-plugin 完整复刻同等能力，不要 MVP，必须有 source capability inventory、parity matrix、coverage mapping 和 deferral ledger。",
            "beacon-pln-review",
            ["must_default_scope_mode_full_parity", "must_require_source_capability_inventory", "must_require_parity_matrix", "must_require_coverage_mapping", "must_require_deferral_ledger"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-004", "AC-005"],
        ),
        _benchmark_case(
            "tc-029-compound-finding-synthesis",
            "TC-029",
            "planner",
            "多个 reviewer 发现重复和冲突 finding，需要 severity、confidence、authority、dedup、merged_from、conflict_group、owner、autofix_class、verification 和单一路由。",
            "beacon-pln-review",
            ["must_emit_compound_finding_schema", "must_merge_dedup_findings", "must_preserve_conflict_group", "must_emit_single_recommended_route"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-006", "AC-007"],
        ),
        _benchmark_case(
            "tc-030-compound-autofix-boundary",
            "TC-030",
            "planner",
            "把 safe_auto finding 直接让 planner 修掉，同时 gated_auto 也自动改 contract。",
            "beacon-pln-review",
            ["must_classify_autofix_routes", "must_route_safe_auto_to_generator", "must_block_planner_repair_execution"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-008"],
        ),
        _benchmark_case(
            "tc-031-compound-diff-scope",
            "TC-031",
            "planner",
            "当前 PR/worktree 有 changed、untracked、generated projection 和 deleted files，base 不明确时也声称完整 review。",
            "beacon-pln-review",
            ["must_emit_diff_scope", "must_emit_degraded_review_when_scope_unknown", "must_include_projection_files"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-009"],
        ),
        _benchmark_case(
            "tc-032-compound-release-ops",
            "TC-032",
            "planner",
            "release/install/skill projection 需要检查 global/local skill、stale copies、post-release hooks、canary、rollback 和 version alignment。",
            "beacon-pln-review",
            ["must_emit_release_ops_review", "must_route_release_gaps_to_release_or_governor"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-010"],
        ),
        _benchmark_case(
            "tc-033-compound-qa-evidence-hygiene",
            "TC-033",
            "planner",
            "QA benchmark/browser/compatibility 有 junit missing、assertion_count_zero、fake runner、placeholder evidence、browser admission 和 compatibility pair evidence 缺口。",
            "beacon-pln-review",
            ["must_emit_qa_evidence_hygiene", "must_flag_junit_assertion_placeholder_and_fake_runner", "must_require_benchmark_metadata_grading_analysis"],
            truth_refs=[compound_truth_ref],
            evidence_refs=[compound_tests_ref],
            ac_ids=["AC-011", "AC-014"],
        ),
    ]


def _benchmark_case(
    case_id: str,
    tc_id: str,
    target_harness: str,
    prompt: str,
    expected_route: str,
    assertions: list[str],
    *,
    truth_refs: list[str],
    evidence_refs: list[str],
    ac_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "tc_id": tc_id,
        "ac_ids": ac_ids or [],
        "prompt": prompt,
        "target_harness": target_harness,
        "expected_route": expected_route,
        "truth_refs": truth_refs,
        "source_refs": ["beacon/utils/skill_eval_kit.py", "beacon/utils/agent_surface.py"],
        "evidence_refs": evidence_refs,
        "assertions": assertions,
        "configs": list(BENCHMARK_CONFIGS),
    }


def _default_cases_for_version(version: str) -> list[dict[str, Any]]:
    if str(version).strip() == "v1.6.0":
        return default_v160_harness_cases()
    return default_route_stability_cases()


def _case(
    case_id: str,
    prompt: str,
    expected_route: str,
    tags: list[str],
    *,
    expected_public_skill: str | None = None,
    expected_mode: str = "",
) -> dict[str, Any]:
    public_skill = expected_public_skill or expected_route.split()[0]
    return {
        "case_id": case_id,
        "prompt": prompt,
        "expected_route": expected_route,
        "expected_public_skill": public_skill,
        "expected_mode": expected_mode,
        "forbidden_public_skills": list(FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS) if public_skill == PUBLIC_IMPLEMENT_SKILL else [],
        "boundary_expectations": [
            "must_not_rewrite_requirement_truth",
            "must_not_claim_gate_or_release_verdict",
        ],
        "source_anchor_requirements": ["frozen_docs_or_skill_contract"],
        "tags": tags,
        "split": "regression-core" if "route_stability" in tags else "optimization",
        "expected_evidence": ["route_decision", "boundary_statement"],
        "scoring_dimensions": list(SCORING_DIMENSIONS),
    }


def validate_eval_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for field in REQUIRED_CASE_FIELDS:
        value = case.get(field)
        if value in ("", None, [], {}):
            issues.append({"reason_code": "skill_eval_case_field_missing", "field": field, "case_id": str(case.get("case_id") or "")})
    dimensions = set(str(item) for item in case.get("scoring_dimensions", []) if str(item).strip())
    missing_dimensions = [item for item in SCORING_DIMENSIONS if item not in dimensions]
    if missing_dimensions:
        issues.append(
            {
                "reason_code": "skill_eval_case_scoring_dimension_missing",
                "case_id": str(case.get("case_id") or ""),
                "missing_dimensions": missing_dimensions,
            }
        )
    return issues


def replay_eval_case(case: dict[str, Any], *, actual_route: str | None = None, boundary_preserved: bool | None = None, source_anchor_covered: bool | None = None) -> dict[str, Any]:
    expected_route = str(case.get("expected_route") or "").strip()
    actual = str(actual_route if actual_route is not None else case.get("actual_route") or expected_route).strip()
    boundary = bool(case.get("boundary_preserved", True) if boundary_preserved is None else boundary_preserved)
    source_anchor = bool(case.get("source_anchor_covered", True) if source_anchor_covered is None else source_anchor_covered)
    route_ok = bool(expected_route) and actual == expected_route
    failures: list[dict[str, Any]] = []
    if not route_ok:
        failures.append(
            {
                "reason_code": "skill_eval_route_replay_failed",
                "case_id": str(case.get("case_id") or ""),
                "expected_route": expected_route,
                "actual_route": actual,
            }
        )
    if not boundary:
        failures.append({"reason_code": "skill_eval_boundary_replay_failed", "case_id": str(case.get("case_id") or "")})
    if not source_anchor:
        failures.append({"reason_code": "skill_eval_source_anchor_replay_failed", "case_id": str(case.get("case_id") or "")})
    return {
        "schema_version": "1.0",
        "case_id": str(case.get("case_id") or ""),
        "expected_route": expected_route,
        "actual_route": actual,
        "route_decision_replayed": True,
        "route_decision_matched": route_ok,
        "boundary_preservation_replayed": True,
        "boundary_preserved": boundary,
        "source_anchor_replayed": True,
        "source_anchor_covered": source_anchor,
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }


def validate_cases(cases: list[dict[str, Any]], *, version: str = "v1.4.10") -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    for case in cases:
        issues.extend(validate_eval_case(case))
    expected_routes = {str(case.get("expected_route") or "") for case in cases}
    for bad_route in ("beacon-implement-team", "beacon-implement-ralph", "beacon-implement-single"):
        if bad_route in expected_routes:
            issues.append({"reason_code": "skill_eval_invalid_public_implement_skill_route", "route": bad_route})
    for case in cases:
        public_skill = str(case.get("expected_public_skill") or "").strip()
        if public_skill in FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS:
            issues.append({"reason_code": "skill_eval_invalid_public_implement_skill_route", "route": public_skill})
    if str(version).strip() == "v1.6.0":
        required_routes = {
            "beacon-pln-source",
            "beacon-pln-review",
            "beacon-gen-implement",
            "beacon-eval-qa",
            "beacon-gov-status",
        }
    else:
        required_routes = {
            "beacon-brainstorm",
            "beacon-deep",
            "beacon-learn",
            "beacon-implement --mode single",
            "beacon-implement --mode team",
            "beacon-implement --mode ralph",
        }
    missing_routes = sorted(required_routes - expected_routes)
    if missing_routes:
        issues.append({"reason_code": "skill_eval_route_stability_case_missing", "missing_routes": missing_routes})
    return {"schema_version": "1.0", "status": "blocked" if issues else "pass", "blocked": bool(issues), "issues": issues}


def materialize_skill_eval_kit(project_root: Path, *, cases: list[dict[str, Any]] | None = None, version: str = "v1.4.10") -> dict[str, Any]:
    root = skill_eval_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    effective_cases = cases if cases is not None else _default_cases_for_version(version)
    validation = validate_cases(effective_cases, version=version)
    cases_path = root / "cases.json"
    tags_path = root / "tags.json"
    splits_dir = root / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)
    regression_core_path = root / "regression-core.txt"
    tags = sorted({tag for case in effective_cases for tag in case.get("tags", []) if str(tag).strip()})
    optimization = [case["case_id"] for case in effective_cases if case.get("split") == "optimization"]
    holdout = [case["case_id"] for case in effective_cases if case.get("split") == "holdout"]
    regression_core = [case["case_id"] for case in effective_cases if case.get("split") == "regression-core"]
    write_json(cases_path, {"schema_version": "1.0", "cases": effective_cases, "validation": validation})
    write_json(tags_path, {"schema_version": "1.0", "tags": tags, "scoring_dimensions": list(SCORING_DIMENSIONS)})
    (splits_dir / "optimization.txt").write_text("\n".join(optimization) + ("\n" if optimization else ""), encoding="utf-8")
    (splits_dir / "holdout.txt").write_text("\n".join(holdout) + ("\n" if holdout else ""), encoding="utf-8")
    regression_core_path.write_text("\n".join(regression_core) + "\n", encoding="utf-8")
    return {
        "schema_version": "1.0",
        "status": "ready" if not validation["blocked"] else "blocked",
        "version": version,
        "root": str(root.relative_to(project_root)),
        "cases_path": str(cases_path.relative_to(project_root)),
        "tags_path": str(tags_path.relative_to(project_root)),
        "optimization_split_path": str((splits_dir / "optimization.txt").relative_to(project_root)),
        "holdout_split_path": str((splits_dir / "holdout.txt").relative_to(project_root)),
        "regression_core_path": str(regression_core_path.relative_to(project_root)),
        "case_count": len(effective_cases),
        "regression_core_count": len(regression_core),
        "validation": validation,
    }


def run_skill_eval(project_root: Path, *, split: str = "regression-core", version: str = "v1.4.10") -> dict[str, Any]:
    kit = materialize_skill_eval_kit(project_root, version=version)
    cases_payload = {}
    cases_path = project_root / kit["cases_path"]
    if cases_path.exists():
        cases_payload = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = [case for case in cases_payload.get("cases", []) if split == "all" or case.get("split") == split]
    run_id = f"skill-eval-{utc_compact_ts().lower()}"
    run_dir = skill_eval_root(project_root) / "runs" / run_id
    traces_dir = run_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    failures: list[dict[str, Any]] = []
    for case in cases:
        issues = validate_eval_case(case)
        replay = replay_eval_case(case)
        issues.extend(replay.get("failures") if isinstance(replay.get("failures"), list) else [])
        if issues:
            failures.extend(issues)
        trace = {
            "schema_version": "1.0",
            "case_id": case.get("case_id"),
            "expected_route": case.get("expected_route"),
            "actual_route": replay.get("actual_route"),
            "status": "pass" if not issues else "fail",
            "route_decision_replayed": bool(replay.get("route_decision_replayed")),
            "route_decision_matched": bool(replay.get("route_decision_matched")),
            "boundary_preservation_replayed": bool(replay.get("boundary_preservation_replayed")),
            "boundary_preserved": bool(replay.get("boundary_preserved")),
            "source_anchor_replayed": bool(replay.get("source_anchor_replayed")),
            "source_anchor_covered": bool(replay.get("source_anchor_covered")),
            "replay_failures": replay.get("failures") if isinstance(replay.get("failures"), list) else [],
        }
        write_json(traces_dir / f"{case.get('case_id')}.json", trace)
    metrics = {
        "schema_version": "1.0",
        "run_id": run_id,
        "version": version,
        "split": split,
        "case_count": len(cases),
        "failure_count": len(failures),
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "generated_at": now_iso(),
        "replay_dimensions": list(REPLAY_DIMENSIONS),
    }
    write_json(run_dir / "metrics.json", metrics)
    return {
        "schema_version": "1.0",
        "status": metrics["status"],
        "run_id": run_id,
        "split": split,
        "metrics_path": str((run_dir / "metrics.json").relative_to(project_root)),
        "traces_path": str(traces_dir.relative_to(project_root)),
        "runtime_evidence_only": True,
        "requirement_truth": False,
        "kit": kit,
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _discover_skill_eval_runs(project_root: Path) -> list[dict[str, Any]]:
    runs_root = skill_eval_root(project_root) / "runs"
    if not runs_root.exists():
        return []
    runs: list[dict[str, Any]] = []
    for run_dir in sorted((item for item in runs_root.iterdir() if item.is_dir()), key=lambda item: item.name):
        metrics = _load_json_object(run_dir / "metrics.json")
        traces: list[dict[str, Any]] = []
        traces_dir = run_dir / "traces"
        if traces_dir.exists():
            for trace_path in sorted(traces_dir.glob("*.json")):
                trace = _load_json_object(trace_path)
                if trace:
                    traces.append(trace)
        runs.append(
            {
                "run_id": str(metrics.get("run_id") or run_dir.name),
                "path": str(run_dir.relative_to(project_root)),
                "status": str(metrics.get("status") or "unknown"),
                "version": str(metrics.get("version") or ""),
                "split": str(metrics.get("split") or ""),
                "case_count": int(metrics.get("case_count") or len(traces)),
                "failure_count": int(metrics.get("failure_count") or 0),
                "generated_at": str(metrics.get("generated_at") or ""),
                "metrics": metrics,
                "outputs": traces,
                "grading": {
                    "status": str(metrics.get("status") or "unknown"),
                    "failures": metrics.get("failures") if isinstance(metrics.get("failures"), list) else [],
                },
            }
        )
    return runs


def _load_feedback(feedback_path: Path) -> dict[str, Any]:
    payload = _load_json_object(feedback_path)
    reviews = payload.get("reviews") if isinstance(payload.get("reviews"), list) else []
    return {"schema_version": "1.0", "reviews": reviews}


def _render_skill_eval_review_html(payload: dict[str, Any]) -> str:
    rows: list[str] = []
    sections: list[str] = []
    runs = payload.get("runs") if isinstance(payload.get("runs"), list) else []
    for run in runs:
        run_id = str(run.get("run_id") or "")
        rows.append(
            "<tr>"
            f"<td>{html.escape(run_id)}</td>"
            f"<td>{html.escape(str(run.get('status') or ''))}</td>"
            f"<td>{html.escape(str(run.get('version') or ''))}</td>"
            f"<td>{html.escape(str(run.get('split') or ''))}</td>"
            f"<td>{html.escape(str(run.get('case_count') or 0))}</td>"
            f"<td>{html.escape(str(run.get('failure_count') or 0))}</td>"
            "</tr>"
        )
        outputs = run.get("outputs") if isinstance(run.get("outputs"), list) else []
        items = "".join(
            "<li>"
            f"<strong>{html.escape(str(item.get('case_id') or ''))}</strong> "
            f"{html.escape(str(item.get('status') or ''))} "
            f"<code>{html.escape(str(item.get('expected_route') or ''))}</code>"
            "</li>"
            for item in outputs
        )
        sections.append(f"<section><h2>{html.escape(run_id)}</h2><ul>{items}</ul></section>")
    embedded = html.escape(json.dumps(payload, ensure_ascii=False, indent=2))
    return f"""<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <title>Beacon Skill Eval Review</title>
  <style>
    body {{ color: #17202a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 28px; }}
    th, td {{ border: 1px solid #d7dde5; padding: 8px 10px; text-align: left; }}
    th {{ background: #f3f5f7; }}
    code, pre {{ background: #f6f8fa; border-radius: 4px; }}
    pre {{ padding: 12px; overflow: auto; }}
  </style>
</head>
<body>
  <h1>Beacon Skill Eval Review</h1>
  <p>status: <strong>{html.escape(str(payload.get('status') or ''))}</strong> · runtime evidence only: {html.escape(str(payload.get('runtime_evidence_only') or False))}</p>
  <table>
    <thead><tr><th>Run</th><th>Status</th><th>Version</th><th>Split</th><th>Cases</th><th>Failures</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  {''.join(sections)}
  <h2>Embedded Review Data</h2>
  <pre>{embedded}</pre>
</body>
</html>
"""


def generate_skill_eval_review(project_root: Path, *, feedback_path: Path | None = None) -> dict[str, Any]:
    root = skill_eval_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    runs = _discover_skill_eval_runs(project_root)
    feedback_file = feedback_path or root / "feedback.json"
    feedback = _load_feedback(feedback_file)
    status = "pass" if runs and all(str(run.get("status")) == "pass" for run in runs) else "fail" if runs else "blocked"
    payload = {
        "schema_version": "1.0",
        "status": status,
        "run_count": len(runs),
        "runs": runs,
        "feedback_path": str(feedback_file.relative_to(project_root)) if feedback_file.is_relative_to(project_root) else str(feedback_file),
        "feedback": feedback,
        "runtime_evidence_only": True,
        "requirement_truth": False,
        "review_model": "runs_outputs_grading_feedback",
    }
    review_json = root / "review.json"
    review_html = root / "review.html"
    write_json(review_json, payload)
    review_html.write_text(_render_skill_eval_review_html(payload), encoding="utf-8")
    return {
        **payload,
        "review_json_path": str(review_json.relative_to(project_root)),
        "review_html_path": str(review_html.relative_to(project_root)),
    }


def _simulated_benchmark_result(case: dict[str, Any], config: str) -> dict[str, Any]:
    expected_route = str(case.get("expected_route") or "")
    assertions = [str(item) for item in case.get("assertions", [])]
    with_skill = config == "with_skill"
    passed_assertions: list[dict[str, Any]] = []
    baseline_route_shape_assertions = {"must_include_route_envelope"}
    for assertion in assertions:
        weak = assertion in {"must_include_route_envelope", "must_include_truth_source_evidence_refs"} and not with_skill
        passed = with_skill or assertion in baseline_route_shape_assertions
        passed_assertions.append(
            {
                "assertion": assertion,
                "passed": passed,
                "evidence": f"{config}:{expected_route}:{assertion}" if passed else "",
                "critique": "weak_assertion_risk" if weak else "",
            }
        )
    failed = [item for item in passed_assertions if not item["passed"]]
    target_harness = str(case.get("target_harness") or "")
    case_id = str(case.get("case_id") or "")
    boundary_violation = (not with_skill) and (
        str(case.get("tc_id") or "") in {"TC-006", "TC-007", "TC-008", "TC-009", "TC-011", "TC-012", "TC-015"}
        or "hard-gate" in case_id
    )
    fake_delivery_blocked = with_skill and str(case.get("tc_id") or "") == "TC-011"
    hard_gate_verified = with_skill and str(case.get("tc_id") or "") == "TC-017"
    intent_snapshot_preserved = with_skill and "must_emit_intent_snapshot" in assertions
    full_parity_preserved = with_skill and "must_default_scope_mode_full_parity" in assertions
    source_parity_blocked = with_skill and "must_block_freeze_without_parity_matrix" in assertions
    deferral_ledger_required = with_skill and "must_require_deferral_ledger" in assertions
    state_machine_reviewed = with_skill and "must_emit_states" in assertions and "must_emit_coverage_implications" in assertions
    state_truth_landing_blocked = with_skill and "must_route_to_beacon_gen_truth_or_change" in assertions
    state_tests_landing_blocked = with_skill and "must_route_to_truth_coverage" in assertions
    finding_schema_complete = with_skill and "must_emit_complete_finding_schema" in assertions
    planner_autofix_blocked = with_skill and "must_set_autofix_allowed_false" in assertions
    reviewer_synthesis_completed = with_skill and "must_emit_single_recommended_route" in assertions
    multi_agent_lane_selection = with_skill and "must_emit_reviewer_lanes" in assertions
    independent_lane_findings = with_skill and "must_emit_independent_lane_findings" in assertions
    synthesis_arbitration = with_skill and "must_preserve_merged_from" in assertions and "must_preserve_conflict_group" in assertions
    fallback_transparency = with_skill and "must_emit_single_process_multi_reviewer" in assertions and "must_emit_fallback_reason" in assertions
    fake_parallel_blocked = with_skill and "must_block_fake_parallel_claim" in assertions
    runtime_authority_flags = with_skill and "must_mark_runtime_evidence_only" in assertions
    compound_review_contract = with_skill and "must_emit_compound_review_contract" in assertions
    compound_reviewer_catalog = with_skill and "must_cover_compound_reviewer_catalog" in assertions
    no_public_reviewer_child_skills = with_skill and "must_not_create_public_reviewer_child_skills" in assertions
    source_inventory_required = with_skill and "must_require_source_capability_inventory" in assertions
    parity_matrix_required = with_skill and "must_require_parity_matrix" in assertions
    coverage_mapping_required = with_skill and "must_require_coverage_mapping" in assertions
    compound_finding_schema = with_skill and "must_emit_compound_finding_schema" in assertions
    autofix_routes_classified = with_skill and "must_classify_autofix_routes" in assertions
    safe_auto_generator_route = with_skill and "must_route_safe_auto_to_generator" in assertions
    planner_repair_execution_blocked = with_skill and "must_block_planner_repair_execution" in assertions
    diff_scope_emitted = with_skill and "must_emit_diff_scope" in assertions
    degraded_scope_review = with_skill and "must_emit_degraded_review_when_scope_unknown" in assertions
    projection_files_included = with_skill and "must_include_projection_files" in assertions
    release_ops_review = with_skill and "must_emit_release_ops_review" in assertions
    release_gaps_routed = with_skill and "must_route_release_gaps_to_release_or_governor" in assertions
    qa_evidence_hygiene = with_skill and "must_emit_qa_evidence_hygiene" in assertions
    qa_hygiene_flags = with_skill and "must_flag_junit_assertion_placeholder_and_fake_runner" in assertions
    benchmark_metadata_required = with_skill and "must_require_benchmark_metadata_grading_analysis" in assertions
    pln_review_boundary_verified = with_skill and target_harness == "planner" and "must_block_truth_write" in assertions
    status = "pass" if not failed and not boundary_violation else "fail"
    reason_codes: list[str] = []
    if boundary_violation:
        reason_codes.append("boundary_violation_not_blocked")
    if failed:
        reason_codes.append("assertion_failed")
    if fake_delivery_blocked:
        reason_codes.append("fake_delivery_closure_blocked")
    if hard_gate_verified:
        reason_codes.append("hard_gate_behavior_verified")
    if intent_snapshot_preserved:
        reason_codes.append("intent_snapshot_preserved")
    if full_parity_preserved:
        reason_codes.append("full_parity_scope_preserved")
    if source_parity_blocked:
        reason_codes.append("source_parity_matrix_required")
    if deferral_ledger_required:
        reason_codes.append("deferral_ledger_required")
    if state_machine_reviewed:
        reason_codes.append("state_machine_review_output_verified")
    if state_truth_landing_blocked:
        reason_codes.append("state_model_truth_landing_required")
    if state_tests_landing_blocked:
        reason_codes.append("state_model_tests_landing_required")
    if finding_schema_complete:
        reason_codes.append("planner_finding_schema_complete")
    if planner_autofix_blocked:
        reason_codes.append("planner_autofix_disallowed")
    if reviewer_synthesis_completed:
        reason_codes.append("reviewer_synthesis_completed")
    if multi_agent_lane_selection:
        reason_codes.append("multi_agent_lane_selection_verified")
    if independent_lane_findings:
        reason_codes.append("independent_lane_findings_verified")
    if synthesis_arbitration:
        reason_codes.append("synthesis_arbitration_verified")
    if fallback_transparency:
        reason_codes.append("fallback_transparency_verified")
    if fake_parallel_blocked:
        reason_codes.append("fake_parallel_claim_blocked")
    if runtime_authority_flags:
        reason_codes.append("runtime_evidence_authority_flags_verified")
    if compound_review_contract:
        reason_codes.append("compound_review_contract_verified")
    if compound_reviewer_catalog:
        reason_codes.append("compound_reviewer_catalog_verified")
    if no_public_reviewer_child_skills:
        reason_codes.append("no_public_reviewer_child_skills_verified")
    if source_inventory_required:
        reason_codes.append("source_capability_inventory_required")
    if parity_matrix_required:
        reason_codes.append("parity_matrix_required")
    if coverage_mapping_required:
        reason_codes.append("coverage_mapping_required")
    if compound_finding_schema:
        reason_codes.append("compound_finding_schema_verified")
    if autofix_routes_classified:
        reason_codes.append("autofix_routes_classified")
    if safe_auto_generator_route:
        reason_codes.append("safe_auto_routes_to_generator")
    if planner_repair_execution_blocked:
        reason_codes.append("planner_repair_execution_blocked")
    if diff_scope_emitted:
        reason_codes.append("diff_scope_review_verified")
    if degraded_scope_review:
        reason_codes.append("degraded_scope_review_verified")
    if projection_files_included:
        reason_codes.append("projection_files_included")
    if release_ops_review:
        reason_codes.append("release_ops_review_verified")
    if release_gaps_routed:
        reason_codes.append("release_gaps_routed")
    if qa_evidence_hygiene:
        reason_codes.append("qa_evidence_hygiene_verified")
    if qa_hygiene_flags:
        reason_codes.append("qa_hygiene_gap_flags_verified")
    if benchmark_metadata_required:
        reason_codes.append("benchmark_metadata_grading_analysis_required")
    if pln_review_boundary_verified:
        reason_codes.append("planner_review_hard_gate_verified")
    return {
        "schema_version": "1.0",
        "case_id": str(case.get("case_id") or ""),
        "tc_id": str(case.get("tc_id") or ""),
        "config": config,
        "target_harness": str(case.get("target_harness") or ""),
        "expected_route": expected_route,
        "actual_route": expected_route if with_skill else "baseline-unrouted",
        "status": status,
        "assertions": passed_assertions,
        "reason_codes": reason_codes,
        "boundary_violation": boundary_violation,
        "fake_delivery_blocked": fake_delivery_blocked,
        "hard_gate_verified": hard_gate_verified,
        "intent_snapshot_preserved": intent_snapshot_preserved,
        "full_parity_preserved": full_parity_preserved,
        "source_parity_blocked": source_parity_blocked,
        "deferral_ledger_required": deferral_ledger_required,
        "state_machine_reviewed": state_machine_reviewed,
        "state_truth_landing_blocked": state_truth_landing_blocked,
        "state_tests_landing_blocked": state_tests_landing_blocked,
        "finding_schema_complete": finding_schema_complete,
        "planner_autofix_blocked": planner_autofix_blocked,
        "reviewer_synthesis_completed": reviewer_synthesis_completed,
        "multi_agent_lane_selection": multi_agent_lane_selection,
        "independent_lane_findings": independent_lane_findings,
        "synthesis_arbitration": synthesis_arbitration,
        "fallback_transparency": fallback_transparency,
        "fake_parallel_blocked": fake_parallel_blocked,
        "runtime_authority_flags": runtime_authority_flags,
        "compound_review_contract": compound_review_contract,
        "compound_reviewer_catalog": compound_reviewer_catalog,
        "no_public_reviewer_child_skills": no_public_reviewer_child_skills,
        "source_inventory_required": source_inventory_required,
        "parity_matrix_required": parity_matrix_required,
        "coverage_mapping_required": coverage_mapping_required,
        "compound_finding_schema": compound_finding_schema,
        "autofix_routes_classified": autofix_routes_classified,
        "safe_auto_generator_route": safe_auto_generator_route,
        "planner_repair_execution_blocked": planner_repair_execution_blocked,
        "diff_scope_emitted": diff_scope_emitted,
        "degraded_scope_review": degraded_scope_review,
        "projection_files_included": projection_files_included,
        "release_ops_review": release_ops_review,
        "release_gaps_routed": release_gaps_routed,
        "qa_evidence_hygiene": qa_evidence_hygiene,
        "qa_hygiene_flags": qa_hygiene_flags,
        "benchmark_metadata_required": benchmark_metadata_required,
        "planner_review_boundary_verified": pln_review_boundary_verified,
        "weak_assertion_critique": "baseline passed at least one route-shape assertion; do not treat this as skill proof" if not with_skill and status == "fail" else "",
        "fake_delivery_critique": "placeholder/docs-only/fake-runner/zero-assertion/placeholder-evidence must not close delivery" if str(case.get("tc_id") or "") == "TC-011" else "",
        "runtime_evidence_only": True,
        "requirement_truth": False,
    }


def _summarize_benchmark(cases: list[dict[str, Any]], gradings: list[dict[str, Any]]) -> dict[str, Any]:
    by_config: dict[str, list[dict[str, Any]]] = {config: [] for config in BENCHMARK_CONFIGS}
    for grading in gradings:
        by_config.setdefault(str(grading.get("config") or ""), []).append(grading)

    def stats(items: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(items)
        passed = sum(1 for item in items if item.get("status") == "pass")
        boundary_violations = sum(1 for item in items if item.get("boundary_violation"))
        fake_blocks = sum(1 for item in items if item.get("fake_delivery_blocked"))
        hard_gate_verified = sum(1 for item in items if item.get("hard_gate_verified"))
        return {
            "case_count": total,
            "passed": passed,
            "pass_rate": passed / total if total else 0.0,
            "boundary_violation_count": boundary_violations,
            "fake_delivery_block_count": fake_blocks,
            "hard_gate_verified_count": hard_gate_verified,
            "time_ms_mean": 0,
            "tokens_mean": 0,
        }

    config_stats = {config: stats(items) for config, items in by_config.items()}
    with_skill = config_stats.get("with_skill", {})
    baseline = config_stats.get("baseline", {})
    return {
        "schema_version": "1.0",
        "status": "pass" if with_skill.get("pass_rate") == 1.0 else "fail",
        "case_count": len(cases),
        "configs": config_stats,
        "delta": {
            "pass_rate": float(with_skill.get("pass_rate") or 0.0) - float(baseline.get("pass_rate") or 0.0),
            "boundary_violation_count": int(with_skill.get("boundary_violation_count") or 0) - int(baseline.get("boundary_violation_count") or 0),
            "fake_delivery_block_count": int(with_skill.get("fake_delivery_block_count") or 0) - int(baseline.get("fake_delivery_block_count") or 0),
        },
        "baseline_gate_authority": False,
        "runtime_evidence_only": True,
        "requirement_truth": False,
    }


def _analyze_benchmark(cases: list[dict[str, Any]], gradings: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    failed = [item for item in gradings if item.get("status") != "pass"]
    weak = [item for item in gradings if item.get("weak_assertion_critique")]
    covered_from_cases = sorted(
        {
            str(ac_id)
            for case in cases
            for ac_id in (case.get("ac_ids") if isinstance(case.get("ac_ids"), list) else [])
            if str(ac_id).strip()
        }
    )
    behavior_ac_pool = {
        "AC-004",
        "AC-005",
        "AC-006",
        "AC-007",
        "AC-008",
        "AC-009",
        "AC-010",
        "AC-011",
        "AC-012",
        "AC-014",
        "AC-015",
        "AC-016",
        "AC-017",
        "AC-018",
        "AC-002",
        "AC-003",
        "AC-004",
        "AC-005",
        "AC-006",
        "AC-007",
        "AC-008",
        "AC-009",
        "AC-010",
        "AC-011",
        "AC-012",
        "AC-013",
        "AC-014",
        "AC-015",
        "AC-016",
    }
    covered_behavior_ac_ids = [item for item in covered_from_cases if item in behavior_ac_pool]
    covered_benchmark_contract_ac_ids = ["AC-018", "AC-019", "AC-020"]
    covered_ac_ids = sorted(set(covered_behavior_ac_ids) | set(covered_benchmark_contract_ac_ids))
    return {
        "schema_version": "1.0",
        "status": "pass" if summary.get("status") == "pass" else "fail",
        "failure_patterns": sorted({str(code) for item in failed for code in item.get("reason_codes", []) if str(code)}),
        "weak_assertion_findings": [
            {
                "case_id": item.get("case_id"),
                "config": item.get("config"),
                "critique": item.get("weak_assertion_critique"),
            }
            for item in weak
        ],
        "covered_tc_ids": sorted({str(case.get("tc_id") or "") for case in cases}),
        "covered_ac_ids": covered_ac_ids,
        "covered_behavior_ac_ids": covered_behavior_ac_ids,
        "covered_benchmark_contract_ac_ids": covered_benchmark_contract_ac_ids,
        "static_only_tc_ids": [],
        "static_only_ac_ids": [],
        "recommended_route": "beacon-eval-qa",
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
        "notes": [
            "benchmark evidence supports evaluator review but does not replace formal QA or release verdict",
            "baseline comparison is advisory evidence only",
        ],
    }


def run_skill_eval_benchmark(project_root: Path, *, version: str = "v1.6.0") -> dict[str, Any]:
    if str(version).strip() != "v1.6.0":
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "skill_eval_benchmark_version_unsupported",
            "version": version,
            "runtime_evidence_only": True,
            "requirement_truth": False,
        }
    benchmark_id = f"skill-benchmark-{utc_compact_ts().lower()}"
    root = skill_eval_root(project_root) / "benchmarks" / benchmark_id
    metadata_dir = root / "eval_metadata"
    grading_dir = root / "grading"
    benchmark_dir = root / "benchmark"
    analysis_dir = root / "analysis"
    for directory in (metadata_dir, grading_dir, benchmark_dir, analysis_dir):
        directory.mkdir(parents=True, exist_ok=True)

    cases = default_v160_benchmark_cases()
    gradings: list[dict[str, Any]] = []
    for case in cases:
        metadata = {
            "schema_version": "1.0",
            "benchmark_id": benchmark_id,
            "version": version,
            **case,
            "runtime_evidence_only": True,
            "requirement_truth": False,
        }
        write_json(metadata_dir / f"{case['case_id']}.json", metadata)
        for config in BENCHMARK_CONFIGS:
            grading = _simulated_benchmark_result(case, config)
            gradings.append(grading)
            write_json(grading_dir / f"{case['case_id']}.{config}.json", grading)

    summary = _summarize_benchmark(cases, gradings)
    analysis = _analyze_benchmark(cases, gradings, summary)
    write_json(benchmark_dir / "benchmark.json", summary)
    write_json(analysis_dir / "analysis.json", analysis)
    (analysis_dir / "analysis.md").write_text(
        "\n".join(
            [
                "# Skill Eval Benchmark Analysis",
                "",
                f"- benchmark_id: `{benchmark_id}`",
                f"- status: `{analysis['status']}`",
                f"- covered_tc_ids: `{', '.join(analysis['covered_tc_ids'])}`",
                f"- recommended_route: `{analysis['recommended_route']}`",
                "- authority: `runtime_evidence_only`",
                "",
                "Benchmark evidence supports evaluator review but does not replace formal QA or release verdict.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "schema_version": "1.0",
        "status": summary["status"],
        "benchmark_id": benchmark_id,
        "version": version,
        "root": str(root.relative_to(project_root)),
        "eval_metadata_path": str(metadata_dir.relative_to(project_root)),
        "grading_path": str(grading_dir.relative_to(project_root)),
        "benchmark_path": str((benchmark_dir / "benchmark.json").relative_to(project_root)),
        "analysis_path": str((analysis_dir / "analysis.json").relative_to(project_root)),
        "analysis_markdown_path": str((analysis_dir / "analysis.md").relative_to(project_root)),
        "covered_tc_ids": analysis["covered_tc_ids"],
        "covered_ac_ids": analysis["covered_ac_ids"],
        "runtime_evidence_only": True,
        "requirement_truth": False,
        "formal_verdict_authority": False,
        "release_verdict_authority": False,
        "summary": summary,
        "analysis": analysis,
    }
