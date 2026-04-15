# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa-r1`
- feature: `beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa`
- version: `v1.3.2`
- revision_id: `R1`
- baseline_hash: `sha256:034eac663dcd457d18ce1b585027ae355ba919fdf202a46f1dda037bf4586a43`
- plan_hash: `sha256:277be300c90f61fe6c8fab747fc4e0a376bf9651c7689236d344ffebc3e42583`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.2/user-story/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.md`
- prd: `docs/beacon/v1.3.2/prd/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.md`
- test_case: `docs/beacon/v1.3.2/qa/test-cases/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.md`
- ac_matrix: `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.qa9-matrix.json`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa" --project-root . --version v1.3.2`
- run_command: `beacon implement team-run "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa" --project . --version v1.3.2`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa" --project . --version v1.3.2`
- qa_team_command: `beacon qa team-run "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa" --project . --version v1.3.2`
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
- git_workflow_ref: `docs/beacon/v1.3.2/.machine/execution/git-workflow-beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.json`

## Tasks

### ITASK-001 — FR-001 三模式只在 `implement` 与 `qa` 生效
- status: `completed`
- mapped_ac_ids: AC-001, AC-013, AC-003, AC-024
- mapped_test_ids: TC-001, TC-013, TC-003, TC-024, TC-027, TC-029
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010, SC-021, SC-022, SC-023, SC-024, SC-025, SC-026, SC-027, SC-028, SC-029, SC-030, SC-096, SC-097, SC-098, SC-099, SC-100, SC-151, SC-152, SC-153, SC-154, SC-155
- mapped_qa_case_ids: TC-001, TC-003, TC-013, TC-024, TC-027, TC-029
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 `implement` 必须支持 `single`
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002, TC-028
- mapped_scenario_ids: SC-011, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020
- mapped_qa_case_ids: TC-002, TC-028
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 `implement` 必须支持 `team`
- status: `completed`
- mapped_ac_ids: AC-014
- mapped_test_ids: TC-014
- mapped_scenario_ids: SC-101, SC-102, SC-103, SC-104, SC-105
- mapped_qa_case_ids: TC-014
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 `implement` 必须支持 `ralph`
- status: `completed`
- mapped_ac_ids: AC-004, AC-011
- mapped_test_ids: TC-004, TC-011, TC-030
- mapped_scenario_ids: SC-031, SC-032, SC-033, SC-034, SC-035, SC-036, SC-037, SC-038, SC-039, SC-040, SC-086, SC-087, SC-088, SC-089, SC-090
- mapped_qa_case_ids: TC-004, TC-011, TC-030
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 `qa` 必须成为三模式体系中的第二执行面
- status: `completed`
- mapped_ac_ids: AC-007, AC-005
- mapped_test_ids: TC-007, TC-005, TC-031, TC-033
- mapped_scenario_ids: SC-041, SC-042, SC-043, SC-044, SC-045, SC-046, SC-047, SC-048, SC-049, SC-050, SC-061, SC-062, SC-063, SC-064, SC-065, SC-066, SC-067, SC-068, SC-069, SC-070
- mapped_qa_case_ids: TC-005, TC-007, TC-031, TC-033
- depends_on: ITASK-004
- target_modules: -

### ITASK-006 — FR-006 `qa` 必须围绕冻结材料顺序推进
- status: `completed`
- mapped_ac_ids: AC-006, AC-009
- mapped_test_ids: TC-006, TC-009, TC-032
- mapped_scenario_ids: SC-051, SC-052, SC-053, SC-054, SC-055, SC-056, SC-057, SC-058, SC-059, SC-060, SC-076, SC-077, SC-078, SC-079, SC-080
- mapped_qa_case_ids: TC-006, TC-009, TC-032
- depends_on: ITASK-005
- target_modules: -

### ITASK-007 — FR-007 `qa` 必须启动目标项目浏览器环境
- status: `completed`
- mapped_ac_ids: AC-012, AC-008, AC-010, AC-015
- mapped_test_ids: TC-012, TC-008, TC-010, TC-015
- mapped_scenario_ids: SC-071, SC-072, SC-073, SC-074, SC-075, SC-081, SC-082, SC-083, SC-084, SC-085, SC-091, SC-092, SC-093, SC-094, SC-095, SC-106, SC-107, SC-108, SC-109, SC-110
- mapped_qa_case_ids: TC-008, TC-010, TC-012, TC-015
- depends_on: ITASK-006
- target_modules: -

### ITASK-008 — FR-008 `qa` 必须支持顺序可迭代演进
- status: `completed`
- mapped_ac_ids: AC-019, AC-020, AC-021, AC-023, AC-025, AC-026, AC-022, AC-016
- mapped_test_ids: TC-019, TC-020, TC-021, TC-023, TC-025, TC-026, TC-022, TC-016
- mapped_scenario_ids: SC-111, SC-112, SC-113, SC-114, SC-115, SC-126, SC-127, SC-128, SC-129, SC-130, SC-131, SC-132, SC-133, SC-134, SC-135, SC-136, SC-137, SC-138, SC-139, SC-140, SC-141, SC-142, SC-143, SC-144, SC-145, SC-146, SC-147, SC-148, SC-149, SC-150, SC-156, SC-157, SC-158, SC-159, SC-160, SC-161, SC-162, SC-163, SC-164, SC-165
- mapped_qa_case_ids: TC-016, TC-019, TC-020, TC-021, TC-022, TC-023, TC-025, TC-026
- depends_on: ITASK-007
- target_modules: -

