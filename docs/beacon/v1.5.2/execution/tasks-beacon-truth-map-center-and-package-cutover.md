# Beacon Implementation Tasks Ledger

- feature: `beacon-truth-map-center-and-package-cutover`
- version: `v1.5.2`
- plan_id: `plan-beacon-truth-map-center-and-package-cutover-r1`
- revision_id: `R1`
- progress: `8/8`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.5.2/.machine/execution/implementation-plan-beacon-truth-map-center-and-package-cutover.progress.json`
- canonical_plan_json: `docs/beacon/v1.5.2/.machine/execution/implementation-plan-beacon-truth-map-center-and-package-cutover.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `features/<slug>/*.md` is authoritative for normal production and con...
  - tests=TC-001,TC-009,TC-010
[x] `ITASK-002` AC-002 Commands and skills must call truth-map resolver before reading truth.
  - tests=TC-002,TC-011,TC-012,TC-013 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 Legacy triptych is not a canonical source in v1.5.2.
  - tests=TC-003,TC-014,TC-015 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 `doctor` can rebuild legacy triptych from package truth.
  - tests=TC-004,TC-016 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 `change` can absorb legacy triptych into package truth.
  - tests=TC-005,TC-017 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 Missing JSON twins do not block Markdown truth validity.
  - tests=TC-006,TC-018,TC-019 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 QA/release/gate use resolver and parser outputs from package truth.
  - tests=TC-007,TC-020,TC-021,TC-022,TC-023 | depends_on=ITASK-006
[x] `ITASK-008` AC-008 Drift against package truth is reported; package truth remains author...
  - tests=TC-008,TC-024,TC-025 | depends_on=ITASK-007
