# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance-r2`
- feature: `Beacon v1.3.10 project topology and version-branch metadata transaction governance`
- version: `v1.3.10`
- revision_id: `R2`
- baseline_hash: `sha256:0c0dc5aa337957fc02ae51e97d926e8a8c2a3d502d72d8d9e960c642dfde7e6f`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.10-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance-R2`
- delivery_baseline_source_hash: `sha256:683819b4930b4ae2316210f02a051a5654e2d85ac9b264f21e864d2aec0e043d`
- plan_hash: `sha256:2da83b71ef0a133e077713b29a5fdb6611990cbda68eabe0a14eaea84e7d12cf`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- prd: `docs/beacon/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- test_case: `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- revision_delta: `docs/beacon/v1.3.10/.machine/execution/revision-delta-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.json`
- ac_matrix: `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/v1.3.10/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "Beacon v1.3.10 project topology and version-branch metadata transaction governance" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.3.10`
- run_command: `beacon implement team-run "Beacon v1.3.10 project topology and version-branch metadata transaction governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.3.10`
- dev_run_command: `beacon implement dev-run "Beacon v1.3.10 project topology and version-branch metadata transaction governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.3.10`
- qa_team_command: `beacon qa team-run "Beacon v1.3.10 project topology and version-branch metadata transaction governance" --project /Users/apple/Developer/Personal/products/beacon --version v1.3.10`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.10`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.10/.machine/execution/git-workflow-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `True`
- revision_delta_ref: `docs/beacon/v1.3.10/.machine/execution/revision-delta-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.json`

## Tasks

### ITASK-001 — FR-001 Beacon 必须定义项目拓扑与分支治理的 project-version metadata schema
- status: `completed`
- mapped_ac_ids: AC-002, AC-001
- mapped_test_ids: TC-002, TC-001, TC-045, TC-046
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004
- mapped_qa_case_ids: TC-001, TC-002, TC-045, TC-046
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-002 — FR-002 Beacon 必须把拓扑与分支元信息持久化为 canonical transaction truth
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-003 — FR-003 Beacon 必须提供确定性的人类面元信息 support surface，并支持增删改查与校验
- status: `completed`
- mapped_ac_ids: AC-019, AC-003, AC-004
- mapped_test_ids: TEST-019, TC-003, TC-041, TC-047
- mapped_scenario_ids: SC-005, SC-006, SC-007
- mapped_qa_case_ids: TC-003, TC-041, TC-047
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-004 — FR-004 Prompt 层与 runtime 层必须确定性消费元信息
- status: `completed`
- mapped_ac_ids: AC-012, AC-005, AC-013, AC-015, AC-017
- mapped_test_ids: TEST-012, TC-042, TEST-013, TEST-015, TEST-017
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-042
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-005 — FR-005 `implement`、`qa`、`release` 必须在 metadata contract 违例时硬阻断
- status: `completed`
- mapped_ac_ids: AC-014, AC-006, AC-007, AC-022
- mapped_test_ids: TEST-014, TC-043, TC-044, TEST-022
- mapped_scenario_ids: SC-009, SC-010
- mapped_qa_case_ids: TC-043, TC-044
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-006 — FR-006 元信息投影必须保持 human、machine、sqlite 三面一致
- status: `completed`
- mapped_ac_ids: AC-027
- mapped_test_ids: TEST-027
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-007 — FR-007 Cross-project artifact reporting 必须是 metadata-safe
- status: `completed`
- mapped_ac_ids: AC-031, AC-030
- mapped_test_ids: TEST-031, TEST-030
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-008 — FR-008 `friction-intake` 输出契约必须显式携带绝对路径元信息
- status: `completed`
- mapped_ac_ids: AC-032, AC-036, AC-034, AC-035
- mapped_test_ids: TEST-032, TEST-036, TEST-034, TEST-035
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-009 — FR-009 domain classifier 必须新增元信息治理规则
- status: `completed`
- mapped_ac_ids: AC-038, AC-039, AC-011, AC-010, AC-008, AC-016, AC-018, AC-020, AC-021, AC-023, AC-024, AC-025, AC-026, AC-028, AC-029, AC-033, AC-037, AC-040, AC-041, AC-042, AC-043, AC-044
- mapped_test_ids: TEST-038, TEST-039, TEST-011, TEST-010, TEST-008, TEST-016, TEST-018, TEST-020, TEST-021, TEST-023, TEST-024, TEST-025, TEST-026, TEST-028, TEST-029, TEST-033, TEST-037, TEST-040, TEST-041, TEST-042, TEST-043, TEST-044
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: topology_axis, single_repo, monorepo, metadata_scope_axis, global_project_metadata, version_scoped_metadata, resolved_metadata_view, requirement_package_axis, human_docs_synced, machine_package_synced, revision_baseline_bound, drift_blocked, remediation_axis, beacon_change, doctor_sync_materials, doctor_verify_materials, execution_surface_axis, implement, qa, release, help, status, real_project_validation

### ITASK-010 — Cleanup superseded surfaces from R1
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: -
- reference_only_services: -
- target_modules: -
- diagram_review_gates: -
- required_cleanup: `True`
- source_revision_id: `R1`
- revision_delta_ref: `docs/beacon/v1.3.10/.machine/execution/revision-delta-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.json`
- cleanup_surface_labels: AC-005: Beacon 能为每个参与 service 保存该版本线对应的 canonical branch contract。, AC-014: 该 skill 的宿主命令面固定收口到 `beacon doctor metadata show/create/update/delete/list/verify`，不新增一级公开命令。, AC-010: 当 metadata 已存在时，prompt 层把项目拓扑、service repo、canonical branch 当作固定输入，而不是重新推断。, AC-006: Beacon 能表达 protected branch 禁写、可写分支约束与违例处理策略。, AC-013: Beacon 提供确定性的人类面元信息子 skill，名称固定为 `beacon:beacon-project-metadata`。
