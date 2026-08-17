---
slug: beacon-goal-hard-stage-exit-gates-v169
version: v1.6.9
revision_id: R1
---

| AC | Command | Assertion |
|----|---------|-----------|
| AC-BG-001..009 | `pytest tests/test_v169_goal_hard_stage_exit_gates.py -q` | pass |
| AC-BG-010 | `pytest tests/test_v169_goal_implement_admission_hard_gate.py -q` | pass |
| AC-BG-006 | enforcement unit in hard stage suite | main blocked |
