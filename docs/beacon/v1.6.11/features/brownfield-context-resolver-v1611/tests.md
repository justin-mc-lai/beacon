---
slug: brownfield-context-resolver-v1611
version: v1.6.11
revision_id: R2
materials_status: current
---

# Tests: L1 Brownfield Context Resolver

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-CTX-001 | AC-CTX-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k context_envelope --tb=no` | envelope contains five baseline surfaces |
| TC-CTX-002 | AC-CTX-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k context_reverse_lookup --tb=no` | goal resolves code and test entries |
| TC-CTX-003 | AC-CTX-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k context_conflict --tb=no` | conflict enters awaiting_human |
| TC-CTX-004 | AC-CTX-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k context_stale --tb=no` | changed fingerprint invalidates downstream |
| TC-CTX-005 | AC-CTX-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k inherited_truth_contracts --tb=no` | all frozen parent contracts are resolved into the envelope and cannot disappear silently |
| TC-CTX-006 | AC-CTX-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k execution_authorities --tb=no` | subagent runtime, truth canonical, worktree governance and trace authority resolve or fail closed |
| TC-CTX-007 | AC-CTX-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k truth_fill_request_context --tb=no` | truth-fill-request.v1 binds utterance, version, four source hashes, R2, semantic compiler, host transport, Humanizer and PAC refs |
| TC-CTX-008 | AC-CTX-008 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k host_fill_fail_closed --tb=no` | missing/empty/conflicting host semantic input blocks instead of falling back to hollow templates |
| TC-CTX-ILLEGAL | AC-CTX-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k context_illegal_transition --tb=no` | illegal resolution without scan or decision_ref is rejected |
