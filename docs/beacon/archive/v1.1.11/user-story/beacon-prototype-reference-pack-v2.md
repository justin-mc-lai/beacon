# User Story: Beacon Prototype v2 升级为 Story-driven 高保真实现参考包（v1.1.11）

**Feature**: `beacon-prototype-reference-pack-v2`
**Version**: `v1.1.11`

## Story

**As a** 使用 Beacon 管理需求、设计、前端实现与验收闭环的产品负责人 / 设计协作者 / 前端负责人 / QA owner / AI coding agent
**I want** `beacon prototype` 不再只生成 archetype 单页 demo，而是基于 User Story + PRD + route/code/baseline sources 编译出 story-driven 的 page-level 高保真实现参考包
**So that** 原型能真实表达页面覆盖、关键信息、状态、CTA、路由闭环、视觉系统与防退化边界，并成为后续实现、评审、测试与 freeze/gate 的正式输入

## Story Slices

### US-001: Prototype 输入从扁平字段升级为结构化 contract compiler
作为原型维护者，我希望 `prototype` 先编译 story/prd/route/baseline sources，再生成页面，而不是直接从几行 `key: value` 拼 HTML。

### US-002: 页面 inventory 成为高保真输出的第一性原理单位
作为前端负责人，我希望 Beacon 先回答“需要哪些页面、哪些状态、哪些页面必须高保真”，再回答页面长什么样。

### US-003: 每个 required page 都有独立高保真画布和关键状态变体
作为设计协作者，我希望 required pages 不再混用 `compact coverage` 或摘要式小卡片，而是输出可评审、可实现的独立画布。

### US-004: 已验证过的页面表达可以被 baseline protection 固定
作为 takeover 项目维护者，我希望原有有效高保真页面不会被新一轮 generic scaffold 退化。

### US-005: Prototype route closure 与 page/state/context/fallback 合同合并
作为 QA owner，我希望 CTA/tab/page jumps 不只是“写在页面里”，而是能被 route closure 和 implementation binding 消费。

### US-006: review / gate / freeze 要基于 coverage、state、route、artifact consistency 做严格判定
作为 release owner，我希望原型不是“文件齐了就 pass”，而是需要真实通过严格检查才允许 freeze。

### US-007: 真实复杂项目可以被 Prototype v2 truthful 表达
作为产品负责人，我希望像 `slow_uni_bmtop` 这样要求 38 页全高保真的项目，能够被 Beacon 的原型产物如实承载，而不是被降级成“13 个重点页 + 25 个补齐页”。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Contract Compiler Input | `prototype plan/create` 必须消费结构化 story/prd blocks，并支持 route source、code source、baseline source，而不是仅依赖前几行扁平 preview |
| AC-002 | CJK-safe Parsing | contract parser 必须正确处理中文分号、中文冒号、换行列表、多段 block，不允许因为 `；` 等标点导致 jump/state/section 丢失 |
| AC-003 | Page Inventory | 必须显式解析 `coverage_mode` 与 `page_inventory`；当 feature 声明 `all-existing-routes` 时，Beacon 需解析 required pages，而不是只渲染 archetype sections |
| AC-004 | Page Spec | 每个 required page 都必须生成 page-spec，至少包含 `page_id`、`intent`、`sections`、`primary_cta`、`states`、`route_targets`、`truth_notes` |
| AC-005 | Hi-fi Output | 每个 required page 都必须生成独立高保真页面/画布；当 contract 声明 `full-hi-fi` 时，不允许退回 `compact coverage`、结构化小画布或摘要式表格替代 |
| AC-006 | Baseline Protection | contract 可声明 `baseline_protection`；被保护页面不得退化为 generic shell，不得丢失既有有效交互与信息层级 |
| AC-007 | Route Closure | CTA/tab/page jumps 必须携带 target、context/params、fallback，并进入 `route-closure-contract.json` 与 `implementation-map.json` |
| AC-008 | Shared Visual System | 产物必须输出单一 `theme.json + tokens.css`，并显式声明页面只能消费共享 token，不允许 per-page 失控硬编码 |
| AC-009 | Review Strictness | `prototype review` 必须检查 page coverage、state coverage、compact-mode drift、baseline regression、route closure、artifact consistency、stale source |
| AC-010 | Freeze Integrity | `prototype freeze` 仅在 `review=pass`、`stale=false`、manifest/freeze/review 自洽、artifact fingerprints 完整时允许通过 |
| AC-011 | Machine Consumers | `test-case/review/gate/implementation` 必须可消费 `prototype-plan.json`、`page-specs/`、coverage report、route closure 工件 |
| AC-012 | Real Fixture Coverage | `slow_uni_bmtop` 这类要求“38 页全高保真 + baseline protection + route closure”的 fixture 必须可被 truthful 表达 |
| AC-013 | Backward Compatibility | 旧的 prototype 流程可继续使用 minimal mode，但 minimal mode 必须显式标记为不具备 `reference-pack-v2` 的强保证 |

## Prototype Contract v2 Draft

```yaml
ui_visualization_required: true
prototype_mode: reference-pack-v2
coverage_mode: all-existing-routes
page_inventory_source:
  - docs/FRONTEND-PAGES-ROUTES.md
  - src/router/index.ts
baseline_protection:
  - page: game-detail
    preserve:
      - full-match-information
      - tab-click-and-swipe-dual-path
      - primary-cta-prominence
  - page: rankings
    preserve:
      - podium-and-list-coexist
      - long-nickname-safe-layout
route_closure_required: true
required_states:
  - empty
  - loading
  - error
  - auth-required
  - completed
```

## Notes

- `v1.1.10` 已解决 prototype route closure 的一部分问题，但还没有解决“原型是否足够 truthful，能否作为实现参考”的更大问题。
- Prototype v2 的第一性原理不是“换更漂亮的模板”，而是“先回答需要交付哪些页面/状态/跳转/边界，再生成页面”。
- `slow_uni_bmtop` 暴露的矛盾说明：真实项目需要 page inventory、baseline protection、strict review，而不是单页 archetype shell。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 13 |
| Status | draft |
| Version | v1.1.11 |
| Feature Slug | beacon-prototype-reference-pack-v2 |

## Prototype Compiler Flat Contract (Minimum Executable)

prototype_archetype: admin-workbench
theme_mood: disciplined
theme_primary: #2563eb
sections: Overview, Page Inventory, Route Closure, Baseline Protection, Delivery Readiness
navigation: Overview, Page Inventory, Route Closure, Delivery Readiness
primary_entry: prototype-plan
primary_exit: prototype-freeze
primary_cta: Generate Reference Pack
jump_map: prototype-plan->page-specs:compile required pages and states; page-specs->route-closure:attach runtime closure contract; route-closure->prototype-review:validate coverage and consistency
states: draft, review-ready, frozen
