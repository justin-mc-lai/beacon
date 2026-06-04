# PRD：prototype-design-intelligence-and-governed-rendering-separation

**Feature**: `prototype-design-intelligence-and-governed-rendering-separation`  
**Version**: `v1.3.11`  
**Date**: `2026-05-02`  
**Status**: `draft`  
**Track**: `parallel`  
**Scenario**: `prototype_governance`  
**Semantic Label**: `原型设计推导与受控渲染分层`  

target_audience: Beacon 产品 owner、原型编译维护者、implement renderer 维护者
primary_use_cases: 冻结 prototype 设计推导分层,阻断治理文案直出,为 implement 提供正式设计中间工件
operator_mental_state: 需要快速判断原型输出是否仍在 requirement truth 边界内，并阻断可见 UI 漂移
usage_environment: 桌面优先的需求评审、原型审阅、实现交付协作环境
brand_tone: formal, restrained, precise, operational
density_preference: workbench-medium

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.3.11/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.3.11/execution/index.md`
- Related PRDs:
  - `docs/beacon/archive/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md`
  - `docs/beacon/archive/v1.3.11/prd/beacon-execution-runtime-kernel.md`
  - `docs/beacon/archive/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- Related change:
  - `docs/beacon/archive/v1.3.11/change/beacon-operator-workbench-and-board-launcher.md`
  - `docs/beacon/archive/v1.3.11/change/prototype-design-intelligence-and-governed-rendering-separation.md`
- Brainstorm evidence:
  - `docs/brainstorms/2026-05-02-结合-ui-ux-pro-max-skill、impeccable、awesome-design-md-三个设计-skill-的思路，分析-beacon-pro.md`

## 1. 问题

### 1.1 当前断层

Beacon 当前 prototype 与 implement 已具备 requirement 驱动能力，但设计推导链仍未独立建模。当前链路把以下三类内容混为一层：

- requirement truth 推导出的页面目标与状态约束
- design skill 提供的设计判断、规范约束、审阅意见
- production-visible UI 需要显示的正式文案与界面结构

结果是：

- 原型页面出现解释性说明块、治理合同语句、设计评审语句
- implement 消费的是混合语义，无法稳定区分首屏 UI 与内部合同
- prototype review gate 无法判断“页面是否符合合同”还是“合同本身被直接渲染”

### 1.2 触发信号

- 真实项目 `shopxo_canada` 的 prototype/preview 已出现首屏解释漂移
- 现有 `prototype UI copy de-explanation / contract-to-ui projection split` 仅停留在 change 层
- `ui-ux-pro-max-skill`、`impeccable`、`awesome-design-md` 已提供设计能力参考，但 Beacon 尚未定义它们在原型链中的正式层级

### 1.3 为什么现在做

若本版本继续只在 preview 或页面文案层做修补，后续问题会重复出现：

- 不同 feature 继续把治理文案渲染到 UI
- prototype 无法稳定为 implement 提供可消费的设计中间件
- prototype 与 implement 无法共用同一套正式语义合同

## 2. 目标

### 2.1 主要目标

- 正式建立 `prototype design intelligence` 与 `governed rendering` 的模型分层
- 规定 design skill 在 Beacon 中只作为推导输入、审阅输入、样式输入，不作为终态 UI 文案来源
- 让 prototype 产出结构化设计中间工件
- 让 implement 只消费受控中间工件与 production-visible copy
- 让 review gate 可以稳定拦截“治理合同直接上屏”的漂移

### 2.2 非目标

- 不把 `prototype` 升级为高保真视觉设计工具
- 不把 Beacon 变成通用设计系统平台
- 不要求本 feature 重写全部现有 prototype 页面
- 不让 design skill 直接替代 requirement truth

## 3. 设计原则

### 3.1 Requirement Truth First

- `prd / user-story / test-case / prototype freeze` 是唯一设计输入真相
- design intelligence 只能在 requirement truth 之上做推导，不得反向改写 requirement

### 3.2 Design Guidance Is Internal Input

- design skill 输出属于内部设计推导材料
- 内部材料允许用于推导布局、密度、组件优先级、语义文案规则
- 内部材料禁止未经投影直接进入 production-visible UI

### 3.3 Governed Rendering Is Mandatory

- prototype preview 与 implement render 必须经过统一投影合同
- 未经过投影合同的设计解释文案、审阅文案、资产目录文案禁止渲染

### 3.4 Formal Semantic Profile Is Shared

- prototype、preview、board、implement 必须共享正式软件语义合同
- 文案必须满足正式、克制、严谨、专业、简洁、准确

### 3.5 Review Gate Must Be Fail-Closed

