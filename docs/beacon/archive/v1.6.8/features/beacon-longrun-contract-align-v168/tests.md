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
| AC-LCA-001 | TC-LCA-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k longrun_default` | primary |
| AC-LCA-002 | TC-LCA-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-LCA-003 | TC-LCA-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-LCA-004 | TC-LCA-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-LCA-005 | TC-LCA-005 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-V168-FC-001 | TC-LCA-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-LCA-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-LCA-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
