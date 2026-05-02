# PRD：beacon-operator-workbench-and-board-launcher

**Feature**: `beacon-operator-workbench-and-board-launcher`  
**Version**: `v1.3.11`  
**Date**: `2026-05-01`  
**Status**: `draft`  
**Track**: `parallel`  
**Scenario**: `runtime_control_plane`  
**Semantic Label**: `运行态投影治理`  

target_audience: Beacon operator、交付负责人、需求冻结维护者
primary_use_cases: 判断当前执行波次, 处理阻塞 run, 进入恢复路径, 校验交付闭环
operator_mental_state: 需要先判断当前状态、当前阻塞与下一步动作，再决定是否继续、重试或回修
usage_environment: 桌面优先的本地执行工作台与版本交付审阅环境
brand_tone: formal, restrained, precise, operational
density_preference: workbench-medium
design_preset: apple-inspired-design-md

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.11/SUMMARY.md`
- Execution index: `docs/beacon/v1.3.11/execution/index.md`
- Runtime substrate dependency:
  - `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- Main runtime anchor PRD:
  - `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- External reference mirrors:
  - `/Users/apple/Developer/Personal/oss-sync/agents/agent-systems/vibe-kanban`
  - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/symphony`

## 1. 问题

### 1.1 当前断层

Beacon 当前已有：

- requirement truth board
- runtime projection summary
- portfolio/project detail
- release/readiness 类状态展示

但仍没有真正的 operator workbench。

当前 board 更像“治理摘要”，不能真正承担：

- 长任务队列观察
- run drilldown
- workspace/diff/log/preview 跳转
- retry/continue/stop/reconcile 操作
- 恢复告警与 repair path 导航

当前 prototype 与 board 还存在两类失真：

- 原型失真：输出更像通用后台资产页，不是 operator workbench prototype
- 语义失真：输出仍包含解释式、设计评审式、通用 SaaS 式文案，不满足正式、克制、严谨、专业、简洁、准确的软件语义约束

### 1.2 触发信号

- `vibe-kanban` 证明 operator 需要的不是更大号 status 页面，而是执行工作台
- `symphony` 证明 dashboard 只能建立在稳定 runtime 之上
- Beacon 真实项目验证已经开始需要“从 requirement truth 回看当前执行面”，仅靠 `status --board` 不够
- 后续若要提供本地可执行看板或桌面壳，必须先定义 workbench contract

### 1.3 为什么现在做

如果 Beacon 继续只强化 board 摘要而不建立 workbench，就会出现两种退化：

- 要么 UI 只负责展示，无法帮助 operator 干预长任务
- 要么 UI 自己发明状态逻辑，反向绕开 runtime kernel

## 2. 目标

### 2.1 主要目标

- 把 Beacon 当前 board 演进为真正的 operator workbench
- 保持 requirement-first lifecycle 不变，同时给长任务执行提供可视化管理面
- 提供统一 launcher contract，让本地启动 web board、桌面壳或只读 public board 都有同一入口语义

### 2.2 非目标

- 不让 workbench 成为新的 requirement source of truth
- 不在本 feature 内实现完整 cloud multi-tenant 平台
- 不在本 feature 内要求所有能力都必须是 GUI，CLI 仍保留
- 不把 Beacon 改造成通用 IDE 替代品

## 3. 设计原则

### 3.1 Runtime-Backed, Not UI-Invented

- workbench 只能消费 runtime kernel 的 read model 与 operator action contract
- UI 不得自行推导“真实当前状态”

### 3.2 Operate, Not Merely Report

- 页面必须支持 operator 执行动作，而不是只显示被动信息
- 至少要能帮助 operator 判断何时继续、停止、重试、回修、验收

### 3.3 Local-First Launcher

- 第一阶段优先本地启动体验
- `beacon board` 应成为正式入口，再决定是否增加 desktop 壳

### 3.4 Lifecycle Above Runtime Mode

- 主导航应先体现 requirement / execution / delivery 闭环
- `single / team / ralph / validation` 等只是运行模式和运行来源，不应喧宾夺主

### 3.5 Read-Only Public Surface And Writable Operator Surface Must Be Separated

- public board 可以是静态或只读
- operator workbench 必须是受控写操作面