- 若页面存在合同泄漏、解释上屏、禁用词、弱约束词、状态枚举漂移，prototype gate 必须阻断

## 4. 范围

### In scope

- prototype 设计推导分层
- design skill 到 prototype compiler 的输入合同
- prototype compiler 的设计中间工件
- implement renderer 的消费合同
- production-visible copy 与 internal governance copy 的边界
- prototype review gate 的新增阻断项

### Out of scope

- 品牌视觉重构
- 全量页面视觉改版
- 独立设计资产管理后台
- 与本 feature 无关的 runtime scheduler 设计

## 5. 功能需求

### FR-001 Design Intelligence Layer

Beacon 必须建立正式 `design-intelligence-layer`，输入至少包含：

- `prd`
- `user-story`
- `test-case`
- `prototype freeze context`
- `software-semantic-profile`
- 可选 design skill references

输出至少包含：

- `surface-profile`
- `layout-pattern`
- `component-priority-map`
- `state-visibility-contract`
- `ui-copy-policy`
- `style-preset`

### FR-002 Design Skill Role Contract

Beacon 必须明确三类设计能力的角色边界：

- `ui-ux-pro-max-skill`：用于页面目标、布局模式、信息密度、组件组织的推导
- `impeccable`：用于反模式识别、界面审阅、视觉与交互约束校验
- `awesome-design-md`：用于设计语法、样式预设、组件语义基线参考

上述能力仅允许生成内部设计工件，不允许直接写入终态页面文案。

### FR-003 Prototype Design Artifact Contract

prototype compiler 必须产出结构化中间工件，至少包括：

- `design-context.json`
- `surface-profile.json`
- `layout-pattern.json`
- `component-state-matrix.json`
- `ui-copy-policy.json`
- `style-preset.json`
- `design-review.json`

每个工件必须记录：

- `source feature`
- `source requirement refs`
- `generated_at`
- `source_hash`
- `projection_role`

### FR-004 Governed Rendering Contract

Beacon 必须建立正式 `governed-rendering-contract`。该合同至少区分三类输出：

- `internal-governance-copy`
- `review-visible-copy`
- `production-visible-copy`

渲染规则如下：

- `internal-governance-copy` 仅允许出现在 ux-prd、review material、gate evidence
- `review-visible-copy` 仅允许出现在 prototype 审阅面
- `production-visible-copy` 才允许进入 `pages/*.md`、`page-specs/*.json`、`preview.html`、implement render 输出

此外必须补充正式 `artifact-topology-contract`：

- `authoring artifacts`：仅服务 prototype compiler / requirement projection，默认不进入 review surface 与 implement surface
- `review artifacts`：仅服务人工审阅与 gate evidence，默认不进入 implement surface
- `projection artifacts`：服务 preview/page-spec/page copy 投影，是 production-visible surface 的唯一上游
- `implementation artifacts`：服务 implement renderer，是实现层默认且唯一允许读取的入口

除 `projection artifacts` 与 `implementation artifacts` 外，其他 artifact 不得默认进入最终渲染与实现消费链。

### FR-005 Production UI Copy Projection

`page intent / state visibility / action hierarchy / recovery diagnostics` 到正式 UI 文案的投影必须经过 `production-ui-copy-profile`。

该 profile 必须满足：

- 一句话只表达一个功能含义
- 标题只描述页面对象与页面动作
- 状态文案只描述状态枚举与当前结果
- 动作文案只描述执行动作
- 禁止输出审阅解释、设计原因、资产目录说明、路径清单、历史噪声

### FR-006 First-Screen Projection Rule

首屏只允许显示页面目标、核心对象、当前主动作、必要状态反馈。

以下内容禁止默认占据首屏：

- `当前状态 / 下一步动作 / 恢复路径` 的解释性说明块
- `why / reasoning / design guidance` 原文
- `design asset catalog` 说明
- 路径列表
- 历史 run 噪声

异常规则：

- 当页面状态为 `blocked`、`failed`、`empty-risk` 时，允许显示恢复信息
- 恢复信息必须由 reason code、受影响对象、允许动作组成

### FR-007 Prototype Review Gate

prototype review gate 必须新增以下阻断检查：

- `design_context_explicit_block`
- `governance_copy_leak`
- `review_copy_rendered_as_production_ui`
- `semantic_profile_violation`
- `first_screen_over_explanation`

任一阻断命中时，prototype 不得判定为可交付。

### FR-008 Implement Consumption Contract

implement renderer 只允许消费以下工件：

- `surface-profile`
- `layout-pattern`
- `component-priority-map`
- `production-ui-copy-profile`
- `style-preset`
- `design-lint-rules`

