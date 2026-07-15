---
program_slug: beacon-loop-meta-remediation-v166
version: v1.6.6
plan_mode: interactive
scope_mode: full_parity
program_phase: P1
---

# Module Map — Loop Meta-Remediation

## 第一性原理

根本问题：**Beacon loop 在重复失败时只有 reason code 和静态 catalog，没有可机器消费的 trace → 检测 → 自动 remediation 链。**

| 缺口 | 根因 | 最小可验证单元 |
|------|------|----------------|
| 决策/失败不可回放 | lifecycle 只有 stage 级事件，无 per-iteration agent trace | Phase A：trace schema + 写入 |
| 停滞不可检测 | `infinite-fix-loop` 是文档 catalog，非运行时 detector | Phase B：deterministic stagnation rules |
| 停滞只会「再试」 | 无 overlay remediation + sandbox eval + rollback | Phase C：remediation FSM |

## 源能力 → Beacon 映射

| 模块 | 用户步骤 | Beacon 落点 | 新/扩 |
|------|----------|-------------|-------|
| **M1 Agent Trace** | Step 1 结构化日志 | `.beacon/traces/<run_id>.jsonl` + lifecycle index + `spine artifacts` | 新 |
| **M2 Stagnation Detector** | Step 2 Meta-Agent 读日志 | governor skill + `.beacon/state/stagnation/` | 新 |
| **M3 Remediation Sandbox** | Step 3 改写 + 沙盒 + 回滚 | `.beacon/runtime-overlays/` + workspace admit + eval subset | 新 |

## 上游消费（v1.6.5，不重复造）

| v1.6.5 模块 | 本 program 消费方式 |
|-------------|---------------------|
| `loop-patterns/registry.yaml` | 每 pattern 增 `stagnation_policy`（Phase B 扩展字段） |
| `execution/loop-failure-modes.md` | 增 `stagnation-plateau` 等运行时模式（Phase B） |
| `loop/budget-ledger.json` | Phase B `token_plateau` 信号输入 |
| workspace pool lease | Phase C 沙盒 worktree |
| `doctor loop-audit` | 增 `agent_trace_coverage` signal（Phase A） |

## v2 对齐面（defer 到 projection，非 v1.6.6 blocker）

| v2 AC | v1.6.6 行为对齐 |
|-------|-----------------|
| AC-106 stop_when maker≠checker | Phase C 沙盒 eval 强制 |
| AC-107 Developer Feedback checkpoint | 并行能力；本 program 是机器 overlay，不替代人注入 |
| AC-108 loop_layer 可观测 | Phase A trace 含 `loop_layer` 字段预留 |

## 明确 Out of Scope（deferral）

- 自动改 canonical `skills/beacon/*.md`（UD-REMED-001 rejected）
- 自动改 `features/*/truth.md`（route change/refreeze only）
- 跨项目 Meta-Agent 学习（v2 global `beacon.db`）
- 替代 v2 orchestrator P2 实现（v1.6.6 先 Python/JSONL 路径）
