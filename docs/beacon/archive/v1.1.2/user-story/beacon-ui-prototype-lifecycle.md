# User Story: Beacon 静态 UI Prototype（Bootstrap 默认栈）生成、冻结与 Workflow 集成（v1.1.2）

## Story

**As a** 使用 Beacon 的产品负责人 / 研发 / QA / AI Agent 维护者，  
**I want** Beacon 能基于需求主链生成使用 Bootstrap 默认栈的静态单页 UI Prototype，并把 prototype 纳入 workflow / gate 生命周期，  
**So that** UI 型需求不再只停留在文字 PRD，而能形成可视化、可冻结、可追溯、可快速预览、可作为参考实现的正式交付物。

## Acceptance Criteria

| AC ID | 维度 | 标准 |
|------|------|------|
| AC-001 | Functionality | 新增 `beacon prototype` 子命令组，至少支持 `create / preview / freeze / status / list` |
| AC-002 | Functionality | `prototype create` 默认从 `user-story / prd` 推导页面结构，生成可运行静态单页 `index.html` |
| AC-003 | Data | prototype 工件统一落盘到 `docs/beacon/<version>/prototype/<feature>/` |
| AC-004 | Data | 每个 prototype 至少生成 `index.html`、`manifest.json`、`source-map.json`、`freeze.json` |
| AC-005 | UX | 生成的原型能直接本地预览，并具备基础视觉设计层，不呈现裸默认组件观感 |
| AC-006 | UX | prototype 默认技术栈采用 `Bootstrap 5.3.x + Bootstrap Icons + Beacon Theme CSS + Alpine.js` |
| AC-007 | UX | 页面默认支持基础导航跳转、Tabs、Modal、Offcanvas/Drawer、Toast、表单交互 |
| AC-008 | Governance | `freeze` 后记录来源 `user-story / prd` 指纹；来源变更后 prototype 必须标记为 `stale` |
| AC-009 | Workflow | workflow 支持 prototype 阶段，并允许对非 UI 需求自动 skip |
| AC-010 | Workflow | UI 需求开启 prototype 时，workflow 阶段顺序为 `think -> user-story -> prd -> prototype -> test-case -> implementation -> verify -> gate` |
| AC-011 | Workflow UX | `workflow status / hud / report` 可展示 prototype 状态（pending/completed/skipped/draft/frozen/stale/blocked） |
| AC-012 | Gate | 当需求声明 `ui_visualization_required=true` 时，若 prototype 缺失、未冻结或 stale，则 gate BLOCKED |
| AC-013 | Intent Routing | `prompt optimize / ask` 可识别 `prototype / 交互原型 / 可点击原型 / UI 原型 / 单页原型` 并路由到 prototype |
| AC-014 | Design Quality | prototype 模板必须包含 Beacon Theme 设计层：色板、排版、层级、卡片、焦点态、状态色、空态/错误态 |
| AC-015 | Accessibility | prototype 页面具备语义化结构、可见 focus、图标按钮 aria-label、表单 label、基础 reduced-motion 兼容 |
| AC-016 | Compatibility | 新能力只以 `docs/beacon/<version>/` 为 source，不重新引入 `docs/product` 人工维护路径 |
| AC-017 | Safety | prototype 明确标注为 reference implementation，不等同于生产代码 |
| AC-018 | Testability | verify 阶段可对 prototype 执行基础 DOM / console / a11y smoke 校验 |

## Notes

- 本轮在 **v1.1.2** 正式明确：**Bootstrap 为默认原型 UI 组件库**。
- 选择 Bootstrap 不是因为它最潮，而是因为它更适合 Beacon 的目标：**静态单页、快速生成、带弹窗跳转、可冻结、可治理**。
- prototype 是正式交付链中的 **可选阶段**，只对 `ui_visualization_required=true` 的需求强制。
- 默认交付形态是 **静态单页参考实现**，不要求生成完整前端工程。
- prototype 的存在是为了冻结需求视觉意图、交互意图和页面结构，不承担生产实现职责。
- 视觉层应吸收前端设计最佳实践：避免“裸 Bootstrap 控件页”，通过主题设计层提升辨识度与层级表达。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | draft |
| Version | v1.1.2 |
| Feature Slug | beacon-ui-prototype-lifecycle |
| Default UI Kit | Bootstrap 5.3.x |
