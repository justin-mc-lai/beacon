# PRD: Beacon 原型基线、实现绑定与防漂移 Debug 闭环（v1.1.8）

## 1. 背景

当前 `beacon prototype` 已经从早期的静态 HTML 生成器升级为带 contract 的原型子命令，能输出：

- `index.html`
- `manifest.json`
- `source-map.json`
- `prototype-brief.json`
- `theme.json`
- `navigation-map.json`
- `interaction-map.json`
- `prototype-review.json / .md`
- `freeze.json`

现有 `review` / `freeze` 主要保障的是：

- 原型能从 `PRD + User Story` 正确解析；
- 原型工件齐全；
- CTA / jump / 基础可访问性存在；
- 来源文档变化时，prototype 会变 stale。

但它**还不能回答最关键的问题**：

> 真实实现代码，是否真的按这个 prototype 落地？

### 1.1 当前不够的地方

1. `source-map.json` 只回指 `user-story / prd`，不回指真实实现；
2. `theme.json` 只有 prototype token，没有映射到真实 CSS 变量 / design token / class system；
3. `freeze.json` 冻结的是 prototype artifact，而不是 implementation binding；
4. `prototype review` 不会对真实页面做视觉、语义、交互、状态、动效差异检查；
5. 没有类似 gstack 的 debug 修复闭环，开发期出现 prototype drift 时只能人工对照。

### 1.2 Milemon 作为真实案例

以 `products/milemon` 为例：

#### Prototype 侧
- `docs/beacon/v0.1.0/prototype/site-visual-system/theme.json`
- `docs/beacon/v0.1.0/prototype/site-visual-system/source-map.json`

其中已经声明：
- primary: `#F26522`
- secondary: `#1E4D8C`
- mood: `premium`
- sections: `Brand System / Home / Shop / Contact / About / Product Detail / Cart & Checkout`

#### 实现侧
- `wp-content/themes/milemon/assets/css/design-tokens.css`
- `wp-content/themes/milemon/style.css`
- `wp-content/themes/milemon/front-page.php`
- `wp-content/themes/milemon/header.php`
- `wp-content/themes/milemon/woocommerce/archive-product.php`
- `wp-content/themes/milemon/woocommerce/single-product.php`

真实实现实际上已经有：
- `--color-primary: #F26522`
- `--color-secondary: #1E4D8C`
- 首页 hero / CTA / 顶栏 / catalog / quote flow 等完整页面结构

但 Beacon 当前**不知道**：
- `site-visual-system` 对应哪些真实模板；
- `theme.json.primary` 对应哪些 CSS var；
- `Home` / `Shop` / `Product Detail` 各自应该对比哪些页面截图与 DOM contract；
- 一旦偏离 baseline，该怎么自动给出 reason code 和修复路径。

### 1.3 基于 frontend-design + web-design-guidelines 的现状审计

结合 `frontend-design` 对“避免 generic AI aesthetics”的要求，以及 `web-design-guidelines` 的界面规范，对当前 `beacon/utils/prototype_utils.py` 的现状审计结论如下：

1. `beacon/utils/prototype_utils.py:253-257`
   - 当前 typography 默认写死为 `Inter Display / Inter / JetBrains Mono`
   - 审计结论：字体人格过于保守，缺少清晰设计方向，容易把 baseline 冻结成“能用但不好看”的原型

2. `beacon/utils/prototype_utils.py:341-395`
   - archetype renderer 仍主要由重复的 Bootstrap card / list / table shell 组成
   - 审计结论：页面结构可用，但差异化构图不足，prototype 很容易退化为 generic dashboard/demo page

3. `beacon/utils/prototype_utils.py:338-339`
   - CTA fallback 仍使用 `Continue / Learn More`
   - 审计结论：文案语义不具体，难以形成真实产品语境

4. `beacon/utils/prototype_utils.py:374`
   - 示例输入缺少 `name / autocomplete / type`
   - 审计结论：表单语义和浏览器体验基线仍偏弱

5. `beacon/utils/prototype_utils.py:443-493`
   - 页面壳已具备 landmarks 与 focus-visible，但仍缺少：
     - skip link
     - decorative icon `aria-hidden`
     - 更正式的 tab semantics
     - heading anchor 的 `scroll-margin-top`
   - 审计结论：当前可访问性不是空白，但尚未形成“默认合格”的 Web UI baseline

因此，v1.1.8 的重点不只是“把 prototype 绑定到实现”，还要**先把 prototype 自身的设计基线补齐**，避免把一个审美和可访问性都偏弱的 reference 继续冻结为 baseline。

## 2. 第一性原理结论

