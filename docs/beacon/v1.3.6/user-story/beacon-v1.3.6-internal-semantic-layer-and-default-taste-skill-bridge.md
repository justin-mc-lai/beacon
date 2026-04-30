# User Story: beacon-v1.3.6-internal-semantic-layer-and-default-taste-skill-bridge

## Story

**As a** Beacon 产品能力维护者 / requirement compiler owner / prototype-to-frontend 交付负责人,  
**I want** Beacon 在 `prototype` 之前先冻结一版官方产品语义，并把 `Leonxlnx/taste-skill` 作为默认外部设计桥接 skill 被 `prototype / implement` 内部受控消费，同时把 CLI 与 project skill 的 stage 词汇对齐到 `prototype / implement / qa / release`,  
**So that** Beacon 的前端产出能更官方、正式、稳定，且语义、原型、实现、QA、发布都围绕同一份语义真相闭环。

## Story Slices

### US-001: 作为 requirement compiler owner，我希望 `semantic layer` 成为 Beacon 内建能力

这样官方语义不会依赖外部 skill 或页面实现阶段临时发挥。

### US-002: 作为 prototype owner，我希望 `prototype` 在 freeze 前先消费官方语义

这样页面名称、状态系统、模块口径和页面叙事都先统一下来，而不是在 wireframe 里泄漏内部词。

### US-003: 作为 implement owner，我希望 `implement` 继续复用同一份语义真相

这样前端实现阶段不会重新翻译需求，也不会把官方表达改写成工程内部话语。

### US-004: 作为设计增强负责人，我希望默认外部设计 bridge skill 被明确冻结

这样 Beacon 对外可以说明：

- 内建语义由 Beacon 自己负责
- 默认设计增强由 `taste-skill` 承担

### US-005: 作为 skill boundary owner，我希望外部 skill 只做 augmentation，不做 truth source

这样第三方 skill 的结果必须经过 Beacon 归一化、审阅和写回，不能直接决定最终真相。

### US-006: 作为 lifecycle owner，我希望 `qa / release` 能检查 semantic/design consistency

这样官方语义不会在实现、修复或交付阶段悄悄漂移。

### US-007: 作为 CLI surface owner，我希望 help 主流程文案回到当前 `7+3` 全局边界

这样人类看到的主链始终稳定，不被旧 `think / gate` 叙事继续带偏。

### US-008: 作为 project skill maintainer，我希望 stage vocabulary 收口为 canonical stages

这样新的 `prototype / implement / qa / release` 语义能成为标准，同时旧 `implementation / verify / review / delivery` 配置继续兼容。

## Acceptance Criteria

- [ ] AC-001 Beacon 必须把 `semantic layer` 明确为内建 requirement compile 能力，而不是外部 skill 依赖。
- [ ] AC-002 `prototype` 必须存在 semantic preflight 语义，并把后续页面表达绑定到同一份官方语义 contract。
- [ ] AC-003 `implement` 必须显式复用 `semantic layer`，并允许在内部受控调用默认 `taste-skill` 做设计增强。
- [ ] AC-004 默认 design bridge 必须明确为：
  - repo: `https://github.com/Leonxlnx/taste-skill`
  - skill: `taste-skill`
- [ ] AC-005 外部 skill 输出必须经过 Beacon canonical writeback / evidence normalization，不能直接成为 truth source。
- [ ] AC-006 `qa / release` 必须能把 semantic/design consistency 作为正式 gate 对象。
- [ ] AC-007 `beacon/cli_factory.py` 顶层 help 文案必须回到当前 `7+3` 全局边界语义。
- [ ] AC-008 `beacon/utils/project_skills.py` 必须采用 `prototype / implement / qa / release` canonical stage vocabulary，同时兼容 legacy aliases。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | frozen-pending-implementation |
| Version | v1.3.6 |
| Track | parallel |
| Created | 2026-04-22 |
| Feature Slug | beacon-v1.3.6-internal-semantic-layer-and-default-taste-skill-bridge |
| Brainstorm Source | docs/brainstorms/2026-04-22-beacon-official-product-language-contract-for-prototype-and-implement-brainstorm.md |