### 3.6 Semantic Governance Before Visual Polish

- prototype、preview、board 首先服从软件语义合同，其次才讨论视觉样式
- 不允许把 `why / reasoning / review guidance / asset catalog wording` 直接投影为首屏 UI 文案

### 3.7 Recovery Judgment Before Artifact Noise

- 首屏必须先回答当前状态、当前阻塞、下一步动作、恢复路径
- run 列表、路径、历史噪声、机器材料引用只能下沉到二级展开或详情页

## 4. 范围

### In scope

- operator workbench 信息架构
- runtime board 视图与下钻视图
- launcher contract
- local web board / desktop shell 预留边界
- operator actions 与 recovery diagnostics surface

### Out of scope

- 完整视觉实现、动效细节、品牌设计系统重做
- 云端账号体系、组织级权限管理
- 与 runtime kernel 无关的 requirement 文档编辑器

## 5. 功能需求

### FR-001 Workbench Information Architecture

Workbench 至少包含以下正式页面或视图：

- `portfolio-board`
- `execution-board`
- `feature-detail`
- `run-detail`
- `review-surface`
- `recovery-diagnostics`

每个视图都必须有明确输入 contract，禁止“页面自己去猜文件目录结构”。

### FR-002 Execution Board

执行主看板至少能展示：

- queued runs
- active runs
- blocked runs
- retry scheduled runs
- needs review runs
- feature ordering / wave grouping
- baseline host health

并支持最小操作：

- open run detail
- continue
- stop
- retry
- open repair path

### FR-003 Run Detail And Review Surface

Run detail 至少能聚合：

- work item metadata
- run status timeline
- workspace root / writable services
- latest evidence refs
- retry history
- operator recommendations

Review surface 至少能聚合：

- diff entrypoint
- acceptance evidence entrypoint
- related feature / revision / baseline host
- QA and release readiness hints

### FR-004 Launcher Contract

Beacon 必须提供正式 board 启动 contract，至少覆盖：

- `beacon board`
- `beacon board --open`
- `beacon board --host ... --port ...`
- `beacon board --desktop` 的未来扩展位

launcher contract 至少返回：

- resolved runtime source
- board url / socket endpoint
- mode
- readiness status
- failure reason if startup blocked

### FR-005 Local-First Executable Surface

workbench 首选形态为本地可执行启动面：

- CLI 启动本地 web console
- 可选封装为桌面壳
- 保留 public board 的只读导出或静态入口

此能力必须与现有 `status --board` 语义兼容，但不能继续局限于文本摘要。

### FR-006 Recovery Diagnostics Surface

Workbench 必须暴露 recovery diagnostics，而不是只显示“失败了”：

- stale baseline host
- stale mirror
- workspace drift
- retry orphan
- blocked dependency
- missing evidence sink

每类诊断都要给出：

- reason code
- affected feature/run
- recommended command or path
- whether operator can self-repair

### FR-007 Software Semantic Profile

Workbench、prototype、preview 必须共享正式 `software-semantic-profile`，至少约束：

- 标题句式
- 状态文案句式
- 动作文案句式
- 字段约束句式
- 异常与恢复文案句式
- 禁用词与弱约束词
- 标准业务动词与状态枚举

该 profile 必须禁止主观词、口语词、泛化 SaaS 词、设计愿景词直接进入 operator-facing UI copy。

### FR-008 UI Copy Projection Contract

`page intent / state visibility / action hierarchy / recovery diagnostics` 到 UI copy 的投影必须经过正式 contract，至少区分：

- 可渲染到首屏的 operator 文案
- 只能保留在 PRD / ux-prd / review material 的解释文案
- 必须进入二级展开的路径、历史、机器材料引用

禁止以下内容直接作为首屏输出：

- design asset catalog wording
- review guidance
- why/reasoning 原文
- 路径清单与运行历史噪声

### FR-009 First-Screen Recovery And Next-Action Contract

execution board 首屏必须优先显示：

- 当前状态
- 当前阻塞
- 下一步动作
- 恢复路径

首屏默认禁止以下内容抢占主区：

- 全量 run 列表
- workspace path
- artifact path
- 历史时间线
- 机器 trace 明细

上述信息仅允许进入二级展开、run detail、review surface、recovery diagnostics detail。

