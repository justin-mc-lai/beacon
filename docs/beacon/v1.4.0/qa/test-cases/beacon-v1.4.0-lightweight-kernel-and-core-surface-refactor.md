# Test Cases: Beacon v1.4.0 lightweight kernel and core surface refactor

## Overview

**Feature**: Beacon v1.4.0 lightweight kernel and core surface refactor
**Test Type**: ALL
**Version**: v1.4.0
**Generated**: 2026-05-06 20:35
**Requested Mode**: auto
**Effective Mode**: requirement-freeze
**Fallback Reason**: machine-contract-not-yet-implemented
**Memory Context**: v1.3.12 runtime closure + v1.4.0 lightweight kernel refactor
**Primary Truth**: docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md
**Upstream User Story**: docs/beacon/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md
**Global Boundary Truth**: docs/beacon/global-boundaries.md
**AC Matrix JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | contract | `python3 -m pytest -q tests/test_v140_truth_contract_projection.py -k "truth_root_is_docs_only"` | `docs/beacon/<version>/**/*.md` remains the only canonical frozen truth root | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-001.json` |
| AC-002 | TC-002 | contract | `python3 -m pytest -q tests/test_v140_truth_contract_projection.py -k "compiled_contract_is_primary_machine_entry"` | `gate / implement / qa / release` resolve from one compiled contract entry instead of fragmented mirrors | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-002.json` |
| AC-003 | TC-003 | integration | `python3 -m pytest -q tests/test_v140_truth_contract_projection.py -k "legacy_projections_are_optional"` | sqlite / pocketbase / board / legacy mirrors are marked optional projections and excluded from truth closure | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-003.json` |
| AC-004 | TC-004 | regression | `python3 -m pytest -q tests/test_v140_truth_contract_projection.py -k "no_projection_reverse_write"` | no projection or support read-model can write back truth-defining state | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-004.json` |
| AC-101 | TC-005 | unit | `python3 -m pytest -q tests/test_v140_change_kernel.py -k "stable_change_identity"` | every truth change gets a stable `change_id` bound to version, feature, and baseline revision | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-005.json` |
| AC-102 | TC-006 | contract | `python3 -m pytest -q tests/test_v140_change_kernel.py -k "change_contract_fields"` | machine-readable change contract contains reason, affected refs, layers, verification refs, and archive status | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-006.json` |
| AC-103 | TC-007 | integration | `python3 -m pytest -q tests/test_v140_change_kernel.py -k "single_change_thread"` | reopen, revise, refreeze, delta implement, delta qa, and release recheck stay on one change thread | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-007.json` |
| AC-104 | TC-008 | integration | `python3 -m pytest -q tests/test_v140_change_kernel.py -k "per_change_archive_and_version_rollup"` | per-change closure rolls up into version summary without losing per-change canonical truth | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-008.json` |
| AC-201 | TC-009 | contract | `python3 -m pytest -q tests/test_v140_change_surface.py -k "borrow_container_not_public_cli_sprawl"` | Beacon borrows change-container semantics without adding a new public primary command family | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-009.json` |
| AC-202 | TC-010 | integration | `python3 -m pytest -q tests/test_v140_change_surface.py -k "support_surface_projects_change_state"` | `help / status / report / gate` project current change id, change state, blocked reason, and next action | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-010.json` |
| AC-203 | TC-011 | regression | `python3 -m pytest -q tests/test_v140_change_surface.py -k "change_is_router_not_stage"` | `beacon-change` remains a routing surface and is not exposed as a new lifecycle stage | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-011.json` |
| AC-204 | TC-012 | integration | `python3 -m pytest -q tests/test_v140_change_surface.py -k "drift_routes_back_to_change_loop"` | truth drift from support or execution surfaces consistently routes back into the change loop | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-012.json` |
| AC-301 | TC-013 | unit | `python3 -m pytest -q tests/test_v140_goal_runtime.py -k "goal_is_optional_host_capability"` | goal integration activates only on Codex-capable hosts and falls back explicitly on others | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-013.json` |
| AC-302 | TC-014 | contract | `python3 -m pytest -q tests/test_v140_goal_runtime.py -k "requirement_package_maps_to_goal"` | goal objective is traceable to the requirement package and implementation plan rather than free text | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-014.json` |
| AC-303 | TC-015 | regression | `python3 -m pytest -q tests/test_v140_goal_runtime.py -k "goal_not_completion_truth"` | `goal.complete` alone cannot satisfy implement complete, QA pass, or release pass | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-015.json` |
| AC-304 | TC-016 | integration | `python3 -m pytest -q tests/test_v140_goal_runtime.py -k "budget_limited_closure"` | `budget_limited` forces explicit closure, handoff, or blocking instead of silent continuation | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-016.json` |
| AC-401 | TC-017 | integration | `python3 -m pytest -q tests/test_v140_ralph_closure.py -k "ralph_reads_goal_state_each_round"` | Ralph rounds can read the current goal objective and status before execution decisions | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-017.json` |
| AC-402 | TC-018 | contract | `python3 -m pytest -q tests/test_v140_ralph_closure.py -k "stop_semantics_are_unified"` | Ralph `release_ready / human_blocked / budget_exhausted` semantics align with goal and verification states | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-018.json` |
| AC-403 | TC-019 | integration | `python3 -m pytest -q tests/test_v140_ralph_closure.py -k "qa_handoff_before_release_ready"` | completed implementation without acceptance enters explicit QA handoff instead of direct release-ready | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-019.json` |
| AC-404 | TC-020 | contract | `python3 -m pytest -q tests/test_v140_ralph_closure.py -k "execution_audit_chain"` | Ralph rounds, goal states, and QA handoff refs remain queryable execution audit evidence | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-020.json` |
| AC-501 | TC-021 | integration | `python3 -m pytest -q tests/test_v140_task_ledger.py -k "human_readable_task_ledger_exists"` | implement stage emits a human-readable tasks progress ledger | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-021.json` |
| AC-502 | TC-022 | unit | `python3 -m pytest -q tests/test_v140_task_ledger.py -k "checkbox_or_equivalent_progress_state"` | task ledger exposes incomplete and complete status with checkbox or equivalent low-friction semantics | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-022.json` |
| AC-503 | TC-023 | integration | `python3 -m pytest -q tests/test_v140_task_ledger.py -k "ledger_shows_progress_and_blockers"` | task ledger shows `N/M progress`, current task, blocked tasks, and next task | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-023.json` |
| AC-504 | TC-024 | regression | `python3 -m pytest -q tests/test_v140_task_ledger.py -k "interruption_recovery_from_ledger"` | humans and agents can resume execution from the ledger after interruption without re-discovery overhead | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-024.json` |
| AC-601 | TC-025 | contract | `python3 -m pytest -q tests/test_v140_task_projection_boundary.py -k "canonical_plan_is_source"` | canonical execution task identity still comes from implementation plan JSON | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-025.json` |
| AC-602 | TC-026 | contract | `python3 -m pytest -q tests/test_v140_task_projection_boundary.py -k "machine_progress_artifact_is_source"` | machine aggregation still comes from progress JSON or equivalent machine progress artifact | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-026.json` |
| AC-603 | TC-027 | regression | `python3 -m pytest -q tests/test_v140_task_projection_boundary.py -k "task_ledger_is_human_projection_only"` | `tasks-<feature>.md` stays a human projection and does not define machine truth | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-027.json` |
| AC-604 | TC-028 | contract | `python3 -m pytest -q tests/test_v140_task_projection_boundary.py -k "gate_does_not_trust_checkbox_alone"` | gate requires evidence, traceability, and QA closure beyond task checkbox completion | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-028.json` |
| AC-701 | TC-029 | integration | `python3 -m pytest -q tests/test_v140_global_boundary_surface.py -k "human_boundary_surface_exists"` | Beacon exposes an explicit human-usable global boundary and context surface | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-029.json` |
| AC-702 | TC-030 | integration | `python3 -m pytest -q tests/test_v140_global_boundary_surface.py -k "boundary_explain_and_calibrate"` | the surface supports boundary explanation, over-boundary judgment, and context calibration | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-030.json` |
| AC-703 | TC-031 | contract | `python3 -m pytest -q tests/test_v140_global_boundary_surface.py -k "layer_separation_global_version_feature"` | the surface distinguishes global, version, and feature-level constraints | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-031.json` |
| AC-704 | TC-032 | regression | `python3 -m pytest -q tests/test_v140_global_boundary_surface.py -k "boundary_surface_is_support_only"` | the boundary surface is support-only and never promoted to a new lifecycle stage | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-032.json` |
| AC-801 | TC-033 | regression | `python3 -m pytest -q tests/test_v140_boundary_governance.py -k "no_freeform_truth_config"` | human boundary operations cannot directly write arbitrary temporary input into canonical truth | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-033.json` |
| AC-802 | TC-034 | unit | `python3 -m pytest -q tests/test_v140_boundary_governance.py -k "placement_judgment_route"` | Beacon can decide whether a principle belongs in global boundaries, version PRD, or brainstorm/research | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-034.json` |
| AC-803 | TC-035 | contract | `python3 -m pytest -q tests/test_v140_boundary_governance.py -k "canonical_writeback_route"` | formal global-boundary changes require an explicit canonical writeback route | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-035.json` |
| AC-804 | TC-036 | integration | `python3 -m pytest -q tests/test_v140_boundary_governance.py -k "boundary_change_auditability"` | boundary change suggestions are fully traceable and auditable | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-036.json` |
| AC-901 | TC-037 | integration | `python3 -m pytest -q tests/test_v140_support_surface.py -k "artifact_focus_first"` | support surfaces answer which artifact is currently blocking or active | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-037.json` |
| AC-902 | TC-038 | integration | `python3 -m pytest -q tests/test_v140_support_surface.py -k "next_action_with_reason_and_command"` | support surfaces answer next action, reason, and suggested command | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-038.json` |
| AC-903 | TC-039 | integration | `python3 -m pytest -q tests/test_v140_support_surface.py -k "unlock_visibility"` | support surfaces explain what executing the next action will unlock | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-039.json` |
| AC-904 | TC-040 | regression | `python3 -m pytest -q tests/test_v140_support_surface.py -k "machine_detail_is_secondary"` | machine/read-model details remain available but are not the default human-facing output | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-040.json` |
| AC-1001 | TC-041 | contract | `python3 -m pytest -q tests/test_v140_artifact_recovery.py -k "artifact_state_ladder"` | key artifacts can be represented as ready, blocked, or completed | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-041.json` |
| AC-1002 | TC-042 | integration | `python3 -m pytest -q tests/test_v140_artifact_recovery.py -k "blocked_artifact_has_dependency_reason"` | blocked artifacts explain the missing dependency that prevents advancement | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-042.json` |
| AC-1003 | TC-043 | integration | `python3 -m pytest -q tests/test_v140_artifact_recovery.py -k "recovery_anchor_is_task_or_artifact_level"` | interruption recovery anchors to task or artifact identity rather than only a run id | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-043.json` |
| AC-1004 | TC-044 | regression | `python3 -m pytest -q tests/test_v140_artifact_recovery.py -k "recovery_prevents_duplicate_work"` | recovery information prevents humans and agents from redoing already completed work | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-044.json` |
| AC-1101 | TC-045 | contract | `python3 -m pytest -q tests/test_v140_skill_taxonomy.py -k "four_tier_taxonomy_defined"` | Beacon defines the four-tier skill taxonomy: lifecycle core, support core, advanced project-specific, internal maintainer | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-045.json` |
| AC-1102 | TC-046 | integration | `python3 -m pytest -q tests/test_v140_skill_taxonomy.py -k "taxonomy_shared_across_surfaces"` | docs, router, help/status, and skill discovery consume the same taxonomy source | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-046.json` |
| AC-1103 | TC-047 | contract | `python3 -m pytest -q tests/test_v140_skill_taxonomy.py -k "skill_has_audience_and_visibility_tier"` | every skill carries intended audience and visibility tier metadata | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-047.json` |
| AC-1104 | TC-048 | regression | `python3 -m pytest -q tests/test_v140_skill_taxonomy.py -k "no_flat_default_skill_list"` | Beacon does not expose every skill as the same-level default human entry | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-048.json` |
| AC-1201 | TC-049 | contract | `python3 -m pytest -q tests/test_v140_skill_visibility.py -k "existence_and_visibility_are_separate"` | capability existence is governed separately from default human-surface visibility | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-049.json` |
| AC-1202 | TC-050 | integration | `python3 -m pytest -q tests/test_v140_skill_visibility.py -k "contextual_recommendation_only"` | advanced and internal skills are recommended contextually rather than exposed by default | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-050.json` |
| AC-1203 | TC-051 | contract | `python3 -m pytest -q tests/test_v140_skill_visibility.py -k "public_surface_is_frozen"` | the default public skill surface is explicitly frozen and versionable | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-051.json` |
| AC-1204 | TC-052 | integration | `python3 -m pytest -q tests/test_v140_skill_visibility.py -k "visibility_rules_are_auditable"` | visibility rules can be documented, verified, and evolved with audit evidence | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-052.json` |
| AC-1301 | TC-053 | contract | `python3 -m pytest -q tests/test_v140_skill_positioning.py -k "iteration_governance_is_internal"` | `beacon-iteration-governance` is classified as internal or maintainer-only | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-053.json` |
| AC-1302 | TC-054 | contract | `python3 -m pytest -q tests/test_v140_skill_positioning.py -k "prototype_reconcile_is_advanced"` | `beacon-prototype-reconcile` is classified as advanced or project-specific | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-054.json` |
| AC-1303 | TC-055 | regression | `python3 -m pytest -q tests/test_v140_skill_positioning.py -k "neither_is_default_public_surface"` | neither skill appears on the default public skill surface | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-055.json` |
| AC-1304 | TC-056 | integration | `python3 -m pytest -q tests/test_v140_skill_positioning.py -k "conditional_routing_rules"` | router or support surfaces recommend those skills only under the specified maintenance or drift conditions | `.beacon/evidence/test-results/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor/TC-056.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-101 |
| TC-006 | Pending | from AC-102 |
| TC-007 | Pending | from AC-103 |
| TC-008 | Pending | from AC-104 |
| TC-009 | Pending | from AC-201 |
| TC-010 | Pending | from AC-202 |
| TC-011 | Pending | from AC-203 |
| TC-012 | Pending | from AC-204 |
| TC-013 | Pending | from AC-301 |
| TC-014 | Pending | from AC-302 |
| TC-015 | Pending | from AC-303 |
| TC-016 | Pending | from AC-304 |
| TC-017 | Pending | from AC-401 |
| TC-018 | Pending | from AC-402 |
| TC-019 | Pending | from AC-403 |
| TC-020 | Pending | from AC-404 |
| TC-021 | Pending | from AC-501 |
| TC-022 | Pending | from AC-502 |
| TC-023 | Pending | from AC-503 |
| TC-024 | Pending | from AC-504 |
| TC-025 | Pending | from AC-601 |
| TC-026 | Pending | from AC-602 |
| TC-027 | Pending | from AC-603 |
| TC-028 | Pending | from AC-604 |
| TC-029 | Pending | from AC-701 |
| TC-030 | Pending | from AC-702 |
| TC-031 | Pending | from AC-703 |
| TC-032 | Pending | from AC-704 |
| TC-033 | Pending | from AC-801 |
| TC-034 | Pending | from AC-802 |
| TC-035 | Pending | from AC-803 |
| TC-036 | Pending | from AC-804 |
| TC-037 | Pending | from AC-901 |
| TC-038 | Pending | from AC-902 |
| TC-039 | Pending | from AC-903 |
| TC-040 | Pending | from AC-904 |
| TC-041 | Pending | from AC-1001 |
| TC-042 | Pending | from AC-1002 |
| TC-043 | Pending | from AC-1003 |
| TC-044 | Pending | from AC-1004 |
| TC-045 | Pending | from AC-1101 |
| TC-046 | Pending | from AC-1102 |
| TC-047 | Pending | from AC-1103 |
| TC-048 | Pending | from AC-1104 |
| TC-049 | Pending | from AC-1201 |
| TC-050 | Pending | from AC-1202 |
| TC-051 | Pending | from AC-1203 |
| TC-052 | Pending | from AC-1204 |
| TC-053 | Pending | from AC-1301 |
| TC-054 | Pending | from AC-1302 |
| TC-055 | Pending | from AC-1303 |
| TC-056 | Pending | from AC-1304 |

