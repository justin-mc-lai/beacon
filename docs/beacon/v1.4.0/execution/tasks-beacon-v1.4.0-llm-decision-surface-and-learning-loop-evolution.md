# Beacon Implementation Tasks Ledger

- feature: `beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution`
- version: `v1.4.0`
- plan_id: `plan-beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution-r2`
- revision_id: `R2`
- progress: `18/18`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.4.0/.machine/execution/implementation-plan-beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.progress.json`
- canonical_plan_json: `docs/beacon/v1.4.0/.machine/execution/implementation-plan-beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` FR-001 核心 skill 必须升级为正式 decision surface
  - tests=TC-002,TC-001,TC-057,TC-058,TC-059,TC-060,TC-061,TC-062,TC-063,TC-064,TC-065
[x] `ITASK-002` FR-002 Inputs Contract 必须最小但可机器消费
  - tests=TC-003 | depends_on=ITASK-001
[x] `ITASK-003` FR-003 Decision Protocol 必须承载主要判断逻辑
  - tests=TC-004,TEST-050 | depends_on=ITASK-002
[x] `ITASK-004` FR-004 Anti-Inertia Notes 必须显式纠正常见误锚
  - tests=TEST-007,TEST-008,TEST-011,TEST-015 | depends_on=ITASK-003
[x] `ITASK-005` FR-005 Learning Notes 必须复用现有 learning plane kernel
  - tests=TEST-013 | depends_on=ITASK-004
[x] `ITASK-006` FR-006 `beacon ask` 必须被冻结为正式的自然语言路由入口
  - tests=TEST-006,TEST-005 | depends_on=ITASK-005
[x] `ITASK-007` FR-007 `beacon ask` 的 `--execute` 必须有更严格的边界契约
  - tests=TEST-009 | depends_on=ITASK-006
[x] `ITASK-008` FR-008 `brainstorm` 与 `ask` 必须建立清晰分工
  - tests=TEST-012 | depends_on=ITASK-007
[x] `ITASK-009` FR-009 requirement 三件套必须增加 diagram-aware 深度思考协议
  - tests=TEST-020,TEST-018,TEST-017 | depends_on=ITASK-008
[x] `ITASK-010` FR-010 semantic trace 必须成为 requirement 深度思考的共享输入
  - tests=TEST-021 | depends_on=ITASK-009
[x] `ITASK-011` FR-011 requirement 建模增强优先采用“升格现有 diagram + semantic”，而不是直接新增五件套目录
  - tests=TEST-025,TEST-026,TEST-054,TEST-023,TEST-024,TEST-055 | depends_on=ITASK-010
[x] `ITASK-012` FR-012 Python 后端必须逐步退回四类职责
  - tests=TEST-029 | depends_on=ITASK-011
[x] `ITASK-013` FR-013 Python 职责瘦身必须覆盖 `qa / implement / prd / release`
  - tests=TEST-033,TEST-052 | depends_on=ITASK-012
[x] `ITASK-014` FR-014 skill surface 的版本漂移必须先修复
  - tests=TEST-042,TEST-043,TEST-014 | depends_on=ITASK-013
[x] `ITASK-015` FR-015 迁移必须采用 trace-scorecard 或等价一致性回归
  - tests=TEST-038,TEST-031,TEST-039,TEST-056 | depends_on=ITASK-014
[x] `ITASK-016` FR-016 support surface 必须能够解释“为什么推荐这条 route”
  - tests=TEST-045 | depends_on=ITASK-015
[x] `ITASK-017` FR-017 本特性不得破坏 `v1.4.0` 已冻结的五层架构
  - tests=TEST-058 | depends_on=ITASK-016
[x] `ITASK-018` FR-018 prototype 在本 feature 中必须被条件触发并补入正式 requirement 链
  - tests=TEST-049,TEST-010,TEST-016,TEST-019,TEST-022,TEST-027,TEST-028,TEST-030,TEST-032,TEST-034,TEST-035,TEST-036,TEST-037,TEST-040,TEST-041,TEST-044,TEST-046,TEST-047,TEST-048,TEST-051,TEST-053,TEST-057,TEST-059,TEST-060 | depends_on=ITASK-017
