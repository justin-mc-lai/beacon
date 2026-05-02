# UX PRD：Prototype Design Intelligence And Governed Rendering Separation

**Feature**: `prototype-design-intelligence-and-governed-rendering-separation`
**Version**: `v1.3.11`

## 设计上下文
- 目标读者：Beacon 产品 owner、原型编译维护者、implement renderer 维护者
- 主要用例：冻结 prototype 设计推导分层, 阻断治理文案直出, 为 implement 提供正式设计中间工件
- 操作者状态：需要快速判断原型输出是否仍在 requirement truth 边界内，并阻断可见 UI 漂移
- 使用环境：桌面优先的需求评审、原型审阅、实现交付协作环境
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
- 首屏判断问题：用户进入 首页 后，第一眼需要先判断什么？
- 主判断：继续下钻、停留处理当前信息，还是先执行恢复/返回动作。
- 动作层级：查看管理总览, 进入重点项目, 进入项目详情, 返回首页, 查看运行中心, 查看恢复诊断

## 页面意图合同
### 首页
- 页面职责：先回答经营判断，展示项目数、阻塞数、当前交付和介入点。
- 支持判断：今天先盯哪些项目，而不是先看所有项目明细。
- 首屏必须展示：经营总览条, 重点介入区
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 管理总览
- 页面职责：提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。
- 支持判断：多项目之间谁健康、谁阻塞、谁接近可发布。
- 首屏必须展示：筛选与排序条, 项目注册表
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 项目详情
- 页面职责：成为接力页，展示版本线、主 PRD、并行 PRD、需求闭环和推荐动作。
- 支持判断：这条版本线当前停在哪个阶段，下一步应该推进哪里。
- 首屏必须展示：项目头部摘要, 版本与分支信息
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 运行中心
- 页面职责：只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。
- 支持判断：当前到底是 single、team 还是 ralph 在推进。
- 首屏必须展示：运行态摘要头部, single / team / ralph 模式切换
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 恢复诊断
- 页面职责：解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。
- 支持判断：当前是 degraded、rebuild 还是 doctor 场景。
- 首屏必须展示：truth 来源说明, degraded / rebuild / doctor 诊断卡
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 项目物料查看器
- 页面职责：按 version -> document type -> feature 提供只读 Markdown 浏览。
- 支持判断：当前要看哪个版本、哪类文档、哪个 feature。
- 首屏必须展示：版本树, 文档类型列表
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细
### 物料文档详情
- 页面职责：冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。
- 支持判断：当前读的是哪一版、哪一类、哪个 feature 的文档。
- 首屏必须展示：文档头部信息, 版本 / 类型 / feature 面包屑
- 首屏禁止展示：transaction_id, projection metadata, 无边界 runtime 明细

## 状态可见性合同
- `ready`：首页 当前发生了什么，我下一步该做什么？
  - 必要反馈：展示项目数、阻塞数、当前交付和下一步。
  - 主动作：查看管理总览, 进入重点项目
  - 恢复动作：继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `blocked`：首页 当前发生了什么，我下一步该做什么？
  - 必要反馈：把阻塞项目和介入点提升到首屏。, 明确恢复动作与回退路径。
  - 主动作：查看管理总览, 进入重点项目
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `intervention-needed`：首页 当前发生了什么，我下一步该做什么？
  - 必要反馈：强调需要 CEO / 负责人介入的项目。
  - 主动作：查看管理总览, 进入重点项目
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `loading`：首页 当前发生了什么，我下一步该做什么？
  - 必要反馈：首页摘要数据仍在汇总。
  - 主动作：查看管理总览, 进入重点项目
  - 恢复动作：继续等待数据加载, 返回上一层
  - AC Refs: -
  - TC Refs: -
- `empty`：首页 当前发生了什么，我下一步该做什么？
  - 必要反馈：当前没有受管项目。, 解释为什么为空，以及回到哪里继续。
  - 主动作：查看管理总览, 进入重点项目
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `error`：首页 当前发生了什么，我下一步该做什么？
  - 必要反馈：摘要聚合失败，但提示可以进入详情或 doctor。, 明确恢复动作与回退路径。
  - 主动作：查看管理总览, 进入重点项目
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `filtered`：管理总览 当前发生了什么，我下一步该做什么？
  - 必要反馈：按阶段、版本、健康态筛选项目。
  - 主动作：进入项目详情, 返回首页
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `requirement-missing`：项目详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：PRD / user-story / test-case 存在缺口。
  - 主动作：查看运行中心, 查看恢复诊断, 查看项目物料
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `draft`：项目详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：需求已建立但未冻结。
  - 主动作：查看运行中心, 查看恢复诊断, 查看项目物料
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `frozen`：项目详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：需求链与 prototype 都已冻结。
  - 主动作：查看运行中心, 查看恢复诊断, 查看项目物料
  - 恢复动作：继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `runtime-active`：项目详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：存在 single / team / ralph 运行摘要。
  - 主动作：查看运行中心, 查看恢复诊断, 查看项目物料
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `single-active`：运行中心 当前发生了什么，我下一步该做什么？
  - 必要反馈：展示单进程执行摘要和 linked run。
  - 主动作：返回项目详情, 返回管理总览
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `team-active`：运行中心 当前发生了什么，我下一步该做什么？
  - 必要反馈：展示 agent 数、角色、状态和 host session metadata。
  - 主动作：返回项目详情, 返回管理总览
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `ralph-active`：运行中心 当前发生了什么，我下一步该做什么？
  - 必要反馈：展示 round_count、failure_streak、next_action、blocker。
  - 主动作：返回项目详情, 返回管理总览
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `idle`：运行中心 当前发生了什么，我下一步该做什么？
  - 必要反馈：当前没有任何 active runtime。, 解释为什么为空，以及回到哪里继续。
  - 主动作：返回项目详情, 返回管理总览
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `healthy-warning`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：当前系统可用但存在恢复风险提示。
  - 主动作：返回项目详情, 前往运行中心
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `degraded`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。
  - 主动作：返回项目详情, 前往运行中心
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `rebuild-suggested`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：投影层需要重建。
  - 主动作：返回项目详情, 前往运行中心
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `doctor-suggested`：恢复诊断 当前发生了什么，我下一步该做什么？
  - 必要反馈：推荐执行 doctor 修复上下文。
  - 主动作：返回项目详情, 前往运行中心
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `document-open`：项目物料查看器 当前发生了什么，我下一步该做什么？
  - 必要反馈：右侧阅读区显示当前文档正文。
  - 主动作：打开文档, 返回项目详情
  - 恢复动作：继续主要操作, 进入下一层或返回上层
  - AC Refs: -
  - TC Refs: -
- `source-missing`：项目物料查看器 当前发生了什么，我下一步该做什么？
  - 必要反馈：目标文档不存在或暂不可读。, 明确恢复动作与回退路径。
  - 主动作：打开文档, 返回项目详情
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `sibling-switch`：物料文档详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：在阅读区切换相邻文档。
  - 主动作：返回物料查看器, 切换同版本文档
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -
- `version-switch`：物料文档详情 当前发生了什么，我下一步该做什么？
  - 必要反馈：切换到同类型的其他版本文档。
  - 主动作：返回物料查看器, 切换同版本文档
  - 恢复动作：返回上一层, 重试当前动作
  - AC Refs: -
  - TC Refs: -

## Traceability
- AC Refs: AC-001, AC-002, AC-003, AC-004, AC-005, AC-101, AC-102, AC-103, AC-104, AC-201, AC-202, AC-203
- TC Refs: TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-012
