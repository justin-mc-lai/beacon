# Beacon Feature Change Document

- feature: `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`
- feature_slug: `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`
- version: `v1.3.4`
- status: `completed`

## Scope
- Landed runtime projection ledger support, split docs/runtime context alignment, and real-project board validation materials for the v1.3.4 management-board line.

## Added
- Beacon Runtime Ledger runtime projection helpers
- real-project board validation checklist and acceptance materials
- formal release-line boundaries, blueprint, and source-architecture package

## Removed / Reduced
- none

## Fixed
- Aligned doctor context setup to overwrite stale onboarding docs version when an explicit docs line is selected
- Allowed managed context to carry runtime and docs versions separately for v1.3.4 supplement-line projects
- Projected beacon, rolo, slow_uni_bmtop, and shopxo_canada into the runtime ledger with stable project semantics

## Traceability Refs
- `beacon/commands/doctor.py`
- `beacon/commands/status.py`
- `beacon/utils/context_files.py`
- `beacon/utils/doctor_orchestrator.py`
- `beacon/utils/doctor_registry.py`
- `beacon/utils/runtime_projection.py`
- `beacon/utils/runtime_projection_store.py`
- `docs/beacon/archive/v1.3.4/prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
- `docs/beacon/archive/v1.3.4/user-story/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
- `docs/beacon/archive/v1.3.4/qa/test-cases/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
