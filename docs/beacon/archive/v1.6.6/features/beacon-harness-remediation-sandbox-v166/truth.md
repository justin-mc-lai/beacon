---
slug: beacon-harness-remediation-sandbox-v166
version: v1.6.6
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Runtime overlay remediation sandbox with eval and auto-rollback (program Phase 3)
canonical_refs:
  truth: docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/truth.md
  tests: docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/tests.md
  tasks: docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/tasks.md
  evidence: docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
---

# Requirement Truth: Harness Remediation Sandbox v1.6.6

## Overview

Beacon loop harness 已有 structured agent trace (Phase 1) 和 stagnation detector (Phase 2)。Phase 2 输出 stagnation report 识别停滞模式，但缺少 **受控的 remediation 执行环境**——在 governed worktree 内运行 runtime overlay，eval 修复效果，失败时自动回滚。

本 feature 定义 `remediation-sandbox` governor utility，消费 stagnation report，在 governed worktree 内创建隔离 sandbox，执行 runtime overlay，评估结果，并在 eval 失败时自动回滚 overlay。禁止自动写入 canonical skill（D-002 rejected）。

## User Intent（一行）

Governor 能在 governed worktree 内隔离执行 runtime overlay 修复停滞问题，eval 修复效果，失败时自动回滚，不自动修改 canonical skill。

## User Intent Snapshot

- user_prompt: "Governor 能自己试着修一下"（program Phase 3）
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/archive/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
- silent_scope_change_allowed: false

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-REMED-001 | Canonical skill boundary | 只写 runtime overlay；不自动写入 canonical skill 文件 |
| UD-REMED-002 | Tests scope | tests.md subset + stop when maker ≠ checker；不做完整 QA 替代 |
| UD-REMED-003 | Rollback trigger | Eval fail → auto rollback overlay；eval pass → surface report for human review |

## Problem Statement

1. Phase 2 stagnation report 输出 finding 但无执行 remediation 的受控环境。
2. 直接在 canonical worktree 修改有高风险（破坏 truth-on-main 原则）。
3. Workspace pool lease (v1.6.5) 提供了 worktree 管理能力但无 overlay 执行层。
4. 修复尝试缺乏自动回滚保护。
5. Eval 结果缺乏机器可消费的 report。

## Non-Goals

- 自动写入 canonical skill 文件（D-002 rejected）。
- 替代 human QA verdict（UD-REMED-002）。
- 修改 requirement truth（harness boundary: evaluator 不改 truth）。
- 跨 project remediation（v2 scope）。
- 概率模型或 ML-based remediation generation（保持 deterministic overlay）。
- 直接 commit 到 main（truth-on-main 保护）。

## Affected Surfaces

- `beacon/utils/remediation_sandbox.py` (new): create_sandbox, apply_overlay, eval_overlay, rollback_overlay, build_remediation_report
- `beacon/commands/doctor.py`: `remediation` signal in loop-audit (read-only status)
- `beacon/utils/workspace_admission.py`: read-only consumer (pool lease)
- `beacon/utils/stagnation_detector.py`: read-only consumer (stagnation report)
- `tests/test_v166_remediation_sandbox.py` (new)
- `.beacon/worktrees/remediation-<run_id>/` (runtime sandbox path)

## Remediation Model

### Overlay Lifecycle

```text
stagnation_report → create_sandbox (governed worktree)
                  → apply_overlay (runtime patch)
                  → eval_overlay (run smoke test / subset)
                  → pass: surface_remediation_report (human review)
                  → fail: rollback_overlay (restore clean state)
```

### Overlay Types

| Overlay Type | Trigger | Description |
|-------------|---------|-------------|
| `retry-with-backoff` | repeat_failure | Wrap failing operation with exponential backoff + max retries |
| `skip-and-continue` | repeat_labor | Skip redundant iteration, advance to next step |
| `break-on-plateau` | plateau | Insert explicit break + human gate when plateau detected |

### Eval Criteria

| Eval Check | Description |
|------------|-------------|
| `smoke_test_pass` | Overlay does not break existing test subset |
| `stagnation_resolved` | Re-run stagnation detector on patched trace → clean |
| `no_truth_write` | Overlay did not write to canonical truth files |
| `rollback_clean` | Rollback restores worktree to pre-overlay state |

### Report Schema

```json
{
  "schema_version": "remediation-report.v1",
  "run_id": "<run_id>",
  "stagnation_ref": "<stagnation_report_run_id>",
  "overlay_type": "retry-with-backoff|skip-and-continue|break-on-plateau",
  "sandbox_path": "<worktree_path>",
  "status": "remediated|rollback|blocked",
  "eval": {
    "smoke_test_pass": true,
    "stagnation_resolved": true,
    "no_truth_write": true,
    "rollback_clean": true
  },
  "findings": [],
  "human_review_required": true
}
```

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | sandbox-create | `create_sandbox` 在 governed worktree 内创建隔离目录，返回 sandbox_path |
| AC-002 | overlay-apply | `apply_overlay` 写入 runtime patch 到 sandbox 目录，不修改 canonical skill |
| AC-003 | eval-pass | 给定有效 overlay，eval 返回 `status=remediated` 且所有 eval checks pass |
| AC-004 | eval-fail-rollback | 给定无效 overlay，eval 返回 `status=rollback`，sandbox 恢复到 pre-overlay 状态 |
| AC-005 | no-truth-write | Overlay 执行后 canonical truth 文件未被修改 |
| AC-006 | stagnation-consumed | Sandbox 消费 Phase 2 stagnation report 作为输入 trigger |
| AC-007 | report-schema | Remediation report 符合 `remediation-report.v1` schema |
| AC-008 | human-review | Eval pass → `human_review_required=true`，不自动进入 release |

## State Model

```text
stagnation_report_received -> sandbox_created -> overlay_applied
                                                -> eval_running
                                                   -> eval_pass -> report_surfaced (human_review)
                                                   -> eval_fail -> overlay_rolled_back -> report_surfaced (rollback)
canonical_truth_touched -> blocked:remediation_truth_write_violation
```

## Deferral Ledger

| ID | Item | user_decision |
|----|------|---------------|
| UD-REMED-001 | Runtime overlay only | accepted (program UD) |
| UD-REMED-002 | Tests subset scope | accepted |
| D-002 | Auto canonical skill rewrite | rejected |
| D-005 | Replace human feedback | accepted parallel (human review always required) |

## Downstream Routes

- `beacon-gen-implement`: sandbox utility, overlay lifecycle, eval harness, tests.
- `beacon-eval-qa`: behavioral TC-RM-* matrix.
- `beacon-eval-release`: human review gate before release verdict.
