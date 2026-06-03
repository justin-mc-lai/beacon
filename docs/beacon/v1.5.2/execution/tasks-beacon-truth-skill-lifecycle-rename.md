# Beacon Implementation Tasks Ledger

- feature: `beacon-truth-skill-lifecycle-rename`
- version: `v1.5.2`
- plan_id: `plan-beacon-truth-skill-lifecycle-rename-r3`
- revision_id: `R3`
- progress: `8/8`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.5.2/.machine/execution/implementation-plan-beacon-truth-skill-lifecycle-rename.progress.json`
- canonical_plan_json: `docs/beacon/v1.5.2/.machine/execution/implementation-plan-beacon-truth-skill-lifecycle-rename.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 Beacon exposes `beacon-truth` as the preferred v1.5.2+ human-facing t...
  - tests=TEST-001,TC-001
[x] `ITASK-002` AC-002 `beacon-truth` must preserve distinct modes for definition, acceptanc...
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 Every `beacon-truth` mode must resolve feature truth through `beacon...
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 Existing `beacon-prd`, `beacon-user-story`, and `beacon-test-case` sk...
  - tests=TEST-004,TC-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 Root Beacon and brainstorm guidance must describe the preferred truth...
  - tests=TEST-005,TC-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 `beacon-truth` must not turn brainstorm, change-refreeze, QA, or rele...
  - tests=TEST-006,TC-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 Coverage truth remains in `features/<slug>/tests.md`; `truth.md` owns...
  - tests=TEST-007,TC-007 | depends_on=ITASK-006
[x] `ITASK-008` AC-008 The new lifecycle language must preserve the closure route from suppo...
  - tests=TEST-008,TC-008 | depends_on=ITASK-007
