---
slug: beacon-release-profile-wiring-v168
version: v1.6.8
status: frozen
revision_id: R1
---

# Tests: beacon-release-profile-wiring-v168

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-RPW-001 | TC-RPW-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k release_profile` | primary |
| AC-RPW-002 | TC-RPW-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-RPW-003 | TC-RPW-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-RPW-004 | TC-RPW-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-RPW-005 | TC-RPW-005 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | suite |
| AC-V168-FC-001 | TC-RPW-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-RPW-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-RPW-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
