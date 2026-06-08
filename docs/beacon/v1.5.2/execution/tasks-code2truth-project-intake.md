# Beacon Implementation Tasks Ledger

- feature: `code2truth-project-intake`
- version: `v1.5.2`
- plan_id: `plan-code2truth-project-intake-r2`
- revision_id: `R2`
- progress: `9/9`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.5.2/.machine/execution/implementation-plan-code2truth-project-intake.progress.json`
- canonical_plan_json: `docs/beacon/v1.5.2/.machine/execution/implementation-plan-code2truth-project-intake.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-001 Define the source inventory model for code, docs, skills, tests, CLI behavior, Beacon source maps, and provider artifacts.
  - tests=TEST-001,TC-001
[x] `ITASK-002` TASK-002 Define provider authority boundaries for `qi-dev-understand-anything` / Understand-Anything and similar code-map tools.
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[x] `ITASK-003` TASK-003 Define candidate truth reconstruction with source refs, confidence, and ambiguity markers.
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[x] `ITASK-004` TASK-004 Require user confirmation before candidate truth can be promoted into package-authoritative truth.
  - tests=TEST-004,TC-004 | depends_on=ITASK-003
[x] `ITASK-005` TASK-005 Freeze package authority through `truth-map` selected `truth.md`, `tests.md`, `tasks.md`, and `evidence.md`.
  - tests=TEST-005,TC-005 | depends_on=ITASK-004
[x] `ITASK-006` TASK-006 Define implement no-op/evidence-only admission when existing code satisfies frozen truth.
  - tests=TEST-006,TC-006 | depends_on=ITASK-005
[x] `ITASK-007` TASK-007 Define QA coverage for package truth, provider evidence, governance verify, and current behavior satisfaction.
  - tests=TEST-008,TC-008 | depends_on=ITASK-006
[x] `ITASK-008` TASK-008 Preserve fail-closed routing for ambiguous, stale, conflicting, low-confidence, or unproven behavior.
  - tests=TEST-009,TC-009 | depends_on=ITASK-007
[x] `ITASK-009` TASK-009 Support a bounded pilot on an existing project or skill pack before whole-repo adoption.
  - tests=TEST-010,TEST-007,TC-007,TC-010 | depends_on=ITASK-008
