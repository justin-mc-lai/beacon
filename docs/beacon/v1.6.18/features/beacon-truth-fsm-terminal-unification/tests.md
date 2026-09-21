---
slug: beacon-truth-fsm-terminal-unification
version: v1.6.18
materials_status: current
---

# Tests: beacon-truth-fsm-terminal-unification

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 -m pytest -q tests/test_v1610_truth_gen_template_and_gates.py -k own_fsm_gate --tb=no` | generated_scaffolds_pass_own_fsm_gate |
| TC-002 | AC-002 | `python3 -m pytest -q tests/test_v1610_truth_review_gate.py -k one_fsm_rule --tb=no` | review_and_freeze_one_rule |
| TC-003 | AC-003 | `python3 -m pytest -q tests/test_v1614_fsm_validate.py -k "undeclared_terminal or blank_transition_target" --tb=no` | structural_terminal_warn_and_blank_target_block |
| TC-004 | AC-004 | `python3 -m pytest -q tests/test_v1614_fsm_validate.py -k "illegal_prose or illegal_declared" --tb=no` | illegal_prose_not_machine_edge |
| TC-005 | AC-005 | `python3 -m pytest -q tests/test_v1614_fsm_validate.py -k "unrelated_mermaid or stale_projection" --tb=no` | projection_resync_without_collateral_write |
| TC-EXEC-CLI | AC-001 | `python3 -c "from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm; md='## FSM 五元组\n\n| State | Event | Guard | To | Action |\n|---|---|---|---|---|\n| a | go | ok | b | x |\n\n### invalid / illegal\n\n- illegal: a -> a\n'; assert validate_truth_fsm(parse_truth_fsm(md), truth_markdown=md)['blocked'] is False"` | structural_terminal_accepted_no_block |
| TC-EXEC-PYTEST | AC-005 | `python3 -m pytest -q tests/test_v1614_fsm_validate.py tests/test_v1610_truth_review_gate.py tests/test_v1610_truth_gen_template_and_gates.py --tb=no` | fsm_suite_green |

## Validation Note

TC-001..TC-005 map 1:1 to AC-001..AC-005; TC-EXEC-CLI/TC-EXEC-PYTEST are the exec-layer TCs required by the v1.6.10 Truth Review Gate Check C / exec-layer check.
