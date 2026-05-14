# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance-r1`
- feature: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- version: `v1.4.6`
- revision_id: `R1`
- baseline_hash: `sha256:dc7f92ee445b2187595014e3c5b0fdea7d9b1e740f744da5ca9317359f9d99c4`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance-R1`
- delivery_baseline_source_hash: `sha256:febfb253b7b66c4493add208d38eea8684307309fc3444a09e14f2d5870da6e8`
- plan_hash: `sha256:7c8c6a62119405756bd834932b9556d34d85951864729dfd418e0fce67fcff24`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- prd: `docs/beacon/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- test_case: `docs/beacon/v1.4.6/qa/test-cases/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- ac_matrix: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.6/.machine/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.json`
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
- plan_command: `beacon implement team-plan "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- run_command: `beacon implement team-run "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
- qa_team_command: `beacon qa team-run "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.6`
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
- git_workflow_ref: `docs/beacon/v1.4.6/.machine/execution/git-workflow-beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.4.6/research/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- source_artifact: `docs/beacon/v1.4.6/.machine/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.json`
- section_count: `0`

## Tasks

### ITASK-001 — FR-001 Beacon 必须冻结 project-local QA feedback ledger
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-AUTO46-001, TC-019, TC-020, TC-021, TC-022, TC-023, TC-024, TC-025, TC-026, TC-027, TC-AUTO46-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-AUTO46-001, TC-AUTO46-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Beacon 必须暴露 feedback ledger 的 public CLI surface
- status: `completed`
- mapped_ac_ids: AC-009, AC-003
- mapped_test_ids: TC-AUTO46-009, TC-AUTO46-003
- mapped_scenario_ids: SC-003, SC-009
- mapped_qa_case_ids: TC-AUTO46-003, TC-AUTO46-009
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Beacon 必须暴露 queue update 的 public CLI surface
- status: `completed`
- mapped_ac_ids: AC-016, AC-018, AC-004
- mapped_test_ids: TC-AUTO46-016, TC-AUTO46-018, TC-AUTO46-004
- mapped_scenario_ids: SC-004, SC-016, SC-018
- mapped_qa_case_ids: TC-AUTO46-004, TC-AUTO46-016, TC-AUTO46-018
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 Queue update 必须保持显式治理
- status: `completed`
- mapped_ac_ids: AC-005, AC-006, AC-013
- mapped_test_ids: TC-AUTO46-005, TC-AUTO46-006, TC-AUTO46-013
- mapped_scenario_ids: SC-005, SC-006, SC-013
- mapped_qa_case_ids: TC-AUTO46-005, TC-AUTO46-006, TC-AUTO46-013
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Nightly QA wrapper 必须在 QA 后刷新 ledger 与 queue
- status: `completed`
- mapped_ac_ids: AC-015, AC-014
- mapped_test_ids: TC-AUTO46-015, TC-AUTO46-014
- mapped_scenario_ids: SC-014, SC-015
- mapped_qa_case_ids: TC-AUTO46-014, TC-AUTO46-015
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 Gated implement wrapper 至少必须消费 queue update flow
- status: `completed`
- mapped_ac_ids: AC-007, AC-008, AC-012
- mapped_test_ids: TC-AUTO46-007, TC-AUTO46-008, TC-AUTO46-012
- mapped_scenario_ids: SC-007, SC-008, SC-012
- mapped_qa_case_ids: TC-AUTO46-007, TC-AUTO46-008, TC-AUTO46-012
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 Capability reporting 必须披露 feedback loop surface
- status: `completed`
- mapped_ac_ids: AC-010, AC-011, AC-017
- mapped_test_ids: TC-AUTO46-010, TC-AUTO46-011, TC-AUTO46-017
- mapped_scenario_ids: SC-010, SC-011, SC-017
- mapped_qa_case_ids: TC-AUTO46-010, TC-AUTO46-011, TC-AUTO46-017
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — FR-008 该补充必须继续保持 Beacon/host boundary
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — FR-009 Beacon 必须暴露 project-local scaffold generation entrypoint
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — FR-010 Scaffold output 必须是目标项目定制的可运行资产
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — FR-011 Scaffold overwrite 行为必须保守
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — FR-012 Beacon 必须冻结 executor capability matrix
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — FR-013 Scaffold 必须支持 executor profile 生成
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — FR-014 Beacon 不得把 unsupported executor 伪装成当前可直接跑 implement/qa
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — FR-015 Beacon 必须冻结 shared automation summary schema
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-016 — FR-016 Beacon 必须暴露 shared summary 的 public CLI surface
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-017 — FR-017 Scaffolded wrapper 与通知 helper 必须消费同一 summary schema
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-018 — FR-018 Beacon 必须暴露 human-facing automation toolkit surface
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
