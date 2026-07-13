---
slug: beacon-loop-token-budget-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-loop-token-budget-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Token Budget v1.6.5

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-TB-001 | contract | `python3 -m pytest tests/test_v165_loop_token_budget.py::test_registry_token_cost_fields_are_consumed -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Budget utility reads token_cost and daily_cap from registry entries. |
| AC-002 | TC-TB-002 | contract | `python3 -m pytest tests/test_v165_loop_token_budget.py::test_budget_ledger_appends_run_record -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Ledger append writes pattern id, run id, estimated/actual tokens, date, and source. |
| AC-003 | TC-TB-003 | contract | `python3 -m pytest tests/test_v165_loop_token_budget.py::test_daily_totals_per_pattern_and_project -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Daily totals are calculated per pattern and overall project. |
| AC-004 | TC-TB-004 | cli | `python3 -m pytest tests/test_v165_loop_token_budget.py::test_status_loop_budget_json -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Status command reports totals, caps, remaining budget, and state. |
| AC-005 | TC-TB-005 | contract | `python3 -m pytest tests/test_v165_loop_token_budget.py::test_unattended_preflight_blocks_when_cap_exceeded -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Unattended preflight blocks with `loop_budget_exceeded` when cap is exceeded. |
| AC-006 | TC-TB-006 | contract | `python3 -m pytest tests/test_v165_loop_token_budget.py::test_kill_switch_blocks_automated_loops -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Pause-all file blocks automated loops with `loop_kill_switch_active`. |

## Verification Notes

- Tests use temporary ledgers and do not write to the user's real budget ledger.
- Manual report-only behavior must remain available even when blocked.
