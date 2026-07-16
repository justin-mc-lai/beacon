---
slug: beacon-loop-goal-closed-loop-orchestrator-v161
version: v1.6.1
status: frozen
revision_id: R1
language: zh
change_reason: v1.6.1 统一长任务入口 + program 外层 FSM + eval supplement（UD-001..007）
source_revision_id: v1.6.0-R10
canonical_refs:
  prd: docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md
  user_story: docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md
  test_case: docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: true
upstream_feature: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md
---

# 需求真相：Beacon Loop Goal Closed-Loop Orchestrator v1.6.1

## 概述

`beacon-loop-goal-closed-loop-orchestrator-v161` 在 **v1.6.0 frozen R10**（`beacon-loop-goal-closed-loop-orchestrator`）之上，交付 v1.6.1 **全量长任务闭环编排**：**单一公共入口** `beacon-loop goal`、**海级 program 外层 FSM**、**湖/海 scope 分类**、**opt-in Agent Eval supplement**；与 `beacon-harness-program-plan-v161` **R4** 及 `beacon-agent-eval-v161` 对接。

本 feature **不**新增 Beacon 主 lifecycle stage；**不**让 loop/runner 产出 formal QA/release verdict；**不** reopen v1.6.0 上游 frozen truth（新 AC 仅在本 v1.6.1 package）。

## User Intent（一行）

一句话 → 湖/海分类 →（海）program P0–P4 → 每湖 truth→generate→qa→release →（可选）eval supplement；操作者只记 **`beacon-loop goal`**。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | v1.6.1 统一长任务闭环：goal 单入口、海嵌入 program、湖直 delivery、eval 可选补充、pre-main 交付 |
| `lake_or_ocean` | **湖**（本 package）；运行时面向 **湖 \| 海** utterance |
| `scope_mode` | `full_parity` |
| 强度词 | 统一入口、煮干、冻结、program FSM、eval supplement |
| 非协商边界 | eval 不 gate qa/release；plan start 不替代 goal 长 FSM |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | Long-task public entry | **`beacon-loop goal "<utterance>"`**（薄委托 `beacon-run`） |
| UD-002 | Sea utterance | Default **embedded program P0–P4** then per-lake delivery |
| UD-003 | Lake utterance | **Skip program**；direct per-lake delivery |
| UD-004 | `beacon plan start` | **Scaffold + plan_mode only**；长 FSM 由 `goal` resume |
| UD-005 | Agent Eval | **Opt-in** `--eval-matrix` / `--eval-scorecard`；never gate qa/release |
| UD-006 | Change landing | **本 package R1** + **program plan R4** |
| UD-007 | Sea/lake ambiguous | **One** MCQ；写入 `intent-contract.json` 或 `program-manifest` |

## Upstream Dependency Matrix

| Upstream | 本 feature 依赖 |
|----------|----------------|
| `beacon-loop-goal-closed-loop-orchestrator` v1.6.0 **R10 frozen** | AC-031..AC-071、Delivery Loop FSM、`truth_freeze_gate`、spine、stop-when |
| `beacon-harness-program-plan-v161` R4 | `--mode program`、P0–P6、`program-run-state.json`、AC-PBP-027/029/030 |
| `beacon-agent-eval-v161` R2 | eval supplement 契约（`formal_verdict_authority=false`） |
| `beacon-pln-review-intent-parity-state-machine-v160` | intent/review 不变 |
| `beacon-truth-integrity-gates-v160` | per-lake / refreeze TIG |

## Command Contract

**Operator guide（人类读模型）**：`docs/beacon/archive/v1.6.1/execution/long-task-operator-guide.md`（TASK-LOOP-A03 / AC-PBP-027）。

**操作者单一公共入口（权威）**：

```bash
beacon-loop goal "<utterance>" [options]
# 薄委托 beacon-run；stdin / --prompt-file
```

**Program scaffold（非长 FSM 所有者）**：

```bash
beacon plan start "<utterance>" --program <slug> --mode auto|interactive|auto-detect
```

**Eval supplement（opt-in）**：

```bash
beacon-loop goal "<utterance>" --eval-matrix --eval-scorecard
```

| `--mode` | 行为 |
|----------|------|
| `delivery` | 湖路径或海路径下单湖 delivery（继承 v1.6.0 R10） |
| `program` | **海路径**：外层 ProgramPlanState P0–P6；P4 ack 后门控 spawn per-lake `delivery` |
| `execute-only` | frozen truth + `--feature`（继承上游） |
| `intent-only` / `review-only` | 继承上游 |

**湖/海**：`lake_or_ocean=湖` → 跳过 program 外层；`海` → `--mode program`（或 goal 自动升格）。低置信度 **一次** MCQ（UD-007）。

