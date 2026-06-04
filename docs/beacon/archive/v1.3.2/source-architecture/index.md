# Beacon v1.3.2 Source Architecture Index

This source-architecture surface explains which code now backs the `v1.3.2` release line.

## Release themes

`v1.3.2` is carried by three implemented product themes:

1. `implement` three execution modes plus iterative browser QA closure
2. Karpathy-style boundary defaults promoted into machine-verifiable contracts
3. `lighthouse` single-file project analysis toolkit

## Command surfaces

- `beacon/commands/implement.py`
  - explicit execution modes
  - bounded team runtime handoff
  - Ralph outer-loop closure
- `beacon/commands/qa.py`
  - feature-aware QA planning
  - team-run isolation
  - iterative browser evidence closure
- `beacon/commands/help.py`
  - human next-step routing
  - mode / round / runner observability
- `beacon/commands/lighthouse.py`
  - minimal analysis entrypoint
  - fixed single-file output contract
- `beacon/commands/review.py`
  - quality review
  - acceptance writeback
  - formal package closure checks

## Shared kernel modules

- `beacon/utils/help_support.py`
  - current execution surface
  - Ralph state
  - QA runner visibility
- `beacon/utils/implementation_plan.py`
  - requirement package to task graph compilation
  - verification-driven plan progress updates
- `beacon/utils/qa_feature.py`
  - feature matrix derivation
  - AC closure and scorecard generation
  - evidence writeback to source QA matrices
- `beacon/utils/global_boundaries.py`
  - canonical global boundary principles
  - source/project inheritance checks
- `beacon/utils/doctor_diagnostics.py`
  - boundary drift diagnostics
  - context inheritance checks
- `beacon/utils/lighthouse.py`
  - single-file analysis templates
  - default output path handling

## Canonical contracts

- `docs/beacon/global-boundaries.md`
- `docs/beacon/archive/v1.3.2/SUMMARY.md`
- `docs/beacon/archive/v1.3.2/execution/architecture-blueprint.md`
- `docs/beacon/archive/v1.3.2/execution/implement-execution-modes-blueprint.md`
- `docs/beacon/archive/v1.3.2/execution/qa-iterative-browser-contract.md`
- `docs/beacon/archive/v1.3.2/execution/lighthouse-analysis-toolkit-blueprint.md`

## Test surfaces backing the line

- `tests/test_v130_implement_team_surface.py`
- `tests/test_v132_karpathy_boundary_defaults.py`
- `tests/test_v132_karpathy_boundary_execution_materials.py`
- `tests/test_v132_implement_three_modes_functional.py`
- `tests/test_v132_implement_three_modes_compatibility.py`
- `tests/test_v119_story_exhaustive_browser_qa.py`

## Boundary note

Even with stronger host-native execution and browser QA loops, `v1.3.2` still treats Beacon as a governed delivery kernel:

- formal requirements remain frozen source of truth
- machine lanes stay internal by default
- `global-boundaries` remains the only canonical cross-version constraint source
- release truth depends on versioned package artifacts, not raw runtime logs
