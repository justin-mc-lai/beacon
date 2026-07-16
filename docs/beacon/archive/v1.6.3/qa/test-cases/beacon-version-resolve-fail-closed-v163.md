# Test Cases: beacon-version-resolve-fail-closed-v163

## Overview

**Feature**: beacon-version-resolve-fail-closed-v163
**Test Type**: ALL
**Version**: v1.6.3
**Generated**: 2026-06-25 17:23
**Requested Mode**: auto
**Effective Mode**: markdown
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/.machine/qa/beacon-version-resolve-fail-closed-v163.ac-test-matrix.json
**QA9 Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/.machine/qa/beacon-version-resolve-fail-closed-v163.qa9-matrix.json
**Story Scenario Map JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/.machine/qa/beacon-version-resolve-fail-closed-v163.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-VR-001 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_no_hardcoded_v161_fallback -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | project_hooks.py:543 区域无 v1.6.1 硬编码字面量作 fallback | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-001.json` |
| AC-002 | TC-VR-002 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_eval_version_resolves_docs_version -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | version=auto/空时 eval_version 解析为 docs 实际版本而非 v1.6.1 | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-002.json` |
| AC-003 | TC-VR-003 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_hook_payload_has_drift_fields -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | post-release hook payload 含 runtime_version/docs_version/drift 字段 | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-003.json` |
| AC-004 | TC-VR-004 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_resolve_failure_fail_closed -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | resolve_target_version 抛异常时 hook block 且 reason_code 含 version_resolve_failed | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-004.json` |
| AC-005 | TC-VR-005 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_agent_eval_uses_resolved_version -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | is_live_runner_admitted 运行时用 resolve 版本，不依赖硬编码默认 | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-005.json` |
| AC-006 | TC-VR-006 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_no_regression_normal_scenario -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime==docs 正常场景 hook 不误 block | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-006.json` |
| AC-007 | TC-VR-007 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_drift_legitimate_not_blocked -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime≠docs 时 drift=true 但 status 不因 drift 而 block | `.beacon/evidence/test-results/beacon-version-resolve-fail-closed-v163/{run_id}/TC-VR-007.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-VR-001 | Pending | from AC-001 |
| TC-VR-002 | Pending | from AC-002 |
| TC-VR-003 | Pending | from AC-003 |
| TC-VR-004 | Pending | from AC-004 |
| TC-VR-005 | Pending | from AC-005 |
| TC-VR-006 | Pending | from AC-006 |
| TC-VR-007 | Pending | from AC-007 |