---

## Freeze Gate Notes

- 当前 QA 包已经把 `v1.4.0` 的减负目标落成正式验收对象，而不是停留在架构偏好：
  - `truth / contract / projection` 分层已进入 fail-closed 检查面
  - `change` 已被编译成事务内核而不是松散 change loop
  - `goal -> Ralph -> QA handoff -> gate` 的执行闭环已进入统一断言面
  - `tasks ledger` 被明确限制为人类投影，不得升级为第二执行真相源
  - `global-boundaries` 人类面只允许解释、校准、路由，不允许自由改写 canonical truth
  - `skill taxonomy / visibility governance` 已成为可验证 contract，而不是隐性经验
- 当前文档声明的是 coverage freeze，不宣称实现已完成或测试已执行通过。
- 如果后续实现无法同时满足以下约束，则本 feature 不应通过 gate：
  - `docs/beacon/<version>/**/*.md` 仍为唯一 truth root
  - `implement` 仍为唯一实现入口
  - `qa` 仍为唯一验收入口
  - `gate` 仍以 evidence 与 traceability 为准，而不是依赖 goals、checkboxes 或 support projection

## Diagram Truth

- `branch-flow`
  - 覆盖 `truth freeze -> compiled contract -> implement -> qa -> gate -> release`
  - 覆盖 `change reopen -> revise -> refreeze -> delta implement -> delta qa -> release recheck`
  - 覆盖 `support/boundary surface -> route back to canonical change or truth layer`
- `decision-priority`
  - `truth > machine contract > execution projection > support projection`
  - `gate/qa verdict > goal state > task ledger checkbox`
  - `capability existence > visibility routing > default public exposure`
