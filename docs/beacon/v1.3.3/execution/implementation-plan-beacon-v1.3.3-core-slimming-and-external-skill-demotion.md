# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.3-core-slimming-and-external-skill-demotion-r1`
- feature: `beacon-v1.3.3-core-slimming-and-external-skill-demotion`
- version: `v1.3.3`
- revision_id: `R1`
- baseline_hash: `sha256:d683028a58cb21b6881b290a4cc7d2e3a726723c0f3c42efbf15f1c58e0c0aba`
- plan_hash: `sha256:d5f3b8cdb6a7a2bc170bd8d4236029ece2a233fd5bb6fdfc5bc4e90e6d4c7a88`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.3/user-story/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
- prd: `docs/beacon/v1.3.3/prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
- test_case: `docs/beacon/v1.3.3/qa/test-cases/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
- ac_matrix: `docs/beacon/v1.3.3/.machine/qa/beacon-v1.3.3-core-slimming-and-external-skill-demotion.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.3/.machine/qa/beacon-v1.3.3-core-slimming-and-external-skill-demotion.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.3/.machine/qa/beacon-v1.3.3-core-slimming-and-external-skill-demotion.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.3-core-slimming-and-external-skill-demotion" --project-root . --version v1.3.3`
- run_command: `beacon implement team-run "beacon-v1.3.3-core-slimming-and-external-skill-demotion" --project . --version v1.3.3`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.3-core-slimming-and-external-skill-demotion" --project . --version v1.3.3`
- qa_team_command: `beacon qa team-run "beacon-v1.3.3-core-slimming-and-external-skill-demotion" --project . --version v1.3.3`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.3`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.3/.machine/execution/git-workflow-beacon-v1.3.3-core-slimming-and-external-skill-demotion.json`

## Tasks

### ITASK-001 — FR-001 默认 runner 必须保持宿主原生优先
- status: `completed`
- mapped_ac_ids: AC-001, AC-002, AC-003
- mapped_test_ids: TC-001, TC-002, TC-003, TC-012, TC-013, TC-014
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006
- mapped_qa_case_ids: TC-001, TC-002, TC-003, TC-012, TC-013, TC-014
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 external adapter 必须退出 core builtin 集合
- status: `completed`
- mapped_ac_ids: AC-007, AC-008
- mapped_test_ids: TC-007, TC-008, TC-018, TC-019
- mapped_scenario_ids: SC-021, SC-022, SC-023, SC-024, SC-025, SC-026, SC-027, SC-028, SC-029, SC-030, SC-031, SC-032
- mapped_qa_case_ids: TC-007, TC-008, TC-018, TC-019
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 兼容迁移必须由 doctor 子命令统一执行
- status: `completed`
- mapped_ac_ids: AC-009, AC-004, AC-011
- mapped_test_ids: TC-009, TC-004, TC-011, TC-015
- mapped_scenario_ids: SC-007, SC-008, SC-009, SC-010, SC-011, SC-012, SC-033, SC-035
- mapped_qa_case_ids: TC-004, TC-009, TC-011, TC-015
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 `qa` 默认不得隐式自动触发 external orchestration
- status: `completed`
- mapped_ac_ids: AC-005, AC-010
- mapped_test_ids: TC-005, TC-010, TC-016
- mapped_scenario_ids: SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-034
- mapped_qa_case_ids: TC-005, TC-010, TC-016
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 `skill/profile/orchestrate` 必须退出默认主叙事
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-006, TC-017
- mapped_scenario_ids: SC-019, SC-020
- mapped_qa_case_ids: TC-006, TC-017
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 `ralph-bridge` 必须退出正式产品叙事
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 文档主面必须只教 `6+3`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 测试合同必须按 core/compat 分层
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 discover/registry 输出必须分层展示
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 project contract 能力必须与 external execution 解耦
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 Ralph HUD 与 Team HUD 轻量增强
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 兼容层必须默认不干扰新用户
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 必须新增并行 HUD PRD 作为实现输入
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 必须新增并行 Memory/Friction Evolution Toolkit PRD
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — FR-015 必须新增 `beacon-prd-bootstrap` 人类 skill（可选）
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- target_modules: -
