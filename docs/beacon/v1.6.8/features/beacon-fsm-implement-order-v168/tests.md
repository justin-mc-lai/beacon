---
slug: beacon-fsm-implement-order-v168
version: v1.6.8
status: frozen
revision_id: R1
---

# Tests: beacon-fsm-implement-order-v168

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-FIO-001 | TC-FSM_IM-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k fsm_implement` | admission |
| AC-FIO-002 | TC-FSM_IM-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | tasks_order |
| AC-FIO-003 | TC-FSM_IM-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | qa_negative |
| AC-FIO-004 | TC-FSM_IM-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | axis |
| AC-FIO-005 | TC-FSM_IM-005 | contract | `beacon goal axis validate -v v1.6.8 --program beacon-friction-closeout-v168` | escape |
| AC-V168-FC-001 | TC-FC-FSM_-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-FC-FSM_-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-FC-FSM_-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-004 | TC-FC-FSM_-S04 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-005 | TC-FC-FSM_-S05 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-006 | TC-FC-FSM_-S06 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-007 | TC-FC-FSM_-S07 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-008 | TC-FC-FSM_-S08 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
