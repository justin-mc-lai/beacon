---
slug: beacon-host-subagent-lifecycle-keyword-v168
version: v1.6.8
---

# Tests

| AC | TC | Command / assertion |
|----|-----|---------------------|
| AC-SA-KW-001 | TC-001 | pytest keyword off |
| AC-SA-KW-002 | TC-002 | global on → pack_default |
| AC-SA-KW-003 | TC-003 | research pack |
| AC-SA-KW-004 | TC-004 | review pack |
| AC-SA-KW-005 | TC-005 | qa pack |
| AC-SA-KW-006 | TC-006 | implement pack |
| AC-SA-KW-007 | TC-007 | negate / --no-subagent |
| AC-SA-KW-008 | TC-008 | 并行 only → host false |
| AC-SA-ST-001 | TC-009 | default single_thread plan |
| AC-SA-BD-001 | TC-010 | cannot_complete_goal |
| AC-SA-BD-002 | TC-011 | public entry still beacon-goal only in skill text |
| AC-SA-IN-001 | TC-012 | install pack writes 6 files |
| AC-SA-VR-001 | TC-013 | verify --require-agents |
| AC-SA-EX-001 | TC-014 | examples exist |
| AC-SA-LM-001 | TC-015 | v2 mirror truth exists |
| AC-SA-SC-001 | TC-016 | score dimensions helper present |

Primary suite: `tests/test_v168_host_subagent_keyword.py`
