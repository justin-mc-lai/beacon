# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.3-memory-friction-evolution-toolkit-r1`
- feature: `beacon-v1.3.3-memory-friction-evolution-toolkit`
- version: `v1.3.3`
- revision_id: `R1`
- baseline_hash: `sha256:90be1fc779c606f333eb4d83d7b1fa9ced56f01c7ba77ec734b81a506b3fed56`
- plan_hash: `sha256:d527755dd7ec41e75fb6b9f2d5a6a0e453e091532b0d031a0704184688381d80`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.3/user-story/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
- prd: `docs/beacon/archive/v1.3.3/prd/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
- test_case: `docs/beacon/archive/v1.3.3/qa/test-cases/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
- story_scenario_map: `docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-memory-friction-evolution-toolkit.story-scenario-map.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.3-memory-friction-evolution-toolkit" --project-root . --version v1.3.3`
- run_command: `beacon implement team-run "beacon-v1.3.3-memory-friction-evolution-toolkit" --project . --version v1.3.3`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.3-memory-friction-evolution-toolkit" --project . --version v1.3.3`
- qa_team_command: `beacon qa team-run "beacon-v1.3.3-memory-friction-evolution-toolkit" --project . --version v1.3.3`
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
- git_workflow_ref: `docs/beacon/archive/v1.3.3/.machine/execution/git-workflow-beacon-v1.3.3-memory-friction-evolution-toolkit.json`

## Tasks

### ITASK-001 — FR-001 Toolkit 必须与 Lighthouse 并行
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 Toolkit 必须复用现有记忆能力
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 输出候选必须可执行
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 命令面必须保持可选
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 必须支持最小回写闭环
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 必须有轮次与退出保护
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -
