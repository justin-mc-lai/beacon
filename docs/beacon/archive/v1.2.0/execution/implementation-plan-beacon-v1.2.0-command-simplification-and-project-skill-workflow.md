# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.2.0-command-simplification-and-project-skill-workflow-r1`
- feature: `beacon-v1.2.0-command-simplification-and-project-skill-workflow`
- version: `v1.2.0`
- revision_id: `R1`
- baseline_hash: `sha256:70058afa4c8e6513c53dbfe2fd31363e64138a61fcc91f64466d1e0e4ec29b95`
- plan_hash: `sha256:0168711ad24ac0fc787eb6bdbcd0d697195d1599fcb8d2c1d5347e0d22486794`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.2.0/user-story/beacon-v1.2.0-command-simplification-and-project-skill-workflow.md`
- prd: `docs/beacon/archive/v1.2.0/prd/beacon-v1.2.0-command-simplification-and-project-skill-workflow.md`
- test_case: `docs/beacon/archive/v1.2.0/qa/test-cases/beacon-v1.2.0-command-simplification-and-project-skill-workflow.md`
- ac_matrix: `docs/beacon/archive/v1.2.0/.machine/qa/beacon-v1.2.0-command-simplification-and-project-skill-workflow.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.2.0/.machine/qa/beacon-v1.2.0-command-simplification-and-project-skill-workflow.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.2.0/.machine/qa/beacon-v1.2.0-command-simplification-and-project-skill-workflow.qa9-matrix.json`

## Tasks

### ITASK-001 — AC-001 默认命令面必须优先暴露 `PRD → story → QA` 主链入口，且不破坏主链向后兼容性
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-021
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-001, TC-021
- depends_on: -
- target_modules: -

### ITASK-002 — AC-002 `help / status` 必须成为主链阶段路由中心，而不是只展示命令清单
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002, TC-022
- mapped_scenario_ids: SC-003, SC-004
- mapped_qa_case_ids: TC-002, TC-022
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — AC-003 低频或高级能力默认降噪，但仍保留显式入口，不得删除专家路径
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003, TC-023
- mapped_scenario_ids: SC-005, SC-006
- mapped_qa_case_ids: TC-003, TC-023
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — AC-004 系统必须根据项目特征推荐服务于 verify / delivery / debug / pipeline 的 skill/profile
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-024
- mapped_scenario_ids: SC-007, SC-008, SC-009, SC-010, SC-011, SC-012
- mapped_qa_case_ids: TC-004, TC-024
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — AC-005 starter packs 必须声明适用技术栈、边界，并保持 capability / evidence / required-cases 合同
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005, TC-025
- mapped_scenario_ids: SC-013, SC-014, SC-015, SC-016, SC-017, SC-018
- mapped_qa_case_ids: TC-005, TC-025
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — AC-006 `beacon skill discover` 必须遵循 `detect → recommend → preview → apply`，且...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-006, TC-026
- mapped_scenario_ids: SC-019, SC-020
- mapped_qa_case_ids: TC-006, TC-026
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — AC-007 discovery 结果必须包含项目特征、推荐模板/skills、评分、理由与证据
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-007
- mapped_scenario_ids: SC-021
- mapped_qa_case_ids: TC-007
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — AC-008 discovery 必须写出有界状态 artifact，并被 `help / profile / skill doctor` 共用
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-008
- mapped_scenario_ids: SC-022
- mapped_qa_case_ids: TC-008
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — AC-009 PRD/story 的关键需求点必须能映射到 prototype 页面或状态
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-009
- mapped_scenario_ids: SC-023, SC-024, SC-025, SC-026, SC-027
- mapped_qa_case_ids: TC-009
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — AC-010 orphan prototype / orphan requirement / UI 模块缺失必须被显式检测并给出修复方向
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TC-010
- mapped_scenario_ids: SC-028, SC-029, SC-030, SC-031, SC-032
- mapped_qa_case_ids: TC-010
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — AC-011 `v1.2.0` 文档必须明确 `PRD → story → QA` 是唯一主链锚点，其他工作流均为 subordinate workst...
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TC-011
- mapped_scenario_ids: SC-033
- mapped_qa_case_ids: TC-011
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — AC-012 `PRD + story + .machine/user-story + QA markdown + AC matrix + scenar...
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TC-012
- mapped_scenario_ids: SC-034
- mapped_qa_case_ids: TC-012
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — AC-013 `qa auto harness` 只能消费 baseline bundle，不得自建 benchmark target
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TC-013
- mapped_scenario_ids: SC-035
- mapped_qa_case_ids: TC-013
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — AC-014 harness 只能迭代 bounded QA policy surfaces，并输出 coverage/evidence/false-c...
- status: `completed`
- mapped_ac_ids: AC-014
- mapped_test_ids: TC-014
- mapped_scenario_ids: SC-036
- mapped_qa_case_ids: TC-014
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — AC-015 当前 requirement package 必须可生成 machine baseline bundle、完成 freeze，并清晰说明“...
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TC-015
- mapped_scenario_ids: SC-037, SC-038, SC-039, SC-040, SC-041
- mapped_qa_case_ids: TC-015
- depends_on: ITASK-014
- target_modules: -

### ITASK-016 — AC-016 `ask / help` 必须承担更强的主链命令推荐职责，而不是只做静态说明
- status: `completed`
- mapped_ac_ids: AC-016
- mapped_test_ids: TC-016
- mapped_scenario_ids: SC-042
- mapped_qa_case_ids: TC-016
- depends_on: ITASK-015
- target_modules: -

### ITASK-017 — AC-017 default visible command surface 必须优先主链，advanced / labs surfaces 通过显式...
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TC-017
- mapped_scenario_ids: SC-043
- mapped_qa_case_ids: TC-017
- depends_on: ITASK-016
- target_modules: -

### ITASK-018 — AC-018 `v1.2.0` 必须显式保持四层架构边界，并避免把 agent-platform rewrite 变成当前中心
- status: `completed`
- mapped_ac_ids: AC-018
- mapped_test_ids: TC-018
- mapped_scenario_ids: SC-044, SC-045, SC-046, SC-047, SC-048
- mapped_qa_case_ids: TC-018
- depends_on: ITASK-017
- target_modules: -

### ITASK-019 — AC-019 泛化 `beacon discover` 代码分析能力必须被标记为未来 advanced/labs 方向，而不是当前主链冻结交付
- status: `completed`
- mapped_ac_ids: AC-019
- mapped_test_ids: TC-019
- mapped_scenario_ids: SC-049
- mapped_qa_case_ids: TC-019
- depends_on: ITASK-018
- target_modules: -

### ITASK-020 — AC-020 三份 April 8 深度调研的结论必须被吸收到 versioned requirement package，并映射到 execution...
- status: `completed`
- mapped_ac_ids: AC-020
- mapped_test_ids: TC-020
- mapped_scenario_ids: SC-050, SC-051, SC-052, SC-053, SC-054
- mapped_qa_case_ids: TC-020
- depends_on: ITASK-019
- target_modules: -
