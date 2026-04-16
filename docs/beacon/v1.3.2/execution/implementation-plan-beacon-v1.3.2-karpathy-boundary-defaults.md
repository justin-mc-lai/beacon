# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.2-karpathy-boundary-defaults-r1`
- feature: `beacon-v1.3.2-karpathy-boundary-defaults`
- version: `v1.3.2`
- revision_id: `R1`
- baseline_hash: `sha256:52346376b274c1813a23a00abe649f54cef68601c3e313c8b33ad1d414f3d0fc`
- plan_hash: `sha256:14395d619b172ff328334083f7be28078ab7b5dc58b4316e873db02715d3f379`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.2/user-story/beacon-v1.3.2-karpathy-boundary-defaults.md`
- prd: `docs/beacon/v1.3.2/prd/beacon-v1.3.2-karpathy-boundary-defaults.md`
- test_case: `docs/beacon/v1.3.2/qa/test-cases/beacon-v1.3.2-karpathy-boundary-defaults.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.2-karpathy-boundary-defaults" --project-root . --version v1.3.2`
- run_command: `beacon implement team-run "beacon-v1.3.2-karpathy-boundary-defaults" --project . --version v1.3.2`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.2-karpathy-boundary-defaults" --project . --version v1.3.2`
- qa_team_command: `beacon qa team-run "beacon-v1.3.2-karpathy-boundary-defaults" --project . --version v1.3.2`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.2`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.2/.machine/execution/git-workflow-beacon-v1.3.2-karpathy-boundary-defaults.json`

## Tasks

### ITASK-001 — FR-001 全局规范必须要求显式假设
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 全局规范必须要求简单优先
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 全局规范必须要求外科手术式改动
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 全局规范必须要求目标驱动执行
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 规则必须进入 Beacon 自有规范，不形成外部 skill 依赖
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 默认全局规范必须同时约束 Beacon 自身与目标项目
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 规则必须与 6+3 主面兼容
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 规则必须支持轻重任务区分
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -
