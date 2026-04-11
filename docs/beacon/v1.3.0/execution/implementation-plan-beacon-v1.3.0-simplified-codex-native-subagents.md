# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.0-simplified-codex-native-subagents-r1`
- feature: `beacon-v1.3.0-simplified-codex-native-subagents`
- version: `v1.3.0`
- revision_id: `R1`
- baseline_hash: `sha256:f3e563bd54e5af6530a5f790683bc0b635bee6642af80ef0158489e9731c0720`
- plan_hash: `sha256:762ff76015b05d735215e4f38cf86149f01b236826d70d4ded7626349bae4821`
- status: `blocked`

## Source Refs
- user_story: `docs/beacon/v1.3.0/user-story/beacon-v1.3.0-simplified-codex-native-subagents.md`
- prd: `docs/beacon/v1.3.0/prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
- test_case: `docs/beacon/v1.3.0/qa/test-cases/beacon-v1.3.0-simplified-codex-native-subagents.md`
- ac_matrix: `docs/beacon/v1.3.0/.machine/qa/beacon-v1.3.0-simplified-codex-native-subagents.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.0/.machine/qa/beacon-v1.3.0-simplified-codex-native-subagents.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.0/.machine/qa/beacon-v1.3.0-simplified-codex-native-subagents.qa9-matrix.json`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.0-simplified-codex-native-subagents" --project-root . --version v1.3.0`
- run_command: `beacon implement team-run "beacon-v1.3.0-simplified-codex-native-subagents" --project . --version v1.3.0`
- qa_team_command: `beacon qa team-run "beacon-v1.3.0-simplified-codex-native-subagents" --project . --version v1.3.0`
- roles: planner, implementer, reviewer, tester

## Tasks

### ITASK-001 — FR-001 阶段级 `subagent_mode`
- status: `blocked`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 角色注册表
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 委托计划工件
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 子代理证据工件
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 正式回写所有权
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 适配器边界
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 规划类 prompt 路由
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 并发边界契约
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 implement-first 落地顺序
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 阶段扩面前置条件
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 版本语义规范注册表
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 字段逐项语义定义
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 统一解析归口
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 防漂移约束
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — FR-015 planning line 解析规则
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- target_modules: -

### ITASK-016 — FR-016 人类默认中文、机器默认英文
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- target_modules: -

### ITASK-017 — FR-017 双面镜像同步
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- target_modules: -

### ITASK-018 — FR-018 新 contract artifact 四件套
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- target_modules: -

### ITASK-019 — FR-019 implement plan 与 implement run 的 team-mode 优先策略
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- target_modules: -

### ITASK-020 — FR-020 QA 的 team-mode 要求
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- target_modules: -

### ITASK-021 — FR-021 implement 与 QA 的上下文隔离
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- target_modules: -

### ITASK-022 — FR-022 显性稳定的 team-mode 触发契约
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- target_modules: -
