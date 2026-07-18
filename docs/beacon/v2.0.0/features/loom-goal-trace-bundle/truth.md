---
slug: loom-goal-trace-bundle
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-18: wire AgentDriver to agent_trace; aggregate goal trace CLI"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-goal-trace-bundle/truth.md
  tests: docs/beacon/v2.0.0/features/loom-goal-trace-bundle/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-goal-trace-bundle/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-goal-trace-bundle/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
ux_required: false
design_deferral: "CLI observability; no product marketing UI"
---

# Requirement Truth: Loom Goal Trace Bundle (R1)

## Overview

闭合排查缺口：

| 通道 | 今日 | 目标 |
|------|------|------|
| execution.jsonl | goal durable **有** | 保持权威进度 |
| agent_trace.v1 | 模块有；**goal/driver 默认不写** | **driver 每 turn 写入** |
| 统一 CLI | 无 | `loom goal trace` / compat `beacon goal trace` |

**原则**：chat 全文仍非权威；trace 记 decision/tool_call/failure/output；verbose 仅路径引用。

## User Intent

长跑 goal 出问题能查：编排事件 + agent 轮次轨迹，不用只靠宿主 session。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-TR-001 | Default | driver turn **默认** append agent_trace（tool_call + exit/output/failure） |
| UD-LOOM-TR-002 | Authority | resume-pack digest **仍是** 续跑权威；trace 为排查面 |
| UD-LOOM-TR-003 | No full chat | 禁止默认把完整 chat/jsonl body 写入权威 |
| UD-LOOM-TR-004 | Verbose | `--trace-verbose` 可记录 prompt **文件路径** 引用 |
| UD-LOOM-TR-005 | CLI | `goal trace --run-id` 聚合 execution + traces + driver |
| UD-LOOM-TR-006 | Schema | 沿用 `agent_trace.v1` 事件类型 |
| UD-LOOM-TR-007 | Compat | beacon goal 与 loom goal 同 CLI 子命令 |

## Event types（Must）

`decision` | `failure` | `retry` | `output` | `tool_call` | `gate_verdict`

Driver 最少：每 turn `tool_call`（spawn）+ `output`/`failure`（exit）。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LOOM-TR-001 | wire | AgentDriver 每 turn 写 agent_trace（**Must**） |
| AC-LOOM-TR-002 | path | `.beacon/traces/<run_id>.jsonl` 或 loom 隔离等价路径（**Must**） |
| AC-LOOM-TR-003 | types | 事件类型符合 agent_trace.v1（**Must**） |
| AC-LOOM-TR-004 | cli | `goal trace --run-id` 聚合输出（**Must**） |
| AC-LOOM-TR-005 | no-chat-auth | 默认不含 full chat body（**Must**） |
| AC-LOOM-TR-006 | verbose | verbose 仅路径引用（**Must**） |
| AC-LOOM-TR-007 | dual | 与 execution.jsonl 并存不互相覆盖（**Must**） |
| AC-LOOM-TR-008 | resume | resume-pack 仍 digest-only（**Must**） |
| AC-LOOM-TR-009 | index | lifecycle run_traces 索引更新（**Should**） |
| AC-LOOM-TR-010 | legal-illegal | tests 含 legal/illegal（**Must**） |

## Illegal

| ID | Illegal |
|----|---------|
| I-LOOM-TR-001 | 用 full chat 替代 resume-pack 权威 |
| I-LOOM-TR-002 | 截断/覆写 execution.jsonl 冒充 trace |
| I-LOOM-TR-003 | 无 turn 却宣称 trace complete |

## Non-Goals

- 重建完整 LLM 可观测 SaaS
- 默认落盘全部 prompt/completion 正文

## Dependencies

- loom-brand-surface
- beacon-v2-goal-durable-longrun / v1.6.7 goal_agent_driver + agent_trace
- beacon/utils/agent_trace.py
- beacon/utils/goal_agent_driver.py
