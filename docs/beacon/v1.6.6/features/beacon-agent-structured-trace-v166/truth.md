---
slug: beacon-agent-structured-trace-v166
version: v1.6.6
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Structured agent trace for loop observability (program Phase 1)
canonical_refs:
  truth: docs/beacon/v1.6.6/features/beacon-agent-structured-trace-v166/truth.md
  tests: docs/beacon/v1.6.6/features/beacon-agent-structured-trace-v166/tests.md
  tasks: docs/beacon/v1.6.6/features/beacon-agent-structured-trace-v166/tasks.md
  evidence: docs/beacon/v1.6.6/features/beacon-agent-structured-trace-v166/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
---

# Requirement Truth: Agent Structured Trace v1.6.6

## Overview

Beacon loop harness 当前只有 stage 级 `workflow-lifecycle` 事件，无法回放单次 agent iteration 内的决策、失败、重试与输出。Phase 2 stagnation detector 与 Phase 3 remediation 依赖可机器消费的 per-run trace。

本 feature 定义 `agent_trace.v1` schema，在 governed harness 入口写入 JSONL trace，并在 lifecycle index 与 loop-audit 中暴露 coverage 信号。

## User Intent（一行）

所有 governed harness Agent 的决策、失败、重试、输出必须结构化写入 JSONL trace，禁止仅靠 print 作为唯一运行证据。

## User Intent Snapshot

- user_prompt: "给所有 Agent 加结构化日志"（program Phase 1）
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
- silent_scope_change_allowed: false

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-TRACE-001 | Storage | v1.6.6 JSONL at `.beacon/traces/<run_id>.jsonl` + lifecycle index pointer; v2 `lifecycle_events` via projection rebuild |
| UD-TRACE-002 | Event types | `decision`, `failure`, `retry`, `output`, `tool_call`, `gate_verdict` |
| UD-TRACE-003 | Dual write | CLI `--json` summary and trace append; missing trace on governed write surfaces → fail-closed |
| UD-TRACE-004 | loop_layer field | Optional `loop_layer` (`coding` / `developer` / `realworld`) on trace events for Loop Engineering observability |

## Problem Statement

1. `workflow_memory` lifecycle events are stage-granular, not iteration-granular.
2. Operators cannot inspect agent decisions or retries without unstructured stdout.
3. `doctor loop-audit` has no `agent_trace_coverage` signal.
4. Phase 2 `beacon-loop-stagnation-detector-v166` has no canonical trace input.

## Non-Goals

- Stagnation detection rules (Phase 2).
- Runtime overlay remediation (Phase 3).
- Replacing `workflow-lifecycle.json` (projection-compatible only).
- v2 global SQLite as v1.6.6 write authority (defer projection rebuild).
- Logging full model payloads by default (use blob pointer + hash for large bodies).

## Affected Surfaces

- `beacon/utils/agent_trace.py` (new): schema, append, validate, resolve
- `beacon/utils/workflow_memory.py`: lifecycle index pointer to trace path
- `beacon/commands/doctor.py`: `loop-audit` signal `agent_trace_coverage`
- Harness write surfaces: implement preflight, qa run metadata, loop/run orchestration hooks
- `tests/test_v166_agent_structured_trace.py`
- `.beacon/traces/<run_id>.jsonl` (runtime blob)

## Trace Schema (`agent_trace.v1`)

Each JSONL line is one event. Required top-level fields:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | `agent_trace.v1` |
| `event_type` | enum | `decision` \| `failure` \| `retry` \| `output` \| `tool_call` \| `gate_verdict` |
| `run_id` | string | Governed run identifier |
| `timestamp` | string | ISO-8601 UTC |
| `iteration` | int | 0-based loop iteration when applicable |
| `reason_code` | string | Machine reason when failure/retry/gate |
| `summary` | string | Short human-readable summary (not raw dump) |
| `payload` | object | Event-specific structured body |

Optional: `loop_layer`, `feature_slug`, `harness`, `agent_backend`, `artifact_refs[]`.

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | schema | Validator accepts `agent_trace.v1` with required fields; invalid `event_type` → `reason_code=agent_trace_invalid_event_type` |
| AC-002 | append-events | Trace writer appends at least one of `decision`/`failure`/`retry`/`output` per governed run when harness executes an iteration |
| AC-003 | fail-closed | Governed harness write without trace path or append failure → block with `reason_code=agent_trace_missing` (no silent pass) |
| AC-004 | lifecycle-index | `workflow-lifecycle` index records `trace_path` + `trace_event_count` for the run |
| AC-005 | loop-audit-signal | `beacon doctor loop-audit --json` reports `agent_trace_coverage` as `pass`/`fail`/`missing` with findings |
| AC-006 | golden-fixture | Golden trace fixture resolves to stable normalized JSON (field order independent) for regression |
| AC-007 | loop-layer-field | Validator accepts optional `loop_layer` with governed values `coding` / `developer` / `realworld`; invalid value → `reason_code=agent_trace_invalid_loop_layer` |

## State Model

```text
run_start -> trace_open -> event_append* -> trace_close -> lifecycle_index_update
trace_missing_on_governed_write -> blocked:agent_trace_missing
invalid_event -> blocked:agent_trace_invalid_event_type
```

## Deferral Ledger

| ID | Item | user_decision |
|----|------|---------------|
| UD-TRACE-001 | JSONL first, v2 projection later | accepted (program UD) |
| UD-TRACE-004 | loop_layer optional reserve | accepted |
| D-004 | Cross-project trace in global db | accepted defer (v2) |

## Downstream Routes

- `beacon-gen-implement`: schema utility, harness hooks, loop-audit signal, tests.
- `beacon-eval-qa`: behavioral TC-TR-* matrix.
- Phase 2 `beacon-loop-stagnation-detector-v166` consumes this trace surface.
