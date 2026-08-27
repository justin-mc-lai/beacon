# Beacon Implementation Plan

- plan_id: `plan-beacon-v1615-automerge-gate-r1`
- feature: `beacon-v1615-automerge-gate`
- version: `v1.6.15`
- revision_id: `R1`
- baseline_hash: `sha256:f5b2b7f639c75749f4cb32553e8b14515fe4490273b77fb4deb48d7f3094bea4`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.15-beacon-v1615-automerge-gate-R1`
- delivery_baseline_source_hash: `sha256:6db5534a76277afd88500cd70baef8f1c021740cd72aff5dbdb58ebe7107becb`
- plan_hash: `sha256:00d589160dd1d8bfb6eda86263666945bb075a6eb223768588f179267238cb27`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/truth.md`
- prd: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/truth.md`
- test_case: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/tests.md`
- truth: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/truth.md`
- tests: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/tests.md`
- tasks: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/tasks.md`
- evidence: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate`
- story_scenario_map: `docs/beacon/v1.6.15/.machine/qa/beacon-v1615-automerge-gate.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.15/.machine/user-story/beacon-v1615-automerge-gate.json`
- architecture_blueprint: `docs/beacon/v1.6.15/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1615-automerge-gate" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- run_command: `beacon implement team-run "beacon-v1615-automerge-gate" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- dev_run_command: `beacon implement dev-run "beacon-v1615-automerge-gate" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- qa_team_command: `beacon qa team-run "beacon-v1615-automerge-gate" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.15/beacon-v1615-automerge-gate`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.15/.machine/execution/git-workflow-beacon-v1615-automerge-gate.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.15/research/beacon-v1615-automerge-gate.md`
- source_artifact: `docs/beacon/v1.6.15/.machine/user-story/beacon-v1615-automerge-gate.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: merge 回 main 前 gate 检查三条件（类型覆盖达标 + 失败模式回归命中 0 + 对抗式审查通过）；任一不达标 → cove... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-001.json`
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001, TC-ILLEGAL
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-002: 失败模式回归库（v1.6.13 D3 已建）作为合并前置输入：在 regression_checked 阶段命中 > 0 → 合并被拦。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-007, SC-008, SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: 对抗式审查（global-boundaries §5）作为合并前置：在 adversarial_checked 阶段缺翻车点清单/验证证据... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-003.json`
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-010, SC-011, SC-012
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-004: release 人类 gate 保持不变：auto-merge 不自动打 tag/部署/发布（merged 后仍须人类确认）；`manua... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-013, SC-014, SC-015
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/QA-MATRIX.json`
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
