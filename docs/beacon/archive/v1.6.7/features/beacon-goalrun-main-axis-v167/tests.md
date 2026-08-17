---
slug: beacon-goalrun-main-axis-v167
version: v1.6.7
status: frozen
revision_id: R1
truth_ref: docs/beacon/archive/v1.6.7/features/beacon-goalrun-main-axis-v167/truth.md
---

# Tests: beacon-goalrun-main-axis-v167

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-AXIS-001 | TC-AXIS-001 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_axis_artifact_exists -q` | md exists + states |
| AC-AXIS-002 | TC-AXIS-002 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_mount_table_covers_lakes -q` | all lakes mounted |
| AC-AXIS-003 | TC-AXIS-003 | unit | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_change_triggers -q` | trigger map |
| AC-AXIS-004 | TC-AXIS-004 | unit | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_validate_fail_closed -q` | missing blocked |
| AC-AXIS-005 | TC-AXIS-005 | unit | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_done_when_domain -q` | domain_fsm_coverage |
| AC-AXIS-006 | TC-AXIS-006 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_no_submachine_complete -q` | illegal complete |
| AC-AXIS-007 | TC-AXIS-007 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_wave_order_section -q` | Wave present |
| AC-AXIS-008 | TC-AXIS-008 | unit | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_generate_machine_json -q` | projection |
| AC-AXIS-009 | TC-AXIS-009 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_q1_q6 -q` | checklist |
| AC-AXIS-010 | TC-AXIS-010 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_legal_illegal -q` | rows |
| AC-AXIS-011 | TC-AXIS-011 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_state_names_shared -q` | shared names |
| AC-AXIS-012 | TC-AXIS-012 | contract | `python3 -m pytest tests/test_v167_goalrun_main_axis.py::test_refreeze_note -q` | refreeze note |

## Legal / Illegal

| TC ID | Assertion |
|-------|-----------|
| TC-AXIS-LEGAL-01 | generate then validate pass |
| TC-AXIS-ILLEGAL-01 | validate fails if GoalRun states missing |
| TC-AXIS-ILLEGAL-02 | change trigger without regenerate blocked by policy API |
