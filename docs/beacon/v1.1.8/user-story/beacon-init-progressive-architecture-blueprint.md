# User Story: Beacon init 渐进式披露、技术架构主文档与版本演进蓝图（v1.1.8）

**Feature**: beacon-init-progressive-architecture-blueprint  
**Version**: v1.1.8

**As a** 初始项目创建者 / 二开接手开发 / 技术负责人 / 使用 Beacon 的 agent  
**I want** `beacon init` 不只初始化目录，还能补齐 AGENTS 主入口的渐进式披露，并生成技术架构主文档与版本演进蓝图  
**So that** 项目在 greenfield 和 takeover 两种场景下，都有清晰的技术阅读入口和长期演进对照面。

## Story Slices

### US-001: init 支持 greenfield / takeover 模式
作为 Beacon 使用者，我希望 init 能区分新项目与接手项目，以便生成更贴合的技术入口。

### US-002: AGENTS 主入口支持渐进式披露
作为技术/agent 使用者，我希望 AGENTS 主入口明确推荐阅读顺序，以便先看概要，再逐步深入。

### US-003: init 生成技术架构蓝图主文档
作为技术负责人，我希望项目初始化后立即有 architecture blueprint，以便后续实现和接手有统一对照面。

### US-004: init 生成版本演进蓝图
作为技术负责人，我希望有版本演进蓝图，以便知道当前版相对前一版/下一版的位置。

### US-005: init 生成 implement 技术归档索引
作为技术查看者，我希望 execution 下有 implementation archive index，以便后续逐步沉淀具体实现归档。

### US-006: init 初始化项目生命周期接管基线
作为 Beacon 使用者，我希望 init 不只建文档，还能初始化项目的生命周期接管状态，以便 Beacon 后续真正接管项目开发。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Project Mode | init 设计支持 greenfield / takeover 两类项目模式 |
| AC-002 | Progressive Disclosure | AGENTS 主入口明确 SUMMARY → execution/index → architecture → prd/us/qa → .machine 的渐进式阅读顺序 |
| AC-003 | Mode Guidance | AGENTS guidance 中区分 greenfield / takeover 场景 |
| AC-004 | Architecture Blueprint | init 生成 `execution/architecture-blueprint.md` |
| AC-005 | Version Blueprint | init 生成 `execution/version-evolution-blueprint.md` |
| AC-006 | Onboarding Doc | init 生成 `execution/project-lifecycle-onboarding.md` |
| AC-007 | Archive Index | init 生成 `execution/implementation-archive-index.md` |
| AC-008 | Adoption State | init 设计支持 `.beacon/state/project-onboarding.json` 与 `lifecycle_adoption_level` |
| AC-009 | Technical Readability | 技术架构蓝图适合技术查看，不只是产品文案 |
| AC-010 | Evolution Readability | 版本蓝图能够支持版本递进对照 |
| AC-011 | Context Compatibility | 新设计不破坏现有 managed block / doctor context 机制 |
| AC-012 | Design Scope | v1.1.8 当前先冻结 init 增强设计，不宣称已实现 |

## 风险与提醒

- 若 AGENTS 主入口没有渐进式披露，技术和 agent 容易直接掉进细节噪音里
- 若没有 architecture blueprint，接手项目仍要靠口口相传或自己翻代码
- 若没有 version blueprint，版本递进关系会越来越模糊
- 若没有 onboarding state 与 adoption level，Beacon 很难判断项目到底被接管到什么深度