### ITASK-009 — FR-009 每一轮 QA 都必须带来新的 auto research 增量
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TC-017
- mapped_scenario_ids: SC-116, SC-117, SC-118, SC-119, SC-120
- mapped_qa_case_ids: TC-017
- depends_on: ITASK-008
- target_modules: -

### ITASK-010 — FR-010 QA 必须反馈边界信息
- status: `completed`
- mapped_ac_ids: AC-018
- mapped_test_ids: TC-018
- mapped_scenario_ids: SC-121, SC-122, SC-123, SC-124, SC-125
- mapped_qa_case_ids: TC-018
- depends_on: ITASK-009
- target_modules: -

### ITASK-011 — FR-011 QA 必须支持结构推演
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- target_modules: -

### ITASK-012 — FR-012 QA 必须逐轮打磨产品功能与体验
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- target_modules: -

### ITASK-013 — FR-013 Ralph 必须使用 `implement + qa` 闭环
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- target_modules: -

### ITASK-014 — FR-014 Ralph 必须有明确终态
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- target_modules: -

### ITASK-015 — FR-015 Ralph 必须复用现有 control plane
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- target_modules: -

### ITASK-016 — FR-016 QA 浏览器验证必须有正式证据输出
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- target_modules: -

### ITASK-017 — FR-017 QA 的结果必须服务下一轮迭代
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- target_modules: -

### ITASK-018 — FR-018 `status/help` 必须显式表达当前模式与迭代轮次
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- target_modules: -

### ITASK-019 — FR-019 Beacon 作为 skill 必须稳定调用 Codex / Claude 原生 team subagent 能力
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- target_modules: -

### ITASK-020 — FR-020 原生 team subagent 调起前必须拆成两个稳定预检查
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- target_modules: -

### ITASK-021 — FR-021 `runtime-readiness precheck` 必须检查宿主原生能力可用性
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- target_modules: -

### ITASK-022 — FR-022 `delegation-readiness precheck` 必须检查项目委托条件
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- target_modules: -

### ITASK-023 — FR-023 `omx` 仅作为调研参考，不作为 `v1.3.2` 目标运行时
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-022
- target_modules: -

### ITASK-024 — FR-024 Codex 路径必须使用 Codex 宿主原生 subagent/team 能力
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-023
- target_modules: -

### ITASK-025 — FR-025 Claude 路径必须区分单 session subagent 与多 session team
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-024
- target_modules: -

### ITASK-026 — FR-026 Claude 多环境 subagent 必须拆成两个稳定预检查
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-025
- target_modules: -

### ITASK-027 — FR-027 预检查失败必须阻断 team subagent 并给出 fallback
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-026
- target_modules: -

### ITASK-028 — FR-028 `doctor` 必须成为多环境 subagent 预检查的统一入口
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-027
- target_modules: -

### ITASK-029 — FR-029 Beacon 必须继续沿袭极简人类主流程
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-028
- target_modules: -

### ITASK-030 — FR-030 对外公开命令面必须极度克制
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-029
- target_modules: -

### ITASK-031 — FR-031 复杂度必须默认留在机器内部
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-030
- target_modules: -

### ITASK-032 — FR-032 预检查必须默认内嵌到 `implement` / `qa`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-031
- target_modules: -

### ITASK-033 — FR-033 宿主上下文必须唯一，不讨论运行时选择
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-032
- target_modules: -

### ITASK-034 — FR-034 人类输出必须极简，机器输出必须完整
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-033
- target_modules: -

### ITASK-035 — FR-035 `global-boundaries` 必须成为 Beacon 的正式全局特性
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-034
- target_modules: -

### ITASK-036 — FR-036 Beacon 源码开发自身必须支持 `global-boundaries`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-035
- target_modules: -

### ITASK-037 — FR-037 Beacon 目标项目必须支持 `global-boundaries`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-036
- target_modules: -

### ITASK-038 — FR-038 `init/setup-context/sync-materials/verify-context` 必须支持 `global-boundaries`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-037
- target_modules: -

### ITASK-039 — FR-039 版本包必须显式声明如何继承 `global-boundaries`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-038
- target_modules: -

### ITASK-040 — FR-040 目标项目的交付闭环必须可验证地遵守 `global-boundaries`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-039
- target_modules: -

### ITASK-041 — FR-041 `doctor` 必须能检查 `global-boundaries` 的源码侧与项目侧一致性
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-040
- target_modules: -

### ITASK-042 — FR-042 `global-boundaries` 必须进入成功判定
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-041
- target_modules: -
