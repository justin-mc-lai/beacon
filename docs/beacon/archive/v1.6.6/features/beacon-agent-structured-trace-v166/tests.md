---
slug: beacon-agent-structured-trace-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.6/features/beacon-agent-structured-trace-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Agent Structured Trace v1.6.6

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-TR-001 | contract | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_schema_accepts_valid_event -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Validator accepts valid `agent_trace.v1` line with all required fields |
| AC-001 | TC-TR-002 | contract | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_schema_rejects_invalid_event_type -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Invalid `event_type` fails with `reason_code=agent_trace_invalid_event_type` |
| AC-002 | TC-TR-003 | integration | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_append_events_on_governed_run -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Simulated governed run appends at least one of decision/failure/retry/output to `.beacon/traces/<run_id>.jsonl` |
| AC-003 | TC-TR-004 | contract | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_fail_closed_when_trace_missing -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Harness preflight blocks with `reason_code=agent_trace_missing` when trace cannot be opened |
| AC-004 | TC-TR-005 | integration | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_lifecycle_index_records_trace_pointer -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `workflow-lifecycle` index contains `trace_path` and `trace_event_count` for the run |
| AC-005 | TC-TR-006 | integration | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_loop_audit_agent_trace_coverage_signal -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `doctor loop-audit` JSON includes `agent_trace_coverage` with status pass/fail/missing |
| AC-007 | TC-TR-008 | contract | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_loop_layer_optional_field -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Valid `loop_layer` values accepted; invalid value fails with `reason_code=agent_trace_invalid_loop_layer` |
| AC-006 | TC-TR-007 | contract | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_golden_trace_normalization -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Golden fixture normalizes to stable JSON equal to reference payload |

## Verification Notes

- Test module `tests/test_v166_agent_structured_trace.py` is created in implement phase; tasks may note `BLOCKED:implement` until then.
- TC-TR-003/005/006 use `tmp_path` project roots; no live agent required.
- Golden fixture path: `tests/fixtures/agent_trace/golden-run.jsonl`.

## Must vs Should

| Priority | AC |
|----------|-----|
| Must | AC-001..007 |
| AC-007 | TC-TR-008 | contract | `python3 -m pytest tests/test_v166_agent_structured_trace.py::test_loop_layer_optional_field -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Valid `loop_layer` values accepted; invalid value fails with `reason_code=agent_trace_invalid_loop_layer` |
