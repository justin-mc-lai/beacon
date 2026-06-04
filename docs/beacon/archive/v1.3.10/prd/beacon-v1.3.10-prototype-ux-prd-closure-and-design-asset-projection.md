# PRD: Beacon v1.3.10 prototype UX PRD closure and design-asset projection

**Feature**: `beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection`  
**Version**: `v1.3.10`  
**Date**: `2026-04-30`  
**Status**: `freeze_ready`  
**Track**: `parallel`  
**Scenario**: `prototype_requirement_closure`  
**Template**: `并行 PRD / prototype-governance`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.3.10/SUMMARY.md`
- Mainline PRD in current version: `docs/beacon/archive/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- Prior prototype design governance line:
  - `docs/beacon/v1.1.12/user-story/beacon-prototype-design-governance-loop.md`
  - `docs/beacon/v1.1.12/research/beacon-external-reference-study-statsclaw-awesome-design-md.md`
- Prior prototype professional UI line:
  - `docs/beacon/v1.1.3/prd/beacon-prototype-professional-ui-generation.md`
- Brainstorm evidence:
  - `docs/brainstorms/2026-04-30-ai-协作下，如何结合-beacon-生命周期，让-prototype-阶段提供-ui/ux-类-prd-能力；要求参考-ui-ux-pro-max-skill.md`
- External reference mirrors:
  - `/Users/apple/Developer/Personal/oss-sync/core-skills/ui-ux-pro-max-skill`
  - `/Users/apple/Developer/Personal/oss-sync/core-skills/impeccable`
  - `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md`

## 1. 问题

Beacon 已经把 `prototype` 固定在主生命周期：

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

并且全局约束已经明确：

- `prototype` 必须是 requirement-driven wireframe freeze
- 它不能退化成静态模板说明
- 它必须覆盖页面、状态、路由、组件契约与 AC/TC 映射

但当前 `prototype` 真实能力仍有四个结构性缺口：

### 1.1 它有结构闭环，但没有 UX PRD 闭环

当前 `prototype` 能生成：

- 页面清单
- 跳转关系
- 状态流转
- 组件契约

但它还不能确定性表达：

- 目标用户是谁
- 用户进入页面先要回答什么问题
- 页面支持哪一个核心判断
- 为什么这样组织信息层级
- 哪些交互和视觉约束必须保留到 implement

结果是：

- 产物更像“结构化说明文档”
- 而不是“可执行的 UI/UX 类 PRD”

### 1.2 它缺少设计上下文输入，导致默认退化成 generic wireframe

从 `impeccable` 的经验看，设计输出在没有明确：

- `target_audience`
- `use_cases`
- `brand_tone`
- `usage_context`

时，必然退化成通用壳子。

Beacon 当前也有同样问题：

- `prototype` 仍可能在 requirement truth 足够完整时，产出语义上正确但视觉/交互上过于泛化的 wireframe
- 用户看完之后仍然不能确定“这个产品具体该怎样被理解和操作”

### 1.3 它缺少设计推理层，无法把“为什么这样设计”冻结成 requirement truth

从 `ui-ux-pro-max-skill` 的经验看，高质量 UI/UX 不是只靠页面 inventory，而是要把：

- 产品表面类型
- 页面模式
- 信息密度策略
- 视觉方向
- 反模式约束
- pre-delivery checklist

一起固定下来。

Beacon 当前没有正式的 `design_reasoning` truth layer，因此：

- 即使页面结构正确
- implement 仍然可能在视觉、布局、交互层级上重新发明
- QA 也无法把“设计偏离”作为 requirement drift 检查

### 1.4 它缺少 agent-friendly 设计资产输出，无法成为 AI 协作的稳定设计输入

从 `awesome-design-md` 的经验看，设计治理最终需要投影成可复用资产：

- `DESIGN.md`
- `preview.html`
- `preview-dark.html`

Beacon 当前原型工件大多是：

- machine-facing contract
- human-facing summary

