# Implementation Brief: Implement Package Legacy Loader Retirement Contract

**Feature**: `implement-package-legacy-loader-retirement-contract`  
**Version**: `v1.4.11`  
**Run ID**: `run-20260526T122005Z-3392`  
**Status**: `implemented`

## What Changed

- Moved the public implement CLI implementation from the historical sibling module into `beacon/commands/implement/commands.py`.
- Replaced the package entrypoint with direct package-owned exports for `app` and `run_implement_stage`.
- Removed the dynamic sibling loader path from `beacon/commands/implement/__init__.py`.
- Updated tests to use package public APIs or the package-owned `commands` module instead of `_legacy_cli`.
- Added v1.4.11 acceptance tests for public CLI routing, static legacy-loader absence, registry binding, and unrelated-surface preservation.

## Evidence

- `rtk python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py`
  - Result: `8 passed`
- `rtk python3 -m pytest -q tests/test_v114_implement_command.py tests/test_v133_ralph_resume_state_refresh.py tests/test_v139_runtime_skill_admission.py tests/test_v147_automation_support_review_and_promotion_contract.py tests/test_v149_ui_ux_externalization.py tests/test_v1411_implement_package_legacy_loader_retirement.py`
  - Result: `78 passed`
- CLI smoke:
  - `rtk python3 -m beacon.main implement --help`
  - `rtk python3 -m beacon.main implement list-runners --help`
  - `rtk python3 -m beacon.main implement import-evidence --help`
  - `rtk python3 -m beacon.main implement run --help`

## Known Non-Blocking Observation

The broader mixed regression subset including `tests/test_v140_branch_blocked_payload_consistency.py` has one pre-existing QA-side failure in `beacon/utils/qa_feature.py`, where a mocked string `targeted_entries` item is treated as a dict. This is outside the implement package loader retirement slice.

## Next Route

Run Beacon QA for this feature:

```bash
rtk python3 -m beacon.main qa run "implement-package-legacy-loader-retirement-contract" --project . --version v1.4.11
```
