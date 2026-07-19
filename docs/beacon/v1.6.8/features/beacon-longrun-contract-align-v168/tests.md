---
slug: beacon-longrun-contract-align-v168
version: v1.6.8
status: frozen
revision_id: R1
---

# Tests: beacon-longrun-contract-align-v168

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LCA-001 | TC-LONGRU-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k longrun_contract` | default |
| AC-LCA-002 | TC-LONGRU-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | opt_out |
| AC-LCA-003 | TC-LONGRU-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | no_env_gate |
| AC-LCA-004 | TC-LONGRU-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | bridge_doctor |
| AC-LCA-005 | TC-LONGRU-005 | contract | `beacon goal axis validate -v v1.6.8 --program beacon-friction-closeout-v168` | docs |
| AC-V168-FC-001 | TC-FC-LONG-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-FC-LONG-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-FC-LONG-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-004 | TC-FC-LONG-S04 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-005 | TC-FC-LONG-S05 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-006 | TC-FC-LONG-S06 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-007 | TC-FC-LONG-S07 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-008 | TC-FC-LONG-S08 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