但还没有把 design governance 收口成 AI 与人类都能直接消费的统一资产面。

这会导致：

- implement agent 看不懂该遵循哪套设计规范
- 人类 review 也缺少一个简洁、可复制、可比对的设计基线

### 1.5 与当前主线的冲突风险

`v1.3.10` 主线已经在收口：

- 项目元信息
- repo / branch / topology 确定性治理
- requirement package dual-write gate

如果 `prototype` 继续停留在“结构 freeze but no UX closure”的状态，则会出现新的漂移：

1. requirement package 虽然双写一致，但 `prototype` 仍然不是高价值 requirement truth
2. `implement` 会重新猜 UI/UX 方向，造成“元信息确定、体验不确定”
3. `qa / release` 无法把设计偏离视作正式 requirement drift

因此这条并行 PRD 不是可选美化，而是 requirement package 完整性的补强线。

### 1.6 当前重构仍有三处 requirement 真空

虽然当前源码已经能输出 `ux-prd.md`、`DESIGN.md`、状态契约与状态流图，但从 requirement truth 角度仍有三处没有被正式冻结：

1. `component-catalog` 仍然更接近 page-global section inventory，缺少“组件负责哪一个状态反馈、哪一组 AC/TC”的精确责任边界。
2. `state-flow-map` 对跨页业务跳转仍偏启发式，尚未把 checkout / retry / fallback / handoff 等跨页业务状态迁移固定为正式 contract。
3. prototype 已经具备 AC/TC traceability，但还没有把“哪些页面/状态/边是 release blocker、哪些只需 smoke、哪些允许人工验证”编译成正式 automation priority truth。

如果这三层不进入 requirement truth，则 prototype 仍然只是“高级 wireframe freeze”，还不是对 implement / qa 真正有约束力的 UI/UX 类 PRD 编译器。

## 2. 目标

### 2.1 主要目标

把 Beacon `prototype` 从“页面/状态/路由/组件的结构化 freeze”升级为：

> **UI/UX 类 PRD 编译器**

它仍然不是高保真设计工具，也不是最终前端实现器；它的职责是把：

- `prd`
- `user-story`
- `test-case`

编译成一套正式的 **UX closure truth**，并在 freeze 前产出面向人和 agent 的设计资产。

本线要达成的最小正确能力：

1. `prototype` 在结构 freeze 之外，新增 UX/interaction closure truth
2. `prototype` 默认要求显式 design context，而不是隐式猜测
3. `prototype` 默认产出 `DESIGN.md + preview assets`
4. `prototype review / gate` 能正式检查 generic wireframe、设计推理缺失、状态反馈缺失、设计资产缺失
5. `implement / qa` 能消费同一套 UX PRD truth，而不是重新发明页面逻辑

### 2.2 非目标

- 不把 `prototype` 升级成 Figma 替代品
- 不把 `prototype` 升级成生产级前端生成器
- 不新增新的公开一级命令
- 不把 `prototype` 从 `wireframe freeze` 扩张成“最终视觉稿批准阶段”
- 不要求 Beacon 核心内置完整品牌设计系统编辑器
- 不让 `prototype` 直接承担 API、状态管理、性能优化、响应式实现代码

### 2.3 Truth 与 Projection 边界

`prototype` 仍必须服从全局边界：

- requirement truth 仍来自 `prd / user-story / test-case`
- `prototype` 只负责编译 UX/interaction closure
- 高保真视觉实现与前端代码仍属于 `implement`

因此本线新增的是：

- **UX PRD truth**
- **design reasoning truth**
- **design asset projection**

而不是把最终前端执行面前置到 `prototype`。

### 2.4 Explicit Design Context Freeze

以下 design context 作为本 feature 的显式冻结 truth，供 prototype compile / review / freeze 直接消费：

target_audience: Beacon 管理者 / 需求 owner / 实现协作者
primary_use_cases:
- 快速理解页面先服务哪一个判断
- 冻结页面下钻路径与状态反馈
- 为 implement / qa 提供统一的 UX truth
operator_mental_state: 需要在有限时间内完成判断与推进，而不是阅读泛化说明。
usage_environment: 桌面优先的管理工作台与需求协作评审环境。
brand_tone:
- quiet
- precise
- operational
- content-first
density_preference: workbench-medium
design_preset: apple-inspired-design-md

## 3. 设计原则

### 3.1 Prototype 仍是 requirement stage，不是 design handoff stage

`prototype` 的升级不能违反全局约束中“requirement-driven wireframe freeze”的定义。

它可以新增：

- design context
- UX contract
- design reasoning
- agent-readable design asset

但不能变成：

- 高保真视觉稿最终审批
- 生产前端代码主入口

### 3.2 设计上下文必须显式，不能继续默认猜测

没有以下信息时，`prototype` 不得被视为 UX freeze ready：

- target audience
- primary use cases
- operator mental state
- usage environment
- brand / tone direction

### 3.3 设计推理必须冻结，而不是只冻结页面结构

页面存在不代表 UX closure 完成。

Beacon 必须冻结：

- why this page exists
- what decision it supports
- what must be visible first
- what must not be surfaced
- what action hierarchy must remain stable

### 3.4 Agent 资产必须来自 canonical truth 单向投影

`DESIGN.md`、preview、theme、tokens 等都必须由 canonical envelope 单向投影生成，不能由人类手工写文档再反向驱动 machine truth。

### 3.5 实现复杂度留在机器内部

即便引入 design context、reasoning、preview 和 review gate：

- 人类主流程仍然只有 `prototype`
- 复杂的设计规则编译、推理、heuristics scoring、asset projection 必须内收

### 3.6 Default design baseline 必须固定而克制

Beacon 默认项目设计规范应固定为：

- Apple-inspired product baseline
- quiet neutral surfaces
- restrained accent
- content-first hierarchy
- management/workbench friendly density

但它只能作为默认 preset，不能阻断项目显式声明其他设计方向。

## 4. 范围

### In scope

- 重构 `prototype` requirement contract
- 为 `prototype` 增加 UX PRD truth layer
- 为 `prototype` 增加 design context / design reasoning 输入
- 增加 `DESIGN.md + preview.html + preview-dark.html` 资产投影
- 增加 UX/heuristic/design gate
- 让 `implement / qa` 正式消费 prototype UX closure truth
- 收口 Beacon 默认 Apple-inspired design baseline
- 将 component contract 升级为 state-aware requirement truth
- 将跨页业务跳转升级为正式 transition contract
- 将 prototype -> QA 自动化优先级收口成正式矩阵资产

### Out of scope

- 生产级多框架 UI 代码生成
- Figma 文件导入导出
- 完整视觉设计师工作流
- 丰富的 token 编辑器或品牌管理后台
- 任意网页风格一键克隆

## 5. 功能需求

### FR-001 Prototype canonical truth 必须新增 `design_context`

Beacon 必须在 prototype canonical envelope 中新增 `design_context`，至少包含：

- `target_audience`
- `primary_use_cases[]`
- `operator_mental_state`
- `usage_environment`
- `brand_tone[]`
- `density_preference`

规则：

- 缺少该字段时，prototype 只能停留在结构 freeze candidate
- 不得判定为 UX freeze ready

### FR-002 Prototype canonical truth 必须新增 `design_reasoning`

Beacon 必须新增 `design_reasoning`，至少包含：

- `product_surface_type`
- `interaction_model`
- `recommended_layout_pattern`
- `visual_priority_rules[]`
- `anti_patterns[]`
- `design_checklist[]`

这层用于吸收：

- `ui-ux-pro-max-skill` 的产品类型 -> 模式 -> 反模式推理
- Beacon 项目本地的 requirement-derived layout logic

### FR-003 Prototype canonical truth 必须新增 `ux_contract`

Beacon 必须把 UI/UX 类 PRD 冻结成正式 `ux_contract`，至少包含：

- `first_glance_question`
- `primary_decision`
- `action_hierarchy`
- `recognition_over_recall_rules[]`
- `error_recovery_policy[]`
- `allowed_machine_noise[]`
- `forbidden_machine_noise[]`

规则：

- 这不是最终视觉细节
- 这是体验闭环要求

### FR-004 每个页面必须新增 `page_intent_contract`

每个 page spec 除现有页面职责外，还必须至少包含：

- `why_this_page_exists`
- `decision_supported`
- `must_show_first[]`
- `must_not_show[]`
- `entry_conditions[]`
- `exit_actions[]`

页面没有 `decision_supported` 时，`prototype review` 必须 fail。

### FR-005 每个关键状态必须新增 `state_visibility_contract`

对 `loading / empty / error / blocked / stale / success` 等关键状态，Beacon 必须为每个状态明确：

- `user_question`
- `required_feedback[]`
- `recovery_actions[]`
- `forbidden_feedback[]`

规则：

- `test-case` 必须能消费这些状态 contract
- `qa` 必须能把它们变成正式验收检查对象

### FR-006 Prototype 必须产出 `ux-prd.md`

在原有 summary / manifest / map 之外，Beacon 必须新增：

- `ux-prd.md`

该文档面向人类，负责收口：

- design context
- design reasoning
- UX contract
- page intent contracts
- state visibility rules
- AC/TC traceability

它是人类可读的“UI/UX 类 PRD”。

### FR-007 Prototype 必须产出 `DESIGN.md`

Beacon 必须把设计治理结果投影成 agent-friendly 资产：

- `DESIGN.md`

其内容至少覆盖：

- visual theme & atmosphere
- color palette & roles
- typography rules
- component stylings
- layout principles
- do / don't
- responsive behavior
- agent prompt guide

该文件必须由 canonical truth 单向投影生成。

### FR-008 Prototype 必须产出 preview assets

Beacon 必须新增以下资产投影：

- `preview.html`
- `preview-dark.html`

用途：

- 让人类快速 review 设计规范是否可理解
- 让 agent 有稳定的视觉资产参考

注意：

- preview 不是产品页面实现
- preview 是 design asset catalog

### FR-009 Beacon 必须提供默认 design preset contract

Beacon 必须定义默认 `design_preset` 机制，至少支持：

- `apple-inspired-design-md`

默认 preset 至少约束：

- quiet neutral surfaces
- restrained primary accent
- SF Pro / system typography bias
- low-noise navigation
- content-first hierarchy
- no marketing-hero dashboard anti-pattern

项目显式 requirement 允许覆盖 preset，但覆盖必须被记录。

### FR-010 Prototype review 必须新增 UX/heuristic gate

`prototype review` 必须除结构校验外，新增 UX/heuristic 审查。

最小检查面至少包括：

- visibility of system status
- match between system and real world
- user control and freedom
- recognition rather than recall
- aesthetic and minimalist discipline
- error recovery clarity

规则：

- 可以采用评分与 finding 混合模式
- review 必须产出 machine-readable 结果

### FR-011 Prototype gate 必须正式阻断 generic wireframe

以下任一情况成立时，`prototype freeze` 或相关 gate 不得判定 pass：

- 缺少 `design_context`
- 缺少 `design_reasoning`
- 页面缺少 `primary_decision`
- 关键状态缺少 `required_feedback`
- 缺少 `DESIGN.md`
- 缺少 preview assets
- 命中 `generic wireframe` / `static explanation only` 检测

### FR-012 Implement 必须消费 prototype UX closure truth

`implement` 不得只消费：

- `page_specs`
- `navigation_map`

还必须能消费：

- `ux_contract`
- `page_intent_contract`
- `design_context`
- `DESIGN.md`

规则：

- implement 可以改变代码实现手段
- 不能改变已经冻结的 UX closure truth

### FR-013 QA 必须消费 prototype UX closure truth

`qa` 必须能够对以下项给出正式 verdict：

- 页面首要判断是否可完成
- 状态反馈是否满足 `state_visibility_contract`
- 设计资产与实现之间是否发生显著 drift
- machine noise 是否越界进入人类主界面

### FR-014 Prototype 子 skill 必须完成语义升级

Beacon 内部 prototype 相关子 skill / prompt / rule surface 必须从：

- “线框生成器”

升级为：

- “UX PRD closure compiler”

它的提示与规则必须默认吸收：

- `impeccable` 的显式上下文要求
- `ui-ux-pro-max-skill` 的设计推理与反模式约束
- `awesome-design-md` 的 DESIGN.md 资产投影形态

### FR-015 Multi-sink 一致性仍然必须受事务约束

新增 `ux-prd.md`、`DESIGN.md`、preview assets 之后，prototype 多写入点必须继续遵循：

- `prepare -> validate -> commit -> publish -> verify`

新增 sink 也必须纳入：

- `source_hash`
- `projection_seq`
- `transaction_id`
- `committed_at`
- `sink_checksums`

### FR-016 Component catalog 必须升级为 state-aware contract

Beacon 必须把现有 `component-catalog` 从 page-global section inventory 升级为可追踪的组件责任契约，至少表达：

- `component_id`
- `page_id`
- `state_refs[]`
- `state_feedback_responsibilities[]`
- `ac_refs[]`
- `tc_refs[]`
- `interaction_responsibilities[]`

规则：

- 组件契约不得只停留在“这个区块存在”，必须说明它在何种状态下承担何种反馈责任。
- `implement` 与 `qa` 必须能够追踪“某个状态反馈由哪个组件负责呈现”。

### FR-017 Cross-page business transition 必须冻结为正式 contract

Beacon 必须把跨页业务迁移从简单 ready-to-ready route map 升级为正式 `cross_page_transition_contract`，至少包含：

- `from_page`
- `from_state`
- `to_page`
- `to_state`
- `event`
- `guard`
- `fallback`
- `route_or_runtime_evidence`
- `ac_refs[]`
- `tc_refs[]`

规则：

- checkout / retry / fallback / handoff / return-path 等跨页业务流必须能被显式建模。
- 不允许只靠“目标页 ready 状态”隐式代替跨页业务语义。

### FR-018 Prototype 必须产出 automation priority matrix

Beacon 必须根据：

- page priority
- product surface type
- state visibility contract
- cross-page transition contract
- AC/TC traceability

编译正式 `automation-priority-matrix`，至少包含：

- `target_id`
- `target_type` (`page` / `state` / `transition` / `component`)
- `priority_class` (`release-blocker` / `primary-automation` / `smoke-only` / `manual-acceptable`)
- `reason`
- `ac_refs[]`
- `tc_refs[]`

规则：

- QA 不得再只看到 AC/TC 列表，而必须看到自动化优先级判断。
- 同一套 priority truth 必须被 `implement / qa / release` 共用。

## 6. 数据 / 状态 / 集成

### 6.1 Truth 来源

本线新增 truth 仍然必须完全从以下来源编译：

- `prd`
- `user-story`
- `test-case`
- 已批准的 design preset / local project profile

不得直接从：

- implement 代码现状
- 手工设计文档
- preview HTML 本身

反向推导 canonical truth。

### 6.2 Prototype canonical envelope 增量字段

本线要求 prototype canonical envelope 至少新增：

- `design_context`
- `design_reasoning`
- `ux_contract`
- `page_intent_contracts[]`
- `state_visibility_contracts[]`
- `component_state_contracts[]`
- `cross_page_transition_contracts[]`
- `automation_priority_matrix`
- `design_asset_contract`
- `review_heuristics`

### 6.3 资产投影

human-readable projections 至少新增：

- `ux-prd.md`
- `DESIGN.md`
- `automation-priority-matrix.md`

preview projections 至少新增：

- `preview.html`
- `preview-dark.html`

machine-readable projections 至少新增：

- `ux-contract.json`
- `design-asset-contract.json`
- `heuristic-review.json`
- `automation-priority-matrix.json`

### 6.4 与已有 prototype 工件的关系

现有工件继续保留：

- `wireframe-summary`
- `navigation-map`
- `state-flow-map`
- `component-catalog`
- `route-closure-contract`

但它们不再足以单独代表 UX closure complete。

### 6.5 Branch-flow

本子线至少显式冻结以下 branch-flow：

```text
requirement_truth_ready
-> design_context_explicit | design_context_missing
-> ux_truth_compiled | structure_only_candidate
-> review_pass | review_blocked
-> freeze_ready | refreeze_required
```

```text
canonical_truth_committed
-> design_assets_projected | asset_projection_missing
-> implement_consumes_same_truth | gate_blocked
```

```text
state_and_transition_truth_compiled
-> component_state_contract_complete | component_contract_blocked
-> automation_priority_ready | qa_priority_blocked
```

异常分支：

```text
prototype_bundle_present
-> generic_wireframe_detected
-> review_blocked
-> requirement_or_projection_fix
-> prototype_bundle_present
```

```text
current_state_takeover_mode
-> current_state_inventory_ready | ui_style_analysis_missing
-> design_md_frozen | takeover_prototype_blocked
```

### 6.6 State-machine

本子线的核心状态机至少包括：

- `structure_only_candidate`
  - 已生成页面、路由、状态、组件结构
  - 但尚未满足 UX freeze

- `ux_truth_compiled`
  - `design_context`
  - `design_reasoning`
  - `ux_contract`
  - `page_intent_contract`
  - `state_visibility_contract`
  已完成编译

- `design_assets_projected`
  - `ux-prd.md`
  - `DESIGN.md`
  - `preview.html`
  - `preview-dark.html`
  已由 canonical truth 单向投影生成

- `review_blocked`
  - 任一 UX truth 缺失
  - 命中 generic wireframe / static explanation only
  - 设计资产缺失

- `freeze_ready`
  - review / projection / traceability / transaction consistency 全部通过

- `implement_bound`
  - implement 与 qa 已绑定同一套 UX closure truth

### 6.7 Decision-priority

本子线的决策优先级必须保持：

1. requirement truth 显式设计上下文，高于运行时临场猜测
2. UX closure truth 完整性，高于仅有结构 freeze 的“差不多可用”
3. canonical single-source projection，高于手工补写 `DESIGN.md` 或 preview
4. review/gate fail-closed，高于“先实现再补 UX 说明”
5. implement / qa 绑定同一 UX truth，高于不同 runtime lane 的局部便利

### 6.8 State Axes

本子线至少显式建模以下 state axes：

- `prototype_semantic_axis`
  - `structure_only_candidate`
  - `ux_truth_compiled`
  - `freeze_ready`

- `design_context_axis`
  - `target_audience_explicit`
  - `use_case_explicit`
  - `operator_state_explicit`
  - `usage_environment_explicit`
  - `brand_tone_explicit`
  - `density_preference_explicit`

- `design_projection_axis`
  - `ux_prd_projected`
  - `design_md_projected`
  - `preview_assets_projected`
  - `transaction_consistent`

- `review_gate_axis`
  - `generic_wireframe_blocked`
  - `static_explanation_blocked`
  - `state_feedback_complete`
  - `page_decision_complete`

- `component_contract_axis`
  - `component_state_contract_complete`
  - `component_feedback_traceable`

- `transition_contract_axis`
  - `cross_page_transition_explicit`
  - `fallback_path_explicit`
  - `route_runtime_evidence_bound`

- `automation_priority_axis`
  - `release_blockers_identified`
  - `primary_automation_ready`
  - `manual_acceptable_explicit`

- `takeover_audit_axis`
  - `current_state_inventory_ready`
  - `route_state_map_ready`
  - `ui_style_analysis_ready`
  - `design_md_freezable`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 把 prototype 扩成高保真设计阶段 | 破坏全局边界 | 明确 `ux-prd freeze` 不是 final visual approval |
| 设计字段过多导致人类负担变高 | 生命周期变重 | 保持外部主命令不变，把上下文编译与 review 复杂度内收 |
| DESIGN.md 变成手工维护文档 | truth 漂移 | 只允许 canonical 单向投影生成 |
| implement 忽略 UX closure truth | 体验重发明 | gate / qa 正式消费 UX contracts |
| 默认 Apple preset 误伤其他项目 | 风格僵化 | 允许 requirement 显式 override，并记录 override reason |

## 8. 验收标准

### AC-001 Prototype 能输出正式 UX PRD truth

`prototype create` 成功后，必须产生：

- `ux-prd.md`
- `ux-contract.json`
- `design_context`
- `design_reasoning`

并且这些内容可追溯到 requirement truth。

### AC-002 Prototype 能输出正式 design assets

`prototype create` 成功后，必须产生：

- `DESIGN.md`
- `preview.html`
- `preview-dark.html`

且这些资产由 canonical projection 生成。

### AC-003 Generic wireframe 会被阻断

在缺少 design context、page decision、state feedback 或 design asset 的情况下：

- `prototype review` 或 `freeze` 必须 fail closed

### AC-004 Implement 与 QA 能消费同一套 UX closure truth

同一 feature line 中：

- implement 能读取并使用 `DESIGN.md` 与 `ux_contract`
- QA 能对 UX contract 与 state visibility rules 给出正式 verdict

### AC-005 默认 design preset 已固定

Beacon 默认项目设计规范必须固定支持：

- `apple-inspired-design-md`

并在 prototype / ui-spec 默认输出中可见。

### AC-006 Component-state 责任边界已冻结

prototype create / review 成功后，组件契约必须能够明确说明：

- 哪个组件负责哪些状态反馈
- 这些反馈绑定哪组 AC/TC
- implement / qa 可以按组件级责任追踪 UX closure

### AC-007 Cross-page business transition 已冻结

prototype create / review 成功后，至少关键跨页迁移必须显式表达：

- from/to page+state
- event / guard / fallback
- route 或 runtime evidence
- AC/TC traceability

### AC-008 Automation priority matrix 已冻结

prototype create / review 成功后，必须存在正式的 automation priority matrix，并使 QA 能区分：

- release blockers
- primary automation
- smoke-only
- manual-acceptable

## 9. 成功指标

- 至少 1 条真实 Beacon prototype line 能从 `prd -> user-story -> test-case -> prototype` 输出：
  - `ux-prd.md`
  - `DESIGN.md`
  - preview assets
  - heuristic review
- 至少 1 条真实 takeover / 二开项目 prototype line 能输出：
  - state-aware component contract
  - cross-page business transitions
  - automation priority matrix
- 至少 1 条真实 implement / qa line 能证明：
  - 实现没有重新发明页面主判断、关键状态反馈和设计基线

## 10. 与主 PRD 的关系

- 主线锚点：`beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`
- 主线解决的是：
  - project topology
  - repo binding
  - branch governance
  - requirement package dual-write
- 本并行线解决的是：
  - requirement package 中 prototype 面的 UX closure 缺口
  - design asset projection 缺口

两者关系是：

1. 主线保证 Beacon 在正确项目、正确 repo、正确 branch 上推进
2. 本线保证 Beacon 即使在正确执行面上，也不会产出“结构正确但体验无用”的 prototype truth

因此本并行线是对 `v1.3.10` requirement package 完整性的直接补强，而不是独立产品方向。

---

**Created**: 2026-04-30  
**Version**: v1.3.10  
**Status**: freeze_ready  
**Memory Context**: Derived from Beacon brainstorm + prior prototype governance lines + mirrored external design references
