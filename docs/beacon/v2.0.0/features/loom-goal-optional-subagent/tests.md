---
slug: loom-goal-optional-subagent
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-goal-optional-subagent/truth.md
---

# Tests: loom-goal-optional-subagent

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LOOM-SA-001 | TC-LOOM-SA-001 | contract | `python3 -m pytest tests/test_v200_loom_subagent.py::test_opt_in_default_off -q` | default no spawn |
| AC-LOOM-SA-002 | TC-LOOM-SA-002 | integration | `python3 -m pytest tests/test_v200_loom_subagent.py::test_plan_creates_worktree -q` | worktree created when opted in |
| AC-LOOM-SA-003 | TC-LOOM-SA-003 | unit | `python3 -m pytest tests/test_v200_loom_subagent.py::test_one_lake_one_satellite -q` | 1:1 |
| AC-LOOM-SA-004 | TC-LOOM-SA-004 | unit | `python3 -m pytest tests/test_v200_loom_subagent.py::test_respects_depends_on -q` | deps gate fan-out |
| AC-LOOM-SA-005 | TC-LOOM-SA-005 | negative | `python3 -m pytest tests/test_v200_loom_subagent.py::test_satellite_no_main_truth -q` | no truth write |
| AC-LOOM-SA-006 | TC-LOOM-SA-006 | unit | `python3 -m pytest tests/test_v200_loom_subagent.py::test_merge_to_star -q` | merge policy |
| AC-LOOM-SA-007 | TC-LOOM-SA-007 | integration | `python3 -m pytest tests/test_v200_loom_subagent.py::test_spawn_backend -q` | tmux or bridge |
| AC-LOOM-SA-008 | TC-LOOM-SA-008 | unit | `python3 -m pytest tests/test_v200_loom_subagent.py::test_fallback_reason -q` | explicit fallback |
| AC-LOOM-SA-009 | TC-LOOM-SA-009 | contract | `python3 -m pytest tests/test_v200_loom_subagent.py::test_omx_checklist_b1_b6 -q` | B1–B6 |
| AC-LOOM-SA-010 | TC-LOOM-SA-010 | contract | `python3 -m pytest tests/test_v200_loom_subagent.py::test_no_complete_from_fanout -q` | no self-cert |
| AC-LOOM-SA-011 | TC-LOOM-SA-011 | unit | `python3 -m pytest tests/test_v200_loom_subagent.py::test_execution_log_events -q` | jsonl events |
| AC-LOOM-SA-012 | TC-LOOM-SA-012 | contract | `python3 -m pytest tests/test_v200_loom_subagent.py::test_legal_illegal -q` | legal/illegal rows |

## Legal / Illegal

| TC ID | Assertion |
|-------|-----------|
| TC-LOOM-SA-LEGAL-01 | opt-in → planned → running → merging → done |
| TC-LOOM-SA-ILLEGAL-01 | fan-out cannot complete product goal without verifier |
| TC-LOOM-SA-ILLEGAL-02 | default run does not spawn |
