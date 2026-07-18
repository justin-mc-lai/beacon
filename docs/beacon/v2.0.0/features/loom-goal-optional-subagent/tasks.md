---
slug: loom-goal-optional-subagent
version: v2.0.0
status: frozen
revision_id: R1
---

# Tasks: loom-goal-optional-subagent

- [x] TASK-LOOM-SA-01 Wire goal --subagent / intent → execute parallel_plan
- [x] TASK-LOOM-SA-02 Create satellite worktrees under .beacon/worktrees/satellite/<lake>
- [x] TASK-LOOM-SA-03 Spawn via tmux or host bridge; write worker spec/result
- [x] TASK-LOOM-SA-04 Enforce depends_on before fan-out
- [x] TASK-LOOM-SA-05 Merge-to-star only; block main truth writes from satellite
- [x] TASK-LOOM-SA-06 Fallback single_process + reason_code
- [x] TASK-LOOM-SA-07 execution.jsonl events for spawn/merge
- [x] TASK-LOOM-SA-08 OMX/OMC B1–B6 checklist tests
- [x] TASK-LOOM-SA-09 tests/test_v200_loom_subagent.py


## Implementation note

2026-07-18 Product Goal pgr-51a763f2a691: Python parity + contract tests shipped (test_v200_*). Engine reuses v1.6.7 modules with v2 version support; Loom brand dual-install; subagent opt-in execute; driver→agent_trace hook; `beacon goal trace`.
