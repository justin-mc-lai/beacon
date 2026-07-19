---
slug: beacon-runtime-install-truth-v168
version: v1.6.8
status: frozen
revision_id: R1
---

# Tests: beacon-runtime-install-truth-v168

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-RIT-001 | TC-RUNTIM-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k runtime_install` | diagnose |
| AC-RIT-002 | TC-RUNTIM-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | pin |
| AC-RIT-003 | TC-RUNTIM-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | drift |
| AC-RIT-004 | TC-RUNTIM-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | fleet |
| AC-RIT-005 | TC-RUNTIM-005 | contract | `beacon goal axis validate -v v1.6.8 --program beacon-friction-closeout-v168` | example |
| AC-V168-FC-001 | TC-FC-RUNT-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-FC-RUNT-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-FC-RUNT-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-004 | TC-FC-RUNT-S04 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-005 | TC-FC-RUNT-S05 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-006 | TC-FC-RUNT-S06 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-007 | TC-FC-RUNT-S07 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-008 | TC-FC-RUNT-S08 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
