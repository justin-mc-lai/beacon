# User Story: Beacon 原型基线、实现绑定与防漂移 Debug 闭环（v1.1.8）

**Feature**: beacon-prototype-baseline  
**Version**: v1.1.8

**As a** 使用 Beacon 进行需求、原型、实现与验收闭环的产品/设计/研发/QA/AI Agent 协作方  
**I want** Beacon 把 prototype 正式升级为可冻结的 baseline，并能绑定真实实现、校验差异、进入 debug 修复闭环  
**So that** 原型不再和实现脱节，主题色、样式、效果、交互与关键页面结构都能被确定性追踪与验收。

## Story Slices

### US-001: Beacon 支持 Prototype Baseline
作为 Beacon 使用者，我希望冻结后的 prototype 能生成正式 baseline manifest，以便实现阶段有明确参照物。

### US-002: Beacon 支持 Implementation Binding
作为 Beacon 使用者，我希望把 baseline 的 surface 绑定到真实 route / template / component / token，以便 Beacon 知道要核对哪里。

### US-003: Beacon 支持 Theme / Style / Effect 映射
作为 Beacon 使用者，我希望 prototype 的主题色、排版、间距、阴影、动效与真实实现 token 建立映射，以便样式落地可被追踪。

### US-004: Beacon 支持 Prototype ↔ Implementation Verify
作为 Beacon 使用者，我希望 Beacon 能对原型与真实实现做视觉、语义、交互、token、effect 多层校验，以便自动发现 drift。

### US-005: Beacon 支持 Prototype Debug Loop
作为 Beacon 使用者，我希望在开发阶段开启 prototype debug，持续看到 mismatch、修复建议与 rerun 结果，以便像 gstack 一样形成修复闭环。

### US-006: Beacon 生命周期支持 baseline rewrite/reopen
作为 Beacon 使用者，我希望 baseline 在任意阶段变化时都能 reopen/rewrite 并重新闭环，以便避免“旧原型、旧绑定、旧验收结果”继续污染当前交付。

### US-007: Beacon 用 Milemon 验证真实可落地性
作为 Beacon 维护者，我希望用 Milemon 作为第一个真实样板，但能力设计保持通用，以便后续扩展到 React/Vue/WordPress 以外的项目。

### US-008: Beacon 为 prototype generator 定义最小审美与 Web UI 基线
作为 Beacon 使用者，我希望 prototype generator 自身先满足最小审美和 Web UI 规范基线，以便被冻结下来的 baseline 本身不会太丑、太泛化、太不具体。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Baseline | Beacon 定义正式的 `prototype baseline` 概念，而不是只依赖 `freeze.json` |
| AC-002 | Baseline | baseline 至少包含 surface、state、breakpoint、theme token、motion/effect、screenshot reference |
| AC-003 | Baseline | baseline 缺少关键 surface/state/token 时必须 fail-fast |
| AC-004 | Binding | Beacon 支持 implementation binding manifest |
| AC-005 | Binding | 每个 surface 可绑定 route/url、code path、selector、state hook、evidence capture plan |
| AC-006 | Adapter | binding 设计支持多 adapter，不写死为 WordPress |
| AC-007 | Token Mapping | prototype 的主题色/排版/间距/圆角/阴影/动效可映射到真实实现 token |
| AC-008 | Verify | Beacon 支持 `prototype verify-impl` 的正式概念 |
| AC-009 | Verify Layers | verify-impl 至少覆盖 visual / semantic / interaction / token / effect 五层差异 |
| AC-010 | Drift Reason | Beacon 对 drift 输出明确 reason code，而不是模糊描述 |
| AC-011 | Gate | 启用 prototype baseline 治理时，quality/accept 必须消费 verify-impl 结果 |
| AC-012 | Missing Binding | surface 未绑定或证据缺失时，不得误判“按原型落地” |
| AC-013 | Debug | Beacon 支持 prototype debug watch/fix/rerun 闭环 |
| AC-014 | Debug Evidence | debug 输出包含 surface、severity、expected、actual、code paths、rerun command |
| AC-015 | Lifecycle | baseline 生命周期至少包含 Draft / Reviewed / Frozen / Bound / Implementing / Verified / Accepted |
| AC-016 | Reopen | baseline 在任意阶段变更后可 reopen/rewrite，并产生新的 revision 闭环 |
| AC-017 | Milemon | Milemon 可作为真实样板，表达 prototype 与 `front-page.php` / `header.php` / `style.css` / `woocommerce/*` 的绑定 |
| AC-018 | Theme Example | Milemon 样板中可表达 `theme.json` 到 `assets/css/design-tokens.css` 的 token mapping |
| AC-019 | Generality | 能力设计保持通用，可扩展到 React/Vue/static-html 项目 |
| AC-020 | Design Scope | v1.1.8 当前为 design-only 版本，先冻结需求结构，不宣称功能已实现 |
| AC-021 | Aesthetic Baseline | baseline 必须包含设计方向、字体组合、配色层级、版面密度、CTA 语气等最小审美基线 |
| AC-022 | Web Guideline | prototype 默认生成结果必须覆盖 skip link、semantic landmark、heading hierarchy、icon `aria-hidden`、表单语义、visible focus 等 Web UI 最小规范 |
| AC-023 | Anti-Generic | finalized baseline / review 需要显式识别 generic CTA、过度模板化 card shell、弱字体人格等“丑但没坏”的退化风险 |

## 风险与提醒

- 若只加 screenshot diff，不加 implementation binding，仍然不知道“该对比哪个真实入口”
- 若只加 binding，不加 token/effect mapping，主题色和动效漂移仍会被漏掉
- 若没有 debug loop，开发期 drift 仍然只能人工追踪，无法形成稳定修复节奏
- 若 prototype 自身缺少审美和 Web UI 基线，再完整的 binding/verify 也只会把“普通甚至难看”的 reference 冻结下来
