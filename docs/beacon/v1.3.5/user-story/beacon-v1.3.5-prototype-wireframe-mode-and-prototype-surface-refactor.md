# User Story: beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor

## Story

**As a** Beacon requirement author / prototype operator / implementation handoff owner,  
**I want** Beacon 的 `prototype` 子能力只生成 wireframe 冻结包，并把页面清单、路由跳转、状态说明与单页草图纳入 `prd -> user-story -> test-case -> prototype -> implement -> qa` 的闭环,  
**So that** 我可以在需求冻结阶段先把业务结构与页面关系讲清楚，而不是再被 HTML 高保真原型拖偏到视觉实现讨论。

## Story Slices

### US-001: Prototype 必须回到需求冻结职责

作为需求作者，我希望 `prototype` 的默认职责是冻结页面结构、交互关系和状态说明，而不是生成看起来完整的 HTML 页面。

### US-002: HTML 高保真原型必须退出 Beacon 正式边界

作为 Beacon 维护者，我希望 Beacon 不再承诺或要求 HTML 高保真原型，避免 artifact 定位错误持续污染 PRD 和实现边界。

### US-003: Wireframe 输出必须形成可 review / 可 freeze 的标准包

作为原型操作者，我希望 `prototype create` 生成固定的 wireframe 包结构，包括页面汇总、导航图、页面草图、freeze 信息和 review 结果。

### US-004: 页面与路由必须可冻结

作为项目负责人，我希望 wireframe 能明确列出页面清单、页面职责、跳转关系、状态说明与平台差异，后续实现直接基于这些冻结信息推进。

### US-005: 单页草图必须能对接 PRD 与用户故事

作为实现接力者，我希望每个页面草图都能回链到相关 PRD、用户故事和验收点，避免原型与需求文档脱节。

### US-006: Prototype 状态面必须识别 wireframe 包健康度

作为 Beacon 使用者，我希望 `prototype status / review / freeze` 能识别是否已经具备完整 wireframe 包，而不是继续围绕 HTML 原型做判断。

### US-007: 人类主链必须显式出现 `prototype`

作为 Beacon 使用者，我希望 `prototype` 正式成为 `test-case` 与 `implement` 之间的人类阶段，而不是继续停留在隐式能力或旁路工具。

### US-008: Host-visible 原型入口必须统一成 `beacon-prototype`

作为 Codex / Claude 操作者，我希望原型阶段只有一个稳定的 host-visible skill 路由，即 `beacon-prototype`，避免在多个 skill 或命令之间猜测。

### US-009: 独立 `wireframe.py` 必须退场

作为 Beacon 维护者，我希望现有独立 `wireframe.py` 不再与 `prototype` 并存，避免两套目录、两套模板、两套心智造成漂移。

## Acceptance Criteria

- AC-001 Prototype 唯一正式模式：`prototype plan/create/status/review/freeze` 都必须以 `wireframe` 作为唯一正式语义，并显式记录 `prototype_mode: "wireframe"`。
- AC-002 HTML 高保真原型移除：Beacon 文档、命令叙事、产物要求中都不再保留 HTML 高保真原型，也不保留兼容模式。
- AC-003 Wireframe 标准包成立：`prototype create` 生成的标准包至少包含 `wireframe-summary.md`、`wireframe-manifest.json`、`navigation-map.md`、`navigation-map.json`、`pages/*.md`、`freeze.json`、`prototype-review.json`。
- AC-004 页面汇总可冻结：`wireframe-summary.md` 必须冻结页面 ID、页面名称、平台、优先级、页面职责、关联 PRD / user-story。
- AC-005 路由说明可冻结：`navigation-map.md/json` 必须能表达页面间跳转、入口、返回路径、关键状态切换和禁止跳转。
- AC-006 单页草图可接力：每个 `pages/*.md` 必须包含页面职责、布局块、关键模块、用户动作、状态说明、相关物料链接。
- AC-007 Requirement 对齐成立：wireframe 包必须能映射到 `prd / user-story / test-case`，并作为页面冻结的正式 requirement artifact。
- AC-008 Freeze / review / status 可验证：当标准包缺失关键文件或映射关系不完整时，`prototype review` 与 `prototype freeze` 必须给出阻断或降级结果。
- AC-009 Prototype 不承担视觉终稿：Beacon `prototype` 只负责 wireframe 冻结，不承担高保真设计稿、最终前端页面或视觉系统定义。
- AC-010 中文可读与实现友好：wireframe 输出必须优先服务中文需求沟通和实现接力，避免只有机器可读结构、缺乏人类可直接审核的页面说明。
- AC-011 人类主链升级：Beacon 的人类闭环明确升级为 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`。
- AC-012 Host-visible skill 统一：Beacon 对外存在 `beacon-prototype`，并由它承担唯一原型阶段路由。
- AC-013 旧 wireframe 命令退役：`wireframe.py` 必须被直接移除，不再保留正式平行入口，也不保留兼容迁移壳层。
- AC-014 文档语义一致：`docs/beacon/v1.3.5/*` 与 Beacon skill 文档都明确 `prototype = requirement-driven wireframe freeze orchestrator`。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Status | frozen-pending-implementation |
| Version | v1.3.5 |
| Track | main |
| Feature Slug | beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor |
| Prototype Boundary | wireframe only |
| Downstream Role | freeze artifact for implementation |
