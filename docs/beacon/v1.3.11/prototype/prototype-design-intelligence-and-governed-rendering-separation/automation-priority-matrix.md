# 自动化优先级矩阵：prototype-design-intelligence-and-governed-rendering-separation

| Target ID | Target Type | Priority Class | Reason | AC Refs | TC Refs |
|---|---|---|---|---|---|
| `home:ready` | `state` | `manual-acceptable` | 展示项目数、阻塞数、当前交付和下一步。 | - | - |
| `home:blocked` | `state` | `manual-acceptable` | 把阻塞项目和介入点提升到首屏。 | - | - |
| `home:intervention-needed` | `state` | `manual-acceptable` | 强调需要 CEO / 负责人介入的项目。 | - | - |
| `home:loading` | `state` | `manual-acceptable` | 首页摘要数据仍在汇总。 | - | - |
| `home:empty` | `state` | `manual-acceptable` | 当前没有受管项目。 | - | - |
| `home:error` | `state` | `manual-acceptable` | 摘要聚合失败，但提示可以进入详情或 doctor。 | - | - |
| `management-overview:ready` | `state` | `manual-acceptable` | 密集展示多项目当前状态。 | - | - |
| `management-overview:filtered` | `state` | `manual-acceptable` | 按阶段、版本、健康态筛选项目。 | - | - |
| `management-overview:empty` | `state` | `manual-acceptable` | 没有任何受管项目进入注册表。 | - | - |
| `management-overview:loading` | `state` | `manual-acceptable` | 项目注册表正在聚合。 | - | - |
| `management-overview:error` | `state` | `manual-acceptable` | 总览聚合失败但保留恢复提示。 | - | - |
| `project-detail:ready` | `state` | `manual-acceptable` | 版本、PRD、需求闭环和下一步信息完整。 | - | - |
| `project-detail:requirement-missing` | `state` | `manual-acceptable` | PRD / user-story / test-case 存在缺口。 | - | - |
| `project-detail:draft` | `state` | `manual-acceptable` | 需求已建立但未冻结。 | - | - |
| `project-detail:frozen` | `state` | `manual-acceptable` | 需求链与 prototype 都已冻结。 | - | - |
| `project-detail:runtime-active` | `state` | `manual-acceptable` | 存在 single / team / ralph 运行摘要。 | - | - |
| `project-detail:loading` | `state` | `manual-acceptable` | 项目详情正在聚合。 | - | - |
| `project-detail:error` | `state` | `manual-acceptable` | 详情聚合失败但给出恢复链路。 | - | - |
| `runtime-center:single-active` | `state` | `manual-acceptable` | 展示单进程执行摘要和 linked run。 | - | - |
| `runtime-center:team-active` | `state` | `manual-acceptable` | 展示 agent 数、角色、状态和 host session metadata。 | - | - |
| `runtime-center:ralph-active` | `state` | `manual-acceptable` | 展示 round_count、failure_streak、next_action、blocker。 | - | - |
| `runtime-center:idle` | `state` | `manual-acceptable` | 当前没有任何 active runtime。 | - | - |
| `runtime-center:loading` | `state` | `manual-acceptable` | 运行态数据仍在读取。 | - | - |
| `runtime-center:error` | `state` | `manual-acceptable` | 运行态投影异常，需要回到诊断页。 | - | - |
| `recovery-diagnostics:healthy-warning` | `state` | `manual-acceptable` | 当前系统可用但存在恢复风险提示。 | - | - |
| `recovery-diagnostics:degraded` | `state` | `manual-acceptable` | SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。 | - | - |
| `recovery-diagnostics:rebuild-suggested` | `state` | `manual-acceptable` | 投影层需要重建。 | - | - |
| `recovery-diagnostics:doctor-suggested` | `state` | `manual-acceptable` | 推荐执行 doctor 修复上下文。 | - | - |
| `recovery-diagnostics:loading` | `state` | `manual-acceptable` | 诊断结果仍在采集。 | - | - |
| `recovery-diagnostics:error` | `state` | `manual-acceptable` | 诊断页本身无法完成聚合。 | - | - |
| `material-viewer:ready` | `state` | `manual-acceptable` | 版本树和文档列表已加载。 | - | - |
| `material-viewer:document-open` | `state` | `manual-acceptable` | 右侧阅读区显示当前文档正文。 | - | - |
| `material-viewer:source-missing` | `state` | `manual-acceptable` | 目标文档不存在或暂不可读。 | - | - |
| `material-viewer:loading` | `state` | `manual-acceptable` | 文档列表或内容仍在加载。 | - | - |
| `material-viewer:empty` | `state` | `manual-acceptable` | 该版本或类型下没有可读文档。 | - | - |
| `material-viewer:error` | `state` | `manual-acceptable` | 文档读取失败。 | - | - |
| `material-document-detail:ready` | `state` | `manual-acceptable` | 显示文档正文与来源路径。 | - | - |
| `material-document-detail:sibling-switch` | `state` | `manual-acceptable` | 在阅读区切换相邻文档。 | - | - |
| `material-document-detail:version-switch` | `state` | `manual-acceptable` | 切换到同类型的其他版本文档。 | - | - |
| `material-document-detail:source-missing` | `state` | `manual-acceptable` | 文档不存在或来源路径不可达。 | - | - |
| `home:ready->management-overview:ready` | `transition` | `release-blocker` | 点击项目组合入口 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `home:ready->project-detail:ready` | `transition` | `release-blocker` | 点击重点项目卡片 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `management-overview:ready->project-detail:ready` | `transition` | `release-blocker` | 点击项目行/卡片 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `management-overview:ready->home:ready` | `transition` | `release-blocker` | 点击首页导航 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `project-detail:ready->runtime-center:ready` | `transition` | `primary-automation` | 点击运行态摘要 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `project-detail:ready->recovery-diagnostics:ready` | `transition` | `primary-automation` | 点击恢复诊断入口 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `project-detail:ready->material-viewer:ready` | `transition` | `primary-automation` | 点击文档查看入口 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `project-detail:ready->management-overview:ready` | `transition` | `release-blocker` | 点击返回 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `runtime-center:ready->project-detail:ready` | `transition` | `release-blocker` | 点击返回 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `runtime-center:ready->management-overview:ready` | `transition` | `release-blocker` | 点击面包屑 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `recovery-diagnostics:ready->project-detail:ready` | `transition` | `release-blocker` | 点击返回 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `recovery-diagnostics:ready->runtime-center:ready` | `transition` | `primary-automation` | 点击运行态关联 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `material-viewer:ready->project-detail:ready` | `transition` | `release-blocker` | 点击返回 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `material-viewer:ready->material-document-detail:ready` | `transition` | `primary-automation` | 点击文档列表项 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `material-document-detail:ready->material-viewer:ready` | `transition` | `primary-automation` | 点击返回 transition must preserve guard, fallback, and evidence binding. | AC-001 | TC-001 |
| `home-component-01` | `component` | `primary-automation` | 经营总览条 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `home-component-02` | `component` | `primary-automation` | 重点介入区 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `home-component-03` | `component` | `primary-automation` | 项目推进摘要 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `home-component-04` | `component` | `primary-automation` | 当前交付卡片 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `home-component-05` | `component` | `primary-automation` | 下一步建议 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-01` | `component` | `primary-automation` | 筛选与排序条 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-02` | `component` | `primary-automation` | 项目注册表 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-03` | `component` | `primary-automation` | 阶段分布摘要 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-04` | `component` | `primary-automation` | 风险与调试摘要 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `management-overview-component-05` | `component` | `primary-automation` | 推荐 skill 区 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `project-detail-component-01` | `component` | `primary-automation` | 项目头部摘要 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `project-detail-component-02` | `component` | `primary-automation` | 版本与分支信息 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `project-detail-component-03` | `component` | `primary-automation` | 主 PRD 与并行 PRD owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `project-detail-component-04` | `component` | `primary-automation` | 需求物料闭环状态 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `project-detail-component-05` | `component` | `primary-automation` | 最近交付与下一步 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `project-detail-component-06` | `component` | `primary-automation` | 运行态摘要卡 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-01` | `component` | `primary-automation` | 运行态摘要头部 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-02` | `component` | `primary-automation` | single / team / ralph 模式切换 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-03` | `component` | `primary-automation` | agent/session 引用 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-04` | `component` | `primary-automation` | artifact 与 linked run owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `runtime-center-component-05` | `component` | `primary-automation` | 最近结果与 blocker owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-01` | `component` | `primary-automation` | truth 来源说明 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-02` | `component` | `primary-automation` | degraded / rebuild / doctor 诊断卡 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-03` | `component` | `primary-automation` | 恢复步骤 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `recovery-diagnostics-component-04` | `component` | `primary-automation` | 风险提示 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-01` | `component` | `primary-automation` | 版本树 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-02` | `component` | `primary-automation` | 文档类型列表 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-03` | `component` | `primary-automation` | feature 目录 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-04` | `component` | `primary-automation` | 文档阅读面板 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-viewer-component-05` | `component` | `primary-automation` | 来源路径信息 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-01` | `component` | `primary-automation` | 文档头部信息 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-02` | `component` | `primary-automation` | 版本 / 类型 / feature 面包屑 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-03` | `component` | `primary-automation` | Markdown 正文区 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-04` | `component` | `primary-automation` | 同类文档切换 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
| `material-document-detail-component-05` | `component` | `primary-automation` | 来源路径与只读说明 owns visible state feedback and interaction continuity. | AC-001, AC-002, AC-003, AC-004 | TC-001, TC-002, TC-003, TC-004 |
