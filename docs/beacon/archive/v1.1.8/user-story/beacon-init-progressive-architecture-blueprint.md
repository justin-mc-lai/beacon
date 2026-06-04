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

### US-007: init 区分项目文档版本与 Beacon 运行时版本
作为 Beacon 使用者，我希望项目 docs 版本线和 Beacon runtime 版本分离，以便老项目能接入最新 Beacon，而不会误创建错误的项目版本目录。

### US-008: status / help / doctor 显式展示双版本上下文
作为 Beacon 使用者，我希望导航和诊断面同时展示 docs_version 与 runtime_version，以便我知道自己在看哪条项目线、运行哪条 Beacon 线。

### US-009: doctor 主动发现版本分离漂移
作为 Beacon 使用者，我希望 doctor 能主动发现 docs/runtime 重新耦合、context marker 漂移和 runtime 同名 docs root 误建，以便问题在扩散前就被发现。

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
| AC-008 | Version Separation | init 支持 `docs_version` 与 `runtime_version` 语义分离 |
| AC-009 | Adoption State | init 设计支持 `.beacon/state/project-onboarding.json` 与 `lifecycle_adoption_level` |
| AC-010 | Technical Readability | 技术架构蓝图适合技术查看，不只是产品文案 |
| AC-011 | Evolution Readability | 版本蓝图能够支持版本递进对照 |
| AC-012 | Context Compatibility | 新设计不破坏现有 managed block / doctor context 机制 |
| AC-013 | Dual-Version Navigation | status/help/doctor 显式输出 `docs_version` / `runtime_version` / `context_managed_version` |
| AC-014 | Drift Detection | doctor 能识别 docs/runtime 分离漂移与 runtime 同名 docs root 可疑误建 |
| AC-015 | Design Scope | v1.1.8 当前先冻结 init 增强设计，不宣称已实现 |

## 风险与提醒

- 若 AGENTS 主入口没有渐进式披露，技术和 agent 容易直接掉进细节噪音里
- 若没有 architecture blueprint，接手项目仍要靠口口相传或自己翻代码
- 若没有 version blueprint，版本递进关系会越来越模糊
- 若没有 onboarding state 与 adoption level，Beacon 很难判断项目到底被接管到什么深度
- 若不分离 docs version 与 runtime version，老项目接入最新 Beacon 时会错误生成新的项目版本线
- 若 status/help/doctor 不显式展示双版本，使用者仍会把 docs line 和 Beacon runtime line 混淆
- 若 doctor 不主动发现漂移，错误目录和错误 context marker 可能再次沉积到项目中
