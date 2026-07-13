---
slug: beacon-harness-remediation-sandbox-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-harness-remediation-sandbox-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Harness Remediation Sandbox v1.6.6

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-RM-001 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_create_sandbox_returns_path -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `create_sandbox` creates isolated directory under governed worktree |
| AC-002 | TC-RM-002 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_apply_overlay_writes_patch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `apply_overlay` writes runtime patch to sandbox without touching canonical skill |
| AC-003 | TC-RM-003 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_eval_pass_returns_remediated -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Valid overlay eval returns `status=remediated` with all eval checks passing |
| AC-004 | TC-RM-004 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_eval_fail_triggers_rollback -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Failed eval triggers rollback and returns `status=rollback` |
| AC-005 | TC-RM-005 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_no_truth_write_during_overlay -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Overlay execution does not modify canonical truth files |
| AC-006 | TC-RM-006 | integration | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_sandbox_consumes_stagnation_report -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Sandbox accepts Phase 2 stagnation report as trigger input |
| AC-007 | TC-RM-007 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_remediation_report_schema -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Report matches `remediation-report.v1` schema |
| AC-008 | TC-RM-008 | contract | `python3 -m pytest tests/test_v166_remediation_sandbox.py::test_human_review_required_on_pass -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Eval pass sets `human_review_required=true` |

## Verification Notes

- Test module `tests/test_v166_remediation_sandbox.py` is created in implement phase.
- All tests use `tmp_path` worktree roots; no live governed worktree required.
- Upstream modules (stagnation_detector, workspace_admission) are consumed read-only.

## Must vs Should

| Priority | AC |
|----------|-----|
| Must | AC-001..008 |
