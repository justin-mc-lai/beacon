# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor-r1`
- feature: `beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor`
- version: `v1.3.5`
- revision_id: `R1`
- baseline_hash: `sha256:e7281feaeab9b8e3ba5cc5ae0efda7d6168e42473b21ef3f0ad2c0b6271742c3`
- plan_hash: `sha256:81ad07e94159d229837108be92ac39e4b2938db2905a203fd8422f28a6efd545`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.5/user-story/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- prd: `docs/beacon/v1.3.5/prd/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- test_case: `docs/beacon/v1.3.5/qa/test-cases/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- ac_matrix: `docs/beacon/v1.3.5/.machine/qa/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.5/.machine/qa/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.5/.machine/qa/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor" --project-root . --version v1.3.5`
- run_command: `beacon implement team-run "beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor" --project . --version v1.3.5`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor" --project . --version v1.3.5`
- qa_team_command: `beacon qa team-run "beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor" --project . --version v1.3.5`
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
- git_workflow_ref: `docs/beacon/v1.3.5/.machine/execution/git-workflow-beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.json`

## Tasks

### ITASK-001 — FR-001 `prototype` 只保留 `wireframe` 草图模式
- status: `completed`
- mapped_ac_ids: AC-003, AC-005, AC-006, AC-001, AC-002
- mapped_test_ids: TC-006, TC-002, TC-003, TC-001, TC-005, TC-011, TC-015, TC-016, TC-012, TC-013
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-021, SC-022, SC-023, SC-024, SC-025, SC-026, SC-027, SC-028
- mapped_qa_case_ids: TC-001, TC-002, TC-003, TC-005, TC-006, TC-011, TC-012, TC-013, TC-015, TC-016
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 必须移除 HTML 高保真原型能力与要求
- status: `completed`
- mapped_ac_ids: AC-007, AC-008, AC-009, AC-004
- mapped_test_ids: TC-004, TC-008, TC-009, TC-007, TC-017, TC-014
- mapped_scenario_ids: SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-029, SC-030, SC-031, SC-032, SC-033, SC-034
- mapped_qa_case_ids: TC-004, TC-007, TC-008, TC-009, TC-014, TC-017
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 Wireframe 输出必须形成冻结包
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TC-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: TC-010
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 `wireframe-summary.md` 必须承担页面汇总职责
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 `navigation-map` 必须冻结路由与跳转逻辑
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 单页草图必须使用 Markdown + ASCII 结构
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 必须支持平台差异说明
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 必须与 `prd / user-story / test-case` 形成对齐面
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 `freeze/review/status` 必须围绕 wireframe 语义工作
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 版本文档与 skill 文档必须同步更新
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 必须从真实 requirement 生成“闭环型”线框内容
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 必须冻结页面状态流转（State Flow），而不只是页面跳转
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 必须冻结页面组件契约（Component Contract）
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 多写入点必须支持事务型一致提交
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — FR-015 人机隔离必须在目录与语义层同时成立
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- target_modules: -
