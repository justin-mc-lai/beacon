# Beacon Implementation Plan

- plan_id: `plan-beacon-version-resolve-fail-closed-v163-r1`
- feature: `beacon-version-resolve-fail-closed-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:6345c4a85545b52a692654e71544054899bdbbe7560beccada5b07a87149b13a`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-version-resolve-fail-closed-v163-R1`
- delivery_baseline_source_hash: `sha256:f41277d983f6d44d2c9468fdf4d278e7b6508a97fd9bb32d21b5f32a13cd5e2f`
- plan_hash: `sha256:6e5dbd15a730bc4455a9c117e85bd9b48de3a9547742373e1e2772db711ab629`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md`
- prd: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md`
- test_case: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/tests.md`
- truth: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md`
- tests: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/tests.md`
- tasks: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/tasks.md`
- evidence: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163`
- ac_matrix: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-version-resolve-fail-closed-v163.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-version-resolve-fail-closed-v163.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-version-resolve-fail-closed-v163.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-version-resolve-fail-closed-v163.json`
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
- plan_command: `beacon implement team-plan "beacon-version-resolve-fail-closed-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-version-resolve-fail-closed-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-version-resolve-fail-closed-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-version-resolve-fail-closed-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
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
- git_workflow_ref: `docs/beacon/archive/v1.6.3/.machine/execution/git-workflow-beacon-version-resolve-fail-closed-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/research/beacon-version-resolve-fail-closed-v163.md`
- source_artifact: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-version-resolve-fail-closed-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `project_hooks.py:543` 不再含硬编码 `v1.6.1` 字面量；改用 `resolve_target_version...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-VR-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-VR-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 version=`auto`/空/`latest` 时 eval_version 解析为 docs 实际版本（如 v1.6.3），非 v1...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-VR-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-VR-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 post-release hook payload 含 `runtime_version`/`docs_version`/`drift`...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-VR-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-VR-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 `resolve_target_version` 解析失败/抛异常时 hook fail-closed block，reason_code...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-VR-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-VR-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 `agent_eval_kit.is_live_runner_admitted` 运行时用 resolve 版本，不依赖硬编码 `AGEN...
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-VR-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-VR-005
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 现有 post-release hook 在 runtime==docs（正常）场景仍 pass，不误 block（**Must**）
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-VR-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-VR-006
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 runtime≠docs（双版本合法推进）时 `drift=true` 但**不** block（仅记录）（**Must**，UD-006）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-VR-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-VR-007
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
