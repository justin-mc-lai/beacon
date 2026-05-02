# 自动化优先级矩阵：Beacon Operator Workbench And Board Launcher

| Target ID | Target Type | Priority Class | Reason | AC Refs | TC Refs |
|---|---|---|---|---|---|
| `recovery-diagnostics:healthy-warning` | `state` | `manual-acceptable` | 当前系统可用但存在恢复风险提示。 | - | - |
| `recovery-diagnostics:degraded` | `state` | `manual-acceptable` | SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。 | - | - |
| `recovery-diagnostics:rebuild-suggested` | `state` | `manual-acceptable` | 投影层需要重建。 | - | - |
| `recovery-diagnostics:doctor-suggested` | `state` | `manual-acceptable` | 推荐执行 doctor 修复上下文。 | - | - |
| `recovery-diagnostics:loading` | `state` | `manual-acceptable` | 诊断结果仍在采集。 | - | - |
| `recovery-diagnostics:error` | `state` | `manual-acceptable` | 诊断页本身无法完成聚合。 | - | - |
| `portfolio-board:ready` | `state` | `manual-acceptable` | 组合状态已汇总，可继续下钻。 | - | - |
| `portfolio-board:blocked` | `state` | `manual-acceptable` | 存在需要优先介入的阻塞 feature。 | - | - |
| `portfolio-board:needs-review` | `state` | `manual-acceptable` | 存在需要进入验收面的 feature。 | - | - |
| `portfolio-board:loading` | `state` | `manual-acceptable` | 组合状态仍在汇总。 | - | - |
| `portfolio-board:error` | `state` | `manual-acceptable` | 组合聚合失败，必须给出恢复入口。 | - | - |
| `execution-board:ready` | `state` | `manual-acceptable` | 当前运行态完整，可执行继续、停止或重试。 | - | - |
| `execution-board:blocked` | `state` | `manual-acceptable` | 存在阻塞运行，必须优先判断恢复路径。 | - | - |
| `execution-board:needs-review` | `state` | `manual-acceptable` | 存在待验收运行，需要进入验收面。 | - | - |
| `execution-board:retry-scheduled` | `state` | `manual-acceptable` | 存在待重试运行，需确认是否继续。 | - | - |
| `execution-board:loading` | `state` | `manual-acceptable` | 运行状态仍在读取。 | - | - |
| `execution-board:error` | `state` | `manual-acceptable` | 运行状态读取失败，必须暴露恢复路径。 | - | - |
| `feature-detail:ready` | `state` | `manual-acceptable` | 功能状态完整，可判断下一步。 | - | - |
| `feature-detail:blocked` | `state` | `manual-acceptable` | 功能依赖或基线存在阻塞。 | - | - |
| `feature-detail:needs-review` | `state` | `manual-acceptable` | 功能已进入待验收状态。 | - | - |
| `feature-detail:error` | `state` | `manual-acceptable` | 功能状态聚合失败，需进入恢复路径。 | - | - |
| `run-detail:running` | `state` | `manual-acceptable` | 当前运行仍在推进。 | - | - |
| `run-detail:blocked` | `state` | `manual-acceptable` | 当前运行被阻断，必须优先判断恢复动作。 | - | - |
| `run-detail:needs-review` | `state` | `manual-acceptable` | 当前运行等待验收。 | - | - |
| `run-detail:retry-scheduled` | `state` | `manual-acceptable` | 当前运行等待重试。 | - | - |
| `run-detail:error` | `state` | `manual-acceptable` | 当前运行状态不一致，必须暴露恢复路径。 | - | - |
| `review-surface:ready` | `state` | `manual-acceptable` | 验收证据完整，可判断是否放行。 | - | - |
| `review-surface:needs-evidence` | `state` | `manual-acceptable` | 验收证据不足，不能放行。 | - | - |
| `review-surface:blocked` | `state` | `manual-acceptable` | 验收存在阻塞，必须进入回修路径。 | - | - |
| `review-surface:error` | `state` | `manual-acceptable` | 验收聚合失败，需优先给出恢复动作。 | - | - |
| `recovery-diagnostics:ready->portfolio-board:ready` | `transition` | `primary-automation` | 点击跳转 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `portfolio-board:ready->execution-board:ready` | `transition` | `release-blocker` | 点击跳转 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `execution-board:ready->feature-detail:ready` | `transition` | `primary-automation` | 点击跳转 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `feature-detail:ready->run-detail:ready` | `transition` | `primary-automation` | 点击跳转 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `run-detail:ready->review-surface:ready` | `transition` | `primary-automation` | 点击跳转 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `recovery-diagnostics-component-01` | `component` | `primary-automation` | truth 来源说明 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-02` | `component` | `primary-automation` | degraded / rebuild / doctor 诊断卡 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-03` | `component` | `primary-automation` | 恢复步骤 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-04` | `component` | `primary-automation` | 风险提示 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `portfolio-board-component-01` | `component` | `primary-automation` | 状态摘要 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `portfolio-board-component-02` | `component` | `primary-automation` | 阻塞分组 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `portfolio-board-component-03` | `component` | `primary-automation` | 待验收分组 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `portfolio-board-component-04` | `component` | `primary-automation` | 下一步动作 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `execution-board-component-01` | `component` | `primary-automation` | 当前状态 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `execution-board-component-02` | `component` | `primary-automation` | 当前阻塞 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `execution-board-component-03` | `component` | `primary-automation` | 下一步动作 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `execution-board-component-04` | `component` | `primary-automation` | 运行分组 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `feature-detail-component-01` | `component` | `primary-automation` | 功能摘要 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `feature-detail-component-02` | `component` | `primary-automation` | 依赖与基线 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `feature-detail-component-03` | `component` | `primary-automation` | 状态与风险 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `feature-detail-component-04` | `component` | `primary-automation` | 下一步动作 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `run-detail-component-01` | `component` | `primary-automation` | 运行状态 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `run-detail-component-02` | `component` | `primary-automation` | 阻塞原因 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `run-detail-component-03` | `component` | `primary-automation` | 建议动作 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `run-detail-component-04` | `component` | `primary-automation` | 二级明细 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `review-surface-component-01` | `component` | `primary-automation` | 验收状态 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `review-surface-component-02` | `component` | `primary-automation` | 差异入口 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `review-surface-component-03` | `component` | `primary-automation` | 证据入口 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `review-surface-component-04` | `component` | `primary-automation` | 放行建议 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
