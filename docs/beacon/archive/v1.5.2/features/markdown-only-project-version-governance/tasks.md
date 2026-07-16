# Tasks: Markdown-Only Project Version Governance

- [ ] TASK-001 Define `beacon-project-governance-v1` parser and governance MD template
- [ ] TASK-002 Implement `resolve_project_governance` in truth-map
- [ ] TASK-003 Switch `load_project_metadata` / commit path to MD-only (zero governance JSON)
- [ ] TASK-004 Fail-closed execution triple branch merge when governance MD exists
- [ ] TASK-005 Unify metadata and branch-governance toolkit write transaction to governance MD
- [ ] TASK-006 Rewire `_branch_guard_inputs` and explicit-version preflight to resolver-only
- [ ] TASK-007 Add `doctor metadata migrate-to-governance-md` and strict JSON absence verify
- [ ] TASK-008 Update material gate and tests to drop hard-coded governance JSON paths
- [ ] TASK-009 Add regression tests per `tests.md` coverage matrix

Checkbox rows are task ledger only. Lifecycle state advances through CLI validation.
