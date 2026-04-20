# User Story: beacon-v1.3.6-visual-management-console-and-material-viewer

## Story

**As a** CEO / 一人公司经营者 / 项目负责人 / Beacon 运行治理者,  
**I want** Beacon 把多项目运行态、版本线、并行 PRD、需求物料与运行中心收口到一个可视化管理端，并提供项目物料 Markdown 只读查看器,  
**So that** 我可以先用极简的人类心智看清项目组合推进、当前交付和介入点，再按需下钻查看某个项目的版本演进、需求闭环、runtime 状态、agent/session 引用与恢复诊断信息。

## Story Slices

### US-001: 首页必须先回答经营判断

作为 CEO，我希望首页先告诉我有哪些项目在推进、推进到哪、当前交付了什么、哪里被阻塞、下一步需要谁介入，而不是先给我机器内部噪音。

### US-002: 总览页必须是多项目密集管理面

作为一人公司经营者，我希望 Beacon 管理端有一个稳定、密集、可扫描的项目注册表，让我能快速比较多个项目的阶段、健康度、物料完整度与运行摘要。

### US-003: 项目详情必须成为接力页

作为项目负责人，我希望进入项目详情后，可以看见当前版本、主 PRD、并行 PRD、生命周期、总进度、下一步和推荐 skill，便于继续推进而不是重新梳理上下文。

### US-004: 需求物料与版本演进必须清晰可读

作为需求负责人，我希望项目详情中能明确展示 `prd / user-story / test-case` 的补齐状态，以及当前版本下有哪些并行 PRD、哪些页面和交付物已经冻结。

### US-005: Markdown 物料查看器必须正式化但只读

作为项目负责人，我希望在管理端内直接查看 Beacon 版本文档、PRD、用户故事和测试用例，但这些文档只能网页只读查看，不能被 UI 直接改写。

### US-006: Runtime 中心必须只在需要时下钻

作为运行治理者，我希望首页和项目详情只展示运行态摘要，真正的 `single / team / ralph` 细节只在运行中心展开，避免 runtime 噪音抢占生命周期主轴。

### US-007: Team 模式必须可见多代理规模与会话引用

作为项目负责人，我希望当项目处于 `team` 模式时，可以看到当前 agent 数、角色、状态、linked run，以及 `Codex / Claude` session metadata 引用，而不是只看到一个泛化的“运行中”。

### US-008: Ralph 模式必须可见闭环推进状态

作为治理者，我希望当项目进入 `ralph` 闭环时，可以直接看到 `round_count`、`failure_streak`、`next_action`、`blocker` 和最近结果，以便判断是否仍在有效推进。

### US-009: 恢复诊断必须能解释 degraded 状态

作为恢复维护者，我希望当 SQLite、PocketBase 或 runtime 投影不可用时，管理端能明确说明 truth 仍来自 `docs/beacon` 与 `.beacon`，并给出 degraded / rebuild / doctor 提示。

### US-010: 真实项目并板必须可解释且边界稳定

作为 Beacon 管理者，我希望 `rolo / slow_uni_bmtop / shopxo_canada / beacon` 四个真实项目都能进入同一管理看板，并且保持 Beacon 产品边界，不把 `omc / omx` 之类外部系统并入默认视图。

### US-011: 页面实现必须回链 `v1.3.5` wireframe freeze

作为需求冻结者，我希望 `v1.3.6` 的正式页面都能回链到 `v1.3.5` 的 wireframe artifact，而不是继续依赖 HTML 高保真原型。

## Acceptance Criteria

- AC-001 首页生命周期优先：首页默认先展示项目数、阻塞数、活跃运行态数、重点介入区、项目清单、当前交付与下一步，不能先展示 runtime 洪流。
- AC-002 CEO 视图极简：首页默认不得出现 tmux pane、raw event、完整 transcript、宿主交互洪流等机器内部细节。
- AC-003 多项目密集管理：管理总览必须提供稳定的项目注册表，至少展示项目名、项目类型、当前版本、主 feature、当前阶段、总进度、健康态、debug 态、下一步与推荐 skill。
- AC-004 项目详情可接力：项目详情页必须展示版本线、主 PRD、并行 PRD、需求物料状态、当前阶段、最近交付摘要与推荐动作。
- AC-005 需求闭环可见：项目详情必须显式表达 `prd / user-story / test-case` 的 `missing / draft / ready / frozen` 或等价冻结状态。
- AC-006 Markdown 只读查看成立：管理端必须支持网页内查看版本包文档、PRD、user-story、test-case，但不得提供在线编辑能力。
- AC-007 文档查看按版本组织：Markdown 查看器必须可以按 `version -> document type -> feature` 浏览 Beacon 文档，并保留来源路径。
- AC-008 Runtime 下钻分层：首页和项目详情只展示 runtime 摘要；`single / team / ralph` 详细字段只在运行中心页展开。
- AC-009 Team 代理态透明：当 runtime 为 `team` 时，必须显示 agent 数、role、status、linked run、artifact 引用，以及 `Codex / Claude` session metadata 引用。
- AC-010 Ralph 闭环可观测：当 runtime 为 `ralph` 时，必须显示 `round_count / failure_streak / next_action / blocker / recent_result`。
- AC-011 Session 边界受控：管理端可以展示 `Codex / Claude` session 的有限 metadata、linked run 与 transcript ref，但不得把完整宿主会话系统并入 Beacon 真相层。
- AC-012 恢复诊断可解释：当 SQLite / PocketBase 缺失或投影失败时，页面必须明确 truth 仍来自 `docs/beacon` 与 `.beacon`，并展示 degraded / rebuild / doctor 提示。
- AC-013 产品边界稳定：默认看板只管理 Beacon 项目，不纳入 `omc / omx` 等 Beacon 外系统。
- AC-014 四个真实项目并板正确：`rolo / slow_uni_bmtop / shopxo_canada / beacon` 必须都可进入看板，并能解释其 `project_kind / lifecycle / debug state / next step`。
- AC-015 页面实现回链 freeze：项目页面的结构实现、路由关系与状态说明必须能回链到 `v1.3.5` wireframe artifact。
- AC-016 人类心智优先：在屏蔽机器交互细节时，管理端仍必须给出足够的人类可决策信息，不得因隐藏 runtime 细节而让项目状态不可判断。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | ready-for-implementation |
| Version | v1.3.6 |
| Track | main |
| Feature Slug | beacon-v1.3.6-visual-management-console-and-material-viewer |
| Upstream Freeze | v1.3.5 wireframe package |
| Projection Surface | Beacon 管理端 + 项目物料查看器 |
