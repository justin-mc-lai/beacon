# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface-r1`
- feature: `beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface`
- version: `v1.3.5`
- revision_id: `R1`
- baseline_hash: `sha256:df90682762ab8f17bcb4e8fdc27db88a999714a1f66b3304ae7c8b22288a366e`
- plan_hash: `sha256:fad74d391576c1d0f2b804e49c49ce9e556c879c361f7bd0f70b44d9586f473e`
- status: `blocked`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.5/user-story/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.md`
- prd: `docs/beacon/archive/v1.3.5/prd/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.md`
- test_case: `docs/beacon/archive/v1.3.5/qa/test-cases/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface" --project-root . --version v1.3.5`
- run_command: `beacon implement team-run "beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface" --project . --version v1.3.5`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface" --project . --version v1.3.5`
- qa_team_command: `beacon qa team-run "beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface" --project . --version v1.3.5`
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
- git_workflow_ref: `docs/beacon/archive/v1.3.5/.machine/execution/git-workflow-beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface.json`

## Tasks

### ITASK-001 — FR-001 增加一个宿主可见子 skill `beacon-change`
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 `beacon-change` 必须稳定接收冻结后调整意图
- status: `blocked`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 `beacon-change` 必须把变更请求编译为 change brief
- status: `completed`
- mapped_ac_ids: AC-003, AC-005
- mapped_test_ids: TEST-003, TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 冻结后调整必须触发 revision reopen
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 变更后必须重编译 requirement truth
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 系统必须支持 requirement re-freeze
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 生命周期状态机必须成为正式文档资产
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 `implement` 必须识别 revised baseline
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 `qa` 必须识别 delta verification
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 `release` 必须识别 recheck 场景
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 `help/status` 必须能路由冻结后调整闭环
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -
