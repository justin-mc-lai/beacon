---
slug: beacon-freeze-integrity-drift-repair-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复冻结流程校验器自身 4 处漂移（dogfooding P0-3 冻结时暴露）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Freeze Integrity Drift Repair v1.6.3

## 概述

`beacon-freeze-integrity-drift-repair-v163` 修复 Beacon 冻结流程校验器自身的 4 处漂移。这些漂移在 dogfooding 冻结 `beacon-gate-truth-model-alignment-v163` 时暴露——**免疫系统（truth integrity gate）自身与 package-authoritative 模型不一致**，导致正确写的 truth 包被误报、需用 workaround（降级 contract 层、改文件名、塞 v1）才能冻结。若不修，后续每个 feature 冻结都会反复踩坑。

**P0 交付（Must）：**

1. **parser_contract 单一源** — `truth_map.py:28 TRUTH_PACKAGE_CONTRACT="beacon-feature-package-v2"`（resolver 对 v1.6.3+ 声明 v2）与 `feature_package.py:21 PARSER_CONTRACT="beacon-feature-package-v1"`（validator `:448` 只认 v1）不一致。同一文件 `feature_package.py:534` 还引用了 v2 常量。修复：validator 接受 resolver 声明的契约版本（v1 与 v2 都合法），消除"resolver 说 v2、validator 要 v1"的分裂。
2. **forbidden field 词边界匹配** — `feature_package.py:490` 用 `field in evidence_lower` 子串匹配，导致测试文件名含 `gate_truth` 子串（如 `test_v163_gate_truth_model_alignment.py`）被误判 `evidence_forbidden_gate_truth_field`。修复：改为字段级/词边界匹配，只在 evidence 实际把 forbidden field 当作 authority 字段使用时才报。
3. **hard markers 含 pytest + integration 不自动软** — `truth_integrity.py:60` `_HARD_TEST_MARKERS_RE` 缺 `pytest`（只认 cargo/beacon/pnpm/npm test/BLOCKED），导致纯 pytest 集成测试行被 `:316 soft_test_assertion` 误报。修复：hard markers 增加 `pytest`；Layer=integration 行在有真实 hard command 时不判软。
4. **校验错误自描述** — `feature_package.py:495 evidence_authority_table_missing` 与 `:500 evidence_invalid_authority` 报错不指明合法值与所需列，无法 action。修复：error message/diagnostics 含 `allowed_authorities` 与所需 `surface/authority` 列提示。

**不**改变 authority 白名单语义；**不**放宽 forbidden field 真实违规的拦截；**不**新增 lifecycle stage。

## User Intent（一行）

冻结流程校验器与 package-authoritative 模型对齐：resolver 声明的契约版本被 validator 接受、forbidden field 用词边界匹配、pytest 是 hard marker、校验错误自描述，让正确 truth 包无需 workaround 即可冻结。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | 冻结 P0-3 时被自家校验器拦 4 次，需修免疫系统自身漂移，否则每个 feature 冻结都踩坑 |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`validator_self_alignment`** |
| 强度词 | 单一源、词边界、hard marker、自描述、不放宽 |
| 非协商边界 | 真实 forbidden field 违规**仍**拦截；authority 白名单语义**不**改；v1 包向后兼容 |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | parser_contract 单一源 | validator 接受 resolver 声明的契约版本；v1 与 v2 都合法；未知版本仍 `parser_contract_mismatch` |
| UD-002 | forbidden field 匹配 | 词边界/字段级匹配；evidence 中路径或文件名含子串**不**触发；仅 authority 字段实际使用 forbidden 名才报 |
| UD-003 | hard markers | `_HARD_TEST_MARKERS_RE` 增加 `pytest`；Layer=integration 行有 hard command 时不判 `soft_test_assertion` |
| UD-004 | 错误自描述 | `evidence_authority_table_missing` / `evidence_invalid_authority` diagnostics 含 `allowed_authorities` 与所需列名 |
| UD-005 | 向后兼容 | 已冻结的 v1 包（v1.6.2 及更早 feature 包）修复后仍 pass |
| UD-006 | 实现位置 | `beacon/utils/feature_package.py` + `beacon/utils/truth_integrity.py` + `beacon/utils/truth_map.py` |
| UD-007 | 不放宽 | 真实 forbidden field 违规、真实 weak-assertion（无 hard command 的 integration 行）仍 block |

## Problem Statement

| 现象 | 根因 |
|------|------|
| v1.6.3 feature 包写 `parser_contract: v2` 被 `parser_contract_mismatch` 拦 | resolver 声明 v2，validator 只认 v1 |
| 测试文件名含 `gate_truth` 被 `evidence_forbidden_gate_truth_field` 拦 | 子串匹配误伤 |
| Layer=integration + pytest 行被 `soft_test_assertion` 拦 | hard markers 缺 pytest |
| authority 报错无法 action | 错误不指明合法值 |

## Non-Goals

- 重构 feature_package.py / truth_integrity.py god-file（另开技术债）
- 改 authority 白名单成员
- 改 forbidden field 列表
- 修复 P0-1/P0-2/P0-3（另开 feature 包；P0-3 已冻结）

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/feature_package.py:21,448` | `PARSER_CONTRACT=v1`，`!= PARSER_CONTRACT` 即报 | 接受 resolver 声明的 v1/v2 |
| `beacon/utils/feature_package.py:490` | `field in evidence_lower` 子串 | 词边界/字段级 |
| `beacon/utils/feature_package.py:495,500` | 错误无合法值提示 | diagnostics 含 `allowed_authorities` + 所需列 |
| `beacon/utils/truth_integrity.py:60` | hard markers 缺 pytest | 增加 `pytest` |
| `beacon/utils/truth_integrity.py:316` | integration cell 即判软 | 有 hard command 时不判 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | parser-contract-single-source | feature 包 `parser_contract` 为 resolver 声明版本（v1 或 v2）时通过；仅未知版本报 `parser_contract_mismatch`（**Must**） |
| AC-002 | forbidden-field-word-boundary | evidence 含 `gate_truth` 子串（路径/文件名）**不**触发 `evidence_forbidden_gate_truth_field`；authority 字段实际用 forbidden 名仍报（**Must**） |
| AC-003 | pytest-hard-marker | tests.md 行 Layer=integration + `pytest` command 不被 `soft_test_assertion` 标记；`_HARD_TEST_MARKERS_RE` 含 `pytest`（**Must**） |
| AC-004 | error-self-describing | `evidence_authority_table_missing` 与 `evidence_invalid_authority` 的 diagnostics 含 `allowed_authorities` 与所需 `surface/authority` 列（**Must**） |
| AC-005 | backward-compat-v1 | 已冻结 v1.6.2 feature 包修复后仍 pass validation（**Must**） |
| AC-006 | no-regression-p03 | 已冻结的 `beacon-gate-truth-model-alignment-v163` 包修复后仍 pass validation（**Must**） |
| AC-007 | no-real-violation-relax | 真实 forbidden field 违规（authority=source_of_truth）与真实 weak-assertion（无 hard command 的 integration 行）仍 block（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | feature_package.py / truth_integrity.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | authority 白名单与 forbidden field 列表的外部化配置 | 另开 feature |
| DEF-003 | P0-1/P0-2/P0-3 | 另开/已开 feature 包 |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | validator 接受 v1+v2，不强制全迁 v2（UD-001，向后兼容） |
| OQ-002 | forbidden field 用词边界，不删 "gate_truth"（UD-002） |
| OQ-003 | pytest 加 hard markers，integration 不自动软（UD-003） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
