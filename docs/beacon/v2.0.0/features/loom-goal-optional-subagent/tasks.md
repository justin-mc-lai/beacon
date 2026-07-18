---
slug: loom-goal-optional-subagent
version: v2.0.0
status: frozen
revision_id: R1
---

# Tasks: loom-goal-optional-subagent

- [ ] TASK-LOOM-SA-01 Wire goal --subagent / intent → execute parallel_plan
- [ ] TASK-LOOM-SA-02 Create satellite worktrees under .beacon/worktrees/satellite/<lake>
- [ ] TASK-LOOM-SA-03 Spawn via tmux or host bridge; write worker spec/result
- [ ] TASK-LOOM-SA-04 Enforce depends_on before fan-out
- [ ] TASK-LOOM-SA-05 Merge-to-star only; block main truth writes from satellite
- [ ] TASK-LOOM-SA-06 Fallback single_process + reason_code
- [ ] TASK-LOOM-SA-07 execution.jsonl events for spawn/merge
- [ ] TASK-LOOM-SA-08 OMX/OMC B1–B6 checklist tests
- [ ] TASK-LOOM-SA-09 tests/test_v200_loom_subagent.py
