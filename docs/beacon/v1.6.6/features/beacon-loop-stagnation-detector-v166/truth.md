---
slug: beacon-loop-stagnation-detector-v166
version: v1.6.6
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Deterministic stagnation detection over agent trace (program Phase 2)
canonical_refs:
  truth: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/truth.md
  tests: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/tests.md
  tasks: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/tasks.md
  evidence: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
---

# Requirement Truth: Loop Stagnation Detector v1.6.6

## Overview

Beacon loop harness 已有 pattern registry (v1.6.5)、failure catalog (v1.6.5)、token budget (v1.6.5) 和 structured agent trace (v1.6.6 Phase 1)。但缺少一个 **governor** 层面的分析器，能够确定性识别 trace 中的停滞模式（重复失败、重复劳动、plateau），并向 operator 输出可路由的 finding。

本 feature 定义 `stagnation-detector` governor utility，读取 agent trace JSONL，交叉 pattern registry 与 failure catalog，产出 stagnation report 供 governor decision surface 消费。

## User Intent（一行）

Governor 能从 agent trace 中自动检测重复失败、重复劳动和 plateau 三类停滞模式，输出机器可消费的 stagnation report，不修改 trace 或 runtime state。

## User Intent Snapshot

- user_prompt: "Governor 能看出 Agent 一直在原地打转"（program Phase 2）
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
- silent_scope_change_allowed: false

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-STAG-001 | Governor surface | 只读分析器，不修改 trace/runtime state；输出 report 供 governor 消费 |
| UD-STAG-002 | Detection determinism | 同一 trace 输入 + 同一 window → 同一 report；禁止概率模型 |
| UD-STAG-003 | Scope | 3 类模式：repeat_failure, repeat_labor, plateau；不扩展到 trend/prediction |

## Problem Statement

1. Operators 无法快速识别 agent 陷入 repeat failure 循环。
2. Pattern registry (v1.6.5) 定义了模式模板但无运行时 detector 消费 trace 事件。
3. Failure catalog (v1.6.5) 记录了失败模式但无跨 run 聚合视图。
4. Token budget (v1.6.5) 只限流不检测停滞质量。
5. Phase 3 `beacon-harness-remediation-sandbox-v166` 需要 stagnation 信号作为 remediation trigger。

## Non-Goals

- Remediation 执行（Phase 3 scope）。
- 概率模型或 ML-based prediction（违反 UD-STAG-002 determinism）。
- 跨 project 停滞聚合（v2 scope）。
- 修改 agent trace 或 runtime state。
- 替代 pattern registry / failure catalog / token budget 的校验职责。
- 自动触发 skill rewrite（D-002 rejected）。

## Affected Surfaces

- `beacon/utils/stagnation_detector.py` (new): detect, classify, report
- `beacon/commands/doctor.py`: `loop-audit` stagnation signal
- `beacon/utils/agent_trace.py`: read-only consumer
- `beacon/utils/loop_patterns.py`: read-only consumer
- `beacon/utils/loop_failure_catalog.py`: read-only consumer
- `beacon/utils/loop_budget.py`: read-only consumer
- `tests/test_v166_stagnation_detector.py` (new)

## Stagnation Model

### Repeat Failure Detection

在同一 trace 或同一 pattern 窗口内，若 `failure` 事件的 `reason_code` 在 N 次连续出现中出现 M 次（M ≥ threshold），判定为 repeat failure。

| Parameter | Default | Description |
|-----------|---------|-------------|
| `window_size` | 5 | 滑动窗口大小（最近 N 个事件） |
| `repeat_threshold` | 3 | 窗口内相同 reason_code 出现次数阈值 |
| `event_type` | `failure` | 检测的事件类型 |

### Repeat Labor Detection

在同一 trace 内，若相同 `(feature_slug, event_type, summary_prefix)` 组合在连续 iterations 中重复出现超过阈值，判定为重复劳动。

| Parameter | Default | Description |
|-----------|---------|-------------|
| `labor_window` | 4 | 滑动窗口大小 |
| `labor_threshold` | 3 | 窗口内相同 labor fingerprint 出现次数阈值 |
| `summary_prefix_len` | 20 | summary 前缀长度用于模糊匹配 |

### Plateau Detection

当 trace 中连续 `output` 事件的 `iteration` 递增但 `reason_code` 始终为空且 summary 相似度高于阈值，判定为 plateau（看似在前进但无实质进展）。

| Parameter | Default | Description |
|-----------|---------|-------------|
| `plateau_min_events` | 3 | 最少连续事件数 |
| `plateau_summary_similarity` | 0.8 | summary 相似度阈值（Jaccard） |

### Report Schema

```json
{
  "schema_version": "stagnation-report.v1",
  "run_id": "<run_id>",
  "detected_at": "<iso-8601>",
  "status": "stagnant|clean",
  "findings": [
    {
      "stagnation_type": "repeat_failure|repeat_labor|plateau",
      "reason_code": "<machine_reason>",
      "severity": "S1|S2|S3",
      "window_events": 5,
      "matched_count": 3,
      "pattern_ref": "<upstream_pattern_id_or_empty>",
      "failure_ref": "<upstream_failure_mode_id_or_empty>",
      "recommendation": "<route_hint>"
    }
  ],
  "upstream_signals": {
    "pattern_registry_status": "pass|fail|warn",
    "failure_catalog_status": "pass|fail|warn",
    "token_budget_status": "ok|blocked"
  }
}
```

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | repeat-failure | 给定包含 3+ 相同 `reason_code` 的 failure trace，detector 返回 `stagnation_type=repeat_failure` finding |
| AC-002 | repeat-labor | 给定包含 3+ 相同 `(feature_slug, summary_prefix)` 的 iteration trace，detector 返回 `stagnation_type=repeat_labor` finding |
| AC-003 | plateau | 给定 3+ 连续 output 事件（iteration 递增、reason_code 空、summary 相似），detector 返回 `stagnation_type=plateau` finding |
| AC-004 | clean-trace | 给定无停滞模式的 trace，detector 返回 `status=clean`，findings 为空 |
| AC-005 | upstream-correlation | Finding 包含 `pattern_ref` 和 `failure_ref` 字段，交叉 pattern registry 和 failure catalog |
| AC-006 | determinism | 同一 trace + 同一参数 → 同一 report（无随机、无时间依赖） |
| AC-007 | doctor-signal | `beacon doctor loop-audit --json` 包含 `stagnation_detection` signal |
| AC-008 | report-schema | Report 输出符合 `stagnation-report.v1` schema |

## State Model

```text
trace_read -> classify_events -> detect_repeat_failure
                              -> detect_repeat_labor
                              -> detect_plateau
         -> correlate_upstream (pattern_registry, failure_catalog, token_budget)
         -> build_report -> stagnation_report.v1
```

## Deferral Ledger

| ID | Item | user_decision |
|----|------|---------------|
| UD-STAG-001 | Governor read-only surface | accepted (program UD) |
| UD-STAG-003 | 3 stagnation types only | accepted |
| D-002 | Auto canonical skill rewrite | rejected |
| D-004 | Cross-project stagnation aggregation | accepted defer (v2) |

## Downstream Routes

- `beacon-gen-implement`: stagnation detector utility, doctor signal integration, tests.
- `beacon-eval-qa`: behavioral TC-ST-* matrix.
- Phase 3 `beacon-harness-remediation-sandbox-v166` consumes stagnation report as remediation trigger.
