---
slug: beacon-qa-coverage-confidence-chain-v164
version: v1.6.4
status: frozen
revision_id: R1
language: zh
change_reason: R1 — qa 层间置信度传递链（unit→...→browser_e2e），层间 gap 可见 + 断链 block
source_revision_id: null
canonical_refs:
  prd: docs/beacon/archive/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/truth.md
  user_story: docs/beacon/archive/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/truth.md
  test_case: docs/beacon/archive/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：QA Coverage Confidence Chain v1.6.4

## 概述

beacon qa 有 9 个 non-browser 层 + 1 个 browser_e2e 层，但**层间无置信度传递**——unit pass 不代表 interface pass，interface pass 不代表 e2e pass，断链不可见。`build_qa_profile_completeness` 只统计每层 executed/skipped/blocked，不表达"上层置信度依赖下层覆盖"。

本 feature 引入 QA 层置信度传递模型：每层置信度依赖其下层覆盖，层间 gap 检测可见，断链 fail-closed block，避免"每层都 pass 但端到端断链"的假交付。

## User Intent（一行）

qa 层间置信度传递可见，断链 block，单例 pass 不被误当作端到端 pass。

## User Intent Snapshot

- user_prompt: "qa 从单例到端到端置信度真实有效，层间 gap 可见"
- lake_or_ocean: 湖（海级程序已拆，本 feature 单点置信度模型，scope 清晰）
- scope_mode: brownfield_takeover（既有 QA9 层级 + profile_completeness，做置信度链扩展）
- silent_scope_change_allowed: false
- program_ref: docs/beacon/archive/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 2)
- depends_on: beacon-qa-chrome-extension-e2e-v164 (Phase 1, browser_e2e 是链终点)

## User Decisions（locked）

- UD-001 链方向：置信度自下而上传递（unit → interface → ... → browser_e2e），下层 gap 削弱上层置信度（非反向）
- UD-002 断链处置：层间 gap → fail-closed block，不静默放行（preamble §4 不假交付）

## Problem Statement

1. `build_qa_profile_completeness` 只统计 executed/skipped/blocked/missing，无层间依赖表达。
2. `coverage.py` 有 story/ac/tc coverage metrics，但无层间传递模型（unit coverage 不影响 e2e 置信度计算）。
3. 断链不可见：unit pass + e2e skipped 时，profile 可能仍显示"complete"，掩盖 e2e 缺口。
4. 无 `confidence_chain` 字段记录每层置信度 + 依赖来源。

## Non-Goals

- 不重定义 QA9 层级（既有 9 层 + browser_e2e 不变）。
- 不做业务状态机覆盖（Phase 3 范围，状态覆盖是置信度输入之一）。
- 不做 defect 路由（Phase 4 范围）。
- 不做 runner 实现（Phase 1 范围）。

## 受影响代码面

- `beacon/utils/qa_acceptance.py`：`build_qa_profile_completeness` 增 `confidence_chain` 字段；新增层间依赖模型 + gap 检测。
- `beacon/utils/coverage.py`：层间置信度传递计算（下层 coverage 影响上层置信度）。
- `tests/test_v164_qa_confidence_chain.py`：TC-CC-001..005。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | chain-model | 定义 QA 层置信度传递模型：每层置信度 = 自身覆盖 ∩ 下层覆盖传递；链方向 unit→...→browser_e2e（**Must**，UD-001） |
| AC-002 | gap-detection | 层间 gap 检测：下层 skipped/missing/blocked 时，上层置信度被削弱并标记 `downstream_gap`（**Must**） |
| AC-003 | confidence-chain-field | `build_qa_profile_completeness` 输出含 `confidence_chain`（每层置信度 + 依赖来源 + gap 标记）；projection 同步（**Must**） |
| AC-004 | break-block | 断链 fail-closed：链终点（browser_e2e）缺失或任一依赖层 gap → profile `partial/blocked`，不显示 complete（**Must**，UD-002） |
| AC-005 | browser-e2e-integration | browser_e2e 作为链终点纳入置信度链；与 Phase 1 的 `playwright-extension` runner 集成（e2e 置信度依赖下层 non-browser 覆盖）（**Must**） |

## Deferral Ledger

| ID | 项 | user_decision |
|---|---|---|
| UD-001 | 链方向自下而上 | accepted |
| UD-002 | 断链 fail-closed block | accepted（preamble §4） |
| UD-003 | 状态机覆盖纳入置信度输入 | accepted（Phase 3 落地，本 feature 预留接口） |

## State Machine

```
[unit 覆盖] --传递--> [interface 置信度] --传递--> ... --传递--> [browser_e2e 置信度]
   │ gap                │ gap                       │ gap
   ▼                    ▼                          ▼
[downstream_gap 标记]                              [链终点缺失]
   └─────────────── 断链 → profile partial/blocked ─────────┘
```

## Closed Questions

链方向：自下而上（UD-001）。断链处置：block（UD-002）。状态机覆盖：Phase 3 预留接口（UD-003）。

## Downstream Routes（post-freeze）

- `beacon-gen-implement`：实现 AC-001..005（置信度模型 + gap 检测 + confidence_chain 字段 + 断链 block + e2e 集成）。
- `beacon-eval-qa`：验证断链 block + 置信度传递真实。
- Phase 3（state-machine）依赖本 feature 的 confidence_chain 接口。
