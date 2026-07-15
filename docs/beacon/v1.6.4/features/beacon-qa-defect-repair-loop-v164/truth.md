---
slug: beacon-qa-defect-repair-loop-v164
version: v1.6.4
status: frozen
revision_id: R1
language: zh
change_reason: R1 — QA defect 修复回归闭环（复用 ROUTE_RECOMMENDATIONS + repair_route 字段 + 回归 QA 触发 + 闭环 evidence）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/truth.md
  user_story: docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/truth.md
  test_case: docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：QA Defect Repair Loop v1.6.4

## 概述

beacon qa 已有 `ROUTE_RECOMMENDATIONS`（qa_attribution.py）做单向 defect 路由（implementation_gap→implement, truth_drift→change, coverage_gap→test-case, execution_lapse→qa），但**缺修复后回归闭环**：defect 路由到 implement/change 后，修复完成无强制回归 QA 触发，闭环 evidence 链断裂。用户要求"及时修复业务 bug"——需完整 defect→修复→回归→闭环 管道。

本 feature 复用现有 `ROUTE_RECOMMENDATIONS` 路由表，补 `repair_route` / `defect_classification` 字段、修复后回归 QA 触发、闭环 evidence 链。

## User Intent（一行）

QA defect 路由修复后强制回归 QA，闭环 evidence 链可见，bug 及时闭环。

## User Intent Snapshot

- user_prompt: "及时修复业务 bug，QA 闭环"
- lake_or_ocean: 湖（海级程序已拆，本 feature 单点回归闭环，scope 清晰）
- scope_mode: brownfield_takeover（既有 ROUTE_RECOMMENDATIONS，补回归闭环）
- silent_scope_change_allowed: false
- program_ref: docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 4)
- depends_on: beacon-qa-coverage-confidence-chain-v164 + beacon-qa-business-state-machine-v164 (Phase 2/3, defect 来自各 QA 层 finding)

## User Decisions（locked）

- UD-001 复用现有路由：defect 分类用既有 `ROUTE_RECOMMENDATIONS`（不重定义 taxonomy）
- UD-002 回归强制：defect 修复后必须回归 QA（非可选），回归未跑 → release block
- UD-003 闭环 evidence：defect→修复→回归 三段 evidence 链必须完整（缺段 block）

## Problem Statement

1. `ROUTE_RECOMMENDATIONS` 是单向路由（QA→route），无修复后回归触发。
2. 无 `repair_route` / `defect_classification` 字段记录 defect 处置状态。
3. 修复后回归 QA 无强制（implement 修复后可直接进 release，跳过回归）。
4. 闭环 evidence 链断裂（defect 发现 + 修复 + 回归无串联证据）。

## Non-Goals

- 不重定义 defect taxonomy（复用既有 ROUTE_RECOMMENDATIONS，UD-001）。
- 不做置信度链（Phase 2）/ 状态机覆盖（Phase 3），本 feature 消费其 finding。
- 不实现 implement/change 本身（本 feature 只做路由 + 回归触发 + 闭环）。

## 受影响代码面

- `beacon/utils/qa_attribution.py`：扩展现有路由，增 `repair_route` / `defect_classification` 字段 + 回归触发。
- `beacon/utils/qa_acceptance.py`：闭环 evidence 链字段（defect→fix→regression 三段）。
- `beacon/utils/qa_feature.py`：defect finding 关联修复 + 回归状态。
- `tests/test_v164_qa_defect_repair_loop.py`：TC-DR-001..005。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | defect-classification | QA finding 复用既有 `ROUTE_RECOMMENDATIONS` 分类（implementation_gap / truth_drift / coverage_gap / execution_lapse / skill_defect / runner_admission_blocker / evidence_insufficient）；分类失败 → block（**Must**，UD-001） |
| AC-002 | repair-route-field | `qa_acceptance` 输出含 `repair_route`（目标 harness）+ `defect_classification`（family + reason_code）；projection 同步（**Must**） |
| AC-003 | route-rules | 路由规则生效：implementation_gap→beacon-implement, truth_drift→beacon-change, coverage_gap→beacon-test-case, execution_lapse→beacon-qa；RELEASE_BLOCKING_FAMILIES 强制 block release（**Must**） |
| AC-004 | regression-trigger | defect 修复后强制回归 QA 触发（`regression_required=True`）；回归未跑 → release block（reason_code `regression_skipped`）（**Must**，UD-002） |
| AC-005 | closure-evidence-chain | 闭环 evidence 链：defect 发现 → 修复 → 回归三段串联；缺段 → block（reason_code `repair_chain_broken`）；evidence 不被记为 full pass（**Must**，UD-003） |

## Deferral Ledger

| ID | 项 | user_decision |
|---|---|---|
| UD-001 | 复用既有 ROUTE_RECOMMENDATIONS | accepted |
| UD-002 | 回归强制 + release block | accepted（preamble §4） |
| UD-003 | 三段闭环 evidence | accepted（preamble §4） |
| UD-004 | 自动缺陷优先级排序 | accepted（延后，本 feature 仅分类不排序） |

## State Machine

```
[QA finding] --AC-001分类--> [defect family]
[defect family] --AC-002/003--> [repair_route -> harness]
[harness 修复] --AC-004--> [regression_required=True]
[回归 QA] --AC-005--> [闭环 evidence: defect->fix->regression]
   │ 缺段
   ▼
[repair_chain_broken block]
```

## Closed Questions

复用既有路由（UD-001）。回归强制（UD-002）。三段闭环（UD-003）。自动排序延后（UD-004）。

## Downstream Routes（post-freeze）

- `beacon-gen-implement`：实现 AC-001..005（字段 + 路由 + 回归触发 + 闭环链）。
- `beacon-eval-qa`：验证 defect→修复→回归闭环 + release block。
- 完成后 v1.6.4 QA 能力增强 4/5 phase 闭环（Phase 5 methodology 独立）。
