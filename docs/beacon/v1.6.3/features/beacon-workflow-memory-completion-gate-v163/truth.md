---
slug: beacon-workflow-memory-completion-gate-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复 workflow memory completion truth 缺失时软放行（P0-2 免疫系统修复）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Workflow Memory Completion Gate v1.6.3

## 概述

`beacon-workflow-memory-completion-gate-v163` 修复 Beacon 免疫系统的 P0-2 漂移：workflow memory completion truth 缺失时**软放行**（warn 不 block），违反 anti-inertia「completion truth 缺失应 fail-closed」原则。

**根因：**

`beacon/utils/workflow_memory.py:1268-1286` 的 `workflow_memory_transaction_contract` 在两种情况下返回 `status: "warn" / blocked: False`：

1. `target_run_id=None`（`:1268`，无匹配 run）
2. run 存在但 `items` 为空（`:1278`，有 run 却无 transaction record）

而 `gate.py:1062` 只在 `status=="fail"` 时 block——`warn` 不 block。**后果**：有 run 却缺 completion transaction record 时，release gate 放行，等于把"没记录完成"当成"完成"。`beacon status` 也因此报 `closure_complete: false / all stages missing / terminal unknown` 的软失效。

**P0 交付（Must）：**

1. **区分 no-run vs run-without-transaction** — `target_run_id=None`（无 run，fresh/初始化）保持 informational warn；run 存在但无 transaction record → fail-closed。
2. **completion truth 缺失 fail-closed** — 有 run 却无 transaction record 时返回 `status: "fail" / blocked: True`，reason_code `workflow_memory_transaction_missing`，gate 据此 block。
3. **status 自描述** — `warn`（无 run）与 `fail`（有 run 无 transaction）的 reason_code 区分，便于诊断"无 run"vs"run 损坏"。

**不**改变 `failed_transaction`/`transaction_drift`/`pass` 的现有语义；**不**让 fresh project（真无 run）误 block；**不**新增 lifecycle stage。

## User Intent（一行）

有 run 却缺 completion transaction record 时 fail-closed 阻断 release，区分"无 run"（warn）与"run 无完成记录"（fail），让 completion truth 缺失不再静默放行。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | workflow_memory_transaction_contract 缺 transaction 时 warn 不 block，completion truth 缺失应 fail-closed |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`completion_truth_fail_closed`** |
| 强度词 | fail-closed、区分、不静默放行、completion truth |
| 非协商边界 | `failed_transaction`/`drift`/`pass` 语义**不**改；fresh project 无 run **不**误 block |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | no-run 语义 | `target_run_id=None` → `status: warn / blocked: False`，reason_code `workflow_memory_no_run_resolved`（informational，不 block） |
| UD-002 | run-without-transaction | run 存在但 `items` 为空 → `status: fail / blocked: True`，reason_code `workflow_memory_transaction_missing` |
| UD-003 | gate 行为 | gate.py:1062 已对 `fail` block；UD-002 使其生效（有 run 无 transaction 时 block） |
| UD-004 | 不改现有语义 | `failed_transaction`→fail、`drift`→fail、metadata/checksum ok→pass 均不变 |
| UD-005 | 实现位置 | `beacon/utils/workflow_memory.py:1260-1286 workflow_memory_transaction_contract` |
| UD-006 | status 报告 | `beacon status` 的 `memory_transaction` 反映新 reason_code，warn/fail 可区分 |

## Problem Statement

| 现象 | 根因 |
|------|------|
| 有 run 缺 transaction record 时 release gate 放行 | `:1278` warn 不 block，gate 只看 fail |
| `beacon status` 报 closure false / stages missing / terminal unknown 软失效 | `:1268` warn 软放行 |
| "无 run"与"run 损坏"无法区分 | 两者同 reason_code `workflow_memory_transaction_missing` |

## Non-Goals

- 改 `failed_transaction` / `transaction_drift` / `pass` 语义
- 改 `resolve_workflow_run_id` 内部逻辑
- 修复 P0-1（已修）/ P0-3（已修）
- 重构 workflow_memory.py god-file

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/workflow_memory.py:1268-1276` | `target_run_id=None` → warn `workflow_memory_transaction_missing` | warn `workflow_memory_no_run_resolved` |
| `beacon/utils/workflow_memory.py:1278-1286` | run 无 items → warn `workflow_memory_transaction_missing` | **fail** `workflow_memory_transaction_missing` (blocked: True) |
| `beacon/commands/gate.py:1062` | 仅 `fail` block | 不变（UD-002 使其生效） |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | no-run-warn | `target_run_id=None`（无 run）→ `status: warn / blocked: False`，reason_code `workflow_memory_no_run_resolved`（**Must**） |
| AC-002 | run-without-tx-fail | run 存在但无 transaction record → `status: fail / blocked: True`，reason_code `workflow_memory_transaction_missing`（**Must**） |
| AC-003 | gate-blocks-on-missing | 有 run 无 transaction 时 gate check release 对应 issue `blocked: True`（**Must**） |
| AC-004 | fresh-project-not-blocked | 真无 run 的 fresh project 不因本修复误 block release gate（**Must**） |
| AC-005 | existing-semantics-preserved | `failed_transaction`→fail、`drift`→fail、ok→pass 语义不变（**Must**） |
| AC-006 | status-distinguishes | `beacon status` 的 `memory_transaction` 在无 run vs 有 run 无 transaction 时 reason_code 不同（**Must**） |
| AC-007 | no-regression-pass | 有 run 且 transaction ok 时仍 `status: pass / blocked: False`（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | workflow_memory.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | fresh project 无 run 的 onboarding 引导 | 另开 feature |
| DEF-003 | P0-1/P0-3 | 已修 |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | no-run 保持 warn 不 block（UD-001，fresh project 不误伤） |
| OQ-002 | run-without-transaction fail-closed（UD-002，completion truth 缺失阻断） |
| OQ-003 | 现有 fail/pass 语义不改（UD-004） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
