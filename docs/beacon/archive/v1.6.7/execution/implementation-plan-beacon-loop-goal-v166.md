# Beacon Implementation Plan

- plan_id: `plan-beacon-loop-goal-v166-r7`
- feature: `beacon-loop-goal-v166`
- version: `v1.6.7`
- revision_id: `R7`
- baseline_hash: `sha256:533f5b4d2a4f33172ef810bdfa6630023f1423c82ccca845fe60d046c4bfff5b`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.7-beacon-loop-goal-v166-R7`
- delivery_baseline_source_hash: `sha256:c99f0bb5796e23b309a950b4e0d6f112bfeb0e68113455866686a3ea159a714d`
- plan_hash: `sha256:046070f47ce108f52e2538fbb415779a9f35c233a937c9a8ff2f2f0aee28409f`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/truth.md`
- prd: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/truth.md`
- test_case: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/tests.md`
- truth: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/truth.md`
- tests: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/tests.md`
- tasks: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/tasks.md`
- evidence: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166`
- revision_delta: `docs/beacon/archive/v1.6.7/.machine/execution/revision-delta-beacon-loop-goal-v166.json`
- story_scenario_map: `docs/beacon/archive/v1.6.7/.machine/qa/beacon-loop-goal-v166.story-scenario-map.json`
- research_projection: `docs/beacon/archive/v1.6.7/.machine/user-story/beacon-loop-goal-v166.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.7/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-loop-goal-v166" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- run_command: `beacon implement team-run "beacon-loop-goal-v166" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- dev_run_command: `beacon implement dev-run "beacon-loop-goal-v166" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- qa_team_command: `beacon qa team-run "beacon-loop-goal-v166" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.7/beacon-loop-goal-v166`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.7/.machine/execution/git-workflow-beacon-loop-goal-v166.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.7/research/beacon-loop-goal-v166.md`
- source_artifact: `docs/beacon/archive/v1.6.7/.machine/user-story/beacon-loop-goal-v166.json`
- section_count: `0`

## Revision Delta
- revision_id: `R7`
- source_revision_id: `R6`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.6.7/.machine/execution/revision-delta-beacon-loop-goal-v166.json`

## Tasks

### ITASK-001 — TASK-023 change → `beacon-gen-change` — R6 reopen + draft human-gate redefinition (AC-014 rewrite + AC-027..030)
- status: `completed`
- mapped_ac_ids: AC-014, AC-027
- mapped_test_ids: TEST-014, TEST-027, TC-LG-014, TC-LG-027
- mapped_scenario_ids: SC-014, SC-027
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-024 implement → `beacon-gen-implement` — update `loop_goal_state.record_review_decision`：P1-only → `standard_execution_precheck` + continue audit；blocking = P0 | user_decision_required | drift routes
- status: `completed`
- mapped_ac_ids: AC-015, AC-001
- mapped_test_ids: TEST-015, TEST-001, TC-LG-001, TC-LG-015
- mapped_scenario_ids: SC-001, SC-015
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-025 implement → `beacon-gen-implement` — update public/packaged `beacon-loop-goal` SKILL.md：AC-014 R6 规则、同会话立即加载下一 skill、auto-decide 表对齐
- status: `completed`
- mapped_ac_ids: AC-029, AC-028, AC-013, AC-016
- mapped_test_ids: TEST-029, TEST-028, TEST-013, TEST-016, TC-LG-013, TC-LG-016, TC-LG-028, TC-LG-029
- mapped_scenario_ids: SC-013, SC-016, SC-028, SC-029
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-026 implement → `beacon-gen-implement` — add `beacon status loop-goal --resume`（读 state，返回 stage + next skill；禁止 no-op 伪装）
- status: `completed`
- mapped_ac_ids: AC-035, AC-034, AC-004
- mapped_test_ids: TEST-035, TEST-034, TEST-004, TC-LG-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-027 implement → `beacon-gen-implement` — emit observability fields：human_stops_per_run / stop_reason 分布 / p1_continue_count（pseudo_stall 可判定时）
- status: `completed`
- mapped_ac_ids: AC-040
- mapped_test_ids: TEST-040
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-028 implement → `beacon-gen-implement` — pytest TC-LG-014 行为翻转 + TC-LG-027..030
- status: `completed`
- mapped_ac_ids: AC-008, AC-003
- mapped_test_ids: TEST-008, TEST-003, TC-LG-003, TC-LG-008
- mapped_scenario_ids: SC-003, SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-029 qa → `beacon-eval-qa` — R6 regression QA (carried forward)
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009, TC-LG-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-030 release → `beacon-eval-release` — human gate before ship（unchanged AC-007）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-LG-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-031 change → `beacon-gen-change` — R7 reopen intent continuation + topology_gate + dual runtime (AC-031..040)
- status: `completed`
- mapped_ac_ids: AC-031
- mapped_test_ids: TEST-031
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — TASK-032 implement → `beacon-gen-implement` — IntentContext, record_intent_fork, decision_cache, interrupt semantics
- status: `completed`
- mapped_ac_ids: AC-030, AC-032, AC-033
- mapped_test_ids: TEST-030, TEST-032, TEST-033, TC-LG-030
- mapped_scenario_ids: SC-030
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — TASK-033 implement → `beacon-gen-implement` — `beacon loop-goal run` CLI + resume utterance map
- status: `completed`
- mapped_ac_ids: AC-023, AC-026, AC-022
- mapped_test_ids: TEST-023, TEST-026, TEST-022, TC-LG-022, TC-LG-023, TC-LG-026
- mapped_scenario_ids: SC-022, SC-023, SC-026
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — TASK-034 implement → `beacon-gen-implement` — topology_gate consume in precheck; SKILL.md R7 sync
- status: `completed`
- mapped_ac_ids: AC-036
- mapped_test_ids: TEST-036
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — TASK-035 implement → `beacon-gen-implement` — v2 schema parity fixtures + tests/test_v167_loop_goal.py
- status: `completed`
- mapped_ac_ids: AC-039
- mapped_test_ids: TEST-039
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — TASK-036 qa → `beacon-eval-qa` — AC-031..040 QA passed
- status: `completed`
- mapped_ac_ids: AC-025
- mapped_test_ids: TEST-025, TC-LG-025
- mapped_scenario_ids: SC-025
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — TASK-037 release → `beacon-eval-release` — human gate before ship
- status: `completed`
- mapped_ac_ids: AC-006, AC-019, AC-021, AC-024, AC-002, AC-005, AC-010, AC-011, AC-012, AC-017, AC-018, AC-020, AC-037, AC-038
- mapped_test_ids: TEST-006, TEST-019, TEST-021, TEST-024, TEST-002, TEST-005, TEST-010, TEST-011, TEST-012, TEST-017, TEST-018, TEST-020, TEST-037, TEST-038, TC-LG-002, TC-LG-005, TC-LG-006, TC-LG-010, TC-LG-011, TC-LG-012, TC-LG-017, TC-LG-018, TC-LG-019, TC-LG-020, TC-LG-021, TC-LG-024
- mapped_scenario_ids: SC-002, SC-005, SC-006, SC-010, SC-011, SC-012, SC-017, SC-018, SC-019, SC-020, SC-021, SC-024
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
