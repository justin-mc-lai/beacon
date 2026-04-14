# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction-r1`
- feature: `beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction`
- version: `v1.3.1`
- revision_id: `R1`
- baseline_hash: `sha256:3f04ee5f7e84775d4e978716492c69f89bcb272454d5a75636c55425fc629b73`
- plan_hash: `sha256:c29c8b1de239150fa3dc61f70d3bfe3d42f2f002f5c72ac71da6296769b22bdd`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.1/user-story/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
- prd: `docs/beacon/v1.3.1/prd/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
- test_case: `docs/beacon/v1.3.1/qa/test-cases/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
- story_scenario_map: `docs/beacon/v1.3.1/.machine/qa/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.story-scenario-map.json`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction" --project-root . --version v1.3.1`
- run_command: `beacon implement team-run "beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction" --project . --version v1.3.1`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction" --project . --version v1.3.1`
- qa_team_command: `beacon qa team-run "beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction" --project . --version v1.3.1`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.1`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.1/.machine/execution/git-workflow-beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.json`

## Tasks

### ITASK-001 — FR-001 人类可见主命令必须收敛
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TEST-001, TEST-002, TC-001, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 `brainstorm` 必须嵌入 `prd -> user-story`
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011, TC-011
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 `implement` 对人类保持单入口
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 `qa` 对人类保持单入口
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 每一轮 QA 都必须带来新的价值
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 learning / auto research 只能围绕冻结用户故事工作
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 旧文档物料必须支持按版本一键更新对齐
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 探索极简 CLI
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008, TC-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 人类交付与机器协作必须分层
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009, TC-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 需求审核未收口不得冻结
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010, TC-010
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 需求审核必须显式输出未决项清单
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012, TC-012
- mapped_scenario_ids: SC-012
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 每个版本必须先做技术评审
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 monorepo / multi-service 项目必须给出确定性服务边界
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 技术评审未完成不得进入正式实现
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — FR-015 极简 CLI 也必须覆盖需求审核与技术评审
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- target_modules: -

### ITASK-016 — FR-016 同一版本必须支持多个并行 feature package
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- target_modules: -

### ITASK-017 — FR-017 交付必须产出独立 change 文档与版本演进图
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- target_modules: -
