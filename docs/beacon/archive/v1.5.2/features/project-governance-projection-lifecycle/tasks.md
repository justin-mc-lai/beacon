# Tasks: Project Governance Projection Lifecycle

- [x] TASK-001 Fix `truth_map.py` dual surface on governance MD (AC-001, AC-002, AC-003)
- [x] TASK-002 Align sqlite projection to MD `source_hash`; optional slim `payload_json` (AC-004, AC-006)
- [x] TASK-003 Add `governance_projection_drift` to `verify_project_metadata` / doctor verify (AC-005)
- [x] TASK-004 Extend governance parser/render for `validation_state` active|archived (AC-007)
- [x] TASK-005 Filter archived contracts in `resolve_project_governance` (AC-008)
- [x] TASK-006 Add `doctor metadata archive-version` and `prune-archived` (AC-009, AC-010)
- [x] TASK-007 Add `tests/test_project_governance_projection_lifecycle.py` per coverage matrix
- [x] TASK-008 Run parent governance regression + package validation before freeze

Checkbox rows are task ledger only. Lifecycle state advances through CLI validation.