### 2.1 Prototype 的真正职责

Prototype 不应只是“帮助需求可视化”，还应成为：

- 实现前的**视觉/交互/主题基线**；
- 实现中的**差异校验参照物**；
- 验收前的**防漂移门禁**；
- 返工时的**reopen / rewrite 重新闭环入口**。

### 2.2 如果没有 baseline，会发生什么

- freeze 只能证明“文档到 prototype 一致”；
- 无法证明“prototype 到 implementation 一致”；
- 最终交付会回到人工凭感觉对照；
- AI/多人协作时，样式色、状态、CTA、页面结构最容易发生静默漂移。

### 2.3 要补的不是“更漂亮的原型”，而是“可执行的基线治理”

因此 v1.1.8 要补的是：

- Prototype Baseline
- Implementation Binding
- Verify-Implementation
- Prototype Debug Loop

而不是再做一层 generic 的原型美化。

## 3. 目标

1. **让 prototype baseline 成为实现阶段可消费的正式基线**
2. **让关键页面、状态、断点、主题 token 与真实实现建立绑定**
3. **让 Beacon 能自动判断原型与实现是否漂移**
4. **让开发期出现漂移时进入 debug 修复闭环**
5. **用 Milemon 证明真实项目可落地，但设计保持通用**
6. **让 prototype generator 先具备最小审美基线与 Web 界面规范基线**

## 4. 非目标

1. 不把 Beacon 变成 Figma 或可视化画布编辑器；
2. 不强制生成生产级前端代码；
3. 不把比对能力写死到 WordPress / WooCommerce；
4. 不要求所有项目都做像素级视觉 diff；
5. 不以“AI 猜实现应该长什么样”取代正式 binding manifest。

## 5. 设计原则

### 5.1 Baseline First
先冻结 prototype baseline，再允许实现绑定与 verify。

### 5.2 Binding Before Acceptance
如果需求声明了 prototype baseline，则 accept 前必须存在 implementation binding。

### 5.3 Multi-layer Drift
漂移不只有视觉漂移，还包括：
- route/surface 漂移
- DOM/semantic 漂移
- interaction/state 漂移
- token/theme 漂移
- motion/effect 漂移

### 5.4 Evidence-driven Debug
出现 drift 后，不是给一句“看起来不一致”，而是要：
- 明确 surface
- 明确 diff layer
- 明确 reason code
- 给出可执行修复路径
- rerun verify

## 6. 核心模型

## 6.1 Prototype Baseline Manifest

新增建议工件：

- `docs/beacon/<version>/prototype/<feature>/baseline.json`

至少包含：

- `feature`
- `version`
- `baseline_id`
- `baseline_hash`
- `source_refs`
- `prototype_refs`
- `surfaces[]`
- `breakpoints[]`
- `states[]`
- `theme_tokens`
- `motion_tokens`
- `required_interactions[]`
- `required_effects[]`
- `screenshot_refs[]`
- `lifecycle_status`

### 说明

`surfaces[]` 是 baseline 的核心单位，表示必须被真实实现覆盖的页面或关键界面，例如：

- home
- catalog
- product-detail
- contact-quote
- cart
- checkout
- account

每个 surface 至少需要：

- `surface_id`
- `label`
- `route_or_entry`
- `breakpoints`
- `required_states`
- `required_components`
- `required_cta`
- `required_tokens`
- `required_effects`

## 6.2 Implementation Binding Manifest

新增建议工件：

- `docs/beacon/<version>/prototype/<feature>/implementation-map.json`

至少包含：

- `feature`
- `version`
- `baseline_id`
- `adapter`
- `binding_status`
- `surfaces[]`

每个 `surface` 绑定至少记录：

- `surface_id`
- `implementation_type`（wordpress-theme / react-route / vue-route / static-html / custom）
- `runtime_entry`
- `route_or_url`
- `code_paths[]`
- `selectors[]`
- `state_hooks[]`
- `theme_binding`
- `interaction_binding`
- `evidence_capture_plan`

### Milemon 示例

`site-visual-system` 可绑定为：

- `home` → `front-page.php`
- `global-header` → `header.php`
- `catalog` → `woocommerce/archive-product.php`
- `product-detail` → `woocommerce/single-product.php`
- `theme tokens` → `assets/css/design-tokens.css`, `style.css`

## 6.3 Theme / Style / Effect Binding

新增建议工件：

- `token-map.json`

至少记录：

- prototype token → implementation token / CSS variable / design token / utility class
- `theme_primary` → `--color-primary`
- `theme_secondary` → `--color-secondary`
- typography scale → `--font-size-*`
- spacing scale → `--spacing-*`
- shadow style → `--shadow-*`
- radius → `--radius-*`
- motion strategy → implementation animation/selectors

