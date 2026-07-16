# Beacon Implementation Plan

- plan_id: `plan-beacon-freeze-integrity-drift-repair-v163-r1`
- feature: `beacon-freeze-integrity-drift-repair-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:3ed29c42171993fafda33450ad2633bcd5d7734ca4452ebf636d9388dc06af58`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-freeze-integrity-drift-repair-v163-R1`
- delivery_baseline_source_hash: `sha256:cff46d027c83fa5138d3c2b5a9199751ad967649252bde9491b44089a00b2c63`
- plan_hash: `sha256:8123a207a67d12107926f60b8b7293c22f6ef48603b6454549ea386e75159e9c`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md`
- prd: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md`
- test_case: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/tests.md`
- truth: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md`
- tests: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/tests.md`
- tasks: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/tasks.md`
- evidence: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163`
- ac_matrix: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-freeze-integrity-drift-repair-v163.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-freeze-integrity-drift-repair-v163.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-freeze-integrity-drift-repair-v163.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-freeze-integrity-drift-repair-v163.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.3/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-freeze-integrity-drift-repair-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-freeze-integrity-drift-repair-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-freeze-integrity-drift-repair-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-freeze-integrity-drift-repair-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.3`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.3/.machine/execution/git-workflow-beacon-freeze-integrity-drift-repair-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/research/beacon-freeze-integrity-drift-repair-v163.md`
- source_artifact: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-freeze-integrity-drift-repair-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 feature 包 `parser_contract` 为 resolver 声明版本（v1 或 v2）时通过；仅未知版本报 `parse...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-FI-001, TC-FI-002, TC-FI-003
- mapped_scenario_ids: SC-001, SC-002, SC-003
- mapped_qa_case_ids: TC-FI-001, TC-FI-002, TC-FI-003
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 evidence 含 `gate_truth` 子串（路径/文件名）**不**触发 `evidence_forbidden_gate_tr...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-FI-010, TC-FI-011
- mapped_scenario_ids: SC-004, SC-005
- mapped_qa_case_ids: TC-FI-010, TC-FI-011
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 tests.md 行 Layer=integration + `pytest` command 不被 `soft_test_asserti...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-FI-020, TC-FI-021
- mapped_scenario_ids: SC-006, SC-007
- mapped_qa_case_ids: TC-FI-020, TC-FI-021
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 `evidence_authority_table_missing` 与 `evidence_invalid_authority` 的 d...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-FI-030, TC-FI-031
- mapped_scenario_ids: SC-008, SC-009
- mapped_qa_case_ids: TC-FI-030, TC-FI-031
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 已冻结 v1.6.2 feature 包修复后仍 pass validation（**Must**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-FI-040
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: TC-FI-040
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 已冻结的 `beacon-gate-truth-model-alignment-v163` 包修复后仍 pass validation（*...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-FI-050
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: TC-FI-050
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 真实 forbidden field 违规（authority=source_of_truth）与真实 weak-assertion（无...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-FI-060
- mapped_scenario_ids: SC-012
- mapped_qa_case_ids: TC-FI-060
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
