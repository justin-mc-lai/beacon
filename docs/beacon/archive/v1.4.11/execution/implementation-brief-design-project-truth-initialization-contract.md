# Implementation Brief: Design Project Truth Initialization Contract

**Feature**: `design-project-truth-initialization-contract`  
**Version**: `v1.4.11`  
**Revision**: `R4`  
**Status**: `implemented`

## Summary

Implemented explicit project-level design/product truth initialization for `beacon design truth`.

## Code Changes

- Added `--include-project-truth` to `beacon design truth`.
- Extended `write_version_design_contracts` with explicit project truth initialization.
- Added project-level templates for `PRODUCT.md` and `DESIGN.md`.
- Preserved default behavior: `--write` still creates only version-wide design truth drafts.
- Preserved existing files by default and reports `exists`.
- Added explicit `--force` overwrite behavior and reports `overwritten`.
- Kept `.machine/design/design-contract.projection.json` projection-only.

## Files Changed

- `beacon/commands/design.py`
- `beacon/utils/design_contract.py`
- `tests/test_v1411_design_project_truth_initialization.py`

## Verification

```bash
rtk python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py tests/test_v1411_beacon_design_human_subskills_closure.py
```

Result:

```text
22 passed
```

Manual CLI smoke:

```bash
rtk python3 -m beacon.main design truth --project <tmpdir> --version v1.4.11 --write --include-project-truth --json
```

Observed:

- `product_truth`: `written`
- `design_truth`: `written`
- `machine_design_projection`: `docs/beacon/archive/v1.4.11/.machine/design/design-contract.projection.json`

## Boundary

- No release gate behavior changed.
- No design support output is promoted into truth automatically.
- No lifecycle stage was added.
- No project-level truth initialization is required for non-UI features.
