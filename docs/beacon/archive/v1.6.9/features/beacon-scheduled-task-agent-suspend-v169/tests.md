---
slug: beacon-scheduled-task-agent-suspend-v169
version: v1.6.9
kind: tests
---

# Tests

| TC | AC | Command / assert |
|----|----|--------------------|
| TC-ST-001 | AC-ST-001 | create+list+get roundtrip |
| TC-ST-002 | AC-ST-002/010 | wake dry_run writes execution |
| TC-ST-003 | AC-ST-003/011 | suspend then wake skips |
| TC-ST-004 | AC-ST-004 | resume then wake runs |
| TC-ST-005 | AC-ST-005 | install-timer without confirm blocked |
| TC-ST-006 | AC-ST-008 | whitelist unchanged (no new public skill) |
| TC-ST-007 | AC-ST-012 | both feature packages exist |

Primary: `tests/test_v169_scheduled_task.py`
