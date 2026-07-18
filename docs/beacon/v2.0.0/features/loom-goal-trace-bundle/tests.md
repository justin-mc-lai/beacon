---
slug: loom-goal-trace-bundle
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-goal-trace-bundle/truth.md
---

# Tests: loom-goal-trace-bundle

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LOOM-TR-001 | TC-LOOM-TR-001 | integration | `python3 -m pytest tests/test_v200_loom_trace.py::test_driver_writes_trace -q` | turn → jsonl |
| AC-LOOM-TR-002 | TC-LOOM-TR-002 | unit | `python3 -m pytest tests/test_v200_loom_trace.py::test_trace_path -q` | path layout |
| AC-LOOM-TR-003 | TC-LOOM-TR-003 | unit | `python3 -m pytest tests/test_v200_loom_trace.py::test_event_types -q` | v1 schema |
| AC-LOOM-TR-004 | TC-LOOM-TR-004 | contract | `python3 -m pytest tests/test_v200_loom_trace.py::test_cli_trace_aggregate -q` | aggregate |
| AC-LOOM-TR-005 | TC-LOOM-TR-005 | negative | `python3 -m pytest tests/test_v200_loom_trace.py::test_no_full_chat -q` | no chat body |
| AC-LOOM-TR-006 | TC-LOOM-TR-006 | unit | `python3 -m pytest tests/test_v200_loom_trace.py::test_verbose_path_only -q` | path refs |
| AC-LOOM-TR-007 | TC-LOOM-TR-007 | unit | `python3 -m pytest tests/test_v200_loom_trace.py::test_dual_logs -q` | both logs |
| AC-LOOM-TR-008 | TC-LOOM-TR-008 | contract | `python3 -m pytest tests/test_v200_loom_trace.py::test_resume_digest -q` | digest |
| AC-LOOM-TR-009 | TC-LOOM-TR-009 | unit | `python3 -m pytest tests/test_v200_loom_trace.py::test_index_update -q` | index |
| AC-LOOM-TR-010 | TC-LOOM-TR-010 | contract | `python3 -m pytest tests/test_v200_loom_trace.py::test_legal_illegal -q` | rows |

## Legal / Illegal

| TC ID | Assertion |
|-------|-----------|
| TC-LOOM-TR-LEGAL-01 | longrun turn writes tool_call+output |
| TC-LOOM-TR-ILLEGAL-01 | full chat cannot be authority |
