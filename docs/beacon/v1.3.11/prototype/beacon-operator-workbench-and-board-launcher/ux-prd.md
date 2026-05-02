# UX PRD：Beacon Operator Workbench And Board Launcher

**Feature**: `beacon-operator-workbench-and-board-launcher`
**Version**: `v1.3.11`

## 设计上下文
- 目标读者：Beacon operator、交付负责人、需求冻结维护者
- 主要用例：判断当前执行波次, 处理阻塞 run, 进入恢复路径, 校验交付闭环
- 操作者状态：需要先判断当前状态、当前阻塞与下一步动作，再决定是否继续、重试或回修
- 使用环境：桌面优先的本地执行工作台与版本交付审阅环境
- 语义基调：formal, restrained, precise, operational
- 信息密度：workbench-medium

## 设计原则
- 产品表面类型：management-workbench
- 交互模型：recognition-first navigation with low-noise drill-down and explicit recovery paths
- 版式模式：header -> primary judgment -> supporting context -> next action

## 软件语义规范
- 标题规则：标题仅陈述对象或状态，不解释设计意图。
- 状态规则：状态文案必须先说明当前状态，再说明允许动作或禁止动作。
- 动作规则：动作名称必须使用可执行动词，不使用泛化 SaaS 词汇。
- 异常规则：异常文案必须同时给出当前失败与恢复路径。

## 交互合同
- 首屏判断问题：用户进入 恢复诊断 后，第一眼需要先判断什么？
- 主判断：继续下钻、停留处理当前信息，还是先执行恢复/返回动作。
- 动作层级：进入项目组合看板, 进入执行看板, 进入功能详情, 进入运行详情, 进入恢复诊断, 进入功能详情

## 页面意图合同
### 恢复诊断
- 页面职责：解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。
- 支持判断：当前是 degraded、rebuild 还是 doctor 场景。
- 首屏必须展示：truth 来源说明, degraded / rebuild / doctor 诊断卡
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 项目组合看板
- 页面职责：汇总当前版本线的 feature 状态、阻塞分布与建议波次，支持先判断先处理哪一组事项。
- 支持判断：当前应先进入阻塞 feature、待验收 feature，还是继续观察整体版本健康态。
- 首屏必须展示：状态摘要, 阻塞分组
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 执行看板
- 页面职责：先暴露当前运行状态、阻塞项与下一步动作，而不是先展示全量运行历史。
- 支持判断：当前应继续、停止、重试，还是先进入恢复路径。
- 首屏必须展示：当前状态, 当前阻塞
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 功能详情
- 页面职责：聚合单个 feature 的基线、依赖、当前状态与建议动作，支持判断是否继续实现或先回修。
- 支持判断：当前 feature 应继续推进、等待依赖，还是进入恢复或验收路径。
- 首屏必须展示：功能摘要, 依赖与基线
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 运行详情
- 页面职责：聚合单次运行的状态时间线、写入范围、证据与建议动作，避免操作者在散落材料中自行拼接上下文。
- 支持判断：当前运行应继续、停止、重试，还是转入 repair handoff。
- 首屏必须展示：运行状态, 阻塞原因
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 验收面
- 页面职责：集中展示差异入口、验收证据与发布提示，支持判断是否放行或回修。
- 支持判断：当前项应通过验收、回到修复路径，还是继续收集证据。
- 首屏必须展示：验收状态, 差异入口
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细

## 状态可见性合同
- `healthy-warning`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：当前系统可用但存在恢复风险提示。
  - 主动作：进入项目组合看板
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `degraded`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。
  - 主动作：进入项目组合看板
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `rebuild-suggested`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：投影层需要重建。
  - 主动作：进入项目组合看板
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `doctor-suggested`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：推荐执行 doctor 修复上下文。
  - 主动作：进入项目组合看板
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `loading`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：诊断结果仍在采集。
  - 主动作：进入项目组合看板
  - 恢复动作：继续等待数据加载, 返回上一层
  - AC Refs: -
  - TC Refs: -
- `error`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：诊断页本身无法完成聚合。, 明确恢复动作与回退路径。
  - 主动作：进入项目组合看板
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `ready`：项目组合看板 当前发生了什么，我下一步该做什么？
  - 必要反馈：组合状态已汇总，可继续下钻。
  - 主动作：进入执行看板, 进入功能详情
  - 恢复动作：继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `blocked`：项目组合看板 当前发生了什么，我下一步该做什么？
  - 必要反馈：存在需要优先介入的阻塞 feature。, 明确恢复动作与回退路径。
  - 主动作：进入执行看板, 进入功能详情
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `needs-review`：项目组合看板 当前发生了什么，我下一步该做什么？
  - 必要反馈：存在需要进入验收面的 feature。
  - 主动作：进入执行看板, 进入功能详情
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `retry-scheduled`：执行看板 当前发生了什么，我下一步该做什么？
  - 必要反馈：存在待重试运行，需确认是否继续。
  - 主动作：进入运行详情, 进入恢复诊断, 进入功能详情
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `running`：运行详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：当前运行仍在推进。
  - 主动作：进入恢复诊断, 进入验收面
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `needs-evidence`：验收面 当前发生了什么，我下一步该做什么？
  - 必要反馈：验收证据不足，不能放行。
  - 主动作：返回运行详情, 进入恢复诊断
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -

## Traceability
- AC Refs: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-101, AC-102, AC-103
- TC Refs: TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-012
