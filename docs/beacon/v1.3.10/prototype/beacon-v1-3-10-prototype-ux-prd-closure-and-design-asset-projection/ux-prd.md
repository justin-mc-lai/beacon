# UX PRD：Beacon v1.3.10 prototype UX PRD closure and design-asset projection

**Feature**: `beacon-v1-3-10-prototype-ux-prd-closure-and-design-asset-projection`
**Version**: `v1.3.10`

## Design Context
- Target Audience: Beacon 管理者 / 需求 owner / 实现协作者
- Primary Use Cases: 快速理解页面先服务哪一个判断
- Operator Mental State: 需要在有限时间内完成判断与推进，而不是阅读泛化说明。
- Usage Environment: 桌面优先的管理工作台与需求协作评审环境。
- Brand Tone: quiet
- Density Preference: workbench-medium

## Design Reasoning
- Product Surface Type: management-workbench
- Interaction Model: recognition-first navigation with low-noise drill-down and explicit recovery paths
- Layout Pattern: header -> primary judgment -> supporting context -> next action

## UX Contract
- First Glance Question: 用户进入 首页 后，第一眼需要先判断什么？
- Primary Decision: 继续下钻、停留处理当前信息，还是先执行恢复/返回动作。
- Action Hierarchy: 查看管理总览, 进入重点项目, 进入项目详情, 返回首页, 查看运行中心, 查看恢复诊断

## Page Intent Contracts
### 首页
- Why: 先回答经营判断，展示项目数、阻塞数、当前交付和介入点。
- Decision Supported: 今天先盯哪些项目，而不是先看所有项目明细。
- Must Show First: 经营总览条, 重点介入区
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### 管理总览
- Why: 提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。
- Decision Supported: 多项目之间谁健康、谁阻塞、谁接近可发布。
- Must Show First: 筛选与排序条, 项目注册表
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### 项目详情
- Why: 成为接力页，展示版本线、主 PRD、并行 PRD、需求闭环和推荐动作。
- Decision Supported: 这条版本线当前停在哪个阶段，下一步应该推进哪里。
- Must Show First: 项目头部摘要, 版本与分支信息
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### 运行中心
- Why: 只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。
- Decision Supported: 当前到底是 single、team 还是 ralph 在推进。
- Must Show First: 运行态摘要头部, single / team / ralph 模式切换
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### 恢复诊断
- Why: 解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。
- Decision Supported: 当前是 degraded、rebuild 还是 doctor 场景。
- Must Show First: truth 来源说明, degraded / rebuild / doctor 诊断卡
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### 项目物料查看器
- Why: 按 version -> document type -> feature 提供只读 Markdown 浏览。
- Decision Supported: 当前要看哪个版本、哪类文档、哪个 feature。
- Must Show First: 版本树, 文档类型列表
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细
### 物料文档详情
- Why: 冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。
- Decision Supported: 当前读的是哪一版、哪一类、哪个 feature 的文档。
- Must Show First: 文档头部信息, 版本 / 类型 / feature 面包屑
- Must Not Show: transaction_id, projection metadata, 无边界 runtime 明细

## State Visibility Contracts
- `ready`: 首页 当前发生了什么，我下一步该做什么？
  - Required Feedback: 展示项目数、阻塞数、当前交付和下一步。
  - Primary Actions: 查看管理总览, 进入重点项目
  - Recovery Actions: 继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `blocked`: 首页 当前发生了什么，我下一步该做什么？
  - Required Feedback: 把阻塞项目和介入点提升到首屏。, 明确恢复动作与回退路径。
  - Primary Actions: 查看管理总览, 进入重点项目
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `intervention-needed`: 首页 当前发生了什么，我下一步该做什么？
  - Required Feedback: 强调需要 CEO / 负责人介入的项目。
  - Primary Actions: 查看管理总览, 进入重点项目
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `loading`: 首页 当前发生了什么，我下一步该做什么？
  - Required Feedback: 首页摘要数据仍在汇总。
  - Primary Actions: 查看管理总览, 进入重点项目
  - Recovery Actions: 继续等待数据加载, 返回上一层
  - AC Refs: -
  - TC Refs: -