### 为什么必须有这个层

仅有 `theme.json` 还不够，因为它只表达“想要什么”，不表达“在实现里对应哪一组变量或类”。

## 6.4 Baseline Evidence Set

新增建议工件：

- `screenshots/<surface>/<breakpoint>/<state>.png`
- `surface-contracts.json`
- `interaction-contracts.json`

Baseline evidence 需要正式声明：

- 哪些截图是 canonical reference；
- 哪些 DOM selector / heading / CTA 是必须存在；
- 哪些 interaction/state 是必须可触发的；
- 哪些动效/效果是必需项，哪些只做 warn。

## 6.5 Aesthetic Baseline Pack

新增建议字段：

- `design_direction`
- `font_pair`
- `palette_hierarchy`
- `surface_density`
- `composition_rules`
- `hero_pattern`
- `cta_tone`
- `icon_treatment`
- `background_treatment`

### 为什么需要这一层

这层不是为了追求“风格花哨”，而是为了避免 prototype 被 freeze 时仍停留在：

- 过度依赖默认 Bootstrap shell
- 字体选择过于通用
- CTA 文案过于 generic
- 背景、层级、版面密度缺乏明确方向

`frontend-design` 的核心要求是：**先选定清晰设计方向，再执行一致的排版、配色、构图与动效**。因此 baseline 需要把这层设计意图正式化，而不是只保留 `theme primary/secondary` 两个 token。

## 6.6 Verify-Implementation Report

新增建议工件：

- `verify-implementation.json`
- `verify-implementation.md`

至少输出：

- `overall_status`
- `baseline_id`
- `binding_status`
- `diff_summary`
- `surface_results[]`
- `reason_codes[]`
- `blockers[]`
- `warnings[]`
- `next_actions[]`

### Diff 分类

#### A. Visual Drift
- 结构层级不符
- CTA 区块缺失
- 主视觉与 baseline 断裂

#### B. Semantic Drift
- 标题/导航/主要区域命名或可访问性结构不符
- required selector 缺失

#### C. Interaction Drift
- CTA 不存在
- 跳转不对
- drawer/modal/tab/state 无法触发

#### D. Token Drift
- 主题色、排版、间距、阴影、圆角未映射或映射错误

#### E. Effect Drift
- baseline 要求的 hover/focus/motion/feedback 没有落地

### 建议 reason codes

- `prototype_baseline_missing`
- `prototype_baseline_not_frozen`
- `prototype_surface_unbound`
- `prototype_token_unmapped`
- `prototype_aesthetic_regression`
- `prototype_ui_guideline_gap`
- `prototype_visual_drift`
- `prototype_semantic_drift`
- `prototype_interaction_drift`
- `prototype_effect_drift`
- `prototype_evidence_missing`
- `prototype_binding_stale`

## 7. 生命周期

## 7.1 Prototype Baseline 子生命周期

建议明确：

```text
Draft
→ Reviewed
→ Frozen
→ Bound
→ Implementing
→ Verified
→ Accepted
```

并支持：

- `Drifted`
- `Reopened`
- `Rewritten`
- `Superseded`

## 7.2 任意阶段重新介入

当 baseline 或实现发生重大变化时，应允许：

- 从 `Bound` / `Implementing` / `Verified` 回到 `Reopened`
- 新 revision 重新 `reviewed → frozen → bound → verify`
- 老 binding/report 标记 `superseded`

这样才能与 Beacon 现有生命周期闭环保持一致，不会因为原型变化而丢失可追溯性。

## 8. 功能需求

### FR-001 新增 Prototype Baseline 阶段

新增建议命令：

- `beacon prototype baseline <feature>`

目标：
- 从已 review/freeze 的 prototype bundle 生成正式 baseline manifest；
- 把 surface / state / breakpoint / token / effect 变成可机读治理对象。

### FR-002 Baseline 必须是 fail-fast 的

当缺少以下关键内容时，`prototype baseline` 必须失败：

- 关键 surface 未定义
- 关键 state 未定义
- 关键 breakpoint 未定义
- 关键 token 未定义
- canonical screenshot reference 缺失

不允许继续依赖“人脑自己补全”。

### FR-003 新增实现绑定能力

新增建议命令：

- `beacon prototype bind <feature> --adapter <adapter>`

要求：
- 可把 baseline surface 绑定到真实实现路径；
- 绑定必须可追溯到代码文件、运行入口与选择器；
- 支持多种 adapter，但不能把实现层抽象成不可执行的空壳。

