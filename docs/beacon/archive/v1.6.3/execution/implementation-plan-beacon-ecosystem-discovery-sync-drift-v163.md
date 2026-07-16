# Beacon Implementation Plan

- plan_id: `plan-beacon-ecosystem-discovery-sync-drift-v163-r1`
- feature: `beacon-ecosystem-discovery-sync-drift-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:aca1f9f71783ddd412991204e7560bd291c6d10a7c1c05ebee3571e57b061a3c`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-ecosystem-discovery-sync-drift-v163-R1`
- delivery_baseline_source_hash: `sha256:1fbd7d3da59d84fe2e8bb28cc108f9a6885e564a47a11d5ef3c9a2016dc6b095`
- plan_hash: `sha256:836347dc85c96b21844d37b8300f4b5819b884f23c8bc55944002f623c293329`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md`
- prd: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md`
- test_case: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/tests.md`
- truth: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md`
- tests: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/tests.md`
- tasks: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/tasks.md`
- evidence: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163`
- story_scenario_map: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-ecosystem-discovery-sync-drift-v163.story-scenario-map.json`
- research_projection: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-ecosystem-discovery-sync-drift-v163.json`
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
- plan_command: `beacon implement team-plan "beacon-ecosystem-discovery-sync-drift-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-ecosystem-discovery-sync-drift-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-ecosystem-discovery-sync-drift-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-ecosystem-discovery-sync-drift-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.3`
- branch_prefix: `beacon/`
- base_branch: `beacon/v1.6.3`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.3/.machine/execution/git-workflow-beacon-ecosystem-discovery-sync-drift-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/research/beacon-ecosystem-discovery-sync-drift-v163.md`
- source_artifact: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-ecosystem-discovery-sync-drift-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `manifest sync` 对 ≥v1.5.2 版本扫到 `features/<slug>/` 下的 feature 包，无需手动 a...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-EC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 `beacon doctor sync-materials` 后 `truth-map verify` 无 `machine_json_s...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-EC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 `beacon freeze` 后 `.machine` source hash 与 frozen truth 一致，`truth-map...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-EC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 <v1.5.2 版本 manifest sync / sync-materials 行为不变（**Must**）
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-EC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 v1.6.2 已有 feature 包修复后仍 pass（**Must**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-EC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 v1.6.3 四个已 frozen 包修复后 truth-map verify pass（**Must**）
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-EC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 `_discover_features`（material_sync）对 ≥v1.5.2 经 manifest 正确发现 features...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-EC-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
