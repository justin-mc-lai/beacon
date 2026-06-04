# User Story: Version Material File Map Contract

**Feature**: `version-material-file-map-contract`
**Version**: `v1.4.12`
**Status**: `frozen`
**Date**: `2026-05-31`
**Language**: `en`

## Story

As a Beacon developer, I want a canonical manifest file to serve as the single source of truth for feature discovery within a version, so that all modules see the same feature set and no module relies on glob-based discovery that can drift.

## Outline

```mermaid
flowchart LR
    A[Developer adds feature] --> B[beacon manifest add-feature]
    B --> C[Manifest tracks all paths]
    C --> D[All consumers read manifest]
    D --> E[Consistent feature list everywhere]
```

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | single-source | `version-features.json` is the canonical source of truth for feature discovery; no glob-based discovery remains |
| AC-002 | no-glob | Zero glob calls for feature discovery in v1.4.12+ code paths |
| AC-003 | registration | `beacon manifest add-feature` registers all truth and evidence paths for a feature |
| AC-004 | verification | `beacon manifest verify --strict` confirms every manifest path exists on disk |
| AC-005 | gate-blocking | `build_requirement_package_gate` blocks on missing truth file with `manifest_truth_file_missing` |

## Test Story Map

| Test ID | Covers | Scenario |
|---------|--------|----------|
| TC-001 | AC-001 | Load manifest returns correct feature list matching disk files |
| TC-002 | AC-001 | Manifest contains version-level paths for research, execution, release, design |
| TC-003 | AC-002 | `_discover_features` uses manifest, not glob |
| TC-004 | AC-002 | `_feature_names` uses manifest, not glob |
| TC-005 | AC-002 | `build_material_audit` uses manifest, not glob |
| TC-006 | AC-003 | `beacon manifest add-feature` writes all 20 fixed paths and transaction record |
| TC-007 | AC-004 | `beacon manifest verify --strict` exits 0 for valid manifest |
| TC-008 | AC-004 | `beacon manifest verify --strict` exits 2 when path missing from disk |
| TC-009 | AC-005 | Deleting truth file causes gate to return `blocked` with `manifest_truth_file_missing` |
| TC-010 | AC-005 | Empty manifest passes verification with zero features |

## References
- Research: `docs/beacon/archive/v1.4.12/research/version-material-file-map-contract.md`
- PRD: `docs/beacon/archive/v1.4.12/prd/version-material-file-map-contract.md`
- Test cases: `docs/beacon/archive/v1.4.12/qa/test-cases/version-material-file-map-contract.md`
