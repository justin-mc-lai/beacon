# Tasks: beacon-v2-ui-state-matrix-ship-gate

- [x] TASK-001 ui-state-matrix.v1 schema + scorecard fields
- [x] TASK-002 freeze/ship fail-closed when matrix missing (UX)
- [x] TASK-003 Enforce not-primitives-only rule
- [x] TASK-004 Parity tests vs v1.6.7
- [x] TASK-005 Implement + formal QA


## Implementation note

2026-07-18 Product Goal pgr-51a763f2a691: Python parity + contract tests shipped (test_v200_*). Engine reuses v1.6.7 modules with v2 version support; Loom brand dual-install; subagent opt-in execute; driver→agent_trace hook; `beacon goal trace`.