## v1.6.1 目标数据流

```text
utterance
  → intent capture + scope_classify（湖 | 海）
  → [海] program outer FSM P0–P4（program-run-state.json）
  → per-lake delivery（topo from feature-graph.json）
        beacon-run iteration + phase harness
        [opt-in] eval supplement（matrix/scorecard）
  → [海] program P6 when all lakes terminal
  → terminal_closed（Beacon evaluator only）
```

## State Model（v1.6.1 扩展）

### Scope axis

`utterance_received` → `scope_classified` → …

非法：`utterance_received` → `generate` 无 classify + freeze。

### Program outer（海，嵌套）

对齐 `ProgramPlanState`（见 program plan truth）：经 P4 ack 后进入 `program_delivery`，内层 per-lake 仍遵守上游 **AC-068** `truth_freeze_gate`。

### Eval supplement（opt-in）

非 lifecycle stage。Artifacts：`run-dir/eval-matrix.json`、`eval-scorecard.json`，必填 `formal_verdict_authority=false`。

## Parity Matrix（v1.6.1 delta）

| Capability | Target AC | Status |
|------------|-----------|--------|
| 统一 goal 入口 + 湖/海分类 | AC-072 | missing |
| program 外层 FSM | AC-073 | missing |
| eval supplement opt-in | AC-074 | missing |
| 海级 program E2E | AC-075 | missing |
| 上游 R10 worktree/spine/stop-when | AC-069..071 @ v1.6.0 | **frozen upstream** |

## Deferral Ledger

| deferral_id | capability | user_decision | recommended_route |
|-------------|------------|---------------|-------------------|
| D-LOOP-161-001 | eval live 默认进 loop | **rejected** | opt-in only |
| D-LOOP-161-002 | eval score gates qa | **rejected** | AC-AE-006 |
| D-LOOP-161-003 | AST full OSS inventory | **accepted defer** | PB-001 program plan |

## Delivery Phases

| Phase | 范围 | AC |
|-------|------|-----|
| A | 统一 goal + scope classify + delegate flags | AC-072 |
| B | `--mode program` 外层 FSM + P4 gate | AC-073 |
| C | eval supplement + spine refs | AC-074 |
| D | 海级 program E2E opt-in | AC-075 |

## Non-goals

- Reopen 或修改 v1.6.0 `beacon-loop-goal-closed-loop-orchestrator` frozen R10
- 替代 formal `beacon qa run` / release gate
- v2 Rust orchestrator / 独立 judge 服务

## 验收标准

| AC ID | Acceptance Criteria |
|-------|---------------------|
| AC-072 | **统一长任务入口 + 湖/海分类**：`beacon-loop goal "<utterance>"` 为操作者 **唯一** 长任务公共入口（薄委托 `beacon-run`）；支持 `--mode delivery|program`、`--program <slug>`、湖/海 classifier。`lake_or_ocean=湖` 跳过 program 外层；`海` 进入 `--mode program`。UD-007：低置信度 **一次** MCQ，写入 `intent-contract.json` 或 `program-manifest.md`。`beacon plan start` 仅 scaffold + `plan_mode`，**不** 替代 goal 续跑长 FSM。 |
| AC-073 | **program 外层 FSM**：`beacon-run --mode program`（经 goal 委托）实现 `ProgramPlanState` P0–P6；状态写入 `program-run-state.json`；P4 user ack **门控** per-lake delivery spawn；非法跳过 P4 须 block；内层遵守上游 AC-068。 |
| AC-074 | **opt-in eval supplement**：支持 `--eval-matrix` / `--eval-scorecard`；evaluate 阶段 supplement 调用 `beacon eval matrix|scorecard`；落盘 `eval-matrix.json`、`eval-scorecard.json`，必填 `formal_verdict_authority=false`。**禁止** 替代 `beacon qa run` 或 release gate；`spine show` 输出 eval refs（若存在）。 |
| AC-075 | **海级 program E2E（opt-in）**：`BEACON_RUN_E2E_PROGRAM=1` 下：海 utterance → program P0–P4（fixture）→ 单湖 truth frozen → generate checkpoint → 可选 eval supplement；formal verdict **仅** Beacon evaluator。 |

## Source Advisory

| Artifact | Role |
|----------|------|
| `docs/beacon/archive/v1.6.1/research/beacon-loop-goal-closed-loop-orchestrator.md` | promoted research（UD-001..007） |
| `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` | upstream frozen R10 |
| `docs/beacon/archive/v1.6.1/execution/long-task-operator-guide.md` | operator read model（goal vs plan start） |
| `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | program handoff R4 |

本文件为 v1.6.1 package-authoritative requirement truth（**R1**，pre-main 交付线）。
