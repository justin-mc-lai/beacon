# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane-r1`
- feature: `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`
- version: `v1.3.4`
- revision_id: `R1`
- baseline_hash: `sha256:a781d38661d57e0ee2e4fa40c65a965761108c0fd76d24372ffaecc161415e62`
- plan_hash: `sha256:7ae92c2434f17b88f695187deb7b9c0c91b3ebd4bbfb4a0d6cf88edfc5c14579`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.3.4/user-story/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
- prd: `docs/beacon/v1.3.4/prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
- test_case: `docs/beacon/v1.3.4/qa/test-cases/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane" --project-root . --version v1.3.4`
- run_command: `beacon implement team-run "beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane" --project . --version v1.3.4`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane" --project . --version v1.3.4`
- qa_team_command: `beacon qa team-run "beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane" --project . --version v1.3.4`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.4`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.4/.machine/execution/git-workflow-beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.json`

## Tasks

### ITASK-001 — FR-001 建立 Project Registry
- status: `planned`
- mapped_ac_ids: AC-001, AC-010
- mapped_test_ids: TEST-001, TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 正式区分 `single_repo` 与 `multi_repo_workspace`
- status: `planned`
- mapped_ac_ids: AC-002, AC-008
- mapped_test_ids: TEST-002, TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 建立 Git Scope Registry
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 建立 Feature / Package Registry
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 建立 Run Registry
- status: `planned`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 建立 Run Event Timeline
- status: `planned`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 建立 Artifact Ref Index
- status: `planned`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 建立 Health Snapshot 与异常观测
- status: `planned`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 PocketBase 必须只消费 Projection Data
- status: `planned`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 提供 Backup / Export 能力
- status: `planned`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 支持断库降级
- status: `planned`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 支持从本地 Truth 重建
- status: `planned`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 看板必须以生命周期为主轴
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 看板必须支持 CEO 总览视图
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — FR-015 看板必须支持项目负责人详情视图
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- target_modules: -

### ITASK-016 — FR-016 必须显式建模需求物料补齐情况
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- target_modules: -

### ITASK-017 — FR-017 必须显式建模实现阶段 runtime 模式
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- target_modules: -

### ITASK-018 — FR-018 必须记录 team 代理运行详情
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- target_modules: -

### ITASK-019 — FR-019 必须记录 git 分支与 worktree 绑定
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- target_modules: -

### ITASK-020 — FR-020 必须记录 Beacon-observed host session 引用
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- target_modules: -

### ITASK-021 — FR-021 必须通过生命周期推荐 skill
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- target_modules: -

### ITASK-022 — FR-022 必须显式排除 Beacon 外运行时
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- target_modules: -
