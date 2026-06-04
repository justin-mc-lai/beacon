# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract-r5`
- feature: `beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract`
- version: `v1.4.8`
- revision_id: `R5`
- baseline_hash: `sha256:57087f23a043c8356bdf378eaa61a2d0c02c70eec3acfb9e3a50045069c23d75`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.8-beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract-R5`
- delivery_baseline_source_hash: `sha256:6bb9254995a90bf35ae677e5c43055615dad43bfbc0a6f552c4ca3de1e395ebd`
- plan_hash: `sha256:20be089ae1cdbbb8a7a9033afa6b0983c83ed11361260caf2ea91f8fd8776f79`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.8/user-story/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- prd: `docs/beacon/archive/v1.4.8/prd/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- test_case: `docs/beacon/archive/v1.4.8/qa/test-cases/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.8/.machine/execution/revision-delta-beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.8/.machine/qa/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.8/.machine/qa/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.8/.machine/qa/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.8/.machine/user-story/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.8/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract" --project-root . --version v1.4.8`
- run_command: `beacon implement team-run "beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract" --project . --version v1.4.8`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract" --project . --version v1.4.8`
- qa_team_command: `beacon qa team-run "beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract" --project . --version v1.4.8`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.8`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.4.8/.machine/execution/git-workflow-beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.8/.machine/user-story/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.json`
- section_count: `2`
- architecture: 执行材料契约层 / 定义 `execution/index.md`、`architecture-blueprint.md`、`service-slice-map.md`、`git-workflow-*`、`technical-review-contract-*` 等执行 host 材料的最低存在与字段要求。 / 子 skill 材料闭环层
- decision_priority: Frozen truth 高于 support finding。 / 显式冻结事实高于 default seed。 / Canonical execution host 高于 side dossier。

## Revision Delta
- revision_id: `R5`
- source_revision_id: `R4`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.8/.machine/execution/revision-delta-beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.json`

## Tasks

### ITASK-001 — FR-001 Beacon 必须恢复 execution host required surface contract
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-MATGATE48-001, TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021, TC-022, TC-MATGATE48-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-MATGATE48-001, TC-MATGATE48-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Beacon 必须阻断缺失或漂移的 architecture blueprint projection
- status: `completed`
- mapped_ac_ids: AC-004, AC-003
- mapped_test_ids: TC-MATGATE48-004, TC-MATGATE48-003
- mapped_scenario_ids: SC-003, SC-004
- mapped_qa_case_ids: TC-MATGATE48-003, TC-MATGATE48-004
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Beacon 必须冻结 branch / service / worktree explicit-fact gate
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-MATGATE48-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-MATGATE48-009
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 Beacon 必须识别 weak fact source
- status: `completed`
- mapped_ac_ids: AC-011, AC-005
- mapped_test_ids: TC-MATGATE48-011, TC-MATGATE48-005
- mapped_scenario_ids: SC-005, SC-011
- mapped_qa_case_ids: TC-MATGATE48-005, TC-MATGATE48-011
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Beacon 必须冻结 per-subskill material effect registry
- status: `completed`
- mapped_ac_ids: AC-006, AC-007, AC-010
- mapped_test_ids: TC-MATGATE48-006, TC-MATGATE48-007, TC-MATGATE48-010
- mapped_scenario_ids: SC-006, SC-007, SC-010
- mapped_qa_case_ids: TC-MATGATE48-006, TC-MATGATE48-007, TC-MATGATE48-010
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 Beacon 必须让 support finding 进入采纳契约
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-MATGATE48-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-MATGATE48-008
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 Beacon 必须让 branch governance 更新走 canonical writeback
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TC-MATGATE48-012
- mapped_scenario_ids: SC-012
- mapped_qa_case_ids: TC-MATGATE48-012
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — FR-008 Beacon 必须阻断 open artifact update obligations
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

### ITASK-009 — FR-009 Beacon 必须提供 no silent pass diagnostics
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

### ITASK-010 — FR-010 Beacon 必须保持 support surface 边界
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
