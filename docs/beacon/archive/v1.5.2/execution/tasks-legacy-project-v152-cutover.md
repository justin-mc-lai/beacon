# Beacon Implementation Tasks Ledger

- feature: `legacy-project-v152-cutover`
- version: `v1.5.2`
- plan_id: `plan-legacy-project-v152-cutover-r5`
- revision_id: `R5`
- progress: `14/14`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.5.2/.machine/execution/implementation-plan-legacy-project-v152-cutover.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.5.2/.machine/execution/implementation-plan-legacy-project-v152-cutover.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-001 Add cutover inventory classification for legacy/mixed truth state.
  - tests=TEST-001,TC-001,TC-009
[x] `ITASK-002` TASK-002 Teach `beacon-change-refreeze` to run cutover preflight before refreeze.
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[x] `ITASK-003` TASK-003 Add a human-facing cutover wrapper command/skill for phased migration.
  - tests=TEST-003,TC-003,TC-010 | depends_on=ITASK-002
[x] `ITASK-004` TASK-004 Wire package materialize/validate and truth-map verify into cutover phases.
  - tests=TEST-004,TC-004 | depends_on=ITASK-003
[x] `ITASK-005` TASK-005 Wire governance MD verify/projection drift checks into cutover phases.
  - tests=TEST-005,TC-005 | depends_on=ITASK-004
[x] `ITASK-006` TASK-006 Detect stale agent-surface skill guidance and route setup/verify.
  - tests=TEST-006,TC-006 | depends_on=ITASK-005
[x] `ITASK-007` TASK-007 Enforce fail-closed behavior for freeze/refreeze/implement/QA/release while cutover is blocked.
  - tests=TEST-007,TC-007 | depends_on=ITASK-006
[x] `ITASK-008` TASK-008 Preserve and resume the original operator intent after successful cutover.
  - tests=TEST-008,TC-008 | depends_on=ITASK-007
[x] `ITASK-009` TASK-009 Add tests for read-only inventory and dry-run next-command reporting.
  - tests=TEST-009,TEST-010 | depends_on=ITASK-008
[x] `ITASK-010` TASK-010 Update skill guidance so research promotion goes through change/refreeze and not direct truth edits.
  - depends_on=ITASK-009
[x] `ITASK-011` TASK-011 Align `beacon implement plan` with package `tasks.md` while keeping runtime progress in execution artifacts.
  - depends_on=ITASK-010
[x] `ITASK-012` TASK-012 Add doctor `truth_source_mismatch` diagnostics with exact repair routing.
  - depends_on=ITASK-011
[x] `ITASK-013` TASK-013 Add QA regressions for truth-cutover routing simplification, root normalization, and change CLI version stability.
  - depends_on=ITASK-012
[x] `ITASK-014` TASK-014 Update help/doctor route copy so `truth-cutover` is presented as a CLI repair transaction, not a new default public skill.
  - depends_on=ITASK-013
