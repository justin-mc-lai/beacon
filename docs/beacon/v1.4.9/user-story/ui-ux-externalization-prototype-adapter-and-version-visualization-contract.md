# User Story: UI/UX 外部化、Prototype Adapter 与版本级需求可视化契约

**Feature**: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
**Version**: `v1.4.9`
**Status**: `frozen`

## Story

As a Beacon operator,
I want UI/UX execution to be handled by `ui-ux-dev` while Beacon governs accepted design results and version-level requirement projections,
So that Beacon remains a requirement governance kernel instead of a redundant design execution toolbox.

## Acceptance Criteria

- AC-001 Beacon stops treating internal UI/UX execution as a future core capability.
- AC-002 Beacon routes UI/UX execution intent to `ui-ux-dev`.
- AC-003 Beacon does not silently fallback to internal design generation when `ui-ux-dev` is unavailable.
- AC-004 Beacon redefines `prototype` as a design-result adapter.
- AC-005 Beacon blocks implementation when accepted design results lack truth bindings.
- AC-006 Beacon keeps historical prototype bundles readable without making them v1.4.9 execution truth.
- AC-007 Beacon defines version-level business flow projection.
- AC-008 Beacon defines version-level state-machine projection.
- AC-009 Beacon defines version-level PRD / user-story / test-case map projection.
- AC-010 Beacon requires truth bindings for every version-level projection.
- AC-011 Requirement clarity blocks when required visualization bindings are missing.
- AC-012 Beacon keeps `beacon-design-review` as route / governance support, not a truth source or UI/UX execution substitute.

## Scenarios

### Scenario 1: UI/UX execution request

When a user asks Beacon for UI/UX exploration, design-system recommendation, UI review, polish, screenshot extraction, or design library reference,
Then Beacon must route to the matching `ui-ux-dev` intent instead of expanding internal design execution.

### Scenario 2: Accepted design result

When a UI/UX output is accepted and affects feature behavior, page intent, interaction handoff, or user acceptance,
Then Beacon must require a design-result adapter binding before implementation.

### Scenario 3: Version-level understanding

When a version package becomes complex enough to require diagrams,
Then Beacon must provide business flow, state-machine, and PRD / user-story / test-case map projections with truth bindings.

### Scenario 4: Historical compatibility

When older Beacon versions contain prototype bundles,
Then Beacon may read them for history and status,
But v1.4.9 must not treat them as proof that Beacon still owns UI/UX execution.

## Non-Goals

- Do not delete all historical prototype artifacts.
- Do not make `ui-ux-dev` a Beacon lifecycle stage.
- Do not make diagrams canonical truth.
- Do not let `beacon-design-review` bypass `beacon-change`.
