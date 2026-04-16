# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.2-lighthouse-project-analysis-toolkit-r1`
- feature: `beacon-v1.3.2-lighthouse-project-analysis-toolkit`
- version: `v1.3.2`
- revision_id: `R1`
- baseline_hash: `sha256:c47d27f20cb243462633407b93b3b75c316f9e17ef892721f4753fd8428ede6e`
- plan_hash: `sha256:aba596b09fa8a9ef5553460f67e49df011c98027beda28c38540dca3d6a43333`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.2/user-story/beacon-v1.3.2-lighthouse-project-analysis-toolkit.md`
- prd: `docs/beacon/v1.3.2/prd/beacon-v1.3.2-lighthouse-project-analysis-toolkit.md`
- test_case: `docs/beacon/v1.3.2/qa/test-cases/beacon-v1.3.2-lighthouse-project-analysis-toolkit.md`
- ac_matrix: `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-lighthouse-project-analysis-toolkit.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-lighthouse-project-analysis-toolkit.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-lighthouse-project-analysis-toolkit.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.2-lighthouse-project-analysis-toolkit" --project-root . --version v1.3.2`
- run_command: `beacon implement team-run "beacon-v1.3.2-lighthouse-project-analysis-toolkit" --project . --version v1.3.2`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.2-lighthouse-project-analysis-toolkit" --project . --version v1.3.2`
- qa_team_command: `beacon qa team-run "beacon-v1.3.2-lighthouse-project-analysis-toolkit" --project . --version v1.3.2`
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
- git_workflow_ref: `docs/beacon/v1.3.2/.machine/execution/git-workflow-beacon-v1.3.2-lighthouse-project-analysis-toolkit.json`

## Tasks

### ITASK-001 — FR-001 必须提供独立的 Beacon skill 入口
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-021
- mapped_qa_case_ids: TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 必须支持任意目标项目分析
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 必须支持单文件输出
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 输出必须类似 `system-architecture-map`
- status: `completed`
- mapped_ac_ids: AC-003, AC-004
- mapped_test_ids: TEST-003, TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 必须提供多种分析视角
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 必须显式区分事实与推断
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 必须带源引用
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 必须与主工作流解耦
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 必须支持“分析后继续”
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 必须保持 Beacon 风格
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -
