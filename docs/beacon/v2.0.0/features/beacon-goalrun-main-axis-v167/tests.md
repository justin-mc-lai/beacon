---
slug: beacon-goalrun-main-axis-v167
version: v2.0.0
status: frozen
revision_id: R1-v2-sync
---

# Tests

| AC ID | TC ID | Command | Assertion |
|-------|-------|---------|-----------|
| AC-AXIS-V2-001 | TC-AXIS-V2-001 | `python3 -m pytest tests/test_v200_goalrun_main_axis.py::test_generate_v2 -q` | generate ok |
| AC-AXIS-V2-002 | TC-AXIS-V2-002 | `python3 -m pytest tests/test_v200_goalrun_main_axis.py::test_mounts_loom -q` | loom lakes listed |
| AC-AXIS-V2-003 | TC-AXIS-V2-003 | `python3 -m pytest tests/test_v200_goalrun_main_axis.py::test_subagent_trace_sections -q` | sections present |
| AC-AXIS-V2-004 | TC-AXIS-V2-004 | `python3 -m pytest tests/test_v200_goalrun_main_axis.py::test_validate_v2 -q` | validate ok |
| AC-AXIS-V2-005 | TC-AXIS-V2-005 | `python3 -m pytest tests/test_v200_goalrun_main_axis.py::test_wave0_to_3 -q` | Wave 0/2/3 |
| AC-AXIS-V2-006 | TC-AXIS-V2-006 | `python3 -m pytest tests/test_v200_goalrun_main_axis.py::test_triggers_shared -q` | shared triggers |
