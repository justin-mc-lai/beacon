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
| AC-RPW-001 | TC-RELEAS-001 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q -k release_profile` | wire |
| AC-RPW-002 | TC-RELEAS-002 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | hotfix_min |
| AC-RPW-003 | TC-RELEAS-003 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | repair |
| AC-RPW-004 | TC-RELEAS-004 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | selfheal |
| AC-RPW-005 | TC-RELEAS-005 | contract | `beacon goal axis validate -v v1.6.8 --program beacon-friction-closeout-v168` | no_fake |
| AC-V168-FC-001 | TC-FC-RELE-S01 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-002 | TC-FC-RELE-S02 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-003 | TC-FC-RELE-S03 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-004 | TC-FC-RELE-S04 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-005 | TC-FC-RELE-S05 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-006 | TC-FC-RELE-S06 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-007 | TC-FC-RELE-S07 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
| AC-V168-FC-008 | TC-FC-RELE-S08 | contract | `python3 -m pytest tests/test_v168_friction_closeout.py -q` | shared |
