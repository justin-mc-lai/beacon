# User Story: Beacon vNext 边界收口与 CLI 分层重构（v1.1.3）

## Story

**As a** Beacon 维护者 / 使用 Beacon 的产品负责人 / 研发 / QA / AI Agent 使用者，  
**I want** Beacon 在 v1.1.3 先完成功能边界收口、命令收口与文档叙事重写，  
**So that** Beacon 能回到“需求交付闭环内核”的清晰定位，而不是继续向 PM 模板大全或多代理编排平台发散。

## Acceptance Criteria

| AC ID | 维度 | 标准 |
|------|------|------|
| AC-001 | Positioning | 明确 Beacon vNext 的一句话定位是“evidence-first 的需求交付闭环内核” |
| AC-002 | Boundary | 功能边界文档明确 Beacon 的 In Scope / Out of Scope，并说明与 `gstack` / `symphony` 的边界 |
| AC-003 | First Principles | 文档明确第一性原则：解决的是需求收敛、交付证据、gate 放行，而不是模板数量或 agent 调度数量 |
| AC-004 | Command Inventory | 命令收口清单覆盖当前 `SUPPORTED_SUBCOMMANDS` 的 40 个子命令 |
| AC-005 | Command Decision | 每个子命令都被标记为 `保留` / `迁出` / `废弃`，并给出理由与目标层级 |
| AC-006 | Core Focus | 保留命令以 `think -> user-story -> prd -> prototype -> test-case -> workflow -> auto-test -> gate -> release` 为核心 |
| AC-007 | Labs Boundary | 竞品分析、JTBD、Kano、Persona、Roadmap、UI Spec、Wireframe 等模板型命令被明确标记为迁出 core |
| AC-008 | Bridge Boundary | `run / team / ralph-bridge` 被明确标记为 bridge/experimental，而不是 core narrative |
| AC-009 | README Draft | README 重写草案只保留“当前版本 / 当前能力边界 / 当前推荐命令 / 当前交付工件 / 当前验证命令”五类信息 |
| AC-010 | Source of Truth | README 草案与本版文档不再重新引入 `docs/product/<version>/` 作为人工双写主源 |
| AC-011 | CLI Layering | CLI 分层方案明确 core / support / labs / bridge 四层与默认路由策略 |
| AC-012 | NL Routing | 分层方案明确自然语言默认只路由 core/support，labs 仅显式调用 |
| AC-013 | Delivery | 本次新增文档全部落在 `docs/beacon/archive/v1.1.3/`，不写 `docs/product/` |
| AC-014 | Release Semantics | 文档明确本版是 v1.1.3 requirement materials draft，不自动代表运行时包版本已经升级 |
| AC-015 | Version Package Semantics | 文档明确一个发布线只保留一个正式版本根目录，版本语义不能再与主题容器语义混用 |
| AC-016 | Delivery Layering | 文档明确正式交付文档与 raw evidence 必须强制分层，避免执行层被机器文件淹没 |
| AC-017 | Minimum Closure | 文档明确每个正式版本包至少具备 `SUMMARY / execution/boundaries / prd / user-story / qa/test-cases / release` 最小闭环 |
| AC-018 | Long-term Truth Source | 文档明确 `docs/beacon/` 是长期事实源，`.beacon/` 只是运行时临时状态 |
| AC-019 | Implementation Phasing | 文档明确“必须先做”1~7 与“其次再做”8~10 的实施顺序，避免实现期失焦 |
| AC-020 | Draft Stage Record | 文档明确 v1.1.3 当前属于需求草稿阶段，未实现是正常现象，不应被误判为版本失败 |
| AC-021 | Canonical Workflow Model | 文档明确 canonical workflow 主状态机只有一套，并收敛到 `think -> user-story -> prd -> [prototype] -> test-case -> implementation -> verify -> gate` |
| AC-022 | Release Semantics | 文档明确 `release` 是 post-gate action，而不是 workflow 内部阶段 |
| AC-023 | Implementation Semantics | 文档明确 `implementation` 是外部执行对齐点，而不是 Beacon 自己承担业务实现 |
| AC-024 | Governance Responsibility Boundary | 文档明确 `doctor / report / gate` 的职责边界：诊断 / 汇总 / 阻断 |
| AC-025 | Review Loop | 文档明确 Beacon 应新增顶层 `review spec|quality`，作为实现阶段正式回写动作 |
| AC-026 | OPSX-inspired Iteration | 文档明确 Beacon 借鉴 OPSX 的“fix artifact then continue”，但不引入 OpenSpec 的 change-folder 结构 |

## Notes

- 本版不是“再加命令”，而是“先收口，再演进”。
- `gstack` 证明了：优秀的 agent 产品应围绕少量高价值工作流与一个硬问题构建，而不是命令越多越好。
- `symphony` 证明了：issue tracker 调度、workspace 生命周期和 agent runner 属于另一类系统，不应和 Beacon core 混为一体。
- `creating-agent-skills` 规范也表明：skill/command 设计应该强调清晰触发、渐进披露和单一职责，而不是无限叠加模板。
- rolo 的高强度使用进一步证明：Beacon 若缺少版本根目录语义、正式面/证据分层、最小闭环与长期事实源约束，就会从 workflow 内核滑向“项目档案堆积层”。
- 当前 v1.1.3 仍是需求草稿阶段，因此和 v1.1.2 代码实现之间存在差距是正常现象；重点是先把实施顺序冻结，而不是误把“未实现”当作异常。
- 实施顺序必须先围绕唯一主源、最小闭环、版本根目录语义、formal/raw 分层、CLI/路由收口，再处理迁移矩阵与帮助文档同步。
- 当前闭环设计复审结论是：主链方向合理，但状态机、release 语义、implementation 语义以及 doctor/report/gate 的职责边界仍需继续收口。
- 当前还需要补齐顶层 `review spec|quality`，让实现阶段发现偏差后可以正式回写物料并继续推进，而不是只写 memory。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 5 |
| Status | draft |
| Version | v1.1.3 |
| Feature Slug | beacon-vnext-boundary-consolidation |
