---
slug: beacon-goal-agent-driver-v167
version: v1.6.7
status: frozen
revision_id: R1
truth_ref: docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md
---

# Tests: Goal AgentDriver v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-GAD-001 | TC-GAD-001 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_depends_on_durable_apis -q` | uses resume-pack/heartbeat APIs |
| AC-GAD-002 | TC-GAD-002 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_longrun_flag -q` | --longrun starts; default idle |
| AC-GAD-003 | TC-GAD-003 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_skill_longrun_intent -q` | skill docs/intent markers |
| AC-GAD-004 | TC-GAD-004 | unit | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_auto_requeue -q` | requeue after turn_ended |
| AC-GAD-005 | TC-GAD-005 | unit | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_digest_prompt_file -q` | prompt is digest-only |
| AC-GAD-006 | TC-GAD-006 | unit | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_bridge_spawn_contract -q` | bridge cmd template |
| AC-GAD-007 | TC-GAD-007 | unit | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_budget_halt -q` | halt_budget no complete |
| AC-GAD-008 | TC-GAD-008 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_complete_needs_verifier -q` | verifier required |
| AC-GAD-009 | TC-GAD-009 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_no_auto_release -q` | no auto release |
| AC-GAD-010 | TC-GAD-010 | unit | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_single_driver_lock -q` | dual start blocked |
| AC-GAD-011 | TC-GAD-011 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_cli_driver_commands -q` | start/status/stop |
| AC-GAD-012 | TC-GAD-012 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_single_public_entry -q` | no second entry skill |
| AC-GAD-013 | TC-GAD-013 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_v2_parity_note -q` | truth cites v2 longrun |
| AC-GAD-014 | TC-GAD-014 | contract | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_tests_md_legal_illegal -q` | legal/illegal rows |

## Legal walk coverage

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-GAD-004 | TC-GAD-LEGAL-01 | legal walk | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_legal_longrun_requeue -q` | longrun requeue path |
| AC-GAD-002 | TC-GAD-LEGAL-02 | legal walk | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_legal_default_no_driver -q` | default run idle driver |

## Illegal transition coverage

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-GAD-008 | TC-GAD-ILLEGAL-01 | illegal | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_illegal_complete_without_verifier -q` | no complete w/o verifier |
| AC-GAD-007 | TC-GAD-ILLEGAL-02 | illegal | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_illegal_budget_complete -q` | budget no complete |
| AC-GAD-009 | TC-GAD-ILLEGAL-03 | illegal | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_illegal_auto_release -q` | no auto release |
| AC-GAD-002 | TC-GAD-ILLEGAL-04 | illegal | `python3 -m pytest tests/test_v167_goal_agent_driver.py::test_illegal_default_autostart -q` | no default autostart |
