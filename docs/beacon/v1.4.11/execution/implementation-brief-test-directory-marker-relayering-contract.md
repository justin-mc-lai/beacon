# Implementation Brief: Test Directory / Marker Re-Layering Contract

**Feature**: `test-directory-marker-relayering-contract`  
**Version**: `v1.4.11`  
**Status**: `implemented`

## What Changed

- Registered pytest markers for `current_contract`, `projection_integrity`, `compat_contract`, `historical_fixture`, `migration`, and `deprecated`.
- Added `beacon.utils.test_marker_governance` to produce deterministic marker governance validation payloads.
- Classified existing v1.4.11 retirement tests with role markers.
- Added direct registry binding checks for compatibility tests.
- Kept historical fixture and deprecated callability tests out of current closure.
- Added `tests/test_v1411_test_directory_marker_relayering.py` to validate all frozen ACs.
- Did not move broad test directories or change runtime behavior.

## Evidence

- `rtk python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py`
  - Result: `10 passed`
- `rtk python3 -m pytest -q tests/test_v1411_*.py`
  - Result: `85 passed`

## Notes

- Marker validation is metadata-only and reads test files plus `pyproject.toml`.
- Compatibility classification requires either direct registry ids or registry validation APIs.
- Migration classification requires evidence or transaction assertions.
- Current contract classification rejects legacy-default assertion patterns.

## Next Route

Run Beacon QA for this feature:

```bash
rtk python3 -m beacon.main qa run "test-directory-marker-relayering-contract" --project . --version v1.4.11
```
