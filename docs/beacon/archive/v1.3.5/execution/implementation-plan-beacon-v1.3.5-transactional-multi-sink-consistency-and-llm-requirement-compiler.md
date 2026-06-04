# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler-r1`
- feature: `beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler`
- version: `v1.3.5`
- revision_id: `R1`
- baseline_hash: `sha256:36b9999f34f43cf79fb93af986ee998ef0f6ae5140c08459725a8a0e21871aa6`
- plan_hash: `sha256:bbd761e70f03265484e2030046b03f1c332024ee834307686d86d9f59d06c997`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.5/user-story/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.md`
- prd: `docs/beacon/archive/v1.3.5/prd/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.md`
- test_case: `docs/beacon/archive/v1.3.5/qa/test-cases/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.md`
- ac_matrix: `docs/beacon/archive/v1.3.5/.machine/qa/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.5/.machine/qa/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.3.5/.machine/qa/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler" --project-root . --version v1.3.5`
- run_command: `beacon implement team-run "beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler" --project . --version v1.3.5`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler" --project . --version v1.3.5`
- qa_team_command: `beacon qa team-run "beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler" --project . --version v1.3.5`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.5`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.3.5/.machine/execution/git-workflow-beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.json`

## Tasks

### ITASK-001 — FR-001 多写入统一事务协调器
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002, TC-007, TC-012
- mapped_scenario_ids: SC-016, SC-017, SC-018, SC-019, SC-020, SC-021, SC-022, SC-023, SC-024, SC-025, SC-026, SC-027, SC-028, SC-029, SC-030
- mapped_qa_case_ids: TC-002, TC-007, TC-012
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 禁止静默部分提交
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-006, TC-011
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-015
- mapped_qa_case_ids: TC-001, TC-006, TC-011
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 Runtime Projection 失败语义收敛
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003, TC-008, TC-013
- mapped_scenario_ids: SC-031, SC-032, SC-033, SC-034, SC-035, SC-036, SC-037, SC-038, SC-039, SC-040, SC-041, SC-042, SC-043, SC-044, SC-045
- mapped_qa_case_ids: TC-003, TC-008, TC-013
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 跨面一致性校验收敛到 gate/review/doctor
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-009
- mapped_scenario_ids: SC-046, SC-047, SC-048, SC-049, SC-050, SC-051, SC-052, SC-053, SC-054, SC-055
- mapped_qa_case_ids: TC-004, TC-009
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 `prd create` 增加 LLM 编译模式
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005, TC-010
- mapped_scenario_ids: SC-056, SC-057, SC-058, SC-059, SC-060, SC-061, SC-062, SC-063, SC-064, SC-065
- mapped_qa_case_ids: TC-005, TC-010
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 模板约束与语义编译解耦
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 PRD 编译证据必须落 machine 面
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 LLM 输出不达标必须阻断或降级可见
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 并行 lane 输出格式统一
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -
