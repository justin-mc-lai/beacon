# PRD: Beacon v1.4.4 pragmatic design baseline and template governance

**Feature**: `beacon-v1.4.4-pragmatic-design-baseline-and-template-governance`  
**Version**: `v1.4.4`  
**Date**: `2026-05-11`  
**Status**: `freeze-ready`  
**Track**: `design-decision + prototype-governance + default-template-baseline`  
**Scenario**: `restrained-design-upgrade-without-skill-sprawl`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Prior version summary: `docs/beacon/v1.4.3/SUMMARY.md`
- Prior design boundary PRD: `docs/beacon/v1.4.3/prd/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
- Prior prototype asset projection PRD: `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- Current public surfaces:
  - `skills/beacon/beacon-design-review/SKILL.md`
  - `skills/beacon/beacon-prototype/SKILL.md`
- External reference inputs:
  - `VoltAgent/awesome-design-md` `apple`
  - `VoltAgent/awesome-design-md` `vercel`
- Design direction constraint:
  - Beacon must improve default UI/UX taste and interaction quality without expanding into a broad design skill family.

## 1. 问题

### 1.1 `v1.4.3` 解决了边界，但还没有解决默认可用性

`v1.4.3` 已经把 `design-review` 和 `prototype` 分层清楚：

- `design-review` 负责 challenge UI/UX direction
- `prototype` 负责 conditional freeze / handoff
- `prototype` 不再承担 final visual approval

但对于真实项目与 Beacon 自身而言，仍然存在一个默认能力缺口：

- 设计判断面已经存在
- 设计资产投影能力已经存在
- 但默认 taste baseline 仍然偏弱
- anti-AI UI/UX 规则仍然没有被收口为稳定 contract
- 没有一个小而固定的模板目录让人类与实现 agent 直接复用

结果是：

- 用户仍然容易得到“语义正确但审美泛化”的产物
- Beacon 容易继续依赖临场 prompt 或 host taste，而不是自己的默认产品约束
- 如果进一步补能力，最容易滑向新增大量 design 子 skill

### 1.2 需要的是“默认基线”，不是“设计 skill 宇宙”

外部参考给了两个互补信号：

- `awesome-design-md` 证明：AI 协作中的设计能力，应该投影成可复用的 `DESIGN.md` 资产与稳定设计基线
- `impeccable` 类路线证明：高质量 UI/UX 需要显式的 anti-pattern、interaction、层级与状态约束

但 Beacon 的目标不是复制这些仓库的产品形态，而是吸收它们的最小有效能力：

- 一套可解释的默认设计基线
- 一套基础 anti-AI UI/UX 检查规则
- 一组极少数、可直接用的模板
- 继续挂载到现有 `design-review / prototype / implement / qa` 闭环

### 1.3 当前缺口会直接影响 implement / qa

如果默认设计基线不存在，会产生三类 drift：

1. `implement` 重新发明视觉与交互层级
2. `qa` 无法把“AI slop”与低质量交互作为正式 drift 检查对象
3. `prototype` 产出的 `DESIGN.md` 仍然太像项目内一次性说明，而不是稳定复用的设计资产包

这说明 Beacon 需要一个新 planning line 来冻结：

- 默认设计基线
- anti-AI UI/UX contract
- 三模板目录
- Apple/Vercel 参考归一化策略

## 2. 目标

### 2.1 主要目标

把 Beacon 的默认设计能力收敛为一个务实、克制、可落地的产品面：

1. 不新增一组设计一级命令或 design 子 skill 家族
2. 在 `design-review` 中内置基础 anti-AI UI/UX 审查 contract
3. 在 `prototype` 中内置固定模板目录与设计资产投影 contract
4. 在 `implement / qa` 中正式消费同一套模板与 anti-drift truth
5. 冻结 3 个模板，且它们显式来源于 `apple` / `vercel` 归一化基线

### 2.2 非目标

- 不新增公开一级主命令
- 不新增 `/polish / distill / bolder / quieter / delight ...` 风格子命令族
- 不把 Beacon 做成开放式设计模板市场
- 不把 `prototype` 升级为 final visual approval
- 不要求运行时依赖 `VoltAgent/awesome-design-md`
- 不支持任意品牌/网站的一键风格克隆

## 3. 设计原则

### 3.1 设计质量能力必须融合进现有人类面

默认设计质量能力应吸收到：

- `design-review`
- `prototype`
- `implement`
- `qa`

而不是变成新的独立主面。

### 3.2 模板数量必须小而固定

模板目录必须固定为 3 个，避免：

- 选择焦虑
- 模板市场化
- 审美分叉
- QA 与实现对齐成本飙升

### 3.3 外部参考只能被归一化，不能直接变成依赖

`apple` / `vercel` 的设计资产只能作为：

- 研究输入
- 归一化来源
- 默认基线借鉴

它们不能成为 Beacon 运行时的必需仓库或外部可用性前提。

### 3.4 Anti-AI UI/UX 必须进入正式 contract

默认 contract 至少应阻断：

- gradient text
- 紫蓝 AI 渐变主色策略
- card 套 card
- 侧边强调条
- bounce / elastic easing
- 只有 hover 没有 focus-visible
- 缺失 empty / loading / error / success 状态
- 主次按钮层级混乱
- 小于 44x44 的主要触达目标

### 3.5 模板只固定骨架，不替代 requirement truth

模板的职责是：

- 固定审美边界
- 固定布局倾向
- 固定交互纪律
- 固定 `DESIGN.md` 投影模式

而不是替代 `prd / user-story / test-case`。

## 4. 范围

### In scope

- `design-review` 默认 rubric 扩展
- anti-AI UI/UX baseline contract
- 3-template catalog freeze
- Apple/Vercel reference normalization
- `prototype` design preset projection
- `implement` / `qa` design drift consumption contract
- 模板 override reason 记录

### Out of scope

- 开放式 style marketplace
- 完整品牌设计系统编辑器
- 视觉灵感仓库型产品
- 每种风格一个独立 Beacon skill
- 高保真视觉稿审批流

## 5. 功能需求

### FR-001 Beacon 必须冻结一个默认 anti-AI UI/UX baseline contract

Beacon 必须定义 machine-readable 的默认审美与交互质量 contract，至少包含：

- `forbidden_visual_patterns[]`
- `interaction_quality_rules[]`
- `required_state_coverage[]`
- `minimum_touch_target`
- `focus_visibility_policy`
- `layout_noise_threshold`
- `button_hierarchy_rules[]`

### FR-002 `design-review` 必须默认消费 anti-AI UI/UX rubric

`beacon-design-review` 除当前：

- hierarchy
- state clarity
- interaction coherence
- UX evidence sufficiency

之外，必须新增：

- anti-AI slop detection
- baseline visual discipline review
- template fit judgment

### FR-003 Beacon 必须冻结 3 个固定模板

模板目录必须固定为：

1. `restrained-product`
2. `operator-console`
3. `editorial-calm`

不允许在默认产品面继续无限扩展模板数。

### FR-004 模板来源必须显式绑定 Apple/Vercel 归一化基线

Beacon 必须记录每个模板的 baseline source：

- `restrained-product` -> `apple`
- `operator-console` -> `vercel`
- `editorial-calm` -> `apple+vercel hybrid`

这里的 `apple` / `vercel` 指向 Beacon 归一化后的内部 preset truth，而不是运行时直接读外部仓库。

### FR-005 `prototype` 必须投影模板与设计基线

当 `prototype` 被触发时，默认 design asset projection 至少需要包含：

- `design_preset`
- `preset_source`
- `preset_override_reason`（如果有）
- `anti_ai_ui_contract`
- `DESIGN.md`
- `preview.html`
- `preview-dark.html`

### FR-006 `implement` 必须消费模板与 anti-AI truth

`implement` 在读取 prototype / design asset truth 时，必须显式消费：

- `design_preset`
- `anti_ai_ui_contract`
- `template_layout_rules`
- `interaction_discipline_rules`

实现可以更换具体代码手段，但不能静默违反这些冻结约束。

### FR-007 `qa` 必须验证设计 drift 与 anti-AI 基线

`qa` 必须能够对以下项给出正式 verdict：

- 是否命中默认 forbidden visual patterns
- 是否覆盖关键交互状态
- 是否违反 touch target / focus-visible / empty-loading-error-success 基线
- 是否偏离选定模板的主要布局与层级规律

### FR-008 模板 override 必须有显式记录

如果 feature 不适合默认模板，Beacon 必须允许显式 override，但必须记录：

- `override_requested`
- `override_reason`
- `design_review_verdict`
- `prototype_projection_delta`

### FR-009 `editorial-calm` 必须是混合模板，而不是第三个独立来源模板

第三模板不得引入第三个外部参考系。它必须是 Beacon 对 `apple` 与 `vercel` 的归一化混合：

- Apple 的 calm, content-first, restrained surfaces
- Vercel 的 precise hierarchy, technical density, operational clarity

### FR-010 外部参考必须保持非依赖边界

Beacon 必须明确：

- `VoltAgent/awesome-design-md` 只是参考来源
- 缺少该仓库时，Beacon 运行不能失效
- 所有运行时判断都基于 Beacon 自己冻结后的 canonical preset truth

## 6. 数据 / 状态 / 集成

### 6.1 新增 canonical fields

本线至少新增：

- `design_preset`
- `preset_source`
- `preset_family`
- `template_layout_rules[]`
- `interaction_discipline_rules[]`
- `anti_ai_ui_contract`
- `template_override_record`

### 6.2 设计模板目录

```text
default_template_catalog
-> restrained-product (apple)
-> operator-console (vercel)
-> editorial-calm (apple+vercel hybrid)
```

### 6.3 分层关系

```text
frozen requirement truth
-> design-review rubric
-> template preset binding
-> prototype design asset projection
-> implement consumes same design truth
-> qa verifies anti-drift
```

### 6.4 Decision-priority

1. requirement truth 高于模板便利
2. Beacon canonical preset truth 高于外部仓库原文
3. anti-AI UI/UX baseline 高于临场审美偏好
4. fixed template catalog 高于开放式风格扩张
5. existing human surface reuse 高于新增 skill surface

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| 模板数继续增长 | 设计面失控 | 固定 3 模板，不新增开放 catalog |
| 外部参考变运行时依赖 | 破坏边界 | 只允许归一化写入 Beacon canonical truth |
| anti-AI 规则过度审美化 | 实用性下降 | 只冻结基础质量线，不冻结风格偏好大全 |
| `prototype` 再次过载 | 边界混乱 | 明确模板与 DESIGN.md 仍是 freeze projection，不是 final UI authority |
| 想通过新增 skill 解决所有设计问题 | skill sprawl | 约束新能力必须先挂载现有 `design-review / prototype / qa` |

## 8. 验收标准

| AC ID | Description |
| --- | --- |
| AC-001 | Beacon freezes a default anti-AI UI/UX baseline contract. |
| AC-002 | `design-review` consumes hierarchy/state/interaction plus anti-AI baseline checks. |
| AC-003 | Beacon freezes exactly 3 templates and no open-ended default catalog. |
| AC-004 | the 3 templates explicitly bind to normalized `apple` / `vercel` sources. |
| AC-005 | `prototype` projects the selected template and anti-AI contract into design assets. |
| AC-006 | `implement` consumes the same preset truth instead of re-inventing the visual/interaction baseline. |
| AC-007 | `qa` can verify design drift and anti-AI baseline violations. |
| AC-008 | external references remain research inputs rather than runtime dependencies. |