### FR-010 Semantic Lint And Freeze Gate

prototype freeze、preview render、board export 前必须执行统一语义校验，至少覆盖：

- 禁用词校验
- 标准术语校验
- 状态枚举校验
- 正反约束成对校验
- 默认值显式校验
- operator-first first-screen 校验

未通过语义校验时，prototype 与 board 不得进入可交付状态。

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- workbench 不是 requirement 编辑器
- workbench 不是 runtime kernel 本身
- launcher 不是独立 truth source
- desktop shell 只是 packaging，不是新的 product layer

### 6.2 分层

本 feature 依赖并消费：

1. Runtime Kernel Layer
2. Operator Read Model Layer
3. UI / Launcher Layer

职责分离：

- kernel 产生权威状态
- read model 组织给 operator 的高信号视图
- workbench / launcher 负责可视化与控制动作转发

### 6.3 恢复策略

若以下前置条件不满足，launcher 必须 fail-closed：

- runtime source unavailable
- baseline host stale
- required read model missing
- version context unresolved

若 board 已启动但 run 状态漂移，workbench 必须优先展示诊断与 repair path，而不是继续允许误操作。

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 只做 UI 美化，没有执行帮助 | 高 | 强制定义 execution board、run detail、operator action、recovery diagnostics |
| workbench 自己维护一套状态 | 高 | 所有视图必须绑定 runtime read model 和 action contract |
| board 与 `status --board` 分叉成两套语义 | 中 | `status --board` 继续保留摘要角色，workbench 作为 richer operator surface，共享同一状态源 |
| desktop 壳过早进入实现，挤压 runtime 核心 | 中 | local web launcher 优先，desktop 只保留 contract 扩展位 |
| 页面过度围绕 agent 模式，丢失 lifecycle 主轴 | 中 | IA 先看 lifecycle / execution / delivery，再暴露 team/ralph 等模式信息 |

## 8. 验收标准

### AC-001 Workbench IA Frozen

- portfolio / execution / feature / run / review / recovery 六类视图均已定义并可追溯到 machine contract

### AC-002 Operator Actions Governed

- continue / stop / retry / repair 等动作均有正式 action contract，且不绕过 runtime kernel

### AC-003 Launcher Contract Available

- Beacon 存在正式 `board` 启动 contract，能表达 readiness、url、mode、failure reason

### AC-004 Local-First Surface Confirmed

- 默认交付路径明确是本地 web console first，desktop shell 为后续可插拔包装

### AC-005 Recovery Diagnostics Integrated

- board/workbench 能直接显示恢复原因与推荐路径，而不是要求 operator 手工翻找 artifacts

### AC-006 Truth Boundary Preserved

- workbench 不会反向成为 requirement truth 或 runtime truth 的新写入源

### AC-007 Semantic Profile Enforced

- `ux-prd / page-spec / pages / component catalog / preview / board` 共享同一语义合同，operator-facing 文案不再出现解释式或设计评审式漂移

### AC-008 First-Screen Operator Priority

- 首屏优先呈现 `当前状态 / 当前阻塞 / 下一步动作 / 恢复路径`，run 列表、路径、历史噪声不占据主区

### AC-009 Preview Anti-Drift Closed

- preview 被定义并渲染为 operator workbench prototype，而不是 design asset catalog；语义 lint 不通过时禁止 freeze/export

## 9. 成功指标

- 主指标：operator 能直接在 board 中完成长任务观察、判断和干预
- 主指标：`status --board` 与 richer workbench 共享统一状态语义
- 辅指标：真实项目长任务不再依赖人工记忆定位 workspace、retry、review 路径
- 辅指标：本地启动 board 成为正式可发现入口

## 10. 与主 PRD 的关系

- 本 feature 直接依赖 `beacon-execution-runtime-kernel`
- kernel 解决“状态和调度是否稳定”，workbench 解决“operator 是否真的能使用”
- 两者共同收敛 `vibe-kanban` 与 `symphony` 对 Beacon 的启发，但 Beacon 仍保持 requirement-first
- 后续任何桌面化、远端化、team 化扩展都应先建立在本 feature contract 之上

---

**Created**: 2026-05-01  
**Version**: v1.3.11  
**Status**: draft
