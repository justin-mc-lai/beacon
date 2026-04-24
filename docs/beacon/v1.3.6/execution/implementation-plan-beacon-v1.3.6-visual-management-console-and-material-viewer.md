# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.6-visual-management-console-and-material-viewer-r1`
- feature: `beacon-v1.3.6-visual-management-console-and-material-viewer`
- version: `v1.3.6`
- revision_id: `R1`
- baseline_hash: `sha256:915c21100211f663304d9e0bac8f67f9daa2dc8e6e9eafc374f5be1d38cfb4f4`
- plan_hash: `sha256:4cd776c3c32a927dfb4b23d1650633075893e1b3e6c5481203fb1ada7d42160a`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md`
- prd: `docs/beacon/v1.3.6/prd/beacon-v1.3.6-visual-management-console-and-material-viewer.md`
- test_case: `docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md`
- story_scenario_map: `docs/beacon/v1.3.6/.machine/qa/beacon-v1.3.6-visual-management-console-and-material-viewer.story-scenario-map.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.6-visual-management-console-and-material-viewer" --project-root . --version v1.3.6`
- run_command: `beacon implement team-run "beacon-v1.3.6-visual-management-console-and-material-viewer" --project . --version v1.3.6`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.6-visual-management-console-and-material-viewer" --project . --version v1.3.6`
- qa_team_command: `beacon qa team-run "beacon-v1.3.6-visual-management-console-and-material-viewer" --project . --version v1.3.6`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `workspace`
- expected_branch: `beacon/v1.3.6`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: ., beacon-console-ui, beacon/commands, docs/beacon/v1.3.6, .beacon
- git_workflow_ref: `docs/beacon/v1.3.6/.machine/execution/git-workflow-beacon-v1.3.6-visual-management-console-and-material-viewer.json`

## Tasks

### ITASK-001 — FR-001 首页必须先回答经营判断
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TEST-001, TEST-002, TC-001, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 管理总览必须提供多项目密集视图
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 项目详情必须成为接力页
- status: `completed`
- mapped_ac_ids: AC-004, AC-005
- mapped_test_ids: TEST-004, TEST-005, TC-004, TC-005
- mapped_scenario_ids: SC-004, SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 运行中心必须下钻 single / team / ralph
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008, TC-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 项目物料查看器必须支持按版本只读查看
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 页面实现必须依赖 `v1.3.5` wireframe 包
- status: `completed`
- mapped_ac_ids: AC-015, AC-013, AC-007, AC-009, AC-010, AC-011, AC-012, AC-014, AC-016
- mapped_test_ids: TEST-015, TEST-013, TEST-007, TEST-009, TEST-010, TEST-011, TEST-012, TEST-014, TEST-016, TC-007, TC-009, TC-010, TC-011, TC-012, TC-013, TC-014, TC-015, TC-016
- mapped_scenario_ids: SC-007, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-021, SC-022, SC-023, SC-024
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -
