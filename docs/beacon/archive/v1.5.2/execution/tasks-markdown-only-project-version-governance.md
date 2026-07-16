# Beacon Implementation Tasks Ledger

- feature: `markdown-only-project-version-governance`
- version: `v1.5.2`
- plan_id: `plan-markdown-only-project-version-governance-r2`
- revision_id: `R2`
- progress: `13/13`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.5.2/.machine/execution/implementation-plan-markdown-only-project-version-governance.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.5.2/.machine/execution/implementation-plan-markdown-only-project-version-governance.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `docs/beacon/governance/project-version-governance.md` is the sole au...
  - tests=TEST-001,TC-001
[x] `ITASK-002` AC-002 No governance JSON records under `.beacon/metadata/` (including `proj...
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 `beacon-toolkit-metadata`, `beacon-toolkit-branch-governance`, implem...
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 `load_project_metadata` (or successor) parses governance MD; it must...
  - tests=TEST-004,TC-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 Metadata/branch-governance write transactions update governance MD on...
  - tests=TEST-005,TC-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 When governance MD exists for the active version, `load_execution_bra...
  - tests=TEST-006,TC-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 Metadata and branch-governance toolkit surfaces share one governance...
  - tests=TEST-007,TC-007 | depends_on=ITASK-006
[x] `ITASK-008` AC-008 `_branch_guard_inputs` derives `expected_branch`, `git_roots`, `parti...
  - tests=TEST-008,TC-008 | depends_on=ITASK-007
[x] `ITASK-009` AC-009 Monorepo topology with multiple `service_bindings` and `per_service_c...
  - tests=TEST-009,TC-009 | depends_on=ITASK-008
[x] `ITASK-010` AC-010 `beacon doctor metadata migrate-to-governance-md` (or equivalent) imp...
  - tests=TEST-010,TC-010 | depends_on=ITASK-009
[x] `ITASK-011` AC-011 Material gate / release supplements reference governance MD via resol...
  - tests=TEST-011,TC-011 | depends_on=ITASK-010
[x] `ITASK-012` AC-012 truth-map registers `project_governance` (or equivalent) as version g...
  - tests=TEST-012,TC-012 | depends_on=ITASK-011
[x] `ITASK-013` AC-013 Explicit-version implement preflight resolves canonical branch/worktr...
  - tests=TEST-013,TC-013 | depends_on=ITASK-012
