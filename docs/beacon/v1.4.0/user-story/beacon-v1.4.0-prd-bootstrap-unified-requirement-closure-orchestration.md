# User Story: Beacon v1.4.0 PRD bootstrap unified requirement closure orchestration

## Story Boundary

- version: `v1.4.0`
- feature: `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`
- status: `freeze-ready`
- upstream_prd: `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- current_revision: `R1`
- source_revision: `R0`

本故事线覆盖对 `beacon-prd-bootstrap` 的 post-freeze 补强：把它从 safe bootstrap initializer 提升成 unified requirement closure entry，但仍然保持 support surface，而不是新的主流程 stage。

## Diagram Truth

- `branch-flow`
  - `detect package state -> fill missing layer -> closure analysis -> verdict -> route`
  - `reverse-derived truth` 与 `drift repair` 必须单独分支
- `decision-priority`
  - `existing frozen truth > derived truth`
  - `drift repair > supplement convenience`
  - `freeze-ready evidence > one-shot automation desire`

## Story 1: 系统必须先识别当前 requirement package state

作为操作者，我希望 bootstrap 先知道当前缺哪层，而不是盲目重生所有文档。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | package-state-detection | 系统必须识别当前 requirement package state。 |
| AC-002 | empty-and-partial-supported | 系统必须支持 empty 与主要 partial package 状态。 |
| AC-003 | full-inconsistent-detected | full but inconsistent package 必须被识别为独立状态。 |
| AC-004 | state-visible | 输出必须向人类显式展示当前 package state。 |

## Story 2: 系统必须统一代理缺失层补齐

作为用户，我希望不用自己决定调用 `prd`、`user-story` 还是 `test-case`，而是让 bootstrap 根据当前状态自动补齐缺失层。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | missing-layer-routing | 系统必须根据 package state 路由到缺失层补齐。 |
| AC-102 | canonical-order-first | 默认必须优先走上游到下游的 canonical compile order。 |
| AC-103 | no-manual-subskill-selection | 操作者不应必须手动判断调用哪个 requirement 子 skill。 |
| AC-104 | canonical-writeback | 补齐结果必须写回 canonical docs tree。 |

## Story 3: reverse-derived truth 必须显式标记

作为 truth governance owner，我希望当系统从下游产物反推上游 truth 时，这件事被显式标记出来，而不是伪装成原生上游 truth。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | reverse-derived-marked | reverse-derived upstream truth 必须被显式标记。 |
| AC-202 | needs-review-marked | 这类 truth 必须同时标记 `needs_truth_review`。 |
| AC-203 | no-silent-promotion | reverse-derived truth 不得静默直接升格为高置信度 frozen truth。 |
| AC-204 | human-visible-risk | 输出必须把 reverse-derived 风险展示给人类。 |

## Story 4: drift package 必须进入 repair route，而不是静默重写

作为维护者，我希望当 PRD、story、test-case 互相冲突时，系统不要静默选择一方覆盖另一方，而是进入 drift repair。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | drift-digest | 系统必须输出 drift digest。 |
| AC-302 | affected-layers | drift digest 必须指出受影响层。 |
| AC-303 | repair-route | 系统必须给出 repair route，而不是静默重写。 |
| AC-304 | no-silent-truth-arbitration | 系统不得静默裁决冲突 truth。 |

## Story 5: 系统必须有 closure verdict 与 readiness verdict

作为产品 owner，我希望 unified entry 不只是“补完文档”，还要判断是否真的闭环，能否进入待实现。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | closure-verdict | 系统必须输出 formal closure verdict。 |
| AC-402 | readiness-verdict | 系统必须输出 readiness verdict。 |
| AC-403 | conditional-promotion | 只有在证据充分时才允许 promotion 到 `freeze_ready / implementation_pending`。 |
| AC-404 | no-unconditional-one-shot-freeze | 系统不得默认无条件 one-shot freeze。 |

## Story 6: 输出必须统一回答人类真正关心的问题

作为使用者，我希望 unified entry 的结果直接告诉我：当前状态、缺哪层、风险在哪、下一步做什么。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | state-summary | 输出必须总结当前 package state。 |
| AC-502 | missing-layer-summary | 输出必须说明缺失层或补齐层。 |
| AC-503 | verdict-summary | 输出必须清晰展示当前 verdict。 |
| AC-504 | next-command-summary | 输出必须给出建议下一步命令。 |

## Story 7: 整个能力必须继续保持 optional support surface 边界

作为 Beacon owner，我希望即使统一入口成立，也不能让它变成新的主流程 stage。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | support-surface-only | 该能力必须继续标记为 optional support surface。 |
| AC-602 | no-new-public-stage | 系统不得把它升级为新的 public primary stage。 |
| AC-603 | truth-structure-retained | `prd / user-story / test-case` 三层 truth 结构必须保留。 |
| AC-604 | global-boundary-compatible | 整个能力必须与 `global-boundaries` 保持兼容。 |

## Delivery Notes

- 这条 story 不是新开 lifecycle，而是对 `beacon-prd-bootstrap` 的 change/refreeze 补强。
- 真正新增的是 orchestrator 与 verdict layer，不是新的 truth tree。

## Freeze Notes

- 如果后续实现只是把 `prd-bootstrap` 改成“总是重生三件套”，那不算完成本 story。
- 只有同时具备：
  - package state detection
  - reverse-derived labeling
  - drift repair routing
  - conditional promotion
  才算符合本 story。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 13 |
| Status | freeze-ready-change-r1 |
| Created | 2026-05-06 |
| Change Scope | prd-bootstrap / unified-entry / partial-package / reverse-derived / drift-repair / verdict |
