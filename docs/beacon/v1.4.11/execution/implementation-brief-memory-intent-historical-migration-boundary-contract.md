# Implementation Brief: Memory / Intent Historical Migration Boundary Contract

**Feature**: `memory-intent-historical-migration-boundary-contract`  
**Version**: `v1.4.11`  
**Status**: `implemented`

## What Changed

- Kept legacy memory rows importable into current `memory-v1`.
- Added first-run memory migration transaction evidence under `.beacon/state/memory-migration/`.
- Stopped current memory writes from updating legacy projection files by default.
- Added explicit compatibility export for legacy memory projection writes through `export_legacy_projection(..., compat_mode=True)` and `beacon remember export-legacy-projection --compat-mode`.
- Marked legacy intent router output as `intent-legacy-router` compatibility evidence.
- Added explicit old-router admission through `route_legacy_intent_compat(..., compat_mode=True)`.
- Added current route evidence to `optimize_prompt_to_plan()` so current routing does not claim legacy router output as current proof.
- Kept this slice out of prototype/design, browser, QA/PRD mirror, implement package, command removal, release, and test marker behavior.

## Evidence

- `rtk python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py`
  - Result: `11 passed`
- `rtk python3 -m pytest -q tests/test_memory_envelope.py tests/test_v103_memory_revision_contract.py tests/utils/test_intent_router.py tests/test_prompt_optimize_contract.py`
  - Result: `36 passed`
- `rtk python3 -m pytest -q tests/test_feedback_memory_assimilation.py tests/test_workflow_memory_lifecycle.py tests/test_team_release_memory_trace.py`
  - Result: `4 passed`
- `rtk python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py tests/test_v1411_implement_package_legacy_loader_retirement.py tests/test_v1411_browser_fallback_deterministic_command.py`
  - Result: `27 passed`

## Notes

- `memory-v1` is the current projection. Legacy files are now export targets, not default write targets.
- Migration transaction evidence includes `migration_transaction_id`, `compat_id`, `source_files`, `imported_count`, `skipped_count`, `current_projection`, `legacy_projection_written`, and `compat_mode`.
- Legacy `detect_intent()` and `route_intent()` remain callable for older imports, but their payloads now self-identify as compatibility router output.

## Next Route

Run Beacon QA for this feature:

```bash
rtk python3 -m beacon.main qa run "memory-intent-historical-migration-boundary-contract" --project . --version v1.4.11
```
