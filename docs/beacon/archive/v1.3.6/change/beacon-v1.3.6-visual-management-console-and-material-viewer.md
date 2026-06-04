# Beacon Feature Change Document

- feature: `beacon-v1.3.6-visual-management-console-and-material-viewer`
- feature_slug: `beacon-v1.3.6-visual-management-console-and-material-viewer`
- version: `v1.3.6`
- status: `completed`

## Scope
- Delivered the Beacon visual management console and material viewer as a release-validated companion feature on the `v1.3.6` line, closing prototype, implement, QA, and release evidence around the seven-page console UI and its fixture-backed management read model.

## Added
- Added the `beacon-console-ui` React/Vite application shell with shared layout, loading, error-boundary, and health-tag components.
- Added seven management surfaces covering `Home`, `Management Overview`, `Project Detail`, `Runtime Center`, `Material Viewer`, `Material Document Detail`, and `Recovery Diagnostics`.
- Added fixture-backed console data, route wiring, and page trace helpers so the management console can explain project lifecycle, runtime summaries, material status, and next-step decisions without mutating Beacon truth.
- Added feature QA scorecard and exhaustiveness evidence showing `16/16` AC and scenario closure for the shipped console surface.

## Removed / Reduced
- Reduced homepage machine-detail noise by keeping raw runtime detail and host-session expansion inside `Runtime Center` instead of the default dashboard view.
- Reduced prototype/release drift by accepting the existing subdirectory wireframe bundle layout and numbered page artifacts as canonical prototype evidence.

## Fixed
- Restored the public `implement` entry so `beacon implement` and its planning surface remain callable after the command refactor.
- Fixed prototype writeback, workflow run resolution, technical-review contract materialization, coverage summary projection, evidence-manifest refresh, and runtime-ledger promotion needed to close the `v1.3.6` release gate for this feature.
- Fixed the version-level release truth so `docs/beacon/archive/v1.3.6/change/` and `docs/beacon/archive/v1.3.6/release/` now include this shipped feature instead of leaving it as an untracked side line.

## Traceability Refs
- `beacon-console-ui/src/App.tsx`
- `beacon-console-ui/src/router/index.tsx`
- `beacon-console-ui/src/data/consoleData.ts`
- `beacon-console-ui/src/pages/HomePage/index.tsx`
- `beacon-console-ui/src/pages/ManagementOverviewPage/index.tsx`
- `beacon-console-ui/src/pages/ProjectDetailPage/index.tsx`
- `beacon-console-ui/src/pages/RuntimeCenterPage/index.tsx`
- `beacon-console-ui/src/pages/MaterialViewerPage/index.tsx`
- `beacon-console-ui/src/pages/MaterialDocumentDetailPage/index.tsx`
- `beacon-console-ui/src/pages/RecoveryDiagnosticsPage/index.tsx`
- `beacon/utils/prototype_utils.py`
- `beacon/utils/workflow_memory.py`
- `beacon/utils/writeback.py`
- `beacon/utils/technical_review_contract.py`
- `beacon/utils/coverage.py`
- `docs/beacon/archive/v1.3.6/.machine/execution/implementation-summary-beacon-v1.3.6-visual-management-console-and-material-viewer.json`
- `docs/beacon/archive/v1.3.6/.machine/execution/deterministic-implementation-contract-beacon-v1.3.6-visual-management-console-and-material-viewer.json`
- `.beacon/qa/features/beacon-v1.3.6-visual-management-console-and-material-viewer/scorecard.json`
- `.beacon/qa/features/beacon-v1.3.6-visual-management-console-and-material-viewer/status.json`
- `tests/test_v120_runtime_release_alignment.py`
- `tests/test_gate_coverage_metrics.py`
- `tests/test_v135_prototype_projection_consistency.py`
