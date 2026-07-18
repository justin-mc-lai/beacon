# Tasks: beacon-v2-golden-commerce-fixture-parity

- [x] TASK-001 Create docs/beacon/v2.0.0/fixtures/parity-v167 index
- [x] TASK-002 Wire fixture loader for v2 gate/QA
- [x] TASK-003 Negative path contract tests
- [x] TASK-004 Implement + formal QA


## Implementation note

2026-07-18 Product Goal pgr-51a763f2a691: Python parity + contract tests shipped (test_v200_*). Engine reuses v1.6.7 modules with v2 version support; Loom brand dual-install; subagent opt-in execute; driver→agent_trace hook; `beacon goal trace`.