implement renderer 禁止直接消费以下输入：

- design brainstorm 原文
- review comments 原文
- ux-prd 解释段落
- prototype gate 诊断原文

实现层必须默认只从以下入口读取：

- `machine-view/index.json`
- `design-artifacts/`
- `implementation-map.json`
- `production-ui-copy-profile.json`
- `design-lint-rules.json`

`ux-prd.md`、`DESIGN.md`、`prototype-review.md`、`pages/*.md` 仅作为 review-only human-readable materials 保留，不得再被视为实现层默认输入面。

### FR-009 Traceability

design intelligence 输出、prototype 输出、implement 输出必须都能追溯到：

- requirement source ref
- design artifact ref
- projection contract ref
- review gate verdict

若任一链路缺失，系统必须阻断 freeze 或判定为人工补录。

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- requirement truth 定义做什么
- design intelligence 定义如何组织界面
- design governance 定义什么不能直接渲染
- governed rendering 定义最终允许渲染什么
- implement 负责代码输出，不负责重建设计推导真相

### 6.2 分层

固定为五层：

1. Requirement Truth Layer
2. Design Intelligence Layer
3. Design Governance Layer
4. Governed Rendering Layer
5. Delivery Render Layer

### 6.2A Artifact Topology

prototype bundle 必须再固定为四层 artifact topology：

1. `authoring artifacts`
2. `review artifacts`
3. `projection artifacts`
4. `implementation artifacts`

拓扑规则：

- 上游只能单向向下游投影
- human-readable explanation materials 只允许停留在 `review artifacts`
- implement 不得跨层回读 `authoring artifacts` 与 `review artifacts`
- 任一 surface 若需要跨层读取，必须通过显式 projection contract，而不是直接读同级 markdown

### 6.3 恢复策略

- 当 `design artifact missing` 时，回退到 prototype compile
- 当 `production copy leakage` 时，阻断 preview / implement，并输出修复 reason code
- 当 `semantic profile violation` 时，阻断 prototype freeze
- 当 `style preset missing` 时，允许降级为默认样式，但必须保留降级记录

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 设计 skill 输出继续被直接渲染 | 高 | 强制 `governed-rendering-contract` 与 gate 拦截 |
| prototype 中间工件过少，implement 继续读 markdown 段落 | 高 | 固定结构化 artifact 列表并作为唯一消费面 |
| human-readable materials 与 implementation artifacts 并排暴露 | 高 | 固定四层 artifact topology，并把 explanation materials 降级为 review-only surface |
| 正式语义合同未共用，页面文案继续漂移 | 高 | 固定 `software-semantic-profile` 为跨 surface 共享合同 |
| 设计约束过强导致页面失去业务可读性 | 中 | 限定只约束语义和投影边界，不规定具体视觉风格 |

## 8. 验收标准

### AC-001 Design Layer Separation

prototype 输出中存在正式设计中间工件，且工件与页面输出分离存放。

同时必须能区分 `authoring / review / projection / implementation` 四层 artifact topology。

### AC-002 No Governance Copy Leakage

`preview.html`、`pages/*.md`、`page-specs/*.json`、implement 生成页面默认不再出现治理合同解释块、设计原因段落、资产目录说明。

### AC-003 Shared Semantic Profile

prototype、preview、board、implement 使用同一 `software-semantic-profile`，且术语、状态枚举、动词口径一致。

### AC-004 Review Gate Enforcement

当页面存在解释上屏、禁用词、弱约束词、状态漂移时，prototype review gate 返回阻断结果与 reason code。

### AC-005 Implement Consumption Closure

implement renderer 能在不读取设计解释原文的前提下，仅依赖结构化设计工件完成页面渲染。

实现层默认读取入口必须收敛到 `machine-view / design-artifacts / implementation-map / projection contracts`，不得把 `ux-prd.md`、`DESIGN.md`、`prototype-review.md` 视为同级默认输入。

## 9. 成功指标

- 主指标：prototype 首屏解释性说明块命中率降为零
- 主指标：production-visible UI copy 的语义违规项在 gate 中可稳定检测
- 辅指标：真实项目二开原型重建时，prototype 与 implement 的设计漂移次数下降

## 10. 与主 PRD 的关系

- 本线是 `beacon-operator-workbench-and-board-launcher` 的模型层补强
- 本线为 `prototype` 与 `implement` 提供共享设计分层，不新增公开生命周期阶段
- 本线与 `beacon-execution-runtime-kernel` 解耦；kernel 提供运行态，design intelligence 提供界面推导

---

**Created**: 2026-05-02  
**Version**: v1.3.11  
**Status**: reopened-draft-r2
