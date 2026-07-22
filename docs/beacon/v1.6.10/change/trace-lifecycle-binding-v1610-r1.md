# Change: trace-lifecycle-binding-v1610 R1

## Intent
Bind 1+6 lifecycle stage exits to `agent_trace.v1` under `.beacon/traces/<run_id>.jsonl` for replay, regression, and anti-drift — without a 7th public harness and without full-chat authority.

## Delivered
- Gold package `docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/` (人话, Intent Matrix, FSM 五元组, AC, Non-goals)
- `record_lifecycle_stage_trace` + `resolve_lifecycle_trace_run_id` in `beacon/utils/agent_trace.py`
- Hooks: truth review, freeze, qa run, implement run start, release check
- Goal driver: surface `last_agent_trace` / error instead of bare `except: pass`
- preflight: fail-closed when `.beacon/traces` is not a directory
- Tests: `tests/test_v1610_trace_lifecycle_binding.py`

## Freeze note
Formal `beacon freeze` requires truth-canonical branch `main`. R1 lands on feature branch; freeze after merge (or on main worktree). TRG report written under `.machine/execution/`.

## Non-goals kept
- release hard-gate on missing trace
- LLM API key requirement for host-skill path
