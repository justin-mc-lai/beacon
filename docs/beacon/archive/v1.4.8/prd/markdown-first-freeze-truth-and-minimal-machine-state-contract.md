# PRD: Markdown-first Freeze Truth 与 Minimal Machine State Contract

**Feature**: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
**Version**: `v1.4.8`
**Date**: `2026-05-21`
**Status**: `frozen`
**Revision**: `R3`
**Track**: `markdown-first-truth + minimal-machine-state + runtime-json-only`
**Scenario**: `beacon_freeze_truth_should_be_markdown_first_without_fulltext_machine_mirrors`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.4.8/SUMMARY.md`
- Research: `docs/beacon/archive/v1.4.8/research/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- Source architecture: `docs/beacon/archive/v1.4.8/source-architecture/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- Existing v1.4.8 gate hardening feature: `docs/beacon/archive/v1.4.8/prd/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`

## 1. 问题

Beacon 当前需求冻结阶段生成的机器面 JSON 过大，且部分内容重复承载 Markdown truth。

这造成：

- token 和执行成本上升
- 冻结材料被机器镜像主导
- Markdown 与 JSON 可能发生双 truth 漂移
- gate 依赖大 JSON 时难以解释真正的 truth 来源

真正需要保留的不是完整机器镜像，而是可验证的最小状态。

## 2. 目标

1. 冻结 Markdown-first truth 原则。
2. 冻结 minimal machine state 原则。
3. 禁止需求冻结阶段 fulltext machine mirrors。
4. 保留 implement / QA / release runtime JSON evidence。
5. 让 gate 优先读取 Markdown truth，再用最小 state cache 验证 hash、revision、refreeze status。

## 3. 设计原则

### 3.1 Markdown is truth

PRD、user-story、test-case、research、execution、release 文档是需求冻结的唯一 truth。

### 3.2 JSON is cache/state

冻结阶段 JSON 只允许存储：

- `feature`
- `version`
- `revision_id`
- `source_revision_id`
- `status`
- `baseline_hash`
- `source_paths`
- `diagnostics`
- `transaction_ref`

### 3.3 No fulltext mirrors

冻结阶段机器 JSON 不得复制整篇 Markdown 正文、完整表格正文、完整研究正文或完整测试文档正文。

### 3.4 Runtime JSON only

implement / QA / release 的 process、thread、session、trace、evidence 继续使用 JSON。

### 3.5 Gate reads Markdown first

Gate 必须先解析 Markdown truth，再使用最小 state cache 校验漂移。

### 3.6 边界 / 分层 / 恢复策略

- 边界：机器缓存不得成为需求 truth。
- 分层：requirement truth 属于 Markdown；runtime evidence 属于 JSON。
- 恢复：当 cache drift 时，重新从 Markdown truth 生成最小 state，而不是反向用 JSON 覆盖 Markdown。

## 4. 范围

### In scope

- freeze/refreeze 阶段机器 JSON 瘦身
- Markdown deterministic parser contract
- PRD / user-story / test-case AC projection from Markdown
- baseline hash from Markdown truth
- minimal state cache contract
- runtime JSON 边界声明

### Out of scope

- 删除 implement / QA / release runtime JSON
- 删除所有 `.machine` 目录
- 用 LLM 解释 Markdown gate
- 放松 gate fail-closed 行为
- 本轮直接实现代码修改

## 5. 功能需求

### FR-001 Beacon 必须把 Markdown 作为需求冻结唯一 truth

冻结阶段 gate 不得以 fulltext machine mirror 作为 truth source。

### FR-002 Beacon 必须提供 Markdown strict parser contract

PRD、user-story、test-case 必须保持可被 deterministic parser 读取的结构。

### FR-003 Beacon 必须将冻结阶段 JSON 收缩为最小状态缓存

冻结阶段 JSON 不得复制 Markdown 全文，只能存储 hash、revision、status、diagnostics、transaction pointer。

### FR-004 Beacon 必须禁止 fulltext machine mirrors

PRD canonical JSON、requirement envelope、candidate ledger、QA matrix 等冻结阶段机器材料不得包含完整 Markdown 正文副本。

### FR-005 Beacon 必须保留 runtime evidence JSON

implement / QA / release 的进程、线程、session、trace、evidence、test result 仍使用 JSON。

### FR-006 Beacon 必须让 gate 从 Markdown 解析 truth

Material audit、requirement clarity、refreeze、implement preflight 必须以 Markdown truth 为第一读取源。

### FR-007 Beacon 必须用 hash 检测 Markdown truth drift

当 Markdown truth 改变但冻结 state 未刷新时，gate 必须阻断并回 `beacon-change`。

### FR-008 Beacon 必须提供 no silent cache fallback

当 Markdown 解析失败、cache 缺失、hash mismatch 或 refreeze status 不明时，gate 必须 fail closed。

## 6. 冻结交付物

- `docs/beacon/archive/v1.4.8/research/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/archive/v1.4.8/source-architecture/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/archive/v1.4.8/change/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/archive/v1.4.8/prd/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/archive/v1.4.8/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/archive/v1.4.8/qa/test-cases/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/archive/v1.4.8/release/checklist-v1.4.8-markdown-first-freeze-truth.md`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| Markdown 格式不严格 | gate 解析不稳定 | 冻结 strict parser contract 并 fail closed |
| 移除 fulltext mirror 后调试困难 | gate 输出信息变少 | diagnostics 保留 path、line、hash、reason_code |
| runtime JSON 被误删 | implement / QA / release evidence 丢失 | 明确 runtime JSON 保留 |
| cache 缺失被误认为不需要 | 静默放行 | missing cache / parse failure 必须阻断 |
| 旧版本大 JSON 兼容问题 | 历史材料读取不一致 | 新合同只约束 v1.4.8+ 新生成材料 |

## 8. 验收标准

- AC-001 Beacon treats Markdown PRD, user-story, test-case, research, execution, and release documents as the canonical freeze truth.
- AC-002 Beacon does not treat frozen-stage fulltext machine mirrors as canonical truth.
- AC-003 Beacon stores only minimal freeze state in requirement-stage JSON.
- AC-004 Beacon keeps implement, QA, release runtime evidence JSON.
- AC-005 Beacon parses AC and test-case coverage from Markdown truth before consulting cache.
- AC-006 Beacon blocks when Markdown parser fails.
- AC-007 Beacon blocks when Markdown baseline hash differs from frozen state.
- AC-008 Beacon blocks when refreeze transaction status is missing or ambiguous.
- AC-009 Beacon emits diagnostics with path, line or section, hash, reason_code, and repair route.
- AC-010 Beacon provides a migration boundary so historical fulltext JSON remains readable but new v1.4.8+ freeze artifacts stop duplicating full Markdown.

## 9. 成功指标

- 新冻结材料的 machine JSON 体积明显下降。
- Gate 仍能 fail closed。
- 人类审查只需要读 Markdown truth。
- Runtime evidence 仍能支持 implement / QA / release。
