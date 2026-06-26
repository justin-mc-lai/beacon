# Beacon Implementation Plan

- plan_id: `plan-beacon-gate-truth-model-alignment-v163-r1`
- feature: `beacon-gate-truth-model-alignment-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:7773405ef5d36c5637a15d7827eb1a8ecf6bc4b90e5be4427a5b7c48b14ab1b6`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-gate-truth-model-alignment-v163-R1`
- delivery_baseline_source_hash: `sha256:1ae4b4d942aa53ef80275be86f5450ebe8a55fb62198dfb0ae02d6dba366521b`
- plan_hash: `sha256:4d452fb2940b90298cf57dfca0735731f8cfbcc997219840c1146d613329ead9`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md`
- prd: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md`
- test_case: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/tests.md`
- truth: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md`
- tests: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/tests.md`
- tasks: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/tasks.md`
- evidence: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163`
- ac_matrix: `docs/beacon/v1.6.3/.machine/qa/beacon-gate-truth-model-alignment-v163.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.6.3/.machine/qa/beacon-gate-truth-model-alignment-v163.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.6.3/.machine/qa/beacon-gate-truth-model-alignment-v163.qa9-matrix.json`
- research_projection: `docs/beacon/v1.6.3/.machine/user-story/beacon-gate-truth-model-alignment-v163.json`
- architecture_blueprint: `docs/beacon/v1.6.3/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-gate-truth-model-alignment-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-gate-truth-model-alignment-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-gate-truth-model-alignment-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-gate-truth-model-alignment-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
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
- git_workflow_ref: `docs/beacon/v1.6.3/.machine/execution/git-workflow-beacon-gate-truth-model-alignment-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/research/beacon-gate-truth-model-alignment-v163.md`
- source_artifact: `docs/beacon/v1.6.3/.machine/user-story/beacon-gate-truth-model-alignment-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `check_formal_version_package_closure` 对 `≥v1.5.2` 版本不再要求 `prd/`/`use...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-GT-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-GT-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 `≥v1.5.2` 版本改为校验 `features/<slug>/` 下至少一个 feature 包含 `truth.md`+`test...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-GT-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-GT-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 `<v1.5.2` 版本（如 v1.4.10）保持原 `prd/`+`user-story/`+`qa/test-cases/` 顶层目录...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-GT-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-GT-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 SUMMARY/execution/boundaries/source-architecture/release 校验对所有版本保留，不因...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-GT-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-GT-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 `≥v1.5.2` 版本无任何 feature 包 → critical block，reason_code `feature_packa...
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-GT-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-GT-005
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 v1.6.2 实测 `gate check release` 的 `formal_package_closure_missing` 不再因...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-GT-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-GT-006
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 空目录（`prd/` 存在但无 `.md`）不再使 `≥v1.5.2` 版本通过；通过需真实 feature 包（**Must**）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-GT-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-GT-007
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
