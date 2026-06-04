# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.3-minimal-hud-scenarios-and-implementation-r1`
- feature: `beacon-v1.3.3-minimal-hud-scenarios-and-implementation`
- version: `v1.3.3`
- revision_id: `R1`
- baseline_hash: `sha256:bd18efe8a43c4ccaaa4bb2651dee6ff9412a77d94cc8ff9b672923d884e2ce98`
- plan_hash: `sha256:e260f41a12d7425b6d380a41fe7a8c61d356dcfed5776eaf459ccefb398ee319`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.3/user-story/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`
- prd: `docs/beacon/archive/v1.3.3/prd/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`
- test_case: `docs/beacon/archive/v1.3.3/qa/test-cases/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`
- ac_matrix: `docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.3.3/.machine/qa/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.3-minimal-hud-scenarios-and-implementation" --project-root . --version v1.3.3`
- run_command: `beacon implement team-run "beacon-v1.3.3-minimal-hud-scenarios-and-implementation" --project . --version v1.3.3`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.3-minimal-hud-scenarios-and-implementation" --project . --version v1.3.3`
- qa_team_command: `beacon qa team-run "beacon-v1.3.3-minimal-hud-scenarios-and-implementation" --project . --version v1.3.3`
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
- git_workflow_ref: `docs/beacon/archive/v1.3.3/.machine/execution/git-workflow-beacon-v1.3.3-minimal-hud-scenarios-and-implementation.json`

## Tasks

### ITASK-001 — FR-001 HUD 必须遵守 1-3 行预算
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-008, TC-015
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007
- mapped_qa_case_ids: TC-001, TC-008, TC-015
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 HUD 默认只展示最小决策信息
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002, TC-009
- mapped_scenario_ids: SC-008, SC-009
- mapped_qa_case_ids: TC-002, TC-009
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 Ralph HUD 必须可观测闭环状态
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003, TC-010
- mapped_scenario_ids: SC-010, SC-011
- mapped_qa_case_ids: TC-003, TC-010
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 Team HUD 必须可观测执行摘要
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-011
- mapped_scenario_ids: SC-012, SC-013, SC-014, SC-015, SC-016, SC-017
- mapped_qa_case_ids: TC-004, TC-011
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 命令面不得扩张
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005, TC-012
- mapped_scenario_ids: SC-018, SC-019, SC-020, SC-021, SC-022, SC-023
- mapped_qa_case_ids: TC-005, TC-012
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 阻断推荐命令必须统一
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-006, TC-013
- mapped_scenario_ids: SC-024, SC-025
- mapped_qa_case_ids: TC-006, TC-013
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 机器细节必须保留但不挤占人类面
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-007, TC-014
- mapped_scenario_ids: SC-026, SC-027
- mapped_qa_case_ids: TC-007, TC-014
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 Codex Hook 必须支持输入框下固定 HUD 注入
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 自动注入事件必须覆盖 UserPromptSubmit 与会话刷新
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 Hook 安装/校验必须走 doctor 治理面
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -
