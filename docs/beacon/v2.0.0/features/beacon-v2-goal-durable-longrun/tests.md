---
slug: beacon-v2-goal-durable-longrun
version: v2.0.0
status: frozen
revision_id: R3
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md
---

# Tests: v2 Goal Durable Long-Run (R3)

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-DLR-001 | TC-V2-DLR-001 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_parity_v167_fixture -q` | v1.6.7 durable fixture loads |
| AC-V2-DLR-002 | TC-V2-DLR-002 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_longrun_flag_attaches -q` | --longrun attaches; default does not |
| AC-V2-DLR-003 | TC-V2-DLR-003 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_skill_longrun_intent -q` | skill/docs 识别长跑意图 |
| AC-V2-DLR-004 | TC-V2-DLR-004 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_heartbeat_default_120 -q` | 120s default |
| AC-V2-DLR-005 | TC-V2-DLR-005 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_jsonl_append_only -q` | append-only log |
| AC-V2-DLR-006 | TC-V2-DLR-006 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_resume_pack_digest -q` | digest only |
| AC-V2-DLR-007 | TC-V2-DLR-007 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_interrupt_ne_blocked -q` | interrupt ≠ blocked |
| AC-V2-DLR-008 | TC-V2-DLR-008 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_driver_auto_requeue -q` | auto requeue after turn_ended |
| AC-V2-DLR-009 | TC-V2-DLR-009 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_tick_execute_no_auto_release -q` | no auto release |
| AC-V2-DLR-010 | TC-V2-DLR-010 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_complete_needs_verifier -q` | verifier required |
| AC-V2-DLR-011 | TC-V2-DLR-011 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_human_release -q` | human release |
| AC-V2-DLR-012 | TC-V2-DLR-012 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_budget_halt -q` | budget halt no complete |
| AC-V2-DLR-013 | TC-V2-DLR-013 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_rust_spine_owns_driver_contract -q` | spine owns driver contract |
| AC-V2-DLR-016 | TC-V2-DLR-016 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_tests_md_legal_illegal -q` | legal/illegal rows present |
| AC-V2-ST-001 | TC-V2-ST-001 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_steering_assets_exist -q` | fixtures + MUST_SECTIONS exist |
| AC-V2-ST-001 | TC-V2-ST-002 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_continuation_must_sections -q` | continuation covers MUST tags |
| AC-V2-ST-002 | TC-V2-ST-003 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_inject_bundle_order -q` | steering before digest before next_action |
| AC-V2-ST-003 | TC-V2-ST-004 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_objective_as_data_language -q` | user-provided data wording present |
| AC-V2-ST-004 | TC-V2-ST-005 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_no_self_complete_language -q` | no verifier-bypass complete language |
| AC-V2-ST-005 | TC-V2-ST-006 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_blocked_audit_three_turns -q` | ≥3 goal turns blocked audit |
| AC-V2-ST-006 | TC-V2-ST-007 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_budget_limit_wrap_up_inject -q` | halt_budget uses budget_limit template |
| AC-V2-ST-007 | TC-V2-ST-008 | unit | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_objective_updated_inject -q` | objective edit → objective_updated |
| AC-V2-ST-008 | TC-V2-ST-009 | contract | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_truth_lists_st_acs -q` | truth lists AC-V2-ST-001..008 |

## Legal walk coverage

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-V2-DLR-008 | TC-V2-DLR-LEGAL-01 | legal walk | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_legal_longrun_to_verifier -q` | longrun → turns → awaiting_verifier |
| AC-V2-DLR-008 | TC-V2-DLR-LEGAL-02 | legal walk | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_legal_context_full_requeue -q` | context full → requeue digest |
| AC-V2-ST-002 | TC-V2-ST-LEGAL-01 | legal walk | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_legal_steering_requeue_bundle -q` | requeue inject full bundle |

## Illegal transition coverage

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-V2-DLR-010 | TC-V2-DLR-ILLEGAL-01 | illegal | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_illegal_complete_without_verifier -q` | no complete without verifier |
| AC-V2-DLR-011 | TC-V2-DLR-ILLEGAL-02 | illegal | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_illegal_auto_release -q` | no auto release |
| AC-V2-DLR-012 | TC-V2-DLR-ILLEGAL-03 | illegal | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_illegal_budget_complete -q` | budget must not complete |
| AC-V2-ST-002 | TC-V2-ST-ILLEGAL-01 | illegal | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_illegal_digest_only_requeue -q` | digest-only requeue forbidden when steering required |
| AC-V2-ST-004 | TC-V2-ST-ILLEGAL-02 | illegal | `python3 -m pytest tests/test_v200_goal_durable_longrun.py::test_illegal_steering_self_complete -q` | steering must not encourage verifier bypass |
