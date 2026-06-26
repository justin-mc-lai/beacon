# Beacon Implementation Plan

- plan_id: `plan-beacon-runtime-release-alignment-v163-r1`
- feature: `beacon-runtime-release-alignment-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:fb7c347d1de0317d2fdfa41200378e9605de13f042289606be2a17d89cfa2cf1`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-runtime-release-alignment-v163-R1`
- delivery_baseline_source_hash: `sha256:b7e765f9de2eb2b58dbccd3d05f00b7cfb578a4d99bd57ea04dfc2f84020de99`
- plan_hash: `sha256:624ea1b68039944443deb4734dc1f74acd4aa28ab2d207f65249bba0f307df2c`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md`
- prd: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md`
- test_case: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/tests.md`
- truth: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md`
- tests: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/tests.md`
- tasks: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/tasks.md`
- evidence: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163`
- story_scenario_map: `docs/beacon/v1.6.3/.machine/qa/beacon-runtime-release-alignment-v163.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.3/.machine/user-story/beacon-runtime-release-alignment-v163.json`
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
- plan_command: `beacon implement team-plan "beacon-runtime-release-alignment-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-runtime-release-alignment-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-runtime-release-alignment-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-runtime-release-alignment-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
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
- git_workflow_ref: `docs/beacon/v1.6.3/.machine/execution/git-workflow-beacon-runtime-release-alignment-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/research/beacon-runtime-release-alignment-v163.md`
- source_artifact: `docs/beacon/v1.6.3/.machine/user-story/beacon-runtime-release-alignment-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 release stage runtime≠docs target → critical block，reason_code `runti...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-RA-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 runtime==docs 时 release gate 不因 drift block（**Must**）
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 post-release hook payload 含 `runtime_alignment` 字段（runtime_version/do...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 runtime≠docs 时 hook `runtime_alignment.recommended_command` 含 `beacon...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 plan/truth/implement/qa stage 不因 runtime≠docs block（开发期合法）（**Must**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 hook 不执行 pip install，只提示（**Must**，UD-004）
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 P0-1 的 `_resolve_eval_version` + resolve failure fail-closed 仍生效（**Mu...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
