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
| AC-RIT-001 | TC-RIT-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k runtime_install` | primary |
| AC-RIT-002 | TC-RIT-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-RIT-003 | TC-RIT-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-RIT-004 | TC-RIT-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-RIT-005 | TC-RIT-005 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-V168-FC-001 | TC-RIT-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-RIT-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-RIT-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
