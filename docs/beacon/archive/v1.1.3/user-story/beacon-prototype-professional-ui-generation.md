# User Story: Beacon 原型子命令升级为专业 UI 原型生成（v1.1.3）

## Story

**As a** 使用 Beacon 的产品负责人 / 设计协作者 / 研发 / QA，  
**I want** `beacon prototype` 能基于 PRD + User Story 中的结构化 Prototype Contract 生成专业级 UI 原型，而不是通用 Bootstrap 壳子，  
**So that** 原型能真实表达需求结构、主题色、页面跳转、交互说明与关键状态，并成为可 review / freeze / gate 的正式交付物。

## Acceptance Criteria

| AC ID | 维度 | 标准 |
|------|------|------|
| AC-001 | Prototype Input | `prototype create` 必须从 PRD + User Story 中读取结构化 Prototype Contract，而不是仅依赖前几行文本预览 |
| AC-002 | Safety | 当 Prototype Contract 缺失关键字段时，`prototype create` 必须直接失败，不允许退化为模糊猜测生成 |
| AC-003 | Contract | Prototype Contract 至少覆盖：`prototype_archetype`、设计意图、信息架构、主 CTA、跳转说明、关键状态 |
| AC-004 | UX | 原型必须能表达专业 UI 气质：主题色、排版层级、卡片/列表/工作台结构，而不是 generic shell |
| AC-005 | Archetype | 原型至少支持 archetype：`dashboard / list-detail / form-wizard / marketing-page / admin-workbench / mobile-task-flow` |
| AC-006 | Theme | 生成物必须包含 `theme.json`，记录主题色、排版、spacing、radius、shadow、motion 策略 |
| AC-007 | Navigation | 生成物必须包含 `navigation-map.json`，记录页面区块、导航节点、跳转目标和跳转说明 |
| AC-008 | Interaction | 生成物必须包含 `interaction-map.json`，记录 CTA、modal、drawer、tabs、toast、表单动作与状态切换 |
| AC-009 | Brief | 生成物必须包含 `prototype-brief.json`，记录 archetype、目标用户、主流程、核心 CTA、设计意图 |
| AC-010 | Review | 新增 `prototype review` 子命令，检查需求覆盖、信息架构、跳转完整性、状态覆盖、设计一致性、可访问性、AI slop 风险 |
| AC-011 | Review Output | `prototype review` 至少输出 `prototype-review.json` 与 `prototype-review.md` |
| AC-012 | Workflow | UI 需求进入 prototype 阶段时，workflow 不只要求 create/freeze，还应要求 review 通过 |
| AC-013 | Gate | 当 `ui_visualization_required=true` 时，gate 必须校验 theme / navigation / interaction / review 产物是否齐全 |
| AC-014 | Testability | `test-case create` 可读取 navigation / interaction contract 生成 CTA 跳转、状态覆盖与 UI smoke 用例 |
| AC-015 | Accessibility | 生成原型必须继续满足语义结构、focus、aria-label、label、reduced-motion 等要求 |
| AC-016 | Draft Stage | 文档必须明确：当前 v1.1.3 仍是需求草稿阶段，现有 `prototype.py` 尚未实现这些能力是正常现象 |

## Prototype Contract (structured draft)

ui_visualization_required: true
prototype_archetype: admin-workbench
target_user: product manager
theme_mood: trusted
theme_primary: #2563eb
theme_secondary: #111827
brand_keywords: trust, delivery, visibility
surface_style: elevated-clean
sections: Overview, Contract, Review
navigation: Overview, Contract, Review
primary_entry: Overview
primary_exit: Review
primary_cta: Review prototype contract
secondary_cta: Freeze approved prototype
jump_map: Overview->Contract: Inspect structured contract; Contract->Review: Validate completeness
modal_map: Review summary modal
drawer_map: Contract details drawer
tab_map: Overview, Contract, States
states: empty, loading, error, success, review-needed

## Notes

- 当前 `prototype.py` 已具备 `create / preview / freeze / status / list` 基础骨架，但生成结果仍偏向 generic Bootstrap 演示页。
- 下一阶段不是“加更多花哨命令”，而是让 `prototype create` 从“读文本片段”升级为“读结构化设计/交互契约”。
- 参考 gstack 的设计思路，原型必须先表达设计意图，再表达 HTML 壳子；真实页面优先于组件展示页。
- `prototype review` 的目标是补齐“生成”之后的设计/交付审计，不是取代 `design` 命令。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | draft |
| Version | v1.1.3 |
| Feature Slug | beacon-prototype-professional-ui-generation |
