# Beacon Implementation Tasks Ledger

- feature: `version-truth-archive-lineage`
- version: `v1.5.2`
- plan_id: `plan-version-truth-archive-lineage-r2`
- revision_id: `R2`
- progress: `12/12`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.5.2/.machine/execution/implementation-plan-version-truth-archive-lineage.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.5.2/.machine/execution/implementation-plan-version-truth-archive-lineage.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `docs/beacon/governance/version-truth-catalog.md` is the sole commit...
  - tests=TC-001
[x] `ITASK-002` AC-002 Catalog lists exactly **3** `validation_state: active` versions; thei...
  - tests=TC-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 Archived versions have `truth_root` under `docs/beacon/archive/<versi...
  - tests=TC-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 `beacon doctor verify-version-truth-catalog --strict` fails closed on...
  - tests=TC-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 Default delivery commands (`implement`, `qa`, `release`, truth-map bu...
  - tests=TC-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 Unified `discover_features(version)` lists `features/*/truth.md` on v...
  - tests=TC-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 `beacon archive lineage <slug> [--from v] [--to v]` returns ordered h...
  - tests=TC-007 | depends_on=ITASK-006
[x] `ITASK-008` AC-008 `beacon archive inventory [--version auto]` builds feature × AC matri...
  - tests=TC-008 | depends_on=ITASK-007
[x] `ITASK-009` AC-009 `docs/beacon/archive/INDEX.md` is regenerated on every `catalog apply...
  - tests=TC-009 | depends_on=ITASK-008
[x] `ITASK-010` AC-010 `beacon archive catalog bootstrap --active v1.5.0,v1.5.1,v1.5.2 --dry...
  - tests=TC-010 | depends_on=ITASK-009
[x] `ITASK-011` AC-011 `beacon-archive` skill documents decision boundary, four operator ver...
  - tests=TC-011 | depends_on=ITASK-010
[x] `ITASK-012` AC-012 Merge global-boundaries **§4.1 MD-only catalog and archive plane** an...
  - tests=TC-012 | depends_on=ITASK-011
