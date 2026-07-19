---
slug: loom-run-agent-stop-when-external
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19 option2: freeze W1-W5 kernel closure lakes under program loom-kernel-closure-w1w5-v200"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-run-agent-stop-when-external/truth.md
  tests: docs/beacon/v2.0.0/features/loom-run-agent-stop-when-external/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-run-agent-stop-when-external/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-run-agent-stop-when-external/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json
parent_kernel: beacon-v2-rust-kernel-redesign
upstream_acs: ["AC-105", "AC-106"]
wave: W2
priority: P0
ux_required: false
design_deferral: "kernel/CLI; no product marketing UI"
display_name: "Loom Run Agent + External Stop-When"
brand: Loom
---

# Requirement Truth: run CLI agent + stop_when 外部校验 (W2)

## 人话

长跑可停可验：loom run --agent；禁止仅 agent 自报 stop。

本湖是 Loom（Beacon 进化品牌）内核补齐的一部分；**不**把生产 `beacon` 默认切走。

## Overview

| Wave | Priority | Upstream AC |
|------|----------|-------------|
| W2 | P0 | AC-105, AC-106 |

Depends on: loom-git-worktree-implement-harness

## User Intent

长跑可停可验：loom run --agent；禁止仅 agent 自报 stop。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-W2-001 | cli | loom run --agent codex|claude|acp:*|subprocess |
| UD-LOOM-W2-002 | no_daemon | loop 在 CLI 进程内；SIGINT graceful |
| UD-LOOM-W2-003 | maker_ne_checker | 禁止仅 stop_signal 终止 |
| UD-LOOM-W2-004 | external_check | 每轮后 gate exit0 / --stop-check-cmd / evaluator |
| UD-LOOM-W2-005 | worktree_bind | 可绑定 W1 admitted cwd |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-105 | run-cli | loom run --agent 映射 AgentBackend；进程内 loop；checkpoint/resume/SIGINT；无 daemon（Must） |
| AC-106 | stop-external | agent stop_signal alone → stop_when_unverified 并继续；外部检查通过才可停（Must） |
| AC-LOOM-W2-001 | agents | 至少 subprocess + 一种 agent 映射可测（Must） |
| AC-LOOM-W2-002 | sigint | SIGINT → graceful stop + checkpoint（Must） |
| AC-LOOM-W2-003 | legal-illegal | legal external stop + illegal self-stop（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-W2-001 | 仅 agent stop_signal 导致 loop 终止 |
| I-W2-002 | daemon 化 run |
| I-W2-003 | orchestrator 输出 release/qa pass verdict |

## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
