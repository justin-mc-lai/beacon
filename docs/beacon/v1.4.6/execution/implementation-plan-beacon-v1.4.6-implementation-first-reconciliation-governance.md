# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.6-implementation-first-reconciliation-governance-r1`
- feature: `beacon-v1.4.6-implementation-first-reconciliation-governance`
- version: `v1.4.6`
- revision_id: `R1`
- baseline_hash: `sha256:c46b59d8d50fcab62b3c69401e28cd1695dc0fe1121c66c0fb6ea34f0fa8fd56`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-implementation-first-reconciliation-governance-R1`
- delivery_baseline_source_hash: `sha256:df9ea8e093c41b533bdcc06401f65b07ff5330ff38c558452b61e1c94e102bf1`
- plan_hash: `sha256:b30fe645f71c72a845dc606e223477857c2bf7c0f22410c0127be32982dbf780`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.4.6/user-story/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- prd: `docs/beacon/v1.4.6/prd/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- test_case: `docs/beacon/v1.4.6/qa/test-cases/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- ac_matrix: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-implementation-first-reconciliation-governance.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-implementation-first-reconciliation-governance.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-implementation-first-reconciliation-governance.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.6/.machine/user-story/beacon-v1.4.6-implementation-first-reconciliation-governance.json`
- architecture_blueprint: `docs/beacon/v1.4.6/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.6-implementation-first-reconciliation-governance" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- run_command: `beacon implement team-run "beacon-v1.4.6-implementation-first-reconciliation-governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.6-implementation-first-reconciliation-governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- qa_team_command: `beacon qa team-run "beacon-v1.4.6-implementation-first-reconciliation-governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.6`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.6/.machine/execution/git-workflow-beacon-v1.4.6-implementation-first-reconciliation-governance.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.6/research/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- source_artifact: `docs/beacon/v1.4.6/.machine/user-story/beacon-v1.4.6-implementation-first-reconciliation-governance.json`
- section_count: `0`

## Tasks

### ITASK-001 — FR-001 Beacon 必须定义 implementation-first reconciliation 为异常恢复语义
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-RECON46-001, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-012, TC-013, TC-014
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-RECON46-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Reconciliation 必须通过 `beacon-change` 路由
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-RECON46-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-RECON46-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Beacon 必须冻结 reconciliation artifact contract
- status: `planned`
- mapped_ac_ids: AC-003, AC-004
- mapped_test_ids: TC-RECON46-003, TC-RECON46-004
- mapped_scenario_ids: SC-003, SC-004
- mapped_qa_case_ids: TC-RECON46-003, TC-RECON46-004
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 补 truth 后必须重新收口受影响 proof
- status: `planned`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-RECON46-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-RECON46-005
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Beacon 不得把 reconciliation 伪装成正常 truth-first 交付
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
