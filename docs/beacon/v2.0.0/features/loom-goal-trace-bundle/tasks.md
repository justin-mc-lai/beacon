---
slug: loom-goal-trace-bundle
version: v2.0.0
status: frozen
revision_id: R1
---

# Tasks: loom-goal-trace-bundle

- [x] TASK-LOOM-TR-01 Hook goal_agent_driver turns → agent_trace append
- [x] TASK-LOOM-TR-02 CLI `goal trace --run-id` aggregate
- [x] TASK-LOOM-TR-03 --trace-verbose path refs only
- [x] TASK-LOOM-TR-04 Keep execution.jsonl append-only dual channel
- [x] TASK-LOOM-TR-05 Update run_traces index
- [x] TASK-LOOM-TR-06 tests/test_v200_loom_trace.py


## Implementation note

2026-07-18 Product Goal pgr-51a763f2a691: Python parity + contract tests shipped (test_v200_*). Engine reuses v1.6.7 modules with v2 version support; Loom brand dual-install; subagent opt-in execute; driver→agent_trace hook; `beacon goal trace`.
