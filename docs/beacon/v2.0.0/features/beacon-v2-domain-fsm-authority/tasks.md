# Tasks: beacon-v2-domain-fsm-authority

- [x] TASK-001 Author domain-fsm.v1 / entity-precedence.v1 schemas in beacon-core/gate
- [x] TASK-002 Wire freeze + requirement_clarity fail-closed checks
- [x] TASK-003 Import/parity load v1.6.7 domain fixtures
- [x] TASK-004 Contract tests TC-V2-DFSM-001..004
- [x] TASK-005 Implement + formal QA


## Implementation note

2026-07-18 Product Goal pgr-51a763f2a691: Python parity + contract tests shipped (test_v200_*). Engine reuses v1.6.7 modules with v2 version support; Loom brand dual-install; subagent opt-in execute; driver→agent_trace hook; `beacon goal trace`.
