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
| AC-FIO-001 | TC-FIO-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k fsm_implement` | primary |
| AC-FIO-002 | TC-FIO-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-FIO-003 | TC-FIO-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-FIO-004 | TC-FIO-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-FIO-005 | TC-FIO-005 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-V168-FC-001 | TC-FIO-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-FIO-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-FIO-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
