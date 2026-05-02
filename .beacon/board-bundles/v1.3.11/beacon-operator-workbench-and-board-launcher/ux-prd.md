# UX PRD：beacon-operator-workbench-and-board-launcher

**Feature**: `beacon-operator-workbench-and-board-launcher`
**Version**: `v1.3.11`

## Design Context
- Target Audience: Beacon 管理者 / 需求 owner / 实现协作者
- Primary Use Cases: 快速理解页面先服务哪一个判断, 冻结页面下钻路径与状态反馈, 为 implement / qa 提供统一的 UX truth
- Operator Mental State: 需要在有限时间内完成判断与推进，而不是阅读泛化说明。
- Usage Environment: 桌面优先的管理工作台与需求协作评审环境。
- Brand Tone: quiet, precise, operational, content-first
- Density Preference: workbench-medium

## Design Reasoning
- Product Surface Type: management-workbench
- Interaction Model: recognition-first navigation with low-noise drill-down and explicit recovery paths
- Layout Pattern: header -> primary judgment -> supporting context -> next action

## UX Contract
- First Glance Question: 用户进入 恢复诊断 后，第一眼需要先判断什么？
- Primary Decision: 继续下钻、停留处理当前信息，还是先执行恢复/返回动作。
- Action Hierarchy: 进入portfolio-board, 进入execution-board, 进入feature-detail

## Page Intent Contracts
### 恢复诊断
- Why: 解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。
- Decision Supported: 当前是 degraded、rebuild 还是 doctor 场景。
- Must Show First: truth 来源说明, degraded / rebuild / doctor 诊断卡
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### portfolio-board
- Why: 冻结 `portfolio-board` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Decision Supported: 冻结 `portfolio-board` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Must Show First: 页面头部, 关键内容区
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### execution-board
- Why: 冻结 `execution-board` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Decision Supported: 冻结 `execution-board` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Must Show First: 页面头部, 关键内容区
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### feature-detail
- Why: 冻结 `feature-detail` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Decision Supported: 冻结 `feature-detail` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Must Show First: 页面头部, 关键内容区
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### run-detail
- Why: 冻结 `run-detail` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Decision Supported: 冻结 `run-detail` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Must Show First: 页面头部, 关键内容区
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### review-surface
- Why: 冻结 `review-surface` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Decision Supported: 冻结 `review-surface` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。
- Must Show First: 页面头部, 关键内容区
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细

## State Visibility Contracts
- `healthy-warning`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 当前系统可用但存在恢复风险提示。
  - Primary Actions: 进入portfolio-board
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `degraded`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。
  - Primary Actions: 进入portfolio-board
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `rebuild-suggested`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 投影层需要重建。
  - Primary Actions: 进入portfolio-board
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `doctor-suggested`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 推荐执行 doctor 修复上下文。
  - Primary Actions: 进入portfolio-board
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `loading`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 诊断结果仍在采集。
  - Primary Actions: 进入portfolio-board
  - Recovery Actions: 继续等待数据加载, 返回上一层
  - AC Refs: -
  - TC Refs: -
- `error`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 诊断页本身无法完成聚合。, 明确恢复动作与回退路径。
  - Primary Actions: 进入portfolio-board
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `ready`: portfolio-board 当前发生了什么，我下一步该做什么？
  - Required Feedback: 页面数据齐备，用户可完成核心操作。
  - Primary Actions: 进入execution-board
  - Recovery Actions: 继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -

## Traceability
- AC Refs: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-101, AC-102, AC-103, AC-104, AC-201, AC-202
- TC Refs: TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-012
