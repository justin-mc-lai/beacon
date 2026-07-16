# Tasks: legacy-project-v152-cutover

## Task Ledger

- [ ] TASK-001 Add cutover inventory classification for legacy/mixed truth state.
- [ ] TASK-002 Teach `beacon-change-refreeze` to run cutover preflight before refreeze.
- [ ] TASK-003 Add a human-facing cutover wrapper command/skill for phased migration.
- [ ] TASK-004 Wire package materialize/validate and truth-map verify into cutover phases.
- [ ] TASK-005 Wire governance MD verify/projection drift checks into cutover phases.
- [ ] TASK-006 Detect stale agent-surface skill guidance and route setup/verify.
- [ ] TASK-007 Enforce fail-closed behavior for freeze/refreeze/implement/QA/release while cutover is blocked.
- [ ] TASK-008 Preserve and resume the original operator intent after successful cutover.
- [ ] TASK-009 Add tests for read-only inventory and dry-run next-command reporting.
- [ ] TASK-010 Update skill guidance so research promotion goes through change/refreeze and not direct truth edits.
- [ ] TASK-011 Align `beacon implement plan` with package `tasks.md` while keeping runtime progress in execution artifacts.
- [ ] TASK-012 Add doctor `truth_source_mismatch` diagnostics with exact repair routing.
- [ ] TASK-013 Add QA regressions for truth-cutover routing simplification, root normalization, and change CLI version stability.
- [ ] TASK-014 Update help/doctor route copy so `truth-cutover` is presented as a CLI repair transaction, not a new default public skill.

## Boundary

Checkboxes are readable task-ledger inputs only. They do not mark implement, QA, or release complete without existing gate validation.

`beacon implement plan` must consume this ledger as requirement-owned task intent. It may project a draft implementation plan from these rows, but implementation progress, completion, blocked state, and evidence refs must be stored in execution/progress artifacts instead of mutating this file.
