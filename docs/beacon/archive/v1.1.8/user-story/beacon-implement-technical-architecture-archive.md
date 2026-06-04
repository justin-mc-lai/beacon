# User Story: Beacon implement 技术实现归档与技术架构落盘（v1.1.8）

**Feature**: beacon-implement-technical-architecture-archive  
**Version**: v1.1.8

**As a** 技术负责人 / 接手开发 / 评审人 / 版本复盘参与者  
**I want** Beacon 在 implement 完成后产出正式技术实现归档文档，而不只是执行摘要  
**So that** 我能清楚看到代码具体改了什么、涉及哪些模块/API/数据库/配置/任务，以及对应风险和回滚信息。

## Story Slices

### US-001: Beacon 支持 implement 技术归档
作为技术查看者，我希望 implementation 后有技术归档工件，以便不必自己从 diff 重新拼装系统变化。

### US-002: Beacon 归档代码改动结构
作为技术查看者，我希望文档区分新增/修改/删除/重构，以便快速理解改动性质。

### US-003: Beacon 归档数据与数据库变化
作为技术查看者，我希望文档明确是否新增表、改表、migration、索引和 CRUD 操作，以便评估风险。

### US-004: Beacon 归档接口与任务变化
作为技术查看者，我希望文档记录 API、queue/job、cron 和外部集成变化，以便做联调和运维沟通。

### US-005: Beacon 归档配置与环境变量变化
作为技术查看者，我希望文档明确 config/env/feature flag 改动，以便减少部署与接手风险。

### US-006: Beacon 支持多服务技术归档
作为多服务项目维护者，我希望归档支持按 service 视角展示改动，以便真正服务复杂项目接手。

### US-007: Beacon 技术归档并入现有规范且强可追溯
作为 Beacon 维护者，我希望 implement 技术归档沿用 runtime raw / machine archive / human archive 三层规范，并带稳定 traceability 主键，以便能无缝并入现有 Beacon 体系。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Archive Surface | implement 完成后支持 `technical-implementation-<feature>.md` 与 `.machine/execution/technical-implementation-<feature>.json` |
| AC-002 | Coexistence | 技术归档与 `implementation-summary` 共存，而不是互相替代 |
| AC-003 | Three-layer Trace | 技术归档沿用 runtime raw / machine archive / human archive 三层关系 |
| AC-004 | Traceability Keys | 技术归档包含 `feature_slug/version/revision_id/run_id/runner/profile_id/git_commit/services[]` |
| AC-005 | Code Change Model | 技术归档区分新增/修改/删除/重构 |
| AC-006 | Data Model | 技术归档覆盖 CRUD / db_changes / migrations / indexes |
| AC-007 | API Model | 技术归档覆盖 API / queue / cron / external integration changes |
| AC-008 | Config Model | 技术归档覆盖 config/env/feature flag/deployment notes |
| AC-009 | None Explicit | 没有 DB/API/ENV 变化时也要显式写 none/[] |
| AC-010 | Multi-service | 技术归档支持多服务结构 |
| AC-011 | Tech Readability | 技术归档可直接给技术接手/评审/复盘使用 |
| AC-012 | Design Scope | v1.1.8 当前先冻结 implement 技术归档设计，不宣称已实现 |

## 风险与提醒

- 若仍只依赖 implementation summary，技术接手文档价值不足
- 若不覆盖 DB/API/ENV 变化，复杂项目的真正风险点仍然会漏掉
- 若不支持多服务结构，这套归档很难在实际业务项目中落地
- 若没有三层归档与 traceability 主键，它就很难真正并入 Beacon 现有规范，也无法稳定回溯到具体 run/revision