### FR-004 Adapter 设计保持通用

至少应允许：

- `wordpress-theme`
- `static-html`
- `react-router`
- `vue-router`
- `custom`

Milemon 只是第一批验证样板，不得把 schema 写死为 WordPress 专用字段。

### FR-005 新增 verify-implementation 能力

新增建议命令：

- `beacon prototype verify-impl <feature>`

要求：
- 基于 baseline + implementation binding 运行对比；
- 输出 surface 级结果；
- 能给出 blocker / warn 结论；
- 能被 quality / accept gate 消费。

### FR-006 Verify 必须覆盖五层差异

最少包括：

1. visual
2. semantic
3. interaction
4. token
5. effect

不允许只做单一截图 diff 后就宣称“实现已按原型落地”。

### FR-007 Gate 必须消费 baseline verify 结果

当 feature 启用了 prototype baseline 治理时：

- `implement` 前若无 frozen baseline，可阻断或强提醒；
- `review quality` 前若无 binding 或 verify-impl，不得 green；
- `review accept` 前若 verify-impl blocker 未清零，必须 blocked。

### FR-008 新增 Prototype Debug Loop

新增建议命令：

- `beacon prototype debug <feature> --watch`

目标：
- 在开发阶段连续观察 mismatch；
- 汇总 surface blocker；
- 给出修复优先级；
- 允许 fix 后直接 rerun verify。

### FR-009 Prototype Debug 复用现有 Beacon Debug 能力

当前已有 `beacon debug` 的 prompt/history/debug-feedback 基础设施。

v1.1.8 的 prototype debug 应优先复用：

- `.beacon/debug-feedback/*`
- debug run id
- event memory
- rerun evidence path

但要新增面向 prototype 的结构化 payload，而不只是 prompt capture。

### FR-010 Debug 输出必须可执行

至少输出：

- `surface_id`
- `severity`
- `reason_code`
- `expected`
- `actual`
- `bound_code_paths[]`
- `suggested_fix_scope`
- `rerun_command`

### FR-011 Milemon 作为首个真实验证样板

Beacon v1.1.8 需要能表达如下 binding：

- `site-visual-system` → 全站主题 token
- `homepage-business-closure` → `front-page.php`
- `shop-catalog-ui-polish` → `archive-product.php`
- `product-list-and-detail` → `single-product.php`
- `global-header` → `header.php`

并可验证：
- 主题色映射是否正确；
- 首页 hero / CTA / 顶栏 / business links 是否与 prototype baseline 一致；
- WooCommerce 列表/详情页是否覆盖 prototype 关键结构。

### FR-012 本版是 design-only，先冻结需求

必须明确：
- v1.1.8 当前阶段只做设计方案与需求物料；
- 不要求当前代码已经支持这些子命令；
- 先冻结 baseline/binding/verify/debug 的正式设计，再进入实现阶段。

### FR-013 Prototype Baseline 必须包含 Aesthetic Baseline Pack

baseline 不能只记录技术 contract，还必须记录最小设计基线：

- 设计方向
- 字体组合
- 配色层级
- 版面密度
- hero / section 构图规则
- CTA 文案语气
- 背景/纹理/层级策略

否则 verify-impl 只能检查“像不像”，无法检查“审美是否退化回 generic shell”。

### FR-014 Prototype 生成默认要满足 Web UI 最小规范

结合 `web-design-guidelines`，prototype 生成默认基线应覆盖：

- skip link
- semantic landmark
- heading hierarchy
- heading anchor `scroll-margin-top`
- decorative icon `aria-hidden`
- 表单 `name / autocomplete / type`
- visible focus
- `prefers-reduced-motion`
- CTA 文案具体而非 generic fallback

### FR-015 Prototype Review 必须显式审计“丑但没坏”的风险

`prototype review` 不能只检查 artifact completeness，还要能标记：

- typography 过于 generic
- 构图过于模板化
- CTA 文案空泛
- 设计 token 不足以支撑差异化界面

建议以 warn/block 形式输出：

- `prototype_aesthetic_regression`
- `prototype_ui_guideline_gap`

## 9. 验收语义

### Pass
- prototype baseline、implementation binding、verify-impl、debug loop 的需求结构完整；
- 可以用 Milemon 举例说明落地方式；
- 设计保持通用，不写死到单一框架。

### Fail
- 仍停留在“生成更漂亮原型”，没有真正定义 baseline 与 binding；
- 无法解释主题色/样式/效果如何绑定到真实实现；
- 没有 debug 闭环与 blocker reason code。

### Blocked
- baseline schema、binding schema、verify layer 与 lifecycle 仍存在关键冲突。