- `empty`: 首页 当前发生了什么，我下一步该做什么？
  - Required Feedback: 当前没有受管项目。, 解释为什么为空，以及回到哪里继续。
  - Primary Actions: 查看管理总览, 进入重点项目
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `error`: 首页 当前发生了什么，我下一步该做什么？
  - Required Feedback: 摘要聚合失败，但提示可以进入详情或 doctor。, 明确恢复动作与回退路径。
  - Primary Actions: 查看管理总览, 进入重点项目
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `filtered`: 管理总览 当前发生了什么，我下一步该做什么？
  - Required Feedback: 按阶段、版本、健康态筛选项目。
  - Primary Actions: 进入项目详情, 返回首页
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `requirement-missing`: 项目详情 当前发生了什么，我下一步该做什么？
  - Required Feedback: PRD / user-story / test-case 存在缺口。
  - Primary Actions: 查看运行中心, 查看恢复诊断, 查看项目物料
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `draft`: 项目详情 当前发生了什么，我下一步该做什么？
  - Required Feedback: 需求已建立但未冻结。
  - Primary Actions: 查看运行中心, 查看恢复诊断, 查看项目物料
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `frozen`: 项目详情 当前发生了什么，我下一步该做什么？
  - Required Feedback: 需求链与 prototype 都已冻结。
  - Primary Actions: 查看运行中心, 查看恢复诊断, 查看项目物料
  - Recovery Actions: 继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `runtime-active`: 项目详情 当前发生了什么，我下一步该做什么？
  - Required Feedback: 存在 single / team / ralph 运行摘要。
  - Primary Actions: 查看运行中心, 查看恢复诊断, 查看项目物料
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `single-active`: 运行中心 当前发生了什么，我下一步该做什么？
  - Required Feedback: 展示单进程执行摘要和 linked run。
  - Primary Actions: 返回项目详情, 返回管理总览
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `team-active`: 运行中心 当前发生了什么，我下一步该做什么？
  - Required Feedback: 展示 agent 数、角色、状态和 host session metadata。
  - Primary Actions: 返回项目详情, 返回管理总览
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `ralph-active`: 运行中心 当前发生了什么，我下一步该做什么？
  - Required Feedback: 展示 round_count、failure_streak、next_action、blocker。
  - Primary Actions: 返回项目详情, 返回管理总览
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `idle`: 运行中心 当前发生了什么，我下一步该做什么？
  - Required Feedback: 当前没有任何 active runtime。, 解释为什么为空，以及回到哪里继续。
  - Primary Actions: 返回项目详情, 返回管理总览
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `healthy-warning`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 当前系统可用但存在恢复风险提示。
  - Primary Actions: 返回项目详情, 前往运行中心
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `degraded`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。
  - Primary Actions: 返回项目详情, 前往运行中心
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `rebuild-suggested`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 投影层需要重建。
  - Primary Actions: 返回项目详情, 前往运行中心
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `doctor-suggested`: 恢复诊断 当前发生了什么，我下一步该做什么？
  - Required Feedback: 推荐执行 doctor 修复上下文。
  - Primary Actions: 返回项目详情, 前往运行中心
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `document-open`: 项目物料查看器 当前发生了什么，我下一步该做什么？
  - Required Feedback: 右侧阅读区显示当前文档正文。
  - Primary Actions: 打开文档, 返回项目详情
  - Recovery Actions: 继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `source-missing`: 项目物料查看器 当前发生了什么，我下一步该做什么？
  - Required Feedback: 目标文档不存在或暂不可读。, 明确恢复动作与回退路径。
  - Primary Actions: 打开文档, 返回项目详情
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `sibling-switch`: 物料文档详情 当前发生了什么，我下一步该做什么？
  - Required Feedback: 在阅读区切换相邻文档。
  - Primary Actions: 返回物料查看器, 切换同版本文档
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `version-switch`: 物料文档详情 当前发生了什么，我下一步该做什么？
  - Required Feedback: 切换到同类型的其他版本文档。
  - Primary Actions: 返回物料查看器, 切换同版本文档
  - Recovery Actions: 返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -

## Traceability
- AC Refs: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-101, AC-102, AC-103, AC-201
- TC Refs: TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-012
